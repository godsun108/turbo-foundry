import tempfile
import unittest
from pathlib import Path
from src.autopilot.event_integrity import EventIntegrity

class TestIntegrity(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store=EventIntegrity(str(Path(tmp.name)/"integrity.sqlite"))

    def test_first_event(self):
        self.assertEqual(self.store.register("shop-a","e1",{"status":"ringing"}).reason,"new_event")

    def test_identical_duplicate(self):
        self.store.register("shop-a","e1",{"status":"ringing","sid":"CA1"})
        self.assertEqual(self.store.register("shop-a","e1",{"sid":"CA1","status":"ringing"}).reason,"exact_duplicate")

    def test_changed_payload_rejected_and_audited(self):
        self.store.register("shop-a","e1",{"status":"ringing"})
        result=self.store.register("shop-a","e1",{"status":"completed"})
        self.assertFalse(result.accepted)
        self.assertTrue(self.store.has_conflict("shop-a","e1"))

    def test_tenant_isolation(self):
        self.store.register("shop-a","e1",{"status":"ringing"})
        self.assertEqual(self.store.register("shop-b","e1",{"status":"completed"}).reason,"new_event")

    def test_persistent_reopen(self):
        self.store.register("shop-a","e1",{"status":"ringing"})
        reopened=EventIntegrity(self.store.db_path)
        self.assertEqual(reopened.register("shop-a","e1",{"status":"ringing"}).reason,"exact_duplicate")

    def test_missing_metadata(self):
        self.assertEqual(self.store.register("","e1",{}).reason,"invalid_event")

if __name__=="__main__":
    unittest.main()
