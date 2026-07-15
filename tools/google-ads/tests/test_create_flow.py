"""Mocked unit tests for create orchestration (dry-run / execute / skip)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from ela_google_ads.campaigns.create import (
    create_campaign_from_spec,
    find_budget_by_exact_name,
    find_campaign_by_exact_name,
)
from ela_google_ads.exceptions import MutationSafetyError
from tests.fake_google_ads import FakeGoogleAdsClient
from tests.test_create_guards import _minimal_spec_dict, _settings


def _write_spec(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "spec.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def test_find_campaign_exact_name(monkeypatch: pytest.MonkeyPatch) -> None:
    client = FakeGoogleAdsClient()

    def fake_run_gaql(_client, _cid, query):
        assert "ELA | Search | Fresno | EN | Nonbrand" in query
        yield SimpleNamespace(
            campaign=SimpleNamespace(
                id=111,
                name="ELA | Search | Fresno | EN | Nonbrand",
                status=SimpleNamespace(name="PAUSED"),
                resource_name="customers/6769947952/campaigns/111",
            )
        )

    monkeypatch.setattr("ela_google_ads.campaigns.create.run_gaql", fake_run_gaql)
    found = find_campaign_by_exact_name(
        client, "6769947952", "ELA | Search | Fresno | EN | Nonbrand"
    )
    assert found is not None
    assert found["campaign_id"] == "111"


def test_find_budget_exact_name(monkeypatch: pytest.MonkeyPatch) -> None:
    client = FakeGoogleAdsClient()

    def fake_run_gaql(_client, _cid, query):
        assert "ELA | Budget | Fresno | EN | Nonbrand" in query
        yield SimpleNamespace(
            campaign_budget=SimpleNamespace(
                id=222,
                name="ELA | Budget | Fresno | EN | Nonbrand",
                resource_name="customers/6769947952/campaignBudgets/222",
                amount_micros=50_000_000,
                status=SimpleNamespace(name="ENABLED"),
            )
        )

    monkeypatch.setattr("ela_google_ads.campaigns.create.run_gaql", fake_run_gaql)
    found = find_budget_by_exact_name(
        client, "6769947952", "ELA | Budget | Fresno | EN | Nonbrand"
    )
    assert found is not None
    assert found["budget_id"] == "222"


def _stub_lookups(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ela_google_ads.campaigns.create.find_campaign_by_exact_name",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "ela_google_ads.campaigns.create.find_budget_by_exact_name",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "ela_google_ads.campaigns.create.find_custom_goal_by_exact_name",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "ela_google_ads.campaigns.create.attach_locked_campaign_negatives",
        lambda *a, **k: 0,
    )


def test_dry_run_validate_only_no_execute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _settings(tmp_path)
    spec_path = _write_spec(tmp_path, _minimal_spec_dict())
    client = FakeGoogleAdsClient()
    _stub_lookups(monkeypatch)

    result = create_campaign_from_spec(
        settings,
        spec_path,
        execute=False,
        client=client,
        out_dir=tmp_path,
    )
    assert result["mode"] == "dry_run"
    assert result["mutated"] is False
    assert result["validate_only_ok"] is True
    assert result["will_mutate"] is False
    assert Path(result["log_path"]).is_file()
    assert len(client.google_ads_service.calls) == 1
    assert client.google_ads_service.calls[0]["validate_only"] is True


def test_skip_existing_campaign_no_mutate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _settings(tmp_path)
    spec_path = _write_spec(tmp_path, _minimal_spec_dict())
    client = FakeGoogleAdsClient()

    monkeypatch.setattr(
        "ela_google_ads.campaigns.create.find_campaign_by_exact_name",
        lambda *a, **k: {
            "campaign_id": "999",
            "campaign_name": "ELA | Search | Fresno | EN | Nonbrand",
            "status": "PAUSED",
            "resource_name": "customers/6769947952/campaigns/999",
        },
    )

    result = create_campaign_from_spec(
        settings,
        spec_path,
        execute=True,
        confirm_customer_id_value="6769947952",
        client=client,
        out_dir=tmp_path,
    )
    assert result["skipped"] is True
    assert result["mutated"] is False
    assert result["resources"]["skipped"]
    assert client.google_ads_service.calls == []


def test_execute_runs_validate_only_then_mutate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _settings(tmp_path)
    spec_path = _write_spec(tmp_path, _minimal_spec_dict())
    client = FakeGoogleAdsClient()
    client.google_ads_service.execute_response = SimpleNamespace(
        mutate_operation_responses=[
            SimpleNamespace(
                campaign_result=SimpleNamespace(
                    resource_name="customers/6769947952/campaigns/1"
                ),
                campaign_budget_result=None,
                campaign_criterion_result=None,
                campaign_asset_result=None,
                asset_result=None,
                ad_group_result=None,
                ad_group_criterion_result=None,
                ad_group_ad_result=None,
            )
        ]
    )
    _stub_lookups(monkeypatch)

    result = create_campaign_from_spec(
        settings,
        spec_path,
        execute=True,
        confirm_customer_id_value="6769947952",
        client=client,
        out_dir=tmp_path,
    )
    assert result["mutated"] is True
    assert result["validate_only_ok"] is True
    assert len(client.google_ads_service.calls) == 2
    assert client.google_ads_service.calls[0]["validate_only"] is True
    assert client.google_ads_service.calls[1]["validate_only"] is False
    assert any(
        c.get("resource_name") == "customers/6769947952/campaigns/1"
        for c in result["resources"]["created"]
    )
    log = Path(result["log_path"])
    assert log.is_file()
    assert "campaign_create_" in log.name


def test_execute_requires_confirm_customer_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _settings(tmp_path)
    spec_path = _write_spec(tmp_path, _minimal_spec_dict())
    client = FakeGoogleAdsClient()
    monkeypatch.setattr(
        "ela_google_ads.campaigns.create.find_campaign_by_exact_name",
        lambda *a, **k: None,
    )
    with pytest.raises(MutationSafetyError, match="confirmation failed"):
        create_campaign_from_spec(
            settings,
            spec_path,
            execute=True,
            confirm_customer_id_value=None,
            client=client,
            out_dir=tmp_path,
        )


def test_bakersfield_create_includes_hold_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _settings(tmp_path)
    data = _minimal_spec_dict(
        name="ELA | Search | Bakersfield | EN | Nonbrand",
        city="bakersfield",
        geo_target_ids=[9057133],
        final_url="https://help.employmentlawassist.com/bakersfield/en",
    )
    data["ad_groups"][0]["keywords"][0]["text"] = "employment lawyer bakersfield"
    data["ad_groups"][0]["final_url"] = data["final_url"]
    spec_path = _write_spec(tmp_path, data)
    client = FakeGoogleAdsClient()
    _stub_lookups(monkeypatch)
    result = create_campaign_from_spec(
        settings,
        spec_path,
        execute=False,
        client=client,
        out_dir=tmp_path,
    )
    assert result["bakersfield_activation_hold"] is not None
    assert result["bakersfield_activation_hold"]["active"] is True


def test_reuse_existing_budget_avoids_duplicate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _settings(tmp_path)
    spec_path = _write_spec(tmp_path, _minimal_spec_dict())
    client = FakeGoogleAdsClient()
    monkeypatch.setattr(
        "ela_google_ads.campaigns.create.find_campaign_by_exact_name",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "ela_google_ads.campaigns.create.find_budget_by_exact_name",
        lambda *a, **k: {
            "budget_id": "55",
            "budget_name": "ELA | Budget | Fresno | EN | Nonbrand",
            "resource_name": "customers/6769947952/campaignBudgets/55",
            "amount_micros": 50_000_000,
            "status": "ENABLED",
        },
    )
    monkeypatch.setattr(
        "ela_google_ads.campaigns.create.find_custom_goal_by_exact_name",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "ela_google_ads.campaigns.create.attach_locked_campaign_negatives",
        lambda *a, **k: 0,
    )
    result = create_campaign_from_spec(
        settings,
        spec_path,
        execute=False,
        client=client,
        out_dir=tmp_path,
    )
    assert result["resources"]["reused"]
    assert result["resources"]["reused"][0]["budget_id"] == "55"
    budget_creates = [
        op
        for op in client.google_ads_service.calls[0]["mutate_operations"]
        if op.campaign_budget_operation.create.name
    ]
    assert budget_creates == []
