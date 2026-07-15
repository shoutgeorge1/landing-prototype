#!/usr/bin/env python3
"""Generate Google Ads Editor fallback files after an API mutation blocker."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from ela_google_ads.builders.tracking import build_final_url_suffix
from ela_google_ads.campaigns.create import attach_locked_campaign_negatives
from ela_google_ads.validators.spec_validators import load_spec_file

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "specs"
OUT = ROOT / "output" / "editor-import"
CALL_PHONE = "+14246781416"
CONVERSION_GOAL = "ELA | Goals | Nonbrand Search"


def _write_csv(name: str, rows: list[dict[str, object]]) -> Path:
    path = OUT / name
    if not rows:
        raise RuntimeError(f"Refusing to write empty Editor file: {name}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    spec_paths = sorted(
        path for path in SPECS.glob("*-*.yaml") if path.name != "markets.yaml"
    )
    specs = [load_spec_file(path) for path in spec_paths]

    campaigns: list[dict[str, object]] = []
    locations: list[dict[str, object]] = []
    ad_groups: list[dict[str, object]] = []
    keywords: list[dict[str, object]] = []
    negatives: list[dict[str, object]] = []
    ads: list[dict[str, object]] = []
    sitelinks: list[dict[str, object]] = []
    callouts: list[dict[str, object]] = []
    snippets: list[dict[str, object]] = []
    calls: list[dict[str, object]] = []
    goals: list[dict[str, object]] = []
    api_status: list[dict[str, object]] = []

    for path, spec in zip(spec_paths, specs, strict=True):
        attach_locked_campaign_negatives(spec, path)
        labels = "ELA;Vendor overlap hold" if spec.city == "bakersfield" else "ELA"
        campaigns.append(
            {
                "Campaign": spec.name,
                "Campaign state": "Paused",
                "Campaign type": "Search",
                "Budget": f"{spec.daily_budget:.2f}",
                "Budget type": "Daily",
                "Bid strategy type": "Maximize clicks",
                "Max CPC bid limit": "25.00",
                "Google Search": "Enabled",
                "Search partners": "Disabled",
                "Display Network": "Disabled",
                "Languages": "English" if spec.language.lower() == "en" else "Spanish",
                "Location targeting method": "People in or regularly in targeted locations",
                # Required by Ads / Editor for new campaigns (not EU political ads).
                "Contains EU political advertising": "No",
                "Final URL suffix": build_final_url_suffix(
                    campaign_name=spec.name,
                    ad_group_name="",
                    custom_suffix=spec.tracking.final_url_suffix,
                ),
                "Labels": labels,
            }
        )
        for geo_id, geo_name in zip(
            spec.geo_target_ids, spec.geo_target_names, strict=True
        ):
            locations.append(
                {
                    "Campaign": spec.name,
                    "Location": geo_name,
                    "Location ID": geo_id,
                    "Bid adjustment": "",
                    "Status": "Enabled",
                }
            )
        for negative in spec.campaign_negative_keywords:
            negatives.append(
                {
                    "Campaign": spec.name,
                    "Keyword": negative.text,
                    "Match type": negative.match_type.title(),
                    "Negative": "Yes",
                }
            )
        for ad_group in spec.ad_groups:
            ad_groups.append(
                {
                    "Campaign": spec.name,
                    "Ad group": ad_group.name,
                    "Ad group state": "Paused",
                    "Ad group type": "Standard",
                }
            )
            for keyword in ad_group.keywords:
                keywords.append(
                    {
                        "Campaign": spec.name,
                        "Ad group": ad_group.name,
                        "Keyword": keyword.text,
                        "Match type": keyword.match_type.title(),
                        "Keyword state": "Paused",
                        "Final URL": ad_group.final_url or spec.final_url or "",
                    }
                )
            if ad_group.rsa is None:
                raise RuntimeError(f"{spec.name}/{ad_group.name} has no RSA")
            row: dict[str, object] = {
                "Campaign": spec.name,
                "Ad group": ad_group.name,
                "Ad type": "Responsive search ad",
                "Ad state": "Paused",
                "Final URL": ad_group.final_url or spec.final_url or "",
                "Final URL suffix": build_final_url_suffix(
                    campaign_name=spec.name,
                    ad_group_name=ad_group.name,
                    custom_suffix=spec.tracking.final_url_suffix,
                ),
                "Path 1": ad_group.rsa.path1 or "",
                "Path 2": ad_group.rsa.path2 or "",
            }
            row.update(
                {
                    f"Headline {index}": headline
                    for index, headline in enumerate(ad_group.rsa.headlines, start=1)
                }
            )
            row.update(
                {
                    f"Description {index}": description
                    for index, description in enumerate(
                        ad_group.rsa.descriptions, start=1
                    )
                }
            )
            ads.append(row)
        for sitelink in spec.sitelinks:
            sitelinks.append(
                {
                    "Campaign": spec.name,
                    "Link text": sitelink["link_text"],
                    "Final URL": sitelink.get("final_url") or spec.final_url or "",
                    "Description line 1": sitelink.get("description1", ""),
                    "Description line 2": sitelink.get("description2", ""),
                    "Asset link state": "Paused",
                }
            )
        for text in spec.callouts:
            callouts.append(
                {
                    "Campaign": spec.name,
                    "Callout text": text,
                    "Asset link state": "Paused",
                }
            )
        for snippet in spec.structured_snippets:
            snippets.append(
                {
                    "Campaign": spec.name,
                    "Header": snippet["header"],
                    "Values": ";".join(snippet["values"]),
                    "Asset link state": "Paused",
                }
            )
        calls.append(
            {
                "Campaign": spec.name,
                "Country code": "US",
                "Phone number": CALL_PHONE,
                "Asset link state": "Paused",
            }
        )
        goals.append(
            {
                "Campaign": spec.name,
                "Custom conversion goal": CONVERSION_GOAL,
                "Conversion action IDs": ";".join(spec.conversion_goals),
            }
        )
        api_status.append(
            {
                "Campaign name": spec.name,
                "Campaign ID": "",
                "Status": "NOT CREATED — API EXPLORER QUOTA BLOCK",
                "Ad groups": len(spec.ad_groups),
                "Keywords": sum(len(group.keywords) for group in spec.ad_groups),
                "Ads": sum(1 for group in spec.ad_groups if group.rsa is not None),
                "Final URL": spec.final_url or "",
                "Geo": "; ".join(spec.geo_target_names),
                "Conversion goal": CONVERSION_GOAL,
                "Upload errors or warnings": (
                    "RESOURCE_EXHAUSTED: Number of operations for explorer access; "
                    "validate-only request ID iULWrXJhORBEGMTScmqKYQ; retry in 26481 seconds"
                ),
            }
        )

    files = [
        _write_csv("00_api_upload_status.csv", api_status),
        _write_csv("01_campaigns.csv", campaigns),
        _write_csv("02_locations.csv", locations),
        _write_csv("03_ad_groups.csv", ad_groups),
        _write_csv("04_keywords.csv", keywords),
        _write_csv("05_responsive_search_ads.csv", ads),
        _write_csv("06_campaign_negatives.csv", negatives),
        _write_csv("07_sitelinks.csv", sitelinks),
        _write_csv("08_callouts.csv", callouts),
        _write_csv("09_structured_snippets.csv", snippets),
        _write_csv("10_call_assets.csv", calls),
        _write_csv("11_campaign_conversion_goals.csv", goals),
    ]
    summary = {
        "generated_at": datetime.now(UTC).isoformat(),
        "reason": (
            "Fallback generated only after Google Ads API validate-only was blocked "
            "by Explorer Access operation quota."
        ),
        "api_error": {
            "status": "RESOURCE_EXHAUSTED",
            "http_status": 429,
            "message": "Too many requests. Retry in 26481 seconds.",
            "quota": "Number of operations for explorer access",
            "request_id": "iULWrXJhORBEGMTScmqKYQ",
            "resources_created": 0,
        },
        "customer_id": "6769947952",
        "all_campaigns_paused": True,
        "bakersfield_vendor_hold": True,
        "counts": {
            "campaigns": len(campaigns),
            "locations": len(locations),
            "ad_groups": len(ad_groups),
            "keywords": len(keywords),
            "responsive_search_ads": len(ads),
            "campaign_negatives": len(negatives),
            "sitelinks": len(sitelinks),
            "callouts": len(callouts),
            "structured_snippets": len(snippets),
            "call_assets": len(calls),
            "campaign_conversion_goals": len(goals),
            "headlines_per_rsa": dict(
                sorted(
                    Counter(
                        len(ad_group.rsa.headlines)
                        for campaign in specs
                        for ad_group in campaign.ad_groups
                    ).items()
                )
            ),
        },
        "files": [str(path) for path in files],
    }
    (OUT / "manifest.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
