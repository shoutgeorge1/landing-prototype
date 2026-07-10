"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { City, Lang } from "@/lib/cities";
import { COPY } from "@/lib/copy";
import { populateGoogleAdsHiddenFields } from "@/lib/googleAdsParams";
import {
  getFormLanguageLabel,
  getHubSpotFormId,
  getHubSpotStandaloneUrl,
  getThankYouPath,
  HUBSPOT_PORTAL_ID,
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

type HubSpotFormElement = Parameters<typeof populateGoogleAdsHiddenFields>[0];

interface HubSpotCreateOptions {
  portalId: string;
  formId: string;
  region?: string;
  target: string;
  cssClass?: string;
  css?: string;
  submitText?: string;
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

const LOAD_TIMEOUT_MS = 20_000;

export function HubSpotForm({ city, lang }: HubSpotFormProps) {
  const router = useRouter();
  const scriptStatus = useHubSpotScriptStatus();
  const formId = getHubSpotFormId(lang);
  const formCopy = COPY[lang].form;
  const configured = isHubSpotConfigured(lang);
  const targetId = `hubspot-form-${city.slug}-${lang}`;
  const formCreatedRef = useRef(false);

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
    formCreatedRef.current = false;
    setIsLoading(true);
    setShowFallback(false);
  }, [formId, targetId]);

  useEffect(() => {
    if (!configured || scriptStatus === "error") {
      setShowFallback(true);
      setIsLoading(false);
      return;
    }

    if (scriptStatus !== "ready" || formCreatedRef.current) return;
    if (!window.hbspt?.forms?.create) {
      setShowFallback(true);
      setIsLoading(false);
      return;
    }

    const target = document.getElementById(targetId);
    if (target) target.innerHTML = "";

    formCreatedRef.current = true;

    window.hbspt.forms.create({
      portalId: HUBSPOT_PORTAL_ID,
      formId,
      region: "na2",
      target: `#${targetId}`,
      cssClass: "ela-hs-form",
      css: "",
      onFormReady: ($form) => {
        populateGoogleAdsHiddenFields($form);
        setIsLoading(false);
        pushEvent("form_ready", { city: city.slug, lang });
      },
      onFormSubmitted: () => {
        pushHubSpotFormSubmission(formId, getFormLanguageLabel(lang));
        pushEvent("form_submit", { city: city.slug, lang });
        const thankYouPath = appendPreservedQueryParams(
          getThankYouPath(city.slug, lang),
          window.location.search,
        );
        router.push(thankYouPath);
      },
    });
  }, [configured, scriptStatus, formId, city.slug, lang, router, targetId]);

  useEffect(() => {
    if (!configured || scriptStatus === "error" || !isLoading) return;

    const timeout = window.setTimeout(() => {
      setIsLoading(false);
      setShowFallback(true);
    }, LOAD_TIMEOUT_MS);

    return () => window.clearTimeout(timeout);
  }, [configured, scriptStatus, isLoading]);

  return (
    <div
      id="lead-form"
      className="scroll-mt-4 overflow-hidden rounded-2xl bg-white shadow-[0_20px_50px_rgba(0,0,0,0.28)] ring-1 ring-black/5"
    >
      <div className="border-b border-slate-100 bg-gradient-to-b from-slate-50 to-white px-5 pb-4 pt-5 sm:px-6 sm:pt-6">
        <div className="mb-3 h-1 w-12 rounded-full bg-[var(--gold)]" aria-hidden />
        <h2 className="text-xl font-extrabold tracking-tight text-[var(--navy)] sm:text-2xl">
          {formCopy.title}
        </h2>
        <p className="mt-1.5 text-sm leading-relaxed text-slate-600 sm:text-base">
          {formCopy.subtitle(city.name)}
        </p>
      </div>

      <div className="relative px-5 py-5 sm:px-6 sm:pb-6">
        {configured && scriptStatus !== "error" ? (
          <>
            {isLoading && (
              <div
                className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3 bg-white/95"
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
              id={targetId}
              className={`ela-hs-form-shell w-full max-w-full transition-opacity duration-300 ${
                isLoading ? "min-h-[320px] opacity-0" : "opacity-100"
              }`}
            />
          </>
        ) : (
          <div className="rounded-xl border border-dashed border-amber-300 bg-amber-50 p-4 text-sm text-amber-950">
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
