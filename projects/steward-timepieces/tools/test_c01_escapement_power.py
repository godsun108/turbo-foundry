"""Synthetic fixtures for WP-28; no values represent C-01 hardware."""
import unittest

from c01_escapement_power import (
    evaluate_balance_energy_per_event, evaluate_chronograph_supply_effect,
    evaluate_interface_power, evaluate_reserve_state_timekeeping,
)


class EscapementPowerTests(unittest.TestCase):
    def test_interface_power_and_state_envelope(self):
        result = evaluate_interface_power({
            "boundary_id": "escapement-input-plane",
            "speed_match_tolerance_fraction": 0.01,
            "samples": [
                {"state_id": "high-wind", "reserve_state_fraction": 0.9,
                 "supplied_torque_nm": 0.002, "supplied_speed_rad_s": 10,
                 "required_torque_nm": 0.0015, "required_speed_rad_s": 10},
                {"state_id": "low-wind", "reserve_state_fraction": 0.2,
                 "supplied_torque_nm": 0.001, "supplied_speed_rad_s": 10,
                 "required_torque_nm": 0.0012, "required_speed_rad_s": 10},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertEqual(result["states"][0]["state_id"], "low-wind")
        self.assertAlmostEqual(result["states"][0]["ideal_power_margin_w"], -0.002)

    def test_speed_mismatch_fails(self):
        result = evaluate_interface_power({
            "boundary_id": "plane", "speed_match_tolerance_fraction": 0.001,
            "samples": [{"state_id": "s1", "reserve_state_fraction": 0.5,
                         "supplied_torque_nm": 1, "supplied_speed_rad_s": 10,
                         "required_torque_nm": 0.5, "required_speed_rad_s": 9}],
        })
        self.assertFalse(result["states"][0]["speed_match_passed"])

    def test_energy_per_measured_event(self):
        result = evaluate_balance_energy_per_event({
            "boundary_id": "balance-input", "interval_id": "trial-1",
            "measured_energy_j": 0.012, "measured_event_count": 100,
            "interval_seconds": 25,
        })
        self.assertAlmostEqual(result["measured_energy_per_event_j"], 0.00012)
        self.assertAlmostEqual(result["average_measured_power_w"], 0.00048)

    def test_chronograph_comparison_requires_same_boundary_and_interval(self):
        stopped = {"boundary_id": "balance", "interval_id": "same",
                   "interval_seconds": 100, "amplitude_deg": 270,
                   "rate_s_per_day": 1, "measured_power_w": 0.001}
        running = {"boundary_id": "balance", "interval_id": "same",
                   "interval_seconds": 100, "amplitude_deg": 260,
                   "rate_s_per_day": 2, "measured_power_w": 0.0012}
        result = evaluate_chronograph_supply_effect(stopped, running)
        self.assertEqual(result["amplitude_change_deg"], -10)
        self.assertAlmostEqual(result["measured_power_change_w"], 0.0002)
        running["boundary_id"] = "other"
        with self.assertRaises(ValueError):
            evaluate_chronograph_supply_effect(stopped, running)

    def test_reserve_state_timekeeping(self):
        result = evaluate_reserve_state_timekeeping({
            "approved_amplitude_min_deg": 200,
            "approved_amplitude_max_deg": 320,
            "approved_rate_min_s_per_day": -4,
            "approved_rate_max_s_per_day": 6,
            "samples": [
                {"state_id": "full", "reserve_state_fraction": 1,
                 "amplitude_deg": 280, "rate_s_per_day": 1},
                {"state_id": "near-end", "reserve_state_fraction": 0.1,
                 "amplitude_deg": 190, "rate_s_per_day": 2},
            ],
        })
        self.assertFalse(result["passed"])
        self.assertFalse(result["remaining_hours_inferred"])

    def test_duplicate_state_and_invalid_fraction_rejected(self):
        base = {"state_id": "s", "reserve_state_fraction": 0.5,
                "supplied_torque_nm": 1, "supplied_speed_rad_s": 1,
                "required_torque_nm": 1, "required_speed_rad_s": 1}
        with self.assertRaises(ValueError):
            evaluate_interface_power({"boundary_id": "b",
                "speed_match_tolerance_fraction": 0.1,
                "samples": [base, dict(base)]})
        with self.assertRaises(ValueError):
            evaluate_reserve_state_timekeeping({
                "approved_amplitude_min_deg": 0, "approved_amplitude_max_deg": 300,
                "approved_rate_min_s_per_day": -5, "approved_rate_max_s_per_day": 5,
                "samples": [{"state_id": "bad", "reserve_state_fraction": 2,
                             "amplitude_deg": 200, "rate_s_per_day": 0}],
            })


if __name__ == "__main__":
    unittest.main()
