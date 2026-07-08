import type { City, Lang } from "@/lib/cities";
import type { Copy } from "@/lib/copy";
import { PhoneCTA } from "./PhoneCTA";
import { ScrollToFormButton } from "./ScrollToFormButton";

interface FinalCTAProps {
  city: City;
  lang: Lang;
  copy: Copy;
}

export function FinalCTA({ city, copy }: FinalCTAProps) {
  return (
    <section className="bg-slate-100 px-5 py-14 text-center">
      <div className="mx-auto max-w-2xl">
        <h2 className="text-[26px] font-extrabold text-[var(--navy)] sm:text-3xl">{copy.finalTitle}</h2>
        <p className="mt-4 text-[17px] leading-relaxed text-slate-700">{copy.finalBody(city.name)}</p>
        <div className="mt-8 flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-center">
          <PhoneCTA location="final_cta" label={copy.ctaCall} className="w-full sm:w-auto" />
          <ScrollToFormButton
            location="final_cta"
            className="inline-flex w-full items-center justify-center rounded-lg border-2 border-[var(--navy)] px-6 py-3.5 text-lg font-bold text-[var(--navy)] transition-colors hover:bg-[var(--navy)] hover:text-white sm:w-auto"
          >
            {copy.ctaPrimary}
          </ScrollToFormButton>
        </div>
        <p className="mt-6 text-base text-slate-600">{copy.finalNote}</p>
      </div>
    </section>
  );
}
