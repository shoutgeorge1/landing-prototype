interface TrustBarProps {
  points: string[];
  tone?: "light" | "dark";
}

export function TrustBar({ points, tone = "light" }: TrustBarProps) {
  const color = tone === "dark" ? "text-white" : "text-[var(--navy)]";
  return (
    <ul className={`flex flex-col gap-y-2.5 text-base font-semibold sm:flex-row sm:flex-wrap sm:gap-x-6 ${color}`}>
      {points.map((point) => (
        <li key={point} className="flex items-center gap-2">
          <span aria-hidden className="text-lg text-[var(--gold)]">
            &#10003;
          </span>
          {point}
        </li>
      ))}
    </ul>
  );
}
