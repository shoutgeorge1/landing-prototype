/** This PPC microsite — separate property from the main firm website. */
export const MICROSITE = {
  host: "help.employmentlawassist.com",
  origin: "https://help.employmentlawassist.com",
  privacyPath: "/privacy",
  termsPath: "/terms",
} as const;

export const FIRM = {
  name: "Employment Law Assist",
  phoneDisplay: "(424) 678-1416",
  phoneTel: "+14246781416",
  email: "info@employmentlawassist.com",
  website: "https://employmentlawassist.com/",
  office: {
    street: "21777 Ventura Blvd, Suite 243",
    city: "Woodland Hills",
    state: "CA",
    zip: "91364",
  },
};

/** Local brand assets under /public/images */
export const BRAND_IMAGES = {
  /** Dark blue long logo — use on light backgrounds */
  logoDarkLong: "/images/ela-logo-dark-long-clear.png",
  /** White long logo — use on navy/dark backgrounds */
  logoWhiteLong: "/images/logo-white.png",
  iconDarkSquare: "/images/ela-icon-dark-square.png",
  attorneyHero: "/images/ela-attorney-hero.png",
  alt: {
    logo: "Employment Law Assist logo",
    icon: "Employment Law Assist icon",
    attorney: "Employment Law Assist attorney",
  },
} as const;
