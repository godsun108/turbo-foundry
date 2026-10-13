import os
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from types import SimpleNamespace
from src.autopilot.recheck_queue import RecheckQueue
from src.autopilot.recheck_leases import RecheckLeases
from src.autopilot.observation_store import ObservationStore
from src.autopilot.recheck_worker import run_recheck
NOW=datetime(2026,10,13,18,0,tzinfo=timezone.utc)
END=NOW-timedelta(minutes=20)
SID="CA"+"a"*32
class Pager:
    def __init__(self,complete=True,reason="sdk_page_exhaustion",ids=(SID,)):
        self.result=SimpleNamespace(complete=complete,reason=reason,child_sids=ids)
    def enumerate_all(self,parent): return self.result
class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.tmp.name,"worker.db")
        self.queue=RecheckQueue(self.path)
        self.leases=RecheckLeases(self.path)
        self.store=ObservationStore(self.path)
        self.queue.schedule("t","p",now=NOW)
    def tearDown(self): self.tmp.cleanup()
    def run(self,now=NOW,pager=None):
        return run_recheck(self.path,"t","p",now=now,call_ended_at=END,
                           pager=pager or Pager())
    def test_first_observation(self):
        result=self.run()
        self.assertTrue(result.recorded)
        self.assertFalse(result.settled_for_review)
        self.assertEqual(result.reason,"insufficient_observations")
    def test_second_observation_stable(self):
        self.run()
        result=self.run(now=NOW+timedelta(minutes=3))
        self.assertTrue(result.settled_for_review)
    def test_provider_failure(self):
        result=self.run(pager=Pager(False,"provider_rate_limited"))
        self.assertFalse(result.recorded)
        self.assertEqual(result.reason,"provider_provider_rate_limited")
        self.assertEqual(self.store.load("t","p"),())
    def test_not_due(self):
        self.run()
        self.assertEqual(self.run().reason,"not_claimed")
    def test_preclaimed(self):
        token=self.leases.claim("t","p",now=NOW)
        self.assertEqual(self.run().reason,"not_claimed")
        self.leases.release("t","p",token)
    def test_changing_records(self):
        self.run()
        result=self.run(now=NOW+timedelta(minutes=3),pager=Pager(ids=()))
        self.assertFalse(result.settled_for_review)
        self.assertEqual(result.reason,"changing_child_set")
if __name__=="__main__":
    unittest.main()
