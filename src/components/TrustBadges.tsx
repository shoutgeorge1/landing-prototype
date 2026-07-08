import { BADGES } from "@/lib/badges";

interface TrustBadgesProps {
  title: string;
  tone?: "light" | "muted";
}

export function TrustBadges({ title, tone = "light" }: TrustBadgesProps) {
  const bg = tone === "muted" ? "bg-slate-50" : "bg-white";
  return (
    <section className={`${bg} px-6 py-10`}>
      <div className="mx-auto max-w-6xl">
        <p className="text-center text-xs font-semibold uppercase tracking-widest text-slate-500">
          {title}
        </p>
        <ul className="mt-6 flex flex-wrap items-center justify-center gap-x-8 gap-y-6">
          {BADGES.map((badge) => (
            <li key={badge.src} className="flex items-center justify-center">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={badge.src}
                alt={badge.alt}
                title={badge.label}
                width={132}
                height={72}
                loading="lazy"
                className="h-16 w-auto object-contain opacity-90 transition-opacity hover:opacity-100"
              />
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
