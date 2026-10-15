import os
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from src.autopilot.recheck_queue import RecheckQueue
NOW=datetime(2026,10,13,18,0,tzinfo=timezone.utc)
class RecheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.queue=RecheckQueue(os.path.join(self.tmp.name,"queue.db"))
    def tearDown(self): self.tmp.cleanup()
    def test_schedule_idempotent(self):
        self.assertTrue(self.queue.schedule("t","p",now=NOW))
        self.assertFalse(self.queue.schedule("t","p",now=NOW))
    def test_due(self):
        self.queue.schedule("t","p",now=NOW)
        self.assertEqual(len(self.queue.due(now=NOW)),1)
    def test_delayed_retry(self):
        self.queue.schedule("t","p",now=NOW)
        self.assertTrue(self.queue.record_attempt("t","p",now=NOW,reason="rate_limit"))
        self.assertEqual(self.queue.due(now=NOW),[])
        self.assertEqual(len(self.queue.due(now=NOW+timedelta(seconds=60))),1)
    def test_exhaustion(self):
        self.queue.schedule("t","p",now=NOW,max_attempts=1)
        self.queue.record_attempt("t","p",now=NOW,reason="timeout")
        self.assertEqual(self.queue.due(now=NOW+timedelta(days=1)),[])
    def test_completion(self):
        self.queue.schedule("t","p",now=NOW)
        self.queue.record_attempt("t","p",now=NOW,reason="stable",completed=True)
        self.assertEqual(self.queue.due(now=NOW+timedelta(days=1)),[])
    def test_persistence(self):
        self.queue.schedule("t","p",now=NOW)
        other=RecheckQueue(self.queue.db_path)
        self.assertEqual(len(other.due(now=NOW)),1)
    def test_future_not_due(self):
        self.queue.schedule("t","p",now=NOW)
        self.assertEqual(self.queue.due(now=NOW-timedelta(seconds=1)),[])
if __name__=="__main__":
    unittest.main()
