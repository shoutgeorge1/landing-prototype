interface ProblemSectionProps {
  title: string;
  body: string[];
}

export function ProblemSection({ title, body }: ProblemSectionProps) {
  return (
    <section className="bg-white px-6 py-16">
      <div className="mx-auto max-w-3xl">
        <h2 className="text-2xl font-bold text-[var(--navy)] sm:text-3xl">{title}</h2>
        <div className="mt-5 space-y-4 text-lg leading-relaxed text-slate-700">
          {body.map((paragraph, i) => (
            <p key={i}>{paragraph}</p>
          ))}
        </div>
      </div>
    </section>
  );
}
