"use client";

import { FIRM } from "@/lib/content";
import { pushEvent } from "@/lib/tracking";

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
          onClick={() => pushEvent("phone_click", { location: "sticky_mobile" })}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--gold)] px-4 py-4 text-lg font-bold text-[var(--navy)]"
          aria-label={`${label} — ${FIRM.name}`}
        >
          <span aria-hidden className="phone-pulse text-xl">
            &#9742;
          </span>
          {label}
        </a>
      </div>
    </>
  );
}
