"""WP-60 evidence-gated integrated chronograph control motion package validator.

This validates explicit, sampled candidate poses for visualization. It does not
solve or simulate mechanism motion, infer missing poses, or certify clearance.
"""
from __future__ import annotations
import math

class MotionVisualizationError(ValueError):
    pass

CANDIDATES = {"CW", "CL"}
STATES = ("stopped_zero", "running", "stopped_retained", "resetting")

def _text(v, name):
    if not isinstance(v, str) or not v.strip():
        raise MotionVisualizationError(f"{name} must be non-empty text")
    return v

def _num(v, name):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise MotionVisualizationError(f"{name} must be finite numeric")
    return float(v)

def _positive(v, name):
    x = _num(v, name)
    if x <= 0:
        raise MotionVisualizationError(f"{name} must be positive")
    return x

def _validate_geometry(g, label):
    if not isinstance(g, dict):
        raise MotionVisualizationError(f"{label}.geometry required")
    kind, p = g.get("type"), g.get("parameters")
    if not isinstance(p, dict):
        raise MotionVisualizationError(f"{label}.geometry.parameters required")
    if kind == "cylinder":
        _positive(p.get("radius_mm"), label+".radius_mm")
        _positive(p.get("height_mm"), label+".height_mm")
    elif kind == "annulus":
        outer = _positive(p.get("outer_radius_mm"), label+".outer_radius_mm")
        inner = _positive(p.get("inner_radius_mm"), label+".inner_radius_mm")
        if inner >= outer:
            raise MotionVisualizationError(f"{label}: annulus inner radius must be smaller")
        _positive(p.get("height_mm"), label+".height_mm")
    elif kind == "extruded_polygon":
        pts = p.get("outline_xy_mm")
        if not isinstance(pts, list) or len(pts) < 3:
            raise MotionVisualizationError(f"{label}: polygon requires at least three points")
        clean = []
        for i, point in enumerate(pts):
            if not isinstance(point, (list, tuple)) or len(point) != 2:
                raise MotionVisualizationError(f"{label}: polygon point must be XY")
            clean.append((_num(point[0], f"{label}.x{i}"), _num(point[1], f"{label}.y{i}")))
        if len(set(clean)) != len(clean):
            raise MotionVisualizationError(f"{label}: polygon vertices must be unique")
        area = sum(clean[i][0]*clean[(i+1)%len(clean)][1] -
                    clean[(i+1)%len(clean)][0]*clean[i][1] for i in range(len(clean))) / 2
        if abs(area) <= 1e-12:
            raise MotionVisualizationError(f"{label}: polygon area must be nonzero")
        _positive(p.get("height_mm"), label+".height_mm")
    else:
        raise MotionVisualizationError(f"{label}: unsupported geometry type")
    return kind

def validate_candidate(candidate):
    cid = candidate.get("candidate_id")
    if cid not in CANDIDATES:
        raise MotionVisualizationError("candidate_id must be CW or CL")
    for f in ("configuration_revision", "requirements_revision", "datum_revision",
              "interface_baseline_revision", "evidence_id", "source_revision"):
        _text(candidate.get(f), f"candidate.{f}")
    if candidate.get("time_unit") != "s" or candidate.get("length_unit") != "mm":
        raise MotionVisualizationError("units must be seconds and millimetres")
    components = candidate.get("components")
    if not isinstance(components, list) or not components:
        raise MotionVisualizationError("components must be non-empty")
    by_id = {}
    for c in components:
        comp_id = _text(c.get("component_id"), "component_id")
        if comp_id in by_id:
            raise MotionVisualizationError("component IDs must be unique")
        for f in ("role", "drawing_ref", "evidence_id", "source_revision"):
            _text(c.get(f), comp_id+"."+f)
        if c.get("status") not in ("tbd", "candidate", "reviewed", "approved"):
            raise MotionVisualizationError(f"{comp_id}: invalid geometry status")
        _validate_geometry(c.get("geometry"), comp_id)
        by_id[comp_id] = c
    frames = candidate.get("frames")
    if not isinstance(frames, list) or len(frames) < 4:
        raise MotionVisualizationError("at least four explicit motion frames required")
    seen_states, times, frame_ids = [], [], set()
    for i, frame in enumerate(frames):
        fid = _text(frame.get("frame_id"), f"frame[{i}].frame_id")
        if fid in frame_ids:
            raise MotionVisualizationError("frame IDs must be unique")
        frame_ids.add(fid)
        state = frame.get("state")
        if state not in STATES:
            raise MotionVisualizationError(f"{fid}: unsupported state")
        if not seen_states or seen_states[-1] != state:
            seen_states.append(state)
        t = _num(frame.get("time_s"), fid+".time_s")
        times.append(t)
        for f in ("evidence_id", "source_revision"):
            _text(frame.get(f), fid+"."+f)
        poses = frame.get("poses")
        if not isinstance(poses, list):
            raise MotionVisualizationError(f"{fid}: poses must be a list")
        pose_ids = [p.get("component_id") for p in poses]
        if len(pose_ids) != len(set(pose_ids)) or set(pose_ids) != set(by_id):
            raise MotionVisualizationError(f"{fid}: every component must have exactly one pose")
        for pose in poses:
            pid = pose["component_id"]
            for f in ("x_mm", "y_mm", "angle_deg", "z_min_mm", "z_max_mm"):
                _num(pose.get(f), fid+"."+pid+"."+f)
            if pose["z_max_mm"] <= pose["z_min_mm"]:
                raise MotionVisualizationError(f"{fid}.{pid}: Z interval must have positive thickness")
    if any(b <= a for a,b in zip(times, times[1:])):
        raise MotionVisualizationError("frame times must strictly increase")
    if frames[0]["state"] != "stopped_zero":
        raise MotionVisualizationError("first frame must be stopped_zero")
    if not set(STATES).issubset({f["state"] for f in frames}):
        raise MotionVisualizationError("all four operating states must be represented")
    # Require the declared reset sequence to follow retained time and return to zero.
    retained = next((i for i,f in enumerate(frames) if f["state"] == "stopped_retained"), None)
    resetting = next((i for i,f in enumerate(frames) if f["state"] == "resetting"), None)
    zero_after = next((i for i,f in enumerate(frames) if i > (resetting if resetting is not None else -1)
                       and f["state"] == "stopped_zero"), None)
    if retained is None or resetting is None or zero_after is None or not retained < resetting < zero_after:
        raise MotionVisualizationError("required sequence: stopped_retained -> resetting -> stopped_zero")
    return {
        "candidate_id": cid, "component_count": len(by_id), "frame_count": len(frames),
        "state_sequence": seen_states, "time_start_s": times[0], "time_end_s": times[-1],
        "unapproved_component_ids": [k for k,v in by_id.items() if v["status"] != "approved"],
        "poses_are_explicit": True, "motion_solved": False,
        "continuous_clearance_certified": False, "physical_fit_certified": False
    }

def validate_visualization_package(package):
    for f in ("package_id", "revision", "evidence_id", "source_revision", "owner"):
        _text(package.get(f), "package."+f)
    baseline = package.get("common_baseline")
    if not isinstance(baseline, dict):
        raise MotionVisualizationError("common_baseline required")
    for f in ("requirements_revision", "datum_revision", "interface_baseline_revision"):
        _text(baseline.get(f), "common_baseline."+f)
    candidates = package.get("candidates")
    if not isinstance(candidates, dict) or set(candidates) != CANDIDATES:
        raise MotionVisualizationError("both separate CW and CL packages are required")
    results = {}
    for cid in sorted(CANDIDATES):
        c = candidates[cid]
        if c.get("candidate_id") != cid:
            raise MotionVisualizationError("candidate key and candidate_id mismatch")
        for f in ("requirements_revision", "datum_revision", "interface_baseline_revision"):
            if c.get(f) != baseline[f]:
                raise MotionVisualizationError(f"{cid} common baseline mismatch: {f}")
        results[cid] = validate_candidate(c)
    return {
        "package_id": package["package_id"], "candidate_results": results,
        "common_baseline_match": True, "architecture_selected": False,
        "design_frozen": False, "motion_solved": False,
        "continuous_clearance_certified": False, "manufacturing_release_authorized": False
    }
