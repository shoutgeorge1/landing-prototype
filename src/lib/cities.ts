export interface City {
  slug: string;
  name: string;
}

export const CITIES: City[] = [
  // Central Valley
  { slug: "bakersfield", name: "Bakersfield" },
  { slug: "fresno", name: "Fresno" },
  { slug: "stockton", name: "Stockton" },
  { slug: "modesto", name: "Modesto" },
  { slug: "visalia", name: "Visalia" },
  // Inland Empire
  { slug: "riverside", name: "Riverside" },
  { slug: "san-bernardino", name: "San Bernardino" },
  { slug: "fontana", name: "Fontana" },
  { slug: "ontario", name: "Ontario" },
  // High Desert / Antelope Valley
  { slug: "victorville", name: "Victorville" },
  { slug: "lancaster", name: "Lancaster" },
  { slug: "palmdale", name: "Palmdale" },
  // Other high-value markets
  { slug: "salinas", name: "Salinas" },
  { slug: "oxnard", name: "Oxnard" },
];

export const LANGS = ["en", "es"] as const;
export type Lang = (typeof LANGS)[number];

export function getCity(slug: string): City | undefined {
  return CITIES.find((c) => c.slug === slug);
}

export function isLang(value: string): value is Lang {
  return (LANGS as readonly string[]).includes(value);
}

export function otherLang(lang: Lang): Lang {
  return lang === "en" ? "es" : "en";
}
