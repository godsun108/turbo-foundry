"""Synthetic WP-64 regression fixtures; never C-01 measurement data."""
import unittest
from c01_power_distribution import (
    aggregate_load_ledger, analyze_event_window, compare_chronograph_conditions,
    evaluate_supply_demand, evaluate_timekeeping_delta, integrate_power_samples,
    shaft_power_w,
)

def series(evidence, powers, boundary="B1", interval="I1"):
    return {"movement_revision":"REV-SYNTH","boundary_id":boundary,
            "interval_id":interval,"test_condition_id":"COND-SYNTH",
            "reserve_state_id":"STATE-SYNTH","evidence_id":evidence,
            "samples":[{"time_s":0,"power_w":powers[0]},
                       {"time_s":10,"power_w":powers[1]},
                       {"time_s":20,"power_w":powers[2]}]}

class PowerDistributionTests(unittest.TestCase):
    def test_shaft_power_from_explicit_torque_and_speed(self):
        self.assertAlmostEqual(shaft_power_w(0.1,60),0.1*2*3.141592653589793,places=10)

    def test_power_integration_trapezoidal(self):
        result=integrate_power_samples([{"time_s":0,"power_w":1},
                                        {"time_s":2,"power_w":3}])
        self.assertEqual(result["energy_j"],4)
        self.assertEqual(result["mean_power_w"],2)

    def test_nonmonotonic_sample_times_rejected(self):
        with self.assertRaises(ValueError):
            integrate_power_samples([{"time_s":1,"power_w":1},{"time_s":1,"power_w":2}])

    def test_matched_chronograph_off_on_increment(self):
        result=compare_chronograph_conditions(series("OFF-E", [1,1,1]),
                                               series("ON-E", [2,3,2]))
        self.assertEqual(result["incremental_energy_j"],30)
        self.assertEqual(result["mean_incremental_power_w"],1.5)
        self.assertEqual(result["peak_sampled_incremental_power_w"],2)

    def test_off_on_metadata_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            compare_chronograph_conditions(series("OFF-E",[1,1,1]),
                                           series("ON-E",[2,2,2],boundary="B2"))

    def test_supply_demand_margin_is_explicit(self):
        result=evaluate_supply_demand({"boundary_id":"B","operating_state_id":"RUN",
            "movement_revision":"R","supply_power_w":2,"demand_power_w":1.5,
            "supply_evidence_id":"S","demand_evidence_id":"D"})
        self.assertEqual(result["power_margin_w"],0.5)
        self.assertTrue(result["measured_margin_nonnegative"])
        self.assertTrue(result["does_not_prove_dynamic_transient_capacity"])

    def test_load_ledger_prevents_double_counting_and_mismatched_intervals(self):
        base={"movement_revision":"R","boundary_id":"B","interval_id":"I",
              "test_condition_id":"C","reserve_state_id":"S","evidence_id":"E"}
        rows=[{**base,"load_id":"a","power_w":1},
              {**base,"load_id":"b","power_w":2}]
        self.assertEqual(aggregate_load_ledger(rows)["total_power_w"],3)
        with self.assertRaises(ValueError):
            aggregate_load_ledger([rows[0],dict(rows[0])])
        rows[1]["interval_id"]="OTHER"
        with self.assertRaises(ValueError):
            aggregate_load_ledger(rows)

    def test_event_window_requires_measured_boundaries(self):
        samples=[{"time_s":0,"power_w":1},{"time_s":5,"power_w":3},
                 {"time_s":10,"power_w":1},{"time_s":15,"power_w":1}]
        result=analyze_event_window(samples,5,10)
        self.assertEqual(result["energy_j"],10)
        with self.assertRaises(ValueError):
            analyze_event_window(samples,2,10)

    def test_timekeeping_delta_uses_supplied_limits_only(self):
        off={"movement_revision":"R","test_condition_id":"C","reserve_state_id":"S",
             "evidence_id":"OFF","rate_s_day":1,"amplitude_deg":270}
        on={**off,"evidence_id":"ON","rate_s_day":3,"amplitude_deg":250}
        result=evaluate_timekeeping_delta(off,on,2,240)
        self.assertEqual(result["rate_delta_s_day"],2)
        self.assertTrue(result["rate_delta_within_supplied_limit"])
        self.assertTrue(result["on_amplitude_meets_supplied_floor"])

if __name__=="__main__":
    unittest.main()
