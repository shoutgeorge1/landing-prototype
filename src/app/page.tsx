import Image from "next/image";
import Link from "next/link";
import type { Metadata } from "next";
import { BRAND_IMAGES, FIRM } from "@/lib/content";

/* Landing-page CTAs use plain <a> so the browser does a full load and HubSpot embeds initialize. */
/* eslint-disable @next/next/no-html-link-for-pages */

export const metadata: Metadata = {
  title: "Employment Law Assist | California Employment Law Support",
  description:
    "Get help understanding your workplace rights. If you believe you were wrongfully terminated, discriminated against, harassed, retaliated against, or denied wages, submit your information for review.",
  robots: { index: true, follow: true },
  openGraph: {
    title: "Employment Law Assist | California Employment Law Support",
    description:
      "California employment law support for employees. Request a case review for wrongful termination, discrimination, harassment, retaliation, or unpaid wages.",
    url: "/",
  },
};

const WORKPLACE_ISSUES = [
  {
    title: "Wrongful Termination",
    body: "If you were fired for an unlawful reason, your situation may warrant review.",
  },
  {
    title: "Workplace Discrimination",
    body: "Unequal treatment based on a protected characteristic can violate California law.",
  },
  {
    title: "Workplace Harassment",
    body: "Hostile or abusive conduct at work should not be ignored.",
  },
  {
    title: "Retaliation",
    body: "Punishment for reporting concerns or asserting your rights may be unlawful.",
  },
  {
    title: "Unpaid Wages and Overtime",
    body: "Missed wages, overtime, or break violations can be addressed.",
  },
  {
    title: "Other Workplace Violations",
    body: "If something else felt unlawful at work, you can still request a review.",
  },
] as const;

const STEPS = [
  {
    step: "1",
    title: "Tell Us What Happened",
    body: "Share a brief description of your workplace situation.",
  },
  {
    step: "2",
    title: "Your Information Is Reviewed",
    body: "The team reviews whether your situation may involve a California employment law claim.",
  },
  {
    step: "3",
    title: "Learn About Possible Next Steps",
    body: "If help is available, you will learn what may happen next.",
  },
] as const;

export default function Home() {
  const year = new Date().getFullYear();

  return (
    <main className="overflow-x-hidden">
      {/* Header */}
      <header className="border-b border-slate-200/80 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-4 sm:px-6">
          <Link href="/" className="min-w-0 shrink">
            <Image
              src={BRAND_IMAGES.logoDarkLong}
              alt={BRAND_IMAGES.alt.logo}
              width={320}
              height={64}
              priority
              className="h-8 w-auto max-w-[11rem] sm:h-10 sm:max-w-none"
            />
          </Link>
          <nav
            aria-label="Primary"
            className="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex"
          >
            <a href="#workplace-issues" className="hover:text-[var(--navy)]">
              Workplace Issues
            </a>
            <a href="#how-it-works" className="hover:text-[var(--navy)]">
              How It Works
            </a>
            <a href="#get-help" className="hover:text-[var(--navy)]">
              Get Help
            </a>
          </nav>
          <a
            href="/bakersfield/en"
            className="shrink-0 rounded-md bg-[var(--navy)] px-3.5 py-2 text-sm font-semibold text-white transition-colors hover:bg-[var(--navy-800)] sm:px-4"
          >
            Request a Case Review
          </a>
        </div>
      </header>

      {/* Hero */}
      <section className="relative bg-[var(--navy)] text-white">
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.07]"
          aria-hidden="true"
          style={{
            backgroundImage:
              "radial-gradient(ellipse 80% 60% at 70% 20%, #e7be02 0%, transparent 55%), linear-gradient(165deg, transparent 40%, #0b1c36 100%)",
          }}
        />
        <div className="relative mx-auto max-w-6xl px-5 py-16 sm:px-6 sm:py-20 lg:py-24">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--gold)] sm:text-sm">
            California Employment Law Support
          </p>
          <h1 className="mt-4 max-w-3xl text-[2rem] font-extrabold leading-[1.12] tracking-tight sm:text-5xl lg:text-[3.25rem]">
            Get Help Understanding Your Workplace Rights
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-relaxed text-white/85 sm:text-lg">
            If you believe you were wrongfully terminated, discriminated against,
            harassed, retaliated against, or denied wages, you can submit your
            information for review.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
            <a
              href="/bakersfield/en"
              className="inline-flex items-center justify-center rounded-md bg-[var(--gold)] px-6 py-3.5 text-base font-bold text-[var(--navy)] transition-opacity hover:opacity-95"
            >
              Request a Case Review
            </a>
            <a
              href="/bakersfield/es"
              className="inline-flex items-center justify-center rounded-md border border-white/35 px-6 py-3.5 text-base font-semibold text-white transition-colors hover:bg-white/10"
              hrefLang="es"
            >
              Ver en Español
            </a>
          </div>
        </div>
      </section>

      {/* Workplace issues */}
      <section
        id="workplace-issues"
        className="scroll-mt-20 bg-slate-50 px-5 py-16 sm:px-6 sm:py-20"
      >
        <div className="mx-auto max-w-6xl">
          <h2 className="text-2xl font-bold text-[var(--navy)] sm:text-3xl">
            Workplace Issues We Review
          </h2>
          <p className="mt-3 max-w-2xl text-slate-600">
            Employment Law Assist helps California employees understand whether
            their workplace situation may involve a legal claim.
          </p>
          <ul className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {WORKPLACE_ISSUES.map((item) => (
              <li key={item.title} className="border-t border-[var(--navy)]/15 pt-4">
                <h3 className="text-lg font-semibold text-[var(--navy)]">
                  {item.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                  {item.body}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* How it works */}
      <section
        id="how-it-works"
        className="scroll-mt-20 bg-white px-5 py-16 sm:px-6 sm:py-20"
      >
        <div className="mx-auto max-w-6xl">
          <h2 className="text-2xl font-bold text-[var(--navy)] sm:text-3xl">
            How It Works
          </h2>
          <ol className="mt-10 grid gap-8 sm:grid-cols-3">
            {STEPS.map((item) => (
              <li key={item.step}>
                <span className="text-sm font-bold tracking-wide text-[var(--gold)]">
                  Step {item.step}
                </span>
                <h3 className="mt-2 text-lg font-semibold text-[var(--navy)]">
                  {item.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                  {item.body}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* Final CTA */}
      <section
        id="get-help"
        className="scroll-mt-20 bg-[var(--navy)] px-5 py-16 text-white sm:px-6 sm:py-20"
      >
        <div className="mx-auto max-w-6xl text-center">
          <h2 className="text-2xl font-bold sm:text-3xl">Tell Us What Happened</h2>
          <p className="mx-auto mt-3 max-w-xl text-white/80">
            Start with the Bakersfield campaign pages to request a confidential
            case review.
          </p>
          <div className="mt-8 flex flex-col items-stretch justify-center gap-3 sm:flex-row sm:items-center">
            <a
              href="/bakersfield/en"
              className="inline-flex items-center justify-center rounded-md bg-[var(--gold)] px-6 py-3.5 text-base font-bold text-[var(--navy)] transition-opacity hover:opacity-95"
            >
              Start in English
            </a>
            <a
              href="/bakersfield/es"
              className="inline-flex items-center justify-center rounded-md border border-white/35 px-6 py-3.5 text-base font-semibold text-white transition-colors hover:bg-white/10"
              hrefLang="es"
            >
              Comenzar en Español
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[var(--navy-800)] px-5 py-10 text-white sm:px-6">
        <div className="mx-auto max-w-6xl">
          <p className="text-sm font-semibold">{FIRM.name}</p>
          <p className="mt-4 max-w-3xl text-xs leading-relaxed text-white/50">
            This website provides general information about California employment
            law support and is not legal advice. Submitting information does not
            create an attorney-client relationship. Past results do not guarantee
            a similar outcome.
          </p>
          <p className="mt-6 text-xs text-white/40">
            &copy; {year} {FIRM.name}
          </p>
        </div>
      </footer>
    </main>
  );
}
