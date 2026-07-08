import { PhoneCTA } from "./PhoneCTA";
import { ScrollToFormButton } from "./ScrollToFormButton";

interface FinalStopCTAProps {
  title: string;
  body: string;
  note: string;
  callLabel: string;
  formLabel: string;
}

export function FinalStopCTA({ title, body, note, callLabel, formLabel }: FinalStopCTAProps) {
  return (
    <section className="border-y-4 border-[var(--gold)] bg-[var(--navy)] px-5 py-16 text-center text-white">
      <div className="mx-auto max-w-2xl">
        <h2 className="text-[26px] font-extrabold leading-tight sm:text-3xl">{title}</h2>
        <p className="mt-5 text-[17px] leading-relaxed text-white/90">{body}</p>
        <div className="mt-8 flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-center">
          <PhoneCTA location="final_stop" label={callLabel} className="w-full text-lg sm:w-auto" />
          <ScrollToFormButton
            location="final_stop"
            className="w-full rounded-lg border-2 border-white px-6 py-3.5 text-lg font-bold text-white transition-colors hover:bg-white/10 sm:w-auto"
          >
            {formLabel}
          </ScrollToFormButton>
        </div>
        <p className="mt-6 text-base font-medium text-[var(--gold)]">{note}</p>
      </div>
    </section>
  );
}
