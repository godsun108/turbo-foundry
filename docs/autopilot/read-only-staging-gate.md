# Read-only staging release gate (NOT approved for deployment)

Status: **CI passed on `2dcf1d66dfa713d38e99b14c81fe37841ec1ed40`; staging and security review still blocked**. A new commit requires fresh CI verification.

## Preflight
- [x] Both Foundry CI and Autopilot unit tests passed on `2dcf1d6` (runs 38583553662 and 38583553651). Reverify on any newer release candidate.
- [x] The previous GitHub Actions queue cleared; both jobs executed successfully on the verified commit.
- [ ] Confirm worker tests: concurrent claims, expired leases, database failures and delayed provider records.
- [ ] Pin trusted server clock, verified Twilio AccountSid and credentials; never accept client-provided pager, time, tenant, or provider account identity.
- [ ] Ensure durable SQLite storage, schema migrations, backups, and one shared database for queue, lease, and observation tables.
- [ ] Configure bounded pagination, request timeouts, rate limits, retries and logging without sensitive credentials.
- [ ] Add an operator kill switch and metrics for failed observations, stale leases, exhausted retries and pagination errors.
- [ ] Prove read-only operation in a sandbox and confirm no SMS provider send, billing charge, or live webhook mutation.
- [ ] Manually review consent, opt-out, tenant isolation and number provisioning before messaging authorization.

## Worker disable gate
The read-only `run_recheck` worker defaults to `enabled=False` and rejects all values other than the literal boolean `True`. An operator-controlled, trusted authorization boundary must explicitly enable the worker for sandbox/staging tests. This is a per-invocation guard, **not** a remotely managed kill switch or an operational staging service; do not treat it as either. No live provider calls are approved by this change.

## Release controls
The current run_recheck is an injected offline callable, **not a scheduled service**. Settlement means *review only*. No production deployment, customer SMS, or billing is authorized by this document. Preserve draft PR status until tests and human approval are complete.

## Next isolated staging rehearsal (not yet executed)
1. Use a disposable local SQLite database and synthetic tenant/call IDs. Do not connect a live Twilio client or load production credentials.
2. Run the unit tests with `python -m unittest discover -s tests -p 'test_*.py' -v` on the exact candidate commit; confirm all required tests execute and pass.
3. Exercise `run_recheck` first with its default disabled state, then with `enabled=True` and an injected offline pager only. Verify no provider requests when disabled, tenant-scoped observations, bounded retries and no outbound SMS.
4. Record the commit SHA, test logs, expected/actual observations, and any errors. Preserve logs without secrets or real caller numbers.
5. Separately review storage backups, trusted account-bound credentials, operational kill switch, monitoring, and compliance before requesting authorization for any real-provider staging access.

**Exit criteria:** green exact-commit CI plus documented offline rehearsal and explicit human approval. Passing CI alone does not satisfy staging readiness.

## Persistent operator control (offline safeguard)
`WorkerControl(db_path)` persists a default-off `read_only_recheck` flag in SQLite. The required `control=` parameter to `run_recheck` blocks processing before provider access when the flag is absent, off, unreadable, or malformed. The caller must still pass `enabled=True` explicitly. All worker invocations must supply a trusted `WorkerControl` instance; no control means no provider access. This is a per-invocation persistent gate, **not yet a centrally administered emergency-stop service**. It does not interrupt already-running provider requests, and revocation races require further testing.

## Mid-request stop rehearsal
The worker now rechecks its persistent control after injected provider pagination returns, before recording an observation or consuming a retry attempt. Offline regression tests cover disabling the control during both successful and unsuccessful pagination. **Limitation:** this is not an atomic stop-versus-commit fence; revocation between the second check and a database write is still a race, and an in-flight provider request is not canceled. A transaction-scoped control check is required before asserting complete revocation safety.

## Atomic stop-versus-observation fence
`commit_observation` now requires a trusted `WorkerControl` for the same SQLite database and checks the persisted enabled flag inside `BEGIN IMMEDIATE`, before writing observations or advancing the job. This serializes observation commits against `WorkerControl.set_enabled(False)` on the same database. If the stop transaction commits first, the observation commit refuses to write; if an observation transaction wins the lock first, it may commit before the stop takes effect. This **does not cancel provider requests already in progress**, and incomplete-pagination retry advancement through `RecheckLeases.finish` is **not yet transaction-fenced against revocation**. Offline tests are necessary but not production authorization.

## Retry-path transactional stop fence
`RecheckLeases.finish` now also requires a trusted `WorkerControl` referencing the same database. Inside its `BEGIN IMMEDIATE` transaction it checks the persisted enabled flag before consuming a retry or completing a job. Both normal incomplete-pagination and unexpected-exception worker paths supply the control; separate tests reject stopped, missing, and foreign controls. This protects retry state only through `finish`; other queue methods and direct maintenance operations are outside this gate. A stop does not cancel already running provider network requests or erase previously committed evidence. Fresh CI results must be checked before considering this change verified.

## Stop-transaction concurrency regression
`tests/test_autopilot_stop_race.py` verifies offline that a previously committed stop blocks both observation persistence and retry completion; it also exercises a stop update blocked behind an active SQLite writer transaction and verifies that a later observation cannot commit after the stop completes. This is a narrow SQLite serialization test, **not** proof of cancellation of active provider requests or an exhaustive concurrent interleaving model. These tests use synthetic identifiers and no live provider access.

## Guarded lease claim
The read-only worker now supplies its mandatory persistent control to `RecheckLeases.claim`. With a control supplied, lease acquisition checks the enabled flag inside `BEGIN IMMEDIATE`, serialized with operator stop updates in the same SQLite database. Missing control tables and mismatched database references fail closed. **Direct maintenance calls that omit `control` remain available** and must never be used to launch provider work. Stopping after a lease claim may still allow an in-flight provider read; final observation and retry writes are separately transaction-fenced.

## Read-only operator metrics (offline implementation)
`snapshot_recheck_metrics(db_path, tenant_id, now=...)` returns tenant-scoped counts of pending/due/complete/exhausted jobs and active/expired leases, from a SQLite read-only connection. It rejects naive timestamps and missing database files rather than creating an empty database. The counts describe persisted state only: an expired lease is a candidate for investigation, not proof of a failed provider operation. This is **not** a deployed dashboard, polling service, alert, or remotely accessible operator console. The caller must authenticate and authorize tenant identity outside this helper. No real provider or customer data is accessed by the tests.
