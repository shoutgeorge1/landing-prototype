"""Campaign specification models (YAML/JSON-backed)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ALLOWED_MATCH_TYPES = frozenset({"EXACT", "PHRASE"})
ALLOWED_CHANNELS = frozenset({"SEARCH"})
ALLOWED_LANGUAGES = frozenset({"en", "es", "EN", "ES", "english", "spanish"})


@dataclass
class KeywordSpec:
    text: str
    match_type: str = "PHRASE"


@dataclass
class RsaSpec:
    headlines: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    path1: str | None = None
    path2: str | None = None
    pinned_headlines: dict[str, int] = field(default_factory=dict)


@dataclass
class AdGroupSpec:
    name: str
    final_url: str | None = None
    keywords: list[KeywordSpec] = field(default_factory=list)
    negative_keywords: list[KeywordSpec] = field(default_factory=list)
    rsa: RsaSpec | None = None


@dataclass
class NetworkSettings:
    target_google_search: bool = True
    target_search_network: bool = False  # Search Partners off by default
    target_content_network: bool = False  # Display off


@dataclass
class BrandHandling:
    brand_lane_owner: str = "hawksem"
    internal_campaign_type: str = "nonbrand"
    shared_brand_negative_list: str | None = "shared/brand-negatives.yaml"


@dataclass
class TrackingSpec:
    tracking_template: str | None = None
    final_url_suffix: str | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class CampaignSpec:
    name: str
    status: str = "PAUSED"
    language: str = "en"
    city: str = "bakersfield"
    daily_budget: float = 0.0
    bidding_strategy: str = "MAXIMIZE_CLICKS"
    network: NetworkSettings = field(default_factory=NetworkSettings)
    start_date: str | None = None
    geo_target_ids: list[int] = field(default_factory=list)
    geo_target_names: list[str] = field(default_factory=list)
    location_presence_only: bool = True
    language_ids: list[int] = field(default_factory=list)
    final_url: str | None = None
    tracking: TrackingSpec = field(default_factory=TrackingSpec)
    ad_schedule: list[dict[str, Any]] = field(default_factory=list)
    call_asset_schedule: list[dict[str, Any]] = field(default_factory=list)
    campaign_negative_keywords: list[KeywordSpec] = field(default_factory=list)
    shared_negative_lists: list[str] = field(default_factory=list)
    ad_groups: list[AdGroupSpec] = field(default_factory=list)
    sitelinks: list[dict[str, Any]] = field(default_factory=list)
    callouts: list[str] = field(default_factory=list)
    structured_snippets: list[dict[str, Any]] = field(default_factory=list)
    conversion_goals: list[str] = field(default_factory=list)
    brand: BrandHandling = field(default_factory=BrandHandling)
    channel: str = "SEARCH"
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


def _keyword_from_obj(obj: Any) -> KeywordSpec:
    if isinstance(obj, str):
        return KeywordSpec(text=obj, match_type="PHRASE")
    return KeywordSpec(
        text=str(obj.get("text", "")).strip(),
        match_type=str(obj.get("match_type", "PHRASE")).upper(),
    )


def campaign_spec_from_dict(data: dict[str, Any]) -> CampaignSpec:
    network_raw = data.get("network") or {}
    brand_raw = data.get("brand") or {}
    tracking_raw = data.get("tracking") or {}

    ad_groups: list[AdGroupSpec] = []
    for ag in data.get("ad_groups") or []:
        rsa_raw = ag.get("rsa") or {}
        rsa = None
        if rsa_raw:
            rsa = RsaSpec(
                headlines=list(rsa_raw.get("headlines") or []),
                descriptions=list(rsa_raw.get("descriptions") or []),
                path1=rsa_raw.get("path1"),
                path2=rsa_raw.get("path2"),
                pinned_headlines=dict(rsa_raw.get("pinned_headlines") or {}),
            )
        ad_groups.append(
            AdGroupSpec(
                name=str(ag.get("name", "")).strip(),
                final_url=ag.get("final_url") or data.get("final_url"),
                keywords=[_keyword_from_obj(k) for k in ag.get("keywords") or []],
                negative_keywords=[
                    _keyword_from_obj(k) for k in ag.get("negative_keywords") or []
                ],
                rsa=rsa,
            )
        )

    return CampaignSpec(
        name=str(data.get("name", "")).strip(),
        status=str(data.get("status", "PAUSED")).upper(),
        language=str(data.get("language", "en")),
        city=str(data.get("city", "bakersfield")),
        daily_budget=float(data.get("daily_budget") or 0),
        bidding_strategy=str(data.get("bidding_strategy", "MAXIMIZE_CLICKS")),
        network=NetworkSettings(
            target_google_search=bool(network_raw.get("target_google_search", True)),
            target_search_network=bool(network_raw.get("target_search_network", False)),
            target_content_network=bool(network_raw.get("target_content_network", False)),
        ),
        start_date=data.get("start_date"),
        geo_target_ids=[int(x) for x in data.get("geo_target_ids") or []],
        geo_target_names=list(data.get("geo_target_names") or []),
        location_presence_only=bool(data.get("location_presence_only", True)),
        language_ids=[int(x) for x in data.get("language_ids") or []],
        final_url=data.get("final_url"),
        tracking=TrackingSpec(
            tracking_template=tracking_raw.get("tracking_template"),
            final_url_suffix=tracking_raw.get("final_url_suffix"),
            notes=list(tracking_raw.get("notes") or []),
        ),
        ad_schedule=list(data.get("ad_schedule") or []),
        call_asset_schedule=list(data.get("call_asset_schedule") or []),
        campaign_negative_keywords=[
            _keyword_from_obj(k) for k in data.get("campaign_negative_keywords") or []
        ],
        shared_negative_lists=list(data.get("shared_negative_lists") or []),
        ad_groups=ad_groups,
        sitelinks=list(data.get("sitelinks") or []),
        callouts=list(data.get("callouts") or []),
        structured_snippets=list(data.get("structured_snippets") or []),
        conversion_goals=list(data.get("conversion_goals") or []),
        brand=BrandHandling(
            brand_lane_owner=str(brand_raw.get("brand_lane_owner", "hawksem")),
            internal_campaign_type=str(
                brand_raw.get("internal_campaign_type", "nonbrand")
            ),
            shared_brand_negative_list=brand_raw.get(
                "shared_brand_negative_list", "shared/brand-negatives.yaml"
            ),
        ),
        channel=str(data.get("channel", "SEARCH")).upper(),
        raw=data,
    )
