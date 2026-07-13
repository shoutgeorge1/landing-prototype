import {
  getHubSpotFormId,
  getHubSpotSubmitUrl,
  HUBSPOT_COMMUNICATION_SUBSCRIPTION_TYPE_ID,
} from "./hubspot";
import { readGoogleAdsParamsFromUrl } from "./googleAdsParams";
import type { Lang } from "./cities";

export interface LeadPayload {
  firstName: string;
  lastName: string;
  phone: string;
  email: string;
  message: string;
  consent: boolean;
  lang: Lang;
  pageName: string;
  /** Exact consent checkbox label sent to HubSpot for audit trail. */
  communicationConsentText: string;
  /** Processing-consent notice text for HubSpot legalConsentOptions. */
  processingConsentText: string;
}

export interface LeadResult {
  ok: boolean;
  error?: string;
}

type HubSpotField = { name: string; value: string };

function readHutk(): string | undefined {
  if (typeof document === "undefined") return undefined;
  const match = document.cookie.match(/(?:^|;\s*)hubspotutk=([^;]+)/);
  return match?.[1] ? decodeURIComponent(match[1]) : undefined;
}

/**
 * Submit to the same HubSpot form GUIDs as the old iframe embed.
 * Leads land in HubSpot under the existing EN/ES forms — no embed script.
 */
export async function submitLead(payload: LeadPayload): Promise<LeadResult> {
  if (!payload.consent) {
    return { ok: false, error: "consent_required" };
  }

  const fields: HubSpotField[] = [
    { name: "firstname", value: payload.firstName.trim() },
    { name: "lastname", value: payload.lastName.trim() },
    { name: "phone", value: payload.phone.trim() },
    { name: "email", value: payload.email.trim() },
  ];

  const message = payload.message.trim();
  if (message) fields.push({ name: "message", value: message });

  const ads = readGoogleAdsParamsFromUrl();
  for (const [name, value] of Object.entries(ads)) {
    if (value) fields.push({ name, value });
  }

  const hutk = readHutk();
  const body = {
    fields,
    context: {
      ...(hutk ? { hutk } : {}),
      pageUri: typeof window !== "undefined" ? window.location.href : "",
      pageName: payload.pageName,
    },
    legalConsentOptions: {
      consent: {
        consentToProcess: true,
        text: payload.processingConsentText,
        communications: [
          {
            value: true,
            subscriptionTypeId: HUBSPOT_COMMUNICATION_SUBSCRIPTION_TYPE_ID,
            text: payload.communicationConsentText,
          },
        ],
      },
    },
  };

  try {
    const response = await fetch(getHubSpotSubmitUrl(payload.lang), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      if (process.env.NODE_ENV === "development") {
        const detail = await response.text().catch(() => "");
        console.error("[submitLead] HubSpot rejected", {
          formId: getHubSpotFormId(payload.lang),
          status: response.status,
          detail,
        });
      }
      return { ok: false, error: "hubspot_rejected" };
    }

    return { ok: true };
  } catch (error) {
    if (process.env.NODE_ENV === "development") {
      console.error("[submitLead] network error", error);
    }
    return { ok: false, error: "network" };
  }
}
