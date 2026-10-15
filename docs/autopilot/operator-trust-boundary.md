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

## Sprint 87: POSIX deployment preflight (CI verification pending)
`check_sqlite_isolation` passively inspects an existing SQLite state file, its parent directory, and optional WAL/SHM/journal sidecars. It flags non-regular files or symlinks, group/other permission exposure, missing paths, and optional owner mismatches. The preflight never alters permissions and cannot read credentials or contact a provider. Offline tests cover private state files, permissive modes, symlinks, sidecars, missing files and wrong owner IDs.

**Critical limitation:** A clean preflight **does not establish independent operating-system principals or prevent code running as the writer account from opening a writable connection**. The preflight examines only the immediate parent directory, not ancestor path components, mount ACLs, containers, supplementary groups, backups, or remote volumes. Actual deployment still requires a separate privileged writer process/service identity, an unprivileged reader account, OS-level permission tests using both identities, and a tightly controlled authenticated control API. Connected staging remains **NO-GO**.

## Sprint 88: opt-in two-identity POSIX isolation rehearsal
`tests/test_autopilot_posix_identity_isolation.py` adds a **privileged, explicit opt-in** subprocess test. On a disposable POSIX host running as root with `AUTOPILOT_RUN_PRIVILEGED_ISOLATION=1`, it creates a private SQLite database, drops a child process to the OS `nobody` account, verifies the child cannot modify the database, and verifies the control value is unchanged. The test defaults to **SKIPPED** in ordinary CI. A green routine CI run therefore confirms test discoverability but **not execution of two-UID isolation**. Record explicit privileged rehearsal logs, hostname/OS, process UIDs and permissions before making any actual two-identity isolation claim. Never run this as root inside a production service; use an approved disposable VM. Security review must separately verify ancestor directories, mounts/ACLs, distinct reader/writer accounts, network/process exposure, and audit protection. The unprivileged monitor should not be given the writer SQLite database at all; deliver sanitized read-only metrics through a narrowly authenticated interface instead.

## Sprint 89: operator-triggered ephemeral Linux isolation rehearsal

The repository includes `.github/workflows/autopilot-isolation-rehearsal.yml`. It has **only** `workflow_dispatch`; push, PR and scheduled events cannot start the privileged test. An operator must select the feature branch and enter `RUN_DISPOSABLE_ISOLATION` as the required confirmation to start it. On an ephemeral GitHub-hosted Ubuntu runner, the workflow executes one synthetic SQLite permission test via `sudo`, with no secrets configured, no provider access, SMS or billing. **The workflow has been authored but has not been triggered.**

### Before approving a manual run
1. Review the exact selected commit and workflow file for unexpected commands or changed permissions.
2. Confirm a GitHub-hosted disposable runner is used, not a production/self-hosted runner.
3. Confirm workflow permissions remain `contents: read`, no application secrets are passed, and the test is the only privileged operation.
4. Manually trigger the workflow and retain its run ID, selected commit SHA, root/child UID evidence and full test output.
5. Require a successful, **non-skipped** test outcome. Routine unit-test green status is not proof of a privileged isolation result.

Even after success, a separate deployable two-service boundary, tenant/account authentication, securely managed database credentials and operational review remain prerequisites for connected staging.
