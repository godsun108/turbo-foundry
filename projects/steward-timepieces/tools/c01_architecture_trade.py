"""WP-45 evidence-gated CW vs cam/lever architecture trade study.

No scores, weights, measurements, limits, or architecture winner are supplied.
The evaluator reports provisional comparisons only and never selects an architecture.
"""
from __future__ import annotations
from fractions import Fraction
import math

class ArchitectureTradeError(ValueError):
    pass

REQUIRED_CRITERIA={
 "actuation_force_travel","state_repeatability","partial_actuation",
 "clutch_phase","retention_phase","reset_interlock","wear_inspection",
 "serviceability","manufacturability","packaging"
}
REQUIRED_GATES={"requirements_baseline","comparable_configuration","measurement_procedures",
 "instrument_calibration","physical_reset_interlock","independent_review"}

def _req(d,fields,label):
    if not isinstance(d,dict): raise ArchitectureTradeError(f"{label} must be an object")
    for f in fields:
        if not isinstance(d.get(f),str) or not d[f].strip():
            raise ArchitectureTradeError(f"{label}.{f} is required")

def _finite(v,label,nonnegative=False):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ArchitectureTradeError(f"{label} must be finite numeric")
    if nonnegative and v<0: raise ArchitectureTradeError(f"{label} must be non-negative")
    return float(v)

def _fraction(v,label):
    try: x=Fraction(str(v))
    except Exception as e: raise ArchitectureTradeError(f"{label} must be a rational number") from e
    if x<0: raise ArchitectureTradeError(f"{label} must be non-negative")
    return x

def validate_criteria(criteria):
    if not isinstance(criteria,list) or not criteria: raise ArchitectureTradeError("criteria must be non-empty")
    ids=[c.get("criterion_id") for c in criteria]
    if len(ids)!=len(set(ids)) or set(ids)!=REQUIRED_CRITERIA:
        raise ArchitectureTradeError("criteria must contain the complete required criterion set exactly once")
    weights=Fraction(0,1)
    for c in criteria:
        _req(c,("criterion_id","definition","measurement_method","acceptance_reference","evidence_id","status"),"criterion")
        if c["status"]!="approved": raise ArchitectureTradeError("all criteria must be approved before scoring")
        w=_fraction(c.get("weight"),"weight"); weights+=w
        if c.get("direction") not in ("lower_is_better","higher_is_better"):
            raise ArchitectureTradeError("criterion direction must be explicit")
    if weights!=1: raise ArchitectureTradeError("approved criterion weights must sum exactly to 1")
    return {"criterion_count":len(criteria),"weight_sum":str(weights),"criteria_approved":True}

def validate_candidate(candidate,expected_id):
    _req(candidate,("candidate_id","control_type","configuration_revision","evidence_id","source_revision","status"),"candidate")
    expected={"CW":"column_wheel","CL":"cam_lever"}
    if candidate["candidate_id"]!=expected_id or candidate["control_type"]!=expected[expected_id]:
        raise ArchitectureTradeError("candidate ID/type mismatch")
    if candidate["status"] not in ("candidate","reviewed","approved"):
        raise ArchitectureTradeError("candidate must be a defined candidate")
    return True

def compare_measurement(a,b,direction):
    for row,label in ((a,"A"),(b,"B")):
        _req(row,("value","unit","evidence_id","procedure_revision","condition_id","configuration_revision"),f"measurement {label}")
        _finite(row["value"],f"measurement {label} value")
        _finite(row.get("expanded_uncertainty"),f"measurement {label} uncertainty",True)
    if a["unit"]!=b["unit"] or a["procedure_revision"]!=b["procedure_revision"] or a["condition_id"]!=b["condition_id"]:
        raise ArchitectureTradeError("measurements must share unit, procedure revision and test condition")
    if a["configuration_revision"]==b["configuration_revision"]:
        raise ArchitectureTradeError("candidate configurations must be separately identified")
    alo=a["value"]-a["expanded_uncertainty"]; ahi=a["value"]+a["expanded_uncertainty"]
    blo=b["value"]-b["expanded_uncertainty"]; bhi=b["value"]+b["expanded_uncertainty"]
    if direction=="lower_is_better":
        a_better=ahi<blo; b_better=bhi<alo
    elif direction=="higher_is_better":
        a_better=alo>bhi; b_better=blo>ahi
    else: raise ArchitectureTradeError("invalid comparison direction")
    return {"A_interval":[alo,ahi],"B_interval":[blo,bhi],
      "distinguishable_at_supplied_uncertainty":a_better or b_better,
      "provisional_result":"A" if a_better else ("B" if b_better else "INDETERMINATE_OR_OVERLAPPING"),
      "uncertainty_method":"reported expanded uncertainty intervals; coverage factor and confidence must be documented externally"}

def evaluate_candidate_scores(criteria,scores):
    byid={c["criterion_id"]:c for c in criteria}
    if not isinstance(scores,list) or {s.get("criterion_id") for s in scores}!=set(byid) or len(scores)!=len(byid):
        raise ArchitectureTradeError("each criterion requires exactly one candidate score")
    total=Fraction(0,1); details=[]
    for s in scores:
        _req(s,("criterion_id","score","evidence_id","review_record_id"),"score")
        score=s["score"]
        if isinstance(score,bool) or not isinstance(score,int) or not 1<=score<=5:
            raise ArchitectureTradeError("scores must be integers from 1 to 5")
        if not s["evidence_id"] or not s["review_record_id"]:
            raise ArchitectureTradeError("score requires evidence and review record")
        weight=_fraction(byid[s["criterion_id"]]["weight"],"weight")
        contribution=weight*score; total+=contribution
        details.append({"criterion_id":s["criterion_id"],"weight":str(weight),
          "score":score,"weighted_contribution":str(contribution)})
    return {"weighted_score":str(total),"score_scale":"1-5; approved review rubric required",
      "details":details,"is_provisional_only":True}

def validate_gates(gates):
    if not isinstance(gates,list): raise ArchitectureTradeError("gates must be a list")
    ids=[g.get("gate_id") for g in gates]
    if len(ids)!=len(set(ids)) or set(ids)!=REQUIRED_GATES:
        raise ArchitectureTradeError("all required decision gates must be represented exactly once")
    for g in gates:
        _req(g,("gate_id","status","evidence_id","review_record_id"),"gate")
        if g["status"] not in ("open","pass","fail","not_applicable"):
            raise ArchitectureTradeError("invalid gate status")
        if g["status"]=="pass" and (g["evidence_id"]=="TBD" or g["review_record_id"]=="TBD"):
            raise ArchitectureTradeError("passed gate requires real evidence and review references")
    return {"gate_count":len(gates),"all_gates_pass":all(g["status"]=="pass" for g in gates)}

def evaluate_trade_study(study):
    _req(study,("study_id","evidence_id","source_revision","review_status","requirements_revision"),"study")
    if study["review_status"] not in ("draft","under_review","approved"):
        raise ArchitectureTradeError("invalid review status")
    validate_candidate(study.get("candidate_cw"),"CW")
    validate_candidate(study.get("candidate_cl"),"CL")
    if study["candidate_cw"]["configuration_revision"]==study["candidate_cl"]["configuration_revision"]:
        raise ArchitectureTradeError("CW and CL configuration revisions must be distinct")
    criteria=study.get("criteria"); validate_criteria(criteria)
    cw=evaluate_candidate_scores(criteria,study.get("scores_cw"))
    cl=evaluate_candidate_scores(criteria,study.get("scores_cl"))
    gates=validate_gates(study.get("gates"))
    delta=Fraction(cw["weighted_score"])-Fraction(cl["weighted_score"])
    result="CW_PROVISIONALLY_HIGHER" if delta>0 else ("CL_PROVISIONALLY_HIGHER" if delta<0 else "TIED")
    approved=study["review_status"]=="approved" and gates["all_gates_pass"]
    return {"study_id":study["study_id"],"candidate_scores":{"CW":cw,"CL":cl},
      "score_delta_CW_minus_CL":str(delta),"provisional_comparison":result,
      "gates":gates,"review_status":study["review_status"],
      "decision_ready_for_authority_review":approved,
      "architecture_selected":False,"design_frozen":False,"prototype_release_authorized":False,
      "note":"A weighted score is a decision aid, not an automatic architecture selection. Design authority must record and approve the decision."}

def compatibility_matrix():
    return {"combinations":[
      {"id":"A","clutch":"vertical_friction","control":"column_wheel","status":"open"},
      {"id":"B","clutch":"vertical_friction","control":"cam_lever","status":"open"},
      {"id":"C","clutch":"horizontal_lateral","control":"column_wheel","status":"open"},
      {"id":"D","clutch":"horizontal_lateral","control":"cam_lever","status":"open"}],
      "clutch_and_control_decisions_are_separate":"Compatibility must be evidenced for each combination; this matrix does not rank or select."}
