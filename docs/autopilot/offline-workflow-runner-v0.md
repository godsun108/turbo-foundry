# Foundry Reusable Workflow Runner v0 — offline execution only

## What exists

`src/autopilot/offline_workflow_runner.py` is a stdlib/SQLite **local fictional action scheduler**. Jobs are isolated by fictional tenant and job ID and have a registered mock action, a due time, persistent attempt count, and state. Submission is idempotent by (tenant,job_id). Jobs can wait for a *fictional* reviewer, run when due, retry mock failures with bounded exponential delays, enter a terminal failure state after a configurable attempt ceiling, or be stopped. Each transition has a local audit row.

`tests/test_autopilot_offline_workflow_runner.py` exercises a mock action registry plus the existing `MockMissedCallEngine` end to end. A fictional missed call creates the mocked event, a manually approved job uses the runner to call `flush_mock`, and a fictional customer question is escalated and persisted. Separate temporary SQLite files represent the runner and mock event engine.

## Verification

```sh
python -m unittest discover -s tests -p 'test_autopilot_offline_workflow_runner.py' -v
```

## Deliberate limits (do not mistake for operational readiness)

- The runner **does not** start itself, continuously poll, create a deployed server, connect providers, communicate with real customers, or accept payments.
- The `fictional_reviewer` string is **not authenticated approval**. The scheduler is callable by trusted test code only.
- Mock actions run synchronously while the runner holds its local SQLite transaction. This serializes local tests; it is **not** a suitable network-worker design.
- A callback can alter its own local database before the runner commits; there is **no distributed transaction** across the runner database and action state. Therefore **exactly-once execution is not proven**. Production needs claimed leases, idempotency keys applied by the destination, recovery from crashes between side effects and receipts, and atomic state reconciliations.
- Time is an injected integer for deterministic offline testing; it is **not** securely sourced from an operating environment. Retries are simulations, not a policy to blindly repeat real SMS messages.
- Human review, consent, tenant authentication, provider account binding, delivery receipts, data retention and usage billing remain separately gated. Real deployment and checkout are **NO-GO**.

The runner's mock action interface is reusable, but live implementations must be developed through a separate reviewed and independently authorized adapter boundary. No Railway services or paid resources are deployed, and no provider requests or messages occur.
