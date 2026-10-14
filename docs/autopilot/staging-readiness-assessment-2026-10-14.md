# Foundry Autopilot — read-only staging readiness assessment

Assessment date: 2026-10-14
Verified baseline: `f129437e5960343ad0d7cef157fcc1826658830e`
Workflow evidence: Foundry CI run 38591405431 — success; Autopilot unit tests run 38591405479 — success.
Decision: **NO-GO for connected staging and customer pilot.** This report is a documentation-only assessment, not authorization.

## Evidence-backed offline capabilities
| Capability | Evidence | Classification |
| --- | --- | --- |
| Synthetic, disposable-database rehearsal | `tests/test_autopilot_offline_rehearsal.py`; included in passing unit-test workflow | Verified by CI, offline only |
| Default-disabled worker with persisted operator gate | `src/autopilot/recheck_worker.py`, `worker_control.py`, worker-control tests | Verified by CI, not a deployed operator service |
| Serialized gate at claim, retry finish, and observation commit | `recheck_leases.py`, `atomic_observation.py`, `test_autopilot_stop_race.py` | Verified regression coverage; not exhaustive race proof |
| Tenant-scoped read-only queue/lease counts | `recheck_metrics.py`, `test_autopilot_recheck_metrics.py` | Verified by CI, not an active dashboard or alert |
| Read-only Twilio SDK paging adapter and conservative evidence policy | `twilio_paging.py`, `provider_audit.py` and corresponding tests | Offline/tested code; no live-provider staging evidence |
| Review-only settlement | `settlement.py`, `recheck_worker.py` | Review signal only; never SMS authorization |

## Blocking gaps and required proof
1. **Connected provider staging approval and credentials.** No demonstrated authenticated, account-bound, least-privilege staging run with real Twilio read-only credentials, exact URL/signature checks, bounded timeouts, and verified provider-account scope. Requires explicit authorization before accessing any live provider account.
2. **Trusted runtime boundary.** Current worker takes injected `pager`, `now`, `tenant_id`, `call_ended_at`, and `control`. A real service must bind those to trusted operator configuration, tenant ownership, and the server clock; do not expose them as client inputs.
3. **Operational stop service.** The gate is persistent and transaction-fenced for tested paths, but there is no centrally authenticated operator console, audit trail, alerting, or cancellation of already-running network reads. Direct maintenance queue methods still bypass the worker gate.
4. **Durable hosting and recovery.** No approved persistence host, migration/backup/restore rehearsal, recovery-time objectives, retention/deletion policy, or verified multi-process operating procedure.
5. **Observability and incident handling.** Only snapshot helpers exist. Need secure operator access, metrics collection, incident alerts, runbook and secrets-safe logs. Validate stale leases, exhausted retries, provider rate limits and outage recovery.
6. **Messaging launch remains a separate gate.** Consent capture, opt-out reconciliation, lawful messaging requirements, frequency/quiet-hour policy, account provisioning, approved templates and end-to-end SMS controls require independent review. Read-only provider history never proves permission to message.
7. **Commercial launch.** No validated deliverability, customer onboarding, support process, conversion outcomes, pricing acceptance, or evidence of paying customers.

## Minimum next offline milestone
- Run exact-commit CI after any change and archive both run links.
- Add a synthetic end-to-end operator rehearsal that covers enabling, one read-only worker invocation, operator stop, subsequent rejected lease/observation/retry, metrics snapshot, and restart persistence.
- Add tests for gate corruption, storage failures, tenant isolation, and stop-versus-claim ordering.
- Record rehearsal output with synthetic identifiers, zero network/SMS/billing operations, and explicit pass/fail assertions.
- Keep the PR draft and connected staging blocked pending separate human review and approval.

## Release decision
**Offline engineering:** ongoing, passing baseline listed above.
**Connected staging:** **BLOCKED**.
**Customer SMS/billing/production:** **DISABLED / NOT AUTHORIZED**.

Operational before victory. Evidence before confidence. Truth before theater.

## Sprint 78: synthetic operator rehearsal added (verification pending)
`tests/test_autopilot_operator_rehearsal.py` exercises a disposable SQLite database, a counting offline pager, operator enablement, one persisted review-only observation, revocation, reopening the control object, a blocked subsequent worker invocation, and tenant-scoped read-only metrics. It asserts no second provider-adapter invocation after stop, no added observation, and unchanged retry attempts. This is an **automated synthetic rehearsal only**, not an independently deployed staging environment. Re-evaluate its status after CI passes on the exact new commit; previous passing workflows do not cover it.

## Sprint 80: offline SQLite recovery rehearsal (CI verification pending)
`src/autopilot/sqlite_backup.py` provides an offline SQLite backup helper using SQLite's backup API, a destination no-overwrite rule, restrictive file creation permissions, and `PRAGMA integrity_check`. `tests/test_autopilot_sqlite_backup.py` tests a disposable synthetic backup/restore of the persisted disabled worker control, previously recorded observation, due queue state, and tenant metrics. It also checks missing-source, same-path and overwrite refusal. This is **not** a configured backup schedule, encryption/key-management solution, retention policy, disaster-recovery deployment, or RPO/RTO validation. The backup helper's caller must separately control destination security, access, lifecycle and restore authorization. Connected staging remains NO-GO pending review. Confirm both CI workflows on the latest commit before treating the rehearsal as verified.

## Sprint 81: local operator-control audit (CI verification pending)
`WorkerControl.set_enabled` now records the requested new state, previous state, a timestamp, claimed actor string, and stated reason in `worker_control_audit` within the **same SQLite write transaction** as the stop-control update. A failed audit insert rolls the state update back. Tests cover disable/enable persistence, failed writes, input validation, and restart. Existing caller sites use the explicit `unattributed_local_caller` / `legacy_local_call` markers. **Identity is not authenticated**: actor strings are caller-provided claims. Records are local and can be edited by an actor with direct database access, so this is **not tamper-evident or a secure centralized audit system**. Production needs authentication, authorization, access controls, retention, immutable forwarding, and incident monitoring. Do not approve connected staging based on this alone.

## Sprint 82: offline operator authorization facade (verification pending)
`OperatorAuthorization` denies control changes for unknown operators and requires a `autopilot.worker.admin` role from a **trusted runtime-provided allowlist**, ignoring roles merely claimed by a principal. Permitted changes use `WorkerControl.set_enabled` and its transactional local audit. Offline tests cover deny-by-default, unknown identities, privilege claims, and authorized enable/stop. **This is NOT authentication**: callers can construct `OperatorPrincipal` objects, and direct calls to `WorkerControl.set_enabled` still bypass this facade. There is no authenticated service entrypoint, identity-provider validation, centralized roles, secret management, or protection against privileged local database access. Never attach this facade directly to untrusted web input. Connected staging remains **NO-GO** pending a trusted runtime and human security review.
