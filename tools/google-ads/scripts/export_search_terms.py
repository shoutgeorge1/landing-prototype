#!/usr/bin/env python3
"""Export search-term report when data exists (read-only)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ela_google_ads.config import load_settings  # noqa: E402
from ela_google_ads.exceptions import ElaGoogleAdsError  # noqa: E402
from ela_google_ads.export_utils import export_records  # noqa: E402
from ela_google_ads.logging_config import configure_logging  # noqa: E402
from ela_google_ads.reports.search_terms import list_search_terms  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30, choices=[7, 14, 30])
    args = parser.parse_args()
    configure_logging()
    settings = load_settings()
    try:
        rows = list_search_terms(settings, days=args.days)
    except ElaGoogleAdsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    paths = export_records(
        settings.output_dir,
        "search_terms",
        rows,
        metadata={"customer_id": settings.customer_id, "days": args.days},
    )
    print(f"Exported {len(rows)} search terms (last {args.days} days)")
    print(paths["csv"])
    print(paths["json"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
