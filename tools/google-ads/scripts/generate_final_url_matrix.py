#!/usr/bin/env python3
"""Build the 28-campaign/ad-group final URL and tracking QA matrix."""

from __future__ import annotations

import csv
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

from ela_google_ads.builders.tracking import append_suffix, build_final_url_suffix
from ela_google_ads.validators.spec_validators import load_spec_file

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
SPECS_DIR = ROOT / "specs"
OUTPUT_DIR = ROOT / "output"

FORM_IDS = {
    "en": "6dc81a33-35df-4dc4-b20a-ec5e409ed420",
    "es": "d11f9f2c-a1d2-4ae0-84b3-9f602ad03d51",
}
THANK_YOU_PATHS = {"en": "/thank-you", "es": "/gracias"}
EXPECTED_PHONE_TEL = "+14246781416"
QA_QUERY = {
    "gclid": "ela-url-qa",
    "utm_source": "google",
    "utm_medium": "cpc",
    "utm_campaign": "ela-url-qa",
    "google_campaign": "ela-url-qa",
    "google_ad_group": "ela-url-qa",
    "google_keyword": "ela-url-qa",
}


@dataclass(frozen=True)
class RouteResult:
    http_status: int | str
    effective_url: str
    query_retained: bool
    phone_link_present: bool
    error: str = ""


@dataclass(frozen=True)
class MatrixRow:
    campaign: str
    ad_group: str
    language: str
    geo: str
    final_url: str
    http_status: int | str
    form_id: str
    thank_you_url: str
    tracking_test_status: str
    vendor_overlap_status: str


def _spec_paths() -> list[Path]:
    return sorted(
        path
        for path in SPECS_DIR.glob("*-*.yaml")
        if path.name != "markets.yaml" and path.parent == SPECS_DIR
    )


def _qa_url(final_url: str) -> str:
    separator = "&" if "?" in final_url else "?"
    return f"{final_url}{separator}{urlencode(QA_QUERY)}"


def _check_route(final_url: str) -> RouteResult:
    requested_url = _qa_url(final_url)
    request = Request(requested_url, headers={"User-Agent": "ELA-Google-Ads-URL-QA/1.0"})
    try:
        with urlopen(request, timeout=30) as response:  # noqa: S310 - fixed HTTPS spec URLs
            body = response.read().decode("utf-8", errors="replace")
            effective_url = response.geturl()
            query = parse_qs(urlparse(effective_url).query)
            query_retained = all(query.get(key) == [value] for key, value in QA_QUERY.items())
            return RouteResult(
                http_status=response.status,
                effective_url=effective_url,
                query_retained=query_retained,
                phone_link_present=EXPECTED_PHONE_TEL in body,
            )
    except HTTPError as exc:
        return RouteResult(exc.code, requested_url, False, False, str(exc))
    except (TimeoutError, URLError) as exc:
        return RouteResult("ERROR", requested_url, False, False, str(exc))


def _source_tracking_checks() -> tuple[bool, list[str]]:
    required = {
        REPO_ROOT / "src" / "lib" / "hubspot.ts": [
            FORM_IDS["en"],
            FORM_IDS["es"],
            'lang === "es" ? "/gracias" : "/thank-you"',
        ],
        REPO_ROOT / "src" / "lib" / "tracking.ts": [
            '"hubspot_form_submission"',
            '"phone_click"',
            '"call_click"',
            "hubspot_submission_id",
        ],
        REPO_ROOT / "src" / "components" / "HubSpotForm.tsx": [
            "pushHubSpotFormSubmission",
            "getThankYouPath",
        ],
    }
    missing: list[str] = []
    for path, needles in required.items():
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                missing.append(f"{path.relative_to(REPO_ROOT)}::{needle}")
    return not missing, missing


def _vendor_overlap(city: str) -> str:
    if city == "bakersfield":
        return "HOLD_ACTIVE_VENDOR_OVERLAP"
    if city == "fresno":
        return "HISTORICAL_VENDOR_INACTIVE"
    if city in {"riverside", "san-bernardino", "fontana", "ontario"}:
        return "HISTORICAL_INLAND_EMPIRE_VENDOR_INACTIVE"
    return "NO_VENDOR_CAMPAIGN_IN_REFERENCE"


def build_matrix() -> tuple[list[MatrixRow], dict[str, object]]:
    specs = [load_spec_file(path) for path in _spec_paths()]
    route_urls = sorted({str(spec.final_url) for spec in specs})
    route_results: dict[str, RouteResult] = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(_check_route, url): url for url in route_urls}
        for future in as_completed(futures):
            route_results[futures[future]] = future.result()

    source_ok, source_missing = _source_tracking_checks()
    rows: list[MatrixRow] = []
    for spec in specs:
        lang = spec.language.lower()
        route = route_results[str(spec.final_url)]
        route_pass = (
            route.http_status == 200
            and route.query_retained
            and route.phone_link_present
            and source_ok
        )
        tracking_status = (
            "PASS_HTTP_QUERY_PHONE_AND_SOURCE_EVENTS; LIVE_FORM_SUBMIT_NOT_SENT"
            if route_pass
            else "FAIL_PRECREATE_QA"
        )
        for ad_group in spec.ad_groups:
            final_url = str(ad_group.final_url or spec.final_url)
            rows.append(
                MatrixRow(
                    campaign=spec.name,
                    ad_group=ad_group.name,
                    language=lang.upper(),
                    geo="; ".join(spec.geo_target_names),
                    final_url=append_suffix(
                        final_url,
                        build_final_url_suffix(
                            campaign_name=spec.name,
                            ad_group_name=ad_group.name,
                            custom_suffix=spec.tracking.final_url_suffix,
                        ),
                    ),
                    http_status=route.http_status,
                    form_id=FORM_IDS[lang],
                    thank_you_url=(
                        f"https://help.employmentlawassist.com{THANK_YOU_PATHS[lang]}"
                    ),
                    tracking_test_status=tracking_status,
                    vendor_overlap_status=_vendor_overlap(spec.city),
                )
            )

    summary: dict[str, object] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "campaigns": len(specs),
        "matrix_rows": len(rows),
        "routes_checked": len(route_results),
        "routes_http_200": sum(r.http_status == 200 for r in route_results.values()),
        "routes_query_retained": sum(r.query_retained for r in route_results.values()),
        "routes_phone_link_present": sum(r.phone_link_present for r in route_results.values()),
        "source_tracking_checks_passed": source_ok,
        "source_tracking_missing": source_missing,
        "live_form_submission_sent": False,
        "note": (
            "No test lead was submitted. Form IDs, thank-you routing, phone-click events, "
            "form-success event, and submission-ID dedup were verified in built source."
        ),
        "routes": {url: asdict(result) for url, result in sorted(route_results.items())},
    }
    return rows, summary


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows, summary = build_matrix()
    fieldnames = list(MatrixRow.__dataclass_fields__)
    csv_path = OUTPUT_DIR / "final_url_tracking_matrix.csv"
    json_path = OUTPUT_DIR / "final_url_tracking_matrix.json"

    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
    json_path.write_text(
        json.dumps({"summary": summary, "rows": [asdict(row) for row in rows]}, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2))
    print(f"Wrote {len(rows)} rows -> {csv_path}")
    print(f"Wrote JSON -> {json_path}")
    return 0 if all(row.tracking_test_status.startswith("PASS_") for row in rows) else 2


if __name__ == "__main__":
    sys.exit(main())
