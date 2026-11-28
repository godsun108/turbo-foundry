"""Synthetic regression tests for the C-01 square packaging comparison model."""
import unittest

from c01_square_packaging_model import (
    CANDIDATES, REQUIRED_SUBSYSTEMS, build_model,
)


class SquarePackagingModelTests(unittest.TestCase):
    def test_all_three_architectures_are_present(self):
        self.assertEqual(set(CANDIDATES), {"SQ-A", "SQ-B", "SQ-C"})

    def test_each_candidate_covers_required_subsystems(self):
        model = build_model()
        for key, candidate in model["candidates"].items():
            with self.subTest(candidate=key):
                self.assertEqual(set(candidate["subsystem_coverage"]), set(REQUIRED_SUBSYSTEMS))
                self.assertEqual(candidate["missing_subsystems"], [])

    def test_no_candidate_claims_dimensions_or_coordinates(self):
        for candidate in build_model()["candidates"].values():
            self.assertIsNone(candidate["coordinates"])
            self.assertIsNone(candidate["dimensions"])
            self.assertEqual(candidate["geometry_status"], "TBD")

    def test_no_candidate_claims_performance(self):
        for candidate in build_model()["candidates"].values():
            self.assertIsNone(candidate["performance_claims"])

    def test_interface_register_is_explicit_and_unresolved(self):
        interfaces = build_model()["interfaces_requiring_resolution"]
        self.assertGreaterEqual(len(interfaces), 10)
        self.assertTrue(all(item["status"] == "TBD" for item in interfaces))

    def test_month_and_moon_phase_remain_out_of_scope(self):
        exclusions = build_model()["scope_exclusions"]
        self.assertIn("month display", exclusions)
        self.assertIn("moon phase", exclusions)

    def test_no_architecture_is_selected(self):
        self.assertIn("No candidate selected", build_model()["decision"])


if __name__ == "__main__":
    unittest.main()
