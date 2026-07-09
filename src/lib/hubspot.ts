import type { Lang } from "./cities";

/**
 * HubSpot embed configuration.
 *
 * Paste your real IDs in `.env.local` (see `.env.example`):
 *   NEXT_PUBLIC_HUBSPOT_PORTAL_ID
 *   NEXT_PUBLIC_HUBSPOT_ENGLISH_FORM_ID  — English PPC form
 *   NEXT_PUBLIC_HUBSPOT_SPANISH_FORM_ID  — Spanish PPC form
 */
export const HUBSPOT_PORTAL_ID = process.env.NEXT_PUBLIC_HUBSPOT_PORTAL_ID ?? "";
export const HUBSPOT_ENGLISH_FORM_ID =
  process.env.NEXT_PUBLIC_HUBSPOT_ENGLISH_FORM_ID ?? "";
export const HUBSPOT_SPANISH_FORM_ID =
  process.env.NEXT_PUBLIC_HUBSPOT_SPANISH_FORM_ID ?? "";

export function getHubSpotFormId(lang: Lang): string {
  return lang === "es" ? HUBSPOT_SPANISH_FORM_ID : HUBSPOT_ENGLISH_FORM_ID;
}

export function isHubSpotConfigured(lang: Lang): boolean {
  return Boolean(HUBSPOT_PORTAL_ID && getHubSpotFormId(lang));
}
