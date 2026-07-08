import { TESTIMONIALS } from "@/lib/testimonials";

interface TestimonialsProps {
  title: string;
  intro: string;
  more: string;
}

const FEATURED_NAMES = ["Teresa Delgado", "Domonic Grisson", "Joshua Cornish"];
const FEATURED = FEATURED_NAMES.map((name) =>
  TESTIMONIALS.find((t) => t.name === name),
).filter((t): t is (typeof TESTIMONIALS)[number] => Boolean(t));

function Stars() {
  return (
    <div aria-label="5 out of 5 stars" className="flex gap-1.5 text-[var(--gold)]">
      {Array.from({ length: 5 }).map((_, i) => (
        <svg key={i} aria-hidden viewBox="0 0 20 20" fill="currentColor" className="h-6 w-6">
          <path d="M10 15.27 16.18 19l-1.64-7.03L20 7.24l-7.19-.61L10 0 7.19 6.63 0 7.24l5.46 4.73L3.82 19z" />
        </svg>
      ))}
    </div>
  );
}

export function Testimonials({ title, intro, more }: TestimonialsProps) {
  return (
    <section className="bg-white px-5 py-16">
      <div className="mx-auto max-w-3xl">
        <h2 className="text-center text-[26px] font-extrabold text-[var(--navy)] sm:text-3xl">
          {title}
        </h2>
        <div className="mx-auto mt-3 h-1 w-12 rounded-full bg-[var(--gold)]" />
        <p className="mx-auto mt-4 max-w-2xl text-center text-[17px] text-slate-600">{intro}</p>
        <div className="mt-10 space-y-5">
          {FEATURED.map((t) => (
            <figure
              key={t.name}
              className="rounded-2xl border-2 border-slate-200 bg-slate-50 p-6 shadow-sm"
            >
              <Stars />
              <blockquote className="mt-4 text-[17px] leading-relaxed text-slate-800">
                &ldquo;{t.quote}&rdquo;
              </blockquote>
              <figcaption className="mt-4 text-base font-bold text-[var(--navy)]">
                {t.name}
              </figcaption>
            </figure>
          ))}
        </div>
        <p className="mt-8 text-center text-base font-semibold text-slate-600">{more}</p>
      </div>
    </section>
  );
}
