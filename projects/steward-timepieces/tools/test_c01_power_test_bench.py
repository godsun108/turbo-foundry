"""Synthetic regression tests for WP-65; fixtures are not C-01 design data."""
import unittest
from c01_power_test_bench import (
    validate_channel, validate_channel_register, validate_power_measurement_plan,
    validate_timebase_sync, combine_uncertainty, validate_raw_channel_samples,
    validate_run_manifest, validate_matched_pair, release_review_gates,
)

def channel(cid, measurand):
    return {"channel_id":cid,"measurand":measurand,"unit":"synthetic",
      "measurement_boundary":"fixture-interface-A","sensor_id":"S-"+cid,
      "instrument_id":"I-"+cid,"calibration_record_id":"CAL-"+cid,
      "calibration_status":"current","range_min":-10,"range_max":10,
      "resolution":0.01,"bandwidth_hz":100,"sample_rate_hz":1000,
      "sampling_method":"simultaneous","timebase_id":"TB-1",
      "evidence_id":"SYNTH-"+cid,"source_revision":"fixture-r1",
      "anti_alias_filter_id":"SYNTH-FILTER","loading_assessment_id":"SYNTH-LOAD"}

class WP65Tests(unittest.TestCase):
    def test_channel_valid(self):
        self.assertTrue(validate_channel(channel("C1","torque"))["channel_valid"])
    def test_duplicate_channel_rejected(self):
        with self.assertRaises(ValueError):
            validate_channel_register([channel("C1","torque"),channel("C1","speed")])
    def test_nyquist_minimum_enforced(self):
        c=channel("C1","torque"); c["sample_rate_hz"]=150
        with self.assertRaises(ValueError): validate_channel(c)
    def test_calibration_must_be_current(self):
        c=channel("C1","torque"); c["calibration_status"]="expired"
        with self.assertRaises(ValueError): validate_channel(c)
    def test_plan_needs_all_measurands(self):
        p={"plan_id":"P","revision":"A","movement_revision":"M","fixture_revision":"F",
           "procedure_revision":"PR","test_condition_id":"TC","measurement_boundary":"B",
           "uncertainty_budget_id":"U","safety_review_id":"S","approver":"A",
           "candidate_architecture":"column_wheel","channels":[channel("1","torque")],
           "status":"approved","safety_review_status":"approved"}
        with self.assertRaises(ValueError): validate_power_measurement_plan(p)
    def test_timebase_sync(self):
        s={"sync_id":"SYNC","reference_timebase_id":"REF","method":"common clock",
           "evidence_id":"E","source_revision":"R","measured_offset_s":0.001,
           "measured_drift_s_per_s":0,"expanded_time_uncertainty_s":0.0001,
           "verification_status":"verified","raw_timestamps_preserved":True}
        self.assertTrue(validate_timebase_sync(s)["sync_verified"])
    def test_uncertainty_requires_independence_basis(self):
        b={"measurand":"torque","unit":"N.m","method_reference":"M",
           "independence_justified":False,"components":[],"coverage_factor":2}
        with self.assertRaises(ValueError): combine_uncertainty(b)
    def test_uncertainty_rss(self):
        b={"measurand":"torque","unit":"N.m","method_reference":"M",
           "independence_justified":True,"components":[
             {"component_id":"a","standard_uncertainty":3,"source_or_rationale":"synthetic"},
             {"component_id":"b","standard_uncertainty":4,"source_or_rationale":"synthetic"}],
           "coverage_factor":2}
        self.assertEqual(combine_uncertainty(b)["expanded_uncertainty"],10)
    def test_raw_samples_monotonic(self):
        with self.assertRaises(ValueError):
            validate_raw_channel_samples([{"time_s":0,"value":1},{"time_s":0,"value":2}],"C")
    def test_manifest_sha256(self):
        m={k:"x" for k in ("run_id","candidate_id","candidate_revision","movement_revision",
          "fixture_revision","procedure_revision","test_condition_id","reserve_state_id",
          "boundary_id","interval_id","timebase_sync_id","raw_data_uri","evidence_id",
          "source_revision","operator_id","started_at_utc")}
        m.update({"candidate_architecture":"cam_lever","raw_data_sha256":"a"*64,"raw_data_immutable":True})
        self.assertTrue(validate_run_manifest(m)["valid"])
    def test_pair_requires_same_boundary(self):
        a={k:"x" for k in ("movement_revision","fixture_revision","procedure_revision",
          "test_condition_id","reserve_state_id","boundary_id","interval_id","timebase_sync_id")}
        a.update({"run_id":"off","candidate_architecture":"column_wheel"})
        b=dict(a,run_id="on",boundary_id="different")
        with self.assertRaises(ValueError): validate_matched_pair(a,b)
    def test_release_gates_fail_closed(self):
        r=release_review_gates({})
        self.assertFalse(r["hardware_test_authorized"])
        self.assertEqual(len(r["open_gates"]),8)

if __name__ == "__main__":
    unittest.main()
