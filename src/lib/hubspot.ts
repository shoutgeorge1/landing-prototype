import type { Lang } from "./cities";

/** HubSpot portal and Bakersfield PPC form IDs (na2 region). */
export const HUBSPOT_PORTAL_ID =
  process.env.NEXT_PUBLIC_HUBSPOT_PORTAL_ID ?? "242396697";
export const HUBSPOT_REGION = process.env.NEXT_PUBLIC_HUBSPOT_REGION ?? "na2";

export const HUBSPOT_ENGLISH_FORM_ID =
  process.env.NEXT_PUBLIC_HUBSPOT_ENGLISH_FORM_ID ??
  "6dc81a33-35df-4dc4-b20a-ec5e409ed420";
export const HUBSPOT_SPANISH_FORM_ID =
  process.env.NEXT_PUBLIC_HUBSPOT_SPANISH_FORM_ID ??
  "d11f9f2c-a1d2-4ae0-84b3-9f602ad03d51";

export const HUBSPOT_STANDALONE_URLS: Record<Lang, string> = {
  en:
    process.env.NEXT_PUBLIC_HUBSPOT_ENGLISH_STANDALONE_URL ??
    "https://40behl.share-na2.hsforms.com/2bcgaMzXfTcSyCuxeQJ7UIA",
  es:
    process.env.NEXT_PUBLIC_HUBSPOT_SPANISH_STANDALONE_URL ??
    "https://40behl.share-na2.hsforms.com/20R-fLKHSSuCEs59gKtA9UQ",
};

/** Same subscription type on EN + ES HubSpot forms (communication consent). */
export const HUBSPOT_COMMUNICATION_SUBSCRIPTION_TYPE_ID = 717581389;

/** Unauthenticated Forms API submit — same portal forms the embed used. */
export function getHubSpotSubmitUrl(lang: Lang): string {
  return `https://api.hsforms.com/submissions/v3/integration/submit/${HUBSPOT_PORTAL_ID}/${getHubSpotFormId(lang)}`;
}

export function getHubSpotFormId(lang: Lang): string {
  return lang === "es" ? HUBSPOT_SPANISH_FORM_ID : HUBSPOT_ENGLISH_FORM_ID;
}

export function getHubSpotStandaloneUrl(lang: Lang): string {
  return HUBSPOT_STANDALONE_URLS[lang];
}

export function isHubSpotConfigured(lang: Lang): boolean {
  return Boolean(HUBSPOT_PORTAL_ID && getHubSpotFormId(lang));
}

/** Post-submit destination: shared EN/ES thank-you pages (not city-specific). */
export function getThankYouPath(lang: Lang): string {
  return lang === "es" ? "/gracias" : "/thank-you";
}

export function getFormLanguageLabel(lang: Lang): "english" | "spanish" {
  return lang === "es" ? "spanish" : "english";
}
