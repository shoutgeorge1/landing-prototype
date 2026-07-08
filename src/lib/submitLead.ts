import { getUtms } from "./tracking";

export interface LeadPayload {
  firstName: string;
  lastName: string;
  phone: string;
  email: string;
  city: string;
  employer: string;
  whatHappened: string;
  consent: boolean;
  citySlug: string;
  lang: string;
}

export interface LeadResult {
  ok: boolean;
}

/**
 * Placeholder lead handler.
 *
 * Swap the body of this function for a real integration later, e.g.:
 *   - HubSpot Forms API / submission endpoint
 *   - Formspree (POST to https://formspree.io/f/XXXX)
 *   - A custom /api/lead route that forwards to a CRM
 *
 * UTM params captured on landing are merged in automatically so the
 * downstream system receives full attribution.
 */
export async function submitLead(payload: LeadPayload): Promise<LeadResult> {
  const fullPayload = {
    ...payload,
    utms: getUtms(),
    submittedAt: new Date().toISOString(),
    pageUrl: typeof window !== "undefined" ? window.location.href : "",
  };

  // eslint-disable-next-line no-console
  console.log("[submitLead] captured lead (placeholder):", fullPayload);

  // TODO: replace with real network call, e.g.
  // await fetch("/api/lead", { method: "POST", body: JSON.stringify(fullPayload) });

  return { ok: true };
}
