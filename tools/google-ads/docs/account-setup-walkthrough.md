# ELA Google Ads — Account Setup Walkthrough

Account: **EMPLOYMENT LAW ASSIST APC** (`6769947952`)  
Toolkit: `tools/google-ads/`

---

## Setup order

| Step | Topic | Status |
|---:|---|---|
| 1 | Negative keywords | **LOCKED** |
| 2 | Account structure & naming | **LOCKED** |
| 3 | Geo targeting & location options | **LOCKED** |
| 4 | Campaign settings | **LOCKED** |
| 5 | Conversion actions & goals | **LOCKED** |
| **6** | Tracking (GTM, HubSpot, phone) | **LOCKED** |
| **7** | Campaign build / upload (PAUSED) | **API BLOCKED — Editor fallback generated** |
| 8 | Ad assets (sitelinks, callouts, snippets, calls) | Pending |
| 9 | Landing page QA | Pending |
| 10 | Launch checklist & monitoring | Pending |

---

## Step 5 — Conversion actions & goals ✅ LOCKED

Policy: `specs/shared/conversion-goals-locked.yaml`  
Map: `specs/shared/conversion-map.yaml`  
QA: `docs/conversion-qa-checklist.md`

### Confirmed tracking stack

| Layer | Setup |
|---|---|
| CRM | **HubSpot** |
| Forms | **API POST** directly into HubSpot (not iframe) |
| Phone | **HubSpot phone number** — same on LP + Google Ads call assets |
| CallRail | **Do not use** |

### Conversion actions

| Name | Role | When Primary |
|---|---|---|
| **ELA \| Lead \| HubSpot Form Submit** | Lead | **At launch** — fires only after successful HubSpot API POST |
| **ELA \| Call \| Calls From Ads** | Call | After phone QA |
| **ELA \| Call \| Website Qualified Call** | Call | After website-call QA |
| **ELA \| Call \| Phone Click** | Diagnostic | **Never** — Secondary only |
| **ELA \| Lead \| Thank You Page** | Diagnostic | **Never** — Secondary only (`/thank-you`, `/gracias`) |

**Form conversion rules:**
- Category: Submit lead form · Count: One · Attribution: Data-driven
- GTM listens to `hubspot_form_submission` (site fires this **only** after API `response.ok`)
- Browser event alone is **not** enough
- Dedup by `hubspot_submission_id` / `event_id` per successful API POST — **not** session-level
- Thank-you refresh must not create another Primary form conversion

**Call conversion rules:**
- HubSpot number **(424) 678-1416** on call assets and landing pages
- **90 seconds** qualified-call duration threshold in Google Ads
- Phone Click (`tel:`) is diagnostic — not a completed call

### Campaign goal: `ELA | Goals | Nonbrand Search`

| Phase | Primary actions in goal |
|---|---|
| Launch | HubSpot Form Submit only |
| After phone QA | + Calls From Ads |
| After website-call QA | + Website Qualified Call |

**Excluded from goal:** Phone Click, Thank You Page, legacy workplaceattorneys.net, old vendor actions.

### Launch gate

**Do not enable campaigns until form QA and phone QA both pass** (see `docs/conversion-qa-checklist.md`).

### Site ↔ GTM alignment (already in code)

```106:110:src/components/HubSpotForm.tsx
    pushHubSpotFormSubmission(
      formId,
      getFormLanguageLabel(lang),
      result.submissionId!,
    );
```

`pushHubSpotFormSubmission` runs only after `submitLead()` returns `ok: true` and includes a unique `hubspot_submission_id` for GTM dedup.

Phone clicks fire `phone_click` + `call_click` via `trackPhoneClick()` for GTM Secondary tagging.

---

## Step 6 — Tracking (GTM, HubSpot fields, phone) ✅ LOCKED

Policy: `specs/shared/tracking-locked.yaml`  
Also: `specs/shared/conversion-goals-locked.yaml`, `specs/shared/conversion-map.yaml`

### Locked decisions

| # | Decision |
|---|---|
| **Z** | HubSpot phone **(424) 678-1416** (`+14246781416`) — verify routing before launch |
| **AA** | **90 seconds** qualified-call duration for call conversions |
| **AB** | **No session dedup** — deduplicate by unique `hubspot_submission_id` / `event_id` per successful API POST |

### Account-level (already live)

- Auto-tagging: **ON**
- Tracking template appends UTMs + `hsa_*` params
- Campaign specs add `google_campaign`, `google_ad_group`, `google_keyword` via final URL suffix

### HubSpot hidden fields (from landing page URL)

`gclid`, UTMs, `google_campaign`, `google_ad_group`, `google_keyword`, `city`, `language`

### GTM tags needed

| Tag | Trigger | Conversion action | Dedup |
|---|---|---|---|
| Ads form conversion | `hubspot_form_submission` | ELA \| Lead \| HubSpot Form Submit | `hubspot_submission_id` |
| Ads phone click | `phone_click` | ELA \| Call \| Phone Click (Secondary) | — |
| Ads thank-you | Pageview `/thank-you` or `/gracias` | ELA \| Lead \| Thank You Page (Secondary) | — |

### Pre-launch phone QA

- Replace legacy call assets **(424) 234-5229** and **(424) 371-7069** with **(424) 678-1416**
- Confirm calls from LP and ad call assets reach HubSpot phone system
- Set **90s** qualified duration on `ELA | Call | Calls From Ads` and `ELA | Call | Website Qualified Call`

---

## Step 7 — Campaign build / upload (PAUSED) ✅ LOCKED

All 28 campaign specs must be created as **PAUSED**. Nothing may be enabled or spend.

### Direct API attempt result

The complete Fresno EN plan passed Google Ads `validate_only`, along with four
other plans in the all-market validation batch. Google then stopped the batch
before execution:

- HTTP/gRPC status: `RESOURCE_EXHAUSTED` (`429`)
- Message: `Too many requests. Retry in 26481 seconds.`
- Quota: `Number of operations for explorer access`
- Request ID: `iULWrXJhORBEGMTScmqKYQ`
- Resources created: **0**

The account still contains the same 15 PAUSED legacy campaigns and no new ELA
campaign names. Per the approved fallback rule, complete Editor files are in
`output/editor-import/`.

Vendor-overlap reference: `405 Ads - ELA Campaigns Report 2026 .xlsx` (read-only;
last updated July 15, 2026 at 8:30 AM). It is evidence only—not a source of campaign
structure or final URLs. The four reported active vendor campaigns are all Bakersfield.

### What to upload

| Item | Source | Count |
|---|---|---|
| Campaigns | `specs/*-en.yaml`, `specs/*-es.yaml` | 28 (14 markets × EN/ES) |
| Negative keyword lists | `output/negative_keywords_upload_en.csv`, `_es.csv` | 2 lists |
| Campaign goal | `ELA \| Goals \| Nonbrand Search` | 1 (from Step 5) |

### Guarded creation path

The creation command defaults to dry-run and requires an explicit `--execute` plus
customer confirmation for account `6769947952`. It rejects any non-PAUSED spec,
validates through the API before applying, skips exact-name duplicates, and never
updates or deletes an existing campaign.

```powershell
cd tools/google-ads
.\.venv\Scripts\python.exe -m ela_google_ads.cli campaigns create specs\fresno-en.yaml
.\.venv\Scripts\python.exe -m ela_google_ads.cli campaigns create specs\fresno-en.yaml `
  --execute --confirm-customer-id 6769947952
```

### Per-campaign contents (each spec)

- 8 ad groups, phrase + exact keywords only
- Maximize Clicks, $25 max CPC ceiling
- $50/day EN, $40/day ES budgets
- Presence-only geo per `specs/shared/geo-targeting-locked.yaml`
- Final URL suffix: `google_campaign`, `google_ad_group`, `google_keyword`
- Campaign, ad group, keyword, RSA, and asset-link status: **PAUSED**
- Campaign budgets have no PAUSED state in Google Ads; they cannot spend while their
  campaigns remain PAUSED

### Non-negotiable safety gates

- Existing vendor and legacy resources are read-only.
- No create command accepts `ENABLED`.
- Bakersfield may be created PAUSED but is on an explicit activation hold.
- No future bulk-enable command may enable Bakersfield.
- Only Athena may release the Bakersfield hold after confirming vendor shutdown.
- New final URLs use `help.employmentlawassist.com`; vendor
  `la.employmentlawassist.com` URLs are forbidden.
