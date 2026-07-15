"""Mutation safety guards.

All write paths must call these helpers. Live mutations require explicit
``--execute``, a hard customer allowlist, and ``--confirm-customer-id``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from ela_google_ads.exceptions import MutationSafetyError
from ela_google_ads.logging_config import get_logger

logger = get_logger(__name__)

ALLOWED_NEW_CAMPAIGN_STATUS = "PAUSED"
ALLOWED_MUTATION_CUSTOMER_IDS = frozenset({"6769947952"})
DEFAULT_CONFIRM_CUSTOMER_ID = "6769947952"

# ELA | Search | {City} | {EN|ES} | Nonbrand
ELA_NONBRAND_SEARCH_NAME_RE = re.compile(
    r"^ELA \| Search \| .+ \| (EN|ES) \| Nonbrand$"
)

BAKERSFIELD_ACTIVATION_HOLD: dict[str, Any] = {
    "active": True,
    "markets": ["bakersfield"],
    "campaign_name_markers": ["Bakersfield"],
    "required_acknowledgement_flag": "vendor_shutdown_acknowledged",
    "reason": (
        "Vendor tracking / keyword overlap on Bakersfield. "
        "Do not enable until vendor shutdown is explicitly acknowledged."
    ),
    "enable_implemented": False,
    "create_behavior": "allowed_paused_only",
    "metadata_path": "specs/shared/bakersfield-activation-hold.yaml",
}


@dataclass
class MutationContext:
    """Context for a proposed or applied mutation."""

    customer_id: str
    operation: str
    execute: bool = False
    validate_only: bool = True
    dry_run: bool = True
    resource_ids: list[str] = field(default_factory=list)
    preview: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    # Back-compat alias used by older call sites / tests.
    @property
    def apply(self) -> bool:
        return self.execute

    @property
    def will_mutate(self) -> bool:
        return self.execute and not self.dry_run and not self.validate_only


def assert_customer_allowlisted(customer_id: str) -> str:
    """Hard-allowlist the only customer this toolkit may mutate."""
    cleaned = str(customer_id or "").strip()
    if cleaned not in ALLOWED_MUTATION_CUSTOMER_IDS:
        raise MutationSafetyError(
            f"Customer {cleaned!r} is not on the mutation allowlist. "
            f"Allowed: {sorted(ALLOWED_MUTATION_CUSTOMER_IDS)}."
        )
    return cleaned


def assert_mutation_allowed(ctx: MutationContext) -> None:
    """Block live mutations unless --execute is set and dry-run/validate-only are off."""
    assert_customer_allowlisted(ctx.customer_id)
    if not ctx.execute:
        raise MutationSafetyError(
            f"Refusing to run '{ctx.operation}' against customer {ctx.customer_id}: "
            "mutations require explicit --execute. Default mode is dry-run / preview."
        )
    if ctx.dry_run:
        raise MutationSafetyError(
            f"Refusing '{ctx.operation}': dry_run is still True. "
            "Pass --execute only when you intend to mutate after validate_only."
        )
    if not ctx.customer_id or not str(ctx.customer_id).isdigit():
        raise MutationSafetyError(
            f"Refusing '{ctx.operation}': target customer ID must be confirmed digits-only."
        )
    logger.warning(
        "MUTATION AUTHORIZED operation=%s customer_id=%s validate_only=%s resources=%s",
        ctx.operation,
        ctx.customer_id,
        ctx.validate_only,
        ctx.resource_ids,
    )


def assert_new_campaign_paused(status: str) -> None:
    if (status or "").upper() != ALLOWED_NEW_CAMPAIGN_STATUS:
        raise MutationSafetyError(
            f"New campaigns must be created as {ALLOWED_NEW_CAMPAIGN_STATUS}, got {status!r}. "
            "Never enable campaigns automatically. ENABLED is refused."
        )


def assert_status_not_enabled(status: str, *, resource: str) -> None:
    if (status or "").upper() == "ENABLED":
        raise MutationSafetyError(
            f"Refusing ENABLED status for {resource}. "
            "Create path only allows PAUSED where the API supports pause."
        )


def assert_ela_nonbrand_search_name(name: str) -> None:
    if not ELA_NONBRAND_SEARCH_NAME_RE.match(name or ""):
        raise MutationSafetyError(
            f"Refusing campaign name {name!r}. Create path only allows new "
            "'ELA | Search | {{City}} | {{EN|ES}} | Nonbrand' campaigns."
        )


def assert_explicit_resource_id(resource_id: str | None, *, action: str) -> str:
    """Edits to existing resources require an explicit resource ID — never name matching alone."""
    if not resource_id or not str(resource_id).strip():
        raise MutationSafetyError(
            f"Cannot {action}: existing resources must be targeted by explicit resource ID, "
            "not by name match alone."
        )
    return str(resource_id).strip()


def assert_no_delete(operation: str) -> None:
    if "delete" in operation.lower() or "remove" in operation.lower():
        raise MutationSafetyError(
            f"Deletion operations are disabled in this toolkit version: {operation}"
        )


def assert_no_existing_resource_mutation(operation: str) -> None:
    """Create path must never update/delete/rename/mutate existing vendor/legacy campaigns."""
    lowered = operation.lower()
    forbidden = ("update", "delete", "remove", "rename", "enable", "mutate_existing")
    if any(token in lowered for token in forbidden):
        raise MutationSafetyError(
            f"Refusing operation that would mutate existing resources: {operation}. "
            "Only create-new + skip-existing is allowed."
        )


def confirm_customer_id(expected: str, provided: str | None) -> None:
    expected_clean = assert_customer_allowlisted(expected)
    if provided is None or str(provided).strip() != expected_clean:
        raise MutationSafetyError(
            f"Customer ID confirmation failed. Expected {expected_clean}, got {provided!r}. "
            f"Pass --confirm-customer-id {expected_clean}."
        )
    assert_customer_allowlisted(str(provided).strip())


def is_bakersfield_campaign(name: str, *, city: str | None = None) -> bool:
    if city and str(city).strip().lower() == "bakersfield":
        return True
    markers = BAKERSFIELD_ACTIVATION_HOLD["campaign_name_markers"]
    return any(marker in (name or "") for marker in markers)


def assert_bakersfield_enable_allowed(
    campaign_names: list[str],
    *,
    vendor_shutdown_acknowledged: bool = False,
) -> None:
    """Guard for future bulk-enable paths — enabling is not implemented yet.

    Bakersfield campaigns cannot be included in an enable set unless the caller
    passes ``vendor_shutdown_acknowledged=True`` (a separate explicit vendor
    shutdown acknowledgement). This function never enables anything.
    """
    held = [name for name in campaign_names if is_bakersfield_campaign(name)]
    if not held:
        return
    if not vendor_shutdown_acknowledged:
        raise MutationSafetyError(
            "Bakersfield activation hold is active. Refusing enable for: "
            + ", ".join(held)
            + ". Requires explicit vendor_shutdown_acknowledged=True. "
            + BAKERSFIELD_ACTIVATION_HOLD["reason"]
        )
    if not BAKERSFIELD_ACTIVATION_HOLD.get("enable_implemented"):
        raise MutationSafetyError(
            "Bakersfield vendor acknowledgement was provided, but enable is not "
            "implemented in this toolkit version. Create remains PAUSED-only."
        )


def bakersfield_hold_metadata_for_spec(
    *, name: str, city: str | None = None
) -> dict[str, Any] | None:
    if not is_bakersfield_campaign(name, city=city):
        return None
    return {
        **BAKERSFIELD_ACTIVATION_HOLD,
        "campaign_name": name,
        "city": city,
        "note": (
            "Created/skipped under activation hold. Future bulk-enable must call "
            "assert_bakersfield_enable_allowed with vendor_shutdown_acknowledged."
        ),
    }
