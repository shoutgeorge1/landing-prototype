import Image from "next/image";
import type { Metadata } from "next";
import { BRAND_IMAGES } from "@/lib/content";
import { COPY } from "@/lib/copy";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { ProofStrip } from "@/components/ProofStrip";
import { TrustBadges } from "@/components/TrustBadges";
import { TrustBar } from "@/components/TrustBar";
import { Disclaimer } from "@/components/Disclaimer";

/* Landing CTAs use plain <a> for a full navigation into city landing pages. */
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
  const copy = COPY.en;

  return (
    <main className="overflow-x-hidden">
      {/* Hero — same navy header treatment as landing pages */}
      <section className="bg-[var(--navy)] px-5 pb-12 pt-6 text-white sm:px-6 sm:pb-14 sm:pt-8">
        <div className="mx-auto max-w-6xl">
          <SiteHeader
            logoHref="/"
            actions={
              <>
                <nav
                  aria-label="Primary"
                  className="hidden items-center gap-5 text-sm font-medium text-white/85 lg:flex"
                >
                  <a href="#workplace-issues" className="hover:text-white">
                    Workplace Issues
                  </a>
                  <a href="#how-it-works" className="hover:text-white">
                    How It Works
                  </a>
                  <a href="#get-help" className="hover:text-white">
                    Get Help
                  </a>
                </nav>
                <a
                  href="/bakersfield/en"
                  className="rounded-md bg-[var(--gold)] px-3 py-2 text-xs font-bold text-[var(--navy)] transition-opacity hover:opacity-95 sm:px-4 sm:text-sm"
                >
                  Request a Case Review
                </a>
              </>
            }
          />

          <div className="mt-8 flex flex-col gap-8 lg:mt-10 lg:grid lg:grid-cols-2 lg:items-center lg:gap-12">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--gold)] sm:text-sm">
                California Employment Law Support
              </p>
              <h1 className="mt-4 text-[28px] font-extrabold leading-[1.15] sm:text-4xl lg:text-5xl">
                Get Help Understanding Your Workplace Rights
              </h1>
              <p className="mt-4 text-base leading-relaxed text-white/90 sm:text-lg">
                If you believe you were wrongfully terminated, discriminated
                against, harassed, retaliated against, or denied wages, you can
                submit your information for review.
              </p>
              <div className="mt-6">
                <TrustBar points={copy.heroBullets} tone="dark" />
              </div>
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

            <div className="mx-auto w-full max-w-[280px] sm:max-w-[320px] lg:mx-0 lg:max-w-[380px]">
              <Image
                src={BRAND_IMAGES.attorneyHero}
                alt={BRAND_IMAGES.alt.attorney}
                width={520}
                height={650}
                priority
                className="h-auto w-full object-contain"
                sizes="(max-width: 1024px) 320px, 380px"
              />
            </div>
          </div>
        </div>
      </section>

      <ProofStrip
        title={copy.proofTitle}
        googleRating={copy.proofGoogleRating}
        googleReviews={copy.proofGoogleReviews}
        yelpLabel={copy.proofYelp}
        points={copy.proofPoints}
      />

      <TrustBadges
        title={copy.trustBadgesTitle}
        membershipsTitle={copy.trustMembershipsTitle}
      />

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

      <Disclaimer text={copy.disclaimerGeneric} />
      <SiteFooter
        officeTitle={copy.footerOfficeTitle}
        contactTitle={copy.footerContactTitle}
        disclaimer={copy.footerDisclaimer}
      />
    </main>
  );
}
