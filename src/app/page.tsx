import Image from "next/image";
import Link from "next/link";
import type { Metadata } from "next";
import { CITIES, LANGS } from "@/lib/cities";
import { BRAND_IMAGES, FIRM } from "@/lib/content";

export const metadata: Metadata = {
  title: "Landing Pages (QA Index)",
  robots: { index: false, follow: false },
};

export default function Home() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <Image
        src={BRAND_IMAGES.logoDarkLong}
        alt={BRAND_IMAGES.alt.logo}
        width={320}
        height={64}
        className="mb-6 h-16 w-auto"
        priority
      />
      <h1 className="text-2xl font-bold text-[var(--navy)]">
        {FIRM.name} &mdash; Bilingual PPC Landing Pages
      </h1>
      <p className="mt-2 text-slate-600">
        Internal QA index (not indexed). Each city has an English and Spanish landing page.
      </p>
      <div className="mt-8 space-y-6">
        {CITIES.map((city) => (
          <div key={city.slug}>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              {city.name}
            </h2>
            <ul className="mt-2 flex flex-wrap gap-3">
              {LANGS.map((lang) => (
                <li key={lang}>
                  <Link
                    href={`/${city.slug}/${lang}`}
                    className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-4 py-2 font-medium text-[var(--navy)] transition-colors hover:bg-slate-50"
                  >
                    /{city.slug}/{lang}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </main>
  );
}
