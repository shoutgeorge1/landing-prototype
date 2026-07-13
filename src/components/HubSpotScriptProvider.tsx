"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { HUBSPOT_EMBED_SCRIPT_URL } from "@/lib/hubspot";
import { applyHubSpotThemeToDocument } from "@/lib/hubspotTheme";

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

function isScriptElementComplete(script: HTMLScriptElement): boolean {
  // readyState exists on HTMLScriptElement in browsers when supported.
  const state = (script as HTMLScriptElement & { readyState?: string }).readyState;
  return state === "complete" || state === "loaded" || script.dataset.elaLoaded === "1";
}

/** Singleton loader for HubSpot V4 portal embed script. */
export function ensureHubSpotScript(): Promise<void> {
  if (typeof document !== "undefined") {
    applyHubSpotThemeToDocument();
  }

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
      if (existing) existing.dataset.elaLoaded = "1";
      setGlobalScriptStatus("ready");
      resolve();
    };
    const onFailure = () => {
      loadPromise = null;
      setGlobalScriptStatus("error");
      reject(new Error("HubSpot forms script failed to load"));
    };

    if (existing) {
      // Layout may have injected this via beforeInteractive — often already loaded.
      if (scriptStatus === "ready" || isScriptElementComplete(existing)) {
        onSuccess();
        return;
      }
      existing.addEventListener("load", onSuccess, { once: true });
      existing.addEventListener("error", onFailure, { once: true });
      // If load fired before listeners attached, complete shortly.
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
    script.onload = () => {
      script.dataset.elaLoaded = "1";
      onSuccess();
    };
    script.onerror = onFailure;
    document.head.appendChild(script);
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
