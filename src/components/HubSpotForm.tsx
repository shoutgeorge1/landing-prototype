"use client";

import { useEffect, useId, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import type { City, Lang } from "@/lib/cities";
import { otherLang } from "@/lib/cities";
import { COPY } from "@/lib/copy";
import { FIRM, MICROSITE } from "@/lib/content";
import {
  getFormLanguageLabel,
  getHubSpotFormId,
  getHubSpotStandaloneUrl,
  getThankYouPath,
  isHubSpotConfigured,
} from "@/lib/hubspot";
import {
  appendPreservedQueryParams,
  appendPreservedQueryParamsToUrl,
  PRESERVED_QUERY_KEYS,
} from "@/lib/queryParams";
import { submitLead } from "@/lib/submitLead";
import {
  getAttributionPayload,
  pushEvent,
  pushHubSpotFormSubmission,
} from "@/lib/tracking";
import { TrackedTelLink } from "./TrackedTelLink";

interface HubSpotFormProps {
  city: City;
  lang: Lang;
}

type FieldErrors = Partial<
  Record<"firstName" | "lastName" | "phone" | "email" | "consent", string>
>;

function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function isValidPhone(value: string): boolean {
  const digits = value.replace(/\D/g, "");
  return digits.length >= 10 && digits.length <= 15;
}

/** Attribution whitelist for thank-you / fallback URLs (URL + localStorage). */
function preservedAttributionExtras(
  overrides: Record<string, string> = {},
): Record<string, string> {
  const attribution = getAttributionPayload();
  const extras: Record<string, string> = {};
  for (const key of PRESERVED_QUERY_KEYS) {
    const value = overrides[key] ?? attribution[key];
    if (value) extras[key] = value;
  }
  return extras;
}

export function HubSpotForm({ city, lang }: HubSpotFormProps) {
  const router = useRouter();
  const formCopy = COPY[lang].form;
  const configured = isHubSpotConfigured(lang);
  const formId = getHubSpotFormId(lang);
  const baseId = useId().replace(/:/g, "");

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [consent, setConsent] = useState(false);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitFailed, setSubmitFailed] = useState(false);

  const standaloneUrl =
    typeof window === "undefined"
      ? getHubSpotStandaloneUrl(lang)
      : appendPreservedQueryParamsToUrl(
          getHubSpotStandaloneUrl(lang),
          window.location.search,
          preservedAttributionExtras(),
        );

  useEffect(() => {
    router.prefetch(`/${city.slug}/${otherLang(lang)}`);
    pushEvent("form_ready", { city: city.slug, lang, form_mode: "native_api" });
  }, [router, city.slug, lang]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting) return;

    const nextErrors: FieldErrors = {};
    if (!firstName.trim()) nextErrors.firstName = formCopy.errFirst;
    if (!lastName.trim()) nextErrors.lastName = formCopy.errLast;
    if (!isValidPhone(phone)) nextErrors.phone = formCopy.errPhone;
    if (!isValidEmail(email.trim())) nextErrors.email = formCopy.errEmail;
    if (!consent) nextErrors.consent = formCopy.errConsent;
    setErrors(nextErrors);
    setSubmitFailed(false);
    if (Object.keys(nextErrors).length > 0) return;

    setSubmitting(true);
    const result = await submitLead({
      firstName,
      lastName,
      phone,
      email,
      message,
      consent,
      lang,
      city: city.slug,
      pageName: `${city.name} ${lang === "es" ? "ES" : "EN"} consultation`,
      communicationConsentText: formCopy.consentCheckbox,
      processingConsentText: formCopy.processingNote,
    });
    setSubmitting(false);

    if (!result.ok) {
      setSubmitFailed(true);
      return;
    }

    pushHubSpotFormSubmission(
      formId,
      getFormLanguageLabel(lang),
      result.submissionId!,
    );
    pushEvent("form_submit", { city: city.slug, lang, form_mode: "native_api" });
    const thankYouPath = appendPreservedQueryParams(
      getThankYouPath(lang),
      window.location.search,
      preservedAttributionExtras({ city: city.slug, language: lang }),
    );
    router.push(thankYouPath);
  }

  if (!configured) {
    return (
      <div
        id="lead-form"
        className="ela-hubspot-form mx-auto w-full max-w-[480px] scroll-mt-4 overflow-hidden rounded-[14px] border border-white/15 bg-white shadow-[0_14px_36px_rgba(0,0,0,0.28)]"
      >
        <div className="bg-[var(--navy)] px-4 pb-3.5 pt-4 sm:px-5 sm:pb-4 sm:pt-5">
          <div className="mb-2.5 h-1 w-10 rounded-full bg-[var(--gold)]" aria-hidden />
          <h2 className="text-[1.15rem] font-extrabold tracking-tight text-white sm:text-xl">
            {formCopy.title}
          </h2>
        </div>
        <div className="px-4 py-4 sm:px-5">
          <div className="rounded-xl border border-dashed border-amber-300 bg-amber-50 p-4 text-sm text-amber-950">
            <p className="font-semibold">{formCopy.loadError}</p>
            <p className="mt-2">
              <TrackedTelLink
                location="form_error"
                className="font-semibold text-[var(--navy)] underline underline-offset-2"
              >
                {FIRM.phoneDisplay}
              </TrackedTelLink>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      id="lead-form"
      className="ela-hubspot-form mx-auto w-full max-w-[480px] scroll-mt-4 overflow-hidden rounded-[14px] border border-white/15 bg-white shadow-[0_14px_36px_rgba(0,0,0,0.28)]"
    >
      <div className="bg-[var(--navy)] px-4 pb-3.5 pt-4 sm:px-5 sm:pb-4 sm:pt-5">
        <div className="mb-2.5 h-1 w-10 rounded-full bg-[var(--gold)]" aria-hidden />
        <h2 className="text-[1.15rem] font-extrabold tracking-tight text-white sm:text-xl">
          {formCopy.title}
        </h2>
        <p className="mt-1 text-[13px] leading-snug text-white/80 sm:text-sm">
          {formCopy.subtitle(city.name)}
        </p>
      </div>

      <form
        className="ela-native-form px-4 pb-4 pt-3.5 sm:px-5 sm:pb-5 sm:pt-4"
        onSubmit={onSubmit}
        noValidate
      >
        <div className="ela-native-form__row ela-native-form__row--split">
          <div className="ela-native-form__field">
            <label htmlFor={`${baseId}-first`}>
              {formCopy.firstName}
              <span aria-hidden="true">*</span>
            </label>
            <input
              id={`${baseId}-first`}
              name="firstname"
              autoComplete="given-name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              aria-invalid={Boolean(errors.firstName)}
              aria-describedby={
                errors.firstName ? `${baseId}-first-err` : undefined
              }
            />
            {errors.firstName ? (
              <p id={`${baseId}-first-err`} className="ela-native-form__error" role="alert">
                {errors.firstName}
              </p>
            ) : null}
          </div>
          <div className="ela-native-form__field">
            <label htmlFor={`${baseId}-last`}>
              {formCopy.lastName}
              <span aria-hidden="true">*</span>
            </label>
            <input
              id={`${baseId}-last`}
              name="lastname"
              autoComplete="family-name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              aria-invalid={Boolean(errors.lastName)}
              aria-describedby={
                errors.lastName ? `${baseId}-last-err` : undefined
              }
            />
            {errors.lastName ? (
              <p id={`${baseId}-last-err`} className="ela-native-form__error" role="alert">
                {errors.lastName}
              </p>
            ) : null}
          </div>
        </div>

        <div className="ela-native-form__field">
          <label htmlFor={`${baseId}-phone`}>
            {formCopy.phone}
            <span aria-hidden="true">*</span>
          </label>
          <input
            id={`${baseId}-phone`}
            name="phone"
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            aria-invalid={Boolean(errors.phone)}
            aria-describedby={errors.phone ? `${baseId}-phone-err` : undefined}
          />
          {errors.phone ? (
            <p id={`${baseId}-phone-err`} className="ela-native-form__error" role="alert">
              {errors.phone}
            </p>
          ) : null}
        </div>

        <div className="ela-native-form__field">
          <label htmlFor={`${baseId}-email`}>
            {formCopy.email}
            <span aria-hidden="true">*</span>
          </label>
          <input
            id={`${baseId}-email`}
            name="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            aria-invalid={Boolean(errors.email)}
            aria-describedby={errors.email ? `${baseId}-email-err` : undefined}
          />
          {errors.email ? (
            <p id={`${baseId}-email-err`} className="ela-native-form__error" role="alert">
              {errors.email}
            </p>
          ) : null}
        </div>

        <div className="ela-native-form__field">
          <label htmlFor={`${baseId}-message`}>{formCopy.whatHappened}</label>
          <textarea
            id={`${baseId}-message`}
            name="message"
            rows={4}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
        </div>

        <p className="ela-native-form__note">{formCopy.consentIntro}</p>

        <label className="ela-native-form__consent" htmlFor={`${baseId}-consent`}>
          <input
            id={`${baseId}-consent`}
            name="consent"
            type="checkbox"
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
            aria-invalid={Boolean(errors.consent)}
            aria-describedby={
              errors.consent ? `${baseId}-consent-err` : undefined
            }
          />
          <span>
            {formCopy.consentCheckbox}
            <span aria-hidden="true">*</span>
          </span>
        </label>
        {errors.consent ? (
          <p id={`${baseId}-consent-err`} className="ela-native-form__error" role="alert">
            {errors.consent}
          </p>
        ) : null}

        <p className="ela-native-form__note">
          {formCopy.privacyNoteBefore}{" "}
          <a href={MICROSITE.privacyPath}>{formCopy.privacyLinkLabel}</a>
          {formCopy.privacyNoteAfter}
        </p>
        <p className="ela-native-form__note">{formCopy.processingNote}</p>

        {submitFailed ? (
          <div className="ela-native-form__fail" role="alert">
            <p className="font-semibold">{formCopy.genericError}</p>
            <p className="mt-1.5">
              <TrackedTelLink
                location="form_submit_error"
                className="font-semibold text-[var(--navy)] underline underline-offset-2"
              >
                {FIRM.phoneDisplay}
              </TrackedTelLink>
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
        ) : null}

        <button type="submit" className="ela-native-form__submit" disabled={submitting}>
          {submitting ? formCopy.submitting : formCopy.submit}
        </button>
      </form>
    </div>
  );
}
