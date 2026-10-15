"""Regression: claimed mode is the only dispatcher once ledger exists."""
import tempfile
import unittest
from pathlib import Path
from src.autopilot.offline_workflow_runner import OfflineWorkflowRunner, RunnerDenied
from src.autopilot.claimed_mock_executor import ClaimedMockExecutor


class UnifiedDispatchTests(unittest.TestCase):
    def test_legacy_path_closed_and_receipt_atomic(self):
        with tempfile.TemporaryDirectory() as directory:
            calls=[]
            def callback(**kw):
                calls.append(kw)
                return True
            db=str(Path(directory)/"shared.sqlite")
            runner=OfflineWorkflowRunner(db,{"mock":callback})
            runner.submit(tenant="shop",job_id="job",action="mock",
                          due_at=10,needs_review=False)
            executor=ClaimedMockExecutor(runner)
            with self.assertRaisesRegex(RunnerDenied,"legacy dispatch disabled"):
                runner.run_due(now=10)
            self.assertEqual(calls,[])
            receipt=executor.execute(tenant="shop",job_id="job",
                                      worker_token="worker",now=10)
            self.assertEqual(receipt["state"],"completed")
            self.assertEqual(len(calls),1)
            self.assertEqual(runner.status(tenant="shop",job_id="job").state,
                             executor.ledger.status(tenant="shop",job_id="job")["state"])
            restarted=OfflineWorkflowRunner(db,{"mock":callback})
            with self.assertRaises(RunnerDenied):
                restarted.run_due(now=11)
            with self.assertRaises(RunnerDenied):
                ClaimedMockExecutor(restarted).execute(
                    tenant="shop",job_id="job",worker_token="worker2",now=11)
            self.assertEqual(len(calls),1)


if __name__=="__main__":
    unittest.main()
