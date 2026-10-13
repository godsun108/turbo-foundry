# Read-only provider recheck worker

`run_recheck` coordinates a due job's lease, injected account-bound provider pager, atomic observation persistence, bounded retry advancement, and settlement assessment. Failed provider enumeration records an unsuccessful attempt and never writes an incomplete observation. A stable history is marked **for review only**.

The worker is an offline callable, not a deployed background service. It does not authenticate the injected pager itself, fetch authoritative call-end evidence, enforce provider quotas, or authorize SMS. Its `now` argument is supplied by the caller; production workers must use trusted UTC time and appropriate lease durations. Crash-safe external provider reads and scheduling orchestration require integration tests. No live messaging or billing.
