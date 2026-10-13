import os
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from src.autopilot.recheck_queue import RecheckQueue
from src.autopilot.recheck_leases import RecheckLeases
NOW=datetime(2026,10,13,18,0,tzinfo=timezone.utc)
class LeaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.tmp.name,"work.db")
        self.queue=RecheckQueue(self.path)
        self.leases=RecheckLeases(self.path)
        self.queue.schedule("t","p",now=NOW)
    def tearDown(self): self.tmp.cleanup()
    def test_claim_exclusive(self):
        token=self.leases.claim("t","p",now=NOW)
        self.assertTrue(token)
        self.assertIsNone(self.leases.claim("t","p",now=NOW))
    def test_expiry_recovery(self):
        token=self.leases.claim("t","p",now=NOW,lease_seconds=30)
        new=self.leases.claim("t","p",now=NOW+timedelta(seconds=31))
        self.assertNotEqual(token,new)
        self.assertFalse(self.leases.owns("t","p",token,now=NOW+timedelta(seconds=31)))
    def test_old_owner_cannot_release_new(self):
        old=self.leases.claim("t","p",now=NOW,lease_seconds=10)
        new=self.leases.claim("t","p",now=NOW+timedelta(seconds=11))
        self.assertFalse(self.leases.release("t","p",old))
        self.assertTrue(self.leases.owns("t","p",new,now=NOW+timedelta(seconds=11)))
    def test_release(self):
        token=self.leases.claim("t","p",now=NOW)
        self.assertTrue(self.leases.release("t","p",token))
        self.assertTrue(self.leases.claim("t","p",now=NOW))
    def test_not_due(self):
        self.queue.record_attempt("t","p",now=NOW,reason="retry")
        self.assertIsNone(self.leases.claim("t","p",now=NOW))
    def test_completed_cannot_claim(self):
        self.queue.record_attempt("t","p",now=NOW,reason="done",completed=True)
        self.assertIsNone(self.leases.claim("t","p",now=NOW))
    def test_unknown_job(self):
        self.assertIsNone(self.leases.claim("t","unknown",now=NOW))
if __name__=="__main__":
    unittest.main()
