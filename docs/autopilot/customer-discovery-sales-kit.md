# Foundry — Customer Discovery Sales Kit (draft, not a live product)

All materials are for transparent, voluntary business discovery. **No live SMS, service delivery, billing, or payment request is authorized**. Do not publish misleading claims of results or readiness.

## Static portfolio preview

From the repository root run:

```sh
python -m src.autopilot.portfolio_page
```

This writes `foundry-portfolio-preview.html` locally. Open that file in a browser to review. It renders all five offerings with explicit *offline demo* or *concept* labels and contains **no customer form, tracking script, external assets, checkout or call-to-action that pretends a product is already live**. Do not publish this preview as an operational production service. Review brand, privacy, accessibility and messaging before public release.

## Fifteen-minute discovery meeting

**Opening (1 minute):** “We’re developing practical automation for service businesses. We have an offline demonstration of a missed-call workflow and are researching other use cases. Could I ask how your team currently handles inbound inquiries?”

**Listen (6 minutes):** Ask what inquiries are missed, which actions staff repeat, how frequently, current software and ownership, whether permission exists to use customer contact data, and what a meaningful improvement would be.

**Demonstrate (4 minutes):** If missed calls are relevant, run `python -m src.autopilot.demo` using fictional events and explicitly state **zero real SMS, zero recovered leads and zero actual revenue**. For the other concepts, present only workflow diagrams/ideas.

**Qualify (3 minutes):** Ask for the decision maker, a rough monthly volume, cost of delays, integration constraints, permission and opt-out method, success criteria, and willingness to consider a later approved pilot.

**Close (1 minute):** Agree on one next step: a follow-up workflow map, permission to prepare an estimated proposal, or no follow-up. Do not pressure the prospect or promise an unbuilt feature.

## Discovery notes template (keep confidential and out of Git)

- Business / industry:
- Decision maker (record contacts only with permission):
- Date and consent to follow up:
- Most expensive repeated task:
- Monthly volume and evidence source:
- Current provider / CRM / calendar:
- Customer contact consent / privacy constraints:
- Manual workaround and estimated costs:
- Desired outcome and how to verify it:
- Budget expectations (stated by buyer, not inferred):
- Agreed next step and owner:
- Suitability blockers:

## One-page proposal template — **not for issue until approved**

**Business:** [Prospect] · **Prepared:** [Date] · **Status:** Evaluation proposal only

**Problem and baseline:** [Business-confirmed measurable process]

**Proposed workflow:** [Input → checks → human escalation → output], clearly labeled as concept, offline demonstration, or separately validated live integration.

**Systems and responsibilities:** [Customer-owned providers, authorized access, human owner, integration dependencies].

**Privacy and safety:** [Data minimization, consent and suppression, audit trail, failure-handling, data deletion policy].

**Acceptance criteria:** [Synthetic tests first; before go-live, approved end-to-end evidence with actual provider and business consent].

**Commercial terms:** [Only after approval: setup, fees, usage expenses, support, cancellation, refund terms and approved start date]. **Do not quote or charge without authorization.**

**Excluded scope:** [Unsupported features, regulated decision making, guaranteed appointments/revenue, unapproved messages].

**Next step:** [Schedule a technical scoping review; no integration, payment or messaging takes place from this document].

## Priorities

1. Three voluntary business discovery interviews.
2. One evidence-backed workflow and customer-authorized demo.
3. One realistic costed pilot proposal, subject to safety and delivery gates.
4. After explicit customer and operator approvals, one measured live pilot.
5. Only then begin packaging the next concept into a repeatable service.

References: `docs/autopilot/first-revenue-plan.md`, `automation-offer-portfolio.md`, `staging-readiness-assessment-2026-10-14.md`.
