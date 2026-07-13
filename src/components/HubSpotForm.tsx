"use client";

import { useEffect, useId, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { City, Lang } from "@/lib/cities";
import { otherLang } from "@/lib/cities";
import { COPY } from "@/lib/copy";
import { FIRM } from "@/lib/content";
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
import {
  ensureHubSpotScript,
  useHubSpotScriptStatus,
} from "./HubSpotScriptProvider";

interface HubSpotFormProps {
  city: City;
  lang: Lang;
}

const SLOW_LOAD_MS = 12_000;
const HARD_FAIL_MS = 25_000;

/** Only one form frame per page, so a loose match is safe and resilient to event-shape changes. */
function eventMatchesForm(event: Event, formId: string): boolean {
  const detail = (event as CustomEvent<{ formId?: string }>).detail;
  const eventFormId = detail?.formId;
  return !eventFormId || eventFormId === formId;
}

function handleHubSpotFormSubmitted(
  city: City,
  lang: Lang,
  push: (href: string) => void,
): void {
  const submittedFormId = getHubSpotFormId(lang);
  pushHubSpotFormSubmission(submittedFormId, getFormLanguageLabel(lang));
  pushEvent("form_submit", { city: city.slug, lang });
  const thankYouPath = appendPreservedQueryParams(
    getThankYouPath(lang),
    window.location.search,
    { city: city.slug, language: lang },
  );
  push(thankYouPath);
}

function FormSkeleton({ lang }: { lang: Lang }) {
  const label = COPY[lang].form.loading;
  return (
    <div
      className="ela-hubspot-skeleton"
      aria-hidden="true"
      data-loading-label={label}
    >
      <div className="ela-hubspot-skeleton__row ela-hubspot-skeleton__row--split">
        <div className="ela-hubspot-skeleton__field">
          <div className="ela-hubspot-skeleton__label" />
          <div className="ela-hubspot-skeleton__input" />
        </div>
        <div className="ela-hubspot-skeleton__field">
          <div className="ela-hubspot-skeleton__label" />
          <div className="ela-hubspot-skeleton__input" />
        </div>
      </div>
      <div className="ela-hubspot-skeleton__field">
        <div className="ela-hubspot-skeleton__label" />
        <div className="ela-hubspot-skeleton__input" />
      </div>
      <div className="ela-hubspot-skeleton__field">
        <div className="ela-hubspot-skeleton__label" />
        <div className="ela-hubspot-skeleton__input" />
      </div>
      <div className="ela-hubspot-skeleton__field">
        <div className="ela-hubspot-skeleton__label" />
        <div className="ela-hubspot-skeleton__textarea" />
      </div>
      <div className="ela-hubspot-skeleton__button" />
    </div>
  );
}

/**
 * HubSpot V4 portal embed (hs-form-frame).
 *
 * Reveal is driven by a MutationObserver watching the frame container, NOT by a
 * strict formId-matched ready event. HubSpot's V4 events sometimes omit/rename
 * detail.formId, which previously left the skeleton hanging forever even though
 * the form had rendered. The observer fires as soon as HubSpot injects content.
 */
export function HubSpotForm({ city, lang }: HubSpotFormProps) {
  const router = useRouter();
  const scriptStatus = useHubSpotScriptStatus();
  const formId = getHubSpotFormId(lang);
  const formCopy = COPY[lang].form;
  const configured = isHubSpotConfigured(lang);
  const reactId = useId().replace(/:/g, "");
  const instanceId = `${city.slug}-${lang}-${reactId}`;

  const frameRef = useRef<HTMLDivElement | null>(null);
  const mountedRef = useRef(true);
  const readyRef = useRef(false);
  const handledSubmitRef = useRef(false);

  const [isLoading, setIsLoading] = useState(true);
  const [showSlowFallback, setShowSlowFallback] = useState(false);
  const [loadFailed, setLoadFailed] = useState(() => !configured);

  const standaloneUrl =
    typeof window === "undefined"
      ? getHubSpotStandaloneUrl(lang)
      : appendPreservedQueryParamsToUrl(
          getHubSpotStandaloneUrl(lang),
          window.location.search,
        );

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    void ensureHubSpotScript().catch(() => {
      if (mountedRef.current) setLoadFailed(true);
    });
  }, []);

  useEffect(() => {
    router.prefetch(`/${city.slug}/${otherLang(lang)}`);
  }, [router, city.slug, lang]);

  const markReady = () => {
    if (readyRef.current || !mountedRef.current) return;
    readyRef.current = true;
    setIsLoading(false);
    setShowSlowFallback(false);
    setLoadFailed(false);
  };

  // Primary reveal: observe the frame container for HubSpot-injected content.
  useEffect(() => {
    if (!configured) return;
    const target = frameRef.current;
    if (!target) return;

    if (target.childElementCount > 0) {
      markReady();
      return;
    }

    const observer = new MutationObserver(() => {
      if (target.childElementCount > 0) {
        markReady();
        observer.disconnect();
      }
    });
    observer.observe(target, { childList: true, subtree: true });

    return () => observer.disconnect();
  }, [configured, scriptStatus, formId]);

  // Secondary: V4 events for attribution + submission redirect (loose match).
  useEffect(() => {
    if (!configured || scriptStatus === "error") return;

    const handleReady = (event: Event) => {
      if (!eventMatchesForm(event, formId)) return;
      void populateGoogleAdsFieldsV4(event);
      markReady();
      pushEvent("form_ready", { city: city.slug, lang });
    };

    const handleSuccess = (event: Event) => {
      if (!eventMatchesForm(event, formId)) return;
      if (handledSubmitRef.current) return;
      handledSubmitRef.current = true;
      handleHubSpotFormSubmitted(city, lang, (href) => router.push(href));
    };

    window.addEventListener("hs-form-event:on-ready", handleReady);
    window.addEventListener(
      "hs-form-event:on-submission:success",
      handleSuccess,
    );

    return () => {
      window.removeEventListener("hs-form-event:on-ready", handleReady);
      window.removeEventListener(
        "hs-form-event:on-submission:success",
        handleSuccess,
      );
    };
  }, [configured, scriptStatus, formId, city, lang, router]);

  // Slow-load hint (non-fatal).
  useEffect(() => {
    if (!configured || loadFailed || !isLoading) return;
    const timeout = window.setTimeout(() => {
      if (mountedRef.current && isLoading) setShowSlowFallback(true);
    }, SLOW_LOAD_MS);
    return () => window.clearTimeout(timeout);
  }, [configured, loadFailed, isLoading]);

  // Hard failure: script/render never completed.
  useEffect(() => {
    if (!configured || !isLoading || loadFailed) return;
    const timeout = window.setTimeout(() => {
      if (!mountedRef.current || readyRef.current) return;
      setLoadFailed(true);
      setIsLoading(false);
      if (process.env.NODE_ENV === "development") {
        console.error("[HubSpot] form never rendered", { lang, formId });
      }
    }, HARD_FAIL_MS);
    return () => window.clearTimeout(timeout);
  }, [configured, isLoading, loadFailed, lang, formId]);

  const showError = loadFailed || scriptStatus === "error" || !configured;
  const showSkeleton = configured && !showError && isLoading;

  return (
    <div
      id="lead-form"
      className="ela-hubspot-form scroll-mt-4 overflow-hidden rounded-2xl bg-white shadow-[0_24px_60px_rgba(0,0,0,0.35)] ring-1 ring-[var(--gold)]/35"
    >
      <div className="border-b border-[var(--gold)]/25 bg-[var(--navy)] px-5 pb-5 pt-5 sm:px-7 sm:pb-6 sm:pt-6">
        <div className="mb-3 h-1 w-12 rounded-full bg-[var(--gold)]" aria-hidden />
        <h2 className="text-xl font-extrabold tracking-tight text-white sm:text-2xl">
          {formCopy.title}
        </h2>
        <p className="mt-1.5 text-sm leading-relaxed text-white/85 sm:text-base">
          {formCopy.subtitle(city.name)}
        </p>
        <ul className="mt-4 flex flex-wrap gap-x-4 gap-y-2 text-xs font-semibold sm:text-sm">
          {COPY[lang].proofPoints.map((point) => (
            <li key={point} className="flex items-center gap-1.5 text-white/90">
              <span aria-hidden className="text-[var(--gold)]">
                &#10003;
              </span>
              {point}
            </li>
          ))}
        </ul>
      </div>

      <div className="relative bg-gradient-to-b from-[#f7f5ef] to-white px-4 py-5 sm:px-6 sm:pb-6 sm:pt-6">
        {showError ? (
          <div className="rounded-xl border border-dashed border-amber-300 bg-amber-50 p-4 text-sm text-amber-950">
            <p className="font-semibold">{formCopy.loadError}</p>
            <p className="mt-2">
              <a
                href={`tel:${FIRM.phoneTel}`}
                className="font-semibold text-[var(--navy)] underline underline-offset-2"
              >
                {FIRM.phoneDisplay}
              </a>
              {" · "}
              <a
                href={standaloneUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold text-[var(--navy)] underline underline-offset-2"
              >
                {formCopy.fallbackLink}
              </a>
            </p>
          </div>
        ) : (
          <>
            {showSkeleton && (
              <div
                className="ela-hubspot-skeleton-wrap"
                aria-busy="true"
                aria-live="polite"
              >
                <span className="sr-only">{formCopy.loading}</span>
                <FormSkeleton lang={lang} />
              </div>
            )}

            {/* Always mounted: HubSpot's V4 script observes and renders into this node. */}
            <div
              ref={frameRef}
              className={`hs-form-frame hubspot-form-frame ela-hs-form-shell w-full max-w-full transition-opacity duration-300 ${
                isLoading
                  ? "pointer-events-none absolute inset-x-4 top-5 opacity-0 sm:inset-x-6 sm:top-6"
                  : "relative opacity-100"
              }`}
              data-region={HUBSPOT_REGION}
              data-form-id={formId}
              data-portal-id={HUBSPOT_PORTAL_ID}
              data-instance-id={instanceId}
            />

            {showSlowFallback && isLoading && (
              <p className="mt-4 text-center text-sm text-slate-600" role="status">
                {formCopy.slowLoad}{" "}
                <a
                  href={`tel:${FIRM.phoneTel}`}
                  className="font-semibold text-[var(--navy)] underline underline-offset-2"
                >
                  {FIRM.phoneDisplay}
                </a>
              </p>
            )}
          </>
        )}
      </div>

      {!showError && (
        <div className="border-t border-[var(--navy)]/10 bg-[var(--navy)]/5 px-5 py-3.5 text-center sm:px-7">
          <a
            href={`tel:${FIRM.phoneTel}`}
            className="text-sm font-bold text-[var(--navy)] underline-offset-2 hover:underline"
          >
            {COPY[lang].ctaCall}
          </a>
        </div>
      )}
    </div>
  );
}
