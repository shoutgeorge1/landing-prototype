import type { City, Lang } from "@/lib/cities";
import { COPY } from "@/lib/copy";
import { Hero } from "./Hero";
import { TrustBadges } from "./TrustBadges";
import { NoWinNoFee } from "./NoWinNoFee";
import { ProblemSection } from "./ProblemSection";
import { PracticeAreas } from "./PracticeAreas";
import { WhyUs } from "./WhyUs";
import { ThreeSteps } from "./ThreeSteps";
import { Testimonials } from "./Testimonials";
import { FinalCTA } from "./FinalCTA";
import { Disclaimer } from "./Disclaimer";
import { SiteFooter } from "./SiteFooter";
import { StickyMobileCTA } from "./StickyMobileCTA";
import { UtmCapture } from "./UtmCapture";

interface LandingPageProps {
  city: City;
  lang: Lang;
}

export function LandingPage({ city, lang }: LandingPageProps) {
  const copy = COPY[lang];
  return (
    <main>
      <UtmCapture />
      <Hero city={city} lang={lang} copy={copy} />
      <TrustBadges title={copy.trustBadgesTitle} />
      <NoWinNoFee title={copy.noWinTitle} body={copy.noWinBody} />
      <ProblemSection title={copy.problemTitle(city.name)} body={copy.problemBody(city.name)} />
      <PracticeAreas
        title={copy.practiceTitle}
        intro={copy.practiceIntro(city.name)}
        items={copy.practiceAreas}
      />
      <WhyUs title={copy.whyUsTitle} items={copy.whyUs} note={copy.whyUsNote} />
      <ThreeSteps title={copy.stepsTitle} steps={copy.steps} />
      <Testimonials title={copy.testimonialsTitle} intro={copy.testimonialsIntro} />
      <TrustBadges title={copy.trustBadgesTitle} tone="muted" />
      <FinalCTA city={city} lang={lang} copy={copy} />
      <Disclaimer text={copy.disclaimer(city.name)} />
      <SiteFooter
        officeTitle={copy.footerOfficeTitle}
        contactTitle={copy.footerContactTitle}
        disclaimer={copy.footerDisclaimer}
      />
      <StickyMobileCTA label={copy.ctaCall} />
    </main>
  );
}
