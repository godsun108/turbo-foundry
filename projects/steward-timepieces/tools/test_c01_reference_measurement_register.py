"""Synthetic regression tests for the reference measurement register."""
import unittest

from c01_reference_measurement_register import FIELDS, blank_record, validate_records


class ReferenceMeasurementRegisterTests(unittest.TestCase):
    def test_blank_template_row_is_ignored(self):
        self.assertEqual(validate_records([blank_record()]), [])

    def test_documented_reference_requires_revision(self):
        row = blank_record()
        row.update({
            "observation_id": "REF-SW500-001",
            "caliber": "SW500",
            "variant": "a",
            "part_interface_id": "GLOBAL-ENVELOPE",
            "parameter": "published_movement_diameter",
            "value": "30.00",
            "unit": "mm",
            "evidence_class": "manufacturer_published",
            "source_document": "Sellita catalogue",
        })
        errors = validate_records([row])
        self.assertIn(
            {"row": "2", "field": "source_revision", "error": "required_for_documented_source"},
            errors,
        )

    def test_measured_record_requires_metrology_traceability(self):
        row = blank_record()
        row.update({
            "observation_id": "MEAS-001",
            "caliber": "SW500",
            "variant": "a",
            "specimen_id": "SAMPLE-01",
            "part_interface_id": "MAIN-PLATE",
            "parameter": "plate_thickness",
            "value": "1.0",
            "unit": "mm",
            "datum": "plate_lower_face",
            "method": "micrometer",
            "instrument": "MIC-01",
            "instrument_resolution": "0.001 mm",
            "calibration_status": "in_calibration",
            "uncertainty": "TBD",
            "evidence_class": "measured",
            "source_document": "inspection record",
            "operator": "operator",
            "measurement_date": "2026-11-28",
        })
        errors = validate_records([row])
        self.assertEqual(errors, [])

    def test_duplicate_observation_ids_are_rejected(self):
        rows = []
        for _ in range(2):
            row = blank_record()
            row.update({
                "observation_id": "DUP-1", "caliber": "SW500", "variant": "a",
                "part_interface_id": "P-1", "parameter": "diameter", "unit": "mm",
                "evidence_class": "tbd", "source_document": "TBD",
            })
            rows.append(row)
        errors = validate_records(rows)
        self.assertTrue(any(error["error"] == "duplicate" for error in errors))

    def test_non_numeric_value_is_rejected(self):
        row = blank_record()
        row.update({
            "observation_id": "BAD-1", "caliber": "SW500", "variant": "a",
            "part_interface_id": "P-1", "parameter": "diameter", "value": "thirty",
            "unit": "mm", "evidence_class": "measured", "source_document": "record",
            "specimen_id": "S-1", "datum": "origin", "method": "method",
            "instrument": "tool", "instrument_resolution": "0.01 mm",
            "calibration_status": "valid", "uncertainty": "0.02 mm",
            "operator": "operator", "measurement_date": "2026-11-28",
        })
        errors = validate_records([row])
        self.assertTrue(any(error["field"] == "value" and error["error"] == "must_be_numeric" for error in errors))

    def test_schema_contains_traceability_fields(self):
        for field in ("source_document", "source_revision", "datum", "uncertainty", "reviewer"):
            self.assertIn(field, FIELDS)


if __name__ == "__main__":
    unittest.main()
