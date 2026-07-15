# ELA Landing Pages

Bilingual PPC landing page prototype for **Employment Law Assist** (ELA).

> **Not MedVirtual.** This is a separate project from `medvirtual-meta-content-doc` (a Meta ad content doc tool for a different company). Open each folder in its own Cursor workspace.

## What this is

- Next.js app with per-city, per-language landing pages (`/[city]/[lang]`)
- Internal QA index at `/` (not indexed by search engines)
- HubSpot PPC forms, GTM tracking, and Google Ads URL parameter capture

## Production links

- **Live site:** [https://landing-prototype-delta.vercel.app](https://landing-prototype-delta.vercel.app)
- **GitHub:** [https://github.com/shoutgeorge1/landing-prototype](https://github.com/shoutgeorge1/landing-prototype)
- **Vercel:** [https://vercel.com/shoutgeorge1s-projects](https://vercel.com/shoutgeorge1s-projects)

### Bakersfield PPC

- English: [https://landing-prototype-delta.vercel.app/bakersfield/en](https://landing-prototype-delta.vercel.app/bakersfield/en)
- Spanish: [https://landing-prototype-delta.vercel.app/bakersfield/es](https://landing-prototype-delta.vercel.app/bakersfield/es)

### Thank-you pages

- English: [https://landing-prototype-delta.vercel.app/thank-you](https://landing-prototype-delta.vercel.app/thank-you)
- Spanish: [https://landing-prototype-delta.vercel.app/gracias](https://landing-prototype-delta.vercel.app/gracias)

## Getting started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) for the QA index, or go directly to a city page (e.g. `/bakersfield/en`).

## Environment

Copy `.env.example` to `.env.local` and set:

```
NEXT_PUBLIC_GTM_ID=GTM-XXXXXXX
NEXT_PUBLIC_HUBSPOT_PORTAL_ID=
NEXT_PUBLIC_HUBSPOT_ENGLISH_FORM_ID=
NEXT_PUBLIC_HUBSPOT_SPANISH_FORM_ID=
```

## Scripts

| Command         | Description              |
| --------------- | ------------------------ |
| `npm run dev`   | Start development server |
| `npm run build` | Production build         |
| `npm run start` | Run production server    |
| `npm run lint`  | Run ESLint               |

## Config

- Firm details (name, phone, logo, office): `src/lib/content.ts`
- HubSpot form IDs: `src/lib/hubspot.ts` (via env vars)
- Page copy (EN/ES): `src/lib/copy.ts`
- City list: `src/lib/cities.ts`
