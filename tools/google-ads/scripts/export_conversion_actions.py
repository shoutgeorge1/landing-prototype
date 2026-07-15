#!/usr/bin/env python3
"""Export conversion actions (read-only)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ela_google_ads.config import load_settings  # noqa: E402
from ela_google_ads.conversions.inventory import list_conversion_actions  # noqa: E402
from ela_google_ads.exceptions import ElaGoogleAdsError  # noqa: E402
from ela_google_ads.export_utils import export_records  # noqa: E402
from ela_google_ads.logging_config import configure_logging  # noqa: E402


def main() -> int:
    configure_logging()
    settings = load_settings()
    try:
        rows = list_conversion_actions(settings)
    except ElaGoogleAdsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    paths = export_records(
        settings.output_dir,
        "conversion_actions",
        rows,
        metadata={"customer_id": settings.customer_id},
    )
    print(f"Exported {len(rows)} conversion actions")
    print(paths["csv"])
    print(paths["json"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
