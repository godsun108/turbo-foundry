import unittest

from c01_structure_layout import build_baseline, evaluate_candidate, evaluate_stack, validate_register


class StructureLayoutTests(unittest.TestCase):
    def test_baseline_has_controlled_datum_ids_but_no_values(self):
        data = build_baseline()
        self.assertEqual(data["master_datum_id"], "M0")
        self.assertTrue(all(item["z_mm"] is None for item in data["datums"]))
        self.assertEqual(data["bearing_axes"], [])
        self.assertEqual(data["bridges"], [])

    def test_baseline_evaluates_without_invented_geometry(self):
        result = evaluate_candidate(build_baseline())
        self.assertEqual(result["overall_fit_status"], "not_certified")
        self.assertEqual(result["structural_geometry_status"], "not_evaluable")
        self.assertEqual(result["missing_reference_datums"], [])

    def test_duplicate_datum_rejected(self):
        data = build_baseline()
        data["datums"].append(dict(data["datums"][0]))
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_register(data)

    def test_unknown_master_datum_rejected(self):
        data = build_baseline()
        data["master_datum_id"] = "UNKNOWN"
        with self.assertRaisesRegex(ValueError, "master_datum_id"):
            validate_register(data)

    def test_bearing_component_reference_checked(self):
        data = build_baseline()
        data["bearing_axes"] = [{
            "id": "AX-01", "component_id": "not_a_component", "axis_id": "ARB-01",
            "support_type": "TBD", "evidence": "drawing", "source_revision": "A"
        }]
        with self.assertRaisesRegex(ValueError, "unknown component"):
            evaluate_candidate(data, {"barrel"})

    def test_bridge_component_reference_checked(self):
        data = build_baseline()
        data["bridges"] = [{
            "id": "BR-01", "zone": "going_train", "supported_components": ["ghost"],
            "evidence": "layout", "source_revision": "A"
        }]
        with self.assertRaisesRegex(ValueError, "unknown components"):
            evaluate_candidate(data, {"barrel"})

    def test_stack_overlap_detected_with_traceable_intervals(self):
        result = evaluate_stack([
            {"id": "part-a", "zone": "going_train", "z_min_mm": 0, "z_max_mm": 2,
             "evidence": "fixture", "source_revision": "test"},
            {"id": "part-b", "zone": "going_train", "z_min_mm": 1.5, "z_max_mm": 3,
             "evidence": "fixture", "source_revision": "test"},
        ])
        self.assertTrue(result["overlap_detected"])
        self.assertAlmostEqual(result["overlaps"][0]["overlap_mm"], 0.5)

    def test_touching_intervals_are_not_positive_overlap(self):
        result = evaluate_stack([
            {"id": "part-a", "zone": "calendar_dial_side", "z_min_mm": 0, "z_max_mm": 1,
             "evidence": "fixture", "source_revision": "test"},
            {"id": "part-b", "zone": "calendar_dial_side", "z_min_mm": 1, "z_max_mm": 2,
             "evidence": "fixture", "source_revision": "test"},
        ])
        self.assertFalse(result["overlap_detected"])

    def test_invalid_interval_rejected(self):
        with self.assertRaisesRegex(ValueError, "positive extent"):
            evaluate_stack([{"id": "bad", "zone": "main_plate", "z_min_mm": 2, "z_max_mm": 2,
                             "evidence": "fixture", "source_revision": "test"}])

    def test_missing_provenance_rejected(self):
        with self.assertRaisesRegex(ValueError, "evidence and source_revision"):
            evaluate_stack([{"id": "part", "zone": "main_plate", "z_min_mm": 0, "z_max_mm": 1}])


if __name__ == "__main__":
    unittest.main()
