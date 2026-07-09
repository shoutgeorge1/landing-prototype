"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

interface PreserveQueryLinkProps {
  href: string;
  className?: string;
  hrefLang?: string;
  children: React.ReactNode;
}

function PreserveQueryLinkInner({
  href,
  className,
  hrefLang,
  children,
}: PreserveQueryLinkProps) {
  const searchParams = useSearchParams();
  const query = searchParams.toString();
  const resolvedHref = query ? `${href}?${query}` : href;

  return (
    <Link href={resolvedHref} className={className} hrefLang={hrefLang}>
      {children}
    </Link>
  );
}

/**
 * Link that keeps the current URL query string (Google Ads tracking params).
 */
export function PreserveQueryLink(props: PreserveQueryLinkProps) {
  return (
    <Suspense
      fallback={
        <Link href={props.href} className={props.className} hrefLang={props.hrefLang}>
          {props.children}
        </Link>
      }
    >
      <PreserveQueryLinkInner {...props} />
    </Suspense>
  );
}
