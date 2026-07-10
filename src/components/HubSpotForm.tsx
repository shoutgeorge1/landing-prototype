"use client";

import { useEffect, useId, useState } from "react";
import { useRouter } from "next/navigation";
import type { City, Lang } from "@/lib/cities";
import { COPY } from "@/lib/copy";
import { populateGoogleAdsFieldsV4 } from "@/lib/googleAdsParams";
import {
  getFormLanguageLabel,
  getHubSpotFormId,
  getHubSpotStandaloneUrl,
  getThankYouPath,
  HUBSPOT_PORTAL_ID,
  HUBSPOT_REGION,
  isHubSpotConfigured,
} from "@/lib/hubspot";
import {
  appendPreservedQueryParams,
  appendPreservedQueryParamsToUrl,
} from "@/lib/queryParams";
import { pushEvent, pushHubSpotFormSubmission } from "@/lib/tracking";
import { useHubSpotScriptStatus } from "./HubSpotScriptProvider";

interface HubSpotFormProps {
  city: City;
  lang: Lang;
}

const LOAD_TIMEOUT_MS = 20_000;

function formIdFromEvent(event: Event): string | undefined {
  const detail = (event as CustomEvent<{ formId?: string }>).detail;
  return detail?.formId;
}

export function HubSpotForm({ city, lang }: HubSpotFormProps) {
  const router = useRouter();
  const instanceId = useId().replace(/:/g, "");
  const scriptStatus = useHubSpotScriptStatus();
  const formId = getHubSpotFormId(lang);
  const formCopy = COPY[lang].form;
  const configured = isHubSpotConfigured(lang);

  const [isLoading, setIsLoading] = useState(true);
  const [showFallback, setShowFallback] = useState(false);
  const [standaloneUrl, setStandaloneUrl] = useState(() =>
    getHubSpotStandaloneUrl(lang),
  );

  useEffect(() => {
    setStandaloneUrl(
      appendPreservedQueryParamsToUrl(
        getHubSpotStandaloneUrl(lang),
        window.location.search,
      ),
    );
  }, [lang]);

  useEffect(() => {
    if (!configured) return;

    const handleReady = (event: Event) => {
      if (formIdFromEvent(event) !== formId) return;
      setIsLoading(false);
      void populateGoogleAdsFieldsV4(event);
      pushEvent("form_ready", { city: city.slug, lang });
    };

    const handleSuccess = (event: Event) => {
      if (formIdFromEvent(event) !== formId) return;

      pushHubSpotFormSubmission(formId, getFormLanguageLabel(lang));
      pushEvent("form_submit", { city: city.slug, lang });

      const thankYouPath = appendPreservedQueryParams(
        getThankYouPath(city.slug, lang),
        window.location.search,
      );
      router.push(thankYouPath);
    };

    window.addEventListener("hs-form-event:on-ready", handleReady);
    window.addEventListener("hs-form-event:on-submission:success", handleSuccess);

    return () => {
      window.removeEventListener("hs-form-event:on-ready", handleReady);
      window.removeEventListener(
        "hs-form-event:on-submission:success",
        handleSuccess,
      );
    };
  }, [configured, formId, city.slug, lang, router]);

  useEffect(() => {
    if (!configured || scriptStatus === "error") {
      setShowFallback(true);
      setIsLoading(false);
      return;
    }

    if (scriptStatus !== "ready" || !isLoading) return;

    const timeout = window.setTimeout(() => {
      setIsLoading(false);
      setShowFallback(true);
    }, LOAD_TIMEOUT_MS);

    return () => window.clearTimeout(timeout);
  }, [configured, scriptStatus, isLoading]);

  return (
    <div
      id="lead-form"
      className="scroll-mt-4 rounded-2xl bg-white p-4 shadow-2xl ring-2 ring-slate-200 sm:p-6"
    >
      <h2 className="text-xl font-bold text-[var(--navy)]">{formCopy.title}</h2>
      <p className="mt-1.5 text-base text-slate-600">
        {formCopy.subtitle(city.name)}
      </p>

      <div className="relative mt-5 min-h-[280px] w-full overflow-hidden">
        {configured && scriptStatus !== "error" ? (
          <>
            {isLoading && (
              <div
                className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3 rounded-lg bg-slate-50"
                aria-live="polite"
                aria-busy="true"
              >
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--navy)] border-t-transparent" />
                <p className="text-sm font-medium text-slate-600">
                  {formCopy.loading}
                </p>
              </div>
            )}
            <div
              className={`hs-form-frame hubspot-form-frame w-full max-w-full transition-opacity duration-300 ${
                isLoading ? "pointer-events-none opacity-0" : "opacity-100"
              }`}
              data-region={HUBSPOT_REGION}
              data-form-id={formId}
              data-portal-id={HUBSPOT_PORTAL_ID}
              data-instance-id={instanceId}
            />
          </>
        ) : (
          <div className="rounded-lg border-2 border-dashed border-amber-300 bg-amber-50 p-4 text-sm text-amber-950">
            <p className="font-semibold">{formCopy.fallbackPrompt}</p>
          </div>
        )}

        {showFallback && (
          <p className="mt-4 text-center text-sm text-slate-600">
            {formCopy.fallbackPrompt}{" "}
            <a
              href={standaloneUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="font-semibold text-[var(--navy)] underline underline-offset-2 hover:text-[var(--gold)]"
            >
              {formCopy.fallbackLink}
            </a>
          </p>
        )}
      </div>
    </div>
  );
}
