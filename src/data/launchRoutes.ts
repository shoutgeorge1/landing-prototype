export type PageStatus = "active" | "not_built";
export type FormStatus = "live" | "pending" | "n/a";
export type TrackingStatus = "configured" | "pending" | "n/a";

export interface LaunchRoute {
  priority: number;
  city: string;
  language: "en" | "es";
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
] as const;

/** Internal PPC launch sequence — Bakersfield is active production; others are placeholders. */
export const LAUNCH_ROUTES: LaunchRoute[] = [
  {
    priority: 1,
    city: "Bakersfield",
    language: "en",
    landingPage: "/bakersfield/en",
    thankYouPage: SHARED_THANK_YOU.en,
    pageStatus: "active",
    formStatus: "live",
    trackingStatus: "configured",
    notes: "Production priority — English",
  },
  {
    priority: 2,
    city: "Bakersfield",
    language: "es",
    landingPage: "/bakersfield/es",
    thankYouPage: SHARED_THANK_YOU.es,
    pageStatus: "active",
    formStatus: "live",
    trackingStatus: "configured",
    notes: "Production priority — Spanish",
  },
  {
    priority: 3,
    city: "Lancaster",
    language: "en",
    landingPage: "/lancaster/en",
    thankYouPage: SHARED_THANK_YOU.en,
    pageStatus: "not_built",
    formStatus: "n/a",
    trackingStatus: "n/a",
    notes: "Not Built",
  },
  {
    priority: 4,
    city: "Lancaster",
    language: "es",
    landingPage: "/lancaster/es",
    thankYouPage: SHARED_THANK_YOU.es,
    pageStatus: "not_built",
    formStatus: "n/a",
    trackingStatus: "n/a",
    notes: "Not Built",
  },
  {
    priority: 5,
    city: "Victorville",
    language: "en",
    landingPage: "/victorville/en",
    thankYouPage: SHARED_THANK_YOU.en,
    pageStatus: "not_built",
    formStatus: "n/a",
    trackingStatus: "n/a",
    notes: "Not Built",
  },
  {
    priority: 6,
    city: "Victorville",
    language: "es",
    landingPage: "/victorville/es",
    thankYouPage: SHARED_THANK_YOU.es,
    pageStatus: "not_built",
    formStatus: "n/a",
    trackingStatus: "n/a",
    notes: "Not Built",
  },
  {
    priority: 7,
    city: "Barstow",
    language: "en",
    landingPage: "/barstow/en",
    thankYouPage: SHARED_THANK_YOU.en,
    pageStatus: "not_built",
    formStatus: "n/a",
    trackingStatus: "n/a",
    notes: "Not Built",
  },
  {
    priority: 8,
    city: "Barstow",
    language: "es",
    landingPage: "/barstow/es",
    thankYouPage: SHARED_THANK_YOU.es,
    pageStatus: "not_built",
    formStatus: "n/a",
    trackingStatus: "n/a",
    notes: "Not Built",
  },
  {
    priority: 9,
    city: "Fresno",
    language: "en",
    landingPage: "/fresno/en",
    thankYouPage: SHARED_THANK_YOU.en,
    pageStatus: "not_built",
    formStatus: "n/a",
    trackingStatus: "n/a",
    notes: "Not Built",
  },
  {
    priority: 10,
    city: "Fresno",
    language: "es",
    landingPage: "/fresno/es",
    thankYouPage: SHARED_THANK_YOU.es,
    pageStatus: "not_built",
    formStatus: "n/a",
    trackingStatus: "n/a",
    notes: "Not Built",
  },
  {
    priority: 11,
    city: "Modesto",
    language: "en",
    landingPage: "/modesto/en",
    thankYouPage: SHARED_THANK_YOU.en,
    pageStatus: "not_built",
    formStatus: "n/a",
    trackingStatus: "n/a",
    notes: "Not Built",
  },
  {
    priority: 12,
    city: "Modesto",
    language: "es",
    landingPage: "/modesto/es",
    thankYouPage: SHARED_THANK_YOU.es,
    pageStatus: "not_built",
    formStatus: "n/a",
    trackingStatus: "n/a",
    notes: "Not Built",
  },
];
