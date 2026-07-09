"use client";

import { FIRM } from "@/lib/content";
import { pushEvent } from "@/lib/tracking";
import { PhoneIcon } from "./PhoneIcon";

interface PhoneCTAProps {
  location: string;
  variant?: "solid" | "outline";
  className?: string;
  label?: string;
}

export function PhoneCTA({
  location,
  variant = "solid",
  className = "",
  label,
}: PhoneCTAProps) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-lg px-6 py-3 text-lg font-bold transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[var(--gold)]";
  const styles =
    variant === "solid"
      ? "bg-[var(--gold)] text-[var(--navy)] hover:brightness-95"
      : "border-2 border-white text-white hover:bg-white/10";

  return (
    <a
      href={`tel:${FIRM.phoneTel}`}
      onClick={() => pushEvent("phone_click", { location })}
      className={`${base} ${styles} ${className}`}
      aria-label={`Call ${FIRM.name} at ${FIRM.phoneDisplay}`}
    >
      <PhoneIcon className="h-5 w-5 shrink-0" />
      {label ?? `Call ${FIRM.phoneDisplay}`}
    </a>
  );
}
