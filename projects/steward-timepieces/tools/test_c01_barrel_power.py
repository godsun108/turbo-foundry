"""Synthetic fixture tests for WP-27; no values represent C-01 hardware."""
import unittest

from c01_barrel_power import (
    compare_chronograph_energy, evaluate_energy_case, evaluate_usable_barrel_window,
    evaluate_winding_capture, integrate_torque_angle, power_at_barrel_interface,
)


class BarrelPowerTests(unittest.TestCase):
    def test_trapezoidal_spring_energy(self):
        result = integrate_torque_angle([
            {"angle_rad": 0, "torque_nm": 0.1},
            {"angle_rad": 2, "torque_nm": 0.1},
        ])
        self.assertAlmostEqual(result["integrated_work_j"], 0.2)

    def test_usable_window_interpolates_measured_curve(self):
        result = evaluate_usable_barrel_window({
            "torque_angle_samples": [
                {"angle_rad": 0, "torque_nm": 0.1},
                {"angle_rad": 2, "torque_nm": 0.2},
                {"angle_rad": 4, "torque_nm": 0.1},
            ],
            "operating_start_angle_rad": 1,
            "operating_end_angle_rad": 3,
        })
        self.assertAlmostEqual(result["usable_spring_energy_j"], 0.35)

    def test_rejects_extrapolation_outside_measured_curve(self):
        with self.assertRaises(ValueError):
            evaluate_usable_barrel_window({
                "torque_angle_samples": [
                    {"angle_rad": 0, "torque_nm": 0.1},
                    {"angle_rad": 1, "torque_nm": 0.1},
                ],
                "operating_start_angle_rad": -1,
                "operating_end_angle_rad": 1,
            })

    def test_shaft_power(self):
        result = power_at_barrel_interface(0.2, 3)
        self.assertAlmostEqual(result["ideal_shaft_power_w"], 0.6)

    def test_winding_capture(self):
        result = evaluate_winding_capture({
            "rotor_input_energy_j": 10, "barrel_energy_gain_j": 6,
            "rotor_revolutions": 20, "elapsed_seconds": 100,
        })
        self.assertAlmostEqual(result["measured_winding_efficiency"], 0.6)
        self.assertAlmostEqual(result["barrel_energy_gain_per_rotor_revolution_j"], 0.3)

    def test_chronograph_increment_requires_matched_boundary_and_interval(self):
        stopped = {"boundary_id": "b", "interval_id": "i",
                   "interval_seconds": 100, "energy_demand_j": 2}
        running = {"boundary_id": "b", "interval_id": "i",
                   "interval_seconds": 100, "energy_demand_j": 3}
        result = compare_chronograph_energy(stopped, running)
        self.assertAlmostEqual(result["chronograph_incremental_energy_j"], 1)
        running["interval_id"] = "other"
        with self.assertRaises(ValueError):
            compare_chronograph_energy(stopped, running)

    def test_energy_case_and_reserve_extrapolation(self):
        result = evaluate_energy_case({
            "boundary_id": "barrel-output", "interval_id": "trial-1",
            "interval_seconds": 100, "usable_barrel_energy_j": 100,
            "loads": [
                {"component": "going-train", "energy_j": 10,
                 "boundary_id": "barrel-output", "interval_id": "trial-1"},
                {"component": "chrono-incremental", "energy_j": 2,
                 "boundary_id": "barrel-output", "interval_id": "trial-1"},
            ],
            "reserve_target_hours": 60,
        })
        self.assertEqual(result["total_load_energy_j"], 12)
        self.assertAlmostEqual(result["idealized_reserve_hours_at_measured_average_load"],
                               100 / (12 / 100) / 3600)
        self.assertTrue(result["reserve_estimate_is_extrapolation"])

    def test_duplicate_load_rejected(self):
        load = {"component": "same", "energy_j": 1,
                "boundary_id": "b", "interval_id": "i"}
        with self.assertRaises(ValueError):
            evaluate_energy_case({
                "boundary_id": "b", "interval_id": "i",
                "interval_seconds": 10, "usable_barrel_energy_j": 10,
                "loads": [load, dict(load)],
            })

    def test_invalid_torque_curve_rejected(self):
        with self.assertRaises(ValueError):
            integrate_torque_angle([
                {"angle_rad": 1, "torque_nm": 0.1},
                {"angle_rad": 1, "torque_nm": 0.2},
            ])


if __name__ == "__main__":
    unittest.main()
