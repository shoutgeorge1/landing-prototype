"""Search-term reporting (read-only)."""

from __future__ import annotations

from typing import Any

from ela_google_ads.client import build_client, enum_name, micros_to_currency, run_gaql
from ela_google_ads.config import GoogleAdsSettings
from ela_google_ads.logging_config import get_logger

logger = get_logger(__name__)


def search_terms_query(days: int = 30) -> str:
    period = f"LAST_{days}_DAYS" if days in {7, 14, 30, 90} else "LAST_30_DAYS"
    return f"""
    SELECT
      search_term_view.search_term,
      search_term_view.status,
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions,
      metrics.conversions_value
    FROM search_term_view
    WHERE segments.date DURING {period}
    ORDER BY metrics.impressions DESC
    """


def list_search_terms(settings: GoogleAdsSettings, *, days: int = 30) -> list[dict[str, Any]]:
    if days not in {7, 14, 30, 90}:
        days = 30
    client = build_client(settings)
    rows: list[dict[str, Any]] = []
    try:
        stream = run_gaql(client, settings.customer_id, search_terms_query(days))
        for row in stream:
            st = row.search_term_view
            rows.append(
                {
                    "search_term": st.search_term,
                    "status": enum_name(client, "SearchTermTargetingStatusEnum", st.status),
                    "campaign_id": str(row.campaign.id),
                    "campaign_name": row.campaign.name,
                    "ad_group_id": str(row.ad_group.id),
                    "ad_group_name": row.ad_group.name,
                    "impressions": int(row.metrics.impressions),
                    "clicks": int(row.metrics.clicks),
                    "cost": micros_to_currency(row.metrics.cost_micros),
                    "conversions": float(row.metrics.conversions),
                    "conversion_value": float(row.metrics.conversions_value),
                }
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Search-term reporting unavailable or empty for last %s days: %s",
            days,
            exc,
        )
        return []
    logger.info("Exported %s search terms (last %s days)", len(rows), days)
    return rows
