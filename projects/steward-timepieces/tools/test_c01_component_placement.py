import unittest

from c01_component_placement import (
    conceptual_register, validate_placement, validate_register,
)


class ComponentPlacementTests(unittest.TestCase):
    def test_starter_register_is_valid_and_unlocated(self):
        rows = conceptual_register()
        result = validate_register(rows)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["xy_assigned_count"], 0)
        self.assertEqual(result["xy_unassigned_count"], len(rows))

    def test_xy_must_be_a_pair(self):
        item = conceptual_register()[0]
        item["x_mm"] = 12
        self.assertIn("x_mm and y_mm must be supplied together",
                      validate_placement(item))

    def test_tbd_cannot_claim_xy(self):
        item = conceptual_register()[0]
        item["x_mm"], item["y_mm"] = 1, 2
        self.assertIn("TBD placement cannot carry assigned XY coordinates",
                      validate_placement(item))

    def test_z_interval_must_have_positive_extent(self):
        item = conceptual_register()[0]
        item["z_min_mm"], item["z_max_mm"] = 2, 2
        self.assertIn("z_max_mm must exceed z_min_mm",
                      validate_placement(item))

    def test_envelope_requires_positive_dimensions(self):
        item = conceptual_register()[0]
        item["envelope_mm"] = {"x": 1, "y": 0, "z": 1}
        self.assertIn("envelope_mm.y must be positive",
                      validate_placement(item))

    def test_duplicate_ids_rejected(self):
        rows = conceptual_register()[:2]
        rows[1]["component_id"] = rows[0]["component_id"]
        self.assertFalse(validate_register(rows)["valid"])

    def test_measured_location_requires_traceable_source_label(self):
        item = conceptual_register()[0]
        item.update({"status": "measured", "x_mm": 1, "y_mm": 2, "source": ""})
        self.assertIn("source must identify evidence or state 'not assigned'",
                      validate_placement(item))


if __name__ == "__main__":
    unittest.main()
