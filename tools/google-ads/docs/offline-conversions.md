# Offline conversion upload architecture (placeholder — not implemented)

## Status

**Not implemented in Phase 1.** Do not upload offline conversions until:

1. Existing Google Ads conversion actions are audited
2. HubSpot lifecycle stages are mapped
3. GCLID / GBRAID / WBRAID capture is verified end-to-end
4. Legal / privacy review is complete

## Intended future sources

| Signal | Likely system | Notes |
|--------|---------------|-------|
| Lead form submitted | HubSpot + GTM/GA4 | Website primary candidate |
| Qualified phone call | Google Ads call reporting and/or HubSpot | Confirm intake coverage first |
| Qualified lead | HubSpot lifecycle | Offline / enhanced |
| Consultation scheduled | HubSpot / calendar | Mid-funnel |
| Retained client | HubSpot deal / custom stage | Strongest value signal |

## Identifiers

Prefer in this order when available:

1. `gclid`
2. `gbraid` / `wbraid` (iOS / privacy contexts)
3. First-party email / phone only under an approved enhanced-conversions design

Landing pages already capture `gclid`, `gbraid`, `wbraid`, UTMs, and
`google_campaign` / `google_ad_group` / `google_keyword` for HubSpot.

## Future API options

- Google Ads API offline conversion uploads (ClickConversion)
- Google Ads Data Manager API workflows where appropriate
- Enhanced conversions for leads if first-party consent model is approved

## Guardrails

- Keep page views / button clicks **secondary**
- Do not optimize bidding to weak micro-events
- Do not create new primary conversion actions until the conversion-map worksheet is filled from a live export (`specs/shared/conversion-map.yaml`)
