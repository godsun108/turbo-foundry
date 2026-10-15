# Foundry purchase-to-fulfillment v0 — offline rehearsal

**Status: test only. There is no working customer checkout, live activation, or delivered commercial service.**

The shared synthetic fulfillment ledger in `src/autopilot/synthetic_fulfillment.py` reuses existing `TestCheckoutLedger`, `AccountOwnership`, `OnboardingInvites`, and `universal_business_templates` rather than creating another billing, onboarding or industry system.

## What the rehearsal proves

A trusted local test fixture registers a Stripe **test-mode** order and a fictional account. Only the already implemented signed synthetic webhook can mark the expected order as test-paid. Account ownership and a completed, one-time onboarding invitation are verified before a fictional industry/workflow configuration can enter the fulfillment ledger.

The ledger records ordered transitions:
`prepared -> reviewed -> simulated_delivered -> stopped`. It rejects wrong owners, mismatched industry, unsupported workflow, unpaid orders, missing onboarding, skipped or repeated transitions, and unapproved transition names. SQLite persistence records each transition.

`simulated_delivered` is an **internal rehearsal state only**, never a claim of customer delivery. Every report has `service_delivered_to_customer: false`, `real_payment_processed: false`, `live_customer_activated: false`, and `production_ready: false`.

Run:
```sh
python -m unittest discover -s tests -p 'test_autopilot_synthetic_fulfillment.py' -v
```

## What has not been built

Real payment session creation, production signed webhook endpoint with lifecycle handling, transaction refunds/subscriptions, authenticated private customer portal, actual industry-specific provider setup, secure independent runtime, scope/consent verification, live SMS opt-outs, delivery monitoring, incident response, commercially approved contracts and customer support are still required.

This ledger is not a trusted public API: an operator with local database/Python access can bypass controls, and the incoming account ID must originate from an independently authenticated session. The `reviewed` state is claimed by the test caller, not independently authenticated human approval. The system does **not** verify external delivery, send messages, or bind to a live vendor.

## Operational path before offering a paid service

1. Approve Foundry-branded domain and verify actual ownership/renewal cost before publishing any custom mailbox.
2. Establish a verified private sales/support channel and independently tested inbound/outbound delivery.
3. Define exactly one service's scope, price, fulfillment SLA, exclusions, authorization requirements and cancellation/refund terms.
4. Verify live provider integration only with written customer approval, completed privacy/regulatory review and known usage costs.
5. Establish secure runtime, separation of customer accounts, recoverability, monitoring, escalation and irreversible payment/audit evidence.
6. Prove real functionality for an authorized pilot with human supervision before enabling a general checkout button.

No new subscription, domain purchase, external outreach, customer enrollment, metered provider traffic, real payment, or public deployment occurred in this sprint. See GitHub issue #9 for live-service release gates.
