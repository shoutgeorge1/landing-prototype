"""Read-only keyword and negative-keyword inventory."""

from __future__ import annotations

from typing import Any

from ela_google_ads.client import build_client, enum_name, micros_to_currency, run_gaql
from ela_google_ads.config import GoogleAdsSettings
from ela_google_ads.logging_config import get_logger

logger = get_logger(__name__)

POSITIVE_KEYWORD_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      ad_group.id,
      ad_group.name,
      ad_group_criterion.criterion_id,
      ad_group_criterion.keyword.text,
      ad_group_criterion.keyword.match_type,
      ad_group_criterion.status,
      ad_group_criterion.cpc_bid_micros,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros
    FROM keyword_view
    WHERE segments.date DURING LAST_30_DAYS
      AND campaign.status != 'REMOVED'
      AND ad_group.status != 'REMOVED'
      AND ad_group_criterion.status != 'REMOVED'
    ORDER BY metrics.impressions DESC
"""

CAMPAIGN_NEGATIVE_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign_criterion.criterion_id,
      campaign_criterion.keyword.text,
      campaign_criterion.keyword.match_type,
      campaign_criterion.negative
    FROM campaign_criterion
    WHERE campaign_criterion.type = 'KEYWORD'
      AND campaign_criterion.negative = TRUE
      AND campaign.status != 'REMOVED'
"""

AD_GROUP_NEGATIVE_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      ad_group_criterion.criterion_id,
      ad_group_criterion.keyword.text,
      ad_group_criterion.keyword.match_type,
      ad_group_criterion.negative
    FROM ad_group_criterion
    WHERE ad_group_criterion.type = 'KEYWORD'
      AND ad_group_criterion.negative = TRUE
      AND campaign.status != 'REMOVED'
      AND ad_group.status != 'REMOVED'
"""


def list_positive_keywords(settings: GoogleAdsSettings) -> list[dict[str, Any]]:
    client = build_client(settings)
    rows: list[dict[str, Any]] = []
    for row in run_gaql(client, settings.customer_id, POSITIVE_KEYWORD_QUERY):
        criterion = row.ad_group_criterion
        keyword = criterion.keyword
        rows.append(
            {
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name,
                "campaign_status": enum_name(client, "CampaignStatusEnum", row.campaign.status),
                "ad_group_id": str(row.ad_group.id),
                "ad_group_name": row.ad_group.name,
                "criterion_id": str(criterion.criterion_id),
                "keyword": keyword.text,
                "match_type": enum_name(
                    client, "KeywordMatchTypeEnum", keyword.match_type
                ),
                "status": enum_name(client, "AdGroupCriterionStatusEnum", criterion.status),
                "cpc_bid": micros_to_currency(criterion.cpc_bid_micros),
                "impressions": int(row.metrics.impressions),
                "clicks": int(row.metrics.clicks),
                "cost": micros_to_currency(row.metrics.cost_micros),
            }
        )
    logger.info("Exported %s positive keywords (30d)", len(rows))
    return rows


def list_negative_keywords(settings: GoogleAdsSettings) -> list[dict[str, Any]]:
    client = build_client(settings)
    rows: list[dict[str, Any]] = []
    for row in run_gaql(client, settings.customer_id, CAMPAIGN_NEGATIVE_QUERY):
        keyword = row.campaign_criterion.keyword
        rows.append(
            {
                "level": "campaign",
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name,
                "ad_group_id": "",
                "ad_group_name": "",
                "criterion_id": str(row.campaign_criterion.criterion_id),
                "keyword": keyword.text,
                "match_type": enum_name(
                    client, "KeywordMatchTypeEnum", keyword.match_type
                ),
            }
        )
    for row in run_gaql(client, settings.customer_id, AD_GROUP_NEGATIVE_QUERY):
        keyword = row.ad_group_criterion.keyword
        rows.append(
            {
                "level": "ad_group",
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name,
                "ad_group_id": str(row.ad_group.id),
                "ad_group_name": row.ad_group.name,
                "criterion_id": str(row.ad_group_criterion.criterion_id),
                "keyword": keyword.text,
                "match_type": enum_name(
                    client, "KeywordMatchTypeEnum", keyword.match_type
                ),
            }
        )
    logger.info("Exported %s negative keywords", len(rows))
    return rows
