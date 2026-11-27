import unittest
from c01_control_kinematics import (ControlKinematicsError, validate_candidate, validate_motion,
 evaluate_constraints, evaluate_clearance, validate_sequence, openscad_envelopes, review)

class WP44Tests(unittest.TestCase):
    def candidate(self,cid="CW",kind="column_wheel"):
        names=["pusher","indexer","clutch_lever","retention_lever","reset_lever","interlock","return"]
        members=[{"member_id":n,"function":n,"evidence_id":"SYNTHETIC","source_revision":"fixture"} for n in names]
        kinds=["pusher_input","index_or_state_retention","clutch_command","stopped_retention_command",
          "reset_hammer_command","running_reset_interlock","return_or_reset"]
        interfaces=[{"interface_id":k,"interface_type":k,"from_member_id":members[0]["member_id"],
          "to_member_id":members[1]["member_id"],"definition":"synthetic","evidence_id":"SYNTHETIC","source_revision":"fixture"} for k in kinds]
        return {"candidate_id":cid,"control_type":kind,"evidence_id":"SYNTHETIC","source_revision":"fixture",
          "status":"concept","members":members,"interfaces":interfaces}
    def motion(self):
        samples=[{"time_s":0.0},{"time_s":1.0},{"time_s":2.0}]
        def member(mid,xs,r=0.5):
            return {"member_id":mid,"role":"synthetic envelope","geometry_type":"circle","radius_mm":r,
              "evidence_id":"SYNTHETIC","source_revision":"fixture",
              "poses":[{"x_mm":x,"y_mm":0,"angle_deg":0,"z_min_mm":0,"z_max_mm":1} for x in xs]}
        return {"candidate_id":"CW","evidence_id":"SYNTHETIC","source_revision":"fixture",
          "time_unit":"s","length_unit":"mm","samples":samples,
          "members":[member("A",[0,1,2]),member("B",[3,4,5])],
          "constraints":[{"constraint_id":"L1","type":"fixed_point_distance","member_a":"A","member_b":"B",
            "a_local_x_mm":0,"a_local_y_mm":0,"b_local_x_mm":0,"b_local_y_mm":0,
            "target_distance_mm":3,"tolerance_mm":0.01,"evidence_id":"SYNTHETIC","source_revision":"fixture"}]}
    def test_candidate_contract(self): self.assertTrue(validate_candidate(self.candidate())["complete"])
    def test_candidate_type_mismatch(self):
        with self.assertRaises(ControlKinematicsError): validate_candidate(self.candidate("CW","cam_lever"))
    def test_motion_contract(self): self.assertEqual(validate_motion(self.motion())["sample_count"],3)
    def test_nonmonotonic_time_rejected(self):
        d=self.motion(); d["samples"][1]["time_s"]=0
        with self.assertRaises(ControlKinematicsError): validate_motion(d)
    def test_missing_pose_rejected(self):
        d=self.motion(); d["members"][0]["poses"].pop()
        with self.assertRaises(ControlKinematicsError): validate_motion(d)
    def test_fixed_distance_constraint_pass(self):
        r=evaluate_constraints(self.motion())
        self.assertTrue(r["all_constraints_screen_pass"])
    def test_constraint_deviation_detected(self):
        d=self.motion(); d["members"][1]["poses"][1]["x_mm"]=3.2
        self.assertFalse(evaluate_constraints(d)["all_constraints_screen_pass"])
    def test_sampled_clearance_detects_overlap(self):
        d=self.motion(); d["members"][1]["poses"][1]["x_mm"]=1.5
        self.assertTrue(evaluate_clearance(d)["pairs"][0]["overlap_detected"])
    def test_nonoverlapping_z_is_not_planar_collision(self):
        d=self.motion()
        for p in d["members"][1]["poses"]: p["z_min_mm"]=2; p["z_max_mm"]=3
        self.assertEqual(evaluate_clearance(d)["pairs"],[])
    def test_sequence_and_running_reset_block(self):
        events=[{"command":"start","result":"running"},
          {"command":"reset","result":"running","interlock_test_id":"TEST-001"},
          {"command":"stop","result":"stopped_retained"},{"command":"reset","result":"stopped_zero"}]
        self.assertTrue(validate_sequence(events)["logical_sequence_valid"])
    def test_running_reset_without_physical_test_rejected(self):
        with self.assertRaises(ControlKinematicsError):
            validate_sequence([{"command":"start","result":"running"},{"command":"reset","result":"running"}])
    def test_openscad_provenance_and_first_pose(self):
        s=openscad_envelopes(self.motion())
        self.assertIn("SYNTHETIC",s); self.assertIn("cylinder",s)
    def test_review_never_freezes_or_releases(self):
        events=[{"command":"start","result":"running"},{"command":"stop","result":"stopped_retained"},{"command":"reset","result":"stopped_zero"}]
        r=review(self.candidate(),self.motion(),events)
        self.assertFalse(r["design_frozen"]); self.assertFalse(r["prototype_release_authorized"])
    def test_duplicate_member_rejected(self):
        d=self.motion(); d["members"][1]["member_id"]="A"
        with self.assertRaises(ControlKinematicsError): validate_motion(d)

if __name__=="__main__": unittest.main()
