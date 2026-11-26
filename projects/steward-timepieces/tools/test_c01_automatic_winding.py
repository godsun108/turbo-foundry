import unittest

from c01_automatic_winding import (
    compare_trials, evaluate_slipping_bridle, evaluate_trial,
)


class AutomaticWindingTests(unittest.TestCase):
    def trial(self, **overrides):
        data = {
            "rotor_input_energy_j": 1.0,
            "barrel_energy_gain_j": 0.5,
            "rotor_revolutions": 100.0,
            "elapsed_hours": 8.0,
        }
        data.update(overrides)
        return data

    def test_efficiency_and_normalized_metrics(self):
        result = evaluate_trial(self.trial())
        self.assertEqual(result["measured_winding_efficiency"], 0.5)
        self.assertEqual(result["barrel_energy_gain_per_rotor_revolution_j"], 0.005)
        self.assertAlmostEqual(result["average_barrel_energy_gain_w"], 0.5 / 28800)

    def test_zero_barrel_gain_is_valid(self):
        result = evaluate_trial(self.trial(barrel_energy_gain_j=0.0))
        self.assertEqual(result["measured_winding_efficiency"], 0.0)

    def test_barrel_gain_cannot_exceed_input(self):
        with self.assertRaises(ValueError):
            evaluate_trial(self.trial(barrel_energy_gain_j=1.1))

    def test_nonpositive_and_nonfinite_inputs_rejected(self):
        for field, value in [
            ("rotor_input_energy_j", 0),
            ("rotor_revolutions", -1),
            ("elapsed_hours", float("inf")),
        ]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                evaluate_trial(self.trial(**{field: value}))

    def test_aggregate_preserves_trial_range(self):
        result = compare_trials([
            self.trial(),
            self.trial(rotor_input_energy_j=2.0, barrel_energy_gain_j=1.2),
        ])
        self.assertEqual(result["trial_count"], 2)
        self.assertAlmostEqual(result["aggregate_efficiency"], 1.7 / 3.0)
        self.assertEqual(result["minimum_trial_efficiency"], 0.5)
        self.assertEqual(result["maximum_trial_efficiency"], 0.6)

    def test_empty_aggregate_rejected(self):
        with self.assertRaises(ValueError):
            compare_trials([])

    def test_slipping_bridle_limit_comparison(self):
        result = evaluate_slipping_bridle({
            "measured_slip_onset_torque_nm": 0.08,
            "approved_maximum_barrel_torque_nm": 0.1,
        })
        self.assertTrue(result["within_approved_limit"])

    def test_slipping_bridle_exceeding_limit_flagged(self):
        result = evaluate_slipping_bridle({
            "measured_slip_onset_torque_nm": 0.12,
            "approved_maximum_barrel_torque_nm": 0.1,
        })
        self.assertFalse(result["within_approved_limit"])

    def test_invalid_bridle_inputs_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_slipping_bridle({
                "measured_slip_onset_torque_nm": 0,
                "approved_maximum_barrel_torque_nm": 0.1,
            })


if __name__ == "__main__":
    unittest.main()
