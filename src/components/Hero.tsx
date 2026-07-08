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
    <section className="bg-[var(--navy)] px-5 pb-12 pt-6 text-white sm:px-6 sm:pb-14 sm:pt-8">
      <div className="mx-auto max-w-6xl">
        <div className="flex items-center justify-between gap-4">
          <Image
            src="/images/logo-white.png"
            alt={FIRM.name}
            width={1024}
            height={242}
            priority
            className="h-10 w-auto sm:h-11"
          />
          <div className="flex items-center gap-3">
            <Link
              href={`/${city.slug}/${alt}`}
              className="rounded-md border border-white/30 px-3 py-1.5 text-sm font-semibold text-white hover:bg-white/10"
              hrefLang={alt}
            >
              {copy.switchLangLabel}
            </Link>
            <a
              href={`tel:${FIRM.phoneTel}`}
              className="hidden text-base font-bold text-white sm:block"
            >
              {FIRM.phoneDisplay}
            </a>
          </div>
        </div>

        {/* Mobile: headline → form → bullets+call. Desktop: two-column */}
        <div className="mt-8 flex flex-col gap-6 lg:grid lg:grid-cols-2 lg:items-start lg:gap-10">
          <div className="lg:col-start-1 lg:row-start-1">
            <h1 className="text-[32px] font-extrabold leading-[1.15] sm:text-4xl lg:text-5xl">
              {copy.headline(city.name)}
            </h1>
            <p className="mt-3 text-[17px] leading-relaxed text-white/90 sm:text-lg">
              {copy.subheadline}
            </p>
          </div>

          <div className="lg:col-start-2 lg:row-span-2 lg:row-start-1">
            <LeadForm city={city} lang={lang} />
          </div>

          <div className="lg:col-start-1 lg:row-start-2">
            <TrustBar points={copy.heroBullets} tone="dark" />
            <div className="mt-6">
              <PhoneCTA
                location="hero"
                label={copy.ctaCall}
                className="w-full py-4 text-lg sm:text-xl lg:w-auto"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
