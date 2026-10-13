# Provider integration gate (not yet production-ready)

The mock HMAC verifier is not a Twilio or other provider signature verifier.
Before enabling any real webhook or message, implement and test:

1. Provider-specific signature validation using the vendor's documented algorithm and raw request context.
2. Server-side tenant resolution by provisioned destination, never trusting a tenant identifier from the request.
3. Tenant-scoped consent evidence, opt-out synchronization, quiet hours, and regulatory review.
4. Provider request idempotency and delivery-status reconciliation.
5. Explicit unknown-outcome handling: hold or reconcile, never blindly resend.
6. Retry backoff, dead-letter queue, audit trails, secrets rotation, monitoring, and abuse/rate limits.
7. Sandbox tests with provider test credentials, including invalid signatures and duplicate callbacks.
8. Approved message templates, opt-out language, verified sending identity, and cost caps.
9. Authorized human approval before enabling real SMS or billing.

Current recovery.py is a pure decision helper, not an integrated provider adapter.
No real SMS, billing, or customer onboarding is enabled.
