import unittest

from c01_barrel_energy_model import TorqueSample, calculate, integrate_energy


class BarrelEnergyModelTests(unittest.TestCase):
    def setUp(self):
        self.inputs = {
            "torque_samples": [
                {"angle_rad": 0.0, "torque_nm": 0.10},
                {"angle_rad": 10.0, "torque_nm": 0.10},
            ],
            "train_efficiency": 0.80,
            "base_load_w": 0.00001,
            "chrono_incremental_load_w": 0.000002,
            "calendar_event_energy_j": 0.01,
            "calendar_events_per_day": 2,
        }

    def test_integrates_constant_torque(self):
        self.assertAlmostEqual(
            integrate_energy([TorqueSample(0.0, 0.1), TorqueSample(10.0, 0.1)]),
            1.0,
        )

    def test_chronograph_running_reduces_estimated_reserve(self):
        result = calculate(self.inputs)
        self.assertGreater(
            result["chrono_stopped"]["estimated_reserve_hours"],
            result["chrono_running"]["estimated_reserve_hours"],
        )

    def test_calendar_load_is_averaged_at_output_plane(self):
        result = calculate(self.inputs)
        self.assertAlmostEqual(
            result["calendar_average_load_w"], 0.02 / 86400.0
        )

    def test_zero_chronograph_load_equalizes_reserve_cases(self):
        data = dict(self.inputs, chrono_incremental_load_w=0.0)
        result = calculate(data)
        self.assertAlmostEqual(
            result["chrono_stopped"]["estimated_reserve_hours"],
            result["chrono_running"]["estimated_reserve_hours"],
        )

    def test_rejects_unordered_samples(self):
        with self.assertRaises(ValueError):
            integrate_energy([TorqueSample(2.0, 0.1), TorqueSample(1.0, 0.1)])

    def test_rejects_efficiency_above_one(self):
        data = dict(self.inputs, train_efficiency=1.1)
        with self.assertRaises(ValueError):
            calculate(data)

    def test_requires_calendar_inputs_as_a_pair(self):
        data = dict(self.inputs, calendar_events_per_day=0.0)
        with self.assertRaises(ValueError):
            calculate(data)


if __name__ == "__main__":
    unittest.main()
