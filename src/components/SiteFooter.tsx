import Image from "next/image";
import { FIRM } from "@/lib/content";

interface SiteFooterProps {
  officeTitle: string;
  contactTitle: string;
  disclaimer: string;
}

export function SiteFooter({ officeTitle, contactTitle, disclaimer }: SiteFooterProps) {
  const { office } = FIRM;
  return (
    <footer className="bg-[var(--navy-800)] px-6 py-12 text-white">
      <div className="mx-auto max-w-6xl">
        <div className="grid gap-8 sm:grid-cols-2">
          <div>
            <Image
              src="/images/logo-white.png"
              alt={FIRM.name}
              width={1024}
              height={242}
              className="h-10 w-auto"
            />
            <p className="mt-4 text-sm font-semibold uppercase tracking-wide text-[var(--gold)]">
              {officeTitle}
            </p>
            <address className="mt-1 text-sm not-italic leading-relaxed text-white/80">
              {office.street}
              <br />
              {office.city}, {office.state} {office.zip}
            </address>
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-[var(--gold)]">
              {contactTitle}
            </p>
            <p className="mt-1 text-sm leading-relaxed text-white/80">
              <a href={`tel:${FIRM.phoneTel}`} className="font-bold text-white hover:underline">
                {FIRM.phoneDisplay}
              </a>
              <br />
              <a href={`mailto:${FIRM.email}`} className="hover:underline">
                {FIRM.email}
              </a>
            </p>
          </div>
        </div>
        <p className="mt-10 border-t border-white/10 pt-6 text-xs leading-relaxed text-white/50">
          {disclaimer}
        </p>
        <p className="mt-4 text-xs text-white/40">
          &copy; {new Date().getFullYear()} {FIRM.name}
        </p>
      </div>
    </footer>
  );
}
