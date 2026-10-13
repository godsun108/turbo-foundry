# Telephony provider sandbox integration plan

## Required selection
Choose a provider (e.g., Twilio) and confirm account access, supported inbound-call status events, messaging test capabilities, and regional compliance requirements.

## Engineering phases
1. Provision test credentials and a nonproduction callback endpoint. Never commit secrets.
2. Implement provider-specific request authentication exactly as documented, including URL and headers when required. Do not reuse the custom mock HMAC protocol.
3. Map provisioned destination numbers to tenant configuration on the server; reject unknown numbers.
4. Verify missed-call semantics using provider statuses; do not treat every completed call as missed.
5. Read consent and suppression from trusted tenant-scoped records; do not accept consent claims from event payloads.
6. Normalize provider event IDs and timestamps and enforce deduplication.
7. Dispatch only via explicitly authorized sandbox mode, reconcile provider message IDs and callbacks, and fail closed on unknown outcomes.
8. Add replay, tampering, cross-tenant, opt-out, quiet-hours, and outage tests.
9. Require human sign-off, compliance review, and cost caps before any real customer messaging.

## Existing modules
- `webhook.py`: custom signed mock protocol; NOT a provider adapter.
- `ingest.py`: offline orchestration; consent currently supplied by the local test harness.
- `delivery.py`: simulated delivery only.
- `reconciliation.py`: persisted recovery decisions, not yet tied to real provider callbacks.

No sandbox provider account or live endpoint has been configured by this document.
