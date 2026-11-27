"""WP-40 evidence-gated physical layout and 3D envelope assembly screening.

This is a candidate-layout validator, not a watch CAD kernel or fit certification.
All physical dimensions and placements require explicit provenance.
"""
from __future__ import annotations
from math import hypot, isfinite

class LayoutInputError(ValueError):
    pass

def _id(v, field):
    if not isinstance(v,str) or not v.strip(): raise LayoutInputError(f"{field} is required")
    return v

def _num(v, field, positive=False):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not isfinite(v):
        raise LayoutInputError(f"{field} must be finite")
    if positive and v<=0: raise LayoutInputError(f"{field} must be positive")
    return float(v)

def _unique(items, field, label):
    vals=[_id(x.get(field),f"{label}.{field}") for x in items]
    if len(vals)!=len(set(vals)): raise LayoutInputError(f"{label} IDs must be unique")
    return set(vals)

def _interval(v, field):
    if not isinstance(v,(list,tuple)) or len(v)!=2: raise LayoutInputError(f"{field} must be [z_min,z_max]")
    lo,hi=(_num(v[0],field),_num(v[1],field))
    if hi<=lo: raise LayoutInputError(f"{field} must have positive extent")
    return lo,hi

def validate_layout(data):
    if not isinstance(data,dict): raise LayoutInputError("layout must be an object")
    _id(data.get("candidate_id"),"candidate_id")
    _id(data.get("evidence_id"),"evidence_id")
    _id(data.get("source_revision"),"source_revision")
    parts=data.get("components")
    if not isinstance(parts,list) or not parts: raise LayoutInputError("components must be non-empty")
    ids=_unique(parts,"component_id","component")
    for p in parts:
        for f in ("role","evidence_id","source_revision"): _id(p.get(f),f"{p.get('component_id')}.{f}")
        xy=p.get("xy_mm")
        if not isinstance(xy,(list,tuple)) or len(xy)!=2: raise LayoutInputError(f"{p['component_id']}.xy_mm must be [x,y]")
        _num(xy[0],"x"); _num(xy[1],"y")
        _num(p.get("envelope_radius_mm"),"envelope_radius_mm",True)
        _interval(p.get("z_interval_mm"),f"{p['component_id']}.z_interval_mm")
        if "arbor_id" in p and p["arbor_id"] is not None: _id(p["arbor_id"],"arbor_id")
    meshes=data.get("gear_meshes",[])
    if not isinstance(meshes,list): raise LayoutInputError("gear_meshes must be a list")
    _unique(meshes,"mesh_id","mesh")
    byid={p["component_id"]:p for p in parts}
    for m in meshes:
        a=m.get("component_a_id"); b=m.get("component_b_id")
        if a not in ids or b not in ids or a==b: raise LayoutInputError("gear mesh endpoints must be distinct declared components")
        for f in ("evidence_id","source_revision"): _id(m.get(f),f"mesh.{f}")
        module=_num(m.get("module_mm"),"module_mm",True)
        za=m.get("teeth_a"); zb=m.get("teeth_b")
        if any(isinstance(z,bool) or not isinstance(z,int) or z<1 for z in (za,zb)): raise LayoutInputError("gear tooth counts must be positive integers")
        nominal=module*(za+zb)/2
        actual=hypot(byid[a]["xy_mm"][0]-byid[b]["xy_mm"][0],byid[a]["xy_mm"][1]-byid[b]["xy_mm"][1])
        tol=_num(m.get("center_distance_tolerance_mm"),"center_distance_tolerance_mm",True)
        delta=actual-nominal
        m["_evaluation"]={"nominal_center_distance_mm":nominal,"actual_center_distance_mm":actual,
            "deviation_mm":delta,"tolerance_mm":tol,"center_distance_pass":abs(delta)<=tol}
    supports=data.get("supports",[])
    if not isinstance(supports,list): raise LayoutInputError("supports must be a list")
    _unique(supports,"support_id","support")
    for s in supports:
        if s.get("component_id") not in ids: raise LayoutInputError("support references unknown component")
        for f in ("structural_member_id","support_type","evidence_id","source_revision"):
            _id(s.get(f),f"support.{f}")
    trajectories=data.get("trajectories",[])
    if not isinstance(trajectories,list): raise LayoutInputError("trajectories must be a list")
    _unique(trajectories,"component_id","trajectory")
    for t in trajectories:
        if t["component_id"] not in ids: raise LayoutInputError("trajectory references unknown component")
        samples=t.get("xy_samples_mm")
        if not isinstance(samples,list) or not samples: raise LayoutInputError("trajectory samples must be non-empty")
        for sample in samples:
            if not isinstance(sample,(list,tuple)) or len(sample)!=2: raise LayoutInputError("trajectory sample must be [x,y]")
            _num(sample[0],"trajectory x"); _num(sample[1],"trajectory y")
        _id(t.get("evidence_id"),"trajectory evidence_id")
        _id(t.get("source_revision"),"trajectory source_revision")
    counts={len(t["xy_samples_mm"]) for t in trajectories}
    if len(counts)>1: raise LayoutInputError("all trajectories must use the same sample count/time base")
    return {"component_ids":ids,"component_count":len(parts),"mesh_count":len(meshes),
        "support_count":len(supports),"trajectory_sample_count":next(iter(counts),0),
        "status":"INPUTS_VALIDATED_NOT_PHYSICALLY_CERTIFIED"}

def _z_overlap(a,b):
    return min(a[1],b[1])-max(a[0],b[0])>0

def evaluate_layout(data):
    validate_layout(data)
    parts=data["components"]; byid={p["component_id"]:p for p in parts}
    clearances=[]
    for i,a in enumerate(parts):
        for b in parts[i+1:]:
            if not _z_overlap(a["z_interval_mm"],b["z_interval_mm"]): continue
            d=hypot(a["xy_mm"][0]-b["xy_mm"][0],a["xy_mm"][1]-b["xy_mm"][1])
            clearance=d-a["envelope_radius_mm"]-b["envelope_radius_mm"]
            clearances.append({"component_a_id":a["component_id"],"component_b_id":b["component_id"],
                "minimum_xy_envelope_clearance_mm":clearance,"screen":"INTERFERENCE" if clearance<0 else "NO_ENVELOPE_OVERLAP"})
    motion=[]
    traj={t["component_id"]:t["xy_samples_mm"] for t in data.get("trajectories",[])}
    for i in range(max((len(x) for x in traj.values()),default=0)):
        moving=[]
        for cid,samples in traj.items():
            p=byid[cid]; moving.append((cid,samples[i],p))
        for j,(aid,ap,a) in enumerate(moving):
            for bid,bp,b in moving[j+1:]:
                if not _z_overlap(a["z_interval_mm"],b["z_interval_mm"]): continue
                clr=hypot(ap[0]-bp[0],ap[1]-bp[1])-a["envelope_radius_mm"]-b["envelope_radius_mm"]
                motion.append({"sample_index":i,"component_a_id":aid,"component_b_id":bid,
                    "envelope_clearance_mm":clr,"screen":"INTERFERENCE" if clr<0 else "NO_ENVELOPE_OVERLAP"})
    meshes=[{"mesh_id":m["mesh_id"],**m["_evaluation"]} for m in data.get("gear_meshes",[])]
    return {"schema":"steward.c01.wp40.v1","candidate_id":data["candidate_id"],
        "static_clearance_screens":clearances,"motion_clearance_screens":motion,"gear_mesh_screens":meshes,
        "support_references":data.get("supports",[]),
        "screening_summary":{"static_interference_flags":sum(x["screen"]=="INTERFERENCE" for x in clearances),
          "motion_interference_flags":sum(x["screen"]=="INTERFERENCE" for x in motion),
          "gear_center_distance_failures":sum(not x["center_distance_pass"] for x in meshes)},
        "status":"LAYOUT_SCREENING_ONLY","physical_fit_certified":False,"design_selected":False,
        "architecture_frozen":False,"manufacturing_release":False,
        "limitations":["Circular XY envelopes are conservative placeholders, not detailed part solids.",
          "Static clearance is checked only for components with overlapping supplied Z intervals.",
          "Motion screening samples supplied poses and can miss collisions between samples.",
          "Gear center-distance check is nominal standard external spur geometry only; profile shift, backlash and tooth contact are not certified.",
          "Support references are checked for traceability only; no bearing load or structural stiffness is calculated.",
          "No swept-solid, tolerance-stack, deflection, shock, service-access or manufacturing verification."]}

def generate_openscad_envelopes(data):
    validate_layout(data)
    out=["// WP-40 candidate envelope visualization; NOT manufacturing CAD",
         f"// candidate={data['candidate_id']} evidence={data['evidence_id']} revision={data['source_revision']}",
         "$fn=48;"]
    for p in data["components"]:
        x,y=p["xy_mm"]; z0,z1=p["z_interval_mm"]
        out += [f"// {p['component_id']} role={p['role']} evidence={p['evidence_id']} source={p['source_revision']}",
          f"translate([{x:.12g},{y:.12g},{z0:.12g}]) cylinder(r={p['envelope_radius_mm']:.12g},h={z1-z0:.12g},center=false);"]
    return "\n".join(out)+"\n"
