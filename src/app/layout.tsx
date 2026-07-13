import type { Metadata } from "next";
import "./globals.css";
import { BRAND_IMAGES } from "@/lib/content";
import { GTM_ID } from "@/lib/tracking";
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
        <link rel="dns-prefetch" href="https://api.hsforms.com" />
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
        <UtmCapture />
        {children}
      </body>
    </html>
  );
}
