import type { Metadata } from "next";
import { ThankYouPage } from "@/components/ThankYouPage";

export const metadata: Metadata = {
  title: "Gracias",
  description: "Hemos recibido su solicitud de consulta gratis.",
  robots: { index: false, follow: false },
};

export default function Page() {
  return <ThankYouPage lang="es" />;
}
