import unittest
from c01_physical_layout import LayoutInputError, validate_layout, evaluate_layout, generate_openscad

class PhysicalLayoutTests(unittest.TestCase):
    def base(self):
        return {"candidate_id":"WP40-SYNTHETIC","evidence_id":"TEST_ONLY","source_revision":"fixture",
          "components":[
            {"component_id":"A","role":"arbor envelope","xy_mm":[0,0],"envelope_radius_mm":1,"z_interval_mm":[0,1],"evidence_id":"SYN","source_revision":"fixture"},
            {"component_id":"B","role":"gear envelope","xy_mm":[10,0],"envelope_radius_mm":1,"z_interval_mm":[0,1],"evidence_id":"SYN","source_revision":"fixture"},
            {"component_id":"C","role":"upper bridge envelope","xy_mm":[0,0],"envelope_radius_mm":1,"z_interval_mm":[2,3],"evidence_id":"SYN","source_revision":"fixture"}],
          "gear_meshes":[{"mesh_id":"M1","component_a_id":"A","component_b_id":"B","module_mm":1,"teeth_a":10,"teeth_b":10,"center_distance_tolerance_mm":0.01,"evidence_id":"SYN","source_revision":"fixture"}],
          "supports":[{"support_id":"S1","component_id":"A","structural_member_id":"PLATE_FIXTURE","support_type":"synthetic support","evidence_id":"SYN","source_revision":"fixture"}],
          "trajectories":[{"component_id":"A","xy_samples_mm":[[0,0],[0.5,0]],"evidence_id":"SYN","source_revision":"fixture"},
                          {"component_id":"B","xy_samples_mm":[[10,0],[1,0]],"evidence_id":"SYN","source_revision":"fixture"}]}

    def test_layout_validates(self):
        self.assertEqual(validate_layout(self.base())["component_count"],3)

    def test_axial_non_overlap_excludes_static_xy_collision(self):
        r=evaluate_layout(self.base())
        pair=[x for x in r["static_clearance_screens"] if {x["component_a_id"],x["component_b_id"]}=={"A","C"}]
        self.assertEqual(pair,[])

    def test_static_clearance_flags_overlap(self):
        d=self.base(); d["components"][1]["xy_mm"]=[1,0]
        r=evaluate_layout(d)
        self.assertTrue(any(x["screen"]=="INTERFERENCE" for x in r["static_clearance_screens"]))

    def test_gear_center_distance(self):
        r=evaluate_layout(self.base())
        self.assertTrue(r["gear_mesh_screens"][0]["center_distance_pass"])

    def test_motion_sample_interference(self):
        r=evaluate_layout(self.base())
        self.assertTrue(any(x["screen"]=="INTERFERENCE" for x in r["motion_clearance_screens"]))

    def test_mismatched_trajectory_timebase_rejected(self):
        d=self.base(); d["trajectories"][1]["xy_samples_mm"]=[[3,0]]
        with self.assertRaises(LayoutInputError): validate_layout(d)

    def test_missing_provenance_rejected(self):
        d=self.base(); d["components"][0]["source_revision"]=""
        with self.assertRaises(LayoutInputError): validate_layout(d)

    def test_scad_source_contains_candidate_provenance(self):
        s=generate_openscad(self.base())
        self.assertIn("WP40-SYNTHETIC",s)
        self.assertIn("cylinder",s)

if __name__=="__main__": unittest.main()
