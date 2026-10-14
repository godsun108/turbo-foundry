import unittest
from src.autopilot.gateway_release_rehearsal import execute

class RehearsalTests(unittest.TestCase):
    def test_lifecycle(self):
        x=execute()
        self.assertTrue(x["passed"],x["checks"])
        self.assertGreaterEqual(len(x["checks"]),7)
        self.assertFalse(x["production_ready"])
        self.assertEqual(x["messages_sent"],0)
        self.assertEqual(x["payments_processed"],0)
