"""Tests for configuration and customer ID normalization."""

from __future__ import annotations

from pathlib import Path

import pytest

from ela_google_ads.config import load_settings, normalize_customer_id
from ela_google_ads.exceptions import ConfigurationError, CredentialRequiredError
from ela_google_ads.validators.config_validators import (
    require_credentials_present,
    validate_customer_id_input,
)


def test_normalize_strips_dashes() -> None:
    assert normalize_customer_id("676-994-7952") == "6769947952"


def test_normalize_rejects_empty() -> None:
    with pytest.raises(ConfigurationError):
        normalize_customer_id("")


def test_normalize_rejects_letters() -> None:
    with pytest.raises(ConfigurationError):
        normalize_customer_id("6769947952abc")


def test_validate_customer_id_input_accepts_dashed() -> None:
    assert validate_customer_id_input("676-994-7952") == "6769947952"


def test_load_settings_default_customer(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("GOOGLE_ADS_CUSTOMER_ID", raising=False)
    monkeypatch.delenv("GOOGLE_ADS_DEVELOPER_TOKEN", raising=False)
    monkeypatch.chdir(tmp_path)
    settings = load_settings(env_file=None)
    assert settings.customer_id == "6769947952"


def test_missing_credentials_detected(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    for key in [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
    ]:
        monkeypatch.setenv(key, "")
    monkeypatch.setenv("GOOGLE_ADS_CUSTOMER_ID", "6769947952")
    settings = load_settings(env_file=None)
    missing = settings.missing_required_fields()
    assert "GOOGLE_ADS_DEVELOPER_TOKEN" in missing
    with pytest.raises(CredentialRequiredError):
        settings.require_live_credentials()


def test_require_credentials_present() -> None:
    with pytest.raises(ConfigurationError):
        require_credentials_present(["GOOGLE_ADS_REFRESH_TOKEN"])


def test_placeholder_login_customer_id(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "REPLACE_WITH_MCC_ID")
    monkeypatch.setenv("GOOGLE_ADS_CUSTOMER_ID", "6769947952")
    settings = load_settings(env_file=None)
    with pytest.raises(ConfigurationError):
        settings.require_login_customer_id()
