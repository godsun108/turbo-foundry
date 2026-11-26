import unittest

from c01_balance_escapement import (
    balance_frequency_from_inertia_and_stiffness,
    evaluate_power_reserve_sweep,
    evaluate_timing_trial,
)


class BalanceEscapementTests(unittest.TestCase):
    def timing_record(self, **overrides):
        data = {
            "frequency_hz": 4.0,
            "rate_s_per_day": 1.0,
            "amplitude_deg": 270.0,
            "beat_error_ms": 0.2,
            "positional_rate_spread_s_per_day": 3.0,
            "chronograph_off_rate_s_per_day": 1.0,
            "chronograph_on_rate_s_per_day": 2.0,
            "frequency_target_hz": 4.0,
            "frequency_tolerance_hz": 0.01,
            "rate_min_s_per_day": -4.0,
            "rate_max_s_per_day": 6.0,
            "amplitude_min_deg": 200.0,
            "amplitude_max_deg": 320.0,
            "beat_error_max_ms": 0.8,
            "positional_rate_spread_max_s_per_day": 8.0,
            "chronograph_rate_delta_max_s_per_day": 3.0,
        }
        data.update(overrides)
        return data

    def test_ideal_frequency_calculation(self):
        result = balance_frequency_from_inertia_and_stiffness(
            balance_inertia_kg_m2=1.0,
            hairspring_torsional_stiffness_n_m_per_rad=(2.0 * 3.141592653589793 * 4.0) ** 2,
        )
        self.assertAlmostEqual(result["ideal_natural_frequency_hz"], 4.0)
        self.assertAlmostEqual(result["ideal_full_period_s"], 0.25)
        self.assertAlmostEqual(result["ideal_half_period_s"], 0.125)

    def test_timing_trial_passes_explicit_limits(self):
        self.assertTrue(evaluate_timing_trial(self.timing_record())["passed"])

    def test_chronograph_rate_interaction_fails_limit(self):
        result = evaluate_timing_trial(
            self.timing_record(chronograph_on_rate_s_per_day=7.0)
        )
        self.assertFalse(result["checks"]["chronograph_interaction_within_limit"])
        self.assertFalse(result["passed"])

    def test_rate_outside_limit_fails(self):
        result = evaluate_timing_trial(self.timing_record(rate_s_per_day=7.0))
        self.assertFalse(result["checks"]["rate_within_limits"])

    def test_missing_limits_are_not_defaulted(self):
        data = self.timing_record()
        del data["beat_error_max_ms"]
        with self.assertRaises(ValueError):
            evaluate_timing_trial(data)

    def test_invalid_frequency_tolerance_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_timing_trial(self.timing_record(frequency_tolerance_hz=0.0))

    def test_reserve_sweep_orders_measured_states(self):
        result = evaluate_power_reserve_sweep(
            [
                {"reserve_state_fraction": 0.2, "amplitude_deg": 230, "rate_s_per_day": 2},
                {"reserve_state_fraction": 0.9, "amplitude_deg": 280, "rate_s_per_day": 1},
            ],
            approved_amplitude_min_deg=200,
            approved_amplitude_max_deg=320,
            approved_rate_min_s_per_day=-4,
            approved_rate_max_s_per_day=6,
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["samples"][0]["reserve_state_fraction"], 0.2)
        self.assertEqual(result["amplitude_span_deg"], 50)

    def test_reserve_sweep_rejects_empty_and_invalid_state(self):
        with self.assertRaises(ValueError):
            evaluate_power_reserve_sweep([], 200, 320, -4, 6)
        with self.assertRaises(ValueError):
            evaluate_power_reserve_sweep(
                [{"reserve_state_fraction": 1.1, "amplitude_deg": 250, "rate_s_per_day": 0}],
                200, 320, -4, 6,
            )


if __name__ == "__main__":
    unittest.main()
