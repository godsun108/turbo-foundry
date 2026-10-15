# Foundry Universal Gateway — offline audited reads

`gateway_audited_reads.py` is a **local-only rehearsal** for a future trusted service boundary. It requires three independent local conditions before dispatching a read: a principal whose tenant access is found in a trusted process-provided allowlist, a persisted tenant/provider/parent binding, and a successfully committed SQLite read-intent audit event. If SQLite binding or audit is unavailable, the provider adapter is never invoked. Denied valid requests are also audited.

The suite tests legitimate synthetic reads, cross-operator refusal, unknown parents, invalid principal types, database failure and persistence without principal authorization.

## Limitations — NOT production authentication

- `TrustedReader(identity)` is caller-constructible, not an authenticated session or cryptographically verified identity. Do not expose its identity field as HTTP request data.
- `bind_parent` is privileged local setup, not a remotely secured provisioning API. A caller with Python/database access can bypass it and call `ReadOnlyGateway.observe` directly.
- SQLite audit is not immutable, complete, signed, encrypted or centrally replicated. It records *request intent* before dispatch, not successful completion; a crash or adapter exception requires separate operational reconciliation.
- No real provider account ownership or consent is verified; test IDs are fictional. Do not store caller identifiers/phone numbers in this demo audit database.
- No TLS, secure server sessions, role provisioning, secret manager, rollback across external providers, alerting or threat assessment. Existing worker stop controls are separate and are **not** automatically enforced by the gateway facade.
- No customer messaging, payment collection or automatic activation; customer pilot remains **NO-GO**.

Run: `python -m unittest discover -s tests -p 'test_autopilot_gateway_audited_reads.py' -v`.

Next meaningful milestone: independently authenticated session-to-tenant resolution and privileged provider account binding, with no raw user-chosen identifiers crossing into the trusted dispatcher. Then test audited dispatch across runtime failures and stop controls. Continue with no new paid services.
