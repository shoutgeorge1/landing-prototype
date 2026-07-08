export interface Badge {
  src: string;
  alt: string;
  label: string;
}

// Trust badges shown below the hero and near the final CTA.
// NOTE: Placeholder SVGs live in /public/badges. Replace each file with the
// real award/membership logo (keep the same filename) to go live — the
// component and layout will not need to change.
export const BADGES: Badge[] = [
  {
    src: "/badges/cela.svg",
    label: "CELA",
    alt: "Member, California Employment Lawyers Association (CELA)",
  },
  {
    src: "/badges/state-bar-california.svg",
    label: "State Bar of California",
    alt: "Member, State Bar of California",
  },
  {
    src: "/badges/caala.svg",
    label: "CAALA",
    alt: "Member, Consumer Attorneys Association of Los Angeles (CAALA)",
  },
  {
    src: "/badges/aba.svg",
    label: "American Bar Association",
    alt: "Member, American Bar Association",
  },
  {
    src: "/badges/super-lawyers.svg",
    label: "Super Lawyers",
    alt: "Super Lawyers — Kasim Idrees, Selected 2023",
  },
  {
    src: "/badges/avvo-clients-choice.svg",
    label: "Avvo Clients' Choice",
    alt: "Avvo Clients' Choice — 5 stars",
  },
  {
    src: "/badges/expertise.svg",
    label: "Expertise.com",
    alt: "Expertise.com — Best Litigation Lawyers in Woodland Hills 2026",
  },
  {
    src: "/badges/lead-counsel-verified.svg",
    label: "Lead Counsel Verified",
    alt: "Lead Counsel Verified attorney",
  },
  {
    src: "/badges/loc8nearme.svg",
    label: "Loc8NearMe Recommended",
    alt: "Loc8NearMe Recommended",
  },
];
