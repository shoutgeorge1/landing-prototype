import { PhoneCTA } from "./PhoneCTA";
import { ScrollToFormButton } from "./ScrollToFormButton";

interface FinalStopCTAProps {
  title: string;
  body: string;
  urgency: string;
  note: string;
  callLabel: string;
  formLabel: string;
}

function StopSign() {
  return (
    <div className="stop-sign-pulse mx-auto mb-6 flex h-[88px] w-[88px] items-center justify-center sm:h-24 sm:w-24">
      <svg
        aria-hidden
        viewBox="0 0 100 100"
        className="h-full w-full drop-shadow-[0_4px_12px_rgba(0,0,0,0.4)]"
      >
        <polygon
          points="50,4 78,14 96,42 96,58 78,86 50,96 22,86 4,58 4,42 22,14"
          fill="#DC2626"
          stroke="#991B1B"
          strokeWidth="2"
        />
        <text
          x="50"
          y="56"
          textAnchor="middle"
          fill="white"
          fontSize="22"
          fontWeight="800"
          fontFamily="Arial, Helvetica, sans-serif"
        >
          STOP
        </text>
      </svg>
    </div>
  );
}

export function FinalStopCTA({
  title,
  body,
  urgency,
  note,
  callLabel,
  formLabel,
}: FinalStopCTAProps) {
  return (
    <section className="relative overflow-hidden border-y-4 border-[var(--gold)] bg-[var(--navy-800)] px-5 py-16 text-center text-white shadow-[inset_0_0_60px_rgba(231,190,2,0.08)]">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(231,190,2,0.12)_0%,transparent_70%)]" />
      <div className="relative mx-auto max-w-2xl">
        <StopSign />
        <h2 className="text-[28px] font-extrabold leading-tight sm:text-3xl">{title}</h2>
        <p className="mt-5 text-[17px] leading-relaxed text-white/90">{body}</p>
        <p className="mt-4 text-base font-semibold text-[var(--gold)]">{urgency}</p>

        <div className="arrow-bounce mx-auto mt-6 text-[var(--gold)]" aria-hidden>
          <svg viewBox="0 0 24 24" fill="currentColor" className="mx-auto h-6 w-6">
            <path d="M12 16l-6-6h12l-6 6z" />
          </svg>
        </div>

        <div className="mt-4 flex flex-col items-stretch gap-3 sm:flex-row sm:items-center sm:justify-center">
          <PhoneCTA
            location="final_stop"
            label={callLabel}
            className="cta-glow w-full py-4 text-lg sm:w-auto"
          />
          <ScrollToFormButton
            location="final_stop"
            className="w-full rounded-lg border-2 border-white px-6 py-4 text-lg font-bold text-white transition-colors hover:bg-white/10 sm:w-auto"
          >
            {formLabel}
          </ScrollToFormButton>
        </div>
        <p className="mt-6 text-base font-medium text-white/75">{note}</p>
      </div>
    </section>
  );
}
