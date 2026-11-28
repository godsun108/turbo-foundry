"""Synthetic WP-62 regression tests; all fixture values are not C-01 design data."""
import unittest
from c01_component_engineering import (
    ComponentEngineeringError, dimension_interval, journal_clearance,
    evaluate_engineering_package
)

ROLES=["drive_source","drive_coupling","clutch","central_seconds","minute_counter",
"hour_counter","stopped_retention","reset_hammer","heart_cam","pusher",
"running_reset_interlock","main_plate","bridge_support","bearing_support"]

def make_candidate(cid):
    control="column_wheel_control" if cid=="CW" else "cam_lever_control"
    roles=ROLES+[control]
    components=[]
    for i,role in enumerate(roles):
        components.append({
            "component_id":"cmp_"+str(i),"role":role,
            "family":"control" if "control" in role else "arbor",
            "candidate_scope":"shared" if role in ROLES else cid,
            "function":"Synthetic function statement",
            "geometry_definition":"Geometry intentionally unspecified in fixture",
            "geometry_status":"not_started","material_status":"tbd",
            "manufacturing_status":"not_started","drawing_ref":"SYNTHETIC",
            "evidence_id":"SYNTHETIC","source_revision":"fixture-r1",
            "dimensions":[],"interface_refs":[],"analysis_refs":[]
        })
    interfaces=[]
    for i in range(len(roles)-1):
        interfaces.append({"interface_id":"int_"+str(i),"interface_type":"synthetic_interface",
            "from_component_id":"cmp_"+str(i),"to_component_id":"cmp_"+str(i+1),
            "definition":"Synthetic connection","evidence_id":"SYNTHETIC",
            "source_revision":"fixture-r1"})
    return {"candidate_id":cid,"configuration_revision":cid+"-r1",
        "requirements_revision":"REQ-r1","datum_revision":"DATUM-r1",
        "interface_baseline_revision":"IF-r1","evidence_id":"SYNTHETIC",
        "source_revision":"fixture-r1","owner":"test",
        "components":components,"interfaces":interfaces,
        "open_decisions":[{"decision_id":"D-OPEN","topic":"architecture",
            "status":"open","evidence_id":"SYNTHETIC"}]}

def packet():
    return {"package_id":"SYNTHETIC-WP62","revision":"r1","evidence_id":"SYNTHETIC",
        "source_revision":"fixture-r1","owner":"test",
        "common_baseline":{"requirements_revision":"REQ-r1","datum_revision":"DATUM-r1",
            "interface_baseline_revision":"IF-r1"},
        "candidates":{"CW":make_candidate("CW"),"CL":make_candidate("CL")}}

class TestWP62(unittest.TestCase):
    def test_both_candidates_complete_role_register(self):
        r=evaluate_engineering_package(packet())
        self.assertEqual(set(r["candidate_results"]),{"CW","CL"})
        self.assertFalse(r["architecture_selected"])

    def test_missing_role_rejected(self):
        p=packet()
        p["candidates"]["CW"]["components"].pop()
        with self.assertRaises(ComponentEngineeringError): evaluate_engineering_package(p)

    def test_candidate_scope_rejected(self):
        p=packet()
        p["candidates"]["CW"]["components"][0]["candidate_scope"]="CL"
        with self.assertRaises(ComponentEngineeringError): evaluate_engineering_package(p)

    def test_duplicate_component_id_rejected(self):
        p=packet()
        p["candidates"]["CL"]["components"][1]["component_id"]="cmp_0"
        with self.assertRaises(ComponentEngineeringError): evaluate_engineering_package(p)

    def test_interface_endpoint_rejected(self):
        p=packet()
        p["candidates"]["CW"]["interfaces"][0]["to_component_id"]="missing"
        with self.assertRaises(ComponentEngineeringError): evaluate_engineering_package(p)

    def test_dimension_interval(self):
        r=dimension_interval(2.0,0.1,0.2,True)
        self.assertAlmostEqual(r["minimum"],1.9)
        self.assertAlmostEqual(r["maximum"],2.2)

    def test_positive_dimension_crossing_zero_rejected(self):
        with self.assertRaises(ComponentEngineeringError):
            dimension_interval(0.1,0.2,0.0,True)

    def test_journal_clearance_screen(self):
        r=journal_clearance(shaft_min_mm=0.99,shaft_max_mm=1.00,
            bore_min_mm=1.01,bore_max_mm=1.02,evidence_id="SYNTHETIC",
            source_revision="fixture-r1")
        self.assertAlmostEqual(r["minimum_diametral_clearance_mm"],0.01)
        self.assertAlmostEqual(r["maximum_diametral_clearance_mm"],0.03)
        self.assertFalse(r["physical_fit_certified"])

    def test_inverted_size_limits_rejected(self):
        with self.assertRaises(ComponentEngineeringError):
            journal_clearance(shaft_min_mm=1.1,shaft_max_mm=1.0,
                bore_min_mm=1.0,bore_max_mm=1.1,evidence_id="SYNTHETIC",
                source_revision="fixture-r1")

if __name__ == "__main__":
    unittest.main()
