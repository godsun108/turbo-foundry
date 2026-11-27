"""Synthetic fixture tests for WP-25 going-train kinematic closure."""
import unittest
from fractions import Fraction

from c01_going_train import (
    compare_escapement_frequency, evaluate_outputs, evaluate_path,
    target_speed_rpm, validate_train,
)


def fixture():
    return {
        "candidate_id": "fixture-only",
        "arbors": [
            {"id": "barrel", "role": "fixture input", "evidence": "synthetic", "source_revision": "test"},
            {"id": "center", "role": "fixture center arbor", "evidence": "synthetic", "source_revision": "test"},
            {"id": "third", "role": "fixture third arbor", "evidence": "synthetic", "source_revision": "test"},
            {"id": "fourth", "role": "fixture seconds arbor", "evidence": "synthetic", "source_revision": "test"},
        ],
        "gears": [
            {"id": "barrel_wheel", "arbor_id": "barrel", "role": "fixture driver", "teeth": 80, "evidence": "synthetic", "source_revision": "test"},
            {"id": "center_pinion", "arbor_id": "center", "role": "fixture pinion", "teeth": 10, "evidence": "synthetic", "source_revision": "test"},
            {"id": "center_wheel", "arbor_id": "center", "role": "fixture wheel", "teeth": 60, "evidence": "synthetic", "source_revision": "test"},
            {"id": "third_pinion", "arbor_id": "third", "role": "fixture pinion", "teeth": 10, "evidence": "synthetic", "source_revision": "test"},
            {"id": "third_wheel", "arbor_id": "third", "role": "fixture wheel", "teeth": 60, "evidence": "synthetic", "source_revision": "test"},
            {"id": "fourth_pinion", "arbor_id": "fourth", "role": "fixture pinion", "teeth": 10, "evidence": "synthetic", "source_revision": "test"},
        ],
        "meshes": [
            {"id": "m1", "driver_gear_id": "barrel_wheel", "driven_gear_id": "center_pinion", "mesh_type": "external", "evidence": "synthetic", "source_revision": "test"},
            {"id": "m2", "driver_gear_id": "center_wheel", "driven_gear_id": "third_pinion", "mesh_type": "external", "evidence": "synthetic", "source_revision": "test"},
            {"id": "m3", "driver_gear_id": "third_wheel", "driven_gear_id": "fourth_pinion", "mesh_type": "external", "evidence": "synthetic", "source_revision": "test"},
        ],
    }


class GoingTrainTests(unittest.TestCase):
    def test_target_speed_exact(self):
        self.assertEqual(target_speed_rpm(60), Fraction(1, 1))
        self.assertEqual(target_speed_rpm(3600), Fraction(1, 60))

    def test_compound_path_exact_ratio_and_direction(self):
        result = evaluate_path(fixture(), "barrel", "fourth", 1)
        self.assertEqual(result["status"], "unique_path")
        self.assertEqual(result["signed_compound_speed_ratio"], "-216")
        self.assertEqual(result["output_direction"], "opposite")

    def test_no_path_reported(self):
        data = fixture()
        data["arbors"].append({"id": "isolated", "role": "fixture", "evidence": "synthetic", "source_revision": "test"})
        result = evaluate_path(data, "barrel", "isolated", 1)
        self.assertEqual(result["status"], "no_path")

    def test_multiple_paths_not_arbitrarily_selected(self):
        data = fixture()
        data["arbors"].append({"id": "alternate", "role": "fixture", "evidence": "synthetic", "source_revision": "test"})
        data["gears"].extend([
            {"id": "alternate_driver", "arbor_id": "barrel", "role": "fixture", "teeth": 20, "evidence": "synthetic", "source_revision": "test"},
            {"id": "alternate_driven", "arbor_id": "alternate", "role": "fixture", "teeth": 20, "evidence": "synthetic", "source_revision": "test"},
            {"id": "alternate_output", "arbor_id": "alternate", "role": "fixture", "teeth": 20, "evidence": "synthetic", "source_revision": "test"},
        ])
        data["meshes"].append({"id": "m4", "driver_gear_id": "alternate_driver", "driven_gear_id": "alternate_driven", "mesh_type": "external", "evidence": "synthetic", "source_revision": "test"})
        data["meshes"].append({"id": "m5", "driver_gear_id": "alternate_output", "driven_gear_id": "fourth_pinion", "mesh_type": "external", "evidence": "synthetic", "source_revision": "test"})
        self.assertEqual(evaluate_path(data, "barrel", "fourth", 1)["status"], "multiple_paths")

    def test_invalid_same_arbor_mesh_rejected(self):
        data = fixture()
        data["meshes"][0]["driven_gear_id"] = "center_wheel"
        with self.assertRaises(ValueError):
            validate_train(data)

    def test_output_target_comparison(self):
        data = fixture()
        data["input"] = {"arbor_id": "barrel", "rpm": "1/216"}
        data["outputs"] = [{"id": "seconds", "arbor_id": "fourth", "period_seconds": 60}]
        result = evaluate_outputs(data)
        self.assertEqual(result["outputs"][0]["path_evaluation"]["output_rpm"], "1")
        self.assertEqual(result["outputs"][0]["fractional_absolute_speed_error"], "0")

    def test_missing_tolerance_not_assumed(self):
        data = fixture()
        data["input"] = {"arbor_id": "barrel", "rpm": "1/216"}
        data["outputs"] = [{"id": "seconds", "arbor_id": "fourth", "period_seconds": 60}]
        result = evaluate_outputs(data)
        self.assertIsNone(result["outputs"][0]["passes_supplied_speed_tolerance"])

    def test_conditional_escapement_relationship(self):
        result = compare_escapement_frequency(4, 2, 15, 15)
        self.assertEqual(result["conditional_escape_wheel_speed_rpm"], "16")

    def test_escape_wheel_speed_requires_event_definition(self):
        with self.assertRaises(ValueError):
            compare_escapement_frequency(4, 2, 15, 0)


if __name__ == "__main__":
    unittest.main()
