export const GTM_ID = process.env.NEXT_PUBLIC_GTM_ID || "GTM-W4GRWHTR";

type DataLayerEntry = Record<string, unknown>;

declare global {
  interface Window {
    dataLayer?: DataLayerEntry[];
  }
}

export function pushEvent(event: string, data: DataLayerEntry = {}): void {
  if (typeof window === "undefined") return;
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ event, ...data });
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
    const merged = { ...getUtms(), ...found };
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
