"""Account access and accessible-customer listing."""

from __future__ import annotations

from typing import Any

from ela_google_ads.client import build_client, enum_name, run_gaql
from ela_google_ads.config import GoogleAdsSettings
from ela_google_ads.exceptions import ApiAccessError
from ela_google_ads.logging_config import get_logger

logger = get_logger(__name__)

CUSTOMER_QUERY = """
    SELECT
      customer.id,
      customer.descriptive_name,
      customer.status,
      customer.currency_code,
      customer.time_zone,
      customer.auto_tagging_enabled,
      customer.test_account,
      customer.manager,
      customer.tracking_url_template,
      customer.final_url_suffix
    FROM customer
    LIMIT 1
"""


def list_accessible_customers(settings: GoogleAdsSettings) -> list[str]:
    """Return customer resource names the OAuth user can access."""
    # list_accessible_customers should be called without login_customer_id.
    client = build_client(settings, include_login_customer_id=False)
    customer_service = client.get_service("CustomerService")
    try:
        response = customer_service.list_accessible_customers()
    except Exception as exc:  # noqa: BLE001
        raise ApiAccessError(f"list_accessible_customers failed: {exc}") from exc

    resource_names = list(response.resource_names)
    logger.info("Found %s accessible customer resource(s)", len(resource_names))
    return resource_names


def get_account_access_summary(settings: GoogleAdsSettings) -> dict[str, Any]:
    """Query account metadata for the configured target customer."""
    client = build_client(settings)
    customer_id = settings.customer_id
    rows = list(run_gaql(client, customer_id, CUSTOMER_QUERY))
    if not rows:
        raise ApiAccessError(
            f"No customer row returned for {customer_id}. "
            "Check GOOGLE_ADS_CUSTOMER_ID and MCC login customer ID."
        )
    row = rows[0]
    customer = row.customer
    status = enum_name(client, "CustomerStatusEnum", customer.status)
    summary = {
        "customer_id": str(customer.id),
        "account_name": customer.descriptive_name,
        "account_status": status,
        "currency_code": customer.currency_code,
        "time_zone": customer.time_zone,
        "auto_tagging_enabled": bool(customer.auto_tagging_enabled),
        "test_account": bool(customer.test_account),
        "is_manager": bool(customer.manager),
        "tracking_url_template": customer.tracking_url_template or None,
        "final_url_suffix": customer.final_url_suffix or None,
        "login_customer_id": settings.login_customer_id,
    }
    logger.info(
        "Account access OK: %s (%s) status=%s auto_tagging=%s",
        summary["customer_id"],
        summary["account_name"],
        summary["account_status"],
        summary["auto_tagging_enabled"],
    )
    return summary
