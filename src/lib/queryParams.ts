/** Keys preserved when redirecting or linking to standalone HubSpot forms. */
export const PRESERVED_QUERY_KEYS = [
  "gclid",
  "gbraid",
  "wbraid",
  "msclkid",
  "fbclid",
  "utm_source",
  "utm_medium",
  "utm_campaign",
  "utm_term",
  "utm_content",
  "city",
  "language",
  "google_campaign",
  "google_ad_group",
  "google_keyword",
] as const;

export function buildPreservedQueryString(
  search: string,
  extras: Record<string, string> = {},
): string {
  const params = new URLSearchParams(search);
  const preserved = new URLSearchParams();
  for (const key of PRESERVED_QUERY_KEYS) {
    const value = extras[key] ?? params.get(key);
    if (value) preserved.set(key, value);
  }
  for (const [key, value] of Object.entries(extras)) {
    if (value && !preserved.has(key)) preserved.set(key, value);
  }
  const query = preserved.toString();
  return query ? `?${query}` : "";
}

export function appendPreservedQueryParams(
  path: string,
  search: string,
  extras: Record<string, string> = {},
): string {
  return `${path}${buildPreservedQueryString(search, extras)}`;
}

export function appendPreservedQueryParamsToUrl(
  baseUrl: string,
  search: string,
): string {
  const query = buildPreservedQueryString(search);
  if (!query) return baseUrl;
  return `${baseUrl}${baseUrl.includes("?") ? "&" : "?"}${query.slice(1)}`;
}
