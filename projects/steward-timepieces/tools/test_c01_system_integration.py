"""Synthetic unit fixtures for C-01 integrated system calculations.

Numbers here exercise arithmetic and validation only; they are not movement
design values, supplier data, or measured prototype results.
"""
import unittest

from c01_system_integration import (
    evaluate_axial_stack,
    evaluate_integrated_energy,
)


class IntegratedEnergyTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "boundary_id": "fixture-boundary-A",
            "interval_id": "fixture-interval-001",
            "interval_seconds": 100.0,
            "usable_barrel_energy_j": 10.0,
            "loads": [
                {"component": "going-train-and-escapement", "energy_j": 2.0,
                 "boundary_id": "fixture-boundary-A", "interval_id": "fixture-interval-001"},
                {"component": "chronograph-incremental", "energy_j": 0.5,
                 "boundary_id": "fixture-boundary-A", "interval_id": "fixture-interval-001"},
                {"component": "calendar-incremental", "energy_j": 0.25,
                 "boundary_id": "fixture-boundary-A", "interval_id": "fixture-interval-001"},
            ],
        }

    def test_energy_aggregation_and_reserve_extrapolation(self):
        result = evaluate_integrated_energy(self.data)
        self.assertAlmostEqual(result["total_measured_load_energy_j"], 2.75)
        self.assertAlmostEqual(result["energy_margin_j"], 7.25)
        self.assertAlmostEqual(result["average_measured_system_power_w"], 0.0275)
        self.assertTrue(result["reserve_is_extrapolation"])
        self.assertAlmostEqual(
            result["idealized_reserve_hours_at_measured_average_load"],
            10.0 / 0.0275 / 3600.0,
        )

    def test_rejects_mismatched_boundary(self):
        self.data["loads"][0]["boundary_id"] = "another-boundary"
        with self.assertRaisesRegex(ValueError, "mismatched measurement boundary"):
            evaluate_integrated_energy(self.data)

    def test_rejects_mismatched_interval(self):
        self.data["loads"][0]["interval_id"] = "another-interval"
        with self.assertRaisesRegex(ValueError, "mismatched measurement interval"):
            evaluate_integrated_energy(self.data)

    def test_rejects_duplicate_component_double_count(self):
        self.data["loads"].append(dict(self.data["loads"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate component"):
            evaluate_integrated_energy(self.data)

    def test_rejects_missing_loads(self):
        self.data["loads"] = []
        with self.assertRaisesRegex(ValueError, "non-empty list"):
            evaluate_integrated_energy(self.data)

    def test_rejects_energy_exceeding_usable_energy_without_hiding_it(self):
        self.data["loads"][0]["energy_j"] = 20.0
        result = evaluate_integrated_energy(self.data)
        self.assertLess(result["energy_margin_j"], 0)
        self.assertFalse(result["energy_margin_nonnegative"])

    def test_rejects_nonfinite_values(self):
        self.data["interval_seconds"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite"):
            evaluate_integrated_energy(self.data)


class AxialStackTests(unittest.TestCase):
    def test_worst_case_stack(self):
        result = evaluate_axial_stack([
            {"name": "fixture-plate", "nominal_mm": 1.0,
             "tolerance_plus_mm": 0.02, "tolerance_minus_mm": 0.01},
            {"name": "fixture-spacer", "nominal_mm": 0.5,
             "tolerance_plus_mm": 0.01, "tolerance_minus_mm": 0.01},
        ])
        self.assertAlmostEqual(result["nominal_stack_mm"], 1.5)
        self.assertAlmostEqual(result["worst_case_upper_mm"], 1.53)
        self.assertAlmostEqual(result["worst_case_lower_mm"], 1.48)
        self.assertAlmostEqual(result["worst_case_total_tolerance_band_mm"], 0.05)

    def test_rejects_incomplete_dimensions(self):
        with self.assertRaisesRegex(ValueError, "nominal_mm"):
            evaluate_axial_stack([{"name": "unknown-part"}])

    def test_rejects_negative_tolerance(self):
        with self.assertRaisesRegex(ValueError, "non-negative"):
            evaluate_axial_stack([{
                "name": "fixture-part", "nominal_mm": 1.0,
                "tolerance_plus_mm": -0.01, "tolerance_minus_mm": 0.01,
            }])


if __name__ == "__main__":
    unittest.main()
