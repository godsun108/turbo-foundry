"""Tests for fail-closed claim recovery and scoped receipts."""
import tempfile
import unittest
from pathlib import Path
from src.autopilot.offline_claim_ledger import OfflineClaimLedger, ClaimDenied


class ClaimTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=str(Path(self.tmp.name)/"claims.sqlite")
        self.ledger=OfflineClaimLedger(self.path)

    def test_claim_receipt_persists_and_cannot_replay(self):
        self.assertTrue(self.ledger.submit(tenant="shop",job_id="job1",due_at=100))
        self.assertFalse(self.ledger.submit(tenant="shop",job_id="job1",due_at=100))
        with self.assertRaises(ClaimDenied):
            self.ledger.claim(tenant="shop",job_id="job1",worker_token="worker1",now=99)
        claim=self.ledger.claim(tenant="shop",job_id="job1",worker_token="worker1",now=100)
        with self.assertRaises(ClaimDenied):
            self.ledger.claim(tenant="shop",job_id="job1",worker_token="worker2",now=100)
        self.assertTrue(self.ledger.complete(claim=claim,receipt="mock-receipt1",now=101))
        self.assertEqual(OfflineClaimLedger(self.path).status(
            tenant="shop",job_id="job1"),
            {"state":"completed","mock_receipt":"mock-receipt1"})
        with self.assertRaises(ClaimDenied):
            self.ledger.complete(claim=claim,receipt="again",now=102)
        self.assertEqual(self.ledger.quarantine_expired(now=10000),0)

    def test_crash_ambiguity_quarantined_not_retried(self):
        self.ledger.submit(tenant="shop",job_id="job1",due_at=0)
        claim=self.ledger.claim(tenant="shop",job_id="job1",
                                worker_token="worker1",now=0,lease_seconds=10)
        self.assertEqual(self.ledger.quarantine_expired(now=9),0)
        self.assertEqual(self.ledger.quarantine_expired(now=10),1)
        self.assertEqual(self.ledger.status(tenant="shop",job_id="job1")["state"],
                         "uncertain")
        with self.assertRaises(ClaimDenied):
            self.ledger.complete(claim=claim,receipt="late",now=10)
        with self.assertRaises(ClaimDenied):
            self.ledger.claim(tenant="shop",job_id="job1",
                              worker_token="worker2",now=11)
        self.assertEqual(self.ledger.quarantine_expired(now=12),0)

    def test_expired_receipt_denied_even_before_quarantine(self):
        self.ledger.submit(tenant="shop",job_id="job1",due_at=0)
        claim=self.ledger.claim(tenant="shop",job_id="job1",
                                worker_token="worker1",now=0,lease_seconds=10)
        with self.assertRaises(ClaimDenied):
            self.ledger.complete(claim=claim,receipt="late",now=10)

    def test_tenant_isolation_and_cancel(self):
        for tenant in ("a","b"):
            self.ledger.submit(tenant=tenant,job_id="same",due_at=0)
        self.assertTrue(self.ledger.cancel(tenant="a",job_id="same"))
        self.assertFalse(self.ledger.cancel(tenant="a",job_id="same"))
        self.assertIsNone(self.ledger.status(tenant="c",job_id="same"))
        self.assertEqual(self.ledger.status(tenant="a",job_id="same")["state"],
                         "cancelled")
        claim=self.ledger.claim(tenant="b",job_id="same",
                                worker_token="worker1",now=0)
        self.assertTrue(self.ledger.complete(claim=claim,receipt="ok",now=1))

    def test_invalid_input_denied(self):
        with self.assertRaises(ClaimDenied):
            self.ledger.submit(tenant="a",job_id="b",due_at=True)
        with self.assertRaises(ClaimDenied):
            self.ledger.claim(tenant="a",job_id="b",worker_token="!",now=0)
        with self.assertRaises(ClaimDenied):
            self.ledger.quarantine_expired(now=-1)


if __name__=="__main__":
    unittest.main()
