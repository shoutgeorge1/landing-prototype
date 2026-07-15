# ELA Google Ads Toolkit

Production-safe Google Ads API automation for **Employment Law Assist APC**.

Guarded **PAUSED** campaign create is available. Default is dry-run (`validate_only`);
live create requires explicit `--execute --confirm-customer-id 6769947952`.

Target customer ID: `6769947952` (676-994-7952)

Toolkit root: `tools/google-ads/` (separate from the Next.js landing site)

---

## 1. Python installation check (Windows / PowerShell)

```powershell
py -3 --version
# Expect Python 3.11+ (3.12 recommended)
```

If `py` is missing:

```powershell
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
# Restart the terminal, then re-check:
py -3 --version
```

### macOS / Linux

```bash
python3 --version
```

---

## 2. Virtual environment

From the repo root:

```powershell
cd tools\google-ads
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
cd tools/google-ads
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

---

## 4. Google Cloud project

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project (e.g. `ela-google-ads`)
3. Note the project for API enablement

---

## 5. Enable the Google Ads API

1. APIs & Services → Library
2. Search **Google Ads API**
3. Enable it for the project

---

## 6. OAuth consent setup

1. APIs & Services → OAuth consent screen
2. Choose **External** (unless you use a Google Workspace internal app)
3. App name / support email: your values
4. Add scope: `https://www.googleapis.com/auth/adwords`
5. If the app is in **Testing**, add your Google account as a **Test user**

---

## 7. Desktop OAuth client

1. APIs & Services → Credentials → Create credentials → OAuth client ID
2. Application type: **Desktop app**
3. Download the JSON

---

## 8. Place the OAuth JSON

```powershell
# From tools\google-ads
New-Item -ItemType Directory -Force -Path credentials | Out-Null
# Copy your downloaded file to:
#   tools\google-ads\credentials\client_secret.json
```

Never commit this file (gitignored).

---

## 9. Generate a refresh token

```powershell
python scripts\generate_refresh_token.py
# or
python scripts\generate_refresh_token.py --client-secrets credentials\client_secret.json
```

The script opens a browser, requests the Ads scope with offline access, and prints the refresh token.

- Copy the token into `.env` as `GOOGLE_ADS_REFRESH_TOKEN`
- The script does **not** write the token to disk
- If Google returns no refresh token: revoke app access at https://myaccount.google.com/permissions and re-run (consent is forced)

### macOS / Linux

```bash
python scripts/generate_refresh_token.py
```

---

## 10. Developer token

1. Sign in to your **Google Ads MCC (manager)** account
2. Tools & Settings → API Center
3. Apply for / copy the **developer token**
4. Put it in `.env` as `GOOGLE_ADS_DEVELOPER_TOKEN`

Basic access is enough for exploration; Standard may be required later for higher write volume.

---

## 11. MCC login customer ID

When authenticating through a manager account, set:

```env
GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890
```

Digits only — **no dashes**.

This repo ships with placeholder `REPLACE_WITH_MCC_ID` until you provide the real MCC ID. Do not guess it.

If your OAuth user has **direct** access to customer `6769947952`, some read calls may work without MCC; manager-context calls still need the login customer ID.

---

## 12. `.env` setup

```powershell
Copy-Item .env.example .env
# Edit .env in your editor — never commit it
```

Required fields:

| Variable | Purpose |
|----------|---------|
| `GOOGLE_ADS_DEVELOPER_TOKEN` | API developer token |
| `GOOGLE_ADS_CLIENT_ID` | OAuth Desktop client ID |
| `GOOGLE_ADS_CLIENT_SECRET` | OAuth Desktop client secret |
| `GOOGLE_ADS_REFRESH_TOKEN` | From generate_refresh_token.py |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | MCC ID (digits) — replace placeholder |
| `GOOGLE_ADS_CUSTOMER_ID` | `6769947952` |
| `GOOGLE_ADS_USE_PROTO_PLUS` | `true` |

Optional:

```env
ELA_CALL_TRACKING_PHONE=4246781416
```

Phone is under evaluation — do not activate call assets until routing/intake coverage is confirmed.

---

## 13. Read-only account test

```powershell
python scripts\test_account_access.py
# or
python -m ela_google_ads.cli account test
```

Expect account name, status, currency, time zone, auto-tagging, test-account flag.

Also list accounts the OAuth user can access:

```powershell
python scripts\list_accessible_customers.py
```

---

## 14. Audit commands

```powershell
python scripts\account_snapshot.py
python -m ela_google_ads.cli account audit
```

Exports land in `tools/google-ads/output/` (gitignored).

---

## 15. Export commands

```powershell
python scripts\export_campaigns.py
python scripts\export_conversion_actions.py
python scripts\export_assets.py
python scripts\export_search_terms.py --days 30

# CLI equivalents
python -m ela_google_ads.cli campaigns export
python -m ela_google_ads.cli conversions export
python -m ela_google_ads.cli assets export
python -m ela_google_ads.cli reports search-terms --days 30
```

CSV + JSON pairs are written under `output/`.

---

## 16. Campaign-spec validation (offline — no API)

```powershell
python -m ela_google_ads.cli specs validate specs\bakersfield-en.yaml
python -m ela_google_ads.cli specs validate specs\bakersfield-es.yaml
python -m ela_google_ads.cli campaigns validate specs\bakersfield-en.yaml
```

Specs live in `specs/`. Shared negatives / brand / conversion map worksheets are under `specs/shared/`.

---

## 17. Dry-run preview

```powershell
python -m ela_google_ads.cli campaigns preview specs\bakersfield-en.yaml
```

Preview includes structure, tracking URL suffix preview, validation issues, and keyword conflicts. **No resources are created.**

---

## 18. Production mutation safeguards

| Guard | Behavior |
|-------|----------|
| Default mode | Dry-run `validate_only` (no resources created) |
| `--execute` | Required for live mutation |
| `--confirm-customer-id` | Must be `6769947952` (hard allowlist) |
| New campaigns | Must be `PAUSED`; `ENABLED` refused |
| Naming | Only `ELA \| Search \| {City} \| {EN\|ES} \| Nonbrand` |
| Existing campaigns | Exact-name skip; never update/delete/rename |
| Budgets | Created ENABLED (API has no PAUSED); deterministic names |
| Bakersfield | Create PAUSED OK; bulk-enable blocked without vendor-shutdown ack |
| Deletes | Disabled |

Example:

```powershell
# Dry-run (validate_only mutate)
python -m ela_google_ads.cli campaigns create specs\fresno-en.yaml

# Live create (PAUSED) — parent/operator runs after review
python -m ela_google_ads.cli campaigns create specs\fresno-en.yaml --execute --confirm-customer-id 6769947952
```

---

## 19. Troubleshooting authentication

| Symptom | Likely fix |
|---------|------------|
| Missing credentials error | Fill `.env`; run refresh-token script |
| `AUTHENTICATION_ERROR` | Regenerate refresh token; check client ID/secret |
| `CUSTOMER_NOT_FOUND` / permission denied | Add user access; set correct MCC `LOGIN_CUSTOMER_ID` |
| `DEVELOPER_TOKEN_NOT_APPROVED` | Check API Center token status |
| No refresh token returned | Revoke app access; re-run with consent; use Desktop client |
| OAuth blocked (Testing) | Add your Google account as a test user |
| Dashed customer IDs | Use digits only in API env vars (`6769947952`) |

---

## Geo target lookup

Do not guess geo IDs. After credentials work:

```powershell
python -m ela_google_ads.cli geo search "Bakersfield"
```

Paste verified IDs into `geo_target_ids` in the YAML specs. Presence-based targeting is required (`location_presence_only: true`).

---

## Tests (no live credentials required)

```powershell
pytest -q
ruff check src tests scripts
```

---

## Package layout

```text
tools/google-ads/
  src/ela_google_ads/   # library + CLI
  scripts/              # standalone read-only scripts
  specs/                # campaign + shared YAML specs
  docs/                 # offline conversion architecture (placeholder)
  output/               # local exports (gitignored)
  credentials/          # OAuth JSON (gitignored)
  tests/
```

---

## Live API boundary

Everything above **campaign create apply** can be built and tested offline.

**Live credentials become required at:**

```text
python scripts/test_account_access.py
```

Until `.env` is complete (developer token, OAuth, refresh token, and usually MCC login customer ID), that command will fail with a clear credentials error — by design.
