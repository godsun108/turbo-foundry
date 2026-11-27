"""Synthetic fixtures for the C-01 architecture-envelope helper.

The values below are intentionally fictitious and test arithmetic only.
They are not C-01 dimensions or fit evidence.
"""
import unittest

from c01_architecture_envelope import (
    evaluate_axial_intervals,
    evaluate_planar_zone,
    normalized_point_to_mm,
    validate_axis_register,
)


class CoordinateTests(unittest.TestCase):
    def test_normalized_conversion_requires_explicit_radius(self):
        result = normalized_point_to_mm(0.5, -0.25, 10.0)
        self.assertAlmostEqual(result["x_mm"], 5.0)
        self.assertAlmostEqual(result["y_mm"], -2.5)
        self.assertAlmostEqual(result["radial_distance_mm"], (31.25) ** 0.5)

    def test_rejects_nonpositive_opening_radius(self):
        with self.assertRaises(ValueError):
            normalized_point_to_mm(0, 0, 0)


class PlanarZoneTests(unittest.TestCase):
    def test_corner_check_inside(self):
        result = evaluate_planar_zone({
            "name": "fixture-window", "x_over_r": 0, "y_over_r": 0,
            "width_over_r": 0.2, "height_over_r": 0.2,
            "evidence": "provisional",
        }, 10.0)
        self.assertTrue(result["within_circular_opening_by_corner_test"])
        self.assertFalse(result["fit_certified"])

    def test_corner_check_outside(self):
        result = evaluate_planar_zone({
            "name": "fixture-window", "x_over_r": 0.9, "y_over_r": 0,
            "width_over_r": 0.3, "height_over_r": 0.1,
            "evidence": "provisional",
        }, 10.0)
        self.assertFalse(result["within_circular_opening_by_corner_test"])

    def test_rejects_missing_evidence(self):
        with self.assertRaisesRegex(ValueError, "missing zone fields"):
            evaluate_planar_zone({"name": "fixture"}, 10.0)


class AxialIntervalTests(unittest.TestCase):
    def test_same_layer_overlap_is_flagged(self):
        result = evaluate_axial_intervals([
            {"name": "fixture-plate", "z_min_mm": 0, "z_max_mm": 1,
             "layer": "movement", "evidence": "provisional"},
            {"name": "fixture-wheel", "z_min_mm": 0.8, "z_max_mm": 1.2,
             "layer": "movement", "evidence": "provisional"},
        ])
        self.assertTrue(result["has_same_layer_intersections"])
        self.assertAlmostEqual(result["same_layer_intersections"][0]["overlap_mm"], 0.2)

    def test_different_layers_not_compared(self):
        result = evaluate_axial_intervals([
            {"name": "fixture-dial", "z_min_mm": 0, "z_max_mm": 1,
             "layer": "dial", "evidence": "provisional"},
            {"name": "fixture-rotor", "z_min_mm": 0, "z_max_mm": 1,
             "layer": "rotor", "evidence": "provisional"},
        ])
        self.assertFalse(result["has_same_layer_intersections"])

    def test_rejects_invalid_interval(self):
        with self.assertRaisesRegex(ValueError, "must exceed"):
            evaluate_axial_intervals([{
                "name": "fixture", "z_min_mm": 1, "z_max_mm": 1,
                "layer": "movement", "evidence": "provisional",
            }])


class AxisRegisterTests(unittest.TestCase):
    def test_unresolved_axes_remain_open(self):
        result = validate_axis_register([
            {"name": "center", "x_mm": 0, "y_mm": 0,
             "evidence": "provisional", "source_id": "concept-origin"},
            {"name": "barrel", "x_mm": None, "y_mm": None,
             "evidence": "TBD", "source_id": ""},
        ])
        self.assertFalse(result["architecture_ready"])
        self.assertEqual(result["unresolved_axes"], ["barrel"])

    def test_measured_axis_requires_source(self):
        with self.assertRaisesRegex(ValueError, "source_id required"):
            validate_axis_register([{
                "name": "fixture-axis", "x_mm": 1, "y_mm": 2,
                "evidence": "measured", "source_id": "",
            }])


if __name__ == "__main__":
    unittest.main()
