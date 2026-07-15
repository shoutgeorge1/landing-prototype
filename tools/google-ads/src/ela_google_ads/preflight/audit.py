"""Read-only preflight audit: live account + generated specs + URL QA."""

from __future__ import annotations

import re
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import yaml

from ela_google_ads.account.snapshot import build_account_snapshot
from ela_google_ads.ads.inventory import list_campaign_network_settings, list_responsive_search_ads
from ela_google_ads.config import GoogleAdsSettings, load_settings
from ela_google_ads.export_utils import ensure_output_dir, write_csv
from ela_google_ads.keywords.inventory import list_negative_keywords, list_positive_keywords
from ela_google_ads.logging_config import get_logger
from ela_google_ads.models.spec import CampaignSpec
from ela_google_ads.reports.search_terms import list_search_terms
from ela_google_ads.validators.spec_validators import (
    find_positive_negative_conflicts,
    load_spec_file,
    validate_campaign_spec,
)

logger = get_logger(__name__)

CLASS_READY = "READY FOR MANUAL REVIEW"
CLASS_BLOCKED = "BLOCKED"
CLASS_LANDING_QA = "GENERATED — LANDING PAGE QA REQUIRED"
CLASS_OVERLAP = "DO NOT LAUNCH WITH OVERLAPPING MARKET"

TARGET_CONVERSION_ID = "7569909838"
DOMAIN = "help.employmentlawassist.com"

BRAND_TERMS = [
    "employment law assist",
    "employmentlawassist",
    "ela employment",
    "employment law assist apc",
]

RISK_POSITIVE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(jobs?|careers?|hiring|paralegal jobs?)\b", re.I), "job_seeker"),
    (re.compile(r"\bfree legal advice\b", re.I), "free_advice"),
    (re.compile(r"\b(pro bono|legal aid)\b", re.I), "free_advice"),
    (re.compile(r"\b(law school|bar exam|lsat)\b", re.I), "education"),
    (re.compile(r"\b(employer defense|hr compliance|terminate employee)\b", re.I), "employer_side"),
    (re.compile(r"\b(template|sample letter|diy)\b", re.I), "diy"),
]

SPANISH_LEAK_PATTERNS = [
    re.compile(r"\bwrongful termination\b", re.I),
    re.compile(r"\bfree case review\b", re.I),
    re.compile(r"\bemployment lawyer\b", re.I),
]

EN_THANK_YOU = "/thank-you"
ES_THANK_YOU = "/gracias"

USER_AGENT = "ELA-GoogleAds-Preflight/1.0 (+read-only audit)"


@dataclass
class SpecAuditResult:
    spec_file: str
    campaign_name: str
    city: str
    language: str
    classification: str
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    keyword_conflict_count: int = 0
    live_overlap_count: int = 0
    url_qa_status: str = ""
    conversion_goal_ok: bool = False
    call_assets_in_spec: bool = False


def discover_spec_files(specs_dir: Path) -> list[Path]:
    return sorted(specs_dir.glob("*-en.yaml")) + sorted(specs_dir.glob("*-es.yaml"))


def load_markets_matrix(specs_dir: Path) -> dict[str, Any]:
    path = specs_dir / "markets.yaml"
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_shared_negative_texts(specs_dir: Path) -> list[str]:
    texts: list[str] = []
    for rel in ("shared/negative-lists.yaml", "shared/brand-negatives.yaml"):
        path = specs_dir / rel
        if not path.is_file():
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if "keywords" in data:
            for kw in data["keywords"]:
                texts.append(str(kw.get("text", "")).lower())
        for lst in (data.get("lists") or {}).values():
            for kw in lst.get("keywords", []):
                texts.append(str(kw.get("text", "")).lower())
    return [t for t in texts if t]


def _market_by_slug(markets_data: dict[str, Any], slug: str) -> dict[str, Any] | None:
    for market in markets_data.get("markets", []):
        if market.get("slug") == slug:
            return market
    return None


def check_city_keyword_modifier(
    spec: CampaignSpec, market: dict[str, Any] | None
) -> tuple[list[str], list[str]]:
    """Return (blockers, warnings) for city/county keyword alignment."""
    blockers: list[str] = []
    warnings: list[str] = []
    city = (spec.city or "").lower()
    city_name = (market or {}).get("city", spec.city or "").lower()
    county_tokens: list[str] = []
    for name in spec.geo_target_names:
        if "county" in name.lower():
            county_tokens.append(name.split(",")[0].replace(" County", "").strip().lower())

    allow_generic_near_me = {"employment law attorney near me", "employment lawyer near me"}
    bleed_markers = {
        "kern county": {"bakersfield"},
        "bakersfield": {"bakersfield"},
        "fresno county": {"fresno"},
        "san joaquin county": {"stockton"},
        "stanislaus county": {"modesto"},
    }

    for ag in spec.ad_groups:
        has_city_kw = False
        for kw in ag.keywords:
            text = kw.text.lower()
            if text in allow_generic_near_me:
                continue
            has_city = city in text or city_name in text
            has_county = any(token in text for token in county_tokens if token)
            if has_city or has_county:
                has_city_kw = True
            for marker, allowed_cities in bleed_markers.items():
                if marker in text and city not in allowed_cities:
                    blockers.append(
                        f"Template keyword bleed: '{kw.text}' in '{ag.name}' "
                        f"(references '{marker}' outside {city})"
                    )
        if not has_city_kw:
            warnings.append(
                f"Ad group '{ag.name}' has no city/county-modified keywords"
            )
    return blockers, warnings


def check_brand_leaks(spec: CampaignSpec) -> list[str]:
    """Brand terms in positive keywords only (firm name in RSA is expected)."""
    issues: list[str] = []
    for ag in spec.ad_groups:
        for kw in ag.keywords:
            lower = kw.text.lower()
            for brand in BRAND_TERMS:
                if brand in lower:
                    issues.append(f"Brand term in positive keyword '{kw.text}' ({ag.name})")
    return issues


def check_risk_positives(spec: CampaignSpec) -> list[str]:
    issues: list[str] = []
    for ag in spec.ad_groups:
        for kw in ag.keywords:
            for pat, label in RISK_POSITIVE_PATTERNS:
                if pat.search(kw.text):
                    issues.append(
                        f"Risk keyword ({label}): '{kw.text}' in '{ag.name}'"
                    )
    return issues


def check_spanish_copy(spec: CampaignSpec) -> list[str]:
    if (spec.language or "").lower() != "es":
        return []
    issues: list[str] = []
    for ag in spec.ad_groups:
        if not ag.rsa:
            continue
        for line in (ag.rsa.headlines or []) + (ag.rsa.descriptions or []):
            for pat in SPANISH_LEAK_PATTERNS:
                if pat.search(line):
                    issues.append(f"English phrase in ES RSA: {line!r}")
    return issues


def check_tracking_suffix(
    spec: CampaignSpec, account_tracking_template: str | None
) -> list[str]:
    issues: list[str] = []
    suffix = (spec.tracking.final_url_suffix or "").lower()
    if not suffix:
        issues.append("Missing final_url_suffix for HubSpot google_* fields")
        return issues
    dup_params = ["utm_source", "utm_medium", "utm_campaign", "gclid", "hsa_cam"]
    for param in dup_params:
        if param in suffix:
            issues.append(
                f"final_url_suffix duplicates account param '{param}' — "
                "account tracking template already handles UTMs/hsa"
            )
    required = ["google_campaign", "google_ad_group", "google_keyword"]
    for param in required:
        if param not in suffix:
            issues.append(f"final_url_suffix missing HubSpot field param: {param}")
    if account_tracking_template and "utm_" in (account_tracking_template or "").lower():
        if "utm_" in suffix:
            issues.append("UTM params in suffix would duplicate account tracking_url_template")
    return issues


def check_language_ids(spec: CampaignSpec) -> list[str]:
    lang = (spec.language or "en").lower()
    expected = 1003 if lang == "es" else 1000
    if expected not in (spec.language_ids or []):
        return [f"language_ids should include {expected} for {lang.upper()} campaigns"]
    if len(spec.language_ids or []) > 1:
        return [f"Multiple language_ids on single-language campaign: {spec.language_ids}"]
    return []


def find_live_campaign_overlap(
    spec: CampaignSpec,
    live_campaigns: list[dict[str, Any]],
) -> list[dict[str, str]]:
    overlaps: list[dict[str, str]] = []
    city = (spec.city or "").lower()
    lang_hint = "spanish" if (spec.language or "").lower() == "es" else "english"
    for camp in live_campaigns:
        name = (camp.get("campaign_name") or "").lower()
        if city not in name and city.replace("-", " ") not in name:
            continue
        reason = "city_name_match"
        if "bakersfield" in city and ("law2" in name or "law--sch" in name):
            reason = "legacy_bakersfield_search"
        overlaps.append(
            {
                "spec_campaign": spec.name,
                "live_campaign_id": str(camp.get("campaign_id", "")),
                "live_campaign_name": camp.get("campaign_name", ""),
                "live_status": camp.get("status", ""),
                "overlap_reason": reason,
            }
        )
        _ = lang_hint
    return overlaps


def find_duplicate_spec_names(specs: list[tuple[Path, CampaignSpec]]) -> list[str]:
    seen: dict[str, str] = {}
    issues: list[str] = []
    for path, spec in specs:
        if spec.name in seen:
            issues.append(
                f"Duplicate campaign name {spec.name!r} in "
                f"{path.name} and {seen[spec.name]}"
            )
        else:
            seen[spec.name] = path.name
        ag_seen: set[str] = set()
        for ag in spec.ad_groups:
            if ag.name in ag_seen:
                issues.append(f"Duplicate ad group {ag.name!r} in {path.name}")
            ag_seen.add(ag.name)
    return issues


def classify_spec(
    *,
    blockers: list[str],
    market: dict[str, Any] | None,
    url_ok: bool,
    landing_status: str,
    overlap_group_conflict: bool,
) -> str:
    if overlap_group_conflict:
        return CLASS_OVERLAP
    if blockers:
        return CLASS_BLOCKED
    if landing_status != "active" or not url_ok:
        return CLASS_LANDING_QA
    return CLASS_READY


def fetch_url(url: str, *, timeout: float = 20.0) -> dict[str, Any]:
    chain: list[dict[str, Any]] = []
    current = url
    ssl_ctx = ssl.create_default_context()
    for _ in range(8):
        req = urllib.request.Request(
            current,
            method="GET",
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
                body = resp.read(500_000)
                status = resp.status
                final = resp.geturl()
                chain.append({"url": current, "status": status})
                if status in {301, 302, 303, 307, 308}:
                    location = resp.headers.get("Location")
                    if location:
                        current = urljoin(final, location)
                        continue
                html = body.decode("utf-8", errors="replace")
                return {
                    "ok": True,
                    "status": status,
                    "redirect_chain": chain,
                    "final_url": final,
                    "html": html,
                    "error": "",
                }
        except urllib.error.HTTPError as exc:
            chain.append({"url": current, "status": exc.code})
            try:
                html = exc.read(200_000).decode("utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                html = ""
            return {
                "ok": False,
                "status": exc.code,
                "redirect_chain": chain,
                "final_url": current,
                "html": html,
                "error": str(exc),
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "ok": False,
                "status": 0,
                "redirect_chain": chain,
                "final_url": current,
                "html": "",
                "error": str(exc),
            }
    return {
        "ok": False,
        "status": 0,
        "redirect_chain": chain,
        "final_url": current,
        "html": "",
        "error": "redirect_loop",
    }


def parse_page_signals(html: str, *, expected_lang: str, city_name: str) -> dict[str, Any]:
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    h1_raw = h1_match.group(1) if h1_match else ""
    h1 = re.sub(r"<[^>]+>", "", h1_raw)
    h1 = re.sub(r"\s+", " ", h1).strip()

    has_native_form = "ela-native-form" in html or 'id="lead-form"' in html
    has_firstname = 'name="firstname"' in html or "firstname" in html.lower()
    has_hubspot_api = "api.hsforms.com" in html
    has_google_campaign_js = "google_campaign" in html
    has_google_ad_group_js = "google_ad_group" in html
    has_google_keyword_js = "google_keyword" in html

    lang_attr = ""
    html_tag = re.search(r"<html[^>]*\blang=[\"']([^\"']+)[\"']", html, re.I)
    if html_tag:
        lang_attr = html_tag.group(1).lower()

    issues: list[str] = []
    if expected_lang == "es":
        if "english" in title.lower() and "español" not in title.lower():
            issues.append("title_looks_english")
        if h1 and city_name.lower() not in h1.lower():
            issues.append("h1_city_mismatch")
    else:
        if "abogado" in h1.lower() or "español" in title.lower():
            issues.append("spanish_content_on_en_page")

    if not has_native_form:
        issues.append("native_form_missing")
    if not has_firstname:
        issues.append("form_fields_missing")
    if expected_lang == "es" and lang_attr == "en":
        issues.append("html_lang_mismatch_es")

    tracking_note = ""
    if not has_google_campaign_js:
        tracking_note = "google_ads_params_client_side"

    return {
        "page_title": title,
        "h1": h1,
        "html_lang": lang_attr,
        "has_native_form": has_native_form,
        "has_form_fields": has_firstname,
        "has_hubspot_api_ref": has_hubspot_api,
        "has_google_campaign_js": has_google_campaign_js,
        "has_google_ad_group_js": has_google_ad_group_js,
        "has_google_keyword_js": has_google_keyword_js,
        "tracking_note": tracking_note,
        "issues": issues,
    }


def audit_urls_for_specs(
    specs: list[tuple[Path, CampaignSpec]],
    markets_data: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    checked: set[str] = set()

    def add_row(url: str, lang: str, city_slug: str, city_name: str, spec_name: str) -> None:
        if url in checked:
            return
        checked.add(url)
        result = fetch_url(url)
        signals = parse_page_signals(
            result.get("html", ""),
            expected_lang=lang,
            city_name=city_name,
        )
        rows.append(
            {
                "url": url,
                "spec_campaign": spec_name,
                "city": city_slug,
                "language": lang,
                "http_status": result.get("status", 0),
                "redirect_chain": " -> ".join(
                    f"{c['url']} ({c['status']})" for c in result.get("redirect_chain", [])
                ),
                "final_url": result.get("final_url", ""),
                "page_title": signals["page_title"],
                "h1": signals["h1"],
                "html_lang": signals["html_lang"],
                "has_native_form": signals["has_native_form"],
                "has_form_fields": signals["has_form_fields"],
                "has_hubspot_api_ref": signals["has_hubspot_api_ref"],
                "has_google_campaign_js": signals["has_google_campaign_js"],
                "has_google_ad_group_js": signals["has_google_ad_group_js"],
                "has_google_keyword_js": signals["has_google_keyword_js"],
                "tracking_note": signals.get("tracking_note", ""),
                "page_issues": "; ".join(signals["issues"]),
                "fetch_error": result.get("error", ""),
                "ok": (
                    result.get("ok")
                    and result.get("status") == 200
                    and signals["has_native_form"]
                    and signals["has_form_fields"]
                    and "spanish_content_on_en_page" not in signals["issues"]
                    and "title_looks_english" not in signals["issues"]
                ),
            }
        )

    for _path, spec in specs:
        market = _market_by_slug(markets_data, spec.city or "")
        city_name = (market or {}).get("city", spec.city or "")
        lang = (spec.language or "en").lower()
        add_row(spec.final_url, lang, spec.city or "", city_name, spec.name)

    base = f"https://{DOMAIN}"
    add_row(f"{base}{EN_THANK_YOU}", "en", "shared", "Shared", "thank-you-en")
    add_row(f"{base}{ES_THANK_YOU}", "es", "shared", "Shared", "thank-you-es")

    for row in rows:
        if row["city"] == "shared":
            row["ok"] = row.get("http_status") == 200 and not row.get("fetch_error")
            row["page_issues"] = ""

    return rows


def build_keyword_conflict_rows(
    specs: list[tuple[Path, CampaignSpec]],
    shared_negatives: list[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path, spec in specs:
        for issue in find_positive_negative_conflicts(spec):
            rows.append(
                {
                    "spec_file": path.name,
                    "campaign": spec.name,
                    "conflict_type": "positive_negative",
                    "detail": issue,
                }
            )
        for ag in spec.ad_groups:
            for kw in ag.keywords:
                lower = kw.text.lower()
                for brand in BRAND_TERMS:
                    if brand in lower:
                        rows.append(
                            {
                                "spec_file": path.name,
                                "campaign": spec.name,
                                "conflict_type": "brand_leak",
                                "detail": f"{ag.name}: {kw.text}",
                            }
                        )
                for pat, label in RISK_POSITIVE_PATTERNS:
                    if pat.search(kw.text):
                        rows.append(
                            {
                                "spec_file": path.name,
                                "campaign": spec.name,
                                "conflict_type": label,
                                "detail": f"{ag.name}: {kw.text}",
                            }
                        )
                for neg in shared_negatives:
                    if neg and neg in lower:
                        rows.append(
                            {
                                "spec_file": path.name,
                                "campaign": spec.name,
                                "conflict_type": "shared_negative_overlap",
                                "detail": f"{ag.name}: '{kw.text}' contains negative theme '{neg}'",
                            }
                        )
    return rows


def conversion_action_valid(
    conversion_id: str, conversions: list[dict[str, Any]]
) -> tuple[bool, str]:
    for action in conversions:
        if str(action.get("conversion_action_id")) == conversion_id:
            status = action.get("status", "")
            if status != "ENABLED":
                return False, f"Conversion {conversion_id} status={status}"
            return True, action.get("name", "")
    return False, f"Conversion action {conversion_id} not found in account"


def render_markdown_report(
    *,
    snapshot: dict[str, Any],
    live_extras: dict[str, Any],
    spec_results: list[SpecAuditResult],
    url_rows: list[dict[str, Any]],
    keyword_rows: list[dict[str, Any]],
    overlap_rows: list[dict[str, Any]],
    generated_at: str,
) -> str:
    account = snapshot.get("account", {})
    conversions = snapshot.get("conversion_actions", [])
    call_assets = snapshot.get("call_assets", [])
    campaigns = snapshot.get("campaigns", [])

    primary_conversions = [
        c
        for c in conversions
        if c.get("primary_for_goal") or c.get("optimization_setting") == "PRIMARY"
    ]

    lines: list[str] = [
        "# ELA Google Ads — Full Account Preflight Audit",
        "",
        f"**Generated:** {generated_at} (UTC)  ",
        f"**Account:** {account.get('account_name')} (`{account.get('customer_id')}`)  ",
        "**Mode:** Read-only — no Google Ads mutations performed",
        "",
        "---",
        "",
        "## 1. Live account findings",
        "",
        (
            f"- **Status:** {account.get('account_status')} | "
            f"**Currency:** {account.get('currency_code')} | "
            f"**TZ:** {account.get('time_zone')}"
        ),
        f"- **Auto-tagging:** {'ON' if account.get('auto_tagging_enabled') else 'OFF'}",
        f"- **Tracking URL template:** `{account.get('tracking_url_template') or '(none)'}`",
        f"- **Account final URL suffix:** `{account.get('final_url_suffix') or '(none)'}`",
        f"- **Campaigns (non-removed):** {len(campaigns)} — all should remain PAUSED pre-launch",
        f"- **Conversion actions:** {len(conversions)} ({len(primary_conversions)} marked primary)",
        f"- **Call assets:** {len(call_assets)}",
        f"- **Live positive keywords (30d):** {live_extras.get('positive_keyword_count', 0)}",
        f"- **Live negative keywords:** {live_extras.get('negative_keyword_count', 0)}",
        f"- **Live RSAs:** {live_extras.get('rsa_count', 0)}",
        f"- **Search terms (90d attempt):** {live_extras.get('search_term_count', 0)} rows",
        "",
        "### Campaign inventory",
        "",
        "| Campaign | Status | Budget | Bidding | Search | Partners | Display |",
        "|---|---:|---:|---|:---:|:---:|:---:|",
    ]

    network_by_id = {
        str(n["campaign_id"]): n for n in live_extras.get("network_settings", [])
    }
    for camp in campaigns:
        net = network_by_id.get(str(camp.get("campaign_id")), {})
        lines.append(
            f"| {camp.get('campaign_name')} | {camp.get('status')} | "
            f"${camp.get('daily_budget', 0):.2f} | {camp.get('bidding_strategy')} | "
            f"{'Y' if net.get('target_google_search', True) else 'N'} | "
            f"{'Y' if net.get('target_search_network') else 'N'} | "
            f"{'Y' if net.get('target_content_network') else 'N'} |"
        )

    lines.extend(
        [
            "",
            "### Bakersfield / city overlap (live)",
            "",
        ]
    )
    city_live = [
        c for c in campaigns
        if any(
            token in (c.get("campaign_name") or "").lower()
            for token in ("bakersfield", "fresno", "kern", "stockton")
        )
    ]
    if city_live:
        for c in city_live:
            lines.append(f"- `{c.get('campaign_name')}` — {c.get('status')}")
    else:
        lines.append("- No obvious city-named live campaigns beyond legacy naming.")

    lines.extend(["", "### Call assets (do not enable until phone routing approved)", ""])
    for asset in call_assets:
        phone = asset.get("phone_number") or asset.get("phone") or "n/a"
        name = asset.get("asset_name") or asset.get("name") or "call asset"
        lines.append(f"- `{name}` — {phone}")

    lines.extend(["", "---", "", "## 2. Spec classification summary", ""])
    by_class: dict[str, list[SpecAuditResult]] = {}
    for result in spec_results:
        by_class.setdefault(result.classification, []).append(result)

    for cls in (CLASS_READY, CLASS_LANDING_QA, CLASS_OVERLAP, CLASS_BLOCKED):
        items = by_class.get(cls, [])
        lines.append(f"### {cls} ({len(items)})")
        lines.append("")
        if not items:
            lines.append("_None_")
        else:
            for item in sorted(items, key=lambda r: (r.city, r.language)):
                lines.append(
                    f"- **{item.campaign_name}** (`{item.spec_file}`) — "
                    f"{len(item.blockers)} blocker(s), {len(item.warnings)} warning(s)"
                )
        lines.append("")

    lines.extend(["---", "", "## 3. Bakersfield launch blockers", ""])
    bf = [r for r in spec_results if r.city == "bakersfield"]
    for r in bf:
        lines.append(f"### {r.campaign_name}")
        if r.blockers:
            for b in r.blockers:
                lines.append(f"- **BLOCKER:** {b}")
        else:
            lines.append("- No structural blockers in spec validation.")
        if r.warnings:
            for w in r.warnings:
                lines.append(f"- Warning: {w}")
        lines.append("")

    lines.extend(["---", "", "## 4. Conversion tracking concerns", ""])
    valid, detail = conversion_action_valid(TARGET_CONVERSION_ID, conversions)
    lines.append(
        f"- Target Form conversion `{TARGET_CONVERSION_ID}`: "
        f"{'VALID' if valid else 'INVALID'} — {detail}"
    )
    lines.append(f"- Primary conversion actions in account: {len(primary_conversions)}")
    for c in primary_conversions[:12]:
        lines.append(
            f"  - `{c.get('conversion_action_id')}` {c.get('name')} "
            f"({c.get('category')}, {c.get('status')})"
        )
    if len(primary_conversions) > 12:
        lines.append(f"  - … and {len(primary_conversions) - 12} more")
    lines.append(
        "- **Recommendation:** Set only Form `7569909838` as primary at launch; "
        "demote call/page-view/legacy primaries."
    )

    lines.extend(["", "---", "", "## 5. Keyword & negative conflicts", ""])
    lines.append(f"- Spec conflict rows exported: **{len(keyword_rows)}**")
    conflict_types: dict[str, int] = {}
    for row in keyword_rows:
        conflict_types[row["conflict_type"]] = conflict_types.get(row["conflict_type"], 0) + 1
    for ctype, count in sorted(conflict_types.items()):
        lines.append(f"  - {ctype}: {count}")

    lines.extend(["", "---", "", "## 6. Vendor / brand overlap risks", ""])
    lines.append(
        "- HawkSEM / external agency may manage brand Search — non-brand specs "
        "include draft brand negatives (DRAFT_DO_NOT_APPLY)."
    )
    lines.append(
        "- Live legacy `LAW--SCH--*` and `LAW2--*` campaigns may compete on "
        "overlapping employment terms."
    )
    lines.append("- Confirm vendor geo/keyword list before enabling any new city campaign.")

    lines.extend(["", "---", "", "## 7. URL & form QA", ""])
    broken = [r for r in url_rows if not r.get("ok")]
    lines.append(f"- URLs tested: {len(url_rows)} | Issues: {len(broken)}")
    for row in broken[:20]:
        lines.append(
            f"  - `{row['url']}` — status {row.get('http_status')} — "
            f"{row.get('page_issues') or row.get('fetch_error')}"
        )

    lines.extend(["", "---", "", "## 8. Safest specs to review first", ""])
    ready = [r for r in spec_results if r.classification == CLASS_READY]
    for r in sorted(ready, key=lambda x: x.city):
        lines.append(f"1. {r.campaign_name}")

    lines.extend(
        [
            "",
            "---",
            "",
            "## 9. Output files",
            "",
            "- `output/spec-audit.csv`",
            "- `output/url-qa.csv`",
            "- `output/keyword-conflicts.csv`",
            "- `output/live-campaign-overlap.csv`",
            "- `docs/full-account-preflight-audit.md`",
            "",
            "---",
            "",
            "_End of read-only preflight audit._",
        ]
    )
    return "\n".join(lines) + "\n"


def run_preflight_audit(
    *,
    settings: GoogleAdsSettings | None = None,
    specs_dir: Path | None = None,
    output_dir: Path | None = None,
    docs_dir: Path | None = None,
    skip_api: bool = False,
    skip_urls: bool = False,
) -> dict[str, Any]:
    settings = settings or load_settings()
    root = Path(__file__).resolve().parents[3]
    specs_dir = specs_dir or (root / "specs")
    output_dir = output_dir or (root / "output")
    docs_dir = docs_dir or (root / "docs")
    ensure_output_dir(output_dir)
    ensure_output_dir(docs_dir)

    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    logger.info("Starting read-only preflight audit")

    snapshot: dict[str, Any] = {}
    live_extras: dict[str, Any] = {}
    if not skip_api:
        snapshot = build_account_snapshot(settings)
        try:
            live_extras["positive_keywords"] = list_positive_keywords(settings)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Positive keyword export failed: %s", exc)
            live_extras["positive_keywords"] = []
        try:
            live_extras["negative_keywords"] = list_negative_keywords(settings)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Negative keyword export failed: %s", exc)
            live_extras["negative_keywords"] = []
        try:
            live_extras["network_settings"] = list_campaign_network_settings(settings)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Network settings export failed: %s", exc)
            live_extras["network_settings"] = []
        try:
            live_extras["rsas"] = list_responsive_search_ads(settings)
        except Exception as exc:  # noqa: BLE001
            logger.warning("RSA export failed: %s", exc)
            live_extras["rsas"] = []
        live_extras["search_terms"] = list_search_terms(settings, days=90)
        if not live_extras["search_terms"]:
            live_extras["search_terms"] = list_search_terms(settings, days=30)
        live_extras["positive_keyword_count"] = len(live_extras.get("positive_keywords", []))
        live_extras["negative_keyword_count"] = len(live_extras.get("negative_keywords", []))
        live_extras["rsa_count"] = len(live_extras.get("rsas", []))
        live_extras["search_term_count"] = len(live_extras.get("search_terms", []))
    else:
        snapshot = {"account": {}, "campaigns": [], "conversion_actions": [], "call_assets": []}

    markets_data = load_markets_matrix(specs_dir)
    shared_negatives = load_shared_negative_texts(specs_dir)
    spec_paths = discover_spec_files(specs_dir)
    loaded: list[tuple[Path, CampaignSpec]] = [
        (path, load_spec_file(path)) for path in spec_paths
    ]

    dup_name_issues = find_duplicate_spec_names(loaded)
    account_template = (snapshot.get("account") or {}).get("tracking_url_template")
    conversions = snapshot.get("conversion_actions", [])
    conv_ok, conv_detail = conversion_action_valid(TARGET_CONVERSION_ID, conversions)

    url_rows: list[dict[str, Any]] = []
    if not skip_urls:
        url_rows = audit_urls_for_specs(loaded, markets_data)
    url_by_final = {r["url"]: r for r in url_rows}

    overlap_rows: list[dict[str, Any]] = []
    spec_results: list[SpecAuditResult] = []
    spec_csv_rows: list[dict[str, Any]] = []

    overlap_groups: dict[str, list[str]] = {}
    for market in markets_data.get("markets", []):
        group = market.get("overlap_group")
        if group:
            overlap_groups.setdefault(group, []).append(market.get("slug", ""))

    for path, spec in loaded:
        market = _market_by_slug(markets_data, spec.city or "")
        validation = validate_campaign_spec(spec)
        blockers: list[str] = [i for i in validation]
        warnings: list[str] = []

        if any(path.name in issue for issue in dup_name_issues):
            blockers.extend([i for i in dup_name_issues if path.name in i])

        city_blockers, city_warnings = check_city_keyword_modifier(spec, market)
        blockers.extend(city_blockers)
        warnings.extend(city_warnings)
        blockers.extend(check_brand_leaks(spec))
        warnings.extend(check_risk_positives(spec))
        warnings.extend(check_spanish_copy(spec))
        tracking_issues = check_tracking_suffix(spec, account_template)
        blockers.extend(tracking_issues)

        lang_issues = check_language_ids(spec)
        blockers.extend(lang_issues)

        if spec.network.target_search_network:
            blockers.append("Search Partners must remain disabled")
        if spec.network.target_content_network:
            blockers.append("Display network must remain disabled")
        if spec.status != "PAUSED":
            blockers.append(f"Campaign status must be PAUSED (got {spec.status})")

        goal_ids = [str(g) for g in (spec.conversion_goals or [])]
        if TARGET_CONVERSION_ID not in goal_ids:
            blockers.append(f"Missing required conversion goal {TARGET_CONVERSION_ID}")
        if not conv_ok:
            blockers.append(f"Account conversion invalid: {conv_detail}")

        has_call_assets = bool(spec.call_asset_schedule)
        if has_call_assets:
            blockers.append("Call assets present in spec — remove until phone routing approved")

        overlaps = find_live_campaign_overlap(spec, snapshot.get("campaigns", []))
        overlap_rows.extend(
            {**row, "spec_file": path.name} for row in overlaps
        )
        if overlaps:
            warnings.append(
                f"{len(overlaps)} live campaign(s) overlap city theme — review before apply"
            )

        landing_status = (market or {}).get("landing_page_status", "unknown")
        url_row = url_by_final.get(spec.final_url, {})
        url_ok = bool(url_row.get("ok"))

        overlap_group_conflict = False
        group = (market or {}).get("overlap_group")
        if group and len(overlap_groups.get(group, [])) > 1:
            do_not = (market or {}).get("do_not_launch_with") or []
            if do_not:
                overlap_group_conflict = True
                warnings.append(
                    f"Overlap group '{group}' — do not launch with: {', '.join(do_not)}"
                )

        classification = classify_spec(
            blockers=blockers,
            market=market,
            url_ok=url_ok,
            landing_status=landing_status,
            overlap_group_conflict=overlap_group_conflict,
        )

        kw_conflicts = find_positive_negative_conflicts(spec)
        result = SpecAuditResult(
            spec_file=path.name,
            campaign_name=spec.name,
            city=spec.city or "",
            language=spec.language or "",
            classification=classification,
            blockers=blockers,
            warnings=warnings,
            keyword_conflict_count=len(kw_conflicts),
            live_overlap_count=len(overlaps),
            url_qa_status="pass" if url_ok else "fail",
            conversion_goal_ok=conv_ok and TARGET_CONVERSION_ID in goal_ids,
            call_assets_in_spec=has_call_assets,
        )
        spec_results.append(result)
        spec_csv_rows.append(
            {
                "spec_file": path.name,
                "campaign_name": spec.name,
                "city": spec.city,
                "language": spec.language,
                "classification": classification,
                "blocker_count": len(blockers),
                "warning_count": len(warnings),
                "blockers": " | ".join(blockers),
                "warnings": " | ".join(warnings),
                "keyword_conflicts": len(kw_conflicts),
                "live_overlaps": len(overlaps),
                "url_qa": result.url_qa_status,
                "landing_page_status": landing_status,
                "conversion_goal_ok": conv_ok,
                "recommended_fix": blockers[0] if blockers else "",
            }
        )

    keyword_rows = build_keyword_conflict_rows(loaded, shared_negatives)

    write_csv(output_dir / "spec-audit.csv", spec_csv_rows)
    write_csv(output_dir / "url-qa.csv", url_rows)
    write_csv(output_dir / "keyword-conflicts.csv", keyword_rows)
    write_csv(output_dir / "live-campaign-overlap.csv", overlap_rows)

    md = render_markdown_report(
        snapshot=snapshot,
        live_extras=live_extras,
        spec_results=spec_results,
        url_rows=url_rows,
        keyword_rows=keyword_rows,
        overlap_rows=overlap_rows,
        generated_at=generated_at,
    )
    report_path = docs_dir / "full-account-preflight-audit.md"
    report_path.write_text(md, encoding="utf-8")
    logger.info("Wrote markdown report: %s", report_path)

    return {
        "spec_count": len(spec_results),
        "classifications": {
            cls: sum(1 for r in spec_results if r.classification == cls)
            for cls in {
                CLASS_READY,
                CLASS_BLOCKED,
                CLASS_LANDING_QA,
                CLASS_OVERLAP,
            }
        },
        "url_issues": sum(1 for r in url_rows if not r.get("ok")),
        "keyword_conflicts": len(keyword_rows),
        "live_overlaps": len(overlap_rows),
        "report_path": str(report_path),
    }
