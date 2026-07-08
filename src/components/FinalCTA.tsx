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
    <section className="bg-slate-100 px-6 py-16 text-center">
      <div className="mx-auto max-w-2xl">
        <h2 className="text-2xl font-bold text-[var(--navy)] sm:text-3xl">{copy.finalTitle}</h2>
        <p className="mt-3 text-slate-600">{copy.finalBody(city.name)}</p>
        <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <PhoneCTA location="final_cta" label={copy.ctaCall} />
          <ScrollToFormButton
            location="final_cta"
            className="inline-flex items-center justify-center rounded-lg border-2 border-[var(--navy)] px-6 py-3 text-lg font-bold text-[var(--navy)] transition-colors hover:bg-[var(--navy)] hover:text-white"
          >
            {copy.ctaPrimary}
          </ScrollToFormButton>
        </div>
        <p className="mt-6 text-sm text-slate-500">{copy.finalNote}</p>
      </div>
    </section>
  );
}
