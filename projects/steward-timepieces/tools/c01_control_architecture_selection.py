"""WP-56 evidence-gated architecture decision packet.

Consumes controlled criteria, candidate scores, measured comparisons and gates.
Calculates transparent weighted summaries but never selects or freezes C-01.
"""
from __future__ import annotations
from fractions import Fraction
import math

class SelectionError(ValueError):
    pass

CANDIDATES={"column_wheel","cam_lever"}
REQUIRED_CRITERIA={
 "actuation_force_travel","state_repeatability","partial_actuation",
 "clutch_phase","retention_phase","reset_interlock","wear_inspection",
 "serviceability","manufacturability","packaging"
}
REQUIRED_GATES={
 "requirements_baseline","candidate_configuration_baseline",
 "comparable_test_conditions","approved_measurement_procedures",
 "instrument_calibration_and_uncertainty","physical_running_reset_interlock",
 "motion_and_contact_review","energy_and_timekeeping_impact_review",
 "risk_disposition","independent_design_review"
}
COMBINATIONS={
 "A":{"clutch":"vertical_friction","control":"column_wheel"},
 "B":{"clutch":"vertical_friction","control":"cam_lever"},
 "C":{"clutch":"horizontal_lateral","control":"column_wheel"},
 "D":{"clutch":"horizontal_lateral","control":"cam_lever"},
}

def _text(v,label):
 if not isinstance(v,str) or not v.strip(): raise SelectionError(f"{label} is required")
 return v

def _num(v,label):
 if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
  raise SelectionError(f"{label} must be finite numeric")
 return float(v)

def _fraction(v,label):
 try: x=Fraction(str(v))
 except Exception as e: raise SelectionError(f"{label} must be rational") from e
 if x<0: raise SelectionError(f"{label} must be non-negative")
 return x

def validate_criteria(criteria):
 if not isinstance(criteria,list): raise SelectionError("criteria must be a list")
 ids=[c.get("criterion_id") for c in criteria]
 if len(ids)!=len(set(ids)) or set(ids)!=REQUIRED_CRITERIA:
  raise SelectionError("criteria must contain each required criterion exactly once")
 total=Fraction(0)
 for c in criteria:
  for f in ("criterion_id","definition","measurement_method","acceptance_reference","evidence_id","source_revision","direction","approval_id"):
   _text(c.get(f),f"criterion.{f}")
  if c["direction"] not in ("higher_is_better","lower_is_better"):
   raise SelectionError("direction must be higher_is_better or lower_is_better")
  if c.get("approved") is not True: raise SelectionError("all criteria require approval")
  w=_fraction(c.get("weight"),"criterion.weight")
  if w<=0: raise SelectionError("each criterion weight must be positive")
  total+=w
 if total!=1: raise SelectionError("criterion weights must sum exactly to 1")
 return {"criterion_count":len(criteria),"weight_sum":str(total),"criteria_approved":True}

def validate_candidate(candidate, expected_id):
 if candidate.get("candidate_id")!=expected_id: raise SelectionError("candidate ID mismatch")
 for f in ("configuration_revision","article_id","requirements_revision","evidence_id","source_revision","clutch_compatibility_review_id"):
  _text(candidate.get(f),f"candidate.{f}")
 if candidate.get("physical_article_status") not in ("not_built","built","inspected","tested"):
  raise SelectionError("invalid physical_article_status")
 if candidate.get("approved_configuration") is not True:
  raise SelectionError("candidate configuration must be approved")
 return True

def validate_scores(criteria, candidate_scores):
 validate_criteria(criteria)
 if not isinstance(candidate_scores,dict) or set(candidate_scores)!=CANDIDATES:
  raise SelectionError("scores required for both CW and CL")
 weights={c["criterion_id"]:_fraction(c["weight"],"weight") for c in criteria}
 summaries={}
 for candidate, rows in candidate_scores.items():
  if not isinstance(rows,list): raise SelectionError("candidate scores must be a list")
  ids=[r.get("criterion_id") for r in rows]
  if len(ids)!=len(set(ids)) or set(ids)!=REQUIRED_CRITERIA:
   raise SelectionError("each candidate requires one score per criterion")
  total=Fraction(0)
  for r in rows:
   for f in ("criterion_id","evidence_id","source_revision","review_id","rationale"):
    _text(r.get(f),f"score.{f}")
   score=_num(r.get("score_1_to_5"),"score_1_to_5")
   if score<1 or score>5: raise SelectionError("scores must be between 1 and 5")
   if r.get("approved") is not True: raise SelectionError("each score requires approval")
   total+=weights[r["criterion_id"]]*Fraction(str(score))
  summaries[candidate]=total
 return summaries

def validate_measured_comparisons(comparisons):
 if not isinstance(comparisons,list) or not comparisons:
  raise SelectionError("at least one measured comparison is required")
 seen=set()
 results=[]
 for c in comparisons:
  for f in ("comparison_id","criterion_id","cw_run_id","cl_run_id","procedure_revision",
            "test_condition_id","fixture_revision","evidence_id","source_revision","unit"):
   _text(c.get(f),f"comparison.{f}")
  if c["comparison_id"] in seen: raise SelectionError("comparison IDs must be unique")
  seen.add(c["comparison_id"])
  if c["cw_run_id"]==c["cl_run_id"]: raise SelectionError("CW and CL run IDs must differ")
  cw=_num(c.get("cw_value"),"cw_value"); cl=_num(c.get("cl_value"),"cl_value")
  cu=_num(c.get("cw_expanded_uncertainty"),"cw_expanded_uncertainty")
  lu=_num(c.get("cl_expanded_uncertainty"),"cl_expanded_uncertainty")
  if cu<0 or lu<0: raise SelectionError("expanded uncertainty must be non-negative")
  direction=c.get("direction")
  if direction not in ("higher_is_better","lower_is_better"):
   raise SelectionError("comparison direction invalid")
  # Intervals overlap -> inconclusive. Otherwise determine which candidate is better.
  c_lo,c_hi=cw-cu,cw+cu; l_lo,l_hi=cl-lu,cl+lu
  if max(c_lo,l_lo)<=min(c_hi,l_hi):
   outcome="indeterminate_overlap"
  elif direction=="higher_is_better":
   outcome="CW_better" if c_lo>l_hi else "CL_better"
  else:
   outcome="CW_better" if c_hi<l_lo else "CL_better"
  results.append({"comparison_id":c["comparison_id"],"criterion_id":c["criterion_id"],
   "cw_interval":[c_lo,c_hi],"cl_interval":[l_lo,l_hi],"outcome":outcome,
   "metadata_match":True,"physical_equivalence_proven":False})
 return results

def validate_gates(gates):
 if not isinstance(gates,list): raise SelectionError("gates must be a list")
 ids=[g.get("gate_id") for g in gates]
 if len(ids)!=len(set(ids)) or set(ids)!=REQUIRED_GATES:
  raise SelectionError("all required gates must be present exactly once")
 results={}
 for g in gates:
  for f in ("gate_id","evidence_id","source_revision","reviewer","disposition"):
   _text(g.get(f),f"gate.{f}")
  if g["disposition"] not in ("open","pass","fail","not_applicable"):
   raise SelectionError("invalid gate disposition")
  if g["disposition"]=="not_applicable":
   if not _text(g.get("approved_na_rationale"),"approved_na_rationale") or g.get("na_approval_id") is None:
    raise SelectionError("not_applicable requires rationale and approval ID")
  results[g["gate_id"]]=g["disposition"]
 return {"gate_results":results,"all_pass":all(v=="pass" for v in results.values()),
         "open_or_failed":[k for k,v in results.items() if v!="pass"]}

def evaluate_decision_packet(packet):
 for f in ("decision_id","requirements_revision","decision_revision","evidence_id","source_revision","decision_authority"):
  _text(packet.get(f),f"packet.{f}")
 criteria=packet.get("criteria")
 validate_criteria(criteria)
 candidates=packet.get("candidates")
 if not isinstance(candidates,dict) or set(candidates)!=CANDIDATES:
  raise SelectionError("both candidate configuration records are required")
 for cid in CANDIDATES: validate_candidate(candidates[cid],cid)
 scores=validate_scores(criteria,packet.get("scores"))
 # Weighted score is a transparent arithmetic summary, not an optimizer or authority.
 score_out={k:{"weighted_score_1_to_5":float(v),"exact_score":str(v)} for k,v in scores.items()}
 comparison=validate_measured_comparisons(packet.get("measured_comparisons"))
 gates=validate_gates(packet.get("gates"))
 approval=packet.get("decision_approval")
 approved=(isinstance(approval,dict) and approval.get("status")=="approved"
           and approval.get("approval_id") and approval.get("signatory")
           and approval.get("date") and approval.get("selected_control") in CANDIDATES
           and approval.get("rationale"))
 all_evidence=bool(packet.get("evidence_index")) and isinstance(packet["evidence_index"],list)
 return {
  "decision_id":packet["decision_id"],"score_summary":score_out,
  "measured_comparisons":comparison,"gate_summary":gates,
  "evidence_index_present":all_evidence,
  "decision_authority_approval_present":bool(approved),
  "recommendation":"READY_FOR_DESIGN_AUTHORITY_REVIEW" if gates["all_pass"] and all_evidence else "NOT_READY",
  "selected_control":approval.get("selected_control") if approved else None,
  "architecture_selected":False,
  "design_frozen":False,
  "manufacturing_release_authorized":False,
  "clutch_architecture_selected":False,
  "combination_compatibility_matrix":COMBINATIONS,
  "limitations":["scores are weighted summaries only","no automatic winner selection",
   "clutch choice is a separate decision","approval record does not freeze or release design"]
 }
