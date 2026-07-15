import { FIRM } from "./content";
import { GOOGLE_ADS_PARAM_KEYS } from "./googleAdsParams";

export const GTM_ID = process.env.NEXT_PUBLIC_GTM_ID || "GTM-W4GRWHTR";

/** Google Ads account conversion ID (Click to call / website tags). */
export const GOOGLE_ADS_AW_ID =
  process.env.NEXT_PUBLIC_GOOGLE_ADS_AW_ID || "AW-18079555023";

/** Click-to-call conversion: AW-ID/label from Google Ads setup email. */
export const GOOGLE_ADS_PHONE_CLICK_SEND_TO =
  process.env.NEXT_PUBLIC_GOOGLE_ADS_PHONE_CLICK_SEND_TO ||
  "AW-18079555023/lfMHCKvIkNEcEM-7gK1D";

type DataLayerEntry = Record<string, unknown>;
const firedHubSpotSubmissionIds = new Set<string>();

declare global {
  interface Window {
    dataLayer?: DataLayerEntry[];
    gtag?: (...args: unknown[]) => void;
  }
}

export function pushEvent(event: string, data: DataLayerEntry = {}): void {
  if (typeof window === "undefined") return;
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ event, ...data });
}

export function pushHubSpotFormSubmission(
  formId: string,
  formLanguage: "english" | "spanish",
  submissionId: string,
): void {
  if (!submissionId || firedHubSpotSubmissionIds.has(submissionId)) return;
  firedHubSpotSubmissionIds.add(submissionId);
  const path = window.location.pathname;
  pushEvent("hubspot_form_submission", {
    form_language: formLanguage,
    form_id: formId,
    hubspot_submission_id: submissionId,
    event_id: submissionId,
    landing_page_path: path,
    page_path: path,
    ...getAttributionPayload(),
  });
}

const ATTRIBUTION_KEYS = [
  "utm_source",
  "utm_medium",
  "utm_campaign",
  "utm_term",
  "utm_content",
  "gclid",
  "gbraid",
  "wbraid",
  "msclkid",
  "fbclid",
  "city",
  "language",
  ...GOOGLE_ADS_PARAM_KEYS,
] as const;

/** Paid click IDs — never discarded by weaker later visits without them. */
const PAID_CLICK_KEYS = [
  "gclid",
  "gbraid",
  "wbraid",
  "msclkid",
  "fbclid",
] as const;

const META_UTM_SOURCES = new Set([
  "facebook",
  "fb",
  "ig",
  "instagram",
  "meta",
  "messenger",
]);

function getLiveAttribution(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const params = new URLSearchParams(window.location.search);
  const live: Record<string, string> = {};
  for (const key of ATTRIBUTION_KEYS) {
    const value = params.get(key);
    if (value) live[key] = value;
  }
  return live;
}

function classifyTrafficSource(merged: Record<string, string>): string {
  if (merged.gclid || merged.gbraid || merged.wbraid) return "google_ads";
  if (merged.msclkid) return "microsoft_ads";
  if (merged.fbclid) return "meta_ads";

  const utm = (merged.utm_source || "").trim().toLowerCase();
  if (utm) {
    if (META_UTM_SOURCES.has(utm) || utm.includes("facebook") || utm.includes("meta")) {
      return "meta_ads";
    }
    return utm.replace(/\s+/g, "_");
  }

  return "direct";
}

/** Merge stored + live query attribution for conversion events. */
export function getAttributionPayload(): Record<string, string> {
  const stored = getUtms();
  const live = getLiveAttribution();
  const merged = { ...stored, ...live };

  // Keep prior paid click IDs if this pageview omitted them.
  for (const key of PAID_CLICK_KEYS) {
    if (!merged[key] && stored[key]) merged[key] = stored[key];
  }

  const path = typeof window !== "undefined" ? window.location.pathname : "";
  const pathParts = path.split("/").filter(Boolean);
  if (!merged.city && pathParts[0]) merged.city = pathParts[0];
  if (!merged.language && (pathParts[1] === "en" || pathParts[1] === "es")) {
    merged.language = pathParts[1];
  }

  return {
    ...merged,
    traffic_source: classifyTrafficSource(merged),
  };
}

/** Fire Google Ads "Click to call" website conversion (does not block tel: navigation). */
function fireGoogleAdsPhoneClickConversion(): void {
  if (typeof window === "undefined") return;
  window.dataLayer = window.dataLayer || [];
  if (typeof window.gtag !== "function") {
    // Match Google's stub so commands queue until gtag.js loads.
    window.gtag = function gtag() {
      // eslint-disable-next-line prefer-rest-params
      window.dataLayer!.push(arguments as unknown as DataLayerEntry);
    };
  }
  window.gtag("event", "conversion", {
    send_to: GOOGLE_ADS_PHONE_CLICK_SEND_TO,
    value: 1.0,
    currency: "USD",
  });
}

/** Dual-fire phone clicks with full source attribution for GTM/Ads. */
export function trackPhoneClick(location: string): void {
  const attribution = getAttributionPayload();
  const path = typeof window !== "undefined" ? window.location.pathname : undefined;
  const payload = {
    location,
    phone_number: FIRM.phoneTel,
    phone_display: FIRM.phoneDisplay,
    page_path: path,
    landing_page_path: path,
    ...attribution,
  };
  pushEvent("phone_click", payload);
  pushEvent("call_click", payload);
  fireGoogleAdsPhoneClickConversion();
}

const UTM_KEYS = [
  "utm_source",
  "utm_medium",
  "utm_campaign",
  "utm_term",
  "utm_content",
  "gclid",
  "gbraid",
  "wbraid",
  "msclkid",
  "fbclid",
  "city",
  "language",
  ...GOOGLE_ADS_PARAM_KEYS,
];

const STORAGE_KEY = "ela_utms";

export type UtmData = Record<string, string>;

export function captureUtms(): void {
  if (typeof window === "undefined") return;
  const params = new URLSearchParams(window.location.search);
  const found: UtmData = {};
  UTM_KEYS.forEach((key) => {
    const value = params.get(key);
    if (value) found[key] = value;
  });
  if (Object.keys(found).length > 0) {
    const previous = getUtms();
    const merged = { ...previous, ...found };
    // Preserve stronger paid-click IDs across later pages without them.
    for (const key of PAID_CLICK_KEYS) {
      if (!merged[key] && previous[key]) merged[key] = previous[key];
    }
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
    } catch {
      // localStorage may be unavailable (private mode); fail silently
    }
  }
}

export function getUtms(): UtmData {
  if (typeof window === "undefined") return {};
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}") as UtmData;
  } catch {
    return {};
  }
}
