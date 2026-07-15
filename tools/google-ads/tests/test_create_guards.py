"""Mocked unit tests for guarded campaign create path (part 1)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from ela_google_ads.builders.mutate_ops import (
    budget_name_for_campaign,
    build_campaign_create_operations,
)
from ela_google_ads.config import GoogleAdsSettings
from ela_google_ads.exceptions import MutationSafetyError
from ela_google_ads.models.spec import campaign_spec_from_dict
from ela_google_ads.safety import (
    ALLOWED_MUTATION_CUSTOMER_IDS,
    assert_bakersfield_enable_allowed,
    assert_customer_allowlisted,
    assert_ela_nonbrand_search_name,
    assert_no_existing_resource_mutation,
    assert_status_not_enabled,
    bakersfield_hold_metadata_for_spec,
    confirm_customer_id,
    is_bakersfield_campaign,
)
from ela_google_ads.validators.mutation_guards import (
    guard_create_spec,
    guard_execute_attempt,
)
from tests.fake_google_ads import FakeGoogleAdsClient

SPECS_DIR = Path(__file__).resolve().parents[1] / "specs"
HOLD_META = SPECS_DIR / "shared" / "bakersfield-activation-hold.yaml"


def _settings(tmp_path: Path) -> GoogleAdsSettings:
    return GoogleAdsSettings(
        developer_token="dev",
        client_id="id",
        client_secret="secret",
        refresh_token="refresh",
        login_customer_id="1234567890",
        customer_id="6769947952",
        use_proto_plus=True,
        output_dir=tmp_path,
        call_tracking_phone=None,
        oauth_client_secrets_file=None,
    )


def _minimal_spec_dict(**overrides: object) -> dict:
    data: dict = {
        "name": "ELA | Search | Fresno | EN | Nonbrand",
        "status": "PAUSED",
        "channel": "SEARCH",
        "language": "en",
        "city": "fresno",
        "daily_budget": 50.0,
        "bidding_strategy": "MAXIMIZE_CLICKS",
        "geo_target_ids": [9057128],
        "geo_target_names": ["Fresno County, California, United States"],
        "location_presence_only": True,
        "language_ids": [1000],
        "final_url": "https://help.employmentlawassist.com/fresno/en",
        "brand": {
            "brand_lane_owner": "external_agency",
            "internal_campaign_type": "nonbrand",
        },
        "network": {
            "target_google_search": True,
            "target_search_network": False,
            "target_content_network": False,
        },
        "conversion_goals": ["7569909838"],
        "sitelinks": [
            {
                "link_text": "Free Case Review",
                "final_url": "https://help.employmentlawassist.com/fresno/en",
                "description1": "Tell us what happened.",
                "description2": "Confidential review.",
            }
        ],
        "callouts": ["Free Consultation"],
        "structured_snippets": [{"header": "Types", "values": ["Discrimination"]}],
        "ad_groups": [
            {
                "name": "Employment Lawyer",
                "keywords": [
                    {"text": "employment lawyer fresno", "match_type": "PHRASE"},
                    {"text": "fresno employment lawyer", "match_type": "EXACT"},
                ],
                "negative_keywords": [
                    {"text": "jobs", "match_type": "PHRASE"},
                ],
                "rsa": {
                    "headlines": [
                        "Employment Lawyer Nearby",
                        "Fresno Work Lawyer",
                        "Employee Rights Guidance",
                    ],
                    "descriptions": [
                        "Were you fired or unpaid at work? Get a confidential case review today.",
                        "Employment Law Assist helps California employees understand options.",
                    ],
                    "path1": "fresno",
                    "path2": "help",
                },
            }
        ],
    }
    data.update(overrides)
    return data


def test_customer_allowlist_hard() -> None:
    assert assert_customer_allowlisted("6769947952") == "6769947952"
    assert "6769947952" in ALLOWED_MUTATION_CUSTOMER_IDS
    with pytest.raises(MutationSafetyError):
        assert_customer_allowlisted("9999999999")


def test_confirm_customer_id_requires_allowlisted() -> None:
    confirm_customer_id("6769947952", "6769947952")
    with pytest.raises(MutationSafetyError):
        confirm_customer_id("6769947952", None)
    with pytest.raises(MutationSafetyError):
        confirm_customer_id("9999999999", "9999999999")


def test_execute_guard_default_dry_run() -> None:
    ctx = guard_execute_attempt(
        customer_id="6769947952",
        operation="campaigns.create",
        execute=False,
    )
    assert ctx.will_mutate is False
    assert ctx.execute is False


def test_execute_guard_authorizes_live() -> None:
    ctx = guard_execute_attempt(
        customer_id="6769947952",
        operation="campaigns.create",
        execute=True,
    )
    assert ctx.execute is True
    assert ctx.dry_run is False
    assert ctx.will_mutate is True


def test_execute_guard_refuses_non_allowlisted() -> None:
    with pytest.raises(MutationSafetyError):
        guard_execute_attempt(
            customer_id="1111111111",
            operation="campaigns.create",
            execute=True,
        )


def test_refuse_enabled_statuses() -> None:
    with pytest.raises(MutationSafetyError):
        assert_status_not_enabled("ENABLED", resource="campaign")
    with pytest.raises(MutationSafetyError):
        guard_create_spec(campaign_spec_from_dict(_minimal_spec_dict(status="ENABLED")))


def test_naming_pattern_enforced() -> None:
    assert_ela_nonbrand_search_name("ELA | Search | Fresno | EN | Nonbrand")
    with pytest.raises(MutationSafetyError):
        assert_ela_nonbrand_search_name("LAW2--Fresno--LabLw--26-05-13 ///")
    with pytest.raises(MutationSafetyError):
        guard_create_spec(
            campaign_spec_from_dict(
                _minimal_spec_dict(name="ELA | Search | Fresno | EN | Brand")
            )
        )


def test_search_partners_and_display_refused() -> None:
    data = _minimal_spec_dict()
    data["network"]["target_search_network"] = True
    with pytest.raises(MutationSafetyError):
        guard_create_spec(campaign_spec_from_dict(data))
    data = _minimal_spec_dict()
    data["network"]["target_content_network"] = True
    with pytest.raises(MutationSafetyError):
        guard_create_spec(campaign_spec_from_dict(data))


def test_presence_only_and_exact_phrase_only() -> None:
    data = _minimal_spec_dict(location_presence_only=False)
    with pytest.raises(MutationSafetyError):
        guard_create_spec(campaign_spec_from_dict(data))
    data = _minimal_spec_dict()
    data["ad_groups"][0]["keywords"][0]["match_type"] = "BROAD"
    with pytest.raises(MutationSafetyError):
        guard_create_spec(campaign_spec_from_dict(data))


def test_budget_name_deterministic() -> None:
    assert (
        budget_name_for_campaign("ELA | Search | Fresno | EN | Nonbrand")
        == "ELA | Budget | Fresno | EN | Nonbrand"
    )


def test_bakersfield_hold_metadata_and_guard() -> None:
    assert HOLD_META.is_file()
    meta = yaml.safe_load(HOLD_META.read_text(encoding="utf-8"))
    assert meta["hold"]["active"] is True
    assert meta["hold"]["required_acknowledgement_flag"] == "vendor_shutdown_acknowledged"
    assert meta["hold"]["enable_implemented"] is False

    assert is_bakersfield_campaign("ELA | Search | Bakersfield | EN | Nonbrand")
    hold = bakersfield_hold_metadata_for_spec(
        name="ELA | Search | Bakersfield | EN | Nonbrand",
        city="bakersfield",
    )
    assert hold is not None
    assert hold["active"] is True

    with pytest.raises(MutationSafetyError, match="activation hold"):
        assert_bakersfield_enable_allowed(
            ["ELA | Search | Bakersfield | EN | Nonbrand"],
            vendor_shutdown_acknowledged=False,
        )
    with pytest.raises(MutationSafetyError, match="not implemented"):
        assert_bakersfield_enable_allowed(
            ["ELA | Search | Bakersfield | EN | Nonbrand"],
            vendor_shutdown_acknowledged=True,
        )
    assert_bakersfield_enable_allowed(
        ["ELA | Search | Fresno | EN | Nonbrand"],
        vendor_shutdown_acknowledged=False,
    )


def test_build_operations_all_paused_where_supported() -> None:
    client = FakeGoogleAdsClient()
    spec = campaign_spec_from_dict(_minimal_spec_dict())
    plan = build_campaign_create_operations(
        client,
        customer_id="6769947952",
        spec=spec,
    )
    assert plan.operations
    assert plan.campaign_resource_name
    assert any(r["type"] == "campaign" and r["status"] == "PAUSED" for r in plan.planned_resources)
    assert any(r["type"] == "ad_group" and r["status"] == "PAUSED" for r in plan.planned_resources)
    assert any(
        r["type"] == "ad_group_criterion.keyword" and r["status"] == "PAUSED"
        for r in plan.planned_resources
    )
    assert any(
        r["type"] == "ad_group_ad.rsa" and r["status"] == "PAUSED"
        for r in plan.planned_resources
    )
    assert any(
        r["type"].startswith("campaign_asset.") and r["status"] == "PAUSED"
        for r in plan.planned_resources
    )
    assert any(
        r["type"] == "campaign_budget" and r["status"] == "ENABLED"
        for r in plan.planned_resources
    )

    campaign_ops = [
        op for op in plan.operations if op.campaign_operation.create.name == spec.name
    ]
    assert campaign_ops
    assert campaign_ops[0].campaign_operation.create.status.name == "PAUSED"
    net = campaign_ops[0].campaign_operation.create.network_settings
    assert net.target_google_search is True
    assert net.target_search_network is False
    assert net.target_content_network is False
    assert net.target_partner_search_network is False
    geo = campaign_ops[0].campaign_operation.create.geo_target_type_setting
    assert geo.positive_geo_target_type.name == "PRESENCE"

    for op in plan.operations:
        if op.ad_group_operation.create.name:
            assert op.ad_group_operation.create.status.name == "PAUSED"
        if op.ad_group_ad_operation.create.ad_group:
            assert op.ad_group_ad_operation.create.status.name == "PAUSED"
        if (
            op.ad_group_criterion_operation.create.ad_group
            and not op.ad_group_criterion_operation.create.negative
            and op.ad_group_criterion_operation.create.keyword.text
        ):
            assert op.ad_group_criterion_operation.create.status.name == "PAUSED"
        if op.campaign_asset_operation.create.asset:
            assert op.campaign_asset_operation.create.status.name == "PAUSED"


def test_refuse_update_delete_operations() -> None:
    with pytest.raises(MutationSafetyError):
        assert_no_existing_resource_mutation("campaigns.update")
    with pytest.raises(MutationSafetyError):
        assert_no_existing_resource_mutation("campaigns.delete")
    with pytest.raises(MutationSafetyError):
        assert_no_existing_resource_mutation("campaigns.enable")


def test_guard_blocks_mutate_existing_operation_name() -> None:
    with pytest.raises(MutationSafetyError):
        guard_execute_attempt(
            customer_id="6769947952",
            operation="campaigns.mutate_existing",
            execute=False,
        )
