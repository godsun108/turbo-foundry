"""Offline workflow runner tests and integration with mock missed-call executor."""
import tempfile
import unittest
from pathlib import Path

from src.autopilot.offline_workflow_runner import OfflineWorkflowRunner, RunnerDenied
from src.autopilot.mock_missed_call_engine import MockMissedCallEngine


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db=str(Path(self.temp.name)/"runner.sqlite")
        self.calls=[]
        def callback(**kw):
            self.calls.append(kw)
            return True
        self.runner=OfflineWorkflowRunner(self.db,{"fictional_action":callback})

    def test_review_scheduling_persistence_and_replay(self):
        self.assertTrue(self.runner.submit(tenant="a",job_id="one",
            action="fictional_action",due_at=100,needs_review=True))
        self.assertFalse(self.runner.submit(tenant="a",job_id="one",
            action="fictional_action",due_at=100,needs_review=True))
        self.assertEqual(self.runner.run_due(now=200),[])
        self.runner.approve(tenant="a",job_id="one",fictional_reviewer="operator")
        self.assertEqual(self.runner.run_due(now=99),[])
        self.assertEqual(self.runner.run_due(now=100),[("a","one","completed")])
        self.assertEqual(self.runner.run_due(now=200),[])
        self.assertEqual(self.calls,[{"tenant":"a","job_id":"one"}])
        later=OfflineWorkflowRunner(self.db,{"fictional_action":lambda **kw: True})
        self.assertEqual(later.status(tenant="a",job_id="one").state,"completed")
        with self.assertRaises(RunnerDenied):
            later.approve(tenant="a",job_id="one",fictional_reviewer="operator")

    def test_retry_and_exhaustion(self):
        attempts=[]
        def failing(**kw):
            attempts.append(kw)
            return False
        runner=OfflineWorkflowRunner(self.db,{"unavailable":failing})
        runner.submit(tenant="a",job_id="fail",action="unavailable",
                      due_at=100,needs_review=False)
        self.assertEqual(runner.run_due(now=100,retry_seconds=10,max_attempts=3)[0][2],
                         "queued")
        self.assertEqual(runner.status(tenant="a",job_id="fail").due_at,110)
        self.assertEqual(runner.run_due(now=109),[])
        runner.run_due(now=110,retry_seconds=10,max_attempts=3)
        self.assertEqual(runner.status(tenant="a",job_id="fail").due_at,130)
        self.assertEqual(runner.run_due(now=130,max_attempts=3)[0][2],"failed")
        self.assertEqual(len(attempts),3)
        self.assertFalse(runner.stop(tenant="a",job_id="absent"))
        self.assertTrue(runner.stop(tenant="a",job_id="fail"))
        self.assertEqual(runner.run_due(now=1000),[])

    def test_isolation_and_stop(self):
        self.runner.submit(tenant="a",job_id="x",action="fictional_action",
                           due_at=1,needs_review=False)
        self.runner.submit(tenant="b",job_id="x",action="fictional_action",
                           due_at=1,needs_review=False)
        self.assertTrue(self.runner.stop(tenant="a",job_id="x"))
        self.assertEqual(self.runner.run_due(now=1),[("b","x","completed")])
        self.assertEqual(self.runner.status(tenant="a",job_id="x").state,"stopped")
        self.assertIsNone(self.runner.status(tenant="c",job_id="x"))

    def test_deny_bad_actions_and_limits(self):
        with self.assertRaises(RunnerDenied):
            self.runner.submit(tenant="a",job_id="x",action="unregistered",due_at=1)
        for value in (-1,True,1.5):
            with self.assertRaises(RunnerDenied):
                self.runner.run_due(now=value)
        with self.assertRaises(RunnerDenied):
            self.runner.submit(tenant="a",job_id="x",action="fictional_action",
                               due_at=1,needs_review="no")

    def test_actual_mock_missed_call_callback(self):
        engine=MockMissedCallEngine(str(Path(self.temp.name)/"events.sqlite"))
        engine.missed_call(tenant="garage",industry="automotive",
                           event_id="call-1",alias="fake-1",
                           consent_flag=True,during_hours=True)
        def dispatch(*,tenant,job_id):
            return engine.flush_mock(tenant=tenant,event_id=job_id).state=="sent_mock"
        runner=OfflineWorkflowRunner(self.db,{"mock_followup":dispatch})
        runner.submit(tenant="garage",job_id="call-1",action="mock_followup",
                      due_at=10,needs_review=True)
        self.assertEqual(engine.status(tenant="garage",event_id="call-1").state,"pending")
        runner.approve(tenant="garage",job_id="call-1",fictional_reviewer="tester")
        self.assertEqual(runner.run_due(now=10),[("garage","call-1","completed")])
        self.assertEqual(engine.status(tenant="garage",event_id="call-1").state,"sent_mock")
        self.assertEqual(runner.run_due(now=11),[])
        self.assertEqual(engine.reply(tenant="garage",event_id="call-1",
                                     reply_id="r1",kind="question").state,"escalated")


if __name__=="__main__":
    unittest.main()
