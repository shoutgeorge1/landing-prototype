"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { City, Lang } from "@/lib/cities";
import { otherLang } from "@/lib/cities";
import { COPY } from "@/lib/copy";
import { FIRM } from "@/lib/content";
import { populateGoogleAdsHiddenFields, populateGoogleAdsHiddenFieldsFromRoot } from "@/lib/googleAdsParams";
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
import {
  ensureHubSpotScript,
  useHubSpotScriptStatus,
} from "./HubSpotScriptProvider";

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

const SLOW_LOAD_MS = 12_000;

/** Park rendered HubSpot form DOM between language navigations so switches are instant. */
const formDomCache = new Map<string, HTMLElement>();
const formCreateInFlight = new Set<string>();
const formReadyKeys = new Set<string>();

function cacheKey(citySlug: string, lang: Lang, formId: string): string {
  return `${citySlug}:${lang}:${formId}`;
}

function parkForm(key: string, target: HTMLElement | null): void {
  if (!target) return;
  const node = target.firstElementChild as HTMLElement | null;
  if (!node) return;
  formDomCache.set(key, node);
}

function restoreForm(key: string, target: HTMLElement): boolean {
  const node = formDomCache.get(key);
  if (!node) return false;
  target.replaceChildren(node);
  formDomCache.delete(key);
  return true;
}

function createFormInto(
  targetId: string,
  city: City,
  lang: Lang,
  onReady: () => void,
  onSubmitted: () => void,
): void {
  const formId = getHubSpotFormId(lang);
  const key = cacheKey(city.slug, lang, formId);
  if (formCreateInFlight.has(key) || !window.hbspt?.forms?.create) return;

  formCreateInFlight.add(key);

  window.hbspt.forms.create({
    portalId: HUBSPOT_PORTAL_ID,
    formId,
    region: "na2",
    target: `#${targetId}`,
    cssClass: "ela-hs-form",
    css: "",
    onFormReady: ($form: HubSpotFormElement) => {
      formCreateInFlight.delete(key);
      formReadyKeys.add(key);
      populateGoogleAdsHiddenFields($form);
      onReady();
    },
    onFormSubmitted: onSubmitted,
  });
}

/** Shared success handler for live and warm/preloaded forms (HubSpot onFormSubmitted only). */
function handleHubSpotFormSubmitted(
  city: City,
  lang: Lang,
  push: (href: string) => void,
): void {
  const submittedFormId = getHubSpotFormId(lang);
  pushHubSpotFormSubmission(submittedFormId, getFormLanguageLabel(lang));
  pushEvent("form_submit", { city: city.slug, lang });
  const thankYouPath = appendPreservedQueryParams(
    getThankYouPath(city.slug, lang),
    window.location.search,
  );
  push(thankYouPath);
}

function scheduleIdle(task: () => void): () => void {
  const ric = window.requestIdleCallback?.bind(window);
  if (typeof ric === "function") {
    const id = ric(() => task(), { timeout: 2500 });
    return () => window.cancelIdleCallback?.(id);
  }
  const id = window.setTimeout(task, 400);
  return () => window.clearTimeout(id);
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

export function HubSpotForm({ city, lang }: HubSpotFormProps) {
  const router = useRouter();
  const scriptStatus = useHubSpotScriptStatus();
  const formId = getHubSpotFormId(lang);
  const formCopy = COPY[lang].form;
  const configured = isHubSpotConfigured(lang);
  const targetId = `hubspot-form-${city.slug}-${lang}`;
  const key = cacheKey(city.slug, lang, formId);
  const mountedRef = useRef(true);
  const visibleReadyRef = useRef(formReadyKeys.has(key) || formDomCache.has(key));

  const [isLoading, setIsLoading] = useState(
    () => !(formReadyKeys.has(key) || formDomCache.has(key)),
  );
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

  // Ensure script starts loading as soon as the form card mounts.
  useEffect(() => {
    void ensureHubSpotScript().catch(() => {
      if (mountedRef.current) setLoadFailed(true);
    });
  }, []);

  // Create the visible-language form as soon as the script is ready.
  useEffect(() => {
    if (!configured) return;
    if (scriptStatus === "error") {
      if (process.env.NODE_ENV === "development") {
        console.error("[HubSpot] script error", { lang, formId });
      }
      return;
    }

    if (scriptStatus !== "ready") return;

    const target = document.getElementById(targetId);
    if (!target) return;

    if (restoreForm(key, target)) {
      // onFormReady will not fire again — refresh attribution from the current URL.
      populateGoogleAdsHiddenFieldsFromRoot(target);
      visibleReadyRef.current = true;
      queueMicrotask(() => {
        if (!mountedRef.current) return;
        setIsLoading(false);
        setShowSlowFallback(false);
        setLoadFailed(false);
      });
      return () => {
        parkForm(key, document.getElementById(targetId));
      };
    }

    if (formCreateInFlight.has(key) && target.childElementCount > 0) {
      return () => {
        parkForm(key, document.getElementById(targetId));
      };
    }

    if (formReadyKeys.has(key) && target.childElementCount > 0) {
      populateGoogleAdsHiddenFieldsFromRoot(target);
      visibleReadyRef.current = true;
      queueMicrotask(() => {
        if (mountedRef.current) setIsLoading(false);
      });
      return () => {
        parkForm(key, document.getElementById(targetId));
      };
    }

    queueMicrotask(() => {
      if (mountedRef.current) setIsLoading(true);
    });
    createFormInto(
      targetId,
      city,
      lang,
      () => {
        if (!mountedRef.current) {
          parkForm(key, document.getElementById(targetId));
          return;
        }
        visibleReadyRef.current = true;
        setIsLoading(false);
        setShowSlowFallback(false);
        pushEvent("form_ready", { city: city.slug, lang });
      },
      () => handleHubSpotFormSubmitted(city, lang, (href) => router.push(href)),
    );

    return () => {
      parkForm(key, document.getElementById(targetId));
    };
  }, [configured, scriptStatus, formId, city, lang, router, targetId, key]);

  // Warm the alternate language only after the visible form is ready.
  useEffect(() => {
    if (scriptStatus !== "ready" || isLoading || loadFailed) return;
    if (!visibleReadyRef.current && !formReadyKeys.has(key)) return;

    const alt = otherLang(lang);
    const altFormId = getHubSpotFormId(alt);
    router.prefetch(`/${city.slug}/${alt}`);

    const altKey = cacheKey(city.slug, alt, altFormId);
    if (formDomCache.has(altKey) || formCreateInFlight.has(altKey) || formReadyKeys.has(altKey)) {
      return;
    }

    const cancel = scheduleIdle(() => {
      if (!mountedRef.current) return;

      const warmId = `hubspot-warm-${city.slug}-${alt}`;
      let warm = document.getElementById(warmId);
      if (!warm) {
        warm = document.createElement("div");
        warm.id = warmId;
        warm.className = "ela-hubspot-form ela-hs-form-shell ela-hubspot-warm";
        warm.setAttribute("aria-hidden", "true");
        warm.setAttribute("inert", "");
        // Off-screen inert bucket: avoids display:none (which can break HubSpot/reCAPTCHA init)
        // while keeping the warm form out of layout, focus, and AT.
        warm.style.cssText =
          "position:fixed;left:-10000px;top:0;width:360px;height:1px;overflow:hidden;opacity:0;pointer-events:none;";
        document.body.appendChild(warm);
      }

      createFormInto(
        warmId,
        city,
        alt,
        () => {
          const node = warm?.firstElementChild as HTMLElement | null;
          if (node) formDomCache.set(altKey, node);
          pushEvent("form_ready", { city: city.slug, lang: alt, warmed: true });
        },
        () => handleHubSpotFormSubmitted(city, alt, (href) => router.push(href)),
      );
    });

    return cancel;
  }, [scriptStatus, isLoading, loadFailed, city, lang, router, key]);

  const formFailed = loadFailed || scriptStatus === "error" || !configured;

  useEffect(() => {
    if (!configured || scriptStatus === "error" || !isLoading || formFailed) {
      return;
    }

    const timeout = window.setTimeout(() => {
      setShowSlowFallback(true);
    }, SLOW_LOAD_MS);

    return () => window.clearTimeout(timeout);
  }, [configured, scriptStatus, isLoading, formFailed]);

  const showSkeleton = configured && !formFailed && isLoading;
  const showFormShell = configured && !formFailed;

  return (
    <div
      id="lead-form"
      className="ela-hubspot-form scroll-mt-4 overflow-hidden rounded-2xl bg-white shadow-[0_20px_50px_rgba(0,0,0,0.28)] ring-1 ring-black/5"
    >
      <div className="border-b border-slate-100 bg-gradient-to-b from-slate-50 to-white px-5 pb-4 pt-5 sm:px-7 sm:pt-7">
        <div className="mb-3 h-1 w-12 rounded-full bg-[var(--gold)]" aria-hidden />
        <h2 className="text-xl font-extrabold tracking-tight text-[var(--navy)] sm:text-2xl">
          {formCopy.title}
        </h2>
        <p className="mt-1.5 text-sm leading-relaxed text-slate-600 sm:text-base">
          {formCopy.subtitle(city.name)}
        </p>
      </div>

      <div className="relative px-5 py-5 sm:px-7 sm:pb-7 sm:pt-6">
        {showFormShell ? (
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

            <div
              id={targetId}
              className={`ela-hs-form-shell w-full max-w-full transition-opacity duration-300 ${
                isLoading
                  ? "pointer-events-none absolute inset-x-5 top-5 opacity-0 sm:inset-x-7 sm:top-6"
                  : "relative opacity-100"
              }`}
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
        ) : (
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
        )}
      </div>
    </div>
  );
}
