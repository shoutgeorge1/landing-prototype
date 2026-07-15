import assert from "node:assert/strict";
import test from "node:test";

import { submitLead } from "../src/lib/submitLead";
import { pushHubSpotFormSubmission } from "../src/lib/tracking";

class MemoryStorage {
  private values = new Map<string, string>();

  getItem(key: string): string | null {
    return this.values.get(key) ?? null;
  }

  setItem(key: string, value: string): void {
    this.values.set(key, value);
  }
}

const search =
  "?gclid=test-gclid&utm_source=google&utm_medium=cpc&utm_campaign=meeting-qa" +
  "&utm_term=employment-lawyer&utm_content=rsa-1" +
  "&google_campaign=ela-fresno-en&google_ad_group=employment_lawyer" +
  "&google_keyword=employment-lawyer";

function installBrowserMocks(): Record<string, unknown>[] {
  const dataLayer: Record<string, unknown>[] = [];
  Object.assign(globalThis, {
    localStorage: new MemoryStorage(),
    document: { cookie: "hubspotutk=test-hutk" },
    window: {
      dataLayer,
      location: {
        href: `https://help.employmentlawassist.com/fresno/en${search}`,
        pathname: "/fresno/en",
        search,
      },
    },
  });
  return dataLayer;
}

test("successful HubSpot POST carries attribution and fires once per submission ID", async () => {
  const dataLayer = installBrowserMocks();
  let submittedBody: {
    fields: Array<{ name: string; value: string }>;
  } | null = null;

  globalThis.fetch = async (_input, init) => {
    submittedBody = JSON.parse(String(init?.body));
    return new Response("", { status: 200 });
  };

  const result = await submitLead({
    firstName: "Athena",
    lastName: "Tracking QA",
    phone: "4246781416",
    email: "tracking-qa@example.com",
    message: "Automated tracking payload verification",
    consent: true,
    lang: "en",
    city: "fresno",
    pageName: "Fresno EN meeting QA",
    communicationConsentText: "QA communication consent",
    processingConsentText: "QA processing consent",
  });

  assert.equal(result.ok, true);
  assert.ok(result.submissionId);
  assert.ok(submittedBody);

  const fields = Object.fromEntries(
    submittedBody.fields.map(({ name, value }) => [name, value]),
  );
  assert.deepEqual(
    {
      gclid: fields.gclid,
      utm_source: fields.utm_source,
      utm_medium: fields.utm_medium,
      utm_campaign: fields.utm_campaign,
      utm_term: fields.utm_term,
      utm_content: fields.utm_content,
      google_campaign: fields.google_campaign,
      google_ad_group: fields.google_ad_group,
      google_keyword: fields.google_keyword,
      city: fields.city,
      language: fields.language,
    },
    {
      gclid: "test-gclid",
      utm_source: "google",
      utm_medium: "cpc",
      utm_campaign: "meeting-qa",
      utm_term: "employment-lawyer",
      utm_content: "rsa-1",
      google_campaign: "ela-fresno-en",
      google_ad_group: "employment_lawyer",
      google_keyword: "employment-lawyer",
      city: "fresno",
      language: "en",
    },
  );

  pushHubSpotFormSubmission(
    "6dc81a33-35df-4dc4-b20a-ec5e409ed420",
    "english",
    result.submissionId,
  );
  pushHubSpotFormSubmission(
    "6dc81a33-35df-4dc4-b20a-ec5e409ed420",
    "english",
    result.submissionId,
  );

  const conversionEvents = dataLayer.filter(
    (entry) => entry.event === "hubspot_form_submission",
  );
  assert.equal(conversionEvents.length, 1);
  assert.equal(
    conversionEvents[0].hubspot_submission_id,
    result.submissionId,
  );
  assert.equal(conversionEvents[0].event_id, result.submissionId);
});

test("a legitimate second submission ID fires a second event", () => {
  const dataLayer = installBrowserMocks();
  pushHubSpotFormSubmission("form-id", "english", "submission-one");
  pushHubSpotFormSubmission("form-id", "english", "submission-two");
  assert.equal(
    dataLayer.filter((entry) => entry.event === "hubspot_form_submission").length,
    2,
  );
});
