"""Config / customer-ID validators."""

from __future__ import annotations

from ela_google_ads.config import has_dashes, normalize_customer_id
from ela_google_ads.exceptions import ConfigurationError


def validate_customer_id_input(raw: str | None, *, field_name: str = "customer_id") -> str:
    """Normalize and validate; used by tests and CLI."""
    if has_dashes(raw):
        # Allowed as input — normalize — but scripts should prefer digits-only in .env.
        pass
    return normalize_customer_id(raw, field_name=field_name)


def require_credentials_present(missing: list[str]) -> None:
    if missing:
        raise ConfigurationError(
            "Missing required credentials: " + ", ".join(missing)
        )
