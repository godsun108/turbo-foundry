# Foundry Portal — Integrated Staging Preview

**Status: runnable application preview, not a customer signup or payment website.**

Run locally:

```sh
python -m src.autopilot.portal_app
```

Browse http://127.0.0.1:8080/ for the mobile-friendly interactive customer journey. The app exposes `GET /api/offers`, `GET /api/readiness`, and `GET /healthz`. Every POST is rejected with HTTP 405. No form submits data and the checkout button remains disabled. There is no customer identity, persistent signup storage, payment, SMS, hosting, or mail delivery.

A deployment preview **must be prominently labeled as a preview**. Server header restrictions reduce accidental embedding/cache, but the stdlib WSGI server is a development server, not a hardened public production server. Do not expose it as-is to the public internet or collect any actual customer information.

## Hosting and next gates

The Railway connection has existing projects, but no dedicated Foundry project was present at the 2026-10-14 review. Creating a new Railway service or using GitHub Actions runners can incur billing. **No service has been created or deployed by this sprint.**

Next steps in order:
1. Verify both CI jobs for the exact portal commit.
2. Choose hosting budget and domain identity, and provision a **staging** environment only after consent.
3. Replace the development WSGI server with a maintained WSGI stack and place TLS, security headers, logs with no PII, health checks, deployment smoke tests, least-privilege filesystem and secrets protection around it.
4. Implement real hosted authentication, tenant authorization, contract/versioned acceptance and secure storage.
5. Integrate Stripe **test-mode** Checkout Sessions via backend-owned prices and a verified webhook, not browser callbacks or synthetic Stripe signatures.
6. Add private customer onboarding screens, per-tenant OAuth integration and a guarded operator fulfillment queue.
7. Test a realistic sandbox purchase, failed-payment path, refund/chargeback, double callbacks, contract rejection, account takeover prevention, backup recovery and stop-control behavior.
8. Require separate approval and demonstrated ability to fulfill before any live payments, email/SMS, or production activation.

The page's optional local fields are only client-side preview content. Do not ask customers to enter sensitive information or tell them they have purchased a service.
