"use client";

import { useEffect } from "react";
import Image from "next/image";
import { FIRM } from "@/lib/content";
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
          src={FIRM.logo}
          alt={FIRM.name}
          width={240}
          height={57}
          priority
          className="mb-8 h-12 w-auto brightness-0 invert"
        />
        <h1 className="max-w-2xl text-3xl font-extrabold sm:text-4xl">{copy.thankYouTitle}</h1>
        <p className="mt-4 max-w-xl text-lg text-white/90">{copy.thankYouBody}</p>
        <div className="mt-8">
          <PhoneCTA location="thank_you" label={copy.ctaCall} />
        </div>
        <p className="mt-6 text-sm text-white/70">{copy.thankYouNote}</p>
      </section>
      <Disclaimer text={copy.disclaimerGeneric} />
    </main>
  );
}
