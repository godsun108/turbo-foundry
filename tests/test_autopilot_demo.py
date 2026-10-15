import unittest
from src.autopilot.demo import run_demo

class TestDemo(unittest.TestCase):
    def test_demo_is_deterministic_and_offline(self):
        result = run_demo()
        self.assertEqual(result["mode"], "offline_simulation")
        self.assertEqual(result["actual_messages_sent"], 0)
        self.assertEqual(result["real_leads_recovered"], 0)
        self.assertEqual(result["revenue_generated_usd"], 0)
        self.assertEqual(result["scenarios"], 5)
        self.assertEqual(result["simulated_messages"], 2)
        self.assertEqual(result["rejected_events"], 3)

if __name__ == "__main__":
    unittest.main()
