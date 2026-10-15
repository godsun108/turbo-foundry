"""Offline capability gate tests: scoped role, revocation, one-time review."""
import tempfile
import unittest
from pathlib import Path

from src.autopilot.offline_workflow_runner import OfflineWorkflowRunner
from src.autopilot.offline_capability_gate import OfflineCapabilityGate, CapabilityDenied


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.invocations=[]
        def action(**kwargs):
            self.invocations.append(kwargs)
            return True
        self.runner=OfflineWorkflowRunner(str(Path(self.tmp.name)/"gate.sqlite"),
                                          {"mock":action})
        self.gate=OfflineCapabilityGate(self.runner)
        self.runner.submit(tenant="a",job_id="one",action="mock",
                           due_at=10,needs_review=True)
        self.runner.submit(tenant="b",job_id="one",action="mock",
                           due_at=10,needs_review=True)

    def test_scoped_review_and_worker_execution(self):
        reviewer=self.gate.issue_fixture(tenant="a",role="reviewer")
        worker=self.gate.issue_fixture(tenant="a",role="worker")
        with self.assertRaises(CapabilityDenied):
            self.gate.approve(token=reviewer,tenant="b",job_id="one")
        with self.assertRaises(CapabilityDenied):
            self.gate.execute(token=reviewer,tenant="a",job_id="one",now=10)
        with self.assertRaises(CapabilityDenied):
            self.gate.approve(token=worker,tenant="a",job_id="one")
        self.assertTrue(self.gate.approve(token=reviewer,tenant="a",job_id="one"))
        with self.assertRaises(CapabilityDenied):
            self.gate.approve(token=reviewer,tenant="a",job_id="one")
        self.assertEqual(self.gate.execute(token=worker,tenant="a",
                         job_id="one",now=10)["state"],"completed")
        self.assertEqual(len(self.invocations),1)
        with self.assertRaises(CapabilityDenied):
            self.gate.execute(token=worker,tenant="b",job_id="one",now=10)

    def test_revoked_capabilities_and_persistence(self):
        reviewer=self.gate.issue_fixture(tenant="a",role="reviewer")
        worker=self.gate.issue_fixture(tenant="a",role="worker")
        self.assertTrue(self.gate.revoke_fixture(token=reviewer))
        with self.assertRaises(CapabilityDenied):
            self.gate.approve(token=reviewer,tenant="a",job_id="one")
        second=self.gate.issue_fixture(tenant="a",role="reviewer")
        self.gate.approve(token=second,tenant="a",job_id="one")
        self.assertTrue(self.gate.revoke_fixture(token=worker))
        restarted=OfflineCapabilityGate(self.runner)
        with self.assertRaises(CapabilityDenied):
            restarted.execute(token=worker,tenant="a",job_id="one",now=10)
        self.assertEqual(len(self.invocations),0)

    def test_denied_approval_does_not_consume_token(self):
        token=self.gate.issue_fixture(tenant="a",role="reviewer")
        with self.assertRaises(CapabilityDenied):
            self.gate.approve(token=token,tenant="a",job_id="missing")
        self.assertTrue(self.gate.approve(token=token,tenant="a",job_id="one"))


if __name__=="__main__":
    unittest.main()
