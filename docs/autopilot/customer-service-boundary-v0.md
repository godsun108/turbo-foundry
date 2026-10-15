# Foundry Customer Service Boundary v0 — synthetic only

This sprint reuses the existing offline order ledger, account/order ownership registry, checkout test fixture, and synthetic fulfillment state machine. It does **not** create a second checkout system or customer database.

## New capability

`src/autopilot/synthetic_customer_portal.py` provides an internal **read-only** customer status facade. A privileged test fixture can issue a short-lived random opaque capability token for a fictional account. Only the token hash is persisted. For a status request, the facade resolves the account from the token server-side, verifies that the requested order belongs to that account, and returns only the order ID, synthetic state, and explicit `false` flags for live activation, customer delivery, real payment, and production readiness.

Invalid, expired, revoked or cross-account sessions fail closed. Unavailable SQLite session storage fails closed. There is no customer-facing URL, public login, SMS sender, payment API, mutable customer endpoint or hosted service.

## Reproducibility

```sh
python -m unittest discover -s tests -p 'test_autopilot_synthetic_customer_portal.py' -v
```

## Hard production blocker

**The privileged fixture issuer is not authentication.** Any code with trusted Python/database access can mint capabilities. The `order_id` is requested by the caller but authorized using the server-resolved identity; no tenant identity is accepted from the request. There is no TLS, secure cookie session, rate limits, verified customer enrollment, managed secret storage, network isolation, customer data lifecycle, immutable audit, production hosting, account recovery or independently verified service fulfillment.

Before exposing this status API publicly, establish an independent authentication provider or hardened session service, a trusted authenticated HTTP boundary, secure data and credentials, revocation and support procedures, and independent security review. A real provider must be connected **only** after written authorization, verified account ownership, regulatory/consent review and cost approval. Existing provider mocks do not establish deliverability.

Domain and Foundry-branded email are still unpurchased/unconfigured. Checkout, production activation and customer messaging remain disabled; all development is on the draft engineering branch. **Live service: NO-GO.**
