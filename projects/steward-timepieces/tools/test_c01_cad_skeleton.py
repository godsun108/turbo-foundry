import unittest

from c01_cad_skeleton import generate_openscad, validate_config


def fixture():
    return {
        "candidate_id": "synthetic-test-fixture",
        "provenance": {"evidence": "unit-test fixture only", "source_revision": "TEST"},
        "plate": {
            "outline_xy_mm": [[0, 0], [10, 0], [10, 8], [0, 8]],
            "thickness_mm": 1.2,
            "top_z_mm": 0,
        },
        "bearing_bores": [{
            "id": "bore-a", "component_id": "barrel", "axis_id": "AX-A",
            "xy_mm": [2, 2], "diameter_mm": 0.8,
            "evidence": "unit-test fixture only", "source_revision": "TEST",
        }],
        "bridges": [{
            "id": "bridge-a", "outline_xy_mm": [[1, 1], [4, 1], [4, 3], [1, 3]],
            "z_min_mm": 1.5, "z_max_mm": 2.1,
            "supported_components": ["barrel"],
            "evidence": "unit-test fixture only", "source_revision": "TEST",
        }],
        "keepouts": [{
            "id": "balance-envelope", "xy_mm": [7, 4], "radius_mm": 1.5,
            "z_min_mm": 0.2, "z_max_mm": 1.4,
            "evidence": "unit-test fixture only", "source_revision": "TEST",
        }],
    }


class CadSkeletonTests(unittest.TestCase):
    def test_fixture_validates(self):
        result = validate_config(fixture())
        self.assertTrue(result["geometry_complete_for_skeleton"])
        self.assertEqual(result["bearing_bore_count"], 1)
        self.assertEqual(result["bridge_count"], 1)
        self.assertEqual(result["keepout_count"], 1)

    def test_openscad_contains_supplied_geometry(self):
        source = generate_openscad(fixture())
        self.assertIn("linear_extrude(height = 1.2)", source)
        self.assertIn("cylinder(h = 1.4, r = 0.4)", source)
        self.assertIn("module bridge_bridge_a()", source)
        self.assertIn("module envelope_balance_envelope()", source)

    def test_missing_plate_rejected(self):
        data = fixture()
        del data["plate"]
        with self.assertRaisesRegex(ValueError, "plate geometry"):
            validate_config(data)

    def test_missing_provenance_rejected(self):
        data = fixture()
        data["provenance"] = {}
        with self.assertRaisesRegex(ValueError, "global provenance"):
            validate_config(data)

    def test_invalid_polygon_rejected(self):
        data = fixture()
        data["plate"]["outline_xy_mm"] = [[0, 0], [1, 1]]
        with self.assertRaisesRegex(ValueError, "at least three"):
            validate_config(data)

    def test_duplicate_bore_ids_rejected(self):
        data = fixture()
        data["bearing_bores"].append(dict(data["bearing_bores"][0]))
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_config(data)

    def test_invalid_axial_bridge_extent_rejected(self):
        data = fixture()
        data["bridges"][0]["z_max_mm"] = data["bridges"][0]["z_min_mm"]
        with self.assertRaisesRegex(ValueError, "positive axial extent"):
            validate_config(data)

    def test_keepout_requires_provenance(self):
        data = fixture()
        data["keepouts"][0]["source_revision"] = None
        with self.assertRaisesRegex(ValueError, "evidence and source_revision"):
            validate_config(data)

    def test_fixture_values_are_not_baseline_defaults(self):
        self.assertEqual(fixture()["candidate_id"], "synthetic-test-fixture")
        self.assertIn("unit-test fixture only", fixture()["provenance"]["evidence"])


if __name__ == "__main__":
    unittest.main()
