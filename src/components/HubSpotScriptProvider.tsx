"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { HUBSPOT_EMBED_SCRIPT_URL } from "@/lib/hubspot";

type ScriptStatus = "idle" | "loading" | "ready" | "error";

const HubSpotScriptContext = createContext<ScriptStatus>("idle");

export function useHubSpotScriptStatus(): ScriptStatus {
  return useContext(HubSpotScriptContext);
}

let scriptStatus: ScriptStatus = "idle";
const listeners = new Set<(status: ScriptStatus) => void>();
let loadPromise: Promise<void> | null = null;

function setGlobalScriptStatus(status: ScriptStatus): void {
  scriptStatus = status;
  listeners.forEach((listener) => listener(status));
}

function hasEmbedScript(): boolean {
  return Boolean(document.getElementById("hubspot-forms-embed"));
}

/** Singleton loader for HubSpot V4 portal embed script. */
export function ensureHubSpotScript(): Promise<void> {
  if (scriptStatus === "ready" && hasEmbedScript()) {
    return Promise.resolve();
  }

  if (loadPromise) return loadPromise;

  setGlobalScriptStatus("loading");

  loadPromise = new Promise<void>((resolve, reject) => {
    const existing = document.getElementById(
      "hubspot-forms-embed",
    ) as HTMLScriptElement | null;

    const onSuccess = () => {
      setGlobalScriptStatus("ready");
      resolve();
    };
    const onFailure = () => {
      loadPromise = null;
      setGlobalScriptStatus("error");
      reject(new Error("HubSpot forms script failed to load"));
    };

    if (existing) {
      // Script tag already present — if it already loaded, succeed; else wait.
      if (scriptStatus === "ready") {
        onSuccess();
        return;
      }
      existing.addEventListener("load", onSuccess, { once: true });
      existing.addEventListener("error", onFailure, { once: true });
      // If the script finished before listeners attached, treat as ready shortly.
      window.setTimeout(() => {
        if (scriptStatus !== "ready" && scriptStatus !== "error") {
          onSuccess();
        }
      }, 50);
      return;
    }

    const script = document.createElement("script");
    script.id = "hubspot-forms-embed";
    script.src = HUBSPOT_EMBED_SCRIPT_URL;
    script.async = true;
    script.defer = true;
    script.onload = onSuccess;
    script.onerror = onFailure;
    document.body.appendChild(script);
  });

  return loadPromise;
}

export function HubSpotScriptProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<ScriptStatus>(scriptStatus);

  useEffect(() => {
    const listener = (next: ScriptStatus) => setStatus(next);
    listeners.add(listener);

    void ensureHubSpotScript().catch((error) => {
      if (process.env.NODE_ENV === "development") {
        console.error("[HubSpot] script load failed", error);
      }
    });

    return () => {
      listeners.delete(listener);
    };
  }, []);

  return (
    <HubSpotScriptContext.Provider value={status}>
      {children}
    </HubSpotScriptContext.Provider>
  );
}
