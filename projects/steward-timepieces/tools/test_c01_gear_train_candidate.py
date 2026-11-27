"""WP-26 synthetic fixture tests; no fixture values are C-01 design data."""
import unittest

from c01_gear_train_candidate import evaluate_candidate


def fixture():
    return {
        "candidate_id": "wp26-test-fixture",
        "provenance": {"evidence": "synthetic unit-test fixture", "source_revision": "test-only"},
        "arbors": [
            {"id": "a", "role": "fixture input", "component_id": "barrel", "axis_id": "axis-a",
             "evidence": "synthetic", "source_revision": "test"},
            {"id": "b", "role": "fixture output", "component_id": "center_wheel", "axis_id": "axis-b",
             "evidence": "synthetic", "source_revision": "test"},
        ],
        "mesh_specs": [{
            "id": "mesh-ab", "arbor_a_id": "a", "arbor_b_id": "b",
            "driver_gear_id": "gear-a", "driven_gear_id": "gear-b",
            "mesh_type": "external", "target_ratio": "1/2",
            "evidence": "synthetic", "source_revision": "test",
            "search": {"min_teeth": 10, "max_teeth": 20,
                       "min_stage_ratio": "1/2", "max_stage_ratio": "1/2",
                       "max_fractional_error": 0, "max_results": 3,
                       "module_mm": "0.1"},
            "center_distance_tolerance_mm": 0,
        }],
        "common_search": {},
        "input": {"arbor_id": "a", "rpm": 2},
        "outputs": [{"id": "out", "arbor_id": "b", "period_seconds": 60,
                     "max_fractional_error": 0}],
        "max_combinations": 5,
    }


class CandidateIntegrationTests(unittest.TestCase):
    def test_synthesis_and_exact_kinematic_closure(self):
        result = evaluate_candidate(fixture())
        self.assertGreater(result["compatible_candidate_count"], 0)
        candidate = result["candidates"][0]
        self.assertEqual(candidate["kinematic_closure"]["outputs"][0]["path_evaluation"]["output_rpm"], "-1")
        self.assertTrue(candidate["kinematic_targets_all_pass_supplied_tolerance"])

    def test_geometry_uses_explicit_coordinates_and_module(self):
        data = fixture()
        data["arbors"][0]["xy_mm"] = [0, 0]
        data["arbors"][1]["xy_mm"] = [1.5, 0]
        result = evaluate_candidate(data)
        check = result["candidates"][0]["center_distance_checks"][0]
        self.assertEqual(check["nominal_center_distance_mm"], 1.5)
        self.assertTrue(check["passes_supplied_center_distance_tolerance"])

    def test_missing_coordinates_not_assumed(self):
        result = evaluate_candidate(fixture())
        self.assertEqual(result["candidates"][0]["center_distance_checks"][0]["status"],
                         "not_evaluable_missing_module_or_coordinates")

    def test_conflicting_shared_gear_arbor_rejected(self):
        data = fixture()
        data["arbors"].append({"id": "c", "role": "fixture", "component_id": "third_wheel",
                               "axis_id": "axis-c", "evidence": "synthetic", "source_revision": "test"})
        data["mesh_specs"].append({
            "id": "mesh-bc", "arbor_a_id": "c", "arbor_b_id": "a",
            "driver_gear_id": "gear-b", "driven_gear_id": "gear-c",
            "mesh_type": "external", "target_ratio": "1/2",
            "evidence": "synthetic", "source_revision": "test",
            "search": {"min_teeth": 10, "max_teeth": 20,
                       "min_stage_ratio": "1/2", "max_stage_ratio": "1/2",
                       "max_fractional_error": 0, "max_results": 2},
        })
        with self.assertRaises(ValueError):
            evaluate_candidate(data)

    def test_no_default_search_bounds(self):
        data = fixture()
        data["mesh_specs"][0]["search"] = {}
        with self.assertRaises(ValueError):
            evaluate_candidate(data)

    def test_internal_mesh_synthesis_not_silently_supported(self):
        data = fixture()
        data["mesh_specs"][0]["mesh_type"] = "internal"
        with self.assertRaises(ValueError):
            evaluate_candidate(data)


if __name__ == "__main__":
    unittest.main()
