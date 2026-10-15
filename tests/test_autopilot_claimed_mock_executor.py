"""Claimed mock executor integration and ambiguous outcome tests."""
import tempfile
import unittest
from pathlib import Path

from src.autopilot.claimed_mock_executor import ClaimedMockExecutor
from src.autopilot.offline_workflow_runner import OfflineWorkflowRunner, RunnerDenied
from src.autopilot.mock_missed_call_engine import MockMissedCallEngine


class ClaimedExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db=str(Path(self.temp.name)/"runner.sqlite")

    def test_approved_missed_call_executes_once_and_receipt_survives(self):
        calls=MockMissedCallEngine(str(Path(self.temp.name)/"calls.sqlite"))
        calls.missed_call(tenant="garage",industry="automotive",
            event_id="event1",alias="fictional1",consent_flag=True,
            during_hours=True)
        def mock_action(*,tenant,job_id):
            return calls.flush_mock(tenant=tenant,event_id=job_id).state=="sent_mock"
        runner=OfflineWorkflowRunner(self.db,{"followup":mock_action})
        runner.submit(tenant="garage",job_id="event1",action="followup",
                      due_at=20,needs_review=True)
        executor=ClaimedMockExecutor(runner)
        with self.assertRaises(RunnerDenied):
            executor.execute(tenant="garage",job_id="event1",
                             worker_token="worker1",now=20)
        runner.approve(tenant="garage",job_id="event1",
                       fictional_reviewer="fixture_reviewer")
        with self.assertRaises(RunnerDenied):
            executor.execute(tenant="garage",job_id="event1",
                             worker_token="worker1",now=19)
        result=executor.execute(tenant="garage",job_id="event1",
                                worker_token="worker1",now=20)
        self.assertEqual(result["state"],"completed")
        self.assertFalse(result["live_effect"])
        self.assertEqual(runner.status(tenant="garage",job_id="event1").state,
                         "completed")
        self.assertEqual(calls.status(tenant="garage",event_id="event1").state,
                         "sent_mock")
        self.assertEqual(ClaimedMockExecutor(runner).ledger.status(
            tenant="garage",job_id="event1")["state"],"completed")
        with self.assertRaises(RunnerDenied):
            executor.execute(tenant="garage",job_id="event1",
                             worker_token="worker2",now=21)

    def test_exception_quarantines_instead_of_retry(self):
        invocations=[]
        def unreliable(**kwargs):
            invocations.append(kwargs)
            raise RuntimeError("simulated crash after unknown mock effect")
        runner=OfflineWorkflowRunner(self.db,{"unreliable":unreliable})
        runner.submit(tenant="a",job_id="x",action="unreliable",
                      due_at=1,needs_review=False)
        executor=ClaimedMockExecutor(runner)
        with self.assertRaisesRegex(RunnerDenied,"quarantined"):
            executor.execute(tenant="a",job_id="x",worker_token="w",now=1)
        self.assertEqual(executor.ledger.status(tenant="a",job_id="x")["state"],
                         "uncertain")
        with self.assertRaisesRegex(RunnerDenied,"reconciliation"):
            executor.execute(tenant="a",job_id="x",worker_token="w2",now=2)
        self.assertEqual(len(invocations),1)

    def test_tenant_separation(self):
        runner=OfflineWorkflowRunner(self.db,{"mock":lambda **kw: True})
        runner.submit(tenant="a",job_id="same",action="mock",
                      due_at=1,needs_review=False)
        executor=ClaimedMockExecutor(runner)
        with self.assertRaises(RunnerDenied):
            executor.execute(tenant="b",job_id="same",worker_token="w",now=1)
        self.assertEqual(executor.execute(tenant="a",job_id="same",
            worker_token="w",now=1)["state"],"completed")
        self.assertIsNone(executor.ledger.status(tenant="b",job_id="same"))


if __name__=="__main__":
    unittest.main()
