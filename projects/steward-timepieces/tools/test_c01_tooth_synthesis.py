import unittest
from fractions import Fraction

from c01_tooth_synthesis import pair_candidates, synthesize


class ToothSynthesisTests(unittest.TestCase):
    def test_pair_ratio_and_direction(self):
        pairs = pair_candidates(10, 20, "1/2", "2")
        item = next(p for p in pairs if p["driver_teeth"] == 10 and p["driven_teeth"] == 20)
        self.assertEqual(item["speed_ratio_magnitude"], Fraction(1, 2))
        self.assertTrue(item["direction_reversed"])

    def test_exact_one_stage_candidate_and_center_distance(self):
        result = synthesize({
            "target_ratio": "1/2",
            "min_teeth": 10, "max_teeth": 30,
            "min_stage_ratio": "1/3", "max_stage_ratio": "3",
            "max_fractional_error": "0",
            "max_results": 20, "module_mm": "0.1",
        })
        exact = [c for c in result["returned_candidates"] if c["fractional_absolute_ratio_error"] == "0"]
        self.assertTrue(exact)
        one = next(c for c in exact if c["stage_count"] == 1)
        self.assertEqual(one["output_direction_relative_to_input"], "opposite")
        self.assertIn("center_distance_mm", one["stages"][0])

    def test_two_external_meshes_restore_direction(self):
        result = synthesize({
            "target_ratio": "1/6",
            "min_teeth": 10, "max_teeth": 36,
            "min_stage_ratio": "1/6", "max_stage_ratio": "1",
            "max_fractional_error": "0",
            "max_results": 100,
        })
        two = next(c for c in result["returned_candidates"]
                   if c["stage_count"] == 2 and c["fractional_absolute_ratio_error"] == "0")
        self.assertEqual(two["output_direction_relative_to_input"], "same")
        self.assertEqual(two["external_mesh_direction_reversals"], 2)

    def test_error_tolerance_filters_candidates(self):
        result = synthesize({
            "target_ratio": "7/13",
            "min_teeth": 10, "max_teeth": 20,
            "min_stage_ratio": "1/2", "max_stage_ratio": "2",
            "max_fractional_error": "0",
            "max_results": 100,
        })
        self.assertTrue(all(c["fractional_absolute_ratio_error"] == "0"
                            for c in result["returned_candidates"]))

    def test_rejects_invalid_bounds(self):
        base = {
            "target_ratio": "1/2", "min_teeth": 10, "max_teeth": 20,
            "min_stage_ratio": "1/3", "max_stage_ratio": "3",
            "max_fractional_error": "0.01", "max_results": 10,
        }
        for change in ({"min_teeth": 0}, {"max_teeth": 5},
                       {"max_fractional_error": "1"}, {"max_results": 0}):
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    synthesize({**base, **change})


if __name__ == "__main__":
    unittest.main()
