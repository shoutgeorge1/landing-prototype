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
    <section className={`${bg} px-5 py-12`}>
      <div className="mx-auto max-w-5xl">
        <p className="text-center text-sm font-bold uppercase tracking-widest text-slate-500">
          {title}
        </p>
        <div className="mx-auto mt-2 h-1 w-12 rounded-full bg-[var(--gold)]" />

        <ul className="mt-8 grid grid-cols-3 place-items-center gap-x-4 gap-y-6 sm:flex sm:flex-wrap sm:justify-center sm:gap-x-8 sm:gap-y-7">
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
                className="h-[72px] w-auto object-contain sm:h-24"
              />
            </li>
          ))}
        </ul>

        {showMemberships && (
          <>
            <p className="mt-10 text-center text-sm font-semibold uppercase tracking-widest text-slate-400">
              {membershipsTitle}
            </p>
            <ul className="mt-5 flex flex-wrap items-center justify-center gap-x-10 gap-y-5 opacity-85">
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
                    className="h-11 w-auto object-contain sm:h-12"
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
