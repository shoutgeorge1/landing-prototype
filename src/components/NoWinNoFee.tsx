interface NoWinNoFeeProps {
  title: string;
  body: string[];
}

export function NoWinNoFee({ title, body }: NoWinNoFeeProps) {
  return (
    <section className="bg-[var(--gold)] px-6 py-14 text-[var(--navy)]">
      <div className="mx-auto max-w-3xl text-center">
        <h2 className="text-2xl font-extrabold tracking-tight sm:text-3xl">{title}</h2>
        <div className="mx-auto mt-5 space-y-4 text-lg font-medium leading-relaxed">
          {body.map((paragraph, i) => (
            <p key={i}>{paragraph}</p>
          ))}
        </div>
      </div>
    </section>
  );
}
