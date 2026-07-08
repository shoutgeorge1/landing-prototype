interface ProofStripProps {
  title: string;
  googleRating: string;
  googleReviews: string;
  yelpLabel: string;
  points: string[];
}

function Stars({ label }: { label: string }) {
  return (
    <div aria-label={label} className="flex justify-center gap-1 text-[var(--gold)]">
      {Array.from({ length: 5 }).map((_, i) => (
        <svg key={i} aria-hidden viewBox="0 0 20 20" fill="currentColor" className="h-7 w-7">
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
    <section className="bg-slate-50 px-5 py-12">
      <div className="mx-auto max-w-4xl">
        <p className="text-center text-sm font-bold uppercase tracking-widest text-slate-500">
          {title}
        </p>
        <div className="mx-auto mt-2 h-1 w-12 rounded-full bg-[var(--gold)]" />

        <div className="mt-8 grid gap-5 sm:grid-cols-2">
          <div className="flex flex-col items-center gap-3 rounded-2xl border-2 border-slate-200 bg-white p-7 shadow-md">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/images/google-logo.svg"
              alt="Google"
              width={120}
              height={40}
              className="h-9 w-auto object-contain"
            />
            <Stars label="4.8 out of 5 stars on Google" />
            <p className="text-xl font-extrabold text-[var(--navy)]">{googleRating}</p>
            <p className="text-base font-semibold text-slate-600">{googleReviews}</p>
          </div>

          <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-slate-200 bg-white p-7 shadow-md">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/images/yelp-logo.png"
              alt="Yelp"
              width={80}
              height={80}
              className="h-14 w-14 rounded-lg object-contain"
            />
            <Stars label="Highly rated on Yelp" />
            <p className="text-xl font-extrabold text-[var(--navy)]">{yelpLabel}</p>
          </div>
        </div>

        <ul className="mt-8 flex flex-col items-center gap-3 text-base font-semibold text-[var(--navy)] sm:flex-row sm:flex-wrap sm:justify-center sm:gap-x-8">
          {points.map((point) => (
            <li key={point} className="flex items-center gap-2">
              <span aria-hidden className="text-lg text-[var(--gold)]">
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
