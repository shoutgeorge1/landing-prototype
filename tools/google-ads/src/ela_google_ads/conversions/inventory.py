"""Conversion action inventory (read-only)."""

from __future__ import annotations

from typing import Any

from ela_google_ads.client import build_client, enum_name, run_gaql
from ela_google_ads.config import GoogleAdsSettings
from ela_google_ads.logging_config import get_logger

logger = get_logger(__name__)

CONVERSION_QUERY = """
    SELECT
      conversion_action.id,
      conversion_action.name,
      conversion_action.category,
      conversion_action.origin,
      conversion_action.status,
      conversion_action.primary_for_goal,
      conversion_action.counting_type,
      conversion_action.attribution_model_settings.attribution_model,
      conversion_action.click_through_lookback_window_days,
      conversion_action.view_through_lookback_window_days,
      conversion_action.value_settings.default_value,
      conversion_action.value_settings.default_currency_code,
      conversion_action.value_settings.always_use_default_value,
      conversion_action.type,
      conversion_action.include_in_conversions_metric
    FROM conversion_action
    ORDER BY conversion_action.name
"""


def list_conversion_actions(settings: GoogleAdsSettings) -> list[dict[str, Any]]:
    client = build_client(settings)
    rows: list[dict[str, Any]] = []
    for row in run_gaql(client, settings.customer_id, CONVERSION_QUERY):
        action = row.conversion_action
        value_settings = action.value_settings
        attribution = action.attribution_model_settings
        rows.append(
            {
                "conversion_action_id": str(action.id),
                "name": action.name,
                "category": enum_name(
                    client, "ConversionActionCategoryEnum", action.category
                ),
                "origin": enum_name(client, "ConversionOriginEnum", action.origin),
                "status": enum_name(client, "ConversionActionStatusEnum", action.status),
                "type": enum_name(client, "ConversionActionTypeEnum", action.type),
                "primary_for_goal": bool(action.primary_for_goal),
                "include_in_conversions_metric": bool(action.include_in_conversions_metric),
                "counting_method": enum_name(
                    client, "ConversionActionCountingTypeEnum", action.counting_type
                ),
                "attribution_model": enum_name(
                    client,
                    "AttributionModelEnum",
                    attribution.attribution_model,
                )
                if attribution
                else None,
                "click_through_window_days": int(action.click_through_lookback_window_days)
                if action.click_through_lookback_window_days
                else None,
                "view_through_window_days": int(action.view_through_lookback_window_days)
                if action.view_through_lookback_window_days
                else None,
                "default_value": float(value_settings.default_value)
                if value_settings
                else None,
                "default_currency_code": value_settings.default_currency_code
                if value_settings
                else None,
                "always_use_default_value": bool(value_settings.always_use_default_value)
                if value_settings
                else None,
                "optimization_setting": (
                    "PRIMARY" if action.primary_for_goal else "SECONDARY"
                ),
            }
        )
    logger.info("Exported %s conversion actions", len(rows))
    return rows
