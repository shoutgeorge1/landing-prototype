import type { Metadata } from "next";
import type { ReactNode } from "react";
import {
  GENERAL_LAUNCH_LINKS,
  LAUNCH_ROUTES,
} from "@/data/launchRoutes";
import { FIRM } from "@/lib/content";

export const metadata: Metadata = {
  title: "Internal PPC Launch Control",
  robots: { index: false, follow: false },
};

function QaLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center rounded-md border border-[var(--navy)] px-3 py-1.5 text-sm font-medium text-[var(--navy)] hover:bg-slate-50"
    >
      {children}
    </a>
  );
}

function StatusBadge({ status }: { status: string }) {
  const isActive = status === "active";
  return (
    <span
      className={`inline-block rounded px-2 py-0.5 text-xs font-semibold uppercase tracking-wide ${
        isActive
          ? "bg-emerald-100 text-emerald-800"
          : "bg-slate-100 text-slate-600"
      }`}
    >
      {isActive ? "Active" : "Not Built"}
    </span>
  );
}

export default function LaunchPage() {
  const bakersfield = LAUNCH_ROUTES.filter((r) => r.city === "Bakersfield");
  const future = LAUNCH_ROUTES.filter((r) => r.city !== "Bakersfield");

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="border-b border-slate-200 bg-white px-6 py-8">
        <div className="mx-auto max-w-4xl">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
            {FIRM.name}
          </p>
          <h1 className="mt-2 text-2xl font-bold text-[var(--navy)] sm:text-3xl">
            Internal PPC Launch Control
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-slate-600">
            Internal campaign, QA, tracking, and deployment links. Not intended
            for prospective clients.
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-4xl space-y-12 px-6 py-10">
        {/* General */}
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            General
          </h2>
          <ul className="mt-4 flex flex-wrap gap-3">
            {GENERAL_LAUNCH_LINKS.map((link) => (
              <li key={link.href}>
                <QaLink href={link.href}>
                  {link.label}: {link.href}
                </QaLink>
              </li>
            ))}
          </ul>
        </section>

        {/* Bakersfield */}
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Bakersfield
          </h2>
          <ul className="mt-4 space-y-4">
            {bakersfield.map((route) => {
              const langLabel = route.language === "en" ? "English" : "Spanish";
              return (
                <li
                  key={route.priority}
                  className="rounded-lg border border-slate-200 bg-white p-4 sm:p-5"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <p className="text-base font-semibold text-[var(--navy)]">
                      {route.city} {langLabel}
                    </p>
                    <StatusBadge status={route.pageStatus} />
                  </div>
                  <div className="mt-4 flex flex-wrap gap-3">
                    <QaLink href={route.landingPage}>
                      Landing: {route.landingPage}
                    </QaLink>
                    <QaLink href={route.thankYouPage}>
                      Thank-you: {route.thankYouPage}
                    </QaLink>
                  </div>
                </li>
              );
            })}
          </ul>
        </section>

        {/* Future cities */}
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Future cities
          </h2>
          <p className="mt-2 text-sm text-slate-500">
            Planned landing routes. All English cities use{" "}
            <code className="text-xs">/thank-you</code>; all Spanish cities use{" "}
            <code className="text-xs">/gracias</code>.
          </p>
          <ul className="mt-4 space-y-3">
            {future.map((route) => {
              const langLabel = route.language === "en" ? "English" : "Spanish";
              return (
                <li
                  key={route.priority}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white px-4 py-3"
                >
                  <div>
                    <p className="text-sm font-semibold text-[var(--navy)]">
                      {route.city} {langLabel}
                    </p>
                    <p className="mt-0.5 font-mono text-xs text-slate-400">
                      {route.landingPage} → {route.thankYouPage}
                    </p>
                  </div>
                  <StatusBadge status={route.pageStatus} />
                </li>
              );
            })}
          </ul>
        </section>
      </div>
    </main>
  );
}
