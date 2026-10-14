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
