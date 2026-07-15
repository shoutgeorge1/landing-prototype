"""Environment-driven configuration for Google Ads API access."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from ela_google_ads.exceptions import ConfigurationError, CredentialRequiredError

# Digits-only Google Ads customer / manager IDs (10 digits typical; allow 1–12).
_CUSTOMER_ID_RE = re.compile(r"^\d{1,12}$")
_PLACEHOLDER_LOGIN = "REPLACE_WITH_MCC_ID"

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def normalize_customer_id(raw: str | None, *, field_name: str = "customer_id") -> str:
    """Strip dashes/spaces and validate a Google Ads customer ID."""
    if raw is None or not str(raw).strip():
        raise ConfigurationError(f"{field_name} is required")

    cleaned = re.sub(r"[\s\-]", "", str(raw).strip())
    if not _CUSTOMER_ID_RE.match(cleaned):
        raise ConfigurationError(
            f"{field_name} must be digits only (no dashes). Got: {raw!r}"
        )
    if "-" in str(raw):
        # Accept dashed input but always return normalized digits.
        pass
    return cleaned


def has_dashes(raw: str | None) -> bool:
    return bool(raw and "-" in str(raw))


@dataclass(frozen=True)
class GoogleAdsSettings:
    """Loaded settings. Secrets are never logged."""

    developer_token: str
    client_id: str
    client_secret: str
    refresh_token: str
    login_customer_id: str | None
    customer_id: str
    use_proto_plus: bool
    output_dir: Path
    call_tracking_phone: str | None
    oauth_client_secrets_file: Path | None

    def missing_required_fields(self) -> list[str]:
        missing: list[str] = []
        if not self.developer_token:
            missing.append("GOOGLE_ADS_DEVELOPER_TOKEN")
        if not self.client_id:
            missing.append("GOOGLE_ADS_CLIENT_ID")
        if not self.client_secret:
            missing.append("GOOGLE_ADS_CLIENT_SECRET")
        if not self.refresh_token:
            missing.append("GOOGLE_ADS_REFRESH_TOKEN")
        if not self.customer_id:
            missing.append("GOOGLE_ADS_CUSTOMER_ID")
        return missing

    def require_live_credentials(self) -> None:
        missing = self.missing_required_fields()
        if missing:
            raise CredentialRequiredError(
                "Live Google Ads credentials are required. Missing: "
                + ", ".join(missing)
                + ". Copy tools/google-ads/.env.example to .env and fill values. "
                "Generate a refresh token with: python scripts/generate_refresh_token.py"
            )
        if self.login_customer_id in (None, "", _PLACEHOLDER_LOGIN):
            # Many accounts still work without MCC if OAuth user has direct access;
            # warn via exception only when caller requires MCC.
            pass

    def require_login_customer_id(self) -> str:
        if not self.login_customer_id or self.login_customer_id == _PLACEHOLDER_LOGIN:
            raise ConfigurationError(
                "GOOGLE_ADS_LOGIN_CUSTOMER_ID is still a placeholder. "
                "Provide your MCC (manager) customer ID as digits only, e.g. 1234567890."
            )
        return self.login_customer_id

    def to_client_dict(self, *, include_login_customer_id: bool = True) -> dict:
        self.require_live_credentials()
        data: dict = {
            "developer_token": self.developer_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "use_proto_plus": self.use_proto_plus,
        }
        if include_login_customer_id and self.login_customer_id:
            if self.login_customer_id != _PLACEHOLDER_LOGIN:
                data["login_customer_id"] = self.login_customer_id
        return data


def _truthy(value: str | None, default: bool = True) -> bool:
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def find_env_file(start: Path | None = None) -> Path | None:
    """Search for .env near the toolkit root, then process cwd."""
    candidates = []
    if start:
        candidates.append(start)
    candidates.extend(
        [
            PACKAGE_ROOT / ".env",
            Path.cwd() / ".env",
            Path.cwd() / "tools" / "google-ads" / ".env",
        ]
    )
    for path in candidates:
        if path.is_file():
            return path
    return None


def load_settings(
    *,
    env_file: Path | str | None = None,
    override: bool = False,
) -> GoogleAdsSettings:
    """Load settings from environment / .env without requiring all secrets."""
    if env_file:
        load_dotenv(env_file, override=override)
    else:
        found = find_env_file()
        if found:
            load_dotenv(found, override=override)

    raw_customer = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "6769947952")
    customer_id = normalize_customer_id(raw_customer, field_name="GOOGLE_ADS_CUSTOMER_ID")

    raw_login = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", _PLACEHOLDER_LOGIN)
    login_customer_id: str | None
    if not raw_login or raw_login.strip() == _PLACEHOLDER_LOGIN:
        login_customer_id = _PLACEHOLDER_LOGIN
    else:
        login_customer_id = normalize_customer_id(
            raw_login, field_name="GOOGLE_ADS_LOGIN_CUSTOMER_ID"
        )

    output_raw = os.getenv("ELA_GOOGLE_ADS_OUTPUT_DIR", "output")
    output_dir = Path(output_raw)
    if not output_dir.is_absolute():
        output_dir = PACKAGE_ROOT / output_dir

    secrets_path = os.getenv("GOOGLE_ADS_OAUTH_CLIENT_SECRETS_FILE")
    oauth_file = Path(secrets_path) if secrets_path else None

    phone = os.getenv("ELA_CALL_TRACKING_PHONE") or os.getenv("ELA_PHONE_NUMBER")
    if phone:
        phone = re.sub(r"[^\d+]", "", phone)

    return GoogleAdsSettings(
        developer_token=os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "").strip(),
        client_id=os.getenv("GOOGLE_ADS_CLIENT_ID", "").strip(),
        client_secret=os.getenv("GOOGLE_ADS_CLIENT_SECRET", "").strip(),
        refresh_token=os.getenv("GOOGLE_ADS_REFRESH_TOKEN", "").strip(),
        login_customer_id=login_customer_id,
        customer_id=customer_id,
        use_proto_plus=_truthy(os.getenv("GOOGLE_ADS_USE_PROTO_PLUS"), True),
        output_dir=output_dir,
        call_tracking_phone=phone,
        oauth_client_secrets_file=oauth_file,
    )
