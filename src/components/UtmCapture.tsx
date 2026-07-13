"use client";

import { useEffect } from "react";
import { captureUtms } from "@/lib/tracking";

/** Capture paid-media attribution on every public page. */
export function UtmCapture() {
  useEffect(() => {
    captureUtms();
  }, []);
  return null;
}
