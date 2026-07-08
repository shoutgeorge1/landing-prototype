"use client";

import { useEffect } from "react";
import { captureUtms } from "@/lib/tracking";

export function UtmCapture() {
  useEffect(() => {
    captureUtms();
  }, []);
  return null;
}
