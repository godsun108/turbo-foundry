import unittest
from c01_central_core_topology import build_model, render_svg

class CentralCoreTopologyTests(unittest.TestCase):
    def setUp(self):
        self.model = build_model()

    def test_candidate_train_path_is_contiguous(self):
        path = self.model["candidate_going_train"]
        self.assertEqual(path, ["barrel", "center", "third", "fourth", "escape", "pallet", "balance"])
        node_ids = {n["id"] for n in self.model["nodes"]}
        self.assertTrue(set(path).issubset(node_ids))

    def test_chronograph_takeoff_is_not_selected(self):
        self.assertEqual(self.model["chronograph_takeoff_candidates"],
                         ["center", "fourth", "derived_intermediate_stage"])

    def test_required_functions_are_represented(self):
        groups = {n["group"] for n in self.model["nodes"]}
        self.assertTrue({"power", "train", "regulator", "automatic", "chronograph", "calendar", "display"}.issubset(groups))

    def test_physical_geometry_remains_unresolved(self):
        self.assertIsNone(self.model["datum"]["physical_axes"])
        for key in ("arbor_coordinates", "tooth_counts", "center_distances", "clearances", "tolerances"):
            self.assertIn(key, self.model["unresolved"])

    def test_no_dimensions_or_performance_claims(self):
        self.assertIn("No physical coordinates", self.model["evidence_policy"])
        svg = render_svg(self.model)
        self.assertIn("NOT TO SCALE", svg)
        self.assertIn("No wheel centers", svg)

    def test_sq_a_is_only_a_working_configuration(self):
        self.assertIn("working study configuration only", self.model["configuration"])

if __name__ == "__main__":
    unittest.main()
