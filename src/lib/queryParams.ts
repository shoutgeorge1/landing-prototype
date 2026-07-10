/** Keys preserved when redirecting or linking to standalone HubSpot forms. */
export const PRESERVED_QUERY_KEYS = [
  "gclid",
  "gbraid",
  "wbraid",
  "utm_source",
  "utm_medium",
  "utm_campaign",
  "utm_term",
  "utm_content",
  "google_campaign",
  "google_ad_group",
  "google_keyword",
] as const;

export function buildPreservedQueryString(search: string): string {
  const params = new URLSearchParams(search);
  const preserved = new URLSearchParams();
  for (const key of PRESERVED_QUERY_KEYS) {
    const value = params.get(key);
    if (value) preserved.set(key, value);
  }
  const query = preserved.toString();
  return query ? `?${query}` : "";
}

export function appendPreservedQueryParams(path: string, search: string): string {
  return `${path}${buildPreservedQueryString(search)}`;
}

export function appendPreservedQueryParamsToUrl(
  baseUrl: string,
  search: string,
): string {
  const query = buildPreservedQueryString(search);
  if (!query) return baseUrl;
  return `${baseUrl}${baseUrl.includes("?") ? "&" : "?"}${query.slice(1)}`;
}
