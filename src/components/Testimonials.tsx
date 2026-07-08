import { TESTIMONIALS } from "@/lib/testimonials";

interface TestimonialsProps {
  title: string;
  intro: string;
}

function Stars() {
  return (
    <div aria-label="5 out of 5 stars" className="flex gap-0.5 text-[var(--gold)]">
      {Array.from({ length: 5 }).map((_, i) => (
        <svg key={i} aria-hidden viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
          <path d="M10 15.27 16.18 19l-1.64-7.03L20 7.24l-7.19-.61L10 0 7.19 6.63 0 7.24l5.46 4.73L3.82 19z" />
        </svg>
      ))}
    </div>
  );
}

export function Testimonials({ title, intro }: TestimonialsProps) {
  return (
    <section className="bg-white px-6 py-16">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-center text-2xl font-bold text-[var(--navy)] sm:text-3xl">{title}</h2>
        <p className="mx-auto mt-3 max-w-2xl text-center text-slate-600">{intro}</p>
        <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {TESTIMONIALS.map((t) => (
            <figure
              key={t.name}
              className="flex h-full flex-col rounded-xl border border-slate-200 bg-slate-50 p-6"
            >
              <Stars />
              <blockquote className="mt-3 flex-1 text-sm leading-relaxed text-slate-700">
                &ldquo;{t.quote}&rdquo;
              </blockquote>
              <figcaption className="mt-4 text-sm font-semibold text-[var(--navy)]">
                {t.name}
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
