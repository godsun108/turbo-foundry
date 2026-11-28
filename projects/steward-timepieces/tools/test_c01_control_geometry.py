"""Synthetic WP-58 geometry tests; values are test fixtures, not C-01 design data."""
import unittest
from c01_control_geometry import (
 GeometryDefinitionError, tolerance_interval, worst_case_stack, circle_clearance,
 lever_geometry, validate_profile, evaluate_geometry_set, REQUIRED_DATUMS
)

def datums():
 return [{"datum_id":d,"definition":"synthetic datum","realization_method":"fixture",
  "evidence_id":"SYNTHETIC","source_revision":"TEST","approval_reference":"TEST",
  "status":"proposed"} for d in sorted(REQUIRED_DATUMS)]
def features():
 roles=("control_axis","pusher_contact","clutch_command_contact","retention_contact",
 "reset_command_contact","reset_hammer_pivot","heart_cam_axis","interlock_contact",
 "return_element_anchor","structural_support_reference")
 return [{"feature_id":f"F{i}","component_id":"COMP","role":r,"datum_id":"M0",
  "position_mm":{"x":float(i),"y":0.0,"z":0.0},"orientation_deg":0.0,
  "definition":"synthetic","evidence_id":"SYNTHETIC","source_revision":"TEST",
  "status":"candidate"} for i,r in enumerate(roles)]
def package(cid):
 return {"candidate_id":cid,"package_id":"PKG-"+cid,"configuration_revision":"TEST",
  "requirements_revision":"REQ-TEST","evidence_id":"SYNTHETIC","source_revision":"TEST","owner":"TEST",
  "datums":datums(),"dimensions":[{"dimension_id":"D1","component_id":"COMP",
   "characteristic":"test dimension","unit":"mm","nominal":10.0,"lower_deviation":0.1,
   "upper_deviation":0.1,"deviation_convention":"bilateral_magnitudes","require_positive":True,
   "evidence_id":"SYNTHETIC","source_revision":"TEST","drawing_ref":"TBD","status":"candidate"}],
  "features":features(),"spring_interfaces":[{"interface_id":"SP1","component_id":"COMP",
   "anchor_feature_id":"F0","moving_feature_id":"F1","spring_type":"TBD",
   "endpoint_coordinates_mm":[{"x":0,"y":0,"z":0},{"x":1,"y":0,"z":0}],
   "evidence_id":"SYNTHETIC","source_revision":"TEST","drawing_ref":"TBD","status":"tbd"}],
  "profiles":[{"profile_id":"P1","component_id":"COMP","points_mm":[[0,0],[2,0],[2,1],[0,1]],
   "evidence_id":"SYNTHETIC","source_revision":"TEST","drawing_ref":"TBD"}],
  "clearance_pairs":[{"pair_id":"CP1","center_a_mm":[0,0],"radius_a_mm":1,
   "center_b_mm":[3,0],"radius_b_mm":1,"axial_overlap_reviewed":True,
   "axial_review_ref":"TEST","evidence_id":"SYNTHETIC","source_revision":"TEST"}],
  "movement_datum_revision":"DATUM-TEST","interface_baseline_revision":"IF-TEST"}
def packet():
 base={"requirements_revision":"REQ-TEST","movement_datum_revision":"DATUM-TEST",
  "interface_baseline_revision":"IF-TEST"}
 return {"geometry_set_id":"SET-TEST","revision":"A","evidence_id":"SYNTHETIC",
  "source_revision":"TEST","owner":"TEST","common_baseline":base,
  "candidates":{"column_wheel":package("column_wheel"),"cam_lever":package("cam_lever")}}

class WP58Tests(unittest.TestCase):
 def test_tolerance_interval(self): self.assertEqual(tolerance_interval(10,0.2,0.3),(9.8,10.3))
 def test_worst_case_stack(self):
  r=worst_case_stack([{"dimension_id":"A","nominal":10,"lower_deviation":0.1,"upper_deviation":0.1,"sign":1},
   {"dimension_id":"B","nominal":2,"lower_deviation":0.2,"upper_deviation":0.2,"sign":-1}],"SYNTHETIC","TEST")
  self.assertAlmostEqual(r["lower"],7.7); self.assertAlmostEqual(r["upper"],8.3)
 def test_circle_clearance(self): self.assertEqual(circle_clearance([0,0],1,[3,0],1)["nominal_signed_clearance_mm"],1)
 def test_circle_overlap(self): self.assertTrue(circle_clearance([0,0],2,[3,0],2)["overlap_or_contact"])
 def test_lever_geometry(self):
  r=lever_geometry(10,5,90,90,2)
  self.assertAlmostEqual(r["ideal_force_ratio"],2); self.assertAlmostEqual(r["ideal_output_travel_mm"],4)
 def test_zero_moment_arm_rejected(self):
  with self.assertRaises(GeometryDefinitionError): lever_geometry(10,5,0,90,2)
 def test_profile_valid(self): self.assertAlmostEqual(validate_profile([[0,0],[2,0],[2,1],[0,1]])["signed_area_mm2"],2)
 def test_self_intersecting_profile_rejected(self):
  with self.assertRaises(GeometryDefinitionError): validate_profile([[0,0],[2,2],[0,2],[2,0]])
 def test_both_candidates_required(self):
  p=packet(); p["candidates"].pop("cam_lever")
  with self.assertRaises(GeometryDefinitionError): evaluate_geometry_set(p)
 def test_datum_set_required(self):
  p=packet(); p["candidates"]["column_wheel"]["datums"].pop()
  with self.assertRaises(GeometryDefinitionError): evaluate_geometry_set(p)
 def test_feature_role_coverage(self):
  p=packet(); p["candidates"]["cam_lever"]["features"].pop()
  with self.assertRaises(GeometryDefinitionError): evaluate_geometry_set(p)
 def test_axial_review_required(self):
  p=packet(); p["candidates"]["cam_lever"]["clearance_pairs"][0]["axial_overlap_reviewed"]=False
  with self.assertRaises(GeometryDefinitionError): evaluate_geometry_set(p)
 def test_common_baseline_mismatch(self):
  p=packet(); p["candidates"]["cam_lever"]["movement_datum_revision"]="OTHER"
  with self.assertRaises(GeometryDefinitionError): evaluate_geometry_set(p)
 def test_geometry_never_certifies_or_releases(self):
  r=evaluate_geometry_set(packet())
  self.assertTrue(r["both_geometry_records_valid"])
  self.assertFalse(r["architecture_selected"])
  self.assertFalse(r["design_frozen"])
  self.assertFalse(r["manufacturing_release_authorized"])
 def test_unapproved_datums_remain_unapproved(self):
  r=evaluate_geometry_set(packet())
  self.assertFalse(r["candidate_results"]["column_wheel"]["all_datums_approved"])

if __name__=="__main__": unittest.main()
