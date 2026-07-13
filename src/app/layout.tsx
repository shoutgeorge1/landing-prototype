import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";
import { BRAND_IMAGES } from "@/lib/content";
import { HUBSPOT_EMBED_SCRIPT_URL } from "@/lib/hubspot";
import { hubSpotThemeCssText } from "@/lib/hubspotTheme";
import { GTM_ID } from "@/lib/tracking";
import { HubSpotScriptProvider } from "@/components/HubSpotScriptProvider";
import { UtmCapture } from "@/components/UtmCapture";

export const metadata: Metadata = {
  metadataBase: new URL("https://help.employmentlawassist.com"),
  title: {
    default: "Employment Law Assist | California Employment Law Support",
    template: "%s | Employment Law Assist",
  },
  description:
    "California employment law support for employees. Request a confidential case review for wrongful termination, discrimination, harassment, retaliation, or unpaid wages.",
  robots: { index: true, follow: true },
  icons: {
    icon: BRAND_IMAGES.iconDarkSquare,
    apple: BRAND_IMAGES.iconDarkSquare,
  },
  openGraph: {
    type: "website",
    siteName: "Employment Law Assist",
    title: "Employment Law Assist | California Employment Law Support",
    description:
      "California employment law support for employees. Request a confidential case review.",
  },
};

const gtmSnippet = `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','${GTM_ID}');`;

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://js-na2.hsforms.net" crossOrigin="anonymous" />
        <link rel="dns-prefetch" href="https://js-na2.hsforms.net" />
        <link rel="dns-prefetch" href="https://forms.hsforms.com" />
        {/* Start HubSpot download during first HTML parse — don't wait for React hydration. */}
        <link
          rel="preload"
          href={HUBSPOT_EMBED_SCRIPT_URL}
          as="script"
          crossOrigin="anonymous"
        />
        {/* HubSpot V4 iframe reads --hsf-* from :root before the embed mounts. */}
        <style
          id="ela-hubspot-theme"
          dangerouslySetInnerHTML={{ __html: hubSpotThemeCssText() }}
        />
        <script dangerouslySetInnerHTML={{ __html: gtmSnippet }} />
      </head>
      <body className="min-h-screen bg-white text-slate-800 antialiased">
        <noscript>
          <iframe
            src={`https://www.googletagmanager.com/ns.html?id=${GTM_ID}`}
            height="0"
            width="0"
            style={{ display: "none", visibility: "hidden" }}
          />
        </noscript>
        <Script
          id="hubspot-forms-embed"
          src={HUBSPOT_EMBED_SCRIPT_URL}
          strategy="beforeInteractive"
        />
        <HubSpotScriptProvider>
          <UtmCapture />
          {children}
        </HubSpotScriptProvider>
      </body>
    </html>
  );
}
