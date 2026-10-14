# Foundry Customer Signup → Payment → Fulfillment

**Current status: functional offline preview + modeled state transitions only. NO public enrollment, checkout, payment acceptance, service activation, real-business data storage, or messaging.** Feature branch is still draft.

## Simplest future customer journey

1. **Select an approved, actually deliverable package.** Show specific included work, exclusions, provider requirements, estimated setup time, clear setup and monthly prices, fees and cancellation/refund policy. Unsupported concepts are visible only as a discovery/request-interest option, not purchasable products.
2. **Short pre-checkout eligibility form.** Business name, industry, problem, phone/CRM platform, country/state, existing sending-number ownership, scheduling needs, business contact email, and estimated usage. Do NOT request API passwords, payment cards, customer call logs, sensitive customer data, credentials or bulk contact lists in a public form. Confirm business decision maker and contact permission.
3. **Automated scope feasibility.** Rule-based eligibility and human review for uncertain cases. If integration is unsupported or consent cannot be verified, offer discovery/waitlist rather than checkout. Do not take money and then discover essential impossibility.
4. **Clear written agreement.** Quote accepted scope, delivery time/contingencies, responsibilities, price, recurring nature and cancellation/refund terms; store agreed version and timestamp using an authenticated backend. Require intentional acceptance, not a prechecked box.
5. **Stripe-hosted Checkout.** Backend creates a checkout session from its own approved price ID and order record. Never trust client-supplied price, offer eligibility or amount. Initially allow only a server-controlled release-eligible offer and configured test-mode products. No public payment links are created in this sprint.
6. **Independent Stripe payment verification.** TLS webhook endpoint validates raw-body Stripe signature and signing secret, rejects replay/duplicates, validates account, Checkout Session ID, local order ID, currency, full expected amount, status, live/test environment and fulfillment eligibility. Persist event idempotently in an atomic transaction before fulfillment work. Browser redirect is not payment evidence; asynchronous payment methods stay pending until verified. Never use a caller-supplied `trusted_webhook=True` flag as a real authentication mechanism.
7. **Secure post-payment onboarding.** Offer an expiring authenticated onboarding link to submit verified business ownership, phone and CRM authorizations via provider OAuth, required consent and opt-out evidence, escalation contacts, business hours, support preferences, data-processing agreement, and onboarding checklist. Avoid asking for raw API keys through web forms. Restrict stored records to tenant-scoped encrypted storage.
8. **Operator and release gates.** Queue account provisioning, consent review and provider tests. Require independently signed operator approval and deployment acceptance tests; do not auto-start messaging simply because payment succeeded. Give customer honest status, contact, ETA and a refund/cancellation path if requirements cannot be met.
9. **Delivery and support.** Verify test events, successful message sending only under approved permissions, opt-outs, duplicate suppression, real metrics, customer acceptance, and support/incident procedures; activate with auditable kill-switch control. Record real collected funds through reconciled provider records, never assumptions.

## Current offline artifacts

- `python -m src.autopilot.signup_preview` writes `foundry-onboarding-preview.html`, a phone-responsive interactive **local** walkthrough. Data stays in browser memory, never transmitted, saved, or sent. Checkout is intentionally disabled. Do not deploy this preview as a real registration form.
- `src/autopilot/customer_fulfillment.py` illustrates gate-checked order transitions from draft, accepted scope and checkout pending through payment, onboarding, review, approval and activation. It has no actual Stripe SDK or secure backend. Its `trusted_webhook` / `release_gate_verified` flags are **test-only representations**, NOT secure trust boundaries. A real server must derive trust from verified provider signatures, durable order state, authenticated administrators and actual evidence, rather than Boolean caller claims.
- `tests/test_autopilot_customer_fulfillment.py` proves key state transitions and invalid synthetic payment cases are rejected. It is NOT payment processing, auth or delivery proof.

## Architecture and security before launch

**Frontend (iPhone-first):** offers, prequalification, quote/contract, Stripe Checkout redirect, payment status, secure onboarding wizard, simple job status dashboard.

**Backend:** authenticated sessions; approved product/price catalog; eligibility and pricing authority; versioned agreement; Checkout Sessions; signature-verified event handler; idempotent order processing; tenant-owned onboarding documents; provisioning queue and operator approval; email notifications; support and cancellation.

**Storage:** distinct schema/tables for orders, accepted terms, exact quote/price version, payment event IDs, billing reconciliations, onboarding steps, tenant-authorized integration scopes, audit events, task outcomes, deletion requests. Sensitive data encrypted with managed keys; granular access control, backups, retention and credential rotation.

**Reliability:** retry-safe webhooks, idempotent activation, out-of-order event handling, failed/partial/refunded/disputed payments, cancellation and chargeback state, email failure, unsigned/forged callbacks, double-click checkout, abandoned checkout, expired sessions, expired OAuth permissions, unfulfillable paid accounts and refund workflow.

**Legal/commercial:** valid business details, applicable taxes, recurring billing disclosures, agreement acceptance and refund rights, privacy policy, data-processing terms, messaging rules, support contact/response time, processor obligations. Keep real automated outbound messages OFF until approved per tenant.

## Strict go/no-go

- **GO now:** offline usability demonstrations, prospect qualification, fake checkout flow tests, draft pricing research and customer journey design.
- **NO-GO now:** deploying this page for public data capture, real Checkout, recurring billing, automatically onboarding a paid account, Twilio sends, live provider operations, or claiming a complete SaaS product.

## Priority implementation sequence

1. Product/price and eligibility decision for a single actually fulfillable workflow; realistic delivery time/support obligations.
2. Authenticated hosted frontend/backend plus tenant-scoped data storage.
3. Secure, test-mode Stripe Checkout Sessions and verified webhooks with durable idempotency.
4. Contracts, secure onboarding link, OAuth integration, review/stop-service capabilities.
5. End-to-end customer testing, processor sandbox, recovery/privacy/compliance checks.
6. Independently approve limited live paid pilot; only then activate real Checkout and fulfillment.

No real orders or charges were created.
