# ELA Google Ads — Conversion & phone QA checklist
# Locked with Steps 5–6 — do not enable campaigns until both sections pass.

Account: **6769947952**  
Policy: `specs/shared/conversion-goals-locked.yaml`, `specs/shared/tracking-locked.yaml`

**Phone:** **(424) 678-1416** (`+14246781416`) — HubSpot, same on LP + call assets  
**Qualified call duration:** **90 seconds**  
**Form dedup:** `hubspot_submission_id` / `event_id` — not session-level

---

## Form QA (EN + ES)

Test on at least one EN and one ES city landing page with `?gclid=test123` and full UTM/suffix params.

- [ ] Submit test lead with unique email
- [ ] HubSpot API POST returns success (network tab → 200)
- [ ] Contact appears in HubSpot with correct properties
- [ ] `gclid` recorded on contact
- [ ] UTMs recorded (`utm_source`, `utm_medium`, `utm_campaign`, `utm_term`)
- [ ] `google_campaign`, `google_ad_group`, `google_keyword` recorded
- [ ] `city` and `language` recorded
- [ ] `hubspot_submission_id` present in dataLayer `hubspot_form_submission` event
- [ ] **One** `ELA | Lead | HubSpot Form Submit` conversion per unique submission ID
- [ ] Second legitimate submit in same session **does** fire a second conversion (different submission ID)
- [ ] Thank-you page refresh does **not** fire another Primary form conversion
- [ ] Simulated API failure does **not** fire Primary form conversion

## Phone QA

HubSpot number **(424) 678-1416** must match on landing page **and** Google Ads call assets. **No CallRail.**

- [ ] Landing page displays **(424) 678-1416** (EN + ES pages)
- [ ] Google Ads call assets updated from legacy **(424) 234-5229** / **(424) 371-7069** to **(424) 678-1416**
- [ ] Qualified-call duration set to **90 seconds** on call conversion actions
- [ ] Test call from ad call asset → reaches HubSpot phone system
- [ ] Test mobile `tel:` click from landing page → reaches HubSpot
- [ ] Test desktop phone display / click
- [ ] Call duration recorded in Google Ads
- [ ] Attribution recorded for calls from ads
- [ ] `ELA | Call | Phone Click` fires on tel: click but stays **Secondary**
- [ ] Promote `ELA | Call | Calls From Ads` to Primary only after above passes
- [ ] Promote `ELA | Call | Website Qualified Call` to Primary only after website-call QA passes

## Campaign goal setup

Create **ELA | Goals | Nonbrand Search** containing:

**At launch (Primary):**
- `ELA | Lead | HubSpot Form Submit`

**After phone QA (add Primary):**
- `ELA | Call | Calls From Ads`
- `ELA | Call | Website Qualified Call`

**Never include:**
- Phone Click
- Thank You Page
- Legacy workplaceattorneys.net / vendor actions

Attach goal to all `ELA | Search | * | Nonbrand` campaigns.

## Legacy cleanup

- [ ] Rename `Form` → `ELA | Lead | HubSpot Form Submit`
- [ ] Rename/demote `THANK_YOU_PAGE_VIEW` → `ELA | Lead | Thank You Page` (Secondary)
- [ ] Create `ELA | Call | Phone Click` (Secondary)
- [ ] Demote all legacy primaries except approved ELA actions
- [ ] Disable workplaceattorneys.net conversion actions
