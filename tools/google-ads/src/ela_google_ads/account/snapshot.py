"""Account configuration snapshot (read-only)."""

from __future__ import annotations

from typing import Any

from ela_google_ads.account.access import get_account_access_summary
from ela_google_ads.assets.inventory import list_assets, list_call_assets
from ela_google_ads.campaigns.inventory import (
    list_campaign_budgets,
    list_campaigns,
    list_language_targets,
    list_location_targets,
)
from ela_google_ads.config import GoogleAdsSettings
from ela_google_ads.conversions.inventory import list_conversion_actions
from ela_google_ads.logging_config import get_logger

logger = get_logger(__name__)


def build_account_snapshot(settings: GoogleAdsSettings) -> dict[str, Any]:
    """Assemble a read-only inventory snapshot of the target account."""
    logger.info("Building account snapshot for customer %s", settings.customer_id)
    account = get_account_access_summary(settings)
    campaigns = list_campaigns(settings, include_metrics=True)
    budgets = list_campaign_budgets(settings)
    conversions = list_conversion_actions(settings)
    locations = list_location_targets(settings)
    languages = list_language_targets(settings)
    assets = list_assets(settings)
    call_assets = list_call_assets(settings)

    warnings: list[str] = []
    if not account.get("auto_tagging_enabled"):
        warnings.append(
            "Auto-tagging is disabled. GCLID capture for HubSpot attribution may be impaired."
        )
    if not call_assets:
        warnings.append("No call assets found. Phone tracking may not be configured yet.")
    if not conversions:
        warnings.append("No conversion actions found.")
    if settings.call_tracking_phone is None:
        warnings.append(
            "ELA_CALL_TRACKING_PHONE is unset. "
            "Do not activate call assets until routing is confirmed."
        )

    return {
        "account": account,
        "counts": {
            "campaigns": len(campaigns),
            "budgets": len(budgets),
            "conversion_actions": len(conversions),
            "location_targets": len(locations),
            "language_targets": len(languages),
            "assets": len(assets),
            "call_assets": len(call_assets),
        },
        "campaigns": campaigns,
        "budgets": budgets,
        "conversion_actions": conversions,
        "location_targets": locations,
        "language_targets": languages,
        "assets": assets,
        "call_assets": call_assets,
        "warnings": warnings,
    }
