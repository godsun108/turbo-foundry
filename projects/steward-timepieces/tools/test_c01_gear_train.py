import unittest

from c01_gear_train import (
    compare_chronograph_states,
    compound_train_ratio,
    evaluate_energy_budget,
    evaluate_energy_transfer,
    gear_pair_ratio,
    integrate_torque_angle_energy,
    reserve_from_energy_and_power,
    wheel_speed_rpm,
)


class GearTrainTests(unittest.TestCase):
    def test_gear_pair_ratio(self):
        result = gear_pair_ratio(10, 40)
        self.assertEqual(result["driven_speed_per_driver_speed"], 0.25)
        self.assertEqual(result["ideal_torque_multiplier"], 4.0)

    def test_compound_train_ratio(self):
        result = compound_train_ratio([
            {"driver_teeth": 10, "driven_teeth": 40},
            {"driver_teeth": 12, "driven_teeth": 36},
        ])
        self.assertAlmostEqual(result["output_speed_per_input_speed"], 1 / 12)
        self.assertAlmostEqual(result["ideal_torque_multiplier"], 12)

    def test_invalid_tooth_counts(self):
        with self.assertRaises(ValueError):
            gear_pair_ratio(0, 20)
        with self.assertRaises(ValueError):
            gear_pair_ratio(10.5, 20)

    def test_wheel_speed(self):
        self.assertEqual(wheel_speed_rpm(60, 0.25), 15)

    def test_torque_angle_integration(self):
        result = integrate_torque_angle_energy([
            {"angle_rad": 0.0, "torque_nm": 0.1},
            {"angle_rad": 1.0, "torque_nm": 0.2},
            {"angle_rad": 2.0, "torque_nm": 0.1},
        ])
        self.assertAlmostEqual(result["integrated_work_j"], 0.3)

    def test_torque_angle_requires_ordered_samples(self):
        with self.assertRaises(ValueError):
            integrate_torque_angle_energy([
                {"angle_rad": 1.0, "torque_nm": 0.1},
                {"angle_rad": 1.0, "torque_nm": 0.2},
            ])

    def test_energy_transfer(self):
        result = evaluate_energy_transfer({
            "input_energy_j": 10,
            "output_energy_j": 8,
            "approved_minimum_efficiency": 0.75,
        })
        self.assertAlmostEqual(result["measured_efficiency"], 0.8)
        self.assertTrue(result["passes_efficiency_limit"])

    def test_passive_transfer_rejects_gain(self):
        with self.assertRaises(ValueError):
            evaluate_energy_transfer({"input_energy_j": 1, "output_energy_j": 1.1})

    def test_energy_budget(self):
        result = evaluate_energy_budget({
            "usable_barrel_energy_j": 10,
            "going_train_loss_j": 1,
            "escapement_demand_j": 5,
            "chronograph_incremental_demand_j": 1,
            "calendar_incremental_demand_j": 0.1,
            "other_incremental_demand_j": 0.2,
            "interval_seconds": 3600,
        })
        self.assertAlmostEqual(result["total_required_energy_j"], 7.3)
        self.assertTrue(result["energy_budget_nonnegative"])

    def test_negative_energy_margin_reported(self):
        result = evaluate_energy_budget({
            "usable_barrel_energy_j": 2,
            "going_train_loss_j": 1,
            "escapement_demand_j": 2,
            "chronograph_incremental_demand_j": 1,
            "calendar_incremental_demand_j": 0,
            "other_incremental_demand_j": 0,
            "interval_seconds": 3600,
        })
        self.assertFalse(result["energy_budget_nonnegative"])

    def test_reserve_estimate(self):
        self.assertAlmostEqual(reserve_from_energy_and_power(720, 0.002), 100)

    def test_chronograph_states_require_matched_intervals(self):
        with self.assertRaises(ValueError):
            compare_chronograph_states(
                {"energy_demand_j": 2, "interval_seconds": 10},
                {"energy_demand_j": 3, "interval_seconds": 11},
            )

    def test_chronograph_incremental_load(self):
        result = compare_chronograph_states(
            {"energy_demand_j": 2, "interval_seconds": 100},
            {"energy_demand_j": 2.5, "interval_seconds": 100},
        )
        self.assertAlmostEqual(result["chronograph_incremental_average_power_w"], 0.005)


if __name__ == "__main__":
    unittest.main()
