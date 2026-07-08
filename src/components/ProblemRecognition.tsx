interface ProblemRecognitionProps {
  title: string;
  items: string[];
}

export function ProblemRecognition({ title, items }: ProblemRecognitionProps) {
  return (
    <section className="bg-white px-5 py-14">
      <div className="mx-auto max-w-3xl">
        <h2 className="text-center text-2xl font-bold text-[var(--navy)] sm:text-3xl">{title}</h2>
        <ul className="mt-8 space-y-4">
          {items.map((item) => (
            <li
              key={item}
              className="flex items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4"
            >
              <span
                aria-hidden
                className="mt-0.5 flex h-6 w-6 flex-none items-center justify-center rounded-full bg-[var(--navy)] text-sm font-bold text-[var(--gold)]"
              >
                &#10003;
              </span>
              <span className="text-lg leading-relaxed text-slate-800">{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
