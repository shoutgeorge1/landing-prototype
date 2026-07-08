import Image from "next/image";
import Link from "next/link";
import { FIRM } from "@/lib/content";
import { otherLang, type City, type Lang } from "@/lib/cities";
import type { Copy } from "@/lib/copy";
import { PhoneCTA } from "./PhoneCTA";
import { TrustBar } from "./TrustBar";
import { LeadForm } from "./LeadForm";

interface HeroProps {
  city: City;
  lang: Lang;
  copy: Copy;
}

export function Hero({ city, lang, copy }: HeroProps) {
  const alt = otherLang(lang);
  return (
    <section className="bg-[var(--navy)] px-6 pb-14 pt-8 text-white">
      <div className="mx-auto max-w-6xl">
        <div className="flex items-center justify-between gap-4">
          <Image
            src={FIRM.logo}
            alt={FIRM.name}
            width={220}
            height={52}
            priority
            className="h-11 w-auto brightness-0 invert"
          />
          <div className="flex items-center gap-4">
            <Link
              href={`/${city.slug}/${alt}`}
              className="rounded-md border border-white/30 px-3 py-1 text-xs font-semibold text-white hover:bg-white/10"
              hrefLang={alt}
            >
              {copy.switchLangLabel}
            </Link>
            <a
              href={`tel:${FIRM.phoneTel}`}
              className="hidden text-sm font-bold text-white sm:block"
            >
              {FIRM.phoneDisplay}
            </a>
          </div>
        </div>

        <div className="mt-10 grid gap-10 lg:grid-cols-2">
          <div>
            <h1 className="text-3xl font-extrabold leading-tight sm:text-4xl lg:text-5xl">
              {copy.headline(city.name)}
            </h1>
            <p className="mt-4 text-lg leading-relaxed text-white/90">{copy.subheadline}</p>
            <div className="mt-6">
              <TrustBar points={copy.trustPoints} tone="dark" />
            </div>
            <div className="mt-8">
              <PhoneCTA location="hero" label={copy.ctaCall} />
            </div>
          </div>

          <div className="lg:pl-4">
            <LeadForm city={city} lang={lang} />
          </div>
        </div>
      </div>
    </section>
  );
}
