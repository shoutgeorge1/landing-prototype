import type { Metadata } from "next";
import { ThankYouPage } from "@/components/ThankYouPage";
import { isLang } from "@/lib/cities";

export const metadata: Metadata = {
  title: "Thank You",
  description: "Your free consultation request has been received.",
  robots: { index: false, follow: false },
};

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ lang?: string }>;
}) {
  const { lang } = await searchParams;
  const resolved = lang && isLang(lang) ? lang : "en";
  return <ThankYouPage lang={resolved} />;
}
