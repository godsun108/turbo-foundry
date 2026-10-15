# Foundry Checkout — Test-Mode Payment Reconciliation

**Status: offline Stripe-style webhook processing only.** Not a hosted app, real Stripe Checkout Session creator, payment processor endpoint, live billing, contract service, or deployed onboarding system.

## What is implemented

`src/autopilot/stripe_test_checkout.py` validates HMAC-SHA256 `Stripe-Signature` `t`/`v1` with a five-minute timestamp tolerance, rejects payloads without matching signatures, rejects livemode events, and only processes `checkout.session.completed` events where `payment_status=paid`, `mode=payment`, and full amount/currency/previously server-registered test Checkout Session match. SQLite writes are transactional and deduplicated by event ID and already-paid order state. Synthetic tests validate replay, tampering, unknown sessions, mismatched charges, unpaid/incorrect mode, and durable state after restart.

## What this does NOT do

- It does not create Checkout Sessions, process cards, authenticate buyers, verify Stripe account ownership, or establish real settlement.
- `register_test_order` is a trusted-backend-only setup helper; allowing a buyer to choose `session_id`, `expected_amount`, `order_id` or `currency` destroys the trust boundary.
- The code does not store a versioned accepted contract, an authenticated customer identity, bank receipts, refunds, disputes, subscriptions, tax, invoices, completed onboarding or an activated service.
- The current ledger checks only a test-mode Session completion event. Real integration must also support asynchronous-payment success/failure, expiration, partial/full refunds, disputes, subscription lifecycle (if approved), Stripe API reconciliation, and out-of-order delivery.
- A forged caller-supplied secret, webhook event, claimed `trusted_webhook` Boolean, or browser redirect cannot establish a real payment. Production requires the Stripe-issued signing secret stored safely in server configuration, TLS webhook endpoint, account/environment checks, official Stripe SDK signature validation where appropriate, and independent provider verification.
- A verified payment does **not** mean authorization to send an SMS or deploy a customer's automation.

## Next work required before accepting any payments

1. Establish secure hosted identity and business/tenant accounts, DNS/TLS and encrypted database. Do not expose local SQLite controls to user-supplied requests.
2. Approve one product's exact deliverability scope, costs, price, contract/cancellation/refund, support owner, and data policy.
3. Create a **test-mode** Stripe product/price and backend-only Checkout Session from an accepted scoped order, returning the Stripe-hosted URL. Do not accept arbitrary amounts from browsers.
4. Use a public HTTPS Stripe webhook with raw-body verification, durable event dedupe, explicit account/environment, payment-status reconciliation and test event fixtures; confirm in actual Stripe test mode.
5. Implement authenticated multi-step customer onboarding, secure provider OAuth and trusted runtime/consent approvals.
6. Run security, performance, privacy, compliance and failed-payment recovery tests; independently approve any live launch. No charge before an offering can be fulfilled.

See `docs/autopilot/self-service-sales-funnel.md` and `commercial-readiness-audit-2026-10-14.md`.
