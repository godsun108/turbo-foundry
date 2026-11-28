"""Synthetic WP-55 regression tests; fixtures are not C-01 design data."""
import unittest
from c01_motion_contact_analysis import (
    MotionContactError, validate_motion_package, analyze_pair_contact,
    differentiate_motion, analyze_event_timing, lever_moment_screen,
    compare_motion_packages,
)

def package(candidate="column_wheel", revision="SYNTHETIC-REV"):
    times=[0.0,1.0,2.0]
    return {"candidate_id":candidate,"configuration_revision":revision,
      "time_unit":"s","length_unit":"mm","evidence_id":"SYNTHETIC-ONLY",
      "source_revision":"TEST-FIXTURE","samples":[{"time_s":t} for t in times],
      "bodies":[
       {"body_id":"wheel","role":"test body","geometry_type":"circle_envelope","radius_mm":1.0,
        "evidence_id":"SYNTHETIC-ONLY","source_revision":"TEST-FIXTURE",
        "poses":[{"x_mm":0.0,"y_mm":0.0,"angle_deg":0.0,"z_min_mm":0.0,"z_max_mm":1.0},
                 {"x_mm":0.0,"y_mm":0.0,"angle_deg":1.0,"z_min_mm":0.0,"z_max_mm":1.0},
                 {"x_mm":0.0,"y_mm":0.0,"angle_deg":2.0,"z_min_mm":0.0,"z_max_mm":1.0}]},
       {"body_id":"follower","role":"test body","geometry_type":"circle_envelope","radius_mm":1.0,
        "evidence_id":"SYNTHETIC-ONLY","source_revision":"TEST-FIXTURE",
        "poses":[{"x_mm":3.0,"y_mm":0.0,"angle_deg":0.0,"z_min_mm":0.0,"z_max_mm":1.0},
                 {"x_mm":2.0,"y_mm":0.0,"angle_deg":0.0,"z_min_mm":0.0,"z_max_mm":1.0},
                 {"x_mm":1.5,"y_mm":0.0,"angle_deg":0.0,"z_min_mm":0.0,"z_max_mm":1.0}]}
      ]}

class WP55Tests(unittest.TestCase):
    def test_validate_package(self):
        self.assertTrue(validate_motion_package(package())["validated"])

    def test_non_monotonic_time_rejected(self):
        p=package(); p["samples"][1]["time_s"]=0
        with self.assertRaises(MotionContactError): validate_motion_package(p)

    def test_contact_gap_and_penetration(self):
        r=analyze_pair_contact(package(),"wheel","follower",0.01)
        self.assertAlmostEqual(r["minimum_gap_mm"],-0.5)
        self.assertEqual(r["maximum_penetration_mm"],0.5)
        self.assertFalse(r["physical_contact_verified"])

    def test_axial_separation_excludes_contact(self):
        p=package()
        for body in p["bodies"]:
            for pose in body["poses"]:
                pose["z_min_mm"]=2.0; pose["z_max_mm"]=3.0
        r=analyze_pair_contact(p,"wheel","follower",0.01)
        self.assertIsNone(r["minimum_gap_mm"])

    def test_unknown_body_rejected(self):
        with self.assertRaises(MotionContactError): analyze_pair_contact(package(),"wheel","missing",0)

    def test_differentiate_translation(self):
        p=package()
        for i,pose in enumerate(p["bodies"][0]["poses"]):
            pose["x_mm"]=float(i)
        r=differentiate_motion(p,"wheel")
        self.assertAlmostEqual(r["samples"][1]["vx_mm_s"],1.0)
        self.assertFalse(r["dynamics_verified"])

    def test_event_order(self):
        r=analyze_event_timing([{"event":"pusher","time_s":0},{"event":"index","time_s":0.2},
                                {"event":"engage","time_s":0.5}],
                               ["pusher","index","engage"],"SYN","TEST")
        self.assertTrue(r["order_pass"])
        self.assertEqual(r["intervals_s"],[0.2,0.3])

    def test_event_order_failure(self):
        r=analyze_event_timing([{"event":"pusher","time_s":0.5},{"event":"index","time_s":0.2}],
                               ["pusher","index"],"SYN","TEST")
        self.assertFalse(r["order_pass"])

    def test_missing_event_rejected(self):
        with self.assertRaises(MotionContactError):
            analyze_event_timing([{"event":"start","time_s":0}],["start","lock"],"SYN","TEST")

    def test_lever_moment(self):
        r=lever_moment_screen([0,0],[2,0],[0,3],"SYN","TEST")
        self.assertEqual(r["moment_n_mm"],6.0)
        self.assertFalse(r["dynamic_equilibrium_verified"])

    def test_comparison_metadata_only(self):
        a=package("column_wheel"); b=package("cam_lever")
        r=compare_motion_packages(a,b)
        self.assertTrue(r["metadata_comparable"])
        self.assertFalse(r["physical_equivalence_proven"])

    def test_compare_revision_mismatch(self):
        a=package(); b=package("cam_lever","OTHER")
        self.assertFalse(compare_motion_packages(a,b)["metadata_comparable"])

if __name__ == "__main__":
    unittest.main()
