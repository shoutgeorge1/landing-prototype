import { PRIMARY_BADGES, MEMBERSHIP_BADGES } from "@/lib/badges";

interface TrustBadgesProps {
  title: string;
  membershipsTitle: string;
  tone?: "light" | "muted";
  showMemberships?: boolean;
}

export function TrustBadges({
  title,
  membershipsTitle,
  tone = "light",
  showMemberships = true,
}: TrustBadgesProps) {
  const bg = tone === "muted" ? "bg-slate-50" : "bg-white";
  return (
    <section className={`${bg} px-5 py-10`}>
      <div className="mx-auto max-w-5xl">
        <p className="text-center text-sm font-semibold uppercase tracking-widest text-slate-500">
          {title}
        </p>

        {/* Primary strip: square / circular badges (mobile-friendly, compact) */}
        <ul className="mt-6 flex flex-wrap items-center justify-center gap-x-6 gap-y-5 sm:gap-x-8">
          {PRIMARY_BADGES.map((badge) => (
            <li key={badge.src} className="flex items-center justify-center">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={badge.src}
                alt={badge.alt}
                title={badge.label}
                width={badge.width}
                height={badge.height}
                loading="lazy"
                className="h-16 w-auto object-contain sm:h-20"
              />
            </li>
          ))}
        </ul>

        {showMemberships && (
          <>
            {/* Secondary row: rectangular wordmark memberships, de-emphasized */}
            <p className="mt-9 text-center text-xs font-semibold uppercase tracking-widest text-slate-400">
              {membershipsTitle}
            </p>
            <ul className="mt-4 flex flex-wrap items-center justify-center gap-x-10 gap-y-5 opacity-80">
              {MEMBERSHIP_BADGES.map((badge) => (
                <li key={badge.src} className="flex items-center justify-center">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={badge.src}
                    alt={badge.alt}
                    title={badge.label}
                    width={badge.width}
                    height={badge.height}
                    loading="lazy"
                    className="h-9 w-auto object-contain sm:h-11"
                  />
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </section>
  );
}
