import unittest
from c01_data_acquisition import (
    AcquisitionError, validate_run_manifest, validate_samples, apply_clock_correction,
    interpolate_at, force_travel_metrics, angular_error_deg, reset_zero_result,
    event_latency, validate_comparison,
)

class TestDataAcquisition(unittest.TestCase):
    def test_manifest_calibration_gate(self):
        m={"run_id":"R","candidate_id":"CW","candidate_revision":"A","article_id":"X",
           "fixture_id":"F","fixture_revision":"A","procedure_id":"P","procedure_revision":"A",
           "test_condition_id":"T","evidence_id":"E","source_revision":"S","operator_id":"O",
           "started_at_utc":"2026-11-27T00:00:00Z",
           "channels":[{"channel_id":"force","measurand":"force","unit":"N","instrument_id":"I",
             "calibration_id":"C","calibration_status":"current","sampling_method":"simultaneous",
             "evidence_id":"E","source_revision":"S","sample_rate_hz":100}]}
        self.assertTrue(validate_run_manifest(m)["valid"])
        m["channels"][0]["calibration_status"]="expired"
        self.assertFalse(validate_run_manifest(m)["valid"])
    def test_monotonic_timestamps(self):
        with self.assertRaises(AcquisitionError):
            validate_samples([{"time_s":0,"value":1},{"time_s":0,"value":2}],"x")
    def test_clock_correction(self):
        r=apply_clock_correction([{"time_s":0,"value":1},{"time_s":2,"value":2}],.1,.01,"SYN","R1")
        self.assertAlmostEqual(r["samples"][1]["time_s"],2.12)
    def test_interpolation_no_extrapolation(self):
        s=[{"time_s":0,"value":0},{"time_s":2,"value":4}]
        self.assertAlmostEqual(interpolate_at(s,[1])[0]["value"],2)
        with self.assertRaises(AcquisitionError): interpolate_at(s,[3])
    def test_force_travel_work(self):
        r=force_travel_metrics([{"time_s":0,"travel_mm":0,"force_n":2},
          {"time_s":1,"travel_mm":2,"force_n":4}],"SYN","R1")
        self.assertAlmostEqual(r["signed_force_travel_work_j"],.006)
        self.assertEqual(r["peak_sampled_force_n"],4)
    def test_angular_wrap(self):
        self.assertAlmostEqual(angular_error_deg(1,359),2)
        self.assertAlmostEqual(angular_error_deg(359,1),-2)
    def test_reset_circular_mean(self):
        r=reset_zero_result([359,1],0,"SYN","R1")
        self.assertAlmostEqual(r["circular_mean_error_deg"],0,places=6)
    def test_event_latency(self):
        r=event_latency([{"event_id":"input","time_s":1},{"event_id":"motion","time_s":1.2}],
                        "input","motion","SYN","R1")
        self.assertAlmostEqual(r["latency_s"],.2)
    def test_comparison_metadata(self):
        a={"procedure_id":"P","procedure_revision":"1","test_condition_id":"T",
           "fixture_id":"F","fixture_revision":"1","candidate_id":"CW"}
        b={**a,"candidate_id":"CL"}
        self.assertTrue(validate_comparison(a,b)["comparable_on_declared_fields"])
        b["test_condition_id"]="T2"
        self.assertFalse(validate_comparison(a,b)["comparable_on_declared_fields"])

if __name__=="__main__": unittest.main()
