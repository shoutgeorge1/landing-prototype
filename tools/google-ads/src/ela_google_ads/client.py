"""Google Ads API client factory and GAQL helpers."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from ela_google_ads.config import GoogleAdsSettings
from ela_google_ads.exceptions import ApiAccessError, CredentialRequiredError
from ela_google_ads.logging_config import get_logger

if TYPE_CHECKING:
    from google.ads.googleads.client import GoogleAdsClient

logger = get_logger(__name__)


def build_client(
    settings: GoogleAdsSettings,
    *,
    include_login_customer_id: bool = True,
) -> GoogleAdsClient:
    """Construct an official Google Ads API client from settings."""
    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError as exc:  # pragma: no cover - install issue
        raise CredentialRequiredError(
            "google-ads package is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    try:
        config = settings.to_client_dict(
            include_login_customer_id=include_login_customer_id
        )
        # Use the client library default API version unless overridden by the package.
        return GoogleAdsClient.load_from_dict(config)
    except CredentialRequiredError:
        raise
    except Exception as exc:  # noqa: BLE001 — surface as clear access error
        raise ApiAccessError(f"Failed to build Google Ads client: {exc}") from exc


def run_gaql(
    client: GoogleAdsClient,
    customer_id: str,
    query: str,
) -> Iterator[Any]:
    """Execute a GAQL query and yield row objects."""
    try:
        from google.ads.googleads.errors import GoogleAdsException
    except ImportError:  # pragma: no cover
        GoogleAdsException = Exception  # type: ignore[misc, assignment]

    ga_service = client.get_service("GoogleAdsService")
    try:
        stream = ga_service.search_stream(customer_id=customer_id, query=query)
        for batch in stream:
            yield from batch.results
    except GoogleAdsException as exc:
        messages = []
        for error in getattr(exc, "failure", None).errors if getattr(exc, "failure", None) else []:
            messages.append(error.message)
        detail = "; ".join(messages) if messages else str(exc)
        raise ApiAccessError(
            f"Google Ads API error for customer {customer_id}: {detail}"
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise ApiAccessError(
            f"Google Ads request failed for customer {customer_id}: {exc}"
        ) from exc


def enum_name(client: GoogleAdsClient, enum_type: str, value: int | Any) -> str:
    """Resolve a proto enum integer/value to a readable name when possible."""
    try:
        enum = getattr(client.enums, enum_type)
        # Proto-plus enums often expose .name on the value wrapper.
        if hasattr(value, "name"):
            return str(value.name)
        for member in enum:
            if int(member.value) == int(value):
                return str(member.name)
    except Exception:  # noqa: BLE001
        pass
    return str(value)


def micros_to_currency(micros: int | None) -> float | None:
    if micros is None:
        return None
    return round(int(micros) / 1_000_000, 2)
