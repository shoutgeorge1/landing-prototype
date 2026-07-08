import { PhoneCTA } from "./PhoneCTA";
import { ScrollToFormButton } from "./ScrollToFormButton";

interface MidCTAProps {
  title: string;
  body: string;
  callLabel: string;
  formLabel: string;
}

export function MidCTA({ title, body, callLabel, formLabel }: MidCTAProps) {
  return (
    <section className="bg-[var(--navy)] px-5 py-14 text-center text-white">
      <div className="mx-auto max-w-2xl">
        <h2 className="text-2xl font-bold sm:text-3xl">{title}</h2>
        <p className="mt-4 text-lg leading-relaxed text-white/90">{body}</p>
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <PhoneCTA location="mid_cta" label={callLabel} className="w-full sm:w-auto" />
          <ScrollToFormButton
            location="mid_cta"
            className="w-full rounded-lg border-2 border-white px-6 py-3 text-lg font-bold text-white transition-colors hover:bg-white/10 sm:w-auto"
          >
            {formLabel}
          </ScrollToFormButton>
        </div>
      </div>
    </section>
  );
}
