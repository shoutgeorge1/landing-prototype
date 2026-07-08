import type { Step } from "@/lib/copy";

interface ThreeStepsProps {
  title: string;
  steps: Step[];
}

export function ThreeSteps({ title, steps }: ThreeStepsProps) {
  return (
    <section className="bg-slate-50 px-5 py-16">
      <div className="mx-auto max-w-5xl">
        <h2 className="text-center text-[26px] font-extrabold text-[var(--navy)] sm:text-3xl">
          {title}
        </h2>
        <div className="mx-auto mt-3 h-1 w-12 rounded-full bg-[var(--gold)]" />
        <ol className="mt-10 space-y-5">
          {steps.map((step, i) => (
            <li
              key={step.title}
              className="flex gap-5 rounded-2xl border-2 border-slate-200 bg-white p-6 shadow-sm"
            >
              <span className="flex h-12 w-12 flex-none items-center justify-center rounded-full bg-[var(--gold)] text-xl font-extrabold text-[var(--navy)]">
                {i + 1}
              </span>
              <div>
                <h3 className="text-lg font-bold text-[var(--navy)]">{step.title}</h3>
                <p className="mt-2 text-[17px] leading-relaxed text-slate-700">{step.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
