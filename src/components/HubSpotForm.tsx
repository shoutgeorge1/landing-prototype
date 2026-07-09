"use client";

import { useEffect, useRef, useState } from "react";
import Script from "next/script";
import { useRouter } from "next/navigation";
import type { City, Lang } from "@/lib/cities";
import { COPY } from "@/lib/copy";
import { populateGoogleAdsHiddenFields } from "@/lib/googleAdsParams";
import {
  getHubSpotFormId,
  HUBSPOT_PORTAL_ID,
  isHubSpotConfigured,
} from "@/lib/hubspot";
import { pushEvent } from "@/lib/tracking";

interface HubSpotFormProps {
  city: City;
  lang: Lang;
}

type HubSpotFormElement = Parameters<typeof populateGoogleAdsHiddenFields>[0];

interface HubSpotCreateOptions {
  portalId: string;
  formId: string;
  target: string;
  onFormReady?: ($form: HubSpotFormElement) => void;
  onFormSubmitted?: () => void;
}

declare global {
  interface Window {
    hbspt?: {
      forms: {
        create: (options: HubSpotCreateOptions) => void;
      };
    };
  }
}

const HS_FORMS_SCRIPT = "https://js.hsforms.net/forms/embed/v2.js";

export function HubSpotForm({ city, lang }: HubSpotFormProps) {
  const router = useRouter();
  const containerId = "lead-form";
  const hubspotTargetId = "hubspot-form-target";
  const targetSelector = `#${hubspotTargetId}`;
  const formCreatedRef = useRef(false);
  const [scriptReady, setScriptReady] = useState(false);
  const configured = isHubSpotConfigured(lang);
  const formId = getHubSpotFormId(lang);
  const formCopy = COPY[lang].form;

  useEffect(() => {
    if (!configured || !scriptReady || formCreatedRef.current) return;
    if (!window.hbspt?.forms?.create) return;

    formCreatedRef.current = true;

    window.hbspt.forms.create({
      portalId: HUBSPOT_PORTAL_ID,
      formId,
      target: targetSelector,
      onFormReady: ($form) => {
        // Hidden fields google_campaign, google_ad_group, and google_keyword are
        // populated from Google Ads Final URL suffix query parameters.
        populateGoogleAdsHiddenFields($form);
        pushEvent("form_ready", { city: city.slug, lang });
      },
      onFormSubmitted: () => {
        pushEvent("form_submit", { city: city.slug, lang });
        router.push(`/thank-you?lang=${lang}`);
      },
    });
  }, [configured, scriptReady, formId, city.slug, lang, router, targetSelector]);

  return (
    <div
      id={containerId}
      className="scroll-mt-4 rounded-2xl bg-white p-4 shadow-2xl ring-2 ring-slate-200 sm:p-6"
    >
      <h2 className="text-xl font-bold text-[var(--navy)]">{formCopy.title}</h2>
      <p className="mt-1.5 text-base text-slate-600">{formCopy.subtitle(city.name)}</p>
      <div className="mt-5">
      {configured ? (
        <>
          <Script
            src={HS_FORMS_SCRIPT}
            strategy="afterInteractive"
            onReady={() => setScriptReady(true)}
            onLoad={() => setScriptReady(true)}
          />
          <div id={hubspotTargetId} />
        </>
      ) : (
        <div className="rounded-lg border-2 border-dashed border-amber-300 bg-amber-50 p-4 text-sm text-amber-950">
          <p className="font-semibold">HubSpot form not configured</p>
          <p className="mt-2">
            Add your portal and form IDs to <code className="text-xs">.env.local</code>{" "}
            (see <code className="text-xs">.env.example</code>):
          </p>
          <ul className="mt-2 list-inside list-disc space-y-1 font-mono text-xs">
            <li>NEXT_PUBLIC_HUBSPOT_PORTAL_ID</li>
            <li>
              {lang === "es"
                ? "NEXT_PUBLIC_HUBSPOT_SPANISH_FORM_ID"
                : "NEXT_PUBLIC_HUBSPOT_ENGLISH_FORM_ID"}
            </li>
          </ul>
        </div>
      )}
      </div>
    </div>
  );
}
