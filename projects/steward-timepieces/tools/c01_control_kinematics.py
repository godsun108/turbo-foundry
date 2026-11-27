"""WP-44 evidence-gated planar control kinematics and CAD handoff.

This is a sampled rigid-body screening model, not a dynamic/contact solver.
All geometry and trajectories are explicit caller inputs with provenance.
"""
from __future__ import annotations
import math

class ControlKinematicsError(ValueError):
    pass

CANDIDATES={"column_wheel","cam_lever"}
STATES=("stopped_zero","running","stopped_retained")
COMMANDS={"start":("stopped_zero","running"),
          "stop":("running","stopped_retained"),
          "resume":("stopped_retained","running"),
          "reset":("stopped_retained","stopped_zero")}

def _number(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ControlKinematicsError(f"{name} must be finite")
    return float(v)

def _positive(v,name):
    x=_number(v,name)
    if x<=0: raise ControlKinematicsError(f"{name} must be positive")
    return x

def _required(row,fields,label):
    for f in fields:
        if not isinstance(row.get(f),str) or not row[f].strip():
            raise ControlKinematicsError(f"{label}.{f} is required")

def validate_candidate(candidate):
    if not isinstance(candidate,dict): raise ControlKinematicsError("candidate must be an object")
    _required(candidate,("candidate_id","control_type","evidence_id","source_revision","status"),"candidate")
    expected={"CW":"column_wheel","CL":"cam_lever"}
    if candidate["candidate_id"] not in expected or expected[candidate["candidate_id"]]!=candidate["control_type"]:
        raise ControlKinematicsError("candidate ID/type mismatch")
    if candidate["status"] not in ("concept","candidate","reviewed","approved"):
        raise ControlKinematicsError("invalid candidate status")
    members=candidate.get("members")
    if not isinstance(members,list) or not members: raise ControlKinematicsError("members must be non-empty")
    ids=[m.get("member_id") for m in members]
    if any(not isinstance(x,str) or not x.strip() for x in ids) or len(ids)!=len(set(ids)):
        raise ControlKinematicsError("member IDs must be unique")
    for m in members: _required(m,("function","evidence_id","source_revision"),"member")
    required={"pusher_input","index_or_state_retention","clutch_command",
      "stopped_retention_command","reset_hammer_command","running_reset_interlock","return_or_reset"}
    interfaces=candidate.get("interfaces")
    if not isinstance(interfaces,list) or not interfaces: raise ControlKinematicsError("interfaces must be non-empty")
    iids=[i.get("interface_id") for i in interfaces]
    if any(not isinstance(x,str) or not x.strip() for x in iids) or len(iids)!=len(set(iids)):
        raise ControlKinematicsError("interface IDs must be unique")
    kinds=set()
    for i in interfaces:
        _required(i,("interface_type","from_member_id","to_member_id","definition","evidence_id","source_revision"),"interface")
        if i["from_member_id"] not in ids or i["to_member_id"] not in ids or i["from_member_id"]==i["to_member_id"]:
            raise ControlKinematicsError("interface endpoints must be distinct declared members")
        kinds.add(i["interface_type"])
    missing=required-kinds
    if missing: raise ControlKinematicsError(f"missing interfaces: {sorted(missing)}")
    return {"candidate_id":candidate["candidate_id"],"member_count":len(members),
      "interface_count":len(interfaces),"complete":True,"winner_selected":False}

def validate_motion(motion):
    _required(motion,("candidate_id","evidence_id","source_revision","time_unit","length_unit"),"motion")
    if motion["candidate_id"] not in ("CW","CL"): raise ControlKinematicsError("candidate_id must be CW or CL")
    if motion["time_unit"]!="s" or motion["length_unit"]!="mm":
        raise ControlKinematicsError("WP-44 units are seconds and millimetres")
    samples=motion.get("samples")
    if not isinstance(samples,list) or len(samples)<2: raise ControlKinematicsError("at least two motion samples required")
    times=[_number(s.get("time_s"),"time_s") for s in samples]
    if any(b<=a for a,b in zip(times,times[1:])): raise ControlKinematicsError("sample times must strictly increase")
    members=motion.get("members")
    if not isinstance(members,list) or not members: raise ControlKinematicsError("motion members required")
    ids=[m.get("member_id") for m in members]
    if any(not isinstance(i,str) or not i.strip() for i in ids) or len(ids)!=len(set(ids)):
        raise ControlKinematicsError("motion member IDs must be unique")
    for m in members:
        _required(m,("role","geometry_type","evidence_id","source_revision"),"motion member")
        if m["geometry_type"] not in ("circle","capsule_envelope"): raise ControlKinematicsError("unsupported envelope geometry")
        _positive(m.get("radius_mm"),"radius_mm")
        poses=m.get("poses")
        if not isinstance(poses,list) or len(poses)!=len(samples): raise ControlKinematicsError("each member needs one pose per time sample")
        for p in poses:
            for f in ("x_mm","y_mm","angle_deg","z_min_mm","z_max_mm"):
                _number(p.get(f),f)
            if p["z_max_mm"]<=p["z_min_mm"]: raise ControlKinematicsError("pose Z interval must have positive thickness")
    constraints=motion.get("constraints",[])
    if not isinstance(constraints,list): raise ControlKinematicsError("constraints must be a list")
    for c in constraints:
        _required(c,("constraint_id","type","member_a","member_b","evidence_id","source_revision"),"constraint")
        if c["member_a"] not in ids or c["member_b"] not in ids or c["member_a"]==c["member_b"]:
            raise ControlKinematicsError("constraint endpoints must be distinct motion members")
        if c["type"]!="fixed_point_distance": raise ControlKinematicsError("only fixed_point_distance constraints are supported")
        for f in ("a_local_x_mm","a_local_y_mm","b_local_x_mm","b_local_y_mm","target_distance_mm","tolerance_mm"):
            _number(c.get(f),f)
        if c["target_distance_mm"]<0 or c["tolerance_mm"]<0: raise ControlKinematicsError("distance and tolerance must be non-negative")
    return {"sample_count":len(samples),"member_count":len(members),"constraint_count":len(constraints),
      "time_start_s":times[0],"time_end_s":times[-1],"validated":True}

def _point(pose,x,y):
    a=math.radians(pose["angle_deg"])
    return (pose["x_mm"]+x*math.cos(a)-y*math.sin(a),
            pose["y_mm"]+x*math.sin(a)+y*math.cos(a))

def evaluate_constraints(motion):
    validate_motion(motion)
    byid={m["member_id"]:m for m in motion["members"]}
    out=[]
    for c in motion.get("constraints",[]):
        errors=[]
        for k in range(len(motion["samples"])):
            a=_point(byid[c["member_a"]]["poses"][k],c["a_local_x_mm"],c["a_local_y_mm"])
            b=_point(byid[c["member_b"]]["poses"][k],c["b_local_x_mm"],c["b_local_y_mm"])
            d=math.hypot(a[0]-b[0],a[1]-b[1])
            errors.append(d-c["target_distance_mm"])
        peak=max(abs(e) for e in errors)
        out.append({"constraint_id":c["constraint_id"],"max_abs_error_mm":peak,
          "tolerance_mm":c["tolerance_mm"],"screen_pass":peak<=c["tolerance_mm"],
          "evidence_id":c["evidence_id"],"source_revision":c["source_revision"]})
    return {"constraints":out,"all_constraints_screen_pass":all(x["screen_pass"] for x in out),
      "physical_constraint_verified":False}

def evaluate_clearance(motion):
    validate_motion(motion)
    members=motion["members"]; results=[]
    for i,a in enumerate(members):
        for b in members[i+1:]:
            samples=[]
            for k in range(len(motion["samples"])):
                pa,pb=a["poses"][k],b["poses"][k]
                if min(pa["z_max_mm"],pb["z_max_mm"])<=max(pa["z_min_mm"],pb["z_min_mm"]):
                    continue
                d=math.hypot(pa["x_mm"]-pb["x_mm"],pa["y_mm"]-pb["y_mm"])
                samples.append(d-a["radius_mm"]-b["radius_mm"])
            if samples:
                j=min(range(len(samples)),key=samples.__getitem__)
                results.append({"member_a":a["member_id"],"member_b":b["member_id"],
                  "minimum_sampled_clearance_mm":samples[j],"overlap_detected":samples[j]<0,
                  "sampled_pair_pass":samples[j]>=0})
    return {"pairs":results,"sampled_pairs_clear":all(x["sampled_pair_pass"] for x in results),
      "continuous_swept_clearance_verified":False}

def validate_sequence(events):
    if not isinstance(events,list) or not events: raise ControlKinematicsError("events must be non-empty")
    state="stopped_zero"; trace=[state]
    for e in events:
        cmd=e.get("command")
        if cmd=="reset" and state=="running":
            if e.get("result")!="running" or not e.get("interlock_test_id"):
                raise ControlKinematicsError("running reset must remain running and cite physical interlock test")
            trace.append(state); continue
        expected=COMMANDS.get(cmd)
        if expected is None or expected[0]!=state or e.get("result")!=expected[1]:
            raise ControlKinematicsError(f"invalid command/state transition at {cmd}")
        state=expected[1]; trace.append(state)
    return {"state_trace":trace,"final_state":state,"logical_sequence_valid":True,
      "physical_sequence_verified":False}

def openscad_envelopes(motion):
    validate_motion(motion)
    rows=["// WP-44 envelope preview; generated from first supplied sample only.",
      "// Not a detailed solid, motion animation, or manufacturing model."]
    for m in motion["members"]:
        p=m["poses"][0]
        rows += [f"// {m['member_id']} | evidence={m['evidence_id']} | source={m['source_revision']}",
          f"translate([{p['x_mm']:.6f},{p['y_mm']:.6f},{p['z_min_mm']:.6f}]) cylinder(h={p['z_max_mm']-p['z_min_mm']:.6f}, r={m['radius_mm']:.6f}, $fn=48);"]
    return "\n".join(rows)+"\n"

def review(candidate,motion,events):
    c=validate_candidate(candidate); m=validate_motion(motion)
    if candidate["candidate_id"]!=motion["candidate_id"]: raise ControlKinematicsError("candidate/motion IDs do not match")
    seq=validate_sequence(events); con=evaluate_constraints(motion); clr=evaluate_clearance(motion)
    return {"candidate":c,"motion":m,"sequence":seq,"constraints":con,"clearance":clr,
      "architecture_winner_selected":False,"design_frozen":False,"prototype_release_authorized":False,
      "note":"A passing sampled screen is not physical verification or release authorization."}
