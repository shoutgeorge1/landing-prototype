#!/usr/bin/env python3
"""Export a read-only account configuration snapshot."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ela_google_ads.account.snapshot import build_account_snapshot  # noqa: E402
from ela_google_ads.config import load_settings  # noqa: E402
from ela_google_ads.exceptions import ElaGoogleAdsError  # noqa: E402
from ela_google_ads.export_utils import export_records, write_json  # noqa: E402
from ela_google_ads.logging_config import configure_logging  # noqa: E402


def main() -> int:
    configure_logging()
    settings = load_settings()
    try:
        snapshot = build_account_snapshot(settings)
    except ElaGoogleAdsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    paths = export_records(
        settings.output_dir,
        "account_snapshot",
        [snapshot["account"]],
        metadata={"counts": snapshot["counts"], "warnings": snapshot["warnings"]},
    )
    full = write_json(settings.output_dir / "account_snapshot_latest.json", snapshot)
    print(f"Wrote {paths['json']}")
    print(f"Wrote {paths['csv']}")
    print(f"Wrote {full}")
    for warning in snapshot.get("warnings") or []:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
