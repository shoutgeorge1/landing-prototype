interface DisclaimerProps {
  text: string;
}

export function Disclaimer({ text }: DisclaimerProps) {
  return (
    <section className="bg-slate-100 px-6 py-8">
      <p className="mx-auto max-w-3xl text-center text-xs leading-relaxed text-slate-500">
        {text}
      </p>
    </section>
  );
}
