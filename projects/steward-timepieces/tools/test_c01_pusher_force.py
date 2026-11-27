import unittest
from c01_pusher_force import (PusherEngineeringError,lever_stage,lever_chain,
 integrate_force_travel,validate_pusher_path)

class PusherTests(unittest.TestCase):
    def test_lever_force_travel_screen(self):
        r=lever_stage(20,10,0.8,2,1,0.1)
        self.assertAlmostEqual(r["estimated_output_force_n"],3.2)
        self.assertAlmostEqual(r["estimated_output_travel_mm"],0.45)

    def test_efficiency_above_one_rejected(self):
        with self.assertRaises(PusherEngineeringError): lever_stage(20,10,1.1,2,1)

    def test_lost_motion_cannot_consume_travel(self):
        with self.assertRaises(PusherEngineeringError): lever_stage(20,10,0.8,2,1,1)

    def test_chain(self):
        r=lever_chain([{"input_arm_mm":20,"output_arm_mm":10,"efficiency":0.9},
          {"input_arm_mm":15,"output_arm_mm":5,"efficiency":0.8}])
        self.assertAlmostEqual(r["ideal_force_ratio"],6)
        self.assertAlmostEqual(r["actual_force_ratio_screen"],4.32)

    def test_force_travel_work(self):
        r=integrate_force_travel([{"travel_mm":0,"force_n":0},{"travel_mm":1,"force_n":2},
          {"travel_mm":2,"force_n":2}],"SYNTHETIC","fixture")
        self.assertAlmostEqual(r["quasi_static_work_j"],0.003)

    def test_nonmonotonic_samples_rejected(self):
        with self.assertRaises(PusherEngineeringError):
            integrate_force_travel([{"travel_mm":1,"force_n":1},{"travel_mm":1,"force_n":2}],"S","R")

    def test_geometry_path(self):
        r=validate_pusher_path({"path_id":"P","source_member_id":"case_pusher","destination_member_id":"control",
          "evidence_id":"SYNTHETIC","source_revision":"fixture","stages":[{"stage_id":"L1",
          "pivot_reference":"TBD","input_contact_reference":"TBD","output_contact_reference":"TBD",
          "input_arm_mm":12,"output_arm_mm":8,"evidence_id":"SYNTHETIC","source_revision":"fixture"}]})
        self.assertFalse(r["physical_path_verified"])

if __name__=="__main__": unittest.main()
