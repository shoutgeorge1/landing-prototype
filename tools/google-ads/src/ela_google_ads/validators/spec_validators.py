"""Campaign-spec and RSA validators (offline — no API required)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from ela_google_ads.exceptions import ValidationError
from ela_google_ads.models.spec import (
    ALLOWED_CHANNELS,
    ALLOWED_MATCH_TYPES,
    CampaignSpec,
    campaign_spec_from_dict,
)
from ela_google_ads.safety import ALLOWED_NEW_CAMPAIGN_STATUS

RSA_HEADLINE_MAX = 30
RSA_DESCRIPTION_MAX = 90
RSA_PATH_MAX = 15
RSA_HEADLINE_MIN_COUNT = 3
RSA_DESCRIPTION_MIN_COUNT = 2
RSA_HEADLINE_MAX_COUNT = 15
RSA_DESCRIPTION_MAX_COUNT = 4

POLICY_RISK_PATTERNS = [
    (re.compile(r"\bguaranteed?\b", re.I), "Avoid guaranteed-outcome language"),
    (re.compile(r"\b100%\b"), "Avoid absolute guarantees"),
    (re.compile(r"\balways\s+win\b", re.I), "Avoid unverified outcome claims"),
    (re.compile(r"\bact\s+now\b", re.I), "Avoid fake urgency"),
    (re.compile(r"\blimited\s+time\b", re.I), "Avoid fake urgency"),
    (re.compile(r"\bbest\s+lawyer\b", re.I), "Avoid unverified superlatives"),
    (re.compile(r"#1\b"), "Avoid unverified superlatives"),
    (re.compile(r"\bfree\s+consultation\s+guaranteed\b", re.I), "Avoid guarantee language"),
]

PLACEHOLDER_PATTERNS = [
    re.compile(r"TODO", re.I),
    re.compile(r"TBD", re.I),
    re.compile(r"PLACEHOLDER", re.I),
    re.compile(r"lorem ipsum", re.I),
    re.compile(r"\[.*(insert|headline|description).*\]", re.I),
]


def load_spec_file(path: Path | str) -> CampaignSpec:
    path = Path(path)
    if not path.is_file():
        raise ValidationError(f"Spec file not found: {path}")
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(text)
    elif path.suffix.lower() == ".json":
        import json

        data = json.loads(text)
    else:
        raise ValidationError(f"Unsupported spec extension: {path.suffix}")
    if not isinstance(data, dict):
        raise ValidationError("Campaign spec must be a mapping/object at the top level")
    return campaign_spec_from_dict(data)


def validate_final_url(url: str | None, *, field: str = "final_url") -> list[str]:
    issues: list[str] = []
    if not url or not str(url).strip():
        issues.append(f"{field} is required")
        return issues
    parsed = urlparse(str(url).strip())
    if parsed.scheme not in {"http", "https"}:
        issues.append(f"{field} must be http(s): {url!r}")
    if not parsed.netloc:
        issues.append(f"{field} is missing a host: {url!r}")
    return issues


def validate_rsa(rsa: Any, *, ad_group: str) -> list[str]:
    issues: list[str] = []
    if rsa is None:
        issues.append(f"Ad group '{ad_group}' is missing RSA copy")
        return issues

    headlines = [h.strip() for h in (rsa.headlines or []) if str(h).strip()]
    descriptions = [d.strip() for d in (rsa.descriptions or []) if str(d).strip()]

    if len(headlines) < RSA_HEADLINE_MIN_COUNT:
        issues.append(
            f"Ad group '{ad_group}': need at least {RSA_HEADLINE_MIN_COUNT} headlines"
        )
    if len(headlines) > RSA_HEADLINE_MAX_COUNT:
        issues.append(
            f"Ad group '{ad_group}': at most {RSA_HEADLINE_MAX_COUNT} headlines allowed"
        )
    if len(descriptions) < RSA_DESCRIPTION_MIN_COUNT:
        issues.append(
            f"Ad group '{ad_group}': need at least {RSA_DESCRIPTION_MIN_COUNT} descriptions"
        )
    if len(descriptions) > RSA_DESCRIPTION_MAX_COUNT:
        issues.append(
            f"Ad group '{ad_group}': at most {RSA_DESCRIPTION_MAX_COUNT} descriptions allowed"
        )

    for h in headlines:
        if len(h) > RSA_HEADLINE_MAX:
            issues.append(
                f"Ad group '{ad_group}': headline exceeds {RSA_HEADLINE_MAX} chars: {h!r}"
            )
        for pat in PLACEHOLDER_PATTERNS:
            if pat.search(h):
                issues.append(f"Ad group '{ad_group}': placeholder copy not allowed: {h!r}")
        for pat, msg in POLICY_RISK_PATTERNS:
            if pat.search(h):
                issues.append(f"Ad group '{ad_group}' policy risk in headline ({msg}): {h!r}")

    for d in descriptions:
        if len(d) > RSA_DESCRIPTION_MAX:
            issues.append(
                f"Ad group '{ad_group}': description exceeds {RSA_DESCRIPTION_MAX} chars: {d!r}"
            )
        for pat in PLACEHOLDER_PATTERNS:
            if pat.search(d):
                issues.append(
                    f"Ad group '{ad_group}': placeholder copy not allowed: {d!r}"
                )
        for pat, msg in POLICY_RISK_PATTERNS:
            if pat.search(d):
                issues.append(
                    f"Ad group '{ad_group}' policy risk in description ({msg}): {d!r}"
                )

    duplicates = _duplicates(headlines + descriptions)
    for dup in duplicates:
        issues.append(f"Ad group '{ad_group}': duplicate RSA text: {dup!r}")

    if rsa.path1 and len(rsa.path1) > RSA_PATH_MAX:
        issues.append(f"Ad group '{ad_group}': path1 exceeds {RSA_PATH_MAX} chars")
    if rsa.path2 and len(rsa.path2) > RSA_PATH_MAX:
        issues.append(f"Ad group '{ad_group}': path2 exceeds {RSA_PATH_MAX} chars")

    return issues


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    dups: list[str] = []
    for value in values:
        key = value.strip().lower()
        if key in seen and value not in dups:
            dups.append(value)
        seen.add(key)
    return dups


def normalize_keyword_key(text: str, match_type: str) -> str:
    cleaned = re.sub(r"[+\]\[]", "", text.strip().lower())
    cleaned = re.sub(r"\s+", " ", cleaned)
    return f"{match_type.upper()}::{cleaned}"


def find_positive_negative_conflicts(spec: CampaignSpec) -> list[str]:
    """Report positives that may be blocked by negatives (exact/phrase heuristics)."""
    issues: list[str] = []
    negatives: list[tuple[str, str]] = []
    for kw in spec.campaign_negative_keywords:
        negatives.append((kw.text, kw.match_type))
    for ag in spec.ad_groups:
        for kw in ag.negative_keywords:
            negatives.append((kw.text, kw.match_type))

    def blocked(positive: str, pos_match: str) -> str | None:
        pos_norm = re.sub(r"\s+", " ", positive.strip().lower())
        for neg_text, neg_match in negatives:
            neg_norm = re.sub(r"\s+", " ", neg_text.strip().lower())
            if neg_match.upper() == "EXACT" and pos_norm == neg_norm:
                return neg_text
            if neg_match.upper() == "PHRASE" and neg_norm in pos_norm:
                return neg_text
            if (
                pos_match.upper() == "EXACT"
                and neg_match.upper() == "PHRASE"
                and neg_norm in pos_norm
            ):
                return neg_text
        return None

    for ag in spec.ad_groups:
        for kw in ag.keywords:
            conflict = blocked(kw.text, kw.match_type)
            if conflict:
                issues.append(
                    f"Conflict in '{ag.name}': positive '{kw.text}' "
                    f"blocked by negative '{conflict}'"
                )
    return issues


def validate_campaign_spec(spec: CampaignSpec) -> list[str]:
    issues: list[str] = []

    if not spec.name:
        issues.append("Campaign name is required")
    if spec.status != ALLOWED_NEW_CAMPAIGN_STATUS:
        issues.append(
            f"Campaign status must be {ALLOWED_NEW_CAMPAIGN_STATUS} for creation "
            f"(got {spec.status!r})"
        )
    if spec.channel not in ALLOWED_CHANNELS:
        issues.append(f"Only SEARCH channel supported in this phase (got {spec.channel})")
    if spec.daily_budget <= 0:
        issues.append(f"daily_budget must be > 0 (got {spec.daily_budget})")
    if not spec.geo_target_ids and not spec.geo_target_names:
        issues.append("At least one geo_target_id or geo_target_name is required")
    if not spec.location_presence_only:
        issues.append(
            "location_presence_only should be true (presence-based targeting required)"
        )
    if not spec.language_ids:
        issues.append("language_ids is required (e.g. English=1000, Spanish=1003)")
    if spec.network.target_content_network:
        issues.append("Display/content network must remain disabled")
    if spec.brand.internal_campaign_type.lower() != "nonbrand":
        issues.append("internal_campaign_type must be 'nonbrand' for internally managed campaigns")
    if not spec.brand.brand_lane_owner:
        issues.append("brand_lane_owner is required (expected hawksem for brand lane)")

    issues.extend(validate_final_url(spec.final_url, field="campaign.final_url"))

    ag_names: set[str] = set()
    for ag in spec.ad_groups:
        if not ag.name:
            issues.append("Ad group name is required")
        elif ag.name in ag_names:
            issues.append(f"Duplicate ad-group name: {ag.name!r}")
        else:
            ag_names.add(ag.name)

        issues.extend(
            validate_final_url(
                ag.final_url or spec.final_url,
                field=f"{ag.name}.final_url",
            )
        )

        if not ag.keywords:
            issues.append(f"Ad group '{ag.name}' has no keywords")
        for kw in ag.keywords:
            if not kw.text.strip():
                issues.append(f"Ad group '{ag.name}' has an empty keyword")
            if kw.match_type.upper() not in ALLOWED_MATCH_TYPES:
                issues.append(
                    f"Ad group '{ag.name}': match type {kw.match_type!r} not allowed "
                    f"(use EXACT or PHRASE; broad match disabled by default)"
                )
            if "{keyword" in kw.text.lower():
                issues.append(
                    f"Ad group '{ag.name}': Dynamic Keyword Insertion is disabled by default"
                )
        issues.extend(validate_rsa(ag.rsa, ad_group=ag.name))

    if not spec.ad_groups:
        issues.append("At least one ad group is required")

    issues.extend(find_positive_negative_conflicts(spec))
    return issues


def validate_spec_file(path: Path | str) -> tuple[CampaignSpec, list[str]]:
    spec = load_spec_file(path)
    return spec, validate_campaign_spec(spec)


def assert_spec_valid(path: Path | str) -> CampaignSpec:
    spec, issues = validate_spec_file(path)
    if issues:
        raise ValidationError(
            f"Spec validation failed with {len(issues)} issue(s)",
            issues=issues,
        )
    return spec
