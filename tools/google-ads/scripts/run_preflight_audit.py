#!/usr/bin/env python3
"""Run read-only preflight audit (live API + specs + URL QA)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ela_google_ads.logging_config import configure_logging
from ela_google_ads.preflight.audit import run_preflight_audit


def main() -> int:
    parser = argparse.ArgumentParser(description="ELA Google Ads read-only preflight audit")
    parser.add_argument(
        "--skip-api",
        action="store_true",
        help="Skip live Google Ads API exports (offline spec/URL checks only)",
    )
    parser.add_argument(
        "--skip-urls",
        action="store_true",
        help="Skip HTTP landing-page QA",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()
    configure_logging(level="DEBUG" if args.verbose else "INFO")

    root = Path(__file__).resolve().parents[1]
    summary = run_preflight_audit(
        specs_dir=root / "specs",
        output_dir=root / "output",
        docs_dir=root / "docs",
        skip_api=args.skip_api,
        skip_urls=args.skip_urls,
    )
    print("Preflight audit complete (read-only).")
    print(f"  Specs audited: {summary['spec_count']}")
    print(f"  Classifications: {summary['classifications']}")
    print(f"  URL issues: {summary['url_issues']}")
    print(f"  Keyword conflicts: {summary['keyword_conflicts']}")
    print(f"  Live overlaps: {summary['live_overlaps']}")
    print(f"  Report: {summary['report_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
