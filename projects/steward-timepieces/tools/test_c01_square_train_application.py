"""Synthetic regression fixtures only; not C-01 design data."""
import unittest
from c01_square_train_application import evaluate_square_going_train
E="synthetic_test_fixture"; R="TEST-ONLY"
def fixture():
    names=("barrel","center","third","fourth","escape")
    arbors=[{"id":n,"role":n,"evidence":E,"source_revision":R} for n in names]
    stages=[("barrel","center","a","b",60,20),("center","third","c","d",40,20),
            ("third","fourth","e","f",30,15),("fourth","escape","g","h",20,10)]
    gears=[]; meshes=[]
    for i,(a,b,g1,g2,z1,z2) in enumerate(stages,1):
        for gid,ar,z in ((g1,a,z1),(g2,b,z2)):
            gears.append({"id":gid,"arbor_id":ar,"teeth":z,"role":"synthetic",
                          "evidence":E,"source_revision":R})
        meshes.append({"id":f"m{i}","driver_gear_id":g1,"driven_gear_id":g2,
                       "mesh_type":"external","evidence":E,"source_revision":R})
    return {"candidate_id":"SYNTHETIC-ONLY","evidence":E,"source_revision":R,
            "arbors":arbors,"gears":gears,"meshes":meshes,"path_arbor_ids":list(names),
            "input_rpm":"1","target_output_period_seconds":60}
class Tests(unittest.TestCase):
    def test_exact_ratio(self):
        x=evaluate_square_going_train(fixture())
        self.assertEqual(x["kinematic_evaluation"]["signed_compound_speed_ratio"],"12")
        self.assertFalse(x["physical_feasibility_established"])
    def test_path_must_match(self):
        x=fixture(); x["path_arbor_ids"]=["barrel","center","fourth","escape"]
        with self.assertRaises(ValueError): evaluate_square_going_train(x)
    def test_explicit_speed_required(self):
        x=fixture(); del x["input_rpm"]
        with self.assertRaises(ValueError): evaluate_square_going_train(x)
    def test_provenance_consistency(self):
        x=fixture(); x["gears"][0]["source_revision"]="OTHER"
        with self.assertRaises(ValueError): evaluate_square_going_train(x)
    def test_no_tolerance_or_design_selection(self):
        x=evaluate_square_going_train(fixture())
        self.assertFalse(x["speed_tolerance_applied"]); self.assertFalse(x["design_selected"])
if __name__=="__main__": unittest.main()
