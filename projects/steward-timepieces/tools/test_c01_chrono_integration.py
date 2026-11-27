import unittest
from c01_chrono_integration import IntegrationInputError, validate_assembly, validate_transition, validate_sequence, integration_review

class ChronographIntegrationTests(unittest.TestCase):
    def base(self):
        roles=["drive_source","clutch","central_seconds","minute_counter","hour_counter",
          "stopped_retention","control","reset_hammer","heart_cam"]
        comps=[{"component_id":r,"role":r,"evidence_id":"SYNTHETIC","source_revision":"fixture"} for r in roles]
        kinds=["drive_coupling","seconds_output","minute_counter_drive","hour_counter_drive",
          "stopped_retention_control","clutch_control","reset_hammer_actuation","seconds_reset",
          "minute_counter_reset","hour_counter_reset","running_reset_interlock"]
        interfaces=[{"interface_id":k,"interface_type":k,"from_component_id":comps[0]["component_id"],
          "to_component_id":comps[1]["component_id"],"definition":"synthetic interface contract",
          "evidence_id":"SYNTHETIC","source_revision":"fixture"} for k in kinds]
        decisions=[{"decision_id":"D1","topic":"clutch topology","status":"open","evidence_id":"TBD"}]
        return {"assembly_id":"WP41-SYNTHETIC","evidence_id":"SYNTHETIC","source_revision":"fixture",
          "architecture_status":"candidate","components":comps,"interfaces":interfaces,"open_decisions":decisions}

    def test_complete_interface_register(self):
        r=validate_assembly(self.base())
        self.assertEqual(r["component_count"],9)
        self.assertEqual(r["interface_count"],11)

    def test_missing_role_rejected(self):
        d=self.base(); d["components"]=[c for c in d["components"] if c["role"]!="heart_cam"]
        with self.assertRaises(IntegrationInputError): validate_assembly(d)

    def test_missing_interface_rejected(self):
        d=self.base(); d["interfaces"].pop()
        with self.assertRaises(IntegrationInputError): validate_assembly(d)

    def test_running_reset_requires_interlock_evidence(self):
        with self.assertRaises(IntegrationInputError):
            validate_transition("running","reset","running")
        r=validate_transition("running","reset","running","physical-test-record-001")
        self.assertTrue(r["reset_blocked"])

    def test_reset_cannot_change_running_state(self):
        with self.assertRaises(IntegrationInputError):
            validate_transition("running","reset","stopped_zero","physical-test-record-001")

    def test_valid_operating_sequence(self):
        events=[{"command":"start","result":"running"},
          {"command":"stop","result":"stopped_retained"},
          {"command":"start","result":"running"},
          {"command":"stop","result":"stopped_retained"},
          {"command":"reset","result":"stopped_zero"}]
        r=validate_sequence(events)
        self.assertEqual(r["final_state"],"stopped_zero")
        self.assertFalse(r["physical_mechanism_verified"])

    def test_integration_does_not_authorize_release(self):
        r=integration_review(self.base())
        self.assertFalse(r["prototype_release_authorized"])
        self.assertFalse(r["design_frozen"])
        self.assertFalse(r["all_architecture_decisions_approved"])

    def test_duplicate_interface_rejected(self):
        d=self.base(); d["interfaces"][1]["interface_id"]=d["interfaces"][0]["interface_id"]
        with self.assertRaises(IntegrationInputError): validate_assembly(d)

if __name__=="__main__": unittest.main()
