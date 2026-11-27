import unittest
from c01_gear_train_optimization import OptimizationInputError, optimize_train

class GearTrainOptimizationTests(unittest.TestCase):
    def base(self):
        return {"candidate_id":"WP39-SYN","evidence_id":"SYNTHETIC","source_revision":"fixture-only",
          "overall_target_ratio":"2","max_overall_fractional_error":"0.05","max_candidates":10,
          "gears":[
            {"gear_id":"G1","arbor_id":"A1","module_mm":0.5,"pressure_angle_deg":20,"addendum_coefficient":1,"dedendum_coefficient":1.25,"profile_shift":0,"evidence_id":"SYN","source_revision":"fixture"},
            {"gear_id":"G2","arbor_id":"A2","module_mm":0.5,"pressure_angle_deg":20,"addendum_coefficient":1,"dedendum_coefficient":1.25,"profile_shift":0,"evidence_id":"SYN","source_revision":"fixture"}],
          "ordered_meshes":[{"mesh_id":"M1","driver_gear_id":"G1","driven_gear_id":"G2","min_teeth":10,"max_teeth":40,
             "min_stage_ratio":"1.5","max_stage_ratio":"2.5","target_ratio":"2","max_fractional_error":"0.05",
             "center_distance_mm":15,"xy_center_distance_mm":15,"center_distance_tolerance_mm":0.01,"min_contact_ratio":1.0}]}

    def test_returns_ranked_candidate_without_selecting_design(self):
        r=optimize_train(self.base())
        self.assertGreater(r["candidate_count"],0)
        self.assertFalse(r["design_selected"])
        self.assertFalse(r["architecture_frozen"])
        self.assertEqual(r["returned_candidates"][0]["overall_ratio"],"2")

    def test_shared_gear_tooth_consistency(self):
        d=self.base()
        d["gears"].append({"gear_id":"G3","arbor_id":"A3","module_mm":.5,"pressure_angle_deg":20,
          "addendum_coefficient":1,"dedendum_coefficient":1.25,"profile_shift":0,"evidence_id":"SYN","source_revision":"fixture"})
        d["ordered_meshes"].append({"mesh_id":"M2","driver_gear_id":"G2","driven_gear_id":"G3","min_teeth":10,
          "max_teeth":40,"min_stage_ratio":"1","max_stage_ratio":"3","target_ratio":"1","max_fractional_error":"0.05",
          "center_distance_mm":15,"xy_center_distance_mm":15,"center_distance_tolerance_mm":.01,"min_contact_ratio":1})
        r=optimize_train(d)
        for c in r["returned_candidates"]:
            self.assertEqual(c["tooth_assignments"]["G2"],c["mesh_schedule"][0]["driven_teeth"])
            self.assertEqual(c["tooth_assignments"]["G2"],c["mesh_schedule"][1]["driver_teeth"])

    def test_missing_geometry_is_not_passed(self):
        d=self.base()
        del d["ordered_meshes"][0]["xy_center_distance_mm"]
        r=optimize_train(d)
        self.assertFalse(r["returned_candidates"][0]["all_declared_screening_constraints_pass"])

    def test_incompatible_module_rejected(self):
        d=self.base(); d["gears"][1]["module_mm"]=.6
        with self.assertRaises(OptimizationInputError): optimize_train(d)

    def test_incompatible_pressure_angle_rejected(self):
        d=self.base(); d["gears"][1]["pressure_angle_deg"]=25
        with self.assertRaises(OptimizationInputError): optimize_train(d)

    def test_invalid_provenance_rejected(self):
        d=self.base(); d["gears"][0]["evidence_id"]=""
        with self.assertRaises(OptimizationInputError): optimize_train(d)

    def test_candidate_limit_is_enforced(self):
        d=self.base(); d["max_candidates"]=1
        r=optimize_train(d)
        self.assertLessEqual(len(r["returned_candidates"]),1)

if __name__=="__main__": unittest.main()
