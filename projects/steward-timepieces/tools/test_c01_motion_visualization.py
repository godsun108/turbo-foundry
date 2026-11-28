"""Synthetic WP-60 validation tests; fixtures are not C-01 design data."""
import unittest
from c01_motion_visualization import MotionVisualizationError, validate_candidate, validate_visualization_package

def component(cid):
    return {"component_id":cid,"role":"synthetic_envelope","drawing_ref":"TEST-DWG",
            "evidence_id":"SYNTHETIC","source_revision":"fixture-r1","status":"candidate",
            "geometry":{"type":"cylinder","parameters":{"radius_mm":1.0,"height_mm":2.0}}}

def frame(fid,state,t,x):
    return {"frame_id":fid,"state":state,"time_s":t,"evidence_id":"SYNTHETIC",
            "source_revision":"fixture-r1",
            "poses":[{"component_id":"control","x_mm":x,"y_mm":0,"angle_deg":0,
                      "z_min_mm":0,"z_max_mm":1}]}

def candidate(cid):
    return {"candidate_id":cid,"configuration_revision":cid+"-r1",
            "requirements_revision":"REQ-r1","datum_revision":"DATUM-r1",
            "interface_baseline_revision":"IF-r1","evidence_id":"SYNTHETIC",
            "source_revision":"fixture-r1","time_unit":"s","length_unit":"mm",
            "components":[component("control")],
            "frames":[frame("f0","stopped_zero",0,0),frame("f1","running",1,1),
                      frame("f2","stopped_retained",2,1.5),frame("f3","resetting",3,0.5),
                      frame("f4","stopped_zero",4,0)]}

def package():
    return {"package_id":"SYNTHETIC","revision":"r1","evidence_id":"SYNTHETIC",
            "source_revision":"fixture-r1","owner":"test",
            "common_baseline":{"requirements_revision":"REQ-r1","datum_revision":"DATUM-r1",
                               "interface_baseline_revision":"IF-r1"},
            "candidates":{"CW":candidate("CW"),"CL":candidate("CL")}}

class TestWP60(unittest.TestCase):
    def test_candidate_frames(self):
        r=validate_candidate(candidate("CW"))
        self.assertEqual(r["frame_count"],5)
        self.assertFalse(r["motion_solved"])

    def test_two_candidates_common_baseline(self):
        r=validate_visualization_package(package())
        self.assertTrue(r["common_baseline_match"])
        self.assertFalse(r["architecture_selected"])

    def test_missing_state_rejected(self):
        c=candidate("CW"); c["frames"]=[f for f in c["frames"] if f["state"]!="running"]
        with self.assertRaises(MotionVisualizationError): validate_candidate(c)

    def test_missing_component_pose_rejected(self):
        c=candidate("CW"); c["frames"][1]["poses"]=[]
        with self.assertRaises(MotionVisualizationError): validate_candidate(c)

    def test_duplicate_pose_rejected(self):
        c=candidate("CW"); c["frames"][1]["poses"].append(c["frames"][1]["poses"][0])
        with self.assertRaises(MotionVisualizationError): validate_candidate(c)

    def test_non_monotonic_time_rejected(self):
        c=candidate("CW"); c["frames"][2]["time_s"]=0.5
        with self.assertRaises(MotionVisualizationError): validate_candidate(c)

    def test_reset_order_rejected(self):
        c=candidate("CW"); c["frames"][3]["state"]="running"
        with self.assertRaises(MotionVisualizationError): validate_candidate(c)

    def test_bad_geometry_rejected(self):
        c=candidate("CW"); c["components"][0]["geometry"]["parameters"]["radius_mm"]=0
        with self.assertRaises(MotionVisualizationError): validate_candidate(c)

    def test_baseline_mismatch_rejected(self):
        p=package(); p["candidates"]["CL"]["datum_revision"]="other"
        with self.assertRaises(MotionVisualizationError): validate_visualization_package(p)

    def test_duplicate_frame_id_rejected(self):
        c=candidate("CL"); c["frames"][1]["frame_id"]="f0"
        with self.assertRaises(MotionVisualizationError): validate_candidate(c)

if __name__ == "__main__":
    unittest.main()
