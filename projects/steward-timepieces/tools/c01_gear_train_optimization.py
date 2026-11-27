"""WP-39 integrated gear-pair and chronograph-train candidate optimization.

Candidate ranking only. Requires explicit search bounds, gear-system inputs,
train order and provenance. No C-01 geometry or acceptance thresholds defaulted.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import product
from math import hypot

try:
    from c01_tooth_synthesis import pair_candidates
    from c01_gear_tooth_design import gear_parameters, external_mesh_screen
except ImportError:
    from .c01_tooth_synthesis import pair_candidates
    from .c01_gear_tooth_design import gear_parameters, external_mesh_screen

class OptimizationInputError(ValueError):
    pass

def _text(v,n):
    if not isinstance(v,str) or not v.strip(): raise OptimizationInputError(f"{n} is required")
    return v

def _pos(v,n):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or v<=0: raise OptimizationInputError(f"{n} must be positive")
    return float(v)

def _fraction(v,n,positive=False):
    try: f=Fraction(str(v))
    except Exception as e: raise OptimizationInputError(f"{n} must be rational") from e
    if positive and f<=0: raise OptimizationInputError(f"{n} must be positive")
    return f

def _ids(records,key,label):
    vals=[_text(r.get(key),f"{label}.{key}") for r in records]
    if len(vals)!=len(set(vals)): raise OptimizationInputError(f"{label} IDs must be unique")
    return set(vals)

def optimize_train(data):
    """Enumerate shared-gear-consistent external spur train candidates.

    Required: candidate_id, evidence_id, source_revision, gears, ordered_meshes,
    overall_target_ratio, max_overall_fractional_error, max_candidates.
    Each gear requires module_mm, pressure_angle_deg, addendum_coefficient,
    dedendum_coefficient, profile_shift, arbor_id, evidence_id, source_revision.
    Each mesh requires driver_gear_id, driven_gear_id, min_teeth, max_teeth,
    min_stage_ratio, max_stage_ratio, max_fractional_error, and optional
    xy_center_distance_mm / center_distance_tolerance_mm / min_contact_ratio.
    """
    if not isinstance(data,dict): raise OptimizationInputError("data must be an object")
    cid=_text(data.get("candidate_id"),"candidate_id")
    evidence=_text(data.get("evidence_id"),"evidence_id")
    revision=_text(data.get("source_revision"),"source_revision")
    gears=data.get("gears"); meshes=data.get("ordered_meshes")
    if not isinstance(gears,list) or not gears: raise OptimizationInputError("gears must be non-empty")
    if not isinstance(meshes,list) or not meshes: raise OptimizationInputError("ordered_meshes must be non-empty")
    gear_ids=_ids(gears,"gear_id","gear")
    _ids(meshes,"mesh_id","mesh")
    bygear={g["gear_id"]:g for g in gears}
    for g in gears:
        for f in ("arbor_id","evidence_id","source_revision"): _text(g.get(f),f"gear {g['gear_id']}.{f}")
        for f in ("module_mm","pressure_angle_deg","addendum_coefficient","dedendum_coefficient"):
            _pos(g.get(f),f"gear {g['gear_id']}.{f}")
        if "profile_shift" not in g or isinstance(g["profile_shift"],bool) or not isinstance(g["profile_shift"],(int,float)):
            raise OptimizationInputError(f"gear {g['gear_id']} needs explicit profile_shift")
    max_candidates=data.get("max_candidates")
    if isinstance(max_candidates,bool) or not isinstance(max_candidates,int) or max_candidates<1:
        raise OptimizationInputError("max_candidates must be a positive integer")
    overall_target=_fraction(data.get("overall_target_ratio"),"overall_target_ratio",True)
    max_error=_fraction(data.get("max_overall_fractional_error"),"max_overall_fractional_error")
    if max_error<0 or max_error>=1: raise OptimizationInputError("overall error bound must be in [0,1)")
    options=[]
    for mesh in meshes:
        for f in ("driver_gear_id","driven_gear_id"):
            if mesh.get(f) not in gear_ids: raise OptimizationInputError(f"mesh {mesh.get('mesh_id')} has unknown {f}")
        if mesh["driver_gear_id"]==mesh["driven_gear_id"]: raise OptimizationInputError("mesh must join distinct gears")
        if bygear[mesh["driver_gear_id"]]["arbor_id"]==bygear[mesh["driven_gear_id"]]["arbor_id"]:
            raise OptimizationInputError("meshing gears must be assigned to distinct arbors")
        if _pos(bygear[mesh["driver_gear_id"]]["module_mm"],"module") != _pos(bygear[mesh["driven_gear_id"]]["module_mm"],"module"):
            raise OptimizationInputError("meshing gear modules must match")
        if bygear[mesh["driver_gear_id"]]["pressure_angle_deg"] != bygear[mesh["driven_gear_id"]]["pressure_angle_deg"]:
            raise OptimizationInputError("meshing reference pressure angles must match")
        required=("min_teeth","max_teeth","min_stage_ratio","max_stage_ratio","max_fractional_error")
        for f in required:
            if f not in mesh: raise OptimizationInputError(f"mesh {mesh['mesh_id']} missing {f}")
        pairs=pair_candidates(mesh["min_teeth"],mesh["max_teeth"],mesh["min_stage_ratio"],mesh["max_stage_ratio"])
        target=_fraction(mesh.get("target_ratio",1),"mesh target_ratio",True)
        bound=_fraction(mesh["max_fractional_error"],"mesh max_fractional_error")
        valid=[p for p in pairs if abs(p["speed_ratio_magnitude"]-target)/target<=bound]
        if not valid: return {"candidate_id":cid,"candidate_count":0,"candidates":[],"status":"no_candidates_within_declared_mesh_bounds","design_selected":False}
        options.append(valid)
    candidates=[]
    for combo in product(*options):
        assignment={}; schedule=[]; consistent=True
        for mesh,pair in zip(meshes,combo):
            for gid,z in ((mesh["driver_gear_id"],pair["driver_teeth"]),(mesh["driven_gear_id"],pair["driven_teeth"])):
                if gid in assignment and assignment[gid]!=z: consistent=False; break
                assignment[gid]=z
            if not consistent: break
            schedule.append({"mesh_id":mesh["mesh_id"],"driver_gear_id":mesh["driver_gear_id"],
                "driven_gear_id":mesh["driven_gear_id"],"driver_teeth":pair["driver_teeth"],
                "driven_teeth":pair["driven_teeth"],"ratio":str(pair["speed_ratio_magnitude"])})
        if not consistent: continue
        total=Fraction(1,1)
        for p in combo: total*=p["speed_ratio_magnitude"]
        error=abs(total-overall_target)/overall_target
        if error>max_error: continue
        geometry=[]; physical_constraints_pass=True; score_terms=[]
        for mesh,pair in zip(meshes,combo):
            ga=dict(bygear[mesh["driver_gear_id"]]); gb=dict(bygear[mesh["driven_gear_id"]])
            for g,z in ((ga,pair["driver_teeth"]),(gb,pair["driven_teeth"])):
                gp=gear_parameters(module_mm=g["module_mm"],teeth=z,pressure_angle_deg=g["pressure_angle_deg"],
                    addendum_coefficient=g["addendum_coefficient"],dedendum_coefficient=g["dedendum_coefficient"],
                    profile_shift=g["profile_shift"],evidence_id=g["evidence_id"],source_revision=g["source_revision"])
                g.update(gp)
            check=external_mesh_screen(gear_a=ga,gear_b=gb,
                center_distance_mm=mesh.get("center_distance_mm"),
                minimum_contact_ratio=mesh.get("min_contact_ratio"),
                evidence_id=evidence,source_revision=revision)
            item={"mesh_id":mesh["mesh_id"],"contact_ratio":check["transverse_contact_ratio"],
                  "contact_ratio_screen":check.get("contact_ratio_screen","THRESHOLD_NOT_SUPPLIED"),
                  "undercut_screens":[check["gear_a_zero_shift_undercut_screen"],check["gear_b_zero_shift_undercut_screen"]]}
            xy=mesh.get("xy_center_distance_mm")
            tol=mesh.get("center_distance_tolerance_mm")
            nominal=check["nominal_reference_center_distance_mm"]
            if xy is not None and tol is not None:
                xy=_pos(xy,"xy_center_distance_mm"); tol=_pos(tol,"center_distance_tolerance_mm")
                delta=xy-nominal; passes=abs(delta)<=tol
                item.update({"xy_center_distance_mm":xy,"nominal_center_distance_mm":nominal,
                    "center_distance_deviation_mm":delta,"center_distance_tolerance_mm":tol,
                    "center_distance_pass":passes})
                if not passes: physical_constraints_pass=False
            else:
                item["center_distance_status"]="NOT_EVALUABLE_MISSING_COORDINATE_OR_TOLERANCE"
                physical_constraints_pass=False
            if item["contact_ratio_screen"]=="BELOW_THRESHOLD": physical_constraints_pass=False
            geometry.append(item)
            score_terms.append(check["transverse_contact_ratio"])
        candidates.append({"tooth_assignments":assignment,"mesh_schedule":schedule,
            "overall_ratio":str(total),"overall_fractional_error":str(error),
            "mesh_geometry":geometry,"all_declared_screening_constraints_pass":physical_constraints_pass,
            "ranking_score":{"ratio_error":float(error),"minimum_contact_ratio":min(score_terms)},
            "status":"ANALYTICAL_CANDIDATE_NOT_A_DESIGN"})
    candidates.sort(key=lambda c:(c["ranking_score"]["ratio_error"],-c["ranking_score"]["minimum_contact_ratio"],
                                  tuple(sorted(c["tooth_assignments"].items()))))
    return {"schema":"steward.c01.wp39.v1","candidate_id":cid,
        "candidate_count":len(candidates),"returned_candidates":candidates[:max_candidates],
        "search_space_truncated":len(candidates)>max_candidates,
        "status":"ranked_analytical_candidates_no_selection","design_selected":False,
        "architecture_frozen":False,"manufacturing_release":False,
        "limitations":["External spur gears only; all mesh modules and reference pressure angles must match.",
          "Candidate enumeration is bounded by declared ranges and result cap; no global optimality claim.",
          "Contact ratio and undercut outputs are analytical screens, not specialist gear certification.",
          "Center-distance screening uses explicit supplied center distance and tolerance only.",
          "No gear strength, fatigue, contact stress, wear, lubrication, dynamic load, efficiency or noise analysis.",
          "No bearing, plate, bridge, swept-motion, assembly or serviceability proof.",
          "No C-01 architecture is selected or frozen."]}

