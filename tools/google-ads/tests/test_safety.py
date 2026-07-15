"""Tests for mutation safety guards."""

from __future__ import annotations

import pytest

from ela_google_ads.exceptions import MutationSafetyError
from ela_google_ads.safety import (
    MutationContext,
    assert_customer_allowlisted,
    assert_explicit_resource_id,
    assert_mutation_allowed,
    assert_new_campaign_paused,
    assert_no_delete,
    confirm_customer_id,
)
from ela_google_ads.validators.mutation_guards import (
    guard_apply_attempt,
    guard_execute_attempt,
)


def test_mutation_blocked_without_execute() -> None:
    ctx = MutationContext(customer_id="6769947952", operation="create", execute=False)
    with pytest.raises(MutationSafetyError):
        assert_mutation_allowed(ctx)


def test_mutation_blocked_when_dry_run() -> None:
    ctx = MutationContext(
        customer_id="6769947952",
        operation="create",
        execute=True,
        dry_run=True,
        validate_only=False,
    )
    with pytest.raises(MutationSafetyError):
        assert_mutation_allowed(ctx)


def test_guard_execute_attempt_dry_run_ok() -> None:
    ctx = guard_execute_attempt(
        customer_id="6769947952",
        operation="campaigns.create",
        execute=False,
    )
    assert ctx.execute is False
    assert ctx.will_mutate is False


def test_guard_apply_attempt_back_compat() -> None:
    ctx = guard_apply_attempt(
        customer_id="6769947952",
        operation="campaigns.create",
        apply=False,
    )
    assert ctx.apply is False
    assert ctx.will_mutate is False


def test_new_campaign_must_be_paused() -> None:
    with pytest.raises(MutationSafetyError):
        assert_new_campaign_paused("ENABLED")
    assert_new_campaign_paused("PAUSED")


def test_no_delete_commands() -> None:
    with pytest.raises(MutationSafetyError):
        assert_no_delete("campaigns.delete")


def test_explicit_resource_id_required() -> None:
    with pytest.raises(MutationSafetyError):
        assert_explicit_resource_id(None, action="update campaign")
    assert assert_explicit_resource_id("123", action="update") == "123"


def test_confirm_customer_id() -> None:
    confirm_customer_id("6769947952", "6769947952")
    with pytest.raises(MutationSafetyError):
        confirm_customer_id("6769947952", "999")


def test_allowlist() -> None:
    assert_customer_allowlisted("6769947952")
    with pytest.raises(MutationSafetyError):
        assert_customer_allowlisted("0000000000")
