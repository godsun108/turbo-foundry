# Foundry offline identity → audited dispatch rehearsal

**Status: synthetic and local only. No public login, messaging or payments.**

`src/autopilot/gateway_offline_identity.py` adds a privileged local demonstration of a credential check before session issuance. Test credentials are injected at startup, hashed with per-operator random salts using scrypt, and compared in constant time. The existing SQLite attempt quota rejects repeated login attempts (including valid logins once the quota is reached). On successful credential comparison, the existing `LocalGatewaySessions` issues a random expiring session token, stored as a digest in SQLite.

The `tests/test_autopilot_gateway_offline_identity.py` rehearsal runs fictional business call histories through credential check → token issuance → tenant and parent authorization → SQLite intent audit → read-only gateway, then tests logout/revocation, session expiry, wrong tenants/parents, an incorrect user, persistent failed-attempt throttling and ledger write failure.

Run without networking or any service credentials:

```bash
python -m unittest discover -s tests -p 'test_autopilot_gateway_offline_identity.py' -v
```

## Boundaries, risks and commercial readiness

This is NOT production-grade identity verification. The operator credentials are synthetic static strings injected by a privileged caller, not credentials securely enrolled by a real person. The module does not implement phishing-resistant MFA, TLS/cookies, IP throttling, secure account recovery, rotation, account lifecycle, session theft defenses, audit immutability or independent provider ownership verification. Recreating the process with another supplied password may replace the verifier, so this is not a deployable identity service. The underlying session issuer and `ReadOnlyGateway` can be called directly by Python code with sufficient process access. Audited reads cannot be used as a security boundary against untrusted code running in the same process.

No public HTTP interface is provided; never expose `login()`, `issue()` or direct adapter calls to the internet. The existing gateway does not yet enforce the persisted worker stop control. Before a customer pilot, implement an actually isolated authenticated runtime, service-side tenant resolution, signed/immutable logs, provider ownership, consent review, security testing and operating procedures. The release decision remains **NO-GO**.

No new services, billable APIs, live messages, payment operations or customer data were created.
