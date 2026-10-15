# Foundry Identity + Trusted Dispatch — offline session rehearsal

**Scope:** local-only, no-cost, read-only security experiment. **No public login, live authentication, provider integration, customer activation, payments or SMS.**

`gateway_local_sessions.py` adds a narrow session resolver over `AuditedGatewayReads`. A privileged local setup issues a cryptographically random 256-bit token for a configured operator. The SQLite session ledger stores **SHA-256 token digests**, not tokens; a request resolves the operator identity from its token instead of accepting a caller-provided identity. Expiry, revocation and the server-side operator-to-tenant mapping remain enforced. The underlying audited gateway requires a persisted tenant/provider/parent binding and records a read intent before adapter dispatch.

Use tests without secrets or connectivity:
```bash
python -m unittest discover -s tests -p 'test_autopilot_gateway_local_sessions.py' -v
```

## Verified only if exact-commit CI passes

- Fresh session reads fictional call history via server-side operator resolution.
- Wrong-tenant, missing-binding, unknown-operator, invalid-token, expired and revoked-token requests are denied.
- Reopened SQLite sessions retain their state; database read failures deny a request.
- Removing an operator from a trusted runtime mapping blocks previously issued sessions.

## Critical limits

**Issuing a token is NOT proof of who holds it.** `issue()` is privileged local setup without an identity-verification ceremony, password, MFA, CSRF prevention, replay-resistant token binding or a user-facing login. A caller who steals a token can use it until expiry or revocation. This is not a production authentication server. `LocalGatewaySessions`, `AuditedGatewayReads` and the lower-level gateway are importable from the same process, so any caller with arbitrary Python execution or database access can bypass these logical boundaries. There is no independently secured network service, TLS, durable immutable audit, device management, distributed rate limiter or full threat model.

Do **not** place bearer tokens or operator IDs in GitHub commits, build logs, URLs or public issues. A real service needs secure cookie/session handling, identity verification, trusted account provisioning, centralized authorization, encrypted storage, independent provider account verification, operator stop fencing, validated secrets lifecycle, and secure deployment review. The present gateway still exposes direct `observe()` calls and **does not apply the worker stop control**; no live provider credentials are authorized.

The commercial release remains **NO-GO**. No new infrastructure spending or provider activity was initiated.
