"""Synthetic-fixture tests for C-01 arbor coordinate calculations."""
import unittest

from c01_arbor_coordinates import (
    cad_bore_register, evaluate_candidate, evaluate_mesh,
    gear_center_distance, solve_axis_from_polar,
    solve_two_circle_intersections, validate_register,
)


class GearCenterDistanceTests(unittest.TestCase):
    def test_external_nominal_center_distance(self):
        self.assertAlmostEqual(gear_center_distance(0.5, 20, 40), 15.0)

    def test_internal_nominal_center_distance(self):
        self.assertAlmostEqual(gear_center_distance(0.5, 80, 20, "internal"), 15.0)

    def test_invalid_mesh_and_teeth_rejected(self):
        for args in [(0.5, 20, 20, "internal"), (0.5, 0, 20, "external"),
                     (0.5, 20, 20, "bevel")]:
            with self.assertRaises(ValueError):
                gear_center_distance(*args)


class CoordinateSolverTests(unittest.TestCase):
    def test_polar_coordinate_solution(self):
        result = solve_axis_from_polar([0, 0], 10, 0)
        self.assertAlmostEqual(result["xy_mm"][0], 10)
        self.assertAlmostEqual(result["xy_mm"][1], 0)

    def test_two_circle_intersections_retain_both_branches(self):
        result = solve_two_circle_intersections([0, 0], 5, [6, 0], 5)
        self.assertEqual(result["solution_count"], 2)
        self.assertAlmostEqual(result["solutions_xy_mm"][0][1],
                               -result["solutions_xy_mm"][1][1])

    def test_tangent_and_no_intersection(self):
        tangent = solve_two_circle_intersections([0, 0], 5, [10, 0], 5)
        self.assertEqual(tangent["status"], "tangent")
        absent = solve_two_circle_intersections([0, 0], 2, [10, 0], 2)
        self.assertEqual(absent["status"], "no_intersection")


class RegisterAndMeshTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "candidate_id": "fixture-only",
            "arbors": [
                {"id": "a", "role": "fixture driver", "component_id": "center_wheel",
                 "axis_id": "AX-A", "xy_mm": [0, 0], "support_ids": ["sa"],
                 "evidence": "synthetic test fixture", "source_revision": "test"},
                {"id": "b", "role": "fixture driven", "component_id": "third_wheel",
                 "axis_id": "AX-B", "xy_mm": [15, 0], "support_ids": ["sb"],
                 "evidence": "synthetic test fixture", "source_revision": "test"},
            ],
            "supports": [
                {"id": "sa", "arbor_id": "a", "structure_id": "fixture plate",
                 "support_type": "fixture", "evidence": "synthetic test fixture",
                 "source_revision": "test"},
                {"id": "sb", "arbor_id": "b", "structure_id": "fixture bridge",
                 "support_type": "fixture", "evidence": "synthetic test fixture",
                 "source_revision": "test"},
            ],
            "gear_meshes": [
                {"id": "mesh-a-b", "arbor_a_id": "a", "arbor_b_id": "b",
                 "module_mm": 0.5, "gear_a_teeth": 20, "gear_b_teeth": 40,
                 "mesh": "external", "center_distance_tolerance_mm": 0.01,
                 "evidence": "synthetic test fixture", "source_revision": "test"},
            ],
        }

    def test_candidate_mesh_passes_fixture_tolerance(self):
        result = evaluate_candidate(self.data)
        self.assertTrue(result["all_evaluated_meshes_within_supplied_tolerance"])

    def test_mesh_fails_when_centers_are_wrong(self):
        mesh = dict(self.data["gear_meshes"][0], xy_a_mm=[0, 0], xy_b_mm=[16, 0])
        self.assertFalse(evaluate_mesh(mesh)["passes_supplied_center_distance_tolerance"])

    def test_unknown_support_rejected(self):
        self.data["arbors"][0]["support_ids"] = ["missing"]
        with self.assertRaises(ValueError):
            validate_register(self.data)

    def test_unknown_component_rejected(self):
        with self.assertRaises(ValueError):
            validate_register(self.data, {"barrel"})

    def test_cad_bore_export_requires_explicit_traceable_diameter(self):
        arbors = self.data["arbors"]
        specs = {"a": {"diameter_mm": 0.8, "evidence": "fixture",
                       "source_revision": "test"}}
        output = cad_bore_register(arbors, specs)
        self.assertEqual(len(output), 1)
        self.assertEqual(output[0]["xy_mm"], [0.0, 0.0])
        with self.assertRaises(ValueError):
            cad_bore_register(arbors, {"a": {"diameter_mm": 0.8}})


if __name__ == "__main__":
    unittest.main()
