import unittest

from c01_layout_geometry import (
    evaluate_component_clearances, evaluate_gear_mesh, evaluate_layout,
    gear_pitch_radius_mm, normalized_to_mm,
)


class LayoutGeometryTests(unittest.TestCase):
    def test_pitch_radius(self):
        self.assertEqual(gear_pitch_radius_mm(20, 0.1), 1.0)

    def test_external_mesh_nominal_center_distance(self):
        result = evaluate_gear_mesh({
            "id": "fixture-mesh", "driver_teeth": 20, "driven_teeth": 40,
            "module_mm": 0.1, "driver_xy_mm": [0, 0],
            "driven_xy_mm": [3, 0], "center_tolerance_mm": 0.001,
        })
        self.assertAlmostEqual(result["nominal_pitch_center_distance_mm"], 3.0)
        self.assertTrue(result["within_supplied_center_tolerance"])

    def test_center_distance_outside_tolerance(self):
        result = evaluate_gear_mesh({
            "id": "fixture-mesh", "driver_teeth": 20, "driven_teeth": 40,
            "module_mm": 0.1, "driver_xy_mm": [0, 0],
            "driven_xy_mm": [3.1, 0], "center_tolerance_mm": 0.01,
        })
        self.assertFalse(result["within_supplied_center_tolerance"])

    def test_axial_overlap_clearance(self):
        result = evaluate_component_clearances([
            {"id": "a", "x_mm": 0, "y_mm": 0, "envelope_radius_mm": 1,
             "z_min_mm": 0, "z_max_mm": 1, "layer": "train"},
            {"id": "b", "x_mm": 3, "y_mm": 0, "envelope_radius_mm": 1,
             "z_min_mm": 0.5, "z_max_mm": 1.5, "layer": "bridge"},
        ])
        self.assertEqual(result["checked_pairs_with_axial_overlap"], 1)
        self.assertTrue(result["clearance_results"][0]["planar_envelopes_clear"])

    def test_interference_is_flagged(self):
        result = evaluate_component_clearances([
            {"id": "a", "x_mm": 0, "y_mm": 0, "envelope_radius_mm": 2,
             "z_min_mm": 0, "z_max_mm": 2, "layer": "a"},
            {"id": "b", "x_mm": 3, "y_mm": 0, "envelope_radius_mm": 2,
             "z_min_mm": 1, "z_max_mm": 3, "layer": "b"},
        ])
        self.assertTrue(result["has_envelope_interference"])

    def test_no_planar_check_without_z_overlap(self):
        result = evaluate_component_clearances([
            {"id": "a", "x_mm": 0, "y_mm": 0, "envelope_radius_mm": 2,
             "z_min_mm": 0, "z_max_mm": 1, "layer": "dial"},
            {"id": "b", "x_mm": 0, "y_mm": 0, "envelope_radius_mm": 2,
             "z_min_mm": 2, "z_max_mm": 3, "layer": "rotor"},
        ])
        self.assertEqual(result["checked_pairs_with_axial_overlap"], 0)

    def test_normalized_dial_coordinate_conversion(self):
        result = normalized_to_mm(0.5, -0.5, 10)
        self.assertEqual(result["x_mm"], 5)
        self.assertEqual(result["y_mm"], -5)

    def test_layout_does_not_claim_fit_certification(self):
        result = evaluate_layout({"gear_meshes": [], "components": []})
        self.assertFalse(result["overall_fit_certified"])

    def test_rejects_invalid_geometry(self):
        with self.assertRaises(ValueError):
            gear_pitch_radius_mm(0, 0.1)
        with self.assertRaises(ValueError):
            evaluate_component_clearances([{
                "id": "bad", "x_mm": 0, "y_mm": 0, "envelope_radius_mm": 1,
                "z_min_mm": 2, "z_max_mm": 1, "layer": "x",
            }])


if __name__ == "__main__":
    unittest.main()
