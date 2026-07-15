#!/usr/bin/env python3
"""Check shared negative lists against campaign specs for conflicts.

Offline — no API required.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any

import yaml

from ela_google_ads.models.spec import CampaignSpec, campaign_spec_from_dict
from ela_google_ads.validators.spec_validators import load_spec_file

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "specs"
SHARED = SPECS / "shared"


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _collect_negatives_from_file(path: Path) -> list[dict[str, str]]:
    data = _load_yaml(path)
    rows: list[dict[str, str]] = []
    source = path.name

    if "keywords" in data:
        for kw in data["keywords"]:
            rows.append(
                {
                    "source": source,
                    "list": "root",
                    "text": str(kw.get("text", "")).strip(),
                    "match_type": str(kw.get("match_type", "PHRASE")).upper(),
                    "tier": str(data.get("tier", data.get("status", ""))),
                }
            )

    for list_name, lst in (data.get("lists") or {}).items():
        for kw in lst.get("keywords", []):
            rows.append(
                {
                    "source": source,
                    "list": list_name,
                    "text": str(kw.get("text", "")).strip(),
                    "match_type": str(kw.get("match_type", "PHRASE")).upper(),
                    "tier": str(lst.get("tier", "")),
                }
            )
    return [row for row in rows if row["text"]]


def _blocked(positive: str, pos_match: str, neg_text: str, neg_match: str) -> bool:
    pos_norm = _norm(positive)
    neg_norm = _norm(neg_text)
    if neg_match == "EXACT":
        return pos_norm == neg_norm
    if neg_match == "PHRASE":
        return neg_norm in pos_norm
    if pos_match == "EXACT" and neg_match == "PHRASE":
        return neg_norm in pos_norm
    return False


def find_conflicts(
    spec: CampaignSpec,
    negatives: list[dict[str, str]],
) -> list[dict[str, str]]:
    conflicts: list[dict[str, str]] = []
    for ag in spec.ad_groups:
        for kw in ag.keywords:
            for neg in negatives:
                if _blocked(kw.text, kw.match_type, neg["text"], neg["match_type"]):
                    conflicts.append(
                        {
                            "campaign": spec.name,
                            "ad_group": ag.name,
                            "positive": kw.text,
                            "positive_match": kw.match_type,
                            "negative": neg["text"],
                            "negative_match": neg["match_type"],
                            "negative_list": f"{neg['source']}::{neg['list']}",
                            "tier": neg.get("tier", ""),
                        }
                    )
    return conflicts


def export_upload_csv(negatives: list[dict[str, str]], path: Path, *, tier: str | None) -> int:
    rows = negatives
    if tier:
        rows = [row for row in rows if row.get("tier") == tier]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["list_name", "keyword", "match_type", "tier", "source_file"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "list_name": row["list"],
                    "keyword": row["text"],
                    "match_type": row["match_type"],
                    "tier": row.get("tier", ""),
                    "source_file": row["source"],
                }
            )
    return len(rows)


def _load_attachment_lists() -> tuple[list[str], list[str]]:
    locked = _load_yaml(SHARED / "negative-keywords-locked.yaml")
    return (
        list(locked.get("attach_to_en_campaigns", {}).get("launch_lists", [])),
        list(locked.get("attach_to_es_campaigns", {}).get("launch_lists", [])),
    )


def export_attachment_csv(
    negatives: list[dict[str, str]],
    path: Path,
    *,
    allowed_lists: set[str],
    list_name_map: dict[str, str],
) -> int:
    rows = [row for row in negatives if row.get("tier") == "launch" and row["list"] in allowed_lists]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["shared_list_name", "list_key", "keyword", "match_type"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "shared_list_name": list_name_map.get(row["list"], row["list"]),
                    "list_key": row["list"],
                    "keyword": row["text"],
                    "match_type": row["match_type"],
                }
            )
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec",
        type=Path,
        default=SPECS / "bakersfield-en.yaml",
        help="Campaign spec to check (default: bakersfield-en.yaml)",
    )
    parser.add_argument(
        "--all-specs",
        action="store_true",
        help="Check every *-en.yaml and *-es.yaml market spec",
    )
    parser.add_argument(
        "--export-csv",
        type=Path,
        default=ROOT / "output" / "negative_keywords_upload.csv",
        help="Export negatives for Google Ads Editor / UI upload",
    )
    parser.add_argument(
        "--tier",
        choices=["launch", "post_launch"],
        default="launch",
        help="Export/check only negatives tagged with this tier",
    )
    args = parser.parse_args()

    negative_files = [
        SHARED / "negative-lists.yaml",
        SHARED / "brand-negatives.yaml",
    ]
    negatives = []
    for path in negative_files:
        if path.is_file():
            negatives.extend(_collect_negatives_from_file(path))

    tier_negatives = [row for row in negatives if row.get("tier") == args.tier]
    print(f"Loaded {len(negatives)} negatives ({len(tier_negatives)} tier={args.tier})")

    spec_paths: list[Path]
    if args.all_specs:
        spec_paths = sorted(
            p
            for p in SPECS.glob("*-*.yaml")
            if p.name != "markets.yaml" and not p.name.startswith("shared")
        )
    else:
        spec_paths = [args.spec]

    total_conflicts = 0
    for spec_path in spec_paths:
        spec = load_spec_file(spec_path)
        conflicts = find_conflicts(spec, tier_negatives)
        if conflicts:
            print(f"\n{spec.name}: {len(conflicts)} conflict(s)")
            for conflict in conflicts[:15]:
                print(
                    f"  - [{conflict['ad_group']}] +'{conflict['positive']}' "
                    f"blocked by -'{conflict['negative']}' ({conflict['negative_list']})"
                )
            if len(conflicts) > 15:
                print(f"  ... and {len(conflicts) - 15} more")
            total_conflicts += len(conflicts)
        else:
            print(f"{spec.name}: OK (0 conflicts)")

    exported = export_upload_csv(negatives, args.export_csv, tier=args.tier)
    print(f"\nWrote {exported} negatives -> {args.export_csv}")

    locked = _load_yaml(SHARED / "negative-keywords-locked.yaml")
    list_name_map = locked.get("shared_list_names", {})
    en_lists, es_lists = _load_attachment_lists()
    en_path = ROOT / "output" / "negative_keywords_upload_en.csv"
    es_path = ROOT / "output" / "negative_keywords_upload_es.csv"
    en_count = export_attachment_csv(
        negatives,
        en_path,
        allowed_lists=set(en_lists),
        list_name_map=list_name_map,
    )
    es_count = export_attachment_csv(
        negatives,
        es_path,
        allowed_lists=set(es_lists),
        list_name_map=list_name_map,
    )
    print(f"Wrote {en_count} EN attach negatives -> {en_path}")
    print(f"Wrote {es_count} ES attach negatives -> {es_path}")

    if total_conflicts:
        print(f"\nWARNING: {total_conflicts} positive/negative conflict(s) found.")
        return 2
    print("\nNo launch-tier conflicts detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
