"""Synthetic WP-61 tests. Fixture geometry is software test data, not C-01 design."""
import unittest
from c01_integrated_chrono_assembly import (
    IntegratedChronographError, evaluate_integrated_package,
    generate_integrated_cad_sources
)

COMMON_ROLES = ["drive_source","drive_coupling","clutch","central_seconds",
 "minute_counter","hour_counter","stopped_retention","reset_hammer","heart_cam",
 "pusher","running_reset_interlock","main_plate","bridge_support","bearing_support"]

def make_candidate(cid):
    role = "column_wheel_control" if cid == "CW" else "cam_lever_control"
    components = []
    all_roles = COMMON_ROLES + [role]
    for i, r in enumerate(all_roles):
        components.append({
            "component_id": "part_"+str(i), "role": r,
            "geometry":{"type":"cylinder","parameters":{"radius_mm":1.0,"height_mm":1.0}},
            "pose":{"translation_mm":{"x":float(i),"y":0.0,"z":0.0},
                    "rotation_deg":{"x":0.0,"y":0.0,"z":0.0}},
            "parent_id":None,"status":"candidate","drawing_ref":"SYNTHETIC-DWG",
            "evidence_id":"SYNTHETIC","source_revision":"fixture-r1"
        })
    interfaces=[]
    types=sorted(["drive_coupling","seconds_output","minute_counter_drive","hour_counter_drive",
     "stopped_retention_control","clutch_control","reset_hammer_actuation","seconds_reset",
     "minute_counter_reset","hour_counter_reset","running_reset_interlock","pusher_input",
     "control_indexing","structural_support","bearing_support"])
    for i,t in enumerate(types):
        interfaces.append({"interface_id":"if_"+str(i),"interface_type":t,
            "from_component_id":"part_0","to_component_id":"part_1",
            "definition":"Synthetic interface only","evidence_id":"SYNTHETIC",
            "source_revision":"fixture-r1"})
    return {"candidate_id":cid,"configuration_revision":cid+"-r1",
        "requirements_revision":"REQ-r1","datum_revision":"DATUM-r1",
        "interface_baseline_revision":"IF-r1","evidence_id":"SYNTHETIC",
        "source_revision":"fixture-r1","owner":"test",
        "components":components,"mates":[],
        "interfaces":interfaces,
        "open_decisions":[{"decision_id":"D-OPEN","topic":"architecture",
                           "status":"open","evidence_id":"SYNTHETIC"}]}

def packet():
    return {"assembly_set_id":"SYNTHETIC-WP61","revision":"r1",
        "evidence_id":"SYNTHETIC","source_revision":"fixture-r1","owner":"test",
        "common_baseline":{"requirements_revision":"REQ-r1","datum_revision":"DATUM-r1",
                           "interface_baseline_revision":"IF-r1"},
        "candidates":{"CW":make_candidate("CW"),"CL":make_candidate("CL")}}

class TestWP61(unittest.TestCase):
    def test_both_candidates_validate(self):
        result=evaluate_integrated_package(packet())
        self.assertFalse(result["architecture_selected"])
        self.assertEqual(set(result["candidate_results"]),{"CW","CL"})

    def test_candidate_control_role_required(self):
        p=packet()
        p["candidates"]["CW"]["components"]=[c for c in p["candidates"]["CW"]["components"]
            if c["role"]!="column_wheel_control"]
        with self.assertRaises(IntegratedChronographError): evaluate_integrated_package(p)

    def test_required_interface_coverage(self):
        p=packet();p["candidates"]["CL"]["interfaces"].pop()
        with self.assertRaises(IntegratedChronographError): evaluate_integrated_package(p)

    def test_baseline_mismatch_rejected(self):
        p=packet();p["candidates"]["CL"]["datum_revision"]="other"
        with self.assertRaises(IntegratedChronographError): evaluate_integrated_package(p)

    def test_missing_open_decisions_rejected(self):
        p=packet();p["candidates"]["CW"]["open_decisions"]=[]
        with self.assertRaises(IntegratedChronographError): evaluate_integrated_package(p)

    def test_cad_sources_separate(self):
        result=generate_integrated_cad_sources(packet())
        self.assertIn("// Candidate: CW",result["cad_sources"]["CW"])
        self.assertIn("// Candidate: CL",result["cad_sources"]["CL"])
        self.assertFalse(result["rendered"])

    def test_synthetic_fixture_is_not_approved(self):
        result=evaluate_integrated_package(packet())
        self.assertTrue(all(r["wp59_geometry_and_mates_validated"] for r in result["candidate_results"].values()))
        self.assertFalse(result["physical_fit_certified"])

    def test_missing_structural_role_rejected(self):
        p=packet()
        p["candidates"]["CW"]["components"]=[c for c in p["candidates"]["CW"]["components"]
            if c["role"]!="bearing_support"]
        with self.assertRaises(IntegratedChronographError): evaluate_integrated_package(p)

if __name__ == "__main__":
    unittest.main()
