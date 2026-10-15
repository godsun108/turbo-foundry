import os
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from src.autopilot.recheck_queue import RecheckQueue
from src.autopilot.recheck_leases import RecheckLeases
from src.autopilot.worker_control import WorkerControl
NOW=datetime(2026,10,13,18,0,tzinfo=timezone.utc)
class LeaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.tmp.name,"work.db")
        self.queue=RecheckQueue(self.path)
        self.leases=RecheckLeases(self.path)
        self.control=WorkerControl(self.path)
        self.control.set_enabled(True)
        self.queue.schedule("t","p",now=NOW)
    def finish(self,tenant,parent,token,**kwargs):
        return self.leases.finish(tenant,parent,token,control=self.control,**kwargs)
    def tearDown(self): self.tmp.cleanup()
    def test_fenced_finish(self):
        token=self.leases.claim("t","p",now=NOW)
        self.assertTrue(self.finish("t","p",token,now=NOW,reason="done",completed=True))
        self.assertEqual(self.queue.due(now=NOW+timedelta(days=1)),[])

    def test_stale_worker_cannot_finish(self):
        old=self.leases.claim("t","p",now=NOW,lease_seconds=10)
        later=NOW+timedelta(seconds=11)
        new=self.leases.claim("t","p",now=later)
        self.assertFalse(self.finish("t","p",old,now=later,reason="stale",completed=True))
        self.assertTrue(self.finish("t","p",new,now=later,reason="retry"))
        self.assertEqual(self.queue.due(now=later),[])

    def test_expired_lease_cannot_finish(self):
        token=self.leases.claim("t","p",now=NOW,lease_seconds=10)
        self.assertFalse(self.finish("t","p",token,
                         now=NOW+timedelta(seconds=11),reason="late"))

    def test_double_finish_rejected(self):
        token=self.leases.claim("t","p",now=NOW)
        self.assertTrue(self.finish("t","p",token,now=NOW,reason="retry"))
        self.assertFalse(self.finish("t","p",token,now=NOW,reason="again"))

    def test_disabled_control_blocks_retry_and_preserves_lease(self):
        token=self.leases.claim("t","p",now=NOW)
        self.control.set_enabled(False)
        self.assertFalse(self.finish("t","p",token,now=NOW,reason="timeout"))
        self.assertTrue(self.leases.owns("t","p",token,now=NOW))
        self.assertEqual(self.queue.due(now=NOW),[("t","p",0,4)])

    def test_missing_control_blocks_retry(self):
        token=self.leases.claim("t","p",now=NOW)
        self.assertFalse(self.leases.finish("t","p",token,now=NOW,reason="timeout"))
        self.assertEqual(self.queue.due(now=NOW),[("t","p",0,4)])

    def test_foreign_control_blocks_retry(self):
        token=self.leases.claim("t","p",now=NOW)
        foreign=WorkerControl(os.path.join(self.tmp.name,"other.db"))
        foreign.set_enabled(True)
        self.assertFalse(self.leases.finish("t","p",token,now=NOW,reason="timeout",control=foreign))
        self.assertEqual(self.queue.due(now=NOW),[("t","p",0,4)])

    def test_guarded_claim_fails_when_stopped_without_lease(self):
        self.control.set_enabled(False)
        self.assertIsNone(self.leases.claim("t","p",now=NOW,control=self.control))
        self.assertEqual(self.queue.due(now=NOW),[("t","p",0,4)])
        self.control.set_enabled(True)
        self.assertTrue(self.leases.claim("t","p",now=NOW,control=self.control))

    def test_guarded_claim_rejects_foreign_control(self):
        foreign=WorkerControl(os.path.join(self.tmp.name,"foreign.db"))
        foreign.set_enabled(True)
        self.assertIsNone(self.leases.claim("t","p",now=NOW,control=foreign))
        self.assertTrue(self.leases.claim("t","p",now=NOW,control=self.control))

    def test_guarded_claim_fails_closed_on_missing_control_table(self):
        import sqlite3
        with sqlite3.connect(self.path) as db:
            db.execute("DROP TABLE worker_control")
        self.assertIsNone(self.leases.claim("t","p",now=NOW,control=self.control))
        self.assertEqual(self.queue.due(now=NOW),[("t","p",0,4)])

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
