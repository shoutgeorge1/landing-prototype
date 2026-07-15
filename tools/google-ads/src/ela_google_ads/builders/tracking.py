"""Tracking URL preview helpers."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from ela_google_ads.models.spec import CampaignSpec

# Align with landing-page HubSpot hidden fields (src/lib/googleAdsParams.ts).
DEFAULT_FINAL_URL_SUFFIX_TEMPLATE = (
    "utm_source=google"
    "&utm_medium=cpc"
    "&utm_campaign={campaignid}"
    "&utm_term={keyword}"
    "&utm_content={creative}"
    "&google_campaign={_campaign_name}"
    "&google_ad_group={_ad_group_name}"
    "&google_keyword={keyword}"
    "&matchtype={matchtype}"
    "&device={device}"
    "&network={network}"
)


def build_final_url_suffix(
    *,
    campaign_name: str,
    ad_group_name: str,
    custom_suffix: str | None = None,
) -> str:
    raw = custom_suffix or DEFAULT_FINAL_URL_SUFFIX_TEMPLATE
    return (
        raw.replace("{_campaign_name}", _slug(campaign_name))
        .replace("{_ad_group_name}", _slug(ad_group_name))
    )


def _slug(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("|", " ")
        .replace("/", " ")
        .replace("  ", " ")
        .replace(" ", "_")
    )


def preview_tracking(spec: CampaignSpec) -> list[dict[str, str]]:
    """Export a tracking preview for campaign / ad groups / ads."""
    rows: list[dict[str, str]] = []
    base = spec.final_url or ""
    for ag in spec.ad_groups:
        final_url = ag.final_url or base
        suffix = build_final_url_suffix(
            campaign_name=spec.name,
            ad_group_name=ag.name,
            custom_suffix=spec.tracking.final_url_suffix,
        )
        preview_url = append_suffix(final_url, suffix)
        rows.append(
            {
                "level": "ad_group",
                "campaign": spec.name,
                "ad_group": ag.name,
                "final_url": final_url,
                "final_url_suffix": suffix,
                "preview_url": preview_url,
                "tracking_template": spec.tracking.tracking_template or "",
            }
        )
    if not rows:
        suffix = build_final_url_suffix(
            campaign_name=spec.name,
            ad_group_name="",
            custom_suffix=spec.tracking.final_url_suffix,
        )
        rows.append(
            {
                "level": "campaign",
                "campaign": spec.name,
                "ad_group": "",
                "final_url": base,
                "final_url_suffix": suffix,
                "preview_url": append_suffix(base, suffix),
                "tracking_template": spec.tracking.tracking_template or "",
            }
        )
    return rows


def append_suffix(url: str, suffix: str) -> str:
    if not url:
        return suffix
    parsed = urlparse(url)
    existing = dict(parse_qsl(parsed.query, keep_blank_values=True))
    extra = dict(parse_qsl(suffix, keep_blank_values=True))
    # Do not overwrite params already present on the landing URL.
    for key, value in extra.items():
        if key not in existing:
            existing[key] = value
    return urlunparse(parsed._replace(query=urlencode(existing)))
