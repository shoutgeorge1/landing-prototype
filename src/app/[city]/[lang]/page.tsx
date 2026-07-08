import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { CITIES, LANGS, getCity, isLang } from "@/lib/cities";
import { COPY } from "@/lib/copy";
import { LandingPage } from "@/components/LandingPage";

type RouteParams = { city: string; lang: string };

export function generateStaticParams(): RouteParams[] {
  return CITIES.flatMap((c) => LANGS.map((l) => ({ city: c.slug, lang: l })));
}

export const dynamicParams = false;

export async function generateMetadata({
  params,
}: {
  params: Promise<RouteParams>;
}): Promise<Metadata> {
  const { city: citySlug, lang } = await params;
  const city = getCity(citySlug);
  if (!city || !isLang(lang)) return {};
  const copy = COPY[lang];
  const url = `/${city.slug}/${lang}`;
  return {
    title: copy.seoTitle(city.name),
    description: copy.seoDescription(city.name),
    alternates: {
      canonical: url,
      languages: {
        en: `/${city.slug}/en`,
        es: `/${city.slug}/es`,
      },
    },
    openGraph: {
      title: copy.seoTitle(city.name),
      description: copy.seoDescription(city.name),
      url,
      locale: copy.locale,
      type: "website",
    },
  };
}

export default async function Page({ params }: { params: Promise<RouteParams> }) {
  const { city: citySlug, lang } = await params;
  const city = getCity(citySlug);
  if (!city || !isLang(lang)) notFound();
  return <LandingPage city={city} lang={lang} />;
}
