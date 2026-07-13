import type { Metadata } from "next";
import { LegalPageShell } from "@/components/LegalPageShell";
import { FIRM, MICROSITE } from "@/lib/content";

export const metadata: Metadata = {
  title: "Terms of Use",
  description: `Terms of Use for the ${FIRM.name} advertising microsite at ${MICROSITE.host}.`,
  robots: { index: true, follow: true },
  alternates: { canonical: MICROSITE.termsPath },
};

const EFFECTIVE = "July 13, 2026";

export default function TermsPage() {
  return (
    <LegalPageShell title="Terms of Use" effectiveDate={EFFECTIVE}>
      <p>
        These Terms of Use (“Terms”) govern your access to and use of the
        advertising microsite at <strong>{MICROSITE.host}</strong> (the
        “Site”), operated by {FIRM.name} (“we,” “us,” or “our”).
      </p>
      <p>
        By using the Site, you agree to these Terms and our{" "}
        <a href={MICROSITE.privacyPath}>Privacy Policy</a>. If you do not
        agree, do not use the Site.
      </p>

      <h2>1. Separate advertising microsite</h2>
      <p>
        This Site is a paid-media and campaign microsite. It is not a
        replacement for our main website and may use separate tracking,
        analytics, and conversion tools. Content and offers on this Site may
        differ from materials on other {FIRM.name} properties.
      </p>

      <h2>2. Attorney advertising — no legal advice</h2>
      <p>
        The Site is attorney advertising and provides general information only.
        Nothing on the Site is legal advice for your specific situation. Laws
        change, and facts matter. Do not rely on Site content as a substitute
        for advice from a licensed attorney who has reviewed your matter.
      </p>

      <h2>3. No attorney-client relationship</h2>
      <p>
        Using the Site, submitting a form, calling, or emailing us does not by
        itself create an attorney-client relationship. An attorney-client
        relationship forms only if we expressly agree to represent you, typically
        in a written engagement agreement.
      </p>
      <p>
        Do not send confidential or sensitive information through the Site
        until an attorney-client relationship exists and you have been
        instructed how to communicate securely.
      </p>

      <h2>4. No guarantees</h2>
      <p>
        We do not guarantee that we will take your case, that you have a valid
        claim, or that any particular result will be obtained. Past results do
        not guarantee a similar outcome.
      </p>

      <h2>5. Case reviews and communications</h2>
      <p>
        Form submissions and calls are requests for information or a case
        review. We may contact you by phone, text, or email using the contact
        details you provide, consistent with any consent you give and applicable
        law. Message and data rates may apply for texts.
      </p>

      <h2>6. Eligibility and acceptable use</h2>
      <p>
        You agree not to misuse the Site, including by attempting to disrupt it,
        scrape it in an abusive way, submit false information, or use it for
        unlawful purposes.
      </p>

      <h2>7. Intellectual property</h2>
      <p>
        Site content, branding, and design are owned by us or our licensors and
        may not be copied or used commercially without permission, except as
        allowed by law.
      </p>

      <h2>8. Third-party tools and links</h2>
      <p>
        The Site may use third-party services (for example form, analytics, or
        advertising providers). We are not responsible for third-party websites
        or services we do not control.
      </p>

      <h2>9. Disclaimer of warranties</h2>
      <p>
        The Site is provided “as is” and “as available.” To the fullest extent
        permitted by law, we disclaim warranties of merchantability, fitness for
        a particular purpose, and non-infringement.
      </p>

      <h2>10. Limitation of liability</h2>
      <p>
        To the fullest extent permitted by law, {FIRM.name} and its attorneys,
        staff, and affiliates are not liable for indirect, incidental, special,
        consequential, or punitive damages arising from your use of the Site.
        Some jurisdictions do not allow certain limitations; in those cases, our
        liability is limited to the maximum extent permitted by law.
      </p>

      <h2>11. Governing law</h2>
      <p>
        These Terms are governed by the laws of the State of California,
        without regard to conflict-of-law rules. Venue for disputes relating to
        the Site that are not otherwise controlled by an engagement agreement
        shall be in the state or federal courts located in California, unless
        applicable law requires otherwise.
      </p>

      <h2>12. Changes</h2>
      <p>
        We may update these Terms from time to time. The effective date above
        will change when we do. Continued use of the Site after an update means
        you accept the revised Terms.
      </p>

      <h2>13. Contact</h2>
      <p>
        {FIRM.name}
        <br />
        {FIRM.office.street}
        <br />
        {FIRM.office.city}, {FIRM.office.state} {FIRM.office.zip}
        <br />
        Email: <a href={`mailto:${FIRM.email}`}>{FIRM.email}</a>
        <br />
        Phone: <a href={`tel:${FIRM.phoneTel}`}>{FIRM.phoneDisplay}</a>
      </p>
    </LegalPageShell>
  );
}
