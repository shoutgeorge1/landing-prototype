import Image from "next/image";
import { BRAND_IMAGES } from "@/lib/content";
import { otherLang, type City, type Lang } from "@/lib/cities";
import type { Copy } from "@/lib/copy";
import { PhoneCTA } from "./PhoneCTA";
import { TrustBar } from "./TrustBar";
import { HubSpotForm } from "./HubSpotForm";
import { PreserveQueryLink } from "./PreserveQueryLink";
import { SiteHeader } from "./SiteHeader";
import { ScrollToFormButton } from "./ScrollToFormButton";

interface HeroProps {
  city: City;
  lang: Lang;
  copy: Copy;
}

export function Hero({ city, lang, copy }: HeroProps) {
  const alt = otherLang(lang);

  return (
    <section className="bg-[var(--navy)] px-5 pb-10 pt-6 text-white sm:px-6 sm:pb-12 sm:pt-8">
      <div className="mx-auto max-w-6xl">
        <SiteHeader
          actions={
            <PreserveQueryLink
              href={`/${city.slug}/${alt}`}
              className="rounded-md border border-white/30 px-2.5 py-1.5 text-xs font-semibold text-white hover:bg-white/10 sm:px-3 sm:text-sm"
              hrefLang={alt}
            >
              {copy.switchLangLabel}
            </PreserveQueryLink>
          }
        />

        {/* Mobile: headline → copy → CTA → form. Desktop: two-column, form top-aligned. */}
        <div className="mt-5 flex flex-col gap-5 sm:mt-7 sm:gap-6 lg:mt-8 lg:grid lg:grid-cols-2 lg:items-start lg:gap-10">
          <div className="lg:col-start-1 lg:row-start-1">
            <h1 className="text-[26px] font-extrabold leading-[1.15] sm:text-4xl lg:text-5xl">
              {copy.headline(city.name)}
            </h1>
            <p className="mt-3 text-[15px] leading-relaxed text-white/90 sm:text-lg">
              {copy.subheadline}
            </p>

            <div className="mt-5 lg:hidden">
              <ScrollToFormButton
                location="hero_mobile"
                className="cta-glow inline-flex w-full items-center justify-center rounded-[10px] bg-[var(--gold)] px-5 py-3.5 text-base font-extrabold text-[var(--navy)]"
              >
                {copy.ctaPrimary}
              </ScrollToFormButton>
            </div>

            <div className="mt-5 hidden max-w-[240px] lg:mt-6 lg:block lg:max-w-[260px]">
              <Image
                src={BRAND_IMAGES.attorneyHero}
                alt={BRAND_IMAGES.alt.attorney}
                width={520}
                height={650}
                className="h-auto w-full object-contain"
                sizes="260px"
                priority
              />
            </div>
          </div>

          <div className="w-full lg:col-start-2 lg:row-span-2 lg:row-start-1 lg:justify-self-end">
            <HubSpotForm city={city} lang={lang} />
          </div>

          <div className="lg:col-start-1 lg:row-start-2">
            <TrustBar points={copy.heroBullets} tone="dark" />
            <div className="mt-5">
              <PhoneCTA
                location="hero"
                label={copy.ctaCall}
                className="w-full py-3.5 text-base sm:text-lg lg:w-auto lg:py-4 lg:text-xl"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
