# Foundry: first-customer operational readiness audit

Audit date: 2026-10-14
Scope: public showcase on `main`; offline Autopilot draft branch. This document is an engineering/product audit, **not a security certification or production authorization**.

## Decision

**DISCOVERY: possible with manual, privacy-aware conversations and truthful research-stage disclosure.**
**CONNECTED PILOT: NO-GO.**
**LIVE CUSTOMER MESSAGING / PAYMENTS: NO-GO.**

Current public showcase offers only a fictional missed-call demonstration and four concepts. It explicitly does not accept private leads, credit cards, or provisioning requests. The draft branch contains offline tests and a synthetic gateway rehearsal. These are valuable **engineering proofs**, not evidence of a revenue-generating service.

## The first offer

**Missed-call follow-up decision support for one opt-in local service business.** Start with a consultative demonstration using entirely fictional data. During discovery, ask how many calls go unanswered, current manual follow-up methods, whether the business already has lawful consent to contact customers, how staff track follow-up, and the operational value of faster response. Do not request or upload real caller details to GitHub or the public demo.

A live automated SMS product is **not** authorized or technically demonstrated. A manual/no-message research pilot is a distinct offer from live missed-call automation; do not describe one as the other.

## P0: first-customer discovery (no external spending)

1. Human operator identifies **one** willing local business via existing relationships or explicitly approved outreach. No unsanctioned cold email, bulk messages, scraping of private contacts, or automated public issues.
2. Hold a 15-minute workflow interview and record **non-sensitive aggregates only**, with permission. Do not collect customers' names, phone numbers, call recordings, logins, or private call histories.
3. Confirm a clear success metric (e.g. minutes spent checking missed calls, follow-up latency, or number of manual tasks in a fictional walkthrough). Establish actual baseline before stating savings.
4. Show fictional demo on the public site and ask for an honest evaluation. Record objections, alternatives and willingness to pilot. **No claimed ROI, recovery rate or guaranteed conversion.**
5. Produce a short anonymized discovery summary and decide whether a human-reviewed manual pilot could deliver value without SMS integration.

**Exit evidence:** one real conversation (with consent), observed current workflow and baseline, named business problem, identified decision-maker, requested next step, and honest go/no-go decision. Do not post identifying prospect details in this public repo.

## P1: prerequisites for any live, connected pilot

- Written customer authorization, verified ownership of test/provider account, and permission for precisely scoped operations.
- Provider account-bound test with real SDK semantics, approved cost exposure and safe credentials; present synthetic integration is not enough.
- Independently authenticated hosted runtime with tenant isolation and tested failure/recovery behavior. `wsgiref` and GitHub Pages are not production hosts.
- Consent and opt-out design, messaging regulatory review, quiet hours, frequency caps and double-send prevention; a missed call **does not imply SMS permission**.
- Security assessment of direct-code bypass, stop-versus-read races, token theft, immutable auditing, backup/restore and deletion/retention.
- Reviewed commercial terms, service support, cancellation, data processing agreement, pricing and payment flow. Stripe test ledger does not authorize production payments.
- Actual delivered outcomes and reconciliation, including downtime and cost tracking, before claiming reliability.

**Exit evidence:** explicit human approval and the independent verified references required by `commercial_release_gate.py`. A self-filled JSON report is not sufficient.

## P2: postpone

Additional channels, more provider adapters, multi-agent autonomy, AI voice receptionists, large product catalogs, fully automatic signup/billing, multi-region uptime, a dedicated mobile app, and new brand/domains are **not prerequisites for one discovery conversation**.

## Stop-doing rule

Until one actual discovery conversation occurs, stop creating new offline components unless they repair a demonstrated blocking defect in the current demo. The highest-value work is offer validation, secure operating design, and evidence gathering.

## Minimum one-page interview worksheet

- Business type and its current missed-call handling (non-sensitive summary):
- Approximate weekly missed-call volume (customer estimate; mark as unverified):
- Current follow-up time and staffing:
- Current customer contact permission and opt-out process (describe policy, not actual contacts):
- Most expensive manual step:
- Decision-maker and willingness to test an **offline, fictional** demo:
- Willingness to pay for a **future** verified service, not a presently offered subscription:
- Next step/date, consent to follow up:
- Evidence gaps and NO-GO flags:

No business identifiers, contact details or credentials belong in public GitHub issues.

## Supporting repository evidence

- `showcase/index.html` on main: demo-only sales framing and public feedback link.
- `src/autopilot/commercial_release_gate.py`: separate discovery and live pilot requirements.
- `src/autopilot/gateway_release_rehearsal.py`: fictional local lifecycle evidence.
- `docs/autopilot/gateway-release-rehearsal.md`: explicit production limitations.
- `docs/autopilot/first-customer-pilot-proof-report.md`: offline release assessment and human verification requirement.

**Truth before theater. Evidence before confidence. Operational before victory.**
