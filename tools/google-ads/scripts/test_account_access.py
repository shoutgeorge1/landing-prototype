#!/usr/bin/env python3
"""Test read access to the configured Google Ads customer account."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ela_google_ads.account.access import get_account_access_summary  # noqa: E402
from ela_google_ads.config import load_settings  # noqa: E402
from ela_google_ads.exceptions import ElaGoogleAdsError  # noqa: E402
from ela_google_ads.logging_config import configure_logging  # noqa: E402


def main() -> int:
    configure_logging()
    settings = load_settings()
    try:
        summary = get_account_access_summary(settings)
    except ElaGoogleAdsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(
            "\nCredentials are required for live access. "
            "Complete .env setup and OAuth before retrying.",
            file=sys.stderr,
        )
        return 1
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
