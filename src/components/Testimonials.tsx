import { TESTIMONIALS } from "@/lib/testimonials";

interface TestimonialsProps {
  title: string;
  intro: string;
  more: string;
}

// Feature three of the strongest, concise real reviews (mobile-first).
const FEATURED_NAMES = ["Teresa Delgado", "Domonic Grisson", "Joshua Cornish"];
const FEATURED = FEATURED_NAMES.map((name) =>
  TESTIMONIALS.find((t) => t.name === name),
).filter((t): t is (typeof TESTIMONIALS)[number] => Boolean(t));

function Stars() {
  return (
    <div aria-label="5 out of 5 stars" className="flex gap-1 text-[var(--gold)]">
      {Array.from({ length: 5 }).map((_, i) => (
        <svg key={i} aria-hidden viewBox="0 0 20 20" fill="currentColor" className="h-5 w-5">
          <path d="M10 15.27 16.18 19l-1.64-7.03L20 7.24l-7.19-.61L10 0 7.19 6.63 0 7.24l5.46 4.73L3.82 19z" />
        </svg>
      ))}
    </div>
  );
}

export function Testimonials({ title, intro, more }: TestimonialsProps) {
  return (
    <section className="bg-white px-5 py-16">
      <div className="mx-auto max-w-5xl">
        <h2 className="text-center text-2xl font-bold text-[var(--navy)] sm:text-3xl">{title}</h2>
        <p className="mx-auto mt-3 max-w-2xl text-center text-base text-slate-600">{intro}</p>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {FEATURED.map((t) => (
            <figure
              key={t.name}
              className="flex h-full flex-col rounded-2xl border border-slate-200 bg-slate-50 p-6"
            >
              <Stars />
              <blockquote className="mt-4 flex-1 text-base leading-relaxed text-slate-800">
                &ldquo;{t.quote}&rdquo;
              </blockquote>
              <figcaption className="mt-4 text-base font-semibold text-[var(--navy)]">
                {t.name}
              </figcaption>
            </figure>
          ))}
        </div>
        <p className="mt-8 text-center text-base font-medium text-slate-600">{more}</p>
      </div>
    </section>
  );
}
