"""Geo-target constant lookup (read-only API utility)."""

from __future__ import annotations

from typing import Any

from ela_google_ads.client import build_client, run_gaql
from ela_google_ads.config import GoogleAdsSettings
from ela_google_ads.logging_config import get_logger

logger = get_logger(__name__)

# Common reference constants (not a substitute for live lookup).
KNOWN_GEO_HINTS = {
    "bakersfield": 1013517,  # Bakersfield, CA — verify via geo search before apply
    "california": 21137,
    "united states": 2840,
}

KNOWN_LANGUAGE_IDS = {
    "en": 1000,
    "english": 1000,
    "es": 1003,
    "spanish": 1003,
}


def search_geo_targets(
    settings: GoogleAdsSettings,
    query_text: str,
    *,
    country_code: str = "US",
    locale: str = "en",
) -> list[dict[str, Any]]:
    """Search Google Ads geo-target constants instead of guessing IDs."""
    client = build_client(settings)
    # GeoTargetConstantService suggestion is preferred; also support GAQL fallback.
    try:
        service = client.get_service("GeoTargetConstantService")
        request = client.get_type("SuggestGeoTargetConstantsRequest")
        request.locale = locale
        request.country_code = country_code
        request.location_names.names.append(query_text)
        response = service.suggest_geo_target_constants(request=request)
        rows: list[dict[str, Any]] = []
        for suggestion in response.geo_target_constant_suggestions:
            gtc = suggestion.geo_target_constant
            rows.append(
                {
                    "resource_name": gtc.resource_name,
                    "id": str(gtc.id),
                    "name": gtc.name,
                    "canonical_name": gtc.canonical_name,
                    "country_code": gtc.country_code,
                    "target_type": gtc.target_type,
                    "status": str(gtc.status),
                    "search_term": suggestion.search_term,
                    "locale": suggestion.locale,
                    "reach": suggestion.reach,
                }
            )
        logger.info("Geo search for %r returned %s suggestion(s)", query_text, len(rows))
        return rows
    except Exception as exc:  # noqa: BLE001
        logger.warning("GeoTargetConstantService failed (%s); trying GAQL", exc)

    escaped = query_text.replace("'", "\\'")
    gaql = f"""
        SELECT
          geo_target_constant.id,
          geo_target_constant.name,
          geo_target_constant.canonical_name,
          geo_target_constant.country_code,
          geo_target_constant.target_type,
          geo_target_constant.status,
          geo_target_constant.resource_name
        FROM geo_target_constant
        WHERE geo_target_constant.name LIKE '%{escaped}%'
          AND geo_target_constant.country_code = '{country_code}'
        LIMIT 50
    """
    rows = []
    for row in run_gaql(client, settings.customer_id, gaql):
        gtc = row.geo_target_constant
        rows.append(
            {
                "resource_name": gtc.resource_name,
                "id": str(gtc.id),
                "name": gtc.name,
                "canonical_name": gtc.canonical_name,
                "country_code": gtc.country_code,
                "target_type": gtc.target_type,
                "status": str(gtc.status),
            }
        )
    return rows


def hint_geo_id(name: str) -> int | None:
    return KNOWN_GEO_HINTS.get(name.strip().lower())
