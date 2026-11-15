"""Tests for append-only recovery and shared sensor-health summary."""
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tricorder import simulated_records
from tricorder_store import ObservationStore, StoreCorruptionError
from sensor_health import summarize_sensor_health


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "observations.jsonl"

    def tearDown(self):
        self.temp.cleanup()

    def test_append_and_reopen_preserves_sequence(self):
        store = ObservationStore(self.path)
        first = next(simulated_records(1))
        self.assertEqual(store.append(first), 1)
        reopened = ObservationStore(self.path)
        self.assertEqual(reopened.last_sequence, 1)
        self.assertEqual(list(reopened.iter_records())[0][0], 1)

    def test_torn_final_write_is_discarded(self):
        store = ObservationStore(self.path)
        store.append(next(simulated_records(1)))
        with self.path.open("ab") as stream:
            stream.write(b'{"sequence":2,"partial":')
        recovered = ObservationStore(self.path)
        self.assertEqual(recovered.last_sequence, 1)
        self.assertTrue(self.path.read_bytes().endswith(b"\n"))

    def test_complete_corrupt_record_fails_closed(self):
        self.path.write_bytes(b'{"sequence":1,"observation":{},"sha256":"bad"}\n')
        with self.assertRaises(StoreCorruptionError):
            ObservationStore(self.path)

    def test_invalid_observation_rejected_before_append(self):
        store = ObservationStore(self.path)
        bad = next(simulated_records(1))
        bad["value"] = float("inf")
        with self.assertRaises(ValueError):
            store.append(bad)
        self.assertEqual(store.last_sequence, 0)


class HealthTests(unittest.TestCase):
    def test_latest_sensor_state_and_staleness(self):
        older, newer = list(simulated_records(2))
        older["sensor_id"] = newer["sensor_id"] = "temp-a"
        older["observed_at"] = "2026-01-01T00:00:00Z"
        newer["observed_at"] = "2026-01-01T00:04:00Z"
        newer["quality_status"] = "valid"
        result = summarize_sensor_health(
            [older, newer],
            now=datetime(2026, 1, 1, 0, 10, tzinfo=timezone.utc),
            stale_after_seconds=60,
        )
        self.assertEqual(result["temp-a"]["health_status"], "stale")
        self.assertEqual(result["temp-a"]["last_observed_at"], newer["observed_at"])

    def test_uncalibrated_is_not_reported_as_online(self):
        item = next(simulated_records(1))
        result = summarize_sensor_health([item])
        self.assertEqual(result[item["sensor_id"]]["health_status"], "uncalibrated")


if __name__ == "__main__":
    unittest.main()
