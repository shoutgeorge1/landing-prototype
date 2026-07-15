"""Asset inventory including call assets (read-only)."""

from __future__ import annotations

from typing import Any

from ela_google_ads.client import build_client, enum_name, run_gaql
from ela_google_ads.config import GoogleAdsSettings
from ela_google_ads.logging_config import get_logger

logger = get_logger(__name__)

ASSET_QUERY = """
    SELECT
      asset.id,
      asset.name,
      asset.type,
      asset.resource_name,
      asset.call_asset.country_code,
      asset.call_asset.phone_number,
      asset.call_asset.call_conversion_reporting_state,
      asset.sitelink_asset.link_text,
      asset.sitelink_asset.description1,
      asset.sitelink_asset.description2,
      asset.callout_asset.callout_text,
      asset.structured_snippet_asset.header,
      asset.structured_snippet_asset.values
    FROM asset
    ORDER BY asset.type, asset.id
"""


def list_assets(settings: GoogleAdsSettings) -> list[dict[str, Any]]:
    client = build_client(settings)
    rows: list[dict[str, Any]] = []
    for row in run_gaql(client, settings.customer_id, ASSET_QUERY):
        asset = row.asset
        asset_type = enum_name(client, "AssetTypeEnum", asset.type)
        item: dict[str, Any] = {
            "asset_id": str(asset.id),
            "name": asset.name or None,
            "type": asset_type,
            "resource_name": asset.resource_name,
        }
        if asset_type == "CALL" or str(asset_type).endswith("CALL"):
            call = asset.call_asset
            item.update(
                {
                    "phone_number": call.phone_number,
                    "country_code": call.country_code,
                    "call_conversion_reporting_state": enum_name(
                        client,
                        "CallConversionReportingStateEnum",
                        call.call_conversion_reporting_state,
                    ),
                }
            )
        if "SITELINK" in str(asset_type):
            sitelink = asset.sitelink_asset
            item.update(
                {
                    "link_text": sitelink.link_text,
                    "description1": sitelink.description1,
                    "description2": sitelink.description2,
                }
            )
        if "CALLOUT" in str(asset_type):
            item["callout_text"] = asset.callout_asset.callout_text
        if "STRUCTURED_SNIPPET" in str(asset_type):
            snippet = asset.structured_snippet_asset
            item.update(
                {
                    "snippet_header": snippet.header,
                    "snippet_values": list(snippet.values),
                }
            )
        rows.append(item)
    logger.info("Exported %s assets", len(rows))
    return rows


def list_call_assets(settings: GoogleAdsSettings) -> list[dict[str, Any]]:
    return [row for row in list_assets(settings) if "CALL" in str(row.get("type", ""))]


def phone_tracking_warnings(
    settings: GoogleAdsSettings,
    *,
    call_assets: list[dict[str, Any]] | None = None,
    conversion_actions: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Non-blocking warnings for call-tracking readiness."""
    warnings: list[str] = []
    if not settings.call_tracking_phone:
        warnings.append("No phone number configured (ELA_CALL_TRACKING_PHONE).")
    assets = call_assets if call_assets is not None else []
    if not assets:
        warnings.append("No call assets found in the account.")
    if conversion_actions is not None:
        call_conversions = [
            c
            for c in conversion_actions
            if "CALL" in str(c.get("type", "")).upper()
            or "call" in str(c.get("name", "")).lower()
            or "PHONE" in str(c.get("category", "")).upper()
        ]
        if not call_conversions:
            warnings.append("No call-related conversion action detected.")
    warnings.append(
        "Do not create or activate a call asset until routing and intake coverage are confirmed."
    )
    warnings.append(
        "Phone under evaluation (424-678-1416) is not assumed production-ready."
    )
    return warnings
