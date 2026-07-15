#!/usr/bin/env python3
"""Export asset inventory including call assets (read-only)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ela_google_ads.assets.inventory import list_assets, phone_tracking_warnings  # noqa: E402
from ela_google_ads.config import load_settings  # noqa: E402
from ela_google_ads.exceptions import ElaGoogleAdsError  # noqa: E402
from ela_google_ads.export_utils import export_records  # noqa: E402
from ela_google_ads.logging_config import configure_logging  # noqa: E402


def main() -> int:
    configure_logging()
    settings = load_settings()
    try:
        rows = list_assets(settings)
    except ElaGoogleAdsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    paths = export_records(
        settings.output_dir,
        "assets",
        rows,
        metadata={"customer_id": settings.customer_id},
    )
    call_assets = [r for r in rows if "CALL" in str(r.get("type", ""))]
    for warning in phone_tracking_warnings(settings, call_assets=call_assets):
        print(f"WARNING: {warning}")
    print(f"Exported {len(rows)} assets ({len(call_assets)} call)")
    print(paths["csv"])
    print(paths["json"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
