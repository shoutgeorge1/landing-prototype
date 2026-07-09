"use client";

import { pushEvent } from "@/lib/tracking";

interface ScrollToFormButtonProps {
  location: string;
  className?: string;
  children: React.ReactNode;
}

export function ScrollToFormButton({
  location,
  className = "",
  children,
}: ScrollToFormButtonProps) {
  function handleClick() {
    pushEvent("cta_click", { location, target: "lead_form" });
    const el = document.getElementById("lead-form");
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: window.innerWidth < 1024 ? "center" : "start" });
      const firstField = el.querySelector<HTMLInputElement>("input, textarea");
      firstField?.focus({ preventScroll: true });
    }
  }

  return (
    <button type="button" onClick={handleClick} className={className}>
      {children}
    </button>
  );
}
