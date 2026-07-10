/**
 * Google Ads Final URL suffix parameters for HubSpot hidden fields.
 *
 * Google Ads passes these at the ad group level via Final URL suffix, e.g.:
 *   google_campaign=bakersfield_employment_lawyer_english
 *   &google_ad_group=wrongful_termination
 *   &google_keyword={keyword}
 *
 * HubSpot hidden fields with matching internal names are populated from the
 * landing page URL query string when the form loads.
 */
export const GOOGLE_ADS_PARAM_KEYS = [
  "google_campaign",
  "google_ad_group",
  "google_keyword",
] as const;

export type GoogleAdsParamKey = (typeof GOOGLE_ADS_PARAM_KEYS)[number];

export type GoogleAdsParams = Partial<Record<GoogleAdsParamKey, string>>;

export function readGoogleAdsParamsFromSearch(search: string): GoogleAdsParams {
  const params = new URLSearchParams(search);
  const found: GoogleAdsParams = {};
  for (const key of GOOGLE_ADS_PARAM_KEYS) {
    const value = params.get(key);
    if (value) found[key] = value;
  }
  return found;
}

export function readGoogleAdsParamsFromUrl(): GoogleAdsParams {
  if (typeof window === "undefined") return {};
  return readGoogleAdsParamsFromSearch(window.location.search);
}

/** jQuery-like form wrapper passed to HubSpot onFormReady callbacks. */
type HubSpotFormElement = {
  find: (selector: string) => {
    length: number;
    val: (value?: string) => unknown;
    get: (index: number) => HTMLElement | undefined;
  };
};

function dispatchInputEvents(input: HTMLInputElement): void {
  input.dispatchEvent(new Event("input", { bubbles: true }));
  input.dispatchEvent(new Event("change", { bubbles: true }));
}

/**
 * Defensive fallback: set HubSpot hidden fields from current URL parameters
 * and dispatch input/change events so HubSpot registers the values.
 *
 * Only writes when the URL has a non-empty value — never clears an existing
 * field value just because the param is absent from the current URL.
 */
export function populateGoogleAdsHiddenFieldsFromRoot(root: ParentNode): void {
  const urlParams = readGoogleAdsParamsFromUrl();
  for (const key of GOOGLE_ADS_PARAM_KEYS) {
    const value = urlParams[key];
    if (!value) continue;

    // HubSpot may emit name="google_campaign" or name="0-1/google_campaign".
    const inputs = root.querySelectorAll<HTMLInputElement>(
      `input[name="${key}"], input[name$="/${key}"]`,
    );
    inputs.forEach((input) => {
      if (input.value === value) return;
      input.value = value;
      dispatchInputEvents(input);
    });
  }
}

/**
 * Same as populateGoogleAdsHiddenFieldsFromRoot, for HubSpot's jQuery-like
 * onFormReady $form wrapper.
 */
export function populateGoogleAdsHiddenFields($form: HubSpotFormElement): void {
  const urlParams = readGoogleAdsParamsFromUrl();
  for (const key of GOOGLE_ADS_PARAM_KEYS) {
    const value = urlParams[key];
    if (!value) continue;

    const inputs = $form.find(
      `input[name="${key}"], input[name$="/${key}"]`,
    );
    if (!inputs.length) continue;

    inputs.val(value);
    const el = inputs.get(0);
    if (el instanceof HTMLInputElement) {
      dispatchInputEvents(el);
    }
  }
}

interface HubSpotFormV4Instance {
  getFormId: () => string;
  setFieldValue?: (name: string, value: string) => Promise<void>;
}

declare global {
  interface Window {
    HubSpotFormsV4?: {
      getFormFromEvent: (event: Event) => HubSpotFormV4Instance | null;
    };
  }
}

/** Populate Google Ads hidden fields on HubSpot V4 forms when the embed API supports it. */
export async function populateGoogleAdsFieldsV4(event: Event): Promise<void> {
  const form = window.HubSpotFormsV4?.getFormFromEvent(event);
  if (!form?.setFieldValue) return;

  const urlParams = readGoogleAdsParamsFromUrl();
  for (const key of GOOGLE_ADS_PARAM_KEYS) {
    const value = urlParams[key];
    if (!value) continue;
    try {
      await form.setFieldValue(key, value);
    } catch {
      // Field may not exist on this form variant; ignore.
    }
  }
}
