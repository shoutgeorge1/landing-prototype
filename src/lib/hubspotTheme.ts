/** HubSpot V4 iframe forms read these from :root at embed time. */
export const HUBSPOT_THEME_VARS: Record<string, string> = {
  "--hsf-global__font-family":
    'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
  "--hsf-global__font-size": "16px",
  "--hsf-global__color": "#0f172a",
  "--hsf-global-error__color": "#b91c1c",
  "--hsf-row__horizontal-spacing": "12px",
  "--hsf-row__vertical-spacing": "12px",
  "--hsf-module__vertical-spacing": "12px",
  "--hsf-background__background-color": "transparent",
  "--hsf-background__border-width": "0",
  "--hsf-background__padding": "0",
  "--hsf-field-label__font-size": "13px",
  "--hsf-field-label__color": "#10284a",
  "--hsf-field-label-requiredindicator__color": "#b45309",
  "--hsf-field-input__font-size": "16px",
  "--hsf-field-input__color": "#0f172a",
  "--hsf-field-input__background-color": "#f4f7fb",
  "--hsf-field-input__placeholder-color": "#8a97a8",
  "--hsf-field-input__border-color": "#b8c4d4",
  "--hsf-field-input__border-width": "1.5px",
  "--hsf-field-input__border-style": "solid",
  "--hsf-field-input__border-radius": "10px",
  "--hsf-field-input__padding": "12px 14px",
  "--hsf-field-textarea__font-size": "16px",
  "--hsf-field-textarea__color": "#0f172a",
  "--hsf-field-textarea__background-color": "#f4f7fb",
  "--hsf-field-textarea__placeholder-color": "#8a97a8",
  "--hsf-field-textarea__border-color": "#b8c4d4",
  "--hsf-field-textarea__border-width": "1.5px",
  "--hsf-field-textarea__border-style": "solid",
  "--hsf-field-textarea__border-radius": "10px",
  "--hsf-field-textarea__padding": "12px 14px",
  "--hsf-field-checkbox__background-color": "#ffffff",
  "--hsf-field-checkbox__color": "#10284a",
  "--hsf-field-checkbox__border-color": "#94a3b8",
  "--hsf-field-checkbox__border-width": "1.5px",
  "--hsf-richtext__font-size": "12.5px",
  "--hsf-richtext__color": "#475569",
  "--hsf-button__font-size": "16px",
  "--hsf-button__font-weight": "800",
  "--hsf-button__color": "#10284a",
  "--hsf-button__background-color": "#e7be02",
  "--hsf-button__border-radius": "10px",
  "--hsf-button__padding": "14px 18px",
  "--hsf-button__width": "100%",
  "--hsf-button__box-shadow": "0 3px 12px rgba(231, 190, 2, 0.35)",
  "--hsf-button--hover__background-color": "#f0c91a",
  "--hsf-button--hover__color": "#0b1c36",
  "--hsf-erroralert__color": "#b91c1c",
};

export function hubSpotThemeCssText(): string {
  const body = Object.entries(HUBSPOT_THEME_VARS)
    .map(([key, value]) => `  ${key}: ${value};`)
    .join("\n");
  return `:root {\n${body}\n}`;
}

export function applyHubSpotThemeToDocument(): void {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  for (const [key, value] of Object.entries(HUBSPOT_THEME_VARS)) {
    root.style.setProperty(key, value);
  }
}
