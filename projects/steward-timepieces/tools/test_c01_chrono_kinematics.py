import unittest
from fractions import Fraction

from c01_chrono_kinematics import (
    GearStage, analyze, counter_architecture_comparison, counter_index_spec,
    evaluate_train, path_ratio, required_ratio, target_display_speeds,
)


class ChronographKinematicsTests(unittest.TestCase):
    def test_required_chronograph_display_speeds(self):
        speeds = target_display_speeds()
        self.assertEqual(speeds["central_chronograph_seconds"]["required_rpm"], "1")
        self.assertEqual(speeds["chronograph_30_minute_register_continuous_convention"]["required_rpm"], "1/30")
        self.assertEqual(speeds["chronograph_12_hour_register_continuous_convention"]["required_rpm"], "1/720")

    def test_required_ratio_derived_from_supplied_source(self):
        result = required_ratio("2", 60)
        self.assertEqual(result["target_rpm"], "1")
        self.assertEqual(result["required_speed_ratio_magnitude"], "1/2")

    def test_external_and_internal_direction(self):
        self.assertEqual(GearStage(12, 36, "external").signed_ratio(), Fraction(-1, 3))
        self.assertEqual(GearStage(12, 36, "internal").signed_ratio(), Fraction(1, 3))

    def test_compound_train_speed_and_direction(self):
        stages = [GearStage(12, 36), GearStage(10, 20)]
        self.assertEqual(path_ratio(stages), Fraction(1, 6))
        result = evaluate_train(6, stages)
        self.assertEqual(result["output_rpm"], "1")
        self.assertEqual(result["output_direction"], "same")

    def test_counter_index_step_is_explicit(self):
        result = counter_index_spec(2, 30)
        self.assertEqual(result["event_interval_seconds"], "1800")
        self.assertEqual(result["angular_step_degrees"], "12")

    def test_counter_architecture_remains_unselected(self):
        result = counter_architecture_comparison()
        self.assertEqual(result["decision"], "open; requires dial convention, load measurements, packaging and reliability evidence")

    def test_analysis_checks_supplied_path(self):
        result = analyze({
            "input_rpm": "2",
            "stages": [{"driver_teeth": 10, "driven_teeth": 20}],
            "target_period_seconds": 60,
            "tolerance_fraction": "0",
        })
        self.assertTrue(result["target_comparison"]["passes_supplied_tolerance"])
        self.assertEqual(result["train"]["output_direction"], "opposite")

    def test_rejects_bad_inputs(self):
        with self.assertRaises(ValueError):
            GearStage(0, 20).signed_ratio()
        with self.assertRaises(ValueError):
            required_ratio(0, 60)
        with self.assertRaises(ValueError):
            counter_index_spec(2.5, 30)


if __name__ == "__main__":
    unittest.main()
