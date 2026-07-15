"""Campaign, budget, geo, and language inventory (read-only)."""

from __future__ import annotations

from typing import Any

from ela_google_ads.client import build_client, enum_name, micros_to_currency, run_gaql
from ela_google_ads.config import GoogleAdsSettings
from ela_google_ads.logging_config import get_logger

logger = get_logger(__name__)

CAMPAIGN_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.advertising_channel_type,
      campaign.bidding_strategy_type,
      campaign.start_date_time,
      campaign.end_date_time,
      campaign_budget.amount_micros,
      campaign_budget.period,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions,
      metrics.conversions_value,
      metrics.search_impression_share
    FROM campaign
    WHERE campaign.status != 'REMOVED'
    ORDER BY campaign.name
"""

BUDGET_QUERY = """
    SELECT
      campaign_budget.id,
      campaign_budget.name,
      campaign_budget.status,
      campaign_budget.amount_micros,
      campaign_budget.delivery_method,
      campaign_budget.explicitly_shared,
      campaign_budget.period
    FROM campaign_budget
    ORDER BY campaign_budget.name
"""

LOCATION_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign_criterion.criterion_id,
      campaign_criterion.location.geo_target_constant,
      campaign_criterion.negative,
      campaign_criterion.type
    FROM campaign_criterion
    WHERE campaign_criterion.type = 'LOCATION'
      AND campaign.status != 'REMOVED'
"""

LANGUAGE_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign_criterion.criterion_id,
      campaign_criterion.language.language_constant,
      campaign_criterion.negative,
      campaign_criterion.type
    FROM campaign_criterion
    WHERE campaign_criterion.type = 'LANGUAGE'
      AND campaign.status != 'REMOVED'
"""


def list_location_targets(settings: GoogleAdsSettings) -> list[dict[str, Any]]:
    client = build_client(settings)
    rows: list[dict[str, Any]] = []
    for row in run_gaql(client, settings.customer_id, LOCATION_QUERY):
        rows.append(
            {
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name,
                "criterion_id": str(row.campaign_criterion.criterion_id),
                "geo_target_constant": row.campaign_criterion.location.geo_target_constant,
                "negative": bool(row.campaign_criterion.negative),
            }
        )
    return rows


def list_language_targets(settings: GoogleAdsSettings) -> list[dict[str, Any]]:
    client = build_client(settings)
    rows: list[dict[str, Any]] = []
    for row in run_gaql(client, settings.customer_id, LANGUAGE_QUERY):
        rows.append(
            {
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name,
                "criterion_id": str(row.campaign_criterion.criterion_id),
                "language_constant": row.campaign_criterion.language.language_constant,
                "negative": bool(row.campaign_criterion.negative),
            }
        )
    return rows


def list_campaign_budgets(settings: GoogleAdsSettings) -> list[dict[str, Any]]:
    client = build_client(settings)
    rows: list[dict[str, Any]] = []
    for row in run_gaql(client, settings.customer_id, BUDGET_QUERY):
        budget = row.campaign_budget
        rows.append(
            {
                "budget_id": str(budget.id),
                "budget_name": budget.name,
                "status": enum_name(client, "BudgetStatusEnum", budget.status),
                "amount": micros_to_currency(budget.amount_micros),
                "delivery_method": enum_name(
                    client, "BudgetDeliveryMethodEnum", budget.delivery_method
                ),
                "explicitly_shared": bool(budget.explicitly_shared),
                "period": enum_name(client, "BudgetPeriodEnum", budget.period),
            }
        )
    return rows


def list_campaigns(
    settings: GoogleAdsSettings,
    *,
    include_metrics: bool = True,
    enrich_targeting: bool = True,
) -> list[dict[str, Any]]:
    client = build_client(settings)
    customer_id = settings.customer_id

    location_map: dict[str, list[dict[str, Any]]] = {}
    language_map: dict[str, list[dict[str, Any]]] = {}
    if enrich_targeting:
        location_map = _group_by_campaign(list_location_targets(settings))
        language_map = _group_by_campaign(list_language_targets(settings))

    rows: list[dict[str, Any]] = []
    for row in run_gaql(client, customer_id, CAMPAIGN_QUERY):
        campaign = row.campaign
        budget = row.campaign_budget
        cid = str(campaign.id)
        item: dict[str, Any] = {
            "campaign_id": cid,
            "campaign_name": campaign.name,
            "status": enum_name(client, "CampaignStatusEnum", campaign.status),
            "advertising_channel": enum_name(
                client, "AdvertisingChannelTypeEnum", campaign.advertising_channel_type
            ),
            "bidding_strategy": enum_name(
                client, "BiddingStrategyTypeEnum", campaign.bidding_strategy_type
            ),
            "daily_budget": micros_to_currency(budget.amount_micros),
            "budget_period": enum_name(client, "BudgetPeriodEnum", budget.period)
            if budget.period
            else None,
            "start_date": campaign.start_date_time or None,
            "end_date": campaign.end_date_time or None,
            "location_targeting": location_map.get(cid, []),
            "language_targeting": language_map.get(cid, []),
        }
        if include_metrics:
            metrics = row.metrics
            item.update(
                {
                    "impressions": int(metrics.impressions),
                    "clicks": int(metrics.clicks),
                    "cost": micros_to_currency(metrics.cost_micros),
                    "conversions": float(metrics.conversions),
                    "conversion_value": float(metrics.conversions_value),
                    "search_impression_share": (
                        float(metrics.search_impression_share)
                        if metrics.search_impression_share
                        else None
                    ),
                }
            )
        rows.append(item)
    logger.info("Exported %s campaigns", len(rows))
    return rows


def _group_by_campaign(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["campaign_id"]), []).append(row)
    return grouped
