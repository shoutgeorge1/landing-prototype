"""Tests for tracking preview helpers."""

from __future__ import annotations

from ela_google_ads.builders.tracking import append_suffix, build_final_url_suffix, preview_tracking
from ela_google_ads.models.spec import campaign_spec_from_dict


def test_final_url_suffix_includes_hubspot_keys() -> None:
    suffix = build_final_url_suffix(
        campaign_name="ELA Search Bakersfield EN",
        ad_group_name="Wrongful Termination",
    )
    assert "google_campaign=" in suffix
    assert "google_ad_group=" in suffix
    assert "google_keyword=" in suffix
    assert "wrongful_termination" in suffix


def test_append_suffix_does_not_overwrite_existing() -> None:
    url = "https://help.employmentlawassist.com/bakersfield/en?utm_source=existing"
    out = append_suffix(url, "utm_source=google&utm_medium=cpc")
    assert "utm_source=existing" in out
    assert "utm_medium=cpc" in out


def test_preview_tracking_rows() -> None:
    spec = campaign_spec_from_dict(
        {
            "name": "ELA | Search | Bakersfield | EN | Nonbrand",
            "final_url": "https://help.employmentlawassist.com/bakersfield/en",
            "ad_groups": [{"name": "Employment Lawyer", "keywords": [], "rsa": {}}],
            "tracking": {},
        }
    )
    rows = preview_tracking(spec)
    assert rows
    assert rows[0]["final_url"].startswith("https://")
