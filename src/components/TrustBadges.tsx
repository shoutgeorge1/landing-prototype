import { PRIMARY_BADGES, MEMBERSHIP_BADGES } from "@/lib/badges";

interface TrustBadgesProps {
  title: string;
  membershipsTitle: string;
  tone?: "light" | "muted";
}

export function TrustBadges({ title, membershipsTitle, tone = "light" }: TrustBadgesProps) {
  const bg = tone === "muted" ? "bg-slate-50" : "bg-white";
  return (
    <section className={`${bg} px-6 py-10`}>
      <div className="mx-auto max-w-6xl">
        <p className="text-center text-xs font-semibold uppercase tracking-widest text-slate-500">
          {title}
        </p>

        {/* Primary strip: square / circular badges (mobile-friendly) */}
        <ul className="mt-6 flex flex-wrap items-center justify-center gap-x-6 gap-y-6 sm:gap-x-10">
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
                className="h-20 w-auto object-contain sm:h-24"
              />
            </li>
          ))}
        </ul>

        {/* Secondary row: rectangular wordmark memberships, de-emphasized */}
        <p className="mt-10 text-center text-[10px] font-semibold uppercase tracking-widest text-slate-400">
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
                className="h-10 w-auto object-contain sm:h-12"
              />
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
