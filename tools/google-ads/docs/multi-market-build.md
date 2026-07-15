# ELA Multi-Market Search Build

All specs are offline drafts and create campaigns as **PAUSED**. No live Google Ads
resources have been created.

## Structure

Each market has separate English and Spanish non-brand Search specs:

- 1 campaign per city/language
- 6 practice-area ad groups:
  - Employment Lawyer / Abogado Laboral
  - Wrongful Termination / Despido Injustificado
  - Workplace Discrimination / Discriminación Laboral
  - Workplace Retaliation / Represalias Laborales
  - Workplace Harassment / Acoso Laboral
  - Wage and Hour / Salarios y Horas
- Exact and phrase match only
- Search Partners off
- Display Network off
- Manual CPC for the initial controlled test
- Presence-only location targeting
- Form conversion action `7569909838` as launch goal
- Account-level tracking template retained; specs add HubSpot attribution fields only

## Market matrix

| Priority | Market | Geo strategy | Google geo IDs | Landing status |
|---:|---|---|---|---|
| 1 | Bakersfield | Kern County | `9057133` | Active |
| 2 | Fresno | Fresno County | `9057128` | Generated; QA required |
| 3 | Stockton | San Joaquin County | `9057156` | Generated; QA required |
| 4 | Modesto | Stanislaus County | `9057167` | Generated; QA required |
| 5 | Visalia | Tulare County | `9057171` | Generated; QA required |
| 6 | Lancaster | Lancaster + Palmdale | `1013931`, `1014108` | Generated; QA required |
| 7 | Palmdale | Palmdale + Lancaster | `1014108`, `1013931` | Alternate; do not launch with Lancaster |
| 8 | Victorville | Victorville/Hesperia/Apple Valley/Adelanto | `1014370`, `1013857`, `1013549`, `1013525` | Generated; QA required |
| 9 | Riverside | Riverside County | `9057150` | Generated; QA required |
| 10 | San Bernardino | San Bernardino County | `9057153` | Generated; QA required |
| 11 | Fontana | San Bernardino County | `9057153` | Alternate; do not launch with San Bernardino/Ontario |
| 12 | Ontario | San Bernardino County | `9057153` | Alternate; do not launch with San Bernardino/Fontana |
| 13 | Salinas | Monterey County | `9057145` | Generated; QA required |
| 14 | Oxnard | Ventura County | `9057173` | Generated; QA required |

## Internal overlap rules

Do not enable multiple campaigns that target the same geo and language:

- Lancaster and Palmdale are alternatives in the Antelope Valley.
- San Bernardino, Fontana, and Ontario are alternatives for San Bernardino County.
- Victorville is a High Desert city cluster and should not run concurrently with a
  county-wide San Bernardino campaign unless geos are made mutually exclusive.
- Existing legacy Fresno, Bakersfield, Riverside/San Bernardino campaigns must remain
  paused when replacement campaigns launch.

## Landing-page reality

The Next.js application statically generates EN/ES routes for all 14 configured cities.
However, the internal launch registry currently marks only Bakersfield EN/ES as active
with live forms and configured tracking. Every other route requires manual QA before its
campaign can move beyond PAUSED.

## Review workflow

Regenerate specs:

```powershell
.\.venv\Scripts\python.exe scripts\generate_market_specs.py
```

Validate all specs:

```powershell
Get-ChildItem specs -Filter "*-??.yaml" | ForEach-Object {
  .\.venv\Scripts\python.exe -m ela_google_ads.cli specs validate $_.FullName
}
```

Preview one market:

```powershell
.\.venv\Scripts\python.exe -m ela_google_ads.cli campaigns preview specs\fresno-en.yaml
```

Use `docs/launch-qa-checklist.md` before any live create or enable action.
