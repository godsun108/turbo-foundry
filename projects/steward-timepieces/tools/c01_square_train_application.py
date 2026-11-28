"""WP-SQ-04 square C-01 application adapter reusing WP-25."""
from __future__ import annotations
from fractions import Fraction
from typing import Any
try:
    from c01_going_train import evaluate_path, validate_train, target_speed_rpm
except ImportError:
    from .c01_going_train import evaluate_path, validate_train, target_speed_rpm

EXPECTED_PATH=("barrel","center","third","fourth","escape")

def evaluate_square_going_train(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data,dict): raise ValueError("candidate data must be an object")
    for key in ("candidate_id","evidence","source_revision"):
        if not isinstance(data.get(key),str) or not data[key].strip(): raise ValueError(f"{key} is required")
    path=data.get("path_arbor_ids")
    if not isinstance(path,list) or tuple(path)!=EXPECTED_PATH:
        raise ValueError("path_arbor_ids must map the WP-SQ-03 barrel-center-third-fourth-escape hypothesis")
    train={k:data.get(k) for k in ("arbors","gears","meshes")}
    checked=validate_train(train)
    if any(a not in checked["arbor_ids"] for a in path): raise ValueError("functional path references an unknown arbor")
    for group,items in train.items():
        for item in items:
            if item.get("evidence")!=data["evidence"] or item.get("source_revision")!=data["source_revision"]:
                raise ValueError(f"{group} provenance must match candidate provenance")
    if "input_rpm" not in data: raise ValueError("input_rpm must be explicit")
    if "target_output_period_seconds" not in data: raise ValueError("target_output_period_seconds must be explicit")
    target=target_speed_rpm(data["target_output_period_seconds"])
    result=evaluate_path(train,path[0],path[-1],data["input_rpm"])
    out={"schema":"steward.c01.square-going-train-application.v1","candidate_id":data["candidate_id"],
         "evidence":data["evidence"],"source_revision":data["source_revision"],
         "functional_path":path,"target_period_seconds":data["target_output_period_seconds"],
         "target_speed_rpm":str(target),"kinematic_evaluation":result,
         "design_selected":False,"physical_feasibility_established":False,
         "speed_tolerance_applied":False}
    if result["status"]=="unique_path":
        actual=abs(Fraction(result["output_rpm"]))
        out["fractional_speed_error"]=str(abs(actual-target)/target)
    else: out["fractional_speed_error"]=None
    out["unresolved_checks"]=["barrel speed/torque over wind state","gear module and tooth form",
        "center distances and tolerance stack","undercut/contact ratio/interference/strength",
        "bearing loads, lubrication and efficiency","escapement event convention and regulator energy",
        "plate/bridge packaging and assembly/service access"]
    return out
