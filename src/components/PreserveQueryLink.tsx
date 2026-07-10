"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useSearchParams } from "next/navigation";
import { startTransition, Suspense, useCallback } from "react";

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
  const router = useRouter();
  const searchParams = useSearchParams();
  const query = searchParams.toString();
  const resolvedHref = query ? `${href}?${query}` : href;

  const onClick = useCallback(
    (event: React.MouseEvent<HTMLAnchorElement>) => {
      if (
        event.defaultPrevented ||
        event.button !== 0 ||
        event.metaKey ||
        event.altKey ||
        event.ctrlKey ||
        event.shiftKey
      ) {
        return;
      }
      event.preventDefault();
      startTransition(() => {
        router.push(resolvedHref);
      });
    },
    [resolvedHref, router],
  );

  const onPointerEnter = useCallback(() => {
    router.prefetch(resolvedHref);
  }, [resolvedHref, router]);

  return (
    <Link
      href={resolvedHref}
      className={className}
      hrefLang={hrefLang}
      prefetch
      onClick={onClick}
      onPointerEnter={onPointerEnter}
    >
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
        <Link href={props.href} className={props.className} hrefLang={props.hrefLang} prefetch>
          {props.children}
        </Link>
      }
    >
      <PreserveQueryLinkInner {...props} />
    </Suspense>
  );
}
