# Read-only staging release gate (NOT approved for deployment)

Status: **blocked until CI and security review pass**.

## Preflight
- [ ] Both Foundry CI and Autopilot unit tests pass on the exact candidate commit.
- [ ] Resolve any queued GitHub Actions runner/capacity problem before interpreting results.
- [ ] Confirm worker tests: concurrent claims, expired leases, database failures and delayed provider records.
- [ ] Pin trusted server clock, verified Twilio AccountSid and credentials; never accept client-provided pager, time, tenant, or provider account identity.
- [ ] Ensure durable SQLite storage, schema migrations, backups, and one shared database for queue, lease, and observation tables.
- [ ] Configure bounded pagination, request timeouts, rate limits, retries and logging without sensitive credentials.
- [ ] Add an operator kill switch and metrics for failed observations, stale leases, exhausted retries and pagination errors.
- [ ] Prove read-only operation in a sandbox and confirm no SMS provider send, billing charge, or live webhook mutation.
- [ ] Manually review consent, opt-out, tenant isolation and number provisioning before messaging authorization.

## Release controls
The current run_recheck is an injected offline callable, **not a scheduled service**. Settlement means *review only*. No production deployment, customer SMS, or billing is authorized by this document. Preserve draft PR status until tests and human approval are complete.
