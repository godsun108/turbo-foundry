"""Synthetic regression tests for WP-54; fixtures are not C-01 design data."""
import unittest
from c01_control_component_design import (
    ComponentDesignError, column_wheel_indexing, validate_profile,
    validate_component, validate_candidate_definition, validate_spring_curve,
    validate_interlock_definition, generate_openscad,
)

def component(cid, candidate, role, geometry="circle"):
    row = {"component_id":cid,"candidate_id":candidate,"role":role,
           "geometry_type":geometry,"unit":"mm","z_thickness_mm":0.2,
           "evidence_id":"SYNTHETIC-TEST-ONLY","source_revision":"TEST-FIXTURE"}
    if geometry == "circle": row["radius_mm"] = 1.0
    elif geometry == "annulus": row.update(outer_radius_mm=2.0,inner_radius_mm=1.0)
    else: row["points"] = [[0,0],[2,0],[1,1]]
    return row

def definition(candidate):
    roles = (["wheel_body","indexing_columns","pivot_or_bore","jumper_interface","reset_hammer","heart_cam","running_reset_interlock"]
             if candidate == "column_wheel" else
             ["cam_profile","follower","operating_lever","state_retention","reset_hammer","heart_cam","running_reset_interlock"])
    comps=[component(f"part_{i}",candidate,r,"polygon" if r in ("cam_profile","heart_cam") else "circle") for i,r in enumerate(roles)]
    types=["pusher_to_control","control_to_clutch","control_to_retention","control_to_reset","reset_hammer_to_heart","running_reset_block"]
    interfaces=[{"interface_id":f"if_{i}","interface_type":t,
                 "from_component_id":comps[0]["component_id"],"to_component_id":comps[-1]["component_id"],
                 "definition":"synthetic interface definition","evidence_id":"SYNTHETIC-TEST-ONLY",
                 "source_revision":"TEST-FIXTURE"} for i,t in enumerate(types)]
    return {"candidate_id":candidate,"configuration_revision":"TEST-CANDIDATE-REV",
            "evidence_id":"SYNTHETIC-TEST-ONLY","source_revision":"TEST-FIXTURE",
            "components":comps,"interfaces":interfaces}

class WP54Tests(unittest.TestCase):
    def test_column_wheel_pitch(self):
        r=column_wheel_indexing(8,2.0,0,"SYN","TEST")
        self.assertEqual(r["angular_pitch_deg"],45.0)
        self.assertGreater(r["adjacent_column_chord_mm"],0)
        self.assertFalse(r["architecture_selected"])

    def test_column_count_requires_integer(self):
        with self.assertRaises(ComponentDesignError): column_wheel_indexing(2.5,2,0,"S","R")

    def test_profile_valid(self):
        r=validate_profile([[0,0],[2,0],[1,1]],"SYN","TEST")
        self.assertEqual(r["point_count"],3)
        self.assertFalse(r["self_intersection_checked"])

    def test_profile_rejects_zero_area(self):
        with self.assertRaises(ComponentDesignError):
            validate_profile([[0,0],[1,0],[2,0]],"SYN","TEST")

    def test_component_annulus(self):
        self.assertTrue(validate_component(component("ring","cam_lever","follower","annulus"))["geometry_valid"])

    def test_annulus_rejects_bad_radii(self):
        c=component("ring","cam_lever","follower","annulus"); c["inner_radius_mm"]=2.0
        with self.assertRaises(ComponentDesignError): validate_component(c)

    def test_candidate_definitions_both_reviewable(self):
        self.assertTrue(validate_candidate_definition(definition("column_wheel"))["definition_complete_for_review"])
        self.assertTrue(validate_candidate_definition(definition("cam_lever"))["definition_complete_for_review"])

    def test_missing_role_rejected(self):
        d=definition("column_wheel"); d["components"].pop(0)
        with self.assertRaises(ComponentDesignError): validate_candidate_definition(d)

    def test_spring_curve_is_not_fitted(self):
        r=validate_spring_curve([{"displacement":0,"force":0},{"displacement":1,"force":2}],
                                "mm","N","SYN","TEST")
        self.assertFalse(r["spring_rate_fitted"])

    def test_spring_curve_rejects_duplicate_displacement(self):
        with self.assertRaises(ComponentDesignError):
            validate_spring_curve([{"displacement":0,"force":0},{"displacement":0,"force":1}],
                                  "mm","N","SYN","TEST")

    def test_interlock_not_physically_verified(self):
        r=validate_interlock_definition({"interlock_id":"IL1","blocked_member_id":"hammer",
            "blocking_member_id":"state_cam","blocked_state":"running","required_safe_state":"no hammer contact",
            "evidence_id":"SYN","source_revision":"TEST"})
        self.assertFalse(r["physical_interlock_verified"])

    def test_openscad_source(self):
        s=generate_openscad(definition("cam_lever"))
        self.assertIn("module part_0()",s)
        self.assertIn("not a manufacturing drawing",s)

    def test_duplicate_component_id_rejected(self):
        d=definition("cam_lever"); d["components"][1]["component_id"]=d["components"][0]["component_id"]
        with self.assertRaises(ComponentDesignError): validate_candidate_definition(d)

if __name__ == "__main__":
    unittest.main()
