import unittest
from c01_chrono_control import (ControlDesignError, validate_control_definition,
 validate_state_table, validate_running_reset_interlock, compare_candidates, evaluate_control_review)

class ControlTests(unittest.TestCase):
    def definition(self,cid,kind):
        names=["pusher","state_element","clutch_lever","retention_lever","reset_lever","interlock","return_spring"]
        members=[{"member_id":n,"function":n,"evidence_id":"SYNTHETIC","source_revision":"fixture"} for n in names]
        types=["pusher_input","index_or_state_retention","clutch_command","stopped_retention_command",
          "reset_hammer_command","running_reset_interlock","return_or_reset"]
        interfaces=[{"interface_id":t,"interface_type":t,"from_member_id":members[0]["member_id"],
          "to_member_id":members[1]["member_id"],"definition":"synthetic interface","evidence_id":"SYNTHETIC",
          "source_revision":"fixture"} for t in types]
        return {"candidate_id":cid,"control_type":kind,"evidence_id":"SYNTHETIC","source_revision":"fixture",
          "status":"concept","members":members,"interfaces":interfaces}

    def test_column_wheel_definition(self):
        self.assertEqual(validate_control_definition(self.definition("CW","column_wheel"))["member_count"],7)

    def test_cam_lever_definition(self):
        self.assertEqual(validate_control_definition(self.definition("CL","cam_lever"))["control_type"],"cam_lever")

    def test_missing_control_interface_rejected(self):
        d=self.definition("CW","column_wheel"); d["interfaces"].pop()
        with self.assertRaises(ControlDesignError): validate_control_definition(d)

    def test_candidate_type_mismatch_rejected(self):
        with self.assertRaises(ControlDesignError): validate_control_definition(self.definition("CW","cam_lever"))

    def test_state_table(self):
        rows=[
          {"command":"start","from_state":"stopped_zero","to_state":"running","actuation_sequence":"engage","completion_condition":"coupled","evidence_id":"SYNTHETIC"},
          {"command":"stop","from_state":"running","to_state":"stopped_retained","actuation_sequence":"disengage","completion_condition":"retained","evidence_id":"SYNTHETIC"},
          {"command":"resume","from_state":"stopped_retained","to_state":"running","actuation_sequence":"reengage","completion_condition":"running","evidence_id":"SYNTHETIC"},
          {"command":"reset","from_state":"stopped_retained","to_state":"stopped_zero","actuation_sequence":"hammer return","completion_condition":"zero","evidence_id":"SYNTHETIC"}]
        self.assertTrue(validate_state_table(rows)["state_table_valid"])

    def test_interlock_definition_does_not_claim_pass(self):
        r=validate_running_reset_interlock({"candidate_id":"CW","physical_interlock_type":"positive mechanical block",
          "blocking_member_id":"pawl","blocked_motion":"reset_hammer_contact","proof_test_id":"TBD",
          "evidence_id":"SYNTHETIC","source_revision":"fixture"})
        self.assertFalse(r["physical_interlock_pass"])

    def test_comparison_does_not_select_winner(self):
        r=compare_candidates(self.definition("CW","column_wheel"),self.definition("CL","cam_lever"))
        self.assertFalse(r["winner_selected"])

    def test_review_requires_all_measurements(self):
        d={"review_id":"R1","candidate_id":"CW","test_procedure_revision":"TBD",
          "configuration_revision":"TBD","measurement_boundary":"TBD","instrument_register_id":"TBD",
          "review_status":"draft","measurements":["actuation_force_travel"]}
        with self.assertRaises(ControlDesignError): evaluate_control_review(d)

if __name__=="__main__": unittest.main()
