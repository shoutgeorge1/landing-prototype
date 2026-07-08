interface PracticeAreasProps {
  title: string;
  intro: string;
  items: string[];
}

// Six simple line icons, matched by index to the practiceAreas order:
// 0 Wrongful Termination, 1 Meal & Rest Break, 2 Retaliation,
// 3 Discrimination, 4 Workers' Comp, 5 Harassment.
const ICONS = [
  // Wrongful termination — door/exit
  "M9 3h9a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H9M4 12h11m0 0-3-3m3 3-3 3",
  // Meal & rest break — clock
  "M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z",
  // Retaliation — shield
  "M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6l-7-3Z",
  // Discrimination — people
  "M17 20v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M10 8a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm11 12v-2a4 4 0 0 0-3-3.87M16 4.13A4 4 0 0 1 16 12",
  // Workers' comp — medical cross
  "M12 3h0a2 2 0 0 1 2 2v3h3a2 2 0 0 1 2 2v0a2 2 0 0 1-2 2h-3v3a2 2 0 0 1-2 2h0a2 2 0 0 1-2-2v-3H7a2 2 0 0 1-2-2v0a2 2 0 0 1 2-2h3V5a2 2 0 0 1 2-2Z",
  // Harassment — alert
  "M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z",
];

export function PracticeAreas({ title, intro, items }: PracticeAreasProps) {
  return (
    <section className="bg-white px-6 py-16">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-center text-2xl font-bold text-[var(--navy)] sm:text-3xl">{title}</h2>
        <p className="mx-auto mt-3 max-w-2xl text-center text-slate-600">{intro}</p>
        <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item, i) => (
            <div
              key={item}
              className="group flex items-start gap-4 rounded-xl border border-slate-200 bg-slate-50 p-6 transition-colors hover:border-[var(--gold)]"
            >
              <span className="flex h-12 w-12 flex-none items-center justify-center rounded-lg bg-[var(--navy)] text-[var(--gold)]">
                <svg
                  aria-hidden
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={1.8}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-6 w-6"
                >
                  <path d={ICONS[i % ICONS.length]} />
                </svg>
              </span>
              <div>
                <h3 className="text-lg font-semibold text-[var(--navy)]">{item}</h3>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
