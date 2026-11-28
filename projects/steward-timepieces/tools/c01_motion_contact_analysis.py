"""WP-55 sampled motion, contact-gap and event-timing analysis.

This is evidence-gated planar/axial envelope screening. It does not solve
rigid-body dynamics, frictional contact, elastic deformation, or physical fit.
All inputs are explicit and carry evidence/source provenance.
"""
from __future__ import annotations
import math

class MotionContactError(ValueError):
    pass

def _text(v, name):
    if not isinstance(v, str) or not v.strip():
        raise MotionContactError(f"{name} is required")
    return v

def _num(v, name):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise MotionContactError(f"{name} must be finite numeric")
    return float(v)

def _positive(v, name):
    x = _num(v, name)
    if x <= 0:
        raise MotionContactError(f"{name} must be positive")
    return x

def validate_motion_package(package):
    for f in ("candidate_id", "configuration_revision", "time_unit", "length_unit", "evidence_id", "source_revision"):
        _text(package.get(f), f"package.{f}")
    if package["candidate_id"] not in ("column_wheel", "cam_lever"):
        raise MotionContactError("candidate_id must be column_wheel or cam_lever")
    if package["time_unit"] != "s" or package["length_unit"] != "mm":
        raise MotionContactError("time unit must be s and length unit must be mm")
    samples = package.get("samples")
    if not isinstance(samples, list) or len(samples) < 2:
        raise MotionContactError("at least two samples required")
    times = [_num(s.get("time_s"), "time_s") for s in samples]
    if any(b <= a for a,b in zip(times,times[1:])):
        raise MotionContactError("sample times must strictly increase")
    bodies = package.get("bodies")
    if not isinstance(bodies, list) or not bodies:
        raise MotionContactError("bodies must be non-empty")
    ids = [b.get("body_id") for b in bodies]
    if any(not isinstance(i,str) or not i.strip() for i in ids) or len(ids) != len(set(ids)):
        raise MotionContactError("body IDs must be present and unique")
    for b in bodies:
        for f in ("role","geometry_type","evidence_id","source_revision"):
            _text(b.get(f), f"body.{f}")
        if b["geometry_type"] != "circle_envelope":
            raise MotionContactError("only circle_envelope is supported in WP-55")
        radius = _positive(b.get("radius_mm"), "radius_mm")
        poses = b.get("poses")
        if not isinstance(poses,list) or len(poses) != len(samples):
            raise MotionContactError("each body requires one pose per sample")
        for p in poses:
            for f in ("x_mm","y_mm","angle_deg","z_min_mm","z_max_mm"):
                _num(p.get(f), f)
            if p["z_max_mm"] <= p["z_min_mm"]:
                raise MotionContactError("body axial interval must have positive thickness")
    return {"sample_count":len(samples),"body_count":len(bodies),
            "time_start_s":times[0],"time_end_s":times[-1],"validated":True}

def analyze_pair_contact(package, body_a_id, body_b_id, contact_tolerance_mm):
    """Evaluate sampled signed envelope gap; negative means envelope penetration."""
    validate_motion_package(package)
    tol = _num(contact_tolerance_mm, "contact_tolerance_mm")
    if tol < 0: raise MotionContactError("contact_tolerance_mm must be non-negative")
    byid = {b["body_id"]:b for b in package["bodies"]}
    if body_a_id not in byid or body_b_id not in byid or body_a_id == body_b_id:
        raise MotionContactError("pair must identify two distinct declared bodies")
    a,b = byid[body_a_id],byid[body_b_id]
    rows=[]
    for i,(pa,pb) in enumerate(zip(a["poses"],b["poses"])):
        axial = min(pa["z_max_mm"],pb["z_max_mm"]) - max(pa["z_min_mm"],pb["z_min_mm"])
        if axial <= 0:
            rows.append({"sample_index":i,"time_s":package["samples"][i]["time_s"],
                         "axial_overlap":False,"gap_mm":None,"contact_band":False,"penetration":False})
            continue
        center=math.hypot(pa["x_mm"]-pb["x_mm"],pa["y_mm"]-pb["y_mm"])
        gap=center-a["radius_mm"]-b["radius_mm"]
        rows.append({"sample_index":i,"time_s":package["samples"][i]["time_s"],
                     "axial_overlap":True,"gap_mm":gap,
                     "contact_band":abs(gap)<=tol,"penetration":gap<0})
    active=[r for r in rows if r["axial_overlap"]]
    if not active:
        return {"body_a":body_a_id,"body_b":body_b_id,"samples":rows,
                "minimum_gap_mm":None,"maximum_penetration_mm":0.0,
                "contact_detected":False,"physical_contact_verified":False}
    minrow=min(active,key=lambda r:r["gap_mm"])
    return {"body_a":body_a_id,"body_b":body_b_id,"samples":rows,
            "minimum_gap_mm":minrow["gap_mm"],
            "minimum_gap_time_s":minrow["time_s"],
            "maximum_penetration_mm":max(0.0,-minrow["gap_mm"]),
            "contact_band_sample_count":sum(r["contact_band"] for r in active),
            "penetration_sample_count":sum(r["penetration"] for r in active),
            "contact_detected":any(r["contact_band"] for r in active),
            "physical_contact_verified":False,
            "limitations":["circle envelopes only","sampled instants only","no friction or contact force",
                           "no elastic deformation or swept-solid continuous collision"]}

def differentiate_motion(package, body_id):
    """Finite-difference planar center velocity/acceleration and angular velocity."""
    validate_motion_package(package)
    body=next((b for b in package["bodies"] if b["body_id"]==body_id),None)
    if body is None: raise MotionContactError("unknown body_id")
    t=[s["time_s"] for s in package["samples"]]
    def derivative(values):
        out=[]
        for i in range(len(values)):
            if i==0: j,k=0,1
            elif i==len(values)-1: j,k=i-1,i
            else: j,k=i-1,i+1
            out.append((values[k]-values[j])/(t[k]-t[j]))
        return out
    x=[p["x_mm"] for p in body["poses"]]; y=[p["y_mm"] for p in body["poses"]]
    # Caller must supply a continuous/unwrapped angle series.
    ang=[p["angle_deg"] for p in body["poses"]]
    vx,vy,omega=derivative(x),derivative(y),derivative(ang)
    ax,ay=derivative(vx),derivative(vy)
    return {"body_id":body_id,"samples":[
        {"time_s":t[i],"vx_mm_s":vx[i],"vy_mm_s":vy[i],
         "speed_mm_s":math.hypot(vx[i],vy[i]),"ax_mm_s2":ax[i],"ay_mm_s2":ay[i],
         "angular_velocity_deg_s":omega[i]} for i in range(len(t))],
        "angle_series_assumption":"input angle_deg is continuous/unwrapped",
        "dynamics_verified":False,"noise_filtered":False}

def analyze_event_timing(events, required_order, evidence_id, source_revision):
    """Check event presence/order and report measured interval; no assumed timing limits."""
    _text(evidence_id,"evidence_id"); _text(source_revision,"source_revision")
    if not isinstance(events,list) or not events: raise MotionContactError("events must be non-empty")
    if not isinstance(required_order,list) or len(required_order)<2 or len(set(required_order))!=len(required_order):
        raise MotionContactError("required_order must contain at least two unique event names")
    seen={}
    for e in events:
        name=_text(e.get("event"),"event.event")
        t=_num(e.get("time_s"),"event.time_s")
        if name in seen: raise MotionContactError("event names must be unique in one sequence")
        seen[name]=t
    missing=[n for n in required_order if n not in seen]
    if missing: raise MotionContactError(f"required events missing: {missing}")
    times=[seen[n] for n in required_order]
    monotonic=all(b>a for a,b in zip(times,times[1:]))
    return {"required_order":required_order,"event_times_s":times,
            "intervals_s":[b-a for a,b in zip(times,times[1:])],
            "order_pass":monotonic,"missing_events":[],
            "evidence_id":evidence_id,"source_revision":source_revision,
            "timing_acceptance_assessed":False}

def lever_moment_screen(pivot_xy_mm, contact_xy_mm, force_vector_n, evidence_id, source_revision):
    """2D signed moment from explicit position vector and force; not a linkage solver."""
    _text(evidence_id,"evidence_id"); _text(source_revision,"source_revision")
    if len(pivot_xy_mm)!=2 or len(contact_xy_mm)!=2 or len(force_vector_n)!=2:
        raise MotionContactError("pivot, contact and force vectors must each have two values")
    px,py=(_num(v,"pivot coordinate") for v in pivot_xy_mm)
    cx,cy=(_num(v,"contact coordinate") for v in contact_xy_mm)
    fx,fy=(_num(v,"force component") for v in force_vector_n)
    rx,ry=cx-px,cy-py
    moment=rx*fy-ry*fx
    return {"moment_n_mm":moment,"moment_n_m":moment/1000.0,
            "evidence_id":evidence_id,"source_revision":source_revision,
            "friction_and_compliance_included":False,"dynamic_equilibrium_verified":False}

def compare_motion_packages(a,b):
    """Metadata comparability gate only; does not assert physical equivalence."""
    validate_motion_package(a); validate_motion_package(b)
    fields=("configuration_revision","time_unit","length_unit")
    mismatches=[f for f in fields if a[f]!=b[f]]
    return {"metadata_comparable":not mismatches,"mismatches":mismatches,
            "physical_equivalence_proven":False,
            "candidate_pair":[a["candidate_id"],b["candidate_id"]]}
