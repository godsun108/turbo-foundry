import unittest
from c01_dynamic_power_envelope import (
    evaluate_reserve_profile, evaluate_operating_load, evaluate_event_increment,
    evaluate_transition, friction_sensitivity, acceptance_summary,
)

class DynamicEnvelopeTests(unittest.TestCase):
    def reserve(self):
        return {"movement_revision":"REV-A","boundary_id":"B1","test_condition_id":"C1",
                "samples":[
                    {"state_id":"full","reserve_state_fraction":1,"source_record_id":"R1",
                     "barrel_torque_nm":0.01,"amplitude_deg":280,"rate_s_per_day":1},
                    {"state_id":"low","reserve_state_fraction":0.2,"source_record_id":"R2",
                     "barrel_torque_nm":0.006,"amplitude_deg":240,"rate_s_per_day":3}]}
    def loads(self):
        base={"boundary_id":"B1","interval_id":"I1","test_condition_id":"C1"}
        return {"movement_revision":"REV-A","boundary_id":"B1","test_condition_id":"C1",
                "interval_id":"I1","interval_seconds":60,
                "loads":[
                    dict(base,load_id="going",category="baseline",incremental=False,energy_j=0.2),
                    dict(base,load_id="chrono",category="chronograph_increment",incremental=True,energy_j=0.03)]}
    def test_reserve_profile_is_ordered_and_not_extrapolated(self):
        r=evaluate_reserve_profile(self.reserve())
        self.assertEqual([x["state_id"] for x in r["states"]],["full","low"])
        self.assertFalse(r["hours_remaining_inferred"])
    def test_duplicate_reserve_fraction_rejected(self):
        d=self.reserve(); d["samples"][1]["reserve_state_fraction"]=1
        with self.assertRaises(ValueError): evaluate_reserve_profile(d)
    def test_load_sum_and_average_power(self):
        r=evaluate_operating_load(self.loads())
        self.assertAlmostEqual(r["total_energy_j"],0.23)
        self.assertAlmostEqual(r["average_power_w"],0.23/60)
    def test_overlapping_load_rejected(self):
        d=self.loads(); d["loads"][0]["includes_other_loads"]=True
        with self.assertRaises(ValueError): evaluate_operating_load(d)
    def test_event_requires_complete_capture(self):
        b={"movement_revision":"REV-A","boundary_id":"B1","test_condition_id":"C1",
           "interval_id":"EV","source_record_id":"S","interval_seconds":10,"energy_j":0.1}
        e=dict(b,source_record_id="E",energy_j=0.13,event_complete=True)
        self.assertAlmostEqual(evaluate_event_increment(b,e)["event_incremental_energy_j"],0.03)
        e["event_complete"]=False
        with self.assertRaises(ValueError): evaluate_event_increment(b,e)
    def test_event_requires_matched_window(self):
        b={"movement_revision":"REV-A","boundary_id":"B1","test_condition_id":"C1",
           "interval_id":"EV","source_record_id":"S","interval_seconds":10,"energy_j":0.1}
        e=dict(b,source_record_id="E",energy_j=0.13,event_complete=True,interval_seconds=9)
        with self.assertRaises(ValueError): evaluate_event_increment(b,e)
    def test_transition_signed_deltas(self):
        rows=[]
        for phase,t,p in (("before",1,0.1),("during",2,0.12),("after",3,0.11)):
            rows.append({"phase":phase,"movement_revision":"REV-A","boundary_id":"B1",
                         "test_condition_id":"C1","timestamp_seconds":t,
                         "measured_power_w":p,"amplitude_deg":250,"rate_s_per_day":2})
        r=evaluate_transition(rows)
        self.assertAlmostEqual(r["during_minus_before"]["measured_power_w"],0.02)
        self.assertFalse(r["transient_interpolation_performed"])
    def test_friction_scenario_requires_evidence_and_bounds(self):
        r=friction_sensitivity(1.0,0.1,"LAB-17")
        self.assertAlmostEqual(r["scenario_downstream_energy_j"],0.9)
        with self.assertRaises(ValueError): friction_sensitivity(1,1.0,"LAB-17")
        with self.assertRaises(ValueError): friction_sensitivity(1,0.1," ")
    def test_join_and_no_reserve_claim(self):
        r=evaluate_reserve_profile(self.reserve())
        l=evaluate_operating_load(self.loads())
        a=acceptance_summary(r,l)
        self.assertTrue(a["measurement_join_passed"])
        self.assertFalse(a["full_run_down_proven"])
    def test_mismatched_revision_rejected(self):
        r=evaluate_reserve_profile(self.reserve())
        l=self.loads(); l["movement_revision"]="REV-B"
        with self.assertRaises(ValueError): acceptance_summary(r,evaluate_operating_load(l))

if __name__ == "__main__":
    unittest.main()
