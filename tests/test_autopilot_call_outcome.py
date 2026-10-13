import unittest
from src.autopilot.call_outcome import classify_call_status

class TestCallOutcome(unittest.TestCase):
    def test_no_answer_inbound(self):
        self.assertTrue(classify_call_status("no-answer", inbound=True).eligible_missed)

    def test_completed_is_not_missed(self):
        self.assertFalse(classify_call_status("completed", inbound=True).eligible_missed)

    def test_busy_not_missed(self):
        self.assertFalse(classify_call_status("busy", inbound=True).eligible_missed)

    def test_no_answer_outbound(self):
        self.assertFalse(classify_call_status("no-answer", inbound=False).eligible_missed)

    def test_answered_elsewhere(self):
        self.assertFalse(classify_call_status("no-answer", inbound=True, answered_elsewhere=True).eligible_missed)

    def test_ringing_not_missed(self):
        self.assertFalse(classify_call_status("ringing", inbound=True).eligible_missed)

    def test_unknown_fail_closed(self):
        self.assertFalse(classify_call_status("unknown", inbound=True).eligible_missed)

if __name__ == "__main__":
    unittest.main()
