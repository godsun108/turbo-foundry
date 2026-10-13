import os
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from src.autopilot.observation_store import ObservationStore
from src.autopilot.settlement import Observation,assess_settlement
NOW=datetime(2026,10,13,18,0,tzinfo=timezone.utc)
SID="CA"+"a"*32
class ObservationStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=ObservationStore(os.path.join(self.temp.name,"observations.db"))
    def tearDown(self): self.temp.cleanup()
    def observation(self,minutes=5,ids=(SID,),complete=True):
        return Observation(NOW-timedelta(minutes=minutes),ids,complete)
    def test_persistence(self):
        self.assertTrue(self.store.append("tenant","parent",self.observation()))
        other=ObservationStore(self.store.db_path)
        self.assertEqual(other.load("tenant","parent"),(self.observation(),))
    def test_idempotence(self):
        self.store.append("tenant","parent",self.observation())
        self.assertFalse(self.store.append("tenant","parent",self.observation()))
    def test_conflict(self):
        self.store.append("tenant","parent",self.observation())
        with self.assertRaises(ValueError):
            self.store.append("tenant","parent",self.observation(ids=()))
    def test_tenant_isolation(self):
        self.store.append("tenant-a","parent",self.observation())
        self.assertEqual(self.store.load("tenant-b","parent"),())
    def test_incomplete_rejected(self):
        with self.assertRaises(ValueError):
            self.store.append("tenant","parent",self.observation(complete=False))
    def test_reloaded_settlement(self):
        self.store.append("tenant","parent",self.observation(5))
        self.store.append("tenant","parent",self.observation(2))
        result=assess_settlement(NOW-timedelta(minutes=10),self.store.load("tenant","parent"),now=NOW)
        self.assertTrue(result.settled_for_review)
if __name__=="__main__":
    unittest.main()
