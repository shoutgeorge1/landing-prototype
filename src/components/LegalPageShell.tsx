import type { ReactNode } from "react";
import { COPY } from "@/lib/copy";
import { SiteHeader } from "./SiteHeader";
import { SiteFooter } from "./SiteFooter";

interface LegalPageShellProps {
  title: string;
  effectiveDate: string;
  children: ReactNode;
}

export function LegalPageShell({
  title,
  effectiveDate,
  children,
}: LegalPageShellProps) {
  const copy = COPY.en;

  return (
    <main className="overflow-x-hidden">
      <div className="bg-[var(--navy)] px-5 py-6 sm:px-6">
        <div className="mx-auto max-w-6xl">
          <SiteHeader logoHref="/" />
        </div>
      </div>

      <article className="mx-auto max-w-3xl px-5 py-12 sm:px-6 sm:py-16">
        <h1 className="text-3xl font-extrabold text-[var(--navy)] sm:text-4xl">
          {title}
        </h1>
        <p className="mt-3 text-sm text-slate-500">
          Effective date: {effectiveDate}
        </p>
        <div className="legal-prose mt-10 space-y-6 text-[15px] leading-relaxed text-slate-700 [&_h2]:mt-10 [&_h2]:text-xl [&_h2]:font-bold [&_h2]:text-[var(--navy)] [&_ul]:list-disc [&_ul]:space-y-2 [&_ul]:pl-5 [&_a]:font-medium [&_a]:text-[var(--navy)] [&_a]:underline">
          {children}
        </div>
      </article>

      <SiteFooter
        officeTitle={copy.footerOfficeTitle}
        contactTitle={copy.footerContactTitle}
        disclaimer={copy.footerDisclaimer}
      />
    </main>
  );
}
