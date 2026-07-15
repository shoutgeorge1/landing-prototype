"""Mutation guard validators."""

from __future__ import annotations

from ela_google_ads.exceptions import MutationSafetyError
from ela_google_ads.models.spec import ALLOWED_CHANNELS, ALLOWED_MATCH_TYPES, CampaignSpec
from ela_google_ads.safety import (
    MutationContext,
    assert_customer_allowlisted,
    assert_ela_nonbrand_search_name,
    assert_mutation_allowed,
    assert_new_campaign_paused,
    assert_no_delete,
    assert_no_existing_resource_mutation,
    assert_status_not_enabled,
)


def guard_execute_attempt(
    *,
    customer_id: str,
    operation: str,
    execute: bool,
    dry_run: bool = True,
    validate_only: bool = True,
) -> MutationContext:
    """Authorize or refuse a mutation attempt.

    Dry-run (execute=False) never mutates. Live execute requires allowlisted
    customer and dry_run=False; callers still run validate_only mutate first.
    """
    assert_customer_allowlisted(customer_id)
    assert_no_delete(operation)
    assert_no_existing_resource_mutation(operation)

    ctx = MutationContext(
        customer_id=customer_id,
        operation=operation,
        execute=execute,
        dry_run=False if execute else dry_run,
        # Live execute path still runs a separate validate_only mutate first;
        # the authorization context itself is not validate_only.
        validate_only=False if execute else validate_only,
    )
    if execute:
        assert_mutation_allowed(ctx)
    elif ctx.will_mutate:  # pragma: no cover
        raise MutationSafetyError("Internal safety invariant broken")
    return ctx


def guard_apply_attempt(
    *,
    customer_id: str,
    operation: str,
    apply: bool,
    dry_run: bool = True,
    validate_only: bool = True,
) -> MutationContext:
    """Back-compat wrapper — prefer ``guard_execute_attempt``."""
    return guard_execute_attempt(
        customer_id=customer_id,
        operation=operation,
        execute=apply,
        dry_run=dry_run,
        validate_only=validate_only,
    )


def guard_new_campaign_status(status: str) -> None:
    assert_new_campaign_paused(status)
    assert_status_not_enabled(status, resource="campaign")


def guard_create_spec(spec: CampaignSpec) -> None:
    """Hard guards for the create path beyond offline YAML validation."""
    guard_new_campaign_status(spec.status)
    assert_ela_nonbrand_search_name(spec.name)
    if spec.channel not in ALLOWED_CHANNELS:
        raise MutationSafetyError(
            f"Create path is Search-only; refused channel {spec.channel!r}."
        )
    if not spec.network.target_google_search:
        raise MutationSafetyError("target_google_search must be true")
    if spec.network.target_search_network:
        raise MutationSafetyError("Search Partners (target_search_network) must be false")
    if spec.network.target_content_network:
        raise MutationSafetyError("Display/content network must be false")
    if not spec.location_presence_only:
        raise MutationSafetyError("location_presence_only (presence-only geo) is required")
    if (spec.brand.internal_campaign_type or "").lower() != "nonbrand":
        raise MutationSafetyError("Only Nonbrand campaigns may be created")

    for ag in spec.ad_groups:
        for kw in ag.keywords:
            if kw.match_type.upper() not in ALLOWED_MATCH_TYPES:
                raise MutationSafetyError(
                    f"Match type {kw.match_type!r} refused; exact/phrase only."
                )
