import type { Step } from "@/lib/copy";

interface ThreeStepsProps {
  title: string;
  steps: Step[];
}

export function ThreeSteps({ title, steps }: ThreeStepsProps) {
  return (
    <section className="bg-slate-50 px-6 py-16">
      <div className="mx-auto max-w-5xl">
        <h2 className="text-center text-2xl font-bold text-[var(--navy)] sm:text-3xl">{title}</h2>
        <ol className="mt-10 grid gap-6 md:grid-cols-3">
          {steps.map((step, i) => (
            <li
              key={step.title}
              className="relative rounded-xl border border-slate-200 bg-white p-6 text-center"
            >
              <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[var(--gold)] text-xl font-extrabold text-[var(--navy)]">
                {i + 1}
              </span>
              <h3 className="mt-4 text-lg font-semibold text-[var(--navy)]">{step.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">{step.body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
