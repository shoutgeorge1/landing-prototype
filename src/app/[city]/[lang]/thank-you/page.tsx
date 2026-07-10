import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getCity } from "@/lib/cities";
import { ThankYouPage } from "@/components/ThankYouPage";

type RouteParams = { city: string; lang: string };

export const metadata: Metadata = {
  title: "Thank You",
  description: "Your free consultation request has been received.",
  robots: { index: false, follow: false },
};

export default async function Page({ params }: { params: Promise<RouteParams> }) {
  const { city: citySlug, lang } = await params;
  if (lang !== "en" || !getCity(citySlug)) notFound();
  return <ThankYouPage lang="en" />;
}
