"""Read-only ad and network inventory."""

from __future__ import annotations

from typing import Any

from ela_google_ads.client import build_client, enum_name, run_gaql
from ela_google_ads.config import GoogleAdsSettings
from ela_google_ads.logging_config import get_logger

logger = get_logger(__name__)

NETWORK_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.network_settings.target_google_search,
      campaign.network_settings.target_search_network,
      campaign.network_settings.target_content_network
    FROM campaign
    WHERE campaign.status != 'REMOVED'
"""

RSA_QUERY = """
    SELECT
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      ad_group_ad.ad.id,
      ad_group_ad.status,
      ad_group_ad.ad.final_urls,
      ad_group_ad.ad.responsive_search_ad.headlines,
      ad_group_ad.ad.responsive_search_ad.descriptions,
      ad_group_ad.ad.responsive_search_ad.path1,
      ad_group_ad.ad.responsive_search_ad.path2
    FROM ad_group_ad
    WHERE ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
      AND campaign.status != 'REMOVED'
      AND ad_group.status != 'REMOVED'
"""


def list_campaign_network_settings(settings: GoogleAdsSettings) -> list[dict[str, Any]]:
    client = build_client(settings)
    rows: list[dict[str, Any]] = []
    for row in run_gaql(client, settings.customer_id, NETWORK_QUERY):
        network = row.campaign.network_settings
        rows.append(
            {
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name,
                "status": enum_name(client, "CampaignStatusEnum", row.campaign.status),
                "target_google_search": bool(network.target_google_search),
                "target_search_network": bool(network.target_search_network),
                "target_content_network": bool(network.target_content_network),
            }
        )
    return rows


def list_responsive_search_ads(settings: GoogleAdsSettings) -> list[dict[str, Any]]:
    client = build_client(settings)
    rows: list[dict[str, Any]] = []
    for row in run_gaql(client, settings.customer_id, RSA_QUERY):
        ad = row.ad_group_ad.ad
        rsa = ad.responsive_search_ad
        headlines = [item.text for item in rsa.headlines]
        descriptions = [item.text for item in rsa.descriptions]
        rows.append(
            {
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name,
                "ad_group_id": str(row.ad_group.id),
                "ad_group_name": row.ad_group.name,
                "ad_id": str(ad.id),
                "status": enum_name(client, "AdGroupAdStatusEnum", row.ad_group_ad.status),
                "final_urls": list(ad.final_urls),
                "headlines": headlines,
                "descriptions": descriptions,
                "path1": rsa.path1 or "",
                "path2": rsa.path2 or "",
            }
        )
    logger.info("Exported %s responsive search ads", len(rows))
    return rows
