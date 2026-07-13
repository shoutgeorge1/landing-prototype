"use client";

import type { ReactNode } from "react";
import { FIRM } from "@/lib/content";
import { trackPhoneClick } from "@/lib/tracking";

interface TrackedTelLinkProps {
  location: string;
  className?: string;
  children?: ReactNode;
  "aria-label"?: string;
}

export function TrackedTelLink({
  location,
  className,
  children,
  "aria-label": ariaLabel,
}: TrackedTelLinkProps) {
  return (
    <a
      href={`tel:${FIRM.phoneTel}`}
      onClick={() => trackPhoneClick(location)}
      className={className}
      aria-label={ariaLabel ?? `Call ${FIRM.name} at ${FIRM.phoneDisplay}`}
    >
      {children ?? FIRM.phoneDisplay}
    </a>
  );
}
