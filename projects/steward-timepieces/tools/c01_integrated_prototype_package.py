"""WP-57 integrated CW/CL prototype package completeness validator.

This is a controlled-record validator, not a CAD, fit, safety, or manufacturing
approval engine. It never authorizes build, inspection acceptance, or test.
"""
from __future__ import annotations

class PrototypePackageError(ValueError):
    pass

CANDIDATES={"column_wheel","cam_lever"}
COMMON_FUNCTIONS={
 "pusher_input","control_state_indexing","clutch_command",
 "stopped_retention_command","reset_hammer_command",
 "running_reset_interlock","return_or_reset"
}
CW_FUNCTIONS={"column_wheel_indexing","column_wheel_jumper"}
CL_FUNCTIONS={"cam_profile_following","cam_lever_state_retention"}
SHARED_COMPONENT_ROLES={
 "reset_hammer","heart_cam","running_reset_interlock",
 "pusher_input_member","return_element","structural_support"
}
REQUIRED_DRAWING_TYPES={"assembly","component","interface_control","inspection"}
REQUIRED_GATES={
 "requirements_baseline","candidate_architecture_approval","interface_control",
 "dimensioned_geometry_and_tolerances","bom_and_configuration_control",
 "assembly_and_lubrication_instructions","inspection_plan_and_acceptance",
 "fixture_and_metrology_qualification","physical_running_reset_interlock",
 "motion_contact_and_clearance_review","risk_and_failure_review",
 "independent_engineering_review"
}

def _text(v,label):
 if not isinstance(v,str) or not v.strip():
  raise PrototypePackageError(f"{label} is required")
 return v

def _unique(records,key,label):
 if not isinstance(records,list) or not records:
  raise PrototypePackageError(f"{label} must be a non-empty list")
 ids=[_text(r.get(key),f"{label}.{key}") for r in records]
 if len(ids)!=len(set(ids)):
  raise PrototypePackageError(f"{label} {key} values must be unique")
 return set(ids)

def validate_components(candidate_id, components):
 if candidate_id not in CANDIDATES: raise PrototypePackageError("unknown candidate")
 ids=_unique(components,"component_id","components")
 roles={c.get("role") for c in components}
 required=SHARED_COMPONENT_ROLES | COMMON_FUNCTIONS
 required |= CW_FUNCTIONS if candidate_id=="column_wheel" else CL_FUNCTIONS
 missing=required-roles
 if missing: raise PrototypePackageError(f"missing component roles: {sorted(missing)}")
 for c in components:
  for f in ("description","part_or_document_ref","revision","configuration_status","evidence_id","source_revision"):
   _text(c.get(f),f"component.{f}")
  if c.get("configuration_status") not in ("tbd","candidate","reviewed","approved"):
   raise PrototypePackageError("invalid component configuration_status")
  # Geometry may remain TBD, but cannot be implied as released.
  if c.get("geometry_status") not in ("not_defined","candidate","reviewed","approved"):
   raise PrototypePackageError("invalid geometry_status")
  if c.get("geometry_status")=="approved" and not c.get("drawing_ref"):
   raise PrototypePackageError("approved geometry requires drawing_ref")
 return {"component_count":len(ids),"roles_present":sorted(roles),"missing_roles":[]}

def validate_bom(bom, component_ids):
 _unique(bom,"item_id","bom")
 for row in bom:
  for f in ("description","unit","part_or_document_ref","revision","make_buy_status",
            "configuration_status","source_evidence_id"):
   _text(row.get(f),f"bom.{f}")
  q=row.get("quantity")
  if isinstance(q,bool) or not isinstance(q,int) or q<=0:
   raise PrototypePackageError("BOM quantity must be a positive integer")
  if row.get("make_buy_status") not in ("make","buy","engineering_placeholder","tbd"):
   raise PrototypePackageError("invalid make_buy_status")
  if row.get("configuration_status") not in ("tbd","candidate","reviewed","approved"):
   raise PrototypePackageError("invalid BOM configuration_status")
  if row.get("component_id") not in component_ids:
   raise PrototypePackageError("BOM row must map to a registered component_id")
 return {"bom_rows":len(bom),"component_coverage":len({r["component_id"] for r in bom})}

def validate_interfaces(interfaces, candidate_id):
 _unique(interfaces,"interface_id","interfaces")
 expected=COMMON_FUNCTIONS
 types={i.get("interface_type") for i in interfaces}
 missing=expected-types
 if missing: raise PrototypePackageError(f"missing functional interfaces: {sorted(missing)}")
 component_ids={i.get("from_component_id") for i in interfaces}|{i.get("to_component_id") for i in interfaces}
 if None in component_ids: raise PrototypePackageError("interface endpoints required")
 for i in interfaces:
  for f in ("interface_type","from_component_id","to_component_id","control_document_ref",
            "revision","evidence_id","source_revision"):
   _text(i.get(f),f"interface.{f}")
  if i["from_component_id"]==i["to_component_id"]:
   raise PrototypePackageError("interface endpoints must be distinct")
 return {"interface_count":len(interfaces),"functional_interfaces_present":True}

def validate_drawings(drawings, component_ids):
 _unique(drawings,"drawing_id","drawings")
 types={d.get("drawing_type") for d in drawings}
 if not REQUIRED_DRAWING_TYPES.issubset(types):
  raise PrototypePackageError(f"missing drawing types: {sorted(REQUIRED_DRAWING_TYPES-types)}")
 for d in drawings:
  for f in ("title","revision","status","evidence_id","source_revision"):
   _text(d.get(f),f"drawing.{f}")
  if d["drawing_type"] not in REQUIRED_DRAWING_TYPES:
   raise PrototypePackageError("unsupported drawing_type")
  if d.get("status") not in ("planned","candidate","reviewed","approved"):
   raise PrototypePackageError("invalid drawing status")
  if d.get("component_id") is not None and d["component_id"] not in component_ids:
   raise PrototypePackageError("drawing references unknown component")
 return {"drawing_count":len(drawings),"drawing_types_present":sorted(types)}

def validate_assembly_steps(steps, component_ids):
 _unique(steps,"step_id","assembly_steps")
 seq=[s.get("sequence") for s in steps]
 if any(isinstance(x,bool) or not isinstance(x,int) or x<=0 for x in seq) or len(seq)!=len(set(seq)):
  raise PrototypePackageError("assembly sequence numbers must be unique positive integers")
 for s in steps:
  for f in ("operation","work_instruction_ref","revision","evidence_id","source_revision"):
   _text(s.get(f),f"assembly_step.{f}")
  if not isinstance(s.get("component_ids"),list) or not s["component_ids"]:
   raise PrototypePackageError("assembly step requires component_ids")
  if not set(s["component_ids"]).issubset(component_ids):
   raise PrototypePackageError("assembly step references unknown component")
  if s.get("hold_point") not in (True,False):
   raise PrototypePackageError("hold_point must be boolean")
 return {"assembly_step_count":len(steps),"sequence_order":sorted(seq)}

def validate_inspection(inspections, component_ids):
 _unique(inspections,"characteristic_id","inspection")
 for x in inspections:
  for f in ("component_id","characteristic","method_ref","acceptance_reference",
            "instrument_or_gauge_ref","evidence_id","source_revision"):
   _text(x.get(f),f"inspection.{f}")
  if x["component_id"] not in component_ids:
   raise PrototypePackageError("inspection references unknown component")
  if x.get("status") not in ("planned","reviewed","approved"):
   raise PrototypePackageError("invalid inspection status")
 return {"inspection_characteristics":len(inspections)}

def validate_verification(verification):
 required={"functional_state_sequence","pusher_force_travel","partial_actuation",
 "reset_zero_repeatability","running_reset_interlock","retention_behavior",
 "wear_and_serviceability","timekeeping_and_energy_impact"}
 if not isinstance(verification,list): raise PrototypePackageError("verification must be a list")
 ids=_unique(verification,"test_id","verification")
 families={v.get("test_family") for v in verification}
 missing=required-families
 if missing: raise PrototypePackageError(f"missing verification families: {sorted(missing)}")
 for v in verification:
  for f in ("test_family","procedure_ref","procedure_revision","acceptance_reference",
            "evidence_id","source_revision"):
   _text(v.get(f),f"verification.{f}")
  if v.get("status") not in ("planned","reviewed","approved","executed"):
   raise PrototypePackageError("invalid verification status")
 return {"verification_tests":len(ids),"test_families_present":sorted(families)}

def validate_gates(gates):
 _unique(gates,"gate_id","gates")
 if {g["gate_id"] for g in gates}!=REQUIRED_GATES:
  raise PrototypePackageError("all required release gates must be present exactly once")
 outcomes={}
 for g in gates:
  for f in ("disposition","evidence_id","source_revision","reviewer"):
   _text(g.get(f),f"gate.{f}")
  if g["disposition"] not in ("open","pass","fail","not_applicable"):
   raise PrototypePackageError("invalid gate disposition")
  if g["disposition"]=="not_applicable":
   _text(g.get("na_rationale"),"gate.na_rationale")
   _text(g.get("na_approval_id"),"gate.na_approval_id")
  outcomes[g["gate_id"]]=g["disposition"]
 return {"gate_outcomes":outcomes,"all_pass":all(x=="pass" for x in outcomes.values()),
         "not_passed":[k for k,v in outcomes.items() if v!="pass"]}

def validate_candidate_package(package, common_baseline):
 candidate_id=package.get("candidate_id")
 if candidate_id not in CANDIDATES: raise PrototypePackageError("candidate_id must be column_wheel or cam_lever")
 for f in ("package_id","configuration_revision","article_id","requirements_revision",
           "architecture_candidate_id","evidence_id","source_revision","responsible_engineer"):
  _text(package.get(f),f"package.{f}")
 if package["requirements_revision"]!=common_baseline.get("requirements_revision"):
  raise PrototypePackageError("candidate requirements revision differs from common baseline")
 if package.get("shared_interface_baseline_id")!=common_baseline.get("shared_interface_baseline_id"):
  raise PrototypePackageError("shared interface baseline mismatch")
 if package.get("common_fixture_revision")!=common_baseline.get("common_fixture_revision"):
  raise PrototypePackageError("common fixture revision mismatch")
 components=package.get("components")
 c=validate_components(candidate_id,components)
 component_ids={x["component_id"] for x in components}
 bom=validate_bom(package.get("bom"),component_ids)
 interfaces=validate_interfaces(package.get("interfaces"),candidate_id)
 if not component_ids.issuperset(
   {i["from_component_id"] for i in package["interfaces"]}|{i["to_component_id"] for i in package["interfaces"]}):
  raise PrototypePackageError("interface endpoint not present in component register")
 drawings=validate_drawings(package.get("drawings"),component_ids)
 assembly=validate_assembly_steps(package.get("assembly_steps"),component_ids)
 inspection=validate_inspection(package.get("inspection"),component_ids)
 verification=validate_verification(package.get("verification"))
 gates=validate_gates(package.get("gates"))
 return {"candidate_id":candidate_id,"component_summary":c,"bom_summary":bom,
  "interface_summary":interfaces,"drawing_summary":drawings,"assembly_summary":assembly,
  "inspection_summary":inspection,"verification_summary":verification,"gate_summary":gates,
  "package_complete_as_record":True,"release_gate_passed":gates["all_pass"],
  "physical_article_exists":package.get("physical_article_status") in ("built","inspected","tested"),
  "build_authorized":False,"inspection_acceptance_authorized":False,
  "test_release_authorized":False,"manufacturing_release_authorized":False}

def evaluate_integrated_package(packet):
 for f in ("package_set_id","package_set_revision","evidence_id","source_revision","owner"):
  _text(packet.get(f),f"packet.{f}")
 baseline=packet.get("common_baseline")
 if not isinstance(baseline,dict): raise PrototypePackageError("common_baseline required")
 for f in ("requirements_revision","shared_interface_baseline_id","common_fixture_revision",
           "common_test_protocol_revision","movement_interface_revision"):
  _text(baseline.get(f),f"common_baseline.{f}")
 packages=packet.get("candidate_packages")
 if not isinstance(packages,dict) or set(packages)!=CANDIDATES:
  raise PrototypePackageError("both CW and CL candidate packages are required")
 results={cid:validate_candidate_package(packages[cid],baseline) for cid in sorted(CANDIDATES)}
 # Comparison basis only: do not pool candidate-specific geometry or claim physical equivalence.
 comparable={
  "requirements_revision_match":True,
  "shared_interface_baseline_match":True,
  "common_fixture_revision_match":True,
  "common_test_protocol_revision_present":True,
  "physical_equivalence_proven":False
 }
 complete=all(r["package_complete_as_record"] for r in results.values())
 gates=all(r["release_gate_passed"] for r in results.values())
 return {"package_set_id":packet["package_set_id"],"candidate_results":results,
  "common_comparison_basis":comparable,"both_packages_record_complete":complete,
  "both_candidate_gate_sets_pass":gates,
  "next_status":"ELIGIBLE_FOR_SEPARATE_RELEASE_REVIEW" if complete and gates else "ENGINEERING_DEFINITION_INCOMPLETE",
  "cw_cl_architecture_selected":False,"clutch_architecture_selected":False,
  "physical_build_authorized":False,"physical_test_authorized":False,
  "manufacturing_release_authorized":False,
  "limitations":["record completeness is not design correctness",
   "no geometry, strength, fit, motion, contact, safety or durability certification",
   "no automatic authorization of build, inspection, test or manufacture",
   "common metadata does not prove physical equivalence"]}
