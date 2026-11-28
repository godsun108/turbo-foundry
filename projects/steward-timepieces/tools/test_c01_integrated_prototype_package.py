"""Synthetic WP-57 package tests; no physical C-01 data."""
import unittest
from c01_integrated_prototype_package import (
 PrototypePackageError, REQUIRED_GATES, evaluate_integrated_package,
 validate_candidate_package
)

def candidate(cid,base):
 roles={"pusher_input","control_state_indexing","clutch_command",
 "stopped_retention_command","reset_hammer_command","running_reset_interlock",
 "return_or_reset","reset_hammer","heart_cam","running_reset_interlock",
 "pusher_input_member","return_element","structural_support"}
 roles |= {"column_wheel_indexing","column_wheel_jumper"} if cid=="column_wheel" else {"cam_profile_following","cam_lever_state_retention"}
 # role list unique
 components=[{"component_id":f"{cid}-C{i}","role":r,"description":"synthetic fixture",
  "part_or_document_ref":"TBD","revision":"TEST","configuration_status":"tbd",
  "geometry_status":"not_defined","evidence_id":"SYNTHETIC","source_revision":"TEST"} for i,r in enumerate(sorted(roles))]
 ids=[x["component_id"] for x in components]
 interfaces=[]
 for i,typ in enumerate(sorted({"pusher_input","control_state_indexing","clutch_command",
 "stopped_retention_command","reset_hammer_command","running_reset_interlock","return_or_reset"})):
  interfaces.append({"interface_id":f"{cid}-IF{i}","interface_type":typ,
   "from_component_id":ids[i],"to_component_id":ids[(i+1)%len(ids)],
   "control_document_ref":"TBD","revision":"TEST","evidence_id":"SYNTHETIC","source_revision":"TEST"})
 bom=[{"item_id":f"{cid}-B{i}","component_id":x["component_id"],"description":"synthetic",
  "quantity":1,"unit":"each","part_or_document_ref":"TBD","revision":"TEST",
  "make_buy_status":"engineering_placeholder","configuration_status":"tbd",
  "source_evidence_id":"SYNTHETIC"} for i,x in enumerate(components)]
 drawings=[{"drawing_id":f"{cid}-D{i}","drawing_type":t,"title":"planned",
  "revision":"TEST","status":"planned","evidence_id":"SYNTHETIC","source_revision":"TEST"}
  for i,t in enumerate(("assembly","component","interface_control","inspection"))]
 steps=[{"step_id":f"{cid}-S1","sequence":1,"operation":"planned assembly step",
  "component_ids":[ids[0]],"work_instruction_ref":"TBD","revision":"TEST",
  "hold_point":True,"evidence_id":"SYNTHETIC","source_revision":"TEST"}]
 inspections=[{"characteristic_id":f"{cid}-I{i}","component_id":ids[i],
  "characteristic":"TBD","method_ref":"TBD","acceptance_reference":"TBD",
  "instrument_or_gauge_ref":"TBD","evidence_id":"SYNTHETIC","source_revision":"TEST",
  "status":"planned"} for i in range(2)]
 families=("functional_state_sequence","pusher_force_travel","partial_actuation",
 "reset_zero_repeatability","running_reset_interlock","retention_behavior",
 "wear_and_serviceability","timekeeping_and_energy_impact")
 verification=[{"test_id":f"{cid}-T{i}","test_family":f,"procedure_ref":"TBD",
  "procedure_revision":"TEST","acceptance_reference":"TBD","evidence_id":"SYNTHETIC",
  "source_revision":"TEST","status":"planned"} for i,f in enumerate(families)]
 gates=[{"gate_id":g,"disposition":"open","evidence_id":"SYNTHETIC",
  "source_revision":"TEST","reviewer":"TEST-REVIEWER"} for g in sorted(REQUIRED_GATES)]
 return {"candidate_id":cid,"package_id":f"PKG-{cid}","configuration_revision":"TEST-REV",
  "article_id":f"ARTICLE-{cid}","requirements_revision":base["requirements_revision"],
  "architecture_candidate_id":cid,"evidence_id":"SYNTHETIC","source_revision":"TEST",
  "responsible_engineer":"TEST","shared_interface_baseline_id":base["shared_interface_baseline_id"],
  "common_fixture_revision":base["common_fixture_revision"],"physical_article_status":"not_built",
  "components":components,"bom":bom,"interfaces":interfaces,"drawings":drawings,
  "assembly_steps":steps,"inspection":inspections,"verification":verification,"gates":gates}

def packet():
 base={"requirements_revision":"REQ-TEST","shared_interface_baseline_id":"IF-TEST",
  "common_fixture_revision":"FIX-TEST","common_test_protocol_revision":"PROTO-TEST",
  "movement_interface_revision":"MOV-TEST"}
 return {"package_set_id":"SET-TEST","package_set_revision":"A","evidence_id":"SYNTHETIC",
  "source_revision":"TEST","owner":"TEST","common_baseline":base,
  "candidate_packages":{cid:candidate(cid,base) for cid in ("column_wheel","cam_lever")}}

class WP57Tests(unittest.TestCase):
 def test_both_candidate_packages_required(self):
  p=packet(); p["candidate_packages"].pop("cam_lever")
  with self.assertRaises(PrototypePackageError): evaluate_integrated_package(p)
 def test_missing_candidate_specific_role_rejected(self):
  p=packet(); p["candidate_packages"]["column_wheel"]["components"]=[x for x in p["candidate_packages"]["column_wheel"]["components"] if x["role"]!="column_wheel_indexing"]
  with self.assertRaises(PrototypePackageError): evaluate_integrated_package(p)
 def test_bom_component_mapping_required(self):
  p=packet(); p["candidate_packages"]["cam_lever"]["bom"][0]["component_id"]="UNKNOWN"
  with self.assertRaises(PrototypePackageError): evaluate_integrated_package(p)
 def test_shared_baseline_mismatch_rejected(self):
  p=packet(); p["candidate_packages"]["cam_lever"]["common_fixture_revision"]="OTHER"
  with self.assertRaises(PrototypePackageError): evaluate_integrated_package(p)
 def test_missing_interface_function_rejected(self):
  p=packet(); p["candidate_packages"]["cam_lever"]["interfaces"].pop()
  with self.assertRaises(PrototypePackageError): evaluate_integrated_package(p)
 def test_drawing_types_required(self):
  p=packet(); p["candidate_packages"]["column_wheel"]["drawings"].pop()
  with self.assertRaises(PrototypePackageError): evaluate_integrated_package(p)
 def test_assembly_steps_require_valid_component(self):
  p=packet(); p["candidate_packages"]["cam_lever"]["assembly_steps"][0]["component_ids"]=["NOPE"]
  with self.assertRaises(PrototypePackageError): evaluate_integrated_package(p)
 def test_verification_family_coverage(self):
  p=packet(); p["candidate_packages"]["cam_lever"]["verification"].pop()
  with self.assertRaises(PrototypePackageError): evaluate_integrated_package(p)
 def test_all_release_gates_must_exist(self):
  p=packet(); p["candidate_packages"]["cam_lever"]["gates"].pop()
  with self.assertRaises(PrototypePackageError): evaluate_integrated_package(p)
 def test_open_gates_prevent_release_readiness(self):
  r=evaluate_integrated_package(packet())
  self.assertEqual(r["next_status"],"ENGINEERING_DEFINITION_INCOMPLETE")
  self.assertFalse(r["physical_build_authorized"])
 def test_passing_gates_only_make_eligible_for_review(self):
  p=packet()
  for pkg in p["candidate_packages"].values():
   for gate in pkg["gates"]: gate["disposition"]="pass"
  r=evaluate_integrated_package(p)
  self.assertEqual(r["next_status"],"ELIGIBLE_FOR_SEPARATE_RELEASE_REVIEW")
  self.assertFalse(r["physical_build_authorized"])
  self.assertFalse(r["physical_test_authorized"])
  self.assertFalse(r["manufacturing_release_authorized"])
 def test_not_applicable_requires_approval(self):
  p=packet(); g=p["candidate_packages"]["cam_lever"]["gates"][0]
  g["disposition"]="not_applicable"
  with self.assertRaises(PrototypePackageError): evaluate_integrated_package(p)
 def test_duplicate_component_id_rejected(self):
  p=packet(); c=p["candidate_packages"]["column_wheel"]["components"]
  c[1]["component_id"]=c[0]["component_id"]
  with self.assertRaises(PrototypePackageError): evaluate_integrated_package(p)
 def test_candidate_specific_roles_stay_distinct(self):
  p=packet()
  r=evaluate_integrated_package(p)
  self.assertFalse(r["cw_cl_architecture_selected"])
  self.assertFalse(r["clutch_architecture_selected"])

if __name__=="__main__": unittest.main()
