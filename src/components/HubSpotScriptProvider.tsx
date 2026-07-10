"use client";

import Script from "next/script";
import { createContext, useContext, useEffect, useState } from "react";
import { HUBSPOT_EMBED_SCRIPT_URL } from "@/lib/hubspot";

type ScriptStatus = "idle" | "loading" | "ready" | "error";

const HubSpotScriptContext = createContext<ScriptStatus>("idle");

export function useHubSpotScriptStatus(): ScriptStatus {
  return useContext(HubSpotScriptContext);
}

let scriptStatus: ScriptStatus = "idle";
const listeners = new Set<(status: ScriptStatus) => void>();

function setGlobalScriptStatus(status: ScriptStatus): void {
  scriptStatus = status;
  listeners.forEach((listener) => listener(status));
}

export function HubSpotScriptProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [status, setStatus] = useState<ScriptStatus>(scriptStatus);

  useEffect(() => {
    setStatus(scriptStatus);
    const listener = (next: ScriptStatus) => setStatus(next);
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }, []);

  const shouldLoadScript = status !== "ready" && status !== "error";

  return (
    <HubSpotScriptContext.Provider value={status}>
      {shouldLoadScript ? (
        <Script
          id="hubspot-forms-embed"
          src={HUBSPOT_EMBED_SCRIPT_URL}
          strategy="afterInteractive"
          onLoad={() => setGlobalScriptStatus("ready")}
          onError={() => setGlobalScriptStatus("error")}
          onReady={() => setGlobalScriptStatus("ready")}
        />
      ) : null}
      {children}
    </HubSpotScriptContext.Provider>
  );
}
