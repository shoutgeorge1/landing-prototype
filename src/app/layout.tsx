import type { Metadata } from "next";
import "./globals.css";
import { BRAND_IMAGES } from "@/lib/content";
import { GTM_ID } from "@/lib/tracking";
import { HubSpotScriptProvider } from "@/components/HubSpotScriptProvider";

export const metadata: Metadata = {
  metadataBase: new URL("https://employmentlawassist.com"),
  title: {
    default: "Employment Law Assist | California Employment Lawyers",
    template: "%s | Employment Law Assist",
  },
  description:
    "California employment law attorneys serving employees statewide. Free, confidential consultation. Hablamos Español. Available 24/7 by phone.",
  robots: { index: false, follow: false },
  icons: {
    icon: BRAND_IMAGES.iconDarkSquare,
    apple: BRAND_IMAGES.iconDarkSquare,
  },
  openGraph: {
    type: "website",
    siteName: "Employment Law Assist",
    title: "Employment Law Assist | California Employment Lawyers",
    description:
      "California employment law attorneys serving employees statewide. Free, confidential consultation.",
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
        <HubSpotScriptProvider>{children}</HubSpotScriptProvider>
      </body>
    </html>
  );
}
