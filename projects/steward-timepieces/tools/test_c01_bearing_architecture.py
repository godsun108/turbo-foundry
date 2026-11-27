"""Synthetic-fixture tests for integrated C-01 bearing architecture."""
import unittest

from c01_bearing_architecture import (
    evaluate_candidate, validate_support_architecture,
)


def fixture():
    return {
        "candidate_id": "fixture-only",
        "provenance": {"evidence": "synthetic test fixture", "source_revision": "test"},
        "arbors": [
            {"id": "a", "role": "fixture arbor", "component_id": "center_wheel",
             "axis_id": "AX-A", "xy_mm": [0, 0], "support_ids": ["s1", "s2"],
             "evidence": "synthetic test fixture", "source_revision": "test"},
        ],
        "supports": [
            {"id": "s1", "arbor_id": "a", "axis_id": "AX-A",
             "structure_id": "plate", "support_type": "fixture jewel",
             "z_mm": 0.0, "evidence": "synthetic test fixture", "source_revision": "test"},
            {"id": "s2", "arbor_id": "a", "axis_id": "AX-A",
             "structure_id": "bridge", "support_type": "fixture jewel",
             "z_mm": 1.0, "evidence": "synthetic test fixture", "source_revision": "test"},
        ],
        "structural_members": [
            {"id": "plate", "member_type": "main_plate",
             "evidence": "synthetic test fixture", "source_revision": "test"},
            {"id": "bridge", "member_type": "bridge",
             "supported_components": ["center_wheel"],
             "evidence": "synthetic test fixture", "source_revision": "test"},
        ],
        "gear_meshes": [],
        "bearing_bore_specs": {
            "a": {"id": "bore_a", "diameter_mm": 0.8,
                  "evidence": "synthetic test fixture", "source_revision": "test"}
        },
    }


class SupportArchitectureTests(unittest.TestCase):
    def test_resolves_plate_bridge_supports_and_span(self):
        result = validate_support_architecture(fixture(), {"center_wheel"})
        self.assertTrue(result["all_support_references_resolve"])
        self.assertEqual(result["support_topology"][0]["axial_support_span_mm"], 1.0)

    def test_unknown_structural_member_rejected(self):
        data = fixture()
        data["supports"][0]["structure_id"] = "missing"
        with self.assertRaises(ValueError):
            validate_support_architecture(data)

    def test_bridge_must_declare_supported_component(self):
        data = fixture()
        data["structural_members"][1]["supported_components"] = ["third_wheel"]
        with self.assertRaises(ValueError):
            validate_support_architecture(data)

    def test_support_axis_must_match_arbor_axis(self):
        data = fixture()
        data["supports"][0]["axis_id"] = "WRONG"
        with self.assertRaises(ValueError):
            validate_support_architecture(data)

    def test_arbor_support_ids_must_match_register(self):
        data = fixture()
        data["arbors"][0]["support_ids"] = ["s1"]
        with self.assertRaises(ValueError):
            validate_support_architecture(data)

    def test_support_count_is_not_assumed_universally(self):
        data = fixture()
        data["arbors"][0]["support_ids"] = ["s1"]
        data["supports"] = data["supports"][:1]
        result = validate_support_architecture(data)
        self.assertEqual(result["support_topology"][0]["declared_support_count"], 1)
        self.assertEqual(result["support_topology"][0]["topology_status"],
                         "support_records_present_but_axial_span_incomplete")

    def test_integrated_candidate_exports_only_explicit_bores(self):
        result = evaluate_candidate(fixture(), {"center_wheel"})
        self.assertEqual(result["cad_bore_handoff"]["bore_count"], 1)
        self.assertEqual(result["overall_fit_status"], "not_certified")

    def test_bore_handoff_requires_explicit_traceability(self):
        data = fixture()
        data["bearing_bore_specs"]["a"] = {"diameter_mm": 0.8}
        with self.assertRaises(ValueError):
            evaluate_candidate(data)


if __name__ == "__main__":
    unittest.main()
