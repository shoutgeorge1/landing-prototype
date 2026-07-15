"""Tests for campaign-spec validation (offline, no API)."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from ela_google_ads.builders.campaign import build_campaign_preview, refuse_create_without_apply
from ela_google_ads.exceptions import ValidationError
from ela_google_ads.models.spec import campaign_spec_from_dict
from ela_google_ads.validators.spec_validators import (
    assert_spec_valid,
    find_positive_negative_conflicts,
    validate_campaign_spec,
    validate_rsa,
)

SPECS_DIR = Path(__file__).resolve().parents[1] / "specs"


def _base_spec_dict() -> dict:
    return {
        "name": "ELA | Search | Test | EN | Nonbrand",
        "status": "PAUSED",
        "channel": "SEARCH",
        "language": "en",
        "daily_budget": 25.0,
        "geo_target_names": ["Bakersfield, California"],
        "location_presence_only": True,
        "language_ids": [1000],
        "final_url": "https://help.employmentlawassist.com/bakersfield/en",
        "brand": {
            "brand_lane_owner": "hawksem",
            "internal_campaign_type": "nonbrand",
        },
        "network": {
            "target_google_search": True,
            "target_search_network": False,
            "target_content_network": False,
        },
        "ad_groups": [
            {
                "name": "Employment Lawyer",
                "keywords": [
                    {"text": "employment lawyer bakersfield", "match_type": "PHRASE"},
                    {"text": "bakersfield employment lawyer", "match_type": "EXACT"},
                ],
                "rsa": {
                    "headlines": [
                        "Employment Lawyer Nearby",
                        "Bakersfield Work Lawyer",
                        "Employee Rights Guidance",
                    ],
                    "descriptions": [
                        "Were you fired or unpaid at work? Get a confidential case review today.",
                        "Employment Law Assist helps California employees understand options.",
                    ],
                },
            }
        ],
    }


def test_bakersfield_en_spec_validates() -> None:
    assert_spec_valid(SPECS_DIR / "bakersfield-en.yaml")


def test_bakersfield_es_spec_validates() -> None:
    assert_spec_valid(SPECS_DIR / "bakersfield-es.yaml")


def test_english_and_spanish_specs_are_separated() -> None:
    en = yaml.safe_load((SPECS_DIR / "bakersfield-en.yaml").read_text(encoding="utf-8"))
    es = yaml.safe_load((SPECS_DIR / "bakersfield-es.yaml").read_text(encoding="utf-8"))
    assert en["language"] == "en"
    assert es["language"] == "es"
    assert en["final_url"].endswith("/en")
    assert es["final_url"].endswith("/es")
    assert en["language_ids"] == [1000]
    assert es["language_ids"] == [1003]
    assert "Employment Lawyer" in {ag["name"] for ag in en["ad_groups"]}
    assert "Abogado Laboral" in {ag["name"] for ag in es["ad_groups"]}


def test_market_matrix_has_valid_en_es_specs() -> None:
    matrix = yaml.safe_load((SPECS_DIR / "markets.yaml").read_text(encoding="utf-8"))
    markets = matrix["markets"]
    assert len(markets) == 14

    for market in markets:
        slug = market["slug"]
        for language, language_id in (("en", 1000), ("es", 1003)):
            path = SPECS_DIR / f"{slug}-{language}.yaml"
            spec = assert_spec_valid(path)
            assert spec.status == "PAUSED"
            assert spec.channel == "SEARCH"
            assert spec.city == slug
            assert spec.language_ids == [language_id]
            assert spec.geo_target_ids == market["geo_target_ids"]
            assert spec.location_presence_only is True
            assert spec.final_url == (
                f"https://help.employmentlawassist.com/{slug}/{language}"
            )
            assert spec.network.target_search_network is False
            assert spec.network.target_content_network is False
            match_types = {
                keyword.match_type
                for ad_group in spec.ad_groups
                for keyword in ad_group.keywords
            }
            assert match_types <= {
                "EXACT",
                "PHRASE",
            }


def test_overlapping_market_alternates_are_explicitly_marked() -> None:
    matrix = yaml.safe_load((SPECS_DIR / "markets.yaml").read_text(encoding="utf-8"))
    by_slug = {market["slug"]: market for market in matrix["markets"]}

    assert "palmdale" in by_slug["lancaster"]["do_not_launch_with"]
    assert "lancaster" in by_slug["palmdale"]["do_not_launch_with"]
    assert "fontana" in by_slug["san-bernardino"]["do_not_launch_with"]
    assert "ontario" in by_slug["san-bernardino"]["do_not_launch_with"]


def test_invalid_daily_budget() -> None:
    data = _base_spec_dict()
    data["daily_budget"] = 0
    issues = validate_campaign_spec(campaign_spec_from_dict(data))
    assert any("daily_budget" in i for i in issues)


def test_duplicate_ad_group_names() -> None:
    data = _base_spec_dict()
    data["ad_groups"].append(deepcopy(data["ad_groups"][0]))
    issues = validate_campaign_spec(campaign_spec_from_dict(data))
    assert any("Duplicate ad-group name" in i for i in issues)


def test_invalid_match_type_rejected() -> None:
    data = _base_spec_dict()
    data["ad_groups"][0]["keywords"][0]["match_type"] = "BROAD"
    issues = validate_campaign_spec(campaign_spec_from_dict(data))
    assert any("BROAD" in i for i in issues)


def test_missing_final_url() -> None:
    data = _base_spec_dict()
    data["final_url"] = ""
    data["ad_groups"][0]["final_url"] = ""
    issues = validate_campaign_spec(campaign_spec_from_dict(data))
    assert any("final_url" in i for i in issues)


def test_invalid_language_configuration() -> None:
    data = _base_spec_dict()
    data["language_ids"] = []
    issues = validate_campaign_spec(campaign_spec_from_dict(data))
    assert any("language_ids" in i for i in issues)


def test_invalid_geo_configuration() -> None:
    data = _base_spec_dict()
    data["geo_target_ids"] = []
    data["geo_target_names"] = []
    issues = validate_campaign_spec(campaign_spec_from_dict(data))
    assert any("geo_target" in i for i in issues)


def test_campaign_status_must_be_paused() -> None:
    data = _base_spec_dict()
    data["status"] = "ENABLED"
    issues = validate_campaign_spec(campaign_spec_from_dict(data))
    assert any("PAUSED" in i for i in issues)


def test_brand_exclusions_required() -> None:
    data = _base_spec_dict()
    data["brand"]["internal_campaign_type"] = "brand"
    issues = validate_campaign_spec(campaign_spec_from_dict(data))
    assert any("nonbrand" in i for i in issues)


def test_positive_negative_keyword_conflicts() -> None:
    data = _base_spec_dict()
    data["campaign_negative_keywords"] = [
        {"text": "employment lawyer bakersfield", "match_type": "EXACT"}
    ]
    spec = campaign_spec_from_dict(data)
    conflicts = find_positive_negative_conflicts(spec)
    assert conflicts


def test_rsa_character_limits() -> None:
    class FakeRsa:
        headlines = ["x" * 31]
        descriptions = ["y" * 20, "z" * 20]
        path1 = None
        path2 = None
        pinned_headlines = {}

    issues = validate_rsa(FakeRsa(), ad_group="Test")
    assert any("30" in i for i in issues)


def test_rsa_missing_copy_fails() -> None:
    data = _base_spec_dict()
    data["ad_groups"][0]["rsa"] = None
    issues = validate_campaign_spec(campaign_spec_from_dict(data))
    assert any("missing RSA" in i for i in issues)


def test_placeholder_copy_rejected() -> None:
    data = _base_spec_dict()
    data["ad_groups"][0]["rsa"]["headlines"][0] = "TODO headline here"
    issues = validate_campaign_spec(campaign_spec_from_dict(data))
    assert any("placeholder" in i.lower() for i in issues)


def test_policy_risk_guaranteed_language() -> None:
    data = _base_spec_dict()
    data["ad_groups"][0]["rsa"]["headlines"][0] = "Guaranteed Results Here"
    issues = validate_campaign_spec(campaign_spec_from_dict(data))
    assert any("policy risk" in i.lower() for i in issues)


def test_preview_does_not_mutate() -> None:
    spec = campaign_spec_from_dict(_base_spec_dict())
    preview = build_campaign_preview(spec)
    assert preview["will_mutate"] is False
    assert preview["requires_execute"] is True


def test_create_refuse_helper_points_to_execute() -> None:
    result = refuse_create_without_apply(apply=True)
    assert result["mutated"] is False
    assert "execute" in result["message"].lower()


def test_assert_spec_valid_raises() -> None:
    data = _base_spec_dict()
    data["daily_budget"] = -1
    # Write temp invalid and assert
    path = SPECS_DIR / "_tmp_invalid_spec.yaml"
    try:
        path.write_text(yaml.safe_dump(data), encoding="utf-8")
        with pytest.raises(ValidationError):
            assert_spec_valid(path)
    finally:
        if path.exists():
            path.unlink()
