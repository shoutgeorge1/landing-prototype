export interface Badge {
  src: string;
  alt: string;
  label: string;
  width: number;
  height: number;
}

// Square / circular award badges — the mobile-friendly primary strip.
export const PRIMARY_BADGES: Badge[] = [
  {
    src: "/badges/state-bar.png",
    label: "State Bar of California",
    alt: "Member, State Bar of California",
    width: 400,
    height: 400,
  },
  {
    src: "/badges/avvo.png",
    label: "Avvo Clients' Choice",
    alt: "Avvo Clients' Choice — 5 stars",
    width: 320,
    height: 300,
  },
  {
    src: "/badges/lead-counsel.png",
    label: "Lead Counsel Verified",
    alt: "Lead Counsel Verified attorney",
    width: 300,
    height: 300,
  },
  {
    src: "/badges/expertise.png",
    label: "Expertise.com",
    alt: "Expertise.com — Best Litigation Lawyers in Woodland Hills 2026",
    width: 440,
    height: 340,
  },
  {
    src: "/badges/super-lawyers.png",
    label: "Super Lawyers",
    alt: "Super Lawyers — Kasim Idrees, Selected 2023",
    width: 300,
    height: 230,
  },
  {
    src: "/badges/loc8nearme.png",
    label: "Loc8NearMe Recommended",
    alt: "Loc8NearMe Recommended — Employment Law Assist",
    width: 300,
    height: 300,
  },
];

// Rectangular wordmark memberships — secondary, de-emphasized row.
export const MEMBERSHIP_BADGES: Badge[] = [
  {
    src: "/badges/cela.png",
    label: "CELA",
    alt: "Member, California Employment Lawyers Association (CELA)",
    width: 300,
    height: 300,
  },
  {
    src: "/badges/caala.png",
    label: "CAALA",
    alt: "Member, Consumer Attorneys Association of Los Angeles (CAALA)",
    width: 700,
    height: 180,
  },
  {
    src: "/badges/aba.png",
    label: "American Bar Association",
    alt: "Member, American Bar Association",
    width: 590,
    height: 180,
  },
];
