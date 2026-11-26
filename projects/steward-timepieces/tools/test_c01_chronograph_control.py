import unittest

from c01_chronograph_control import (
    Button, ChronographState, outputs_for, sequence, transition,
)


class ChronographControlTests(unittest.TestCase):
    def test_start_engages_clutch_and_releases_brake(self):
        state = transition(ChronographState.STOPPED_ZERO, Button.START_STOP)
        outputs = outputs_for(state)
        self.assertEqual(state, ChronographState.RUNNING)
        self.assertTrue(outputs.clutch_engaged)
        self.assertFalse(outputs.brake_applied)

    def test_stop_disengages_clutch_and_applies_brake(self):
        state = transition(ChronographState.RUNNING, Button.START_STOP)
        outputs = outputs_for(state)
        self.assertEqual(state, ChronographState.STOPPED_ELAPSED)
        self.assertFalse(outputs.clutch_engaged)
        self.assertTrue(outputs.brake_applied)
        self.assertTrue(outputs.counters_held)

    def test_reset_returns_stopped_elapsed_to_zero(self):
        state = transition(ChronographState.STOPPED_ELAPSED, Button.RESET)
        self.assertEqual(state, ChronographState.STOPPED_ZERO)

    def test_reset_is_rejected_while_running(self):
        with self.assertRaises(ValueError):
            transition(ChronographState.RUNNING, Button.RESET)

    def test_start_stop_start_sequence(self):
        self.assertEqual(sequence(["start_stop", "start_stop", "start_stop"]), [
            "stopped_zero", "running", "stopped_elapsed", "running"
        ])

    def test_reset_from_zero_is_idempotent(self):
        self.assertEqual(
            transition(ChronographState.STOPPED_ZERO, Button.RESET),
            ChronographState.STOPPED_ZERO,
        )

    def test_no_reset_hammer_command_during_running(self):
        outputs = outputs_for(ChronographState.RUNNING)
        self.assertFalse(outputs.reset_hammers_active)


if __name__ == "__main__":
    unittest.main()
