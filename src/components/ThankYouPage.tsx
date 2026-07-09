"use client";

import { useEffect } from "react";
import Image from "next/image";
import { BRAND_IMAGES, FIRM } from "@/lib/content";
import { COPY } from "@/lib/copy";
import type { Lang } from "@/lib/cities";
import { pushEvent } from "@/lib/tracking";
import { PhoneCTA } from "./PhoneCTA";
import { Disclaimer } from "./Disclaimer";

export function ThankYouPage({ lang }: { lang: Lang }) {
  const copy = COPY[lang];

  useEffect(() => {
    pushEvent("thank_you_view", { lang });
  }, [lang]);

  return (
    <main className="flex min-h-screen flex-col">
      <section className="flex flex-1 flex-col items-center justify-center bg-[var(--navy)] px-6 py-20 text-center text-white">
        <Image
          src={BRAND_IMAGES.logoWhiteLong}
          alt={BRAND_IMAGES.alt.logo}
          width={320}
          height={64}
          priority
          className="mx-auto mb-8 h-10 w-auto"
        />
        <h1 className="max-w-2xl text-3xl font-extrabold sm:text-4xl">{copy.thankYouTitle}</h1>
        <p className="mt-4 max-w-xl text-lg text-white/90">{copy.thankYouBody}</p>
        <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <a
            href={FIRM.website}
            className="inline-flex items-center justify-center rounded-lg border-2 border-white/40 px-6 py-3 text-base font-bold text-white transition-colors hover:bg-white/10"
          >
            {copy.thankYouHomeCta}
          </a>
          <PhoneCTA location="thank_you" label={copy.ctaCall} />
        </div>
        <p className="mt-6 text-sm text-white/70">{copy.thankYouNote}</p>
      </section>
      <Disclaimer text={copy.disclaimerGeneric} />
    </main>
  );
}
