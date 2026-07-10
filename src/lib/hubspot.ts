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

export const HUBSPOT_EMBED_SCRIPT_URL = `https://js-${HUBSPOT_REGION}.hsforms.net/forms/embed/${HUBSPOT_PORTAL_ID}.js`;

export function getHubSpotFormId(lang: Lang): string {
  return lang === "es" ? HUBSPOT_SPANISH_FORM_ID : HUBSPOT_ENGLISH_FORM_ID;
}

export function getHubSpotStandaloneUrl(lang: Lang): string {
  return HUBSPOT_STANDALONE_URLS[lang];
}

export function isHubSpotConfigured(lang: Lang): boolean {
  return Boolean(HUBSPOT_PORTAL_ID && getHubSpotFormId(lang));
}

/** Post-submit destination: English uses /thank-you, Spanish uses /gracias. */
export function getThankYouPath(citySlug: string, lang: Lang): string {
  return lang === "es"
    ? `/${citySlug}/es/gracias`
    : `/${citySlug}/en/thank-you`;
}

export function getFormLanguageLabel(lang: Lang): "english" | "spanish" {
  return lang === "es" ? "spanish" : "english";
}
