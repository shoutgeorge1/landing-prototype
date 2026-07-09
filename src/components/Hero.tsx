import Image from "next/image";
import { BRAND_IMAGES, FIRM } from "@/lib/content";
import { otherLang, type City, type Lang } from "@/lib/cities";
import type { Copy } from "@/lib/copy";
import { PhoneCTA } from "./PhoneCTA";
import { TrustBar } from "./TrustBar";
import { HubSpotForm } from "./HubSpotForm";
import { PreserveQueryLink } from "./PreserveQueryLink";

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
        <div className="flex items-center justify-between gap-3 sm:gap-4">
          <div className="min-w-0 shrink">
            <Image
              src={BRAND_IMAGES.logoWhiteLong}
              alt={BRAND_IMAGES.alt.logo}
              width={320}
              height={64}
              priority
              className="h-7 w-auto max-w-[11rem] sm:h-9 sm:max-w-none"
            />
          </div>
          <div className="flex shrink-0 items-center gap-2 sm:gap-3">
            <PreserveQueryLink
              href={`/${city.slug}/${alt}`}
              className="rounded-md border border-white/30 px-2.5 py-1.5 text-xs font-semibold text-white hover:bg-white/10 sm:px-3 sm:text-sm"
              hrefLang={alt}
            >
              {copy.switchLangLabel}
            </PreserveQueryLink>
            <a
              href={`tel:${FIRM.phoneTel}`}
              className="hidden text-base font-bold text-white sm:block"
            >
              {FIRM.phoneDisplay}
            </a>
          </div>
        </div>

        {/* Mobile: headline → form → bullets+call. Desktop: two-column */}
        <div className="mt-6 flex flex-col gap-5 sm:mt-8 sm:gap-6 lg:grid lg:grid-cols-2 lg:items-start lg:gap-10">
          <div className="lg:col-start-1 lg:row-start-1">
            <h1 className="text-[28px] font-extrabold leading-[1.15] sm:text-4xl lg:text-5xl">
              {copy.headline(city.name)}
            </h1>
            <p className="mt-3 text-base leading-relaxed text-white/90 sm:text-lg">
              {copy.subheadline}
            </p>
            <div className="mt-4 max-w-[200px] sm:max-w-[220px] lg:mt-5 lg:max-w-[260px]">
              <Image
                src={BRAND_IMAGES.attorneyHero}
                alt={BRAND_IMAGES.alt.attorney}
                width={520}
                height={650}
                className="h-auto w-full object-contain"
                sizes="(max-width: 640px) 200px, 260px"
              />
            </div>
          </div>

          <div className="lg:col-start-2 lg:row-span-2 lg:row-start-1">
            <HubSpotForm city={city} lang={lang} />
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
