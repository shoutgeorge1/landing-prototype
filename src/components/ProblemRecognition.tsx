interface ProblemRecognitionProps {
  title: string;
  items: string[];
}

export function ProblemRecognition({ title, items }: ProblemRecognitionProps) {
  return (
    <section className="bg-white px-5 py-16">
      <div className="mx-auto max-w-3xl">
        <h2 className="text-center text-[26px] font-extrabold text-[var(--navy)] sm:text-3xl">
          {title}
        </h2>
        <div className="mx-auto mt-3 h-1 w-12 rounded-full bg-[var(--gold)]" />
        <ul className="mt-10 space-y-4">
          {items.map((item) => (
            <li
              key={item}
              className="flex items-start gap-4 rounded-2xl border-2 border-slate-200 bg-white p-5 shadow-sm"
            >
              <span
                aria-hidden
                className="mt-0.5 flex h-8 w-8 flex-none items-center justify-center rounded-full bg-[var(--navy)] text-base font-bold text-[var(--gold)]"
              >
                &#10003;
              </span>
              <span className="text-[17px] font-medium leading-relaxed text-slate-800">{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
