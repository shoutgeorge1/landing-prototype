"""CSV / JSON export helpers."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ela_google_ads.logging_config import get_logger

logger = get_logger(__name__)


def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def timestamp_slug() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def write_json(path: Path, payload: Any) -> Path:
    ensure_output_dir(path.parent)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    logger.info("Wrote JSON export: %s", path)
    return path


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> Path:
    ensure_output_dir(path.parent)
    if not fieldnames:
        keys: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for key in row:
                if key not in seen:
                    seen.add(key)
                    keys.append(key)
        fieldnames = keys
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _csv_value(row.get(k)) for k in fieldnames})
    logger.info("Wrote CSV export: %s (%s rows)", path, len(rows))
    return path


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, default=str)
    return value


def export_records(
    output_dir: Path,
    stem: str,
    rows: list[dict[str, Any]],
    *,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Write paired CSV + JSON exports under output_dir."""
    ensure_output_dir(output_dir)
    stamp = timestamp_slug()
    json_path = output_dir / f"{stem}_{stamp}.json"
    csv_path = output_dir / f"{stem}_{stamp}.csv"
    payload = {
        "exported_at": datetime.now(UTC).isoformat(),
        "row_count": len(rows),
        "metadata": metadata or {},
        "rows": rows,
    }
    write_json(json_path, payload)
    write_csv(csv_path, rows)
    return {"json": json_path, "csv": csv_path}
