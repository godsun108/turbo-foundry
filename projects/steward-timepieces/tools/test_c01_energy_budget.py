import unittest

from c01_energy_budget import (
    TorquePoint,
    average_power_w,
    integrate_usable_barrel_energy,
    output_power_w,
    required_energy_j,
    reserve_change_percent,
    series_efficiency,
)


class EnergyBudgetTests(unittest.TestCase):
    def test_trapezoid_energy(self):
        points = [TorquePoint(0.0, 0.1), TorquePoint(2.0, 0.1)]
        self.assertAlmostEqual(integrate_usable_barrel_energy(points), 0.2)

    def test_average_power_and_required_energy_round_trip(self):
        power = average_power_w(100.0, 50.0)
        self.assertAlmostEqual(required_energy_j(power, 50.0), 100.0)

    def test_reserve_change(self):
        self.assertAlmostEqual(reserve_change_percent(54.0, 62.0), 14.8148148148)

    def test_series_efficiency(self):
        self.assertAlmostEqual(series_efficiency([0.9, 0.8]), 0.72)
        self.assertAlmostEqual(output_power_w(1.0, 0.72), 0.72)

    def test_rejects_non_monotonic_samples(self):
        with self.assertRaises(ValueError):
            integrate_usable_barrel_energy([
                TorquePoint(1.0, 0.1),
                TorquePoint(0.5, 0.1),
            ])


if __name__ == "__main__":
    unittest.main()
