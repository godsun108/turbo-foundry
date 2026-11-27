import unittest

from c01_integrated_layout import (
    build_baseline, evaluate_candidate, validate_interfaces,
)


class IntegratedLayoutTests(unittest.TestCase):
    def test_baseline_has_required_functional_components(self):
        baseline = build_baseline()
        ids = {item["id"] for item in baseline["components"]}
        self.assertIn("chrono_seconds", ids)
        self.assertIn("chrono_30m", ids)
        self.assertIn("chrono_12h", ids)
        self.assertIn("weekday_display", ids)
        self.assertIn("date_display", ids)
        self.assertIn("automatic_rotor", ids)
        self.assertTrue(all(item["xy_mm"] is None for item in baseline["components"]))

    def test_baseline_interfaces_resolve(self):
        baseline = build_baseline()
        result = validate_interfaces(baseline["components"], baseline["interfaces"])
        self.assertTrue(result["all_interface_endpoints_resolve"])

    def test_missing_geometry_is_not_evaluable(self):
        baseline = build_baseline()
        result = evaluate_candidate({
            "candidate_id": "fixture-incomplete",
            "components": baseline["components"],
            "interfaces": baseline["interfaces"],
        })
        self.assertEqual(result["geometry_status"], "not_evaluable")
        self.assertEqual(result["completeness_status"], "complete_register")
        self.assertEqual(result["overall_fit_status"], "not_certified")

    def test_partial_geometry_only_evaluates_supplied_subset(self):
        baseline = build_baseline()
        components = [dict(item) for item in baseline["components"]]
        components[0].update({
            "x_mm": 0, "y_mm": 0, "envelope_radius_mm": 1,
            "z_min_mm": 0, "z_max_mm": 1, "layer": "fixture",
        })
        result = evaluate_candidate({
            "candidate_id": "fixture-partial",
            "components": components,
            "interfaces": baseline["interfaces"],
        })
        self.assertEqual(result["geometry_status"], "evaluated_subset_only")
        self.assertEqual(result["geometric_component_count"], 1)
        self.assertGreater(len(result["components_missing_geometry"]), 0)
        self.assertFalse(result["interference_detected_in_evaluated_subset"])

    def test_unknown_interface_endpoint_rejected(self):
        baseline = build_baseline()
        edges = list(baseline["interfaces"]) + [{
            "from": "not_a_component", "to": "barrel", "type": "energy"
        }]
        with self.assertRaises(ValueError):
            validate_interfaces(baseline["components"], edges)

    def test_duplicate_component_id_rejected(self):
        baseline = build_baseline()
        components = list(baseline["components"]) + [dict(baseline["components"][0])]
        with self.assertRaises(ValueError):
            validate_interfaces(components, baseline["interfaces"])

    def test_display_and_packaging_options_remain_unselected(self):
        baseline = build_baseline()
        self.assertEqual(set(baseline["display_alternatives"]), {"A", "B", "C"})
        self.assertTrue(all(v["status"] == "candidate_not_selected"
                            for v in baseline["display_alternatives"].values()))
        self.assertTrue(all(v["status"] == "candidate_not_selected"
                            for v in baseline["packaging_families"]))


if __name__ == "__main__":
    unittest.main()
