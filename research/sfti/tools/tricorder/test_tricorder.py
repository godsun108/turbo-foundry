"""Unit tests for the dependency-free TRICORDER data tool."""
import unittest
from datetime import datetime, timezone

from tricorder import SCHEMA_VERSION, simulated_records, validate_observation


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.record = next(simulated_records(1))
        self.record["quality_status"] = "valid"
        self.record["calibration_id"] = "cal-test-001"

    def test_simulated_record_has_required_shape(self):
        record = next(simulated_records(1))
        self.assertEqual(validate_observation(record), [])

    def test_valid_record_passes(self):
        self.assertEqual(validate_observation(self.record), [])

    def test_missing_unit_fails(self):
        del self.record["unit"]
        self.assertTrue(validate_observation(self.record))

    def test_naive_timestamp_fails(self):
        self.record["observed_at"] = "2026-01-01T12:00:00"
        self.assertIn("observed_at must include a timezone", validate_observation(self.record))

    def test_non_finite_value_fails(self):
        self.record["value"] = float("nan")
        self.assertIn("value must be a finite number", validate_observation(self.record))

    def test_boolean_is_not_numeric_measurement(self):
        self.record["value"] = True
        self.assertIn("value must be a finite number", validate_observation(self.record))

    def test_unknown_field_fails(self):
        self.record["operator_override"] = True
        self.assertTrue(any("unknown fields" in item for item in validate_observation(self.record)))

    def test_unsupported_quality_fails(self):
        self.record["quality_status"] = "probably_fine"
        self.assertIn("quality_status is not a supported status", validate_observation(self.record))

    def test_malformed_quality_type_fails_without_crashing(self):
        self.record["quality_status"] = ["valid"]
        self.assertIn("quality_status is not a supported status", validate_observation(self.record))


if __name__ == "__main__":
    unittest.main()
