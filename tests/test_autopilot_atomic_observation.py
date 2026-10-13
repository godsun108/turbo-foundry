import os
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from src.autopilot.recheck_queue import RecheckQueue
from src.autopilot.recheck_leases import RecheckLeases
from src.autopilot.observation_store import ObservationStore
from src.autopilot.atomic_observation import commit_observation
from src.autopilot.settlement import Observation

NOW=datetime(2026,10,13,18,0,tzinfo=timezone.utc)
SID="CA"+"a"*32
class AtomicObservationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.tmp.name,"worker.db")
        self.queue=RecheckQueue(self.path)
        self.leases=RecheckLeases(self.path)
        self.store=ObservationStore(self.path)
        self.queue.schedule("tenant","parent",now=NOW)
        self.token=self.leases.claim("tenant","parent",now=NOW)
    def tearDown(self): self.tmp.cleanup()
    def obs(self,ids=(SID,)):
        return Observation(NOW-timedelta(seconds=30),ids,True)
    def commit(self,token=None,**kwargs):
        return commit_observation(self.path,"tenant","parent",token or self.token,
                                  now=NOW,observation=self.obs(),**kwargs)
    def test_atomic_success(self):
        self.assertTrue(self.commit())
        self.assertEqual(len(self.store.load("tenant","parent")),1)
        self.assertFalse(self.leases.owns("tenant","parent",self.token,now=NOW))
        self.assertEqual(self.queue.due(now=NOW),[])
    def test_stale_worker_cannot_write(self):
        self.assertFalse(self.commit(token="stale"))
        self.assertEqual(self.store.load("tenant","parent"),())
    def test_duplicate_finish_no_second_write(self):
        self.assertTrue(self.commit())
        self.assertFalse(self.commit())
        self.assertEqual(len(self.store.load("tenant","parent")),1)
    def test_conflict_rolls_back(self):
        self.store.append("tenant","parent",self.obs(ids=()))
        with self.assertRaises(ValueError):
            self.commit()
        self.assertTrue(self.leases.owns("tenant","parent",self.token,now=NOW))
        self.assertEqual(self.queue.due(now=NOW),[("tenant","parent",0,4)])
    def test_completed(self):
        self.assertTrue(self.commit(completed=True))
        self.assertEqual(self.queue.due(now=NOW+timedelta(days=1)),[])
if __name__=="__main__":
    unittest.main()
