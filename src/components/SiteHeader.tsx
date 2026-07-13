import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";
import { BRAND_IMAGES, FIRM } from "@/lib/content";

interface SiteHeaderProps {
  /** When set, logo links here (homepage). Landing pages omit this to avoid exit links. */
  logoHref?: string;
  /** Right-side actions (lang switch, nav CTA, etc.) */
  actions?: ReactNode;
  /** Show phone on sm+ (default true) */
  showPhone?: boolean;
}

export function SiteHeader({
  logoHref,
  actions,
  showPhone = true,
}: SiteHeaderProps) {
  const logo = (
    <Image
      src={BRAND_IMAGES.logoWhiteLong}
      alt={BRAND_IMAGES.alt.logo}
      width={480}
      height={96}
      priority
      className="h-11 w-auto max-w-[16rem] sm:h-14 sm:max-w-none"
    />
  );

  return (
    <div className="flex items-center justify-between gap-3 sm:gap-4">
      <div className="min-w-0 shrink">
        {logoHref ? (
          <Link href={logoHref} className="inline-block">
            {logo}
          </Link>
        ) : (
          logo
        )}
      </div>
      <div className="flex shrink-0 items-center gap-2 sm:gap-4">
        {actions}
        {showPhone && (
          <a
            href={`tel:${FIRM.phoneTel}`}
            className="hidden text-base font-bold text-white sm:block sm:text-lg"
          >
            {FIRM.phoneDisplay}
          </a>
        )}
      </div>
    </div>
  );
}
