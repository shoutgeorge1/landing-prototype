"""Keyword helpers and negative-list loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ela_google_ads.logging_config import get_logger
from ela_google_ads.models.spec import CampaignSpec
from ela_google_ads.validators.spec_validators import find_positive_negative_conflicts

logger = get_logger(__name__)


def load_negative_lists(path: Path | str) -> dict[str, Any]:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Negative list file must be a mapping: {path}")
    return data


def conflict_report(spec: CampaignSpec) -> dict[str, Any]:
    conflicts = find_positive_negative_conflicts(spec)
    return {
        "campaign": spec.name,
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "guidance": (
            "Do not blindly apply negatives that could block legitimate employment-law cases. "
            "Review conflicts before apply."
        ),
    }
