"""Crash-stage fault injection for the offline claimed executor.

This is a deterministic simulation; no real provider, worker or external effect.
"""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.autopilot.claimed_mock_executor import ClaimedMockExecutor
from src.autopilot.offline_workflow_runner import OfflineWorkflowRunner, RunnerDenied


class CrashStageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=str(Path(self.temp.name)/"jobs.sqlite")
        self.invocations=[]
        def action(**kw):
            self.invocations.append(kw)
            return True
        self.runner=OfflineWorkflowRunner(self.path,{"mock":action})
        self.runner.submit(tenant="shop",job_id="job",action="mock",
                           due_at=10,needs_review=False)
        self.executor=ClaimedMockExecutor(self.runner)

    def test_crash_after_claim_before_action_quarantines(self):
        ledger=self.executor.ledger
        ledger.submit(tenant="shop",job_id="job",due_at=10)
        ledger.claim(tenant="shop",job_id="job",worker_token="worker",now=10,
                     lease_seconds=5)
        self.assertEqual(ledger.quarantine_expired(now=15),1)
        with self.assertRaisesRegex(RunnerDenied,"reconciliation"):
            self.executor.execute(tenant="shop",job_id="job",
                                  worker_token="newworker",now=16)
        self.assertEqual(self.invocations,[])

    def test_crash_after_mock_action_before_receipt_quarantines(self):
        ledger=self.executor.ledger
        ledger.submit(tenant="shop",job_id="job",due_at=10)
        ledger.claim(tenant="shop",job_id="job",worker_token="worker",now=10,
                     lease_seconds=5)
        self.invocations.append({"simulated":"action happened before crash"})
        self.assertEqual(ledger.quarantine_expired(now=15),1)
        with self.assertRaises(RunnerDenied):
            self.executor.execute(tenant="shop",job_id="job",
                                  worker_token="newworker",now=16)
        self.assertEqual(len(self.invocations),1)
        self.assertEqual(self.runner.status(tenant="shop",job_id="job").state,
                         "queued")
        self.assertEqual(ledger.status(tenant="shop",job_id="job")["state"],
                         "uncertain")

    def test_receipt_and_job_completion_survive_restart(self):
        result=self.executor.execute(tenant="shop",job_id="job",
                                     worker_token="worker",now=10)
        self.assertEqual(result["state"],"completed")
        new_runner=OfflineWorkflowRunner(self.path,{"mock":lambda **kw: True})
        new_executor=ClaimedMockExecutor(new_runner)
        self.assertEqual(new_runner.status(tenant="shop",job_id="job").state,
                         "completed")
        self.assertEqual(new_executor.ledger.status(
            tenant="shop",job_id="job")["state"],"completed")
        with self.assertRaises(RunnerDenied):
            new_executor.execute(tenant="shop",job_id="job",
                                 worker_token="newworker",now=11)
        self.assertEqual(len(self.invocations),1)

    def test_transaction_rollback_on_audit_failure(self):
        # Force the receipt+runner transaction to abort after mock callback.
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TRIGGER block_mock_audit
                BEFORE INSERT ON offline_job_audit
                WHEN NEW.reason='claimed_mock_receipt'
                BEGIN SELECT RAISE(ABORT, 'injected crash'); END""")
        with self.assertRaises(sqlite3.DatabaseError):
            self.executor.execute(tenant="shop",job_id="job",
                                  worker_token="worker",now=10)
        self.assertEqual(len(self.invocations),1)
        self.assertEqual(self.runner.status(tenant="shop",job_id="job").state,
                         "queued")
        self.assertEqual(self.executor.ledger.status(
            tenant="shop",job_id="job")["state"],"claimed")
        self.assertEqual(self.executor.ledger.quarantine_expired(now=40),1)
        with self.assertRaises(RunnerDenied):
            self.executor.execute(tenant="shop",job_id="job",
                                  worker_token="newworker",now=41)


if __name__=="__main__":
    unittest.main()
