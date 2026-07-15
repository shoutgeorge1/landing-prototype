"""Guarded campaign create orchestration (dry-run default; --execute only)."""

from __future__ import annotations

import csv
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ela_google_ads.builders.campaign import build_campaign_preview
from ela_google_ads.builders.mutate_ops import (
    ELA_CUSTOM_CONVERSION_GOAL_NAME,
    budget_name_for_campaign,
    build_campaign_create_operations,
)
from ela_google_ads.client import build_client, run_gaql
from ela_google_ads.config import GoogleAdsSettings
from ela_google_ads.exceptions import ApiAccessError, MutationSafetyError
from ela_google_ads.export_utils import timestamp_slug, write_json
from ela_google_ads.logging_config import get_logger
from ela_google_ads.models.spec import CampaignSpec, KeywordSpec
from ela_google_ads.safety import (
    bakersfield_hold_metadata_for_spec,
    confirm_customer_id,
)
from ela_google_ads.validators.mutation_guards import (
    guard_create_spec,
    guard_execute_attempt,
)
from ela_google_ads.validators.spec_validators import assert_spec_valid, validate_campaign_spec

logger = get_logger(__name__)

CAMPAIGN_BY_NAME_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.resource_name
    FROM campaign
    WHERE campaign.name = '{name}'
      AND campaign.status != 'REMOVED'
"""

BUDGET_BY_NAME_QUERY = """
    SELECT
      campaign_budget.id,
      campaign_budget.name,
      campaign_budget.resource_name,
      campaign_budget.amount_micros,
      campaign_budget.status
    FROM campaign_budget
    WHERE campaign_budget.name = '{name}'
"""

CUSTOM_GOAL_BY_NAME_QUERY = """
    SELECT
      custom_conversion_goal.id,
      custom_conversion_goal.name,
      custom_conversion_goal.status,
      custom_conversion_goal.resource_name,
      custom_conversion_goal.conversion_actions
    FROM custom_conversion_goal
    WHERE custom_conversion_goal.name = '{name}'
      AND custom_conversion_goal.status != 'REMOVED'
"""


def find_campaign_by_exact_name(
    client: Any,
    customer_id: str,
    campaign_name: str,
) -> dict[str, Any] | None:
    """Exact-name lookup for idempotent create. Never updates the match."""
    safe = campaign_name.replace("\\", "\\\\").replace("'", "\\'")
    query = CAMPAIGN_BY_NAME_QUERY.format(name=safe)
    matches: list[dict[str, Any]] = []
    for row in run_gaql(client, customer_id, query):
        matches.append(
            {
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name,
                "status": str(getattr(row.campaign.status, "name", row.campaign.status)),
                "resource_name": row.campaign.resource_name,
            }
        )
    if not matches:
        return None
    if len(matches) > 1:
        raise MutationSafetyError(
            f"Multiple non-removed campaigns named {campaign_name!r}; "
            "refusing create/skip ambiguity."
        )
    return matches[0]


def find_budget_by_exact_name(
    client: Any,
    customer_id: str,
    budget_name: str,
) -> dict[str, Any] | None:
    safe = budget_name.replace("\\", "\\\\").replace("'", "\\'")
    query = BUDGET_BY_NAME_QUERY.format(name=safe)
    matches: list[dict[str, Any]] = []
    for row in run_gaql(client, customer_id, query):
        matches.append(
            {
                "budget_id": str(row.campaign_budget.id),
                "budget_name": row.campaign_budget.name,
                "resource_name": row.campaign_budget.resource_name,
                "amount_micros": int(row.campaign_budget.amount_micros),
                "status": str(
                    getattr(row.campaign_budget.status, "name", row.campaign_budget.status)
                ),
            }
        )
    if not matches:
        return None
    if len(matches) > 1:
        logger.warning(
            "Multiple budgets named %r; reusing first resource_name=%s",
            budget_name,
            matches[0]["resource_name"],
        )
    return matches[0]


def find_custom_goal_by_exact_name(
    client: Any,
    customer_id: str,
    goal_name: str = ELA_CUSTOM_CONVERSION_GOAL_NAME,
) -> dict[str, Any] | None:
    safe = goal_name.replace("\\", "\\\\").replace("'", "\\'")
    matches: list[dict[str, Any]] = []
    for row in run_gaql(
        client,
        customer_id,
        CUSTOM_GOAL_BY_NAME_QUERY.format(name=safe),
    ):
        goal = row.custom_conversion_goal
        matches.append(
            {
                "goal_id": str(goal.id),
                "goal_name": goal.name,
                "status": str(getattr(goal.status, "name", goal.status)),
                "resource_name": goal.resource_name,
                "conversion_actions": list(goal.conversion_actions),
            }
        )
    if len(matches) > 1:
        raise MutationSafetyError(
            f"Multiple custom conversion goals named {goal_name!r}; refusing ambiguity."
        )
    return matches[0] if matches else None


def attach_locked_campaign_negatives(spec: CampaignSpec, spec_path: Path) -> int:
    """Flatten the locked launch lists into campaign-level negative criteria."""
    root = spec_path.resolve().parent.parent
    language = spec.language.lower()
    csv_path = root / "output" / f"negative_keywords_upload_{language}.csv"
    if not csv_path.is_file():
        raise MutationSafetyError(
            f"Locked negative export is missing: {csv_path}. "
            "Run scripts/check_negative_conflicts.py --all-specs first."
        )
    existing = {
        (keyword.text.strip().lower(), keyword.match_type.upper())
        for keyword in spec.campaign_negative_keywords
    }
    added = 0
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            text = str(row.get("keyword") or "").strip()
            match_type = str(row.get("match_type") or "").upper()
            if not text:
                continue
            if match_type not in {"PHRASE", "EXACT"}:
                raise MutationSafetyError(
                    f"Refusing non-phrase/exact campaign negative {text!r}: {match_type!r}"
                )
            key = (text.lower(), match_type)
            if key in existing:
                continue
            spec.campaign_negative_keywords.append(
                KeywordSpec(text=text, match_type=match_type)
            )
            existing.add(key)
            added += 1
    return added


def _run_mutate(
    client: Any,
    *,
    customer_id: str,
    operations: list[Any],
    validate_only: bool,
) -> Any:
    try:
        from google.ads.googleads.errors import GoogleAdsException
    except ImportError:  # pragma: no cover
        GoogleAdsException = Exception  # type: ignore[misc, assignment]

    ga_service = client.get_service("GoogleAdsService")
    try:
        request = client.get_type("MutateGoogleAdsRequest")
        request.customer_id = customer_id
        request.mutate_operations.extend(operations)
        request.partial_failure = False
        request.validate_only = validate_only
        request.response_content_type = (
            client.enums.ResponseContentTypeEnum.RESOURCE_NAME_ONLY
        )
        return ga_service.mutate(request=request)
    except GoogleAdsException as exc:
        messages: list[str] = []
        failure = getattr(exc, "failure", None)
        if failure is not None:
            for index, error in enumerate(failure.errors, start=1):
                path_parts: list[str] = []
                location = getattr(error, "location", None)
                for element in getattr(location, "field_path_elements", []) or []:
                    field = str(getattr(element, "field_name", "") or "")
                    field_index = getattr(element, "index", None)
                    if field:
                        path_parts.append(
                            f"{field}[{field_index}]" if field_index is not None else field
                        )
                error_code = str(getattr(error, "error_code", "") or "").strip()
                details = getattr(error, "details", None)
                policy = getattr(details, "policy_violation_details", None)
                topics = [
                    str(getattr(entry, "topic", "") or "")
                    for entry in getattr(policy, "policy_topic_entries", []) or []
                    if getattr(entry, "topic", None)
                ]
                policy_text = str(policy or "").strip()
                messages.append(
                    " | ".join(
                        part
                        for part in (
                            f"#{index}",
                            f"code={error_code}" if error_code else "",
                            f"path={'.'.join(path_parts)}" if path_parts else "",
                            f"message={error.message}",
                            f"policy_topics={','.join(topics)}" if topics else "",
                            f"policy_details={policy_text}" if policy_text else "",
                        )
                        if part
                    )
                )
        detail = "; ".join(messages) if messages else str(exc)
        mode = "validate_only" if validate_only else "execute"
        request_id = getattr(exc, "request_id", None)
        raise ApiAccessError(
            f"Google Ads mutate ({mode}) failed"
            f"{f' request_id={request_id}' if request_id else ''}: {detail}"
        ) from exc


def _collect_mutate_resource_names(response: Any) -> list[str]:
    names: list[str] = []
    for result in getattr(response, "mutate_operation_responses", []) or []:
        for field in (
            "campaign_budget_result",
            "campaign_result",
            "campaign_criterion_result",
            "campaign_asset_result",
            "asset_result",
            "ad_group_result",
            "ad_group_criterion_result",
            "ad_group_ad_result",
        ):
            part = getattr(result, field, None)
            if part is not None and getattr(part, "resource_name", None):
                names.append(part.resource_name)
                break
    return names


def create_campaign_from_spec(
    settings: GoogleAdsSettings,
    spec_path: Path | str,
    *,
    execute: bool = False,
    confirm_customer_id_value: str | None = None,
    out_dir: Path | None = None,
    client: Any | None = None,
) -> dict[str, Any]:
    """Validate and optionally create a PAUSED ELA Nonbrand Search campaign.

    Default is dry-run (no mutation). ``execute=True`` requires
    ``--confirm-customer-id 6769947952``, runs validate_only mutate first, then
    a live mutate. Existing exact-name campaigns are skipped without modification.
    """
    path = Path(spec_path)
    spec = assert_spec_valid(path)
    issues = validate_campaign_spec(spec)
    if issues:
        raise MutationSafetyError(
            "Spec validation issues remain: " + "; ".join(issues[:5])
        )
    guard_create_spec(spec)

    customer_id = settings.customer_id
    guard_execute_attempt(
        customer_id=customer_id,
        operation="campaigns.create",
        execute=execute,
    )
    if execute:
        confirm_customer_id(customer_id, confirm_customer_id_value)
        settings.require_live_credentials()

    preview = build_campaign_preview(spec)
    hold = bakersfield_hold_metadata_for_spec(name=spec.name, city=spec.city)
    destination = out_dir or settings.output_dir
    destination.mkdir(parents=True, exist_ok=True)

    result: dict[str, Any] = {
        "mode": "execute" if execute else "dry_run",
        "will_mutate": False,
        "customer_id": customer_id,
        "spec_path": str(path),
        "campaign_name": spec.name,
        "status_requested": "PAUSED",
        "skipped": False,
        "skip_reason": None,
        "validate_only_ok": None,
        "mutated": False,
        "preview": preview,
        "bakersfield_activation_hold": hold,
        "resources": {
            "created": [],
            "skipped": [],
            "reused": [],
            "planned": [],
        },
        "notes": [],
        "logged_at": datetime.now(UTC).isoformat(),
    }

    ads_client = client or build_client(settings)

    existing = find_campaign_by_exact_name(ads_client, customer_id, spec.name)
    if existing:
        result["skipped"] = True
        result["skip_reason"] = (
            "Campaign with exact name already exists; refusing to modify it."
        )
        result["resources"]["skipped"].append(
            {
                "type": "campaign",
                "name": existing["campaign_name"],
                "campaign_id": existing["campaign_id"],
                "resource_name": existing["resource_name"],
                "status": existing["status"],
                "action": "skip_existing_no_mutate",
            }
        )
        result["notes"].append(
            "Idempotent skip: existing vendor/legacy/ELA campaigns are never "
            "updated, deleted, renamed, or otherwise mutated by name match."
        )
        log_path = _write_create_log(destination, result)
        result["log_path"] = str(log_path)
        return result

    # Attach locked launch negatives only when we are about to create/validate.
    negative_count = attach_locked_campaign_negatives(spec, path)
    post_attach_issues = validate_campaign_spec(spec)
    if post_attach_issues:
        raise MutationSafetyError(
            "Spec validation failed after attaching locked negatives: "
            + "; ".join(post_attach_issues[:5])
        )
    budget_name = budget_name_for_campaign(spec.name)
    existing_budget = find_budget_by_exact_name(ads_client, customer_id, budget_name)
    existing_budget_rn = existing_budget["resource_name"] if existing_budget else None
    if existing_budget:
        result["resources"]["reused"].append(
            {
                "type": "campaign_budget",
                "name": existing_budget["budget_name"],
                "budget_id": existing_budget["budget_id"],
                "resource_name": existing_budget["resource_name"],
                "status": existing_budget["status"],
                "action": "reuse_deterministic_budget",
            }
        )

    existing_custom_goal = find_custom_goal_by_exact_name(
        ads_client, customer_id
    )
    existing_custom_goal_rn = (
        existing_custom_goal["resource_name"] if existing_custom_goal else None
    )
    if existing_custom_goal:
        expected_actions = {
            f"customers/{customer_id}/conversionActions/{action_id}"
            for action_id in spec.conversion_goals
        }
        if set(existing_custom_goal["conversion_actions"]) != expected_actions:
            raise MutationSafetyError(
                f"Existing {ELA_CUSTOM_CONVERSION_GOAL_NAME!r} has different "
                "conversion actions; refusing to modify it."
            )
        result["resources"]["reused"].append(
            {
                "type": "custom_conversion_goal",
                **existing_custom_goal,
                "action": "reuse_exact_name_no_mutate",
            }
        )

    plan = build_campaign_create_operations(
        ads_client,
        customer_id=customer_id,
        spec=spec,
        existing_budget_resource_name=existing_budget_rn,
        existing_custom_goal_resource_name=existing_custom_goal_rn,
    )
    result["resources"]["planned"] = plan.planned_resources
    result["notes"].extend(plan.notes)
    result["notes"].append(
        f"Attached {negative_count} locked {spec.language.upper()} campaign-level negatives."
    )
    result["operations_count"] = len(plan.operations)

    # Always run validate_only before any live mutate. In dry-run mode this is
    # the only API mutate call (no resource creation).
    _run_mutate(
        ads_client,
        customer_id=customer_id,
        operations=plan.operations,
        validate_only=True,
    )
    result["validate_only_ok"] = True
    result["notes"].append("validate_only mutate succeeded")

    if not execute:
        result["notes"].append(
            "Dry-run only. Re-run with --execute --confirm-customer-id "
            f"{customer_id} to create PAUSED resources after review."
        )
        log_path = _write_create_log(destination, result)
        result["log_path"] = str(log_path)
        return result

    response = _run_mutate(
        ads_client,
        customer_id=customer_id,
        operations=plan.operations,
        validate_only=False,
    )
    created_names = _collect_mutate_resource_names(response)
    result["mutated"] = True
    result["will_mutate"] = True
    result["resources"]["created"] = [
        {"resource_name": name, "action": "created"} for name in created_names
    ]
    for item in plan.planned_resources:
        if item.get("action") == "create":
            result["resources"]["created"].append({**item, "action": "created"})
    result["notes"].append(
        f"Created {len(created_names)} resources (PAUSED where API supports it)."
    )
    log_path = _write_create_log(destination, result)
    result["log_path"] = str(log_path)
    logger.warning(
        "CAMPAIGN CREATE EXECUTED customer_id=%s campaign=%s resources=%s",
        customer_id,
        spec.name,
        len(created_names),
    )
    return result


def create_campaigns_from_specs(
    settings: GoogleAdsSettings,
    spec_paths: list[Path | str],
    *,
    execute: bool = False,
    confirm_customer_id_value: str | None = None,
    out_dir: Path | None = None,
    client: Any | None = None,
) -> dict[str, Any]:
    """Create or dry-run multiple specs sequentially; never mutates existing names."""
    destination = out_dir or settings.output_dir
    results: list[dict[str, Any]] = []
    for spec_path in spec_paths:
        results.append(
            create_campaign_from_spec(
                settings,
                spec_path,
                execute=execute,
                confirm_customer_id_value=confirm_customer_id_value,
                out_dir=destination,
                client=client,
            )
        )
    summary = {
        "mode": "execute" if execute else "dry_run",
        "customer_id": settings.customer_id,
        "count": len(results),
        "created": sum(1 for r in results if r.get("mutated")),
        "skipped": sum(1 for r in results if r.get("skipped")),
        "dry_run_validated": sum(
            1 for r in results if r.get("validate_only_ok") and not r.get("mutated")
        ),
        "results": results,
        "logged_at": datetime.now(UTC).isoformat(),
    }
    path = write_json(
        destination / f"campaign_create_batch_{timestamp_slug()}.json",
        summary,
    )
    summary["log_path"] = str(path)
    return summary


def _write_create_log(destination: Path, result: dict[str, Any]) -> Path:
    safe = "".join(
        ch if ch.isalnum() or ch in "-_" else "_" for ch in result["campaign_name"]
    )
    return write_json(
        destination / f"campaign_create_{safe}_{timestamp_slug()}.json",
        result,
    )
