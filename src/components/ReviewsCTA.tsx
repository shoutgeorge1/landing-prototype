interface ReviewsCTAProps {
  title: string;
  googleLabel: string;
  yelpLabel: string;
}

function Stars() {
  return (
    <div aria-label="5 out of 5 stars" className="flex justify-center gap-1 text-[var(--gold)]">
      {Array.from({ length: 5 }).map((_, i) => (
        <svg key={i} aria-hidden viewBox="0 0 20 20" fill="currentColor" className="h-6 w-6">
          <path d="M10 15.27 16.18 19l-1.64-7.03L20 7.24l-7.19-.61L10 0 7.19 6.63 0 7.24l5.46 4.73L3.82 19z" />
        </svg>
      ))}
    </div>
  );
}

export function ReviewsCTA({ title, googleLabel, yelpLabel }: ReviewsCTAProps) {
  const cards = [
    { src: "/images/google-logo.svg", label: googleLabel },
    { src: "/images/yelp-logo.png", label: yelpLabel },
  ];
  return (
    <section className="bg-slate-50 px-6 py-14">
      <div className="mx-auto max-w-4xl">
        <h2 className="text-center text-2xl font-bold text-[var(--navy)] sm:text-3xl">{title}</h2>
        <div className="mx-auto mt-8 grid max-w-2xl gap-6 sm:grid-cols-2">
          {cards.map((card) => (
            <div
              key={card.label}
              className="flex flex-col items-center gap-3 rounded-xl border border-slate-200 bg-white p-6"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={card.src}
                alt={card.label}
                width={120}
                height={40}
                className="h-8 w-auto object-contain"
              />
              <Stars />
              <p className="text-sm font-semibold text-[var(--navy)]">{card.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
