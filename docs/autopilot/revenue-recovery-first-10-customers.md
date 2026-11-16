# Revenue Recovery — First 10 Customer Acquisition Plan

**Status:** internal strategy / discovery plan. This is not a live offer, price quote, deployment approval, or authorization to contact prospects automatically.

**Parent mission:** [Turbo Foundry #28 — Revenue Recovery subscription](https://github.com/godsun108/turbo-foundry/issues/28)

**Existing gates to preserve:** [#6 first-customer validation](https://github.com/godsun108/turbo-foundry/issues/6), [#9 purchase-to-fulfillment release gates](https://github.com/godsun108/turbo-foundry/issues/9), and [#10 isolated provider staging](https://github.com/godsun108/turbo-foundry/issues/10).

## 1. Working thesis

Build a recurring-revenue product that helps small service businesses follow through on inbound opportunities they already paid to generate:

- missed inbound inquiries that need a human callback;
- estimates that have not received a decision;
- previous customers who may be due for appropriate follow-up;
- follow-up work that currently lives in memory, sticky notes, inboxes, or disconnected tools.

The product should complement the customer's existing field-service software rather than demand a CRM migration.

**Core promise to validate:** make follow-up more consistent and visible. Do not promise recovered jobs, conversion rates, or ROI before customer-specific results are measured.

## 2. Initial ideal customer profile

Start with one narrow segment: independent residential plumbing and HVAC businesses.

| Attribute | Initial qualification hypothesis |
| --- | --- |
| Business | Owner-operated or locally managed plumbing / HVAC company |
| Team | Approximately 1–10 field technicians |
| Demand | Receives inbound calls and estimate requests each week |
| Current process | Follow-up is manual, inconsistent, or spread across several tools |
| Buyer | Owner, general manager, or service manager can approve a pilot |
| Need | Can describe a real cost or operational consequence of delayed follow-up |
| Access | Will discuss workflow using aggregate information and fictional examples |

### Strong-fit signals

- The owner or manager acknowledges missed calls or estimates that go stale.
- There is enough inbound volume to justify a recurring workflow.
- The company already has a business phone and/or field-service system.
- A responsible employee can review exceptions and urgent requests.
- The business can explain its customer-contact permissions and opt-out practices.
- A decision-maker agrees to a specific next conversation or evaluation step.

### Disqualifiers for the first cohort

- No identifiable follow-up problem or insufficient volume.
- No access to a decision-maker.
- Requests for unsolicited bulk messaging or unlawful contact practices.
- The business expects guaranteed bookings or revenue.
- The required phone/CRM integration cannot be authorized or safely supported.
- Emergency dispatch or other high-risk workflows cannot be reliably escalated to a human.

## 3. Competitor map

This is a positioning map, not a claim that any competitor lacks a particular feature. Re-check current product features, plan limits, and prices on official vendor pages before making a proposal.

| Competitor category | Examples to benchmark | Customer expectation | Our possible distinction |
| --- | --- | --- | --- |
| Field-service management suites | Jobber, Housecall Pro | Scheduling, estimates, invoices, customer records, automation | Lightweight follow-up visibility alongside the system already in use |
| General CRM / automation platforms | HighLevel | Pipelines, forms, messaging, workflow automation | A narrow service-business workflow with setup and outcome measurement |
| AI receptionist / call handling | Jobber AI Receptionist, Housecall Pro AI CSR and specialist vendors | Answering, intake, routing, booking | Close the loop after the call: estimate follow-up, repeat-customer tasks, and attributable outcomes |
| Manual office process | Spreadsheets, inboxes, callbacks, paper notes | Flexible and familiar, but dependent on staff consistency | Clear ownership, reminders, exception handling, and auditable follow-up |

### Competitive research checklist

For each product, record the date checked and official source URL:

- Current plan prices and billing cadence.
- AI / phone / SMS add-on prices and included usage.
- Supported phone, CRM, calendar, and field-service integrations.
- Whether missed-call follow-up, estimate follow-up, and reactivation are included or separate add-ons.
- Human escalation and opt-out controls.
- Onboarding requirements, contract terms, and cancellation.
- Reviews and recurring complaints, separating anecdote from verified fact.

Do not publish stale competitor prices or claim a feature gap without verifying the current vendor documentation.

## 4. Pricing hypotheses — discovery only

No public price is approved. Test a small set of price points only after learning the customer's workflow and the full delivery cost.

| Hypothesis | Monthly price | What it tests |
| --- | ---: | --- |
| Entry | $99 | Whether a narrow follow-up queue has standalone value |
| Founding | $149 | Whether a broader follow-up and reporting workflow has value |
| Higher-touch | $249 | Whether onboarding, integrations, and greater support justify a higher tier |

These are interview hypotheses, not published prices, commitments, or checkout products.

Before selecting a price, calculate:

- messaging / telephony / model / hosting and integration costs;
- onboarding and ongoing support labor;
- customer acquisition cost;
- compliance, insurance, taxes, refunds, and payment processing;
- usage limits and overage policy;
- expected contribution margin at realistic utilization.

Ask what the customer currently spends, what the problem costs, what alternatives they pay for, and what outcome would justify a monthly fee. Do not anchor every interview on $149 or treat a hypothetical yes as a sale.

## 5. First-customer motion

### Stage A — Validate the problem

1. Select one metro or service area where founder-led conversations are practical. Geography is intentionally undecided until a market is chosen.
2. Build a private research list of qualified businesses using public business websites and public business contact channels.
3. Research in weekly batches of up to 25 new prospects; remove duplicates and verify that each business is operating.
4. Invite owners/managers to a short discovery conversation through a human-reviewed, appropriate channel.
5. Complete 10 consented interviews before expanding speculative engineering.

### Stage B — Qualify design partners

Aim to identify up to three businesses with:

- a concrete recurring follow-up problem;
- a decision-maker willing to evaluate a solution;
- a documented current workflow and aggregate baseline;
- an authorized integration path, if needed;
- an appropriate consent and opt-out process;
- a measurable success criterion;
- a concrete next step.

A design partner is not automatically a paying customer or a live pilot.

### Stage C — Convert only after readiness

Once delivery, security, compliance, support, and payment gates are independently verified:

1. Present a written scope with included workflows, usage limits, exclusions, support, cancellation, data handling, and price.
2. Obtain written business authorization and verify provider-account ownership.
3. Run a controlled customer-specific pilot with human oversight.
4. Reconcile actual provider events, delivery, replies, bookings, and collected revenue.
5. Offer a recurring subscription only when the product can genuinely deliver the described service.

### Funnel dashboard

Track counts, not vanity metrics:

| Stage | Definition |
| --- | --- |
| Researched | Public business appears to match the ICP |
| Qualified | Fit verified against the rubric |
| Contact approved | Human has approved the specific outreach |
| Contacted | A real, documented contact attempt occurred |
| Conversation | Decision-maker completed a discovery discussion |
| Demo | Fictional/offline demo shown with readiness disclosure |
| Design partner | Concrete evaluation step agreed |
| Pilot authorized | Written scope and required approvals complete |
| Paying | Payment actually collected for a deliverable service |
| Retained | Subscription remains active after the first renewal |

Never count a prospect, proposal, verbal expression of interest, simulated booking, or test payment as recurring revenue.

## 6. Discovery interview script

Opening:

> We're researching how small plumbing and HVAC companies handle missed calls, estimate follow-up, and repeat-customer reminders. We're not selling a live automated service today. Could I ask a few questions about your current workflow and show you a fictional offline demonstration?

Questions:

1. What happens when a new customer calls and nobody can answer?
2. How are missed inquiries assigned and followed up today?
3. How do you track estimates that have not been accepted?
4. Which existing phone, CRM, scheduling, or field-service tools do you use?
5. Roughly how many missed inquiries or open estimates occur in a typical week? An estimate is enough; do not share caller records.
6. Who owns follow-up, and how much staff time does it consume?
7. How do you manage permission to contact customers, opt-outs, and quiet hours?
8. What would have to improve for a monthly service to be worth paying for?
9. What alternatives have you tried, and what do they cost?
10. Who else would need to approve a pilot, and what would the next step be?

Record objections and exact customer language with permission. Store only anonymized, non-sensitive findings in public GitHub.

## 7. Prospect qualification rubric

Score each item 0, 1, or 2. This is a prioritization aid, not a credit or eligibility decision.

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Follow-up pain | Not identified | General frustration | Specific recurring workflow problem |
| Inbound volume | Unknown / negligible | Some volume | Meaningful recurring volume |
| Buyer access | No buyer | Influencer | Decision-maker engaged |
| Current process | Already solved | Partly manual | Clear gaps and ownership issues |
| Integration path | No permission/path | Unclear | Existing supported system and authorization path |
| Measurement | No baseline | Approximate | Agreed measurable baseline |
| Willingness to act | No next step | Interested | Specific follow-up/evaluation agreed |

Prioritize high scores for discovery, but do not bypass privacy, consent, security, or commercial release gates.

## 8. Privacy, outreach, and safety boundaries

- Prospect research may use public business information. Do not scrape private personal contact data.
- Keep prospect names, individual contact details, call notes, customer records, and credentials out of this public repository and CI.
- Store any necessary prospect records only in an approved private system with access controls and retention limits.
- No automated outreach, bulk email/SMS, cold-call campaigns, or public issue-based lead collection.
- Human review and explicit approval are required before external outreach.
- A missed call is not consent to send a text. Any messaging requires documented permission, opt-out/suppression, quiet hours, frequency limits, applicable carrier registration, delivery reconciliation, and a tested stop mechanism.
- No paid vendor, domain, phone number, hosting, or infrastructure spend without explicit amount-bounded approval.
- Do not collect customer PII during discovery. Use fictional demo records.

## 9. Product scope discipline

For the first validation cycle, prioritize a truthful, human-reviewed workflow:

- opportunity / follow-up task capture;
- owner and due date;
- estimate follow-up status;
- customer-approved next action;
- audit trail and simple aggregate reporting.

Do not add live SMS, AI voice, automatic bookings, CRM migration, or broad multi-industry support merely to make the demo look complete. Expand only when interviews and a willing customer demonstrate the need and the required safety gates can be met.

## 10. Decision gates

**Discovery GO:** at least 10 consented conversations or a documented reason to revise the sample; one clearly recurring problem; evidence of a reachable buyer; and an agreed next step from qualified prospects.

**Build-next GO:** a repeated workflow need across multiple businesses, a credible integration path, conservative positive unit economics, and a narrow implementation scope.

**Paid-pilot GO:** every relevant requirement in `src/autopilot/commercial_release_gate.py` has independently verified evidence, plus customer-specific written authorization and a human-approved release decision.

**Stop / revise:** no meaningful pain, no willingness to pay, high support burden, weak economics, unworkable consent/integration, or inability to deliver reliably.

## 11. First ten paying customers — definition of done

The milestone is achieved only when ten distinct businesses have:

- a signed/accepted scope and service terms;
- a real, authorized customer account;
- successfully provisioned and verified service;
- an actual recurring payment collected;
- working cancellation and support paths;
- a documented first renewal / retention state.

Do not claim ten customers from waitlist signups, interviews, free pilots, test-mode Stripe events, or unverified checkout events.

---

**Operating principle:** Find the customer pain first. Build the smallest workflow that solves it. Verify delivery. Then compound recurring relationships.
