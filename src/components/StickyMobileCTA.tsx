"use client";

import { FIRM } from "@/lib/content";
import { trackPhoneClick } from "@/lib/tracking";
import { PhoneIcon } from "./PhoneIcon";

interface StickyMobileCTAProps {
  label: string;
}

export function StickyMobileCTA({ label }: StickyMobileCTAProps) {
  return (
    <>
      <div aria-hidden className="h-[72px] md:hidden" />
      <div className="fixed inset-x-0 bottom-0 z-50 border-t-2 border-[var(--gold)] bg-[var(--navy)] p-3 shadow-[0_-4px_20px_rgba(0,0,0,0.25)] md:hidden">
        <a
          href={`tel:${FIRM.phoneTel}`}
          onClick={() => trackPhoneClick("sticky_mobile")}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--gold)] px-3 py-3.5 text-base font-bold text-[var(--navy)] sm:px-4 sm:py-4 sm:text-lg"
          aria-label={`${label} — ${FIRM.name}`}
        >
          <PhoneIcon className="phone-pulse h-5 w-5 shrink-0" />
          {label}
        </a>
      </div>
    </>
  );
}
