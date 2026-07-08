"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { City, Lang } from "@/lib/cities";
import { COPY } from "@/lib/copy";
import { pushEvent } from "@/lib/tracking";
import { submitLead, type LeadPayload } from "@/lib/submitLead";

interface LeadFormProps {
  city: City;
  lang: Lang;
}

type Fields = Omit<LeadPayload, "citySlug" | "lang">;

const labelClass = "block text-sm font-semibold text-[var(--navy)]";
const inputClass =
  "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-base text-slate-900 outline-none focus:border-[var(--navy)] focus:ring-1 focus:ring-[var(--navy)]";

function isEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function isPhone(value: string): boolean {
  return value.replace(/\D/g, "").length >= 10;
}

export function LeadForm({ city, lang }: LeadFormProps) {
  const router = useRouter();
  const c = COPY[lang].form;
  const [fields, setFields] = useState<Fields>({
    firstName: "",
    lastName: "",
    phone: "",
    email: "",
    city: city.name,
    employer: "",
    whatHappened: "",
    consent: false,
  });
  const [errors, setErrors] = useState<Partial<Record<keyof Fields, string>>>({});
  const [submitting, setSubmitting] = useState(false);
  const startedRef = useRef(false);

  function markStarted() {
    if (!startedRef.current) {
      startedRef.current = true;
      pushEvent("form_start", { city: city.slug, lang });
    }
  }

  function update<K extends keyof Fields>(key: K, value: Fields[K]) {
    setFields((prev) => ({ ...prev, [key]: value }));
  }

  function validate(): boolean {
    const next: Partial<Record<keyof Fields, string>> = {};
    if (!fields.firstName.trim()) next.firstName = c.errFirst;
    if (!fields.lastName.trim()) next.lastName = c.errLast;
    if (!isPhone(fields.phone)) next.phone = c.errPhone;
    if (!isEmail(fields.email)) next.email = c.errEmail;
    if (!fields.city.trim()) next.city = c.errCity;
    if (!fields.whatHappened.trim()) next.whatHappened = c.errWhat;
    if (!fields.consent) next.consent = c.errConsent;
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (submitting) return;
    if (!validate()) return;
    setSubmitting(true);

    const payload: LeadPayload = { ...fields, citySlug: city.slug, lang };
    try {
      await submitLead(payload);
      pushEvent("form_submit", { city: city.slug, lang });
      router.push(`/thank-you?lang=${lang}`);
    } catch {
      setSubmitting(false);
      setErrors({ whatHappened: c.genericError });
    }
  }

  return (
    <form
      id="lead-form"
      onSubmit={handleSubmit}
      onChange={markStarted}
      noValidate
      className="rounded-2xl bg-white p-6 shadow-xl ring-1 ring-slate-200"
    >
      <h2 className="text-xl font-bold text-[var(--navy)]">{c.title}</h2>
      <p className="mt-1 text-sm text-slate-600">{c.subtitle(city.name)}</p>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="firstName" className={labelClass}>
            {c.firstName}
          </label>
          <input
            id="firstName"
            name="firstName"
            autoComplete="given-name"
            className={inputClass}
            value={fields.firstName}
            onFocus={markStarted}
            onChange={(e) => update("firstName", e.target.value)}
            aria-invalid={!!errors.firstName}
          />
          {errors.firstName && <p className="mt-1 text-xs text-red-600">{errors.firstName}</p>}
        </div>
        <div>
          <label htmlFor="lastName" className={labelClass}>
            {c.lastName}
          </label>
          <input
            id="lastName"
            name="lastName"
            autoComplete="family-name"
            className={inputClass}
            value={fields.lastName}
            onChange={(e) => update("lastName", e.target.value)}
            aria-invalid={!!errors.lastName}
          />
          {errors.lastName && <p className="mt-1 text-xs text-red-600">{errors.lastName}</p>}
        </div>
        <div>
          <label htmlFor="phone" className={labelClass}>
            {c.phone}
          </label>
          <input
            id="phone"
            name="phone"
            type="tel"
            autoComplete="tel"
            className={inputClass}
            value={fields.phone}
            onChange={(e) => update("phone", e.target.value)}
            aria-invalid={!!errors.phone}
          />
          {errors.phone && <p className="mt-1 text-xs text-red-600">{errors.phone}</p>}
        </div>
        <div>
          <label htmlFor="email" className={labelClass}>
            {c.email}
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            className={inputClass}
            value={fields.email}
            onChange={(e) => update("email", e.target.value)}
            aria-invalid={!!errors.email}
          />
          {errors.email && <p className="mt-1 text-xs text-red-600">{errors.email}</p>}
        </div>
        <div>
          <label htmlFor="city" className={labelClass}>
            {c.cityLabel}
          </label>
          <input
            id="city"
            name="city"
            autoComplete="address-level2"
            className={inputClass}
            value={fields.city}
            onChange={(e) => update("city", e.target.value)}
            aria-invalid={!!errors.city}
          />
          {errors.city && <p className="mt-1 text-xs text-red-600">{errors.city}</p>}
        </div>
        <div>
          <label htmlFor="employer" className={labelClass}>
            {c.employer} <span className="font-normal text-slate-400">{c.optional}</span>
          </label>
          <input
            id="employer"
            name="employer"
            className={inputClass}
            value={fields.employer}
            onChange={(e) => update("employer", e.target.value)}
          />
        </div>
      </div>

      <div className="mt-4">
        <label htmlFor="whatHappened" className={labelClass}>
          {c.whatHappened}
        </label>
        <textarea
          id="whatHappened"
          name="whatHappened"
          rows={4}
          className={inputClass}
          value={fields.whatHappened}
          onChange={(e) => update("whatHappened", e.target.value)}
          aria-invalid={!!errors.whatHappened}
        />
        {errors.whatHappened && <p className="mt-1 text-xs text-red-600">{errors.whatHappened}</p>}
      </div>

      <div className="mt-4 flex items-start gap-3">
        <input
          id="consent"
          name="consent"
          type="checkbox"
          className="mt-1 h-5 w-5 shrink-0 rounded border-slate-300"
          checked={fields.consent}
          onChange={(e) => update("consent", e.target.checked)}
          aria-invalid={!!errors.consent}
        />
        <label htmlFor="consent" className="text-xs leading-relaxed text-slate-600">
          {c.consent}
        </label>
      </div>
      {errors.consent && <p className="mt-1 text-xs text-red-600">{errors.consent}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="mt-6 w-full rounded-lg bg-[var(--gold)] px-6 py-3.5 text-lg font-bold text-[var(--navy)] transition-colors hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {submitting ? c.submitting : c.submit}
      </button>
    </form>
  );
}
