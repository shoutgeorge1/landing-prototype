import { CITIES, LANGS, type Lang } from "@/lib/cities";

export type PageStatus = "active" | "generated_needs_qa";
export type FormStatus = "live" | "pending" | "n/a";
export type TrackingStatus = "configured" | "pending" | "n/a";

export interface LaunchRoute {
  priority: number;
  city: string;
  language: Lang;
  landingPage: string;
  thankYouPage: string;
  pageStatus: PageStatus;
  formStatus: FormStatus;
  trackingStatus: TrackingStatus;
  notes: string;
}

/** Shared thank-you destinations for all cities. */
export const SHARED_THANK_YOU = {
  en: "/thank-you",
  es: "/gracias",
} as const;

export const GENERAL_LAUNCH_LINKS = [
  { label: "Homepage", href: "/" },
  { label: "English thank-you page", href: SHARED_THANK_YOU.en },
  { label: "Spanish thank-you page", href: SHARED_THANK_YOU.es },
  { label: "Privacy Policy", href: "/privacy" },
  { label: "Terms of Use", href: "/terms" },
] as const;

/**
 * Internal PPC launch sequence — one EN + one ES route per supported city.
 * Bakersfield is active production; other generated routes still need QA.
 */
export const LAUNCH_ROUTES: LaunchRoute[] = CITIES.flatMap((city, cityIndex) =>
  LANGS.map((language, langIndex): LaunchRoute => {
    const isBakersfield = city.slug === "bakersfield";
    const langLabel = language === "en" ? "English" : "Spanish";
    return {
      priority: cityIndex * LANGS.length + langIndex + 1,
      city: city.name,
      language,
      landingPage: `/${city.slug}/${language}`,
      thankYouPage: SHARED_THANK_YOU[language],
      pageStatus: isBakersfield ? "active" : "generated_needs_qa",
      formStatus: "live",
      trackingStatus: isBakersfield ? "configured" : "pending",
      notes: isBakersfield
        ? `Production priority — ${langLabel}`
        : `Generated route — needs QA before spend (${langLabel})`,
    };
  }),
);
