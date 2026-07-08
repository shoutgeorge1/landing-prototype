import type { City, Lang } from "@/lib/cities";
import { COPY } from "@/lib/copy";
import { Hero } from "./Hero";
import { TrustBadges } from "./TrustBadges";
import { NoWinNoFee } from "./NoWinNoFee";
import { ProblemSection } from "./ProblemSection";
import { PracticeAreas } from "./PracticeAreas";
import { WhyUs } from "./WhyUs";
import { AttorneyOffice } from "./AttorneyOffice";
import { ThreeSteps } from "./ThreeSteps";
import { Testimonials } from "./Testimonials";
import { ReviewsCTA } from "./ReviewsCTA";
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
      <TrustBadges
        title={copy.trustBadgesTitle}
        membershipsTitle={copy.trustMembershipsTitle}
      />
      <NoWinNoFee title={copy.noWinTitle} body={copy.noWinBody} />
      <ProblemSection title={copy.problemTitle(city.name)} body={copy.problemBody(city.name)} />
      <PracticeAreas
        title={copy.practiceTitle}
        intro={copy.practiceIntro(city.name)}
        items={copy.practiceAreas}
      />
      <WhyUs title={copy.whyUsTitle} items={copy.whyUs} note={copy.whyUsNote} />
      <AttorneyOffice
        title={copy.attorneyTitle}
        name={copy.attorneyName}
        role={copy.attorneyRole}
        bio={copy.attorneyBio}
        officeCaption={copy.officeCaption}
        teamCaption={copy.teamCaption}
      />
      <ThreeSteps title={copy.stepsTitle} steps={copy.steps} />
      <Testimonials title={copy.testimonialsTitle} intro={copy.testimonialsIntro} />
      <ReviewsCTA
        title={copy.reviewsTitle}
        googleLabel={copy.reviewsGoogle}
        yelpLabel={copy.reviewsYelp}
      />
      <TrustBadges
        title={copy.trustBadgesTitle}
        membershipsTitle={copy.trustMembershipsTitle}
        tone="muted"
      />
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
