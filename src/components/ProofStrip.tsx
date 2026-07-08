interface ProofStripProps {
  title: string;
  googleRating: string;
  googleReviews: string;
  yelpLabel: string;
  points: string[];
}

function Stars() {
  return (
    <div aria-label="4.8 out of 5 stars" className="flex justify-center gap-1 text-[var(--gold)]">
      {Array.from({ length: 5 }).map((_, i) => (
        <svg key={i} aria-hidden viewBox="0 0 20 20" fill="currentColor" className="h-6 w-6">
          <path d="M10 15.27 16.18 19l-1.64-7.03L20 7.24l-7.19-.61L10 0 7.19 6.63 0 7.24l5.46 4.73L3.82 19z" />
        </svg>
      ))}
    </div>
  );
}

export function ProofStrip({
  title,
  googleRating,
  googleReviews,
  yelpLabel,
  points,
}: ProofStripProps) {
  return (
    <section className="bg-white px-5 py-10">
      <div className="mx-auto max-w-4xl">
        <p className="text-center text-sm font-bold uppercase tracking-widest text-slate-500">
          {title}
        </p>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {/* Google proof (approved figures) */}
          <div className="flex flex-col items-center gap-2 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/images/google-logo.svg"
              alt="Google"
              width={120}
              height={40}
              className="h-8 w-auto object-contain"
            />
            <Stars />
            <p className="text-lg font-extrabold text-[var(--navy)]">{googleRating}</p>
            <p className="text-base font-semibold text-slate-600">{googleReviews}</p>
          </div>

          {/* Yelp proof (soft language, no exact rating) */}
          <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/images/yelp-logo.png"
              alt="Yelp"
              width={80}
              height={80}
              className="h-12 w-12 rounded-lg object-contain"
            />
            <p className="text-lg font-extrabold text-[var(--navy)]">{yelpLabel}</p>
          </div>
        </div>

        <ul className="mt-6 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-base font-semibold text-[var(--navy)]">
          {points.map((point) => (
            <li key={point} className="flex items-center gap-2">
              <span aria-hidden className="text-[var(--gold)]">
                &#10003;
              </span>
              {point}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
