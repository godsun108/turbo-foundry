"""Synthetic WP-66 regression fixtures; not measured C-01 engineering data."""
import unittest
from c01_source_train_test_system import (
    validate_channel_register, validate_campaign, validate_barrel_curve,
    validate_reserve_profile, validate_train_speed_series,
    validate_energy_comparison, release_gates,
)

def ch(i,kind):
    return {"channel_id":i,"measurand":kind,"unit":"synthetic","boundary_id":"B",
      "sensor_id":"S"+i,"instrument_id":"I"+i,"calibration_record_id":"CAL"+i,
      "calibration_status":"current","range_min":-1,"range_max":1,
      "resolution":0.001,"bandwidth_hz":10,"sample_rate_hz":100,
      "sample_method":"simultaneous","timebase_id":"T","evidence_id":"E"+i,
      "source_revision":"synthetic-r1","loading_assessment_id":"L"+i,
      "anti_alias_disposition":"synthetic-filter"}
KINDS=["barrel_torque","barrel_angle_or_state","barrel_speed",
 "going_train_input_torque","going_train_input_speed","going_train_output_speed",
 "balance_amplitude","rate","beat_error","temperature","event_marker"]

class WP66Tests(unittest.TestCase):
    def test_channel_register_complete(self):
        self.assertTrue(validate_channel_register([ch(str(i),k) for i,k in enumerate(KINDS)])["complete_for_full_campaign"])
    def test_duplicate_channel_rejected(self):
        with self.assertRaises(ValueError): validate_channel_register([ch("x","barrel_torque"),ch("x","barrel_speed")])
    def test_nyquist_floor(self):
        x=ch("x","barrel_torque"); x["sample_rate_hz"]=19
        with self.assertRaises(ValueError): validate_channel_register([x])
    def test_barrel_curve_energy(self):
        r=validate_barrel_curve([{"angle_rad":0,"torque_nm":1},{"angle_rad":2,"torque_nm":1}],"E","R")
        self.assertEqual(r["integrated_energy_j"],2)
        self.assertFalse(r["reserve_hours_inferred"])
    def test_barrel_curve_rejects_nonmonotonic(self):
        with self.assertRaises(ValueError):
            validate_barrel_curve([{"angle_rad":1,"torque_nm":1},{"angle_rad":1,"torque_nm":2}],"E","R")
    def test_reserve_states_descend(self):
        base={"evidence_id":"E","source_revision":"R","barrel_torque_nm":1,
          "barrel_speed_rpm":1,"amplitude_deg":200,"rate_s_per_day":0}
        states=[dict(base,state_id="full",measured_state_fraction=1),
                dict(base,state_id="mid",measured_state_fraction=.5)]
        self.assertEqual(validate_reserve_profile(states)["state_count"],2)
    def test_reserve_states_no_inference(self):
        base={"evidence_id":"E","source_revision":"R","barrel_torque_nm":1,
          "barrel_speed_rpm":1,"amplitude_deg":200,"rate_s_per_day":0}
        r=validate_reserve_profile([dict(base,state_id="full",measured_state_fraction=1)])
        self.assertFalse(r["hours_remaining_established"])
    def test_train_speed_samples(self):
        r=validate_train_speed_series([{"time_s":0,"input_speed_rpm":1,"output_speed_rpm":2},
          {"time_s":1,"input_speed_rpm":1,"output_speed_rpm":2}],"E","R")
        self.assertEqual(r["sample_count"],2)
    def test_energy_pair_requires_same_boundary(self):
        a={k:"x" for k in ("movement_revision","boundary_id","interval_id","test_condition_id","reserve_state_id","timebase_sync_id")}
        a.update({"evidence_id":"E1","measured_energy_j":5})
        b=dict(a,evidence_id="E2",boundary_id="other")
        with self.assertRaises(ValueError): validate_energy_comparison(a,b)
    def test_energy_margin_is_not_proof(self):
        a={k:"x" for k in ("movement_revision","boundary_id","interval_id","test_condition_id","reserve_state_id","timebase_sync_id")}
        a.update({"evidence_id":"E1","measured_energy_j":5})
        b=dict(a,evidence_id="E2",measured_energy_j=3)
        r=validate_energy_comparison(a,b)
        self.assertEqual(r["measured_energy_difference_j"],2)
        self.assertFalse(r["physical_power_sufficiency_proven"])
    def test_release_gates_fail_closed(self):
        r=release_gates({})
        self.assertFalse(r["hardware_test_authorized"])
        self.assertEqual(len(r["open_gates"]),10)

if __name__ == "__main__":
    unittest.main()
