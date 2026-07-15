#!/usr/bin/env python3
"""List Google Ads customers accessible to the configured OAuth user."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ela_google_ads.account.access import list_accessible_customers  # noqa: E402
from ela_google_ads.config import load_settings  # noqa: E402
from ela_google_ads.exceptions import ElaGoogleAdsError  # noqa: E402
from ela_google_ads.logging_config import configure_logging  # noqa: E402


def main() -> int:
    configure_logging()
    settings = load_settings()
    try:
        names = list_accessible_customers(settings)
    except ElaGoogleAdsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if not names:
        print("No accessible customers returned.")
        return 0
    for name in names:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
