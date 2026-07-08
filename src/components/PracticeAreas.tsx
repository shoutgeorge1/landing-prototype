interface PracticeAreasProps {
  title: string;
  intro: string;
  items: string[];
}

const ICONS = [
  "M9 3h9a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H9M4 12h11m0 0-3-3m3 3-3 3",
  "M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z",
  "M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6l-7-3Z",
  "M17 20v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M10 8a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm11 12v-2a4 4 0 0 0-3-3.87M16 4.13A4 4 0 0 1 16 12",
  "M12 3h0a2 2 0 0 1 2 2v3h3a2 2 0 0 1 2 2v0a2 2 0 0 1-2 2h-3v3a2 2 0 0 1-2 2h0a2 2 0 0 1-2-2v-3H7a2 2 0 0 1-2-2v0a2 2 0 0 1 2-2h3V5a2 2 0 0 1 2-2Z",
  "M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z",
];

export function PracticeAreas({ title, intro, items }: PracticeAreasProps) {
  return (
    <section className="bg-slate-50 px-5 py-16">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-center text-[26px] font-extrabold text-[var(--navy)] sm:text-3xl">
          {title}
        </h2>
        <div className="mx-auto mt-3 h-1 w-12 rounded-full bg-[var(--gold)]" />
        <p className="mx-auto mt-4 max-w-2xl text-center text-[17px] leading-relaxed text-slate-600">
          {intro}
        </p>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item, i) => (
            <div
              key={item}
              className="flex items-center gap-4 rounded-2xl border-2 border-slate-200 bg-white p-5 shadow-sm"
            >
              <span className="flex h-14 w-14 flex-none items-center justify-center rounded-xl bg-[var(--navy)] text-[var(--gold)]">
                <svg
                  aria-hidden
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={1.8}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-7 w-7"
                >
                  <path d={ICONS[i % ICONS.length]} />
                </svg>
              </span>
              <h3 className="text-[17px] font-bold text-[var(--navy)]">{item}</h3>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
