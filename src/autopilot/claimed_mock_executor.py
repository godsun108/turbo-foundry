"""Opt-in OFFLINE integration of approved jobs and claim/receipt ledger.

Never calls a network provider. Ambiguous mock outcomes are quarantined, not
retried. This is an integration rehearsal, not a production worker.
"""
import sqlite3

from .offline_claim_ledger import OfflineClaimLedger, ClaimDenied, _clock, _id
from .offline_workflow_runner import OfflineWorkflowRunner, RunnerDenied


class ClaimedMockExecutor:
    """Trusted local fixture. Caller supplies clock and fictional worker token."""

    def __init__(self, runner: OfflineWorkflowRunner):
        if not isinstance(runner, OfflineWorkflowRunner):
            raise ValueError("offline runner required")
        self.runner = runner
        self.ledger = OfflineClaimLedger(runner.db_path)

    def execute(self, *, tenant, job_id, worker_token, now, lease_seconds=30):
        if (not all(_id(x) for x in (tenant,job_id,worker_token))
                or not _clock(now) or type(lease_seconds) is not int
                or not 1 <= lease_seconds <= 3600):
            raise RunnerDenied("invalid fictional claim request")
        job=self.runner.status(tenant=tenant,job_id=job_id)
        if job is None or job.state!="queued" or job.due_at>now:
            raise RunnerDenied("job not approved or not due")
        # Ledger is stored in the SAME local database as the runner.
        # Reconciliation is mandatory if a prior execution was interrupted.
        recorded=self.ledger.status(tenant=tenant,job_id=job_id)
        if recorded is None:
            self.ledger.submit(tenant=tenant,job_id=job_id,due_at=job.due_at)
        elif recorded["state"]!="queued":
            raise RunnerDenied("previous claim requires reconciliation")
        claim=self.ledger.claim(tenant=tenant,job_id=job_id,
                                worker_token=worker_token,now=now,
                                lease_seconds=lease_seconds)
        try:
            acknowledged=self.runner._actions[job.action](
                tenant=tenant,job_id=job_id)
            if acknowledged is not True:
                raise RunnerDenied("mock callback did not acknowledge")
        except Exception:
            # A callback could have acted before raising. Do not auto-retry.
            self.ledger.quarantine_expired(now=claim.lease_until)
            raise RunnerDenied("mock callback outcome uncertain; quarantined") from None
        # Receipt is a fictional acknowledgement, not provider evidence.
        try:
            self.ledger.complete(claim=claim,receipt="mock_ack_"+job_id,now=now)
        except ClaimDenied as exc:
            raise RunnerDenied("mock receipt uncertain; manual reconciliation") from exc
        with sqlite3.connect(self.runner.db_path,timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            count=db.execute("""UPDATE offline_jobs SET state='completed',
                attempts=attempts+1 WHERE tenant=? AND job_id=?
                AND state='queued'""",(tenant,job_id)).rowcount
            if count!=1:
                raise RunnerDenied("runner state diverged; manual reconciliation")
            self.runner._audit(db,tenant,job_id,"completed","claimed_mock_receipt")
        return {"tenant":tenant,"job_id":job_id,"state":"completed",
                "receipt":"mock_ack_"+job_id,"live_effect":False}
