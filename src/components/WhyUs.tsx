interface WhyUsProps {
  title: string;
  items: string[];
  note: string;
}

export function WhyUs({ title, items, note }: WhyUsProps) {
  return (
    <section className="bg-[var(--navy)] px-6 py-16 text-white">
      <div className="mx-auto max-w-5xl">
        <h2 className="text-center text-2xl font-bold sm:text-3xl">{title}</h2>
        <ul className="mx-auto mt-10 grid max-w-4xl gap-5 md:grid-cols-3">
          {items.map((item) => (
            <li key={item} className="rounded-xl border border-white/10 bg-white/5 p-6">
              <span aria-hidden className="text-2xl text-[var(--gold)]">
                &#9670;
              </span>
              <p className="mt-3 text-sm leading-relaxed text-white/90">{item}</p>
            </li>
          ))}
        </ul>
        <p className="mx-auto mt-8 max-w-3xl text-center text-sm leading-relaxed text-white/70">
          {note}
        </p>
      </div>
    </section>
  );
}
