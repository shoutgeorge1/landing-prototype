interface TrustBarProps {
  points: string[];
  tone?: "light" | "dark";
}

export function TrustBar({ points, tone = "light" }: TrustBarProps) {
  const color = tone === "dark" ? "text-white/90" : "text-[var(--navy)]";
  return (
    <ul className={`flex flex-wrap gap-x-6 gap-y-2 text-sm font-semibold ${color}`}>
      {points.map((point) => (
        <li key={point} className="flex items-center gap-2">
          <span aria-hidden className="text-[var(--gold)]">
            &#10003;
          </span>
          {point}
        </li>
      ))}
    </ul>
  );
}
