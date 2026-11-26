import unittest
from fractions import Fraction

from c01_train_topology import (
    GearStage, analyze_supplied_stages, build_requirements,
    compound_ratio, ideal_torque_after_path, required_speed_rpm,
)


class TrainTopologyTests(unittest.TestCase):
    def test_required_display_speeds_are_exact(self):
        self.assertEqual(required_speed_rpm(60), Fraction(1, 1))
        self.assertEqual(required_speed_rpm(3600), Fraction(1, 60))
        self.assertEqual(required_speed_rpm(43200), Fraction(1, 720))
        self.assertEqual(required_speed_rpm(1800), Fraction(1, 30))

    def test_external_and_internal_mesh_directions(self):
        self.assertEqual(GearStage(12, 36, "external").ratio(), Fraction(-1, 3))
        self.assertEqual(GearStage(12, 36, "internal").ratio(), Fraction(1, 3))

    def test_compound_ratio_multiplies_exactly(self):
        stages = [GearStage(12, 36), GearStage(10, 20)]
        self.assertEqual(compound_ratio(stages), Fraction(1, 6))

    def test_torque_transform_uses_ratio_and_efficiency(self):
        stages = [GearStage(12, 36)]
        self.assertAlmostEqual(ideal_torque_after_path(0.003, stages), 0.009)
        self.assertAlmostEqual(
            ideal_torque_after_path(0.003, stages, [0.8]), 0.0072
        )

    def test_rejects_invalid_mesh_and_tooth_counts(self):
        with self.assertRaises(ValueError):
            GearStage(0, 20).ratio()
        with self.assertRaises(ValueError):
            GearStage(10, 20, "bevel").ratio()

    def test_rejects_efficiency_count_mismatch(self):
        with self.assertRaises(ValueError):
            ideal_torque_after_path(0.01, [GearStage(10, 20)], [])

    def test_topology_keeps_both_power_paths_open(self):
        data = build_requirements()
        self.assertEqual(
            {item["id"] for item in data["power_path_candidates"]},
            {"P1_fourth_wheel_takeoff", "P2_dedicated_chronograph_drive"},
        )
        self.assertTrue(all(
            item["status"] == "candidate_not_selected"
            for item in data["power_path_candidates"]
        ))

    def test_supplied_stage_path_is_evaluated(self):
        result = analyze_supplied_stages({
            "input_rpm": "1",
            "stages": [{"driver_teeth": 10, "driven_teeth": 30, "mesh": "external"}],
        })
        self.assertEqual(result["output_rpm"], "-1/3")
        self.assertEqual(result["output_direction"], "opposite")


if __name__ == "__main__":
    unittest.main()
