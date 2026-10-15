# Foundry offline claim and crash recovery v0

The local-only `OfflineClaimLedger` adds a durable SQLite **mock** claim/receipt mechanism beside the existing `OfflineWorkflowRunner`. It is not yet wired into that runner's dispatch path.

- `submit` is idempotent by fictional tenant and job ID.
- `claim` atomically moves a due queued job to a leased claimed state; a competing claim fails.
- `complete` records a fictional receipt only while the claim is active and its token matches.
- `quarantine_expired` moves expired claimed work to `uncertain`, **not** queued. This prevents blind retries of work whose outcome cannot be proven.
- `cancel` only stops queued work. A claimed action cannot be assumed cancelled.
- `status` is scoped by fictional tenant and job ID.

Run `python -m unittest discover -s tests -p 'test_autopilot_offline_claim_ledger.py' -v`.

**Limitations:** No actual worker loop, independent authenticated approval, provider idempotency key, destination reconciliation, tamper-evident audit, durable cross-database atomicity or real customer communications. A caller-supplied worker token is a *fixture*, not identity authentication. The receipt is a fictional caller-provided string, not provider evidence. A stale worker could still have performed an external action; quarantine requires independent review. Before real effects, implement authenticated worker identity, non-guessable tokens, atomic job/receipt state, provider-side idempotency and read-after-write reconciliation. Existing mock runner still holds a SQLite transaction while executing a callback, and must not be used for external network actions.

**Status:** local-only proof of a claim-state pattern; no Railway service, no real provider access, no payment, no SMS, no new spending. Live release **NO-GO**.
