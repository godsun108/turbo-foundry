"""Unit tests for C-01 chronograph logic and measurement calculations."""
import unittest

from c01_chronograph import (
    STOPPED, RUNNING, transition, validate_command_sequence,
    display_speed_ratio, display_revolutions, energy_comparison,
)


class ChronographStateTests(unittest.TestCase):
    def test_start_stop_reset_sequence(self):
        result = validate_command_sequence(["start", "stop", "reset"])
        self.assertEqual([x["state"] for x in result],
                         [RUNNING, STOPPED, STOPPED])
        self.assertEqual([x["action"] for x in result],
                         ["engage", "disengage", "hammer_release"])

    def test_reset_while_running_rejected(self):
        with self.assertRaises(ValueError):
            transition(RUNNING, "reset")

    def test_start_twice_rejected(self):
        with self.assertRaises(ValueError):
            validate_command_sequence(["start", "start"])

    def test_stop_while_stopped_rejected(self):
        with self.assertRaises(ValueError):
            transition(STOPPED, "stop")

    def test_unknown_command_rejected(self):
        with self.assertRaises(ValueError):
            transition(STOPPED, "pause")


class DisplayRatioTests(unittest.TestCase):
    def test_pair_ratio(self):
        self.assertAlmostEqual(display_speed_ratio(10, 60), 1 / 6)

    def test_compound_display_ratio(self):
        stages = [
            {"driver_teeth": 10, "driven_teeth": 60},
            {"driver_teeth": 12, "driven_teeth": 48},
        ]
        self.assertAlmostEqual(display_revolutions(12, stages), 0.5)

    def test_invalid_tooth_count(self):
        with self.assertRaises(ValueError):
            display_speed_ratio(0, 20)

    def test_missing_stage_input(self):
        with self.assertRaises(ValueError):
            display_revolutions(1, [{"driver_teeth": 10}])


class EnergyComparisonTests(unittest.TestCase):
    def test_matched_interval_incremental_load(self):
        result = energy_comparison(0.020, 0.026, 100, 100)
        self.assertAlmostEqual(result["incremental_energy_j"], 0.006)
        self.assertAlmostEqual(result["incremental_average_power_w"], 0.00006)

    def test_mismatched_intervals_rejected(self):
        with self.assertRaises(ValueError):
            energy_comparison(1, 2, 60, 61)

    def test_negative_increment_reported(self):
        result = energy_comparison(2, 1, 10, 10)
        self.assertAlmostEqual(result["incremental_energy_j"], -1)

    def test_efficiency_limit_not_misapplied(self):
        with self.assertRaises(ValueError):
            energy_comparison(1, 2, 10, 10, minimum_efficiency=0.8)


if __name__ == "__main__":
    unittest.main()
