"""WP-43 pusher/lever force and travel calculation framework.

All dimensions and measured curves are caller-supplied. Ideal rigid-lever
relations are screening calculations, not a substitute for contact, flexure,
friction, dynamic or tolerance analysis.
"""
from __future__ import annotations
import math

class PusherEngineeringError(ValueError):
    pass

def _positive(value, name):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:
        raise PusherEngineeringError(f"{name} must be a finite positive number")
    return float(value)

def _nonnegative(value,name):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
        raise PusherEngineeringError(f"{name} must be a finite non-negative number")
    return float(value)

def lever_stage(input_arm_mm, output_arm_mm, efficiency, input_force_n, input_travel_mm, lost_motion_mm=0.0):
    ri=_positive(input_arm_mm,"input_arm_mm"); ro=_positive(output_arm_mm,"output_arm_mm")
    eta=_positive(efficiency,"efficiency")
    if eta>1: raise PusherEngineeringError("efficiency cannot exceed 1")
    fi=_positive(input_force_n,"input_force_n")
    xi=_positive(input_travel_mm,"input_travel_mm")
    lost=_nonnegative(lost_motion_mm,"lost_motion_mm")
    if lost>=xi: raise PusherEngineeringError("lost motion must be less than input travel")
    ma=ri/ro
    xo=(xi-lost)/ma
    fo=fi*ma*eta
    return {"ideal_mechanical_advantage":ma,"input_force_n":fi,"estimated_output_force_n":fo,
      "input_travel_mm":xi,"lost_motion_mm":lost,"estimated_output_travel_mm":xo,
      "efficiency_assumption":eta,"output_force_is_screening_estimate":True}

def lever_chain(stages):
    if not isinstance(stages,list) or not stages: raise PusherEngineeringError("stages must be non-empty")
    total_ma=1.0; total_eta=1.0
    for i,s in enumerate(stages):
        ri=_positive(s.get("input_arm_mm"),f"stage {i} input_arm_mm")
        ro=_positive(s.get("output_arm_mm"),f"stage {i} output_arm_mm")
        eta=_positive(s.get("efficiency"),f"stage {i} efficiency")
        if eta>1: raise PusherEngineeringError("stage efficiency cannot exceed 1")
        total_ma*=ri/ro; total_eta*=eta
    return {"ideal_force_ratio":total_ma,"combined_efficiency_assumption":total_eta,
      "actual_force_ratio_screen":total_ma*total_eta,"stage_count":len(stages),
      "note":"Rigid, quasi-static, small-angle lever screening only; friction and compliance require measured validation."}

def integrate_force_travel(samples, evidence_id, source_revision):
    if not isinstance(evidence_id,str) or not evidence_id.strip() or not isinstance(source_revision,str) or not source_revision.strip():
        raise PusherEngineeringError("evidence_id and source_revision are required")
    if not isinstance(samples,list) or len(samples)<2: raise PusherEngineeringError("at least two force-travel samples required")
    clean=[]
    for i,p in enumerate(samples):
        x=_nonnegative(p.get("travel_mm"),f"sample {i} travel_mm")
        f=_nonnegative(p.get("force_n"),f"sample {i} force_n")
        if clean and x<=clean[-1][0]: raise PusherEngineeringError("travel samples must be strictly increasing")
        clean.append((x,f))
    work_n_mm=sum((clean[i+1][1]+clean[i][1])*0.5*(clean[i+1][0]-clean[i][0]) for i in range(len(clean)-1))
    return {"travel_range_mm":[clean[0][0],clean[-1][0]],"peak_sampled_force_n":max(p[1] for p in clean),
      "quasi_static_work_j":work_n_mm/1000.0,"sample_count":len(clean),
      "evidence_id":evidence_id,"source_revision":source_revision,
      "limitations":["Interpolation is piecewise linear between measured samples.",
        "Dynamic inertia, impact, hysteresis, side loading and measurement uncertainty are not inferred."]}

def validate_pusher_path(record):
    required=("path_id","source_member_id","destination_member_id","evidence_id","source_revision")
    for f in required:
        if not isinstance(record.get(f),str) or not record[f].strip(): raise PusherEngineeringError(f"{f} is required")
    if record["source_member_id"]==record["destination_member_id"]: raise PusherEngineeringError("path endpoints must differ")
    stages=record.get("stages")
    if not isinstance(stages,list) or not stages: raise PusherEngineeringError("at least one lever stage is required")
    for i,s in enumerate(stages):
        for f in ("stage_id","pivot_reference","input_contact_reference","output_contact_reference","evidence_id","source_revision"):
            if not isinstance(s.get(f),str) or not s[f].strip(): raise PusherEngineeringError(f"stage {i} {f} is required")
        for f in ("input_arm_mm","output_arm_mm"):
            _positive(s.get(f),f"stage {i} {f}")
    return {"path_id":record["path_id"],"stage_count":len(stages),"geometry_record_complete":True,
      "physical_path_verified":False}
