"""Synthetic regression tests for WP-59; fixtures are not C-01 design data."""
import unittest
from c01_control_cad_assembly import (
    AssemblyDefinitionError, evaluate_candidate, evaluate_assembly_set,
    generate_assembly_scad, validate_mates
)

def component(cid, x=0.0, status="candidate", parent=None):
    return {
        "component_id": cid, "role": "synthetic_envelope",
        "geometry": {"type": "cylinder", "parameters": {"radius_mm": 1.0, "height_mm": 2.0}},
        "pose": {"translation_mm": {"x": x, "y": 0, "z": 0},
                 "rotation_deg": {"x": 0, "y": 0, "z": 0}},
        "parent_id": parent, "status": status, "drawing_ref": "TEST-DWG",
        "evidence_id": "SYNTHETIC-TEST", "source_revision": "fixture-r1"
    }

def candidate(cid):
    return {
        "candidate_id": cid, "configuration_revision": cid+"-r1",
        "requirements_revision": "REQ-r1", "datum_revision": "DATUM-r1",
        "interface_baseline_revision": "IF-r1", "evidence_id": "SYNTHETIC-TEST",
        "source_revision": "fixture-r1", "owner": "test",
        "components": [component(cid+"_base"), component(cid+"_lever", 3.0, parent=cid+"_base")],
        "mates": [{
            "mate_id": cid+"_distance", "type": "fixed_distance",
            "component_a": cid+"_base", "component_b": cid+"_lever",
            "target_distance_mm": 3.0, "tolerance_mm": 0.01,
            "definition": "synthetic test relation", "evidence_id": "SYNTHETIC-TEST",
            "source_revision": "fixture-r1"
        }]
    }

class TestWP59(unittest.TestCase):
    def test_candidate_and_mate(self):
        result = evaluate_candidate(candidate("CW"))
        self.assertEqual(result["component_count"], 2)
        self.assertTrue(result["all_numeric_mates_within_tolerance"])
        self.assertFalse(result["physical_fit_certified"])

    def test_both_candidate_baseline(self):
        packet = {"assembly_set_id":"SYNTHETIC", "revision":"r1",
                  "evidence_id":"SYNTHETIC-TEST", "source_revision":"fixture-r1", "owner":"test",
                  "common_baseline":{"requirements_revision":"REQ-r1","datum_revision":"DATUM-r1",
                                     "interface_baseline_revision":"IF-r1"},
                  "candidates":{"CW":candidate("CW"),"CL":candidate("CL")}}
        result = evaluate_assembly_set(packet)
        self.assertTrue(result["common_baseline_match"])
        self.assertFalse(result["architecture_selected"])

    def test_scad_contains_explicit_parts(self):
        src = generate_assembly_scad(candidate("CL"))
        self.assertIn("part_CL_base();", src)
        self.assertIn("SYNTHETIC-TEST", src)

    def test_unknown_parent_rejected(self):
        c = candidate("CW")
        c["components"][1]["parent_id"] = "missing"
        with self.assertRaises(AssemblyDefinitionError):
            evaluate_candidate(c)

    def test_parent_cycle_rejected(self):
        c = candidate("CW")
        c["components"][0]["parent_id"] = "CW_lever"
        with self.assertRaises(AssemblyDefinitionError):
            evaluate_candidate(c)

    def test_duplicate_component_rejected(self):
        c = candidate("CW")
        c["components"].append(component("CW_base"))
        with self.assertRaises(AssemblyDefinitionError):
            evaluate_candidate(c)

    def test_bad_mate_endpoint_rejected(self):
        c = candidate("CW")
        c["mates"][0]["component_b"] = "absent"
        with self.assertRaises(AssemblyDefinitionError):
            evaluate_candidate(c)

    def test_coaxial_screen(self):
        a, b = component("a"), component("b")
        from c01_control_cad_assembly import validate_components
        comps = validate_components([a,b])
        mate = {"mate_id":"axis", "type":"coaxial", "component_a":"a","component_b":"b",
                "angular_tolerance_deg":0.001,"offset_tolerance_mm":0.001,"definition":"test","evidence_id":"SYNTHETIC",
                "source_revision":"r1"}
        self.assertTrue(validate_mates([mate], comps)[0]["within_tolerance"])

    def test_planar_and_angular_screens(self):
        from c01_control_cad_assembly import validate_components
        comps = validate_components([component("a"), component("b")])
        mates = [
            {"mate_id":"plane","type":"planar","component_a":"a","component_b":"b",
             "tolerance_mm":0.01,"definition":"test","evidence_id":"SYNTHETIC","source_revision":"r1"},
            {"mate_id":"angle","type":"angular","component_a":"a","component_b":"b",
             "target_angle_deg":0,"tolerance_deg":0.01,"definition":"test",
             "evidence_id":"SYNTHETIC","source_revision":"r1"}
        ]
        self.assertTrue(all(x["within_tolerance"] for x in validate_mates(mates, comps)))

    def test_contact_is_reference_only(self):
        from c01_control_cad_assembly import validate_components
        comps = validate_components([component("a"), component("b")])
        m = {"mate_id":"contact","type":"contact_reference","component_a":"a","component_b":"b",
             "contact_feature_a":"face_a","contact_feature_b":"face_b","definition":"reference",
             "evidence_id":"SYNTHETIC","source_revision":"r1"}
        r = validate_mates([m], comps)[0]
        self.assertFalse(r["contact_geometry_verified"])
        self.assertIsNone(r["within_tolerance"])

    def test_invalid_geometry_rejected(self):
        c = candidate("CW")
        c["components"][0]["geometry"]["parameters"]["radius_mm"] = 0
        with self.assertRaises(AssemblyDefinitionError):
            evaluate_candidate(c)

    def test_candidate_baseline_mismatch_rejected(self):
        c = candidate("CL")
        c["datum_revision"] = "different"
        with self.assertRaises(AssemblyDefinitionError):
            evaluate_assembly_set({"assembly_set_id":"S", "revision":"r1",
                "evidence_id":"e","source_revision":"s","owner":"o",
                "common_baseline":{"requirements_revision":"REQ-r1","datum_revision":"DATUM-r1",
                                   "interface_baseline_revision":"IF-r1"},
                "candidates":{"CW":candidate("CW"),"CL":c}})

if __name__ == "__main__":
    unittest.main()
