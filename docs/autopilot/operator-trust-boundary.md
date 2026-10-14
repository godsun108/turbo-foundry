# Operator trust boundary — deployment blocker

Status: **NO-GO for any externally reachable operator API or real-provider staging.**
Baseline reviewed: 2026-10-14. All described checks are local/offline only.

## Boundary audit

- `OfflineOperatorEntrypoint.apply` checks a credential, local attempt quota, server-configured operator roles and an audited database control.
- `WorkerControl.set_enabled` is directly callable without authentication and **can bypass that entrypoint**. Legacy usage by offline fixtures remains intentionally supported. A passing credential test does not protect this direct method.
- The SQLite database is a trusted local resource. Any process with sufficient file access can directly update or delete control and audit rows; the local audit log is not immutable.
- Operator ID in a command is an unverified lookup key. Reusable secret strings are not a production authentication system. The local attempt quota is per operator ID, not globally rate-limited.
- `OfflineOperatorEntrypoint.apply` rejects invalid control objects before attempting to read their database paths. The regression suite explicitly demonstrates the direct method bypass so it cannot be mistaken for resolved risk.

## Required architecture before connected staging

1. Expose no public operator API while the direct mutation path remains available to untrusted execution environments.
2. Run all privileged control mutations in a separate trusted process/identity with exclusive write access to the SQLite database. Treat other processes and callers as untrusted; restrict filesystem permissions, runtime privileges and network access.
3. Require an authenticated identity provider or independently verified short-lived session, strong MFA for enabling workers, authorization from server-side roles, and CSRF/replay protection as appropriate.
4. Forward audit events to restricted, tamper-evident centralized storage. Define retention, rotation, alerting and break-glass procedures.
5. Replace test-oriented static secrets and injected clocks with managed secret distribution, rotation, safe time sources, and centrally enforced account-level limits.
6. Test that all externally reachable entrypoints cannot invoke `WorkerControl.set_enabled` directly, and confirm a revoked operator cannot change state through any available route.
7. Document and obtain explicit human authorization for any connected-provider staging run. Messaging and billing need independent approval.

## Immediate development rule

**Never equate credential checking in a helper with a security boundary when untrusted callers can reach the underlying mutation function.** Keep the PR draft, the worker off by default, and provider access, SMS, billing and production disabled.

## Sprint 86: explicit SQLite read-only view (CI verification pending)
`ReadOnlyOperatorView` connects to an existing SQLite database with `mode=ro` and exposes a state/audit-count snapshot without schema creation or mutation methods. Synthetic tests explicitly try to update the stop flag and delete audit records through this read-only connection; SQLite must deny both attempts. Missing files also fail without database creation. This demonstrates **connection-level read-only behavior only**. It does not prevent a process with filesystem permissions from opening a separate writable connection or calling `WorkerControl.set_enabled`; production isolation requires independent OS identities, file/directory permissions, and an authenticated writer service with a limited surface. No security approval or connected staging authorization is implied.
