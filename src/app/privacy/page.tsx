import type { Metadata } from "next";
import { LegalPageShell } from "@/components/LegalPageShell";
import { TrackedTelLink } from "@/components/TrackedTelLink";
import { FIRM, MICROSITE } from "@/lib/content";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: `Privacy Policy for the ${FIRM.name} advertising microsite at ${MICROSITE.host}.`,
  robots: { index: true, follow: true },
  alternates: { canonical: MICROSITE.privacyPath },
};

const EFFECTIVE = "July 13, 2026";

export default function PrivacyPage() {
  return (
    <LegalPageShell title="Privacy Policy" effectiveDate={EFFECTIVE}>
      <p>
        This Privacy Policy explains how {FIRM.name} (“we,” “us,” or “our”)
        collects, uses, and shares information on this advertising microsite
        operated at{" "}
        <strong>{MICROSITE.host}</strong> (the “Site”).
      </p>
      <p>
        This Site is a paid-media and campaign microsite. It is operated
        separately from our main website at{" "}
        <a href={FIRM.website}>{FIRM.website.replace(/\/$/, "")}</a> and uses
        its own analytics, tag management, and advertising tracking. Practices
        described here apply to this Site unless we say otherwise.
      </p>

      <h2>1. Information we collect</h2>
      <p>We may collect:</p>
      <ul>
        <li>
          <strong>Information you submit</strong> — such as name, phone number,
          email address, city, employer name, and a description of your
          workplace situation when you complete a form or contact us.
        </li>
        <li>
          <strong>Device and usage data</strong> — such as IP address, browser
          type, pages viewed, referring URL, and approximate location derived
          from IP.
        </li>
        <li>
          <strong>Advertising and attribution data</strong> — such as UTM
          parameters and click identifiers (for example gclid, msclkid, or
          fbclid) that help us measure campaign performance.
        </li>
      </ul>

      <h2>2. How we use information</h2>
      <p>We use information to:</p>
      <ul>
        <li>Respond to case-review or consultation requests</li>
        <li>Operate, secure, and improve the Site</li>
        <li>Measure advertising and conversion performance on this Site</li>
        <li>Comply with law and enforce our terms</li>
      </ul>
      <p>
        Submitting a form does not create an attorney-client relationship.
        Information you share may be reviewed to determine whether we can help.
      </p>

      <h2>3. Cookies, pixels, and tracking</h2>
      <p>
        This Site uses its own Google Tag Manager container and related
        analytics or advertising tags (which may include Google Analytics /
        GA4, Google Ads conversion tags, and similar tools configured in that
        container). These technologies help us understand Site use and measure
        paid media results for this microsite.
      </p>
      <p>
        We also use HubSpot forms to collect submissions. HubSpot may set
        cookies or process form data as our service provider.
      </p>
      <p>
        You can control cookies through your browser settings. Blocking cookies
        may limit some Site features or tracking accuracy.
      </p>

      <h2>4. How we share information</h2>
      <p>We may share information with:</p>
      <ul>
        <li>
          Service providers that help us run the Site, forms, hosting,
          analytics, and advertising measurement
        </li>
        <li>
          Professional advisors, or others as needed to evaluate or handle an
          inquiry, where appropriate
        </li>
        <li>Authorities when required by law or to protect rights and safety</li>
      </ul>
      <p>
        We do not sell your personal information for money. California law may
        treat some advertising or analytics disclosures as a “sale” or
        “sharing” of personal information for cross-context behavioral
        advertising. If that applies, you may exercise rights described below.
      </p>

      <h2>5. California privacy rights</h2>
      <p>
        If you are a California resident, you may have rights under the
        California Consumer Privacy Act (CCPA/CPRA), including the right to
        know, delete, correct, and opt out of certain sale or sharing of
        personal information, subject to legal exceptions.
      </p>
      <p>
        To make a request, email{" "}
        <a href={`mailto:${FIRM.email}`}>{FIRM.email}</a> or call{" "}
        <TrackedTelLink
          location="privacy_ccpa"
          className="font-medium text-[var(--navy)] underline"
        />
        . We may need to verify your identity before fulfilling a request.
      </p>

      <h2>6. Retention</h2>
      <p>
        We keep information as long as reasonably needed for the purposes above,
        including inquiry follow-up, legal compliance, dispute resolution, and
        business records, unless a longer period is required or permitted by
        law.
      </p>

      <h2>7. Children</h2>
      <p>
        The Site is not directed to children under 16, and we do not knowingly
        collect personal information from them.
      </p>

      <h2>8. Changes</h2>
      <p>
        We may update this Privacy Policy from time to time. The effective date
        above will change when we do. Continued use of the Site after an update
        means you accept the revised policy.
      </p>

      <h2>9. Contact</h2>
      <p>
        {FIRM.name}
        <br />
        {FIRM.office.street}
        <br />
        {FIRM.office.city}, {FIRM.office.state} {FIRM.office.zip}
        <br />
        Email: <a href={`mailto:${FIRM.email}`}>{FIRM.email}</a>
        <br />
        Phone:{" "}
        <TrackedTelLink
          location="privacy_contact"
          className="font-medium text-[var(--navy)] underline"
        />
      </p>
    </LegalPageShell>
  );
}
