"""Campaign preview builder (no live mutation in preview)."""

from __future__ import annotations

from typing import Any

from ela_google_ads.builders.tracking import preview_tracking
from ela_google_ads.models.spec import CampaignSpec
from ela_google_ads.validators.spec_validators import (
    find_positive_negative_conflicts,
    validate_campaign_spec,
)


def build_campaign_preview(spec: CampaignSpec) -> dict[str, Any]:
    """Produce a dry-run preview of a campaign create payload."""
    issues = validate_campaign_spec(spec)
    conflicts = find_positive_negative_conflicts(spec)
    return {
        "mode": "dry_run_preview",
        "will_mutate": False,
        "requires_execute": True,
        "requires_apply": True,  # back-compat alias
        "default_status": "PAUSED",
        "campaign": {
            "name": spec.name,
            "status": spec.status,
            "channel": spec.channel,
            "daily_budget": spec.daily_budget,
            "bidding_strategy": spec.bidding_strategy,
            "network": {
                "target_google_search": spec.network.target_google_search,
                "target_search_network": spec.network.target_search_network,
                "target_content_network": spec.network.target_content_network,
            },
            "geo_target_ids": spec.geo_target_ids,
            "geo_target_names": spec.geo_target_names,
            "location_presence_only": spec.location_presence_only,
            "language_ids": spec.language_ids,
            "final_url": spec.final_url,
            "brand": {
                "brand_lane_owner": spec.brand.brand_lane_owner,
                "internal_campaign_type": spec.brand.internal_campaign_type,
                "shared_brand_negative_list": spec.brand.shared_brand_negative_list,
            },
            "shared_negative_lists": spec.shared_negative_lists,
            "ad_group_count": len(spec.ad_groups),
            "ad_groups": [
                {
                    "name": ag.name,
                    "keyword_count": len(ag.keywords),
                    "match_types": sorted({k.match_type for k in ag.keywords}),
                    "headline_count": len(ag.rsa.headlines) if ag.rsa else 0,
                    "description_count": len(ag.rsa.descriptions) if ag.rsa else 0,
                    "final_url": ag.final_url or spec.final_url,
                }
                for ag in spec.ad_groups
            ],
        },
        "tracking_preview": preview_tracking(spec),
        "validation_issues": issues,
        "keyword_conflicts": conflicts,
        "notes": [
            "No live Google Ads resources will be created from preview.",
            "Creation: campaigns create SPEC  (dry-run validate_only)",
            "Live create: campaigns create SPEC --execute --confirm-customer-id 6769947952",
            "New campaigns always default to PAUSED; ENABLED is refused.",
            "Existing campaigns are never modified by name match alone.",
            "Bakersfield campaigns stay under activation hold for future enable.",
        ],
    }


def refuse_create_without_apply(*, apply: bool) -> dict[str, Any]:
    """Deprecated helper retained for older tests; prefer create_campaign_from_spec."""
    if apply:
        return {
            "status": "use_execute",
            "message": (
                "Live creation is available via campaigns create --execute "
                "--confirm-customer-id 6769947952 (validate_only runs first)."
            ),
            "mutated": False,
        }
    return {
        "status": "dry_run",
        "message": "Dry-run only. Pass --execute to mutate after validate_only.",
        "mutated": False,
    }
