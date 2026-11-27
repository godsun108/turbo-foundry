"""WP-41 chronograph mechanism integration and assembly interface validator."""
from __future__ import annotations

class IntegrationInputError(ValueError):
    pass

REQUIRED_ROLES={"drive_source","clutch","central_seconds","minute_counter","hour_counter",
                "stopped_retention","control","reset_hammer","heart_cam"}
REQUIRED_INTERFACES={"drive_coupling","seconds_output","minute_counter_drive","hour_counter_drive",
                     "stopped_retention_control","clutch_control","reset_hammer_actuation",
                     "seconds_reset","minute_counter_reset","hour_counter_reset","running_reset_interlock"}
ALLOWED_STATES={"stopped_zero","running","stopped_retained"}

def _required(obj, fields, label):
    for f in fields:
        v=obj.get(f)
        if not isinstance(v,str) or not v.strip():
            raise IntegrationInputError(f"{label}.{f} is required")

def _unique(rows, key, label):
    vals=[r.get(key) for r in rows]
    if any(not isinstance(v,str) or not v.strip() for v in vals):
        raise IntegrationInputError(f"{label}.{key} is required")
    if len(vals)!=len(set(vals)): raise IntegrationInputError(f"{label}.{key} values must be unique")
    return set(vals)

def validate_assembly(data):
    if not isinstance(data,dict): raise IntegrationInputError("assembly must be an object")
    _required(data,("assembly_id","evidence_id","source_revision","architecture_status"),"assembly")
    if data["architecture_status"] not in ("candidate","selected_for_prototype","approved_baseline"):
        raise IntegrationInputError("invalid architecture_status")
    components=data.get("components")
    interfaces=data.get("interfaces")
    if not isinstance(components,list) or not components: raise IntegrationInputError("components must be non-empty")
    if not isinstance(interfaces,list) or not interfaces: raise IntegrationInputError("interfaces must be non-empty")
    cids=_unique(components,"component_id","component")
    _unique(interfaces,"interface_id","interface")
    roles=set()
    for c in components:
        _required(c,("role","evidence_id","source_revision"),f"component {c['component_id']}")
        roles.add(c["role"])
    missing=REQUIRED_ROLES-roles
    if missing: raise IntegrationInputError(f"missing required functional roles: {sorted(missing)}")
    kinds=set()
    byid={c["component_id"]:c for c in components}
    for i in interfaces:
        _required(i,("interface_type","from_component_id","to_component_id","definition","evidence_id","source_revision"),f"interface {i['interface_id']}")
        a=i["from_component_id"]; b=i["to_component_id"]
        if a not in cids or b not in cids or a==b: raise IntegrationInputError("interface endpoints must be distinct declared components")
        kinds.add(i["interface_type"])
        if not isinstance(i["definition"],str) or not i["definition"].strip(): raise IntegrationInputError("interface definition cannot be blank")
    missing_if=REQUIRED_INTERFACES-kinds
    if missing_if: raise IntegrationInputError(f"missing functional interfaces: {sorted(missing_if)}")
    decisions=data.get("open_decisions")
    if not isinstance(decisions,list) or not decisions: raise IntegrationInputError("open_decisions must preserve unresolved architecture choices")
    for d in decisions:
        _required(d,("decision_id","topic","status","evidence_id"),"open_decision")
        if d["status"] not in ("open","under_review","approved","deferred"): raise IntegrationInputError("invalid decision status")
    return {"component_count":len(components),"interface_count":len(interfaces),
        "functional_roles_present":sorted(roles),"functional_interfaces_present":sorted(kinds),
        "missing_roles":[],"missing_interfaces":[],"status":"INTERFACE_REGISTER_COMPLETE_NOT_PHYSICALLY_VERIFIED"}

def validate_transition(current, command, result, evidence=None):
    if current not in ALLOWED_STATES: raise IntegrationInputError("unknown current state")
    normal={("stopped_zero","start"):"running",
            ("running","stop"):"stopped_retained",
            ("stopped_retained","start"):"running",
            ("stopped_retained","reset"):"stopped_zero"}
    if current=="running" and command=="reset":
        if not isinstance(evidence,str) or not evidence.strip():
            raise IntegrationInputError("running reset block requires physical interlock evidence")
        if result!="running": raise IntegrationInputError("blocked reset must leave chronograph running")
        return {"accepted":True,"state":"running","reset_blocked":True,"evidence_id":evidence}
    expected=normal.get((current,command))
    if expected is None or result!=expected: raise IntegrationInputError("invalid state transition")
    return {"accepted":True,"state":result,"reset_blocked":False}

def validate_sequence(events):
    if not isinstance(events,list) or not events: raise IntegrationInputError("events must be non-empty")
    state="stopped_zero"; output=[]
    for index,event in enumerate(events):
        if not isinstance(event,dict): raise IntegrationInputError("each event must be an object")
        _required(event,("command","result"),f"event {index}")
        r=validate_transition(state,event["command"],event["result"],event.get("physical_interlock_evidence"))
        output.append({"event_index":index,**r})
        state=r["state"]
    return {"events":output,"final_state":state,"logical_sequence_valid":True,
            "physical_mechanism_verified":False}

def integration_review(data):
    base=validate_assembly(data)
    decisions=data["open_decisions"]
    open_items=[d["decision_id"] for d in decisions if d["status"]!="approved"]
    return {"assembly_id":data["assembly_id"],"interface_review":base,
        "open_decision_ids":open_items,"all_architecture_decisions_approved":not open_items,
        "prototype_release_authorized":False,"design_frozen":False,
        "status":"INTEGRATION_FRAMEWORK_COMPLETE_REVIEW_REQUIRED",
        "limitations":["Interface completeness does not prove dimensions, motion, timing or physical compatibility.",
          "No clutch, control, counter, brake, hammer or heart-cam architecture is selected.",
          "Logical state validation is not physical interlock verification.",
          "No forces, torques, gear ratios, contact stress, energy, wear or timing performance are calculated.",
          "No CAD assembly, swept-volume or tolerance analysis is performed."]}
