import type { City, Lang } from "@/lib/cities";
import { COPY } from "@/lib/copy";
import { Hero } from "./Hero";
import { ProofStrip } from "./ProofStrip";
import { TrustBadges } from "./TrustBadges";
import { ProblemRecognition } from "./ProblemRecognition";
import { PracticeAreas } from "./PracticeAreas";
import { NoWinNoFee } from "./NoWinNoFee";
import { MidCTA } from "./MidCTA";
import { AttorneyOffice } from "./AttorneyOffice";
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
      <ProofStrip
        title={copy.proofTitle}
        googleRating={copy.proofGoogleRating}
        googleReviews={copy.proofGoogleReviews}
        yelpLabel={copy.proofYelp}
        points={copy.proofPoints}
      />
      <TrustBadges
        title={copy.trustBadgesTitle}
        membershipsTitle={copy.trustMembershipsTitle}
      />
      <ProblemRecognition title={copy.problemTitle} items={copy.problemItems} />
      <PracticeAreas
        title={copy.practiceTitle}
        intro={copy.practiceIntro(city.name)}
        items={copy.practiceAreas}
      />
      <NoWinNoFee title={copy.noWinTitle} body={copy.noWinBody} />
      <MidCTA
        title={copy.notSureTitle}
        body={copy.notSureBody}
        callLabel={copy.ctaCall}
        formLabel={copy.ctaPrimary}
      />
      <AttorneyOffice
        title={copy.attorneyTitle}
        name={copy.attorneyName}
        role={copy.attorneyRole}
        bio={copy.attorneyBio}
        officeCaption={copy.officeCaption}
        teamCaption={copy.teamCaption}
      />
      <ThreeSteps title={copy.stepsTitle} steps={copy.steps} />
      <Testimonials
        title={copy.testimonialsTitle}
        intro={copy.testimonialsIntro}
        more={copy.testimonialsMore}
      />
      <TrustBadges
        title={copy.trustBadgesTitle}
        membershipsTitle={copy.trustMembershipsTitle}
        tone="muted"
        showMemberships={false}
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
