# ELA Google Ads Launch QA Checklist

Use this before enabling any campaign. All commands run from `tools/google-ads/` with the venv Python:

```powershell
.\.venv\Scripts\python.exe <command>
```

## 1. Credentials and access (read-only)

```powershell
.\.venv\Scripts\python.exe scripts\test_account_access.py
.\.venv\Scripts\python.exe scripts\list_accessible_customers.py
```

Confirm:

- [ ] Target customer `6769947952` is accessible
- [ ] MCC login `9671361752` is set in `.env`
- [ ] Auto-tagging is enabled (should be `true`)

## 2. Account audit (read-only)

```powershell
.\.venv\Scripts\python.exe scripts\account_snapshot.py
.\.venv\Scripts\python.exe scripts\export_campaigns.py
.\.venv\Scripts\python.exe scripts\export_conversion_actions.py
.\.venv\Scripts\python.exe scripts\export_assets.py
.\.venv\Scripts\python.exe scripts\export_search_terms.py --days 30
```

Review exports in `output/`:

- [ ] No accidental duplicate live campaigns for same city/language
- [ ] Conversion primaries are sane (see `specs/shared/conversion-map.yaml`)
- [ ] Call assets use approved phone number
- [ ] No vendor overlap on brand keywords (manual check until vendor list received)

## 3. Spec validation (offline)

```powershell
.\.venv\Scripts\python.exe -m ela_google_ads.cli specs validate specs\bakersfield-en.yaml
.\.venv\Scripts\python.exe -m ela_google_ads.cli specs validate specs\bakersfield-es.yaml
```

Confirm:

- [ ] Status is `PAUSED`
- [ ] Channel is `SEARCH` only
- [ ] Search Partners off
- [ ] Display off
- [ ] `geo_target_ids` populated
- [ ] `location_presence_only: true`
- [ ] Language IDs correct (EN `1000`, ES `1003`)
- [ ] No placeholder ad copy
- [ ] No broad match keywords

## 4. Dry-run preview (offline)

```powershell
.\.venv\Scripts\python.exe -m ela_google_ads.cli campaigns preview specs\bakersfield-en.yaml
.\.venv\Scripts\python.exe -m ela_google_ads.cli campaigns preview specs\bakersfield-es.yaml
```

Review `output/preview_*.json`:

- [ ] Tracking preview URLs look correct
- [ ] `validation_issues` is empty
- [ ] `keyword_conflicts` is empty or reviewed

## 5. Geo verification

```powershell
.\.venv\Scripts\python.exe -m ela_google_ads.cli geo search "Kern County"
```

Confirm geo IDs in spec match `specs/shared/geo/bakersfield-service-area.yaml`.

## 6. Landing page QA (manual)

- [ ] `https://help.employmentlawassist.com/bakersfield/en` loads
- [ ] `https://help.employmentlawassist.com/bakersfield/es` loads
- [ ] HubSpot form submits in EN and ES
- [ ] Phone number on page matches approved intake number
- [ ] Someone answers phone during business hours
- [ ] GCLID + UTMs appear on test form submission in HubSpot

## 7. GTM / GA4 / HubSpot (manual)

- [ ] GTM publishes on `help.employmentlawassist.com`
- [ ] GA4 receives page_view and form events
- [ ] HubSpot hidden fields populate: `google_campaign`, `google_ad_group`, `google_keyword`
- [ ] Qualified-lead lifecycle stage defined for later offline upload

## 8. Conversion settings (manual in Google Ads UI)

See `specs/shared/conversion-goals-locked.yaml` and `docs/conversion-qa-checklist.md`:

- [ ] Rename/create ELA conversion actions per locked naming
- [ ] **ELA | Lead | HubSpot Form Submit** is sole Primary at launch
- [ ] **ELA | Lead | Thank You Page** and **ELA | Call | Phone Click** are Secondary only
- [ ] Campaign goal **ELA | Goals | Nonbrand Search** created and attached
- [ ] Legacy workplaceattorneys.net actions disabled
- [ ] Call primaries held until HubSpot phone QA passes
- [ ] **Do not enable campaigns** until form + phone QA both pass

## 9. Billing and ownership

- [ ] Account billing active
- [ ] Company retains admin access
- [ ] Daily budget approved for sniper test

## 10. Apply safeguards (when mutation phase is enabled)

```powershell
# Preview only — default
.\.venv\Scripts\python.exe -m ela_google_ads.cli campaigns create specs\bakersfield-en.yaml

# Live create requires explicit flags
.\.venv\Scripts\python.exe -m ela_google_ads.cli campaigns create specs\bakersfield-en.yaml --execute --confirm-customer-id 6769947952
```

Before `--execute`:

- [ ] Spec validated and previewed
- [ ] Customer ID confirmed
- [ ] Campaign created as `PAUSED`
- [ ] Old overlapping Bakersfield campaigns remain paused

## 11. Post-launch monitoring (first 7 days)

```powershell
.\.venv\Scripts\python.exe scripts\export_search_terms.py --days 7
.\.venv\Scripts\python.exe scripts\export_campaigns.py
```

- [ ] Search terms show no job-seeker / free-advice waste
- [ ] No brand overlap with external vendor
- [ ] Form leads in HubSpot match campaign/ad group fields
- [ ] Spend within test budget
