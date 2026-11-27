"""WP-42 column-wheel and cam/lever control-system engineering validators."""
from __future__ import annotations

class ControlDesignError(ValueError):
    pass

CANDIDATES={"column_wheel","cam_lever"}
REQUIRED_FUNCTIONS={"start","stop","resume","reset"}
REQUIRED_CONTROL_INTERFACES={"pusher_input","index_or_state_retention","clutch_command",
 "stopped_retention_command","reset_hammer_command","running_reset_interlock","return_or_reset"}

def _req(row, fields, label):
    for f in fields:
        v=row.get(f)
        if not isinstance(v,str) or not v.strip():
            raise ControlDesignError(f"{label}.{f} is required")

def validate_control_definition(d):
    if not isinstance(d,dict): raise ControlDesignError("control definition must be an object")
    _req(d,("candidate_id","control_type","evidence_id","source_revision","status"),"candidate")
    if d["candidate_id"] not in ("CW","CL"): raise ControlDesignError("candidate_id must be CW or CL")
    expected={"CW":"column_wheel","CL":"cam_lever"}[d["candidate_id"]]
    if d["control_type"]!=expected: raise ControlDesignError("candidate ID and control type mismatch")
    if d["status"] not in ("concept","candidate","reviewed","approved"): raise ControlDesignError("invalid status")
    members=d.get("members")
    if not isinstance(members,list) or not members: raise ControlDesignError("members must be non-empty")
    ids=[m.get("member_id") for m in members]
    if any(not isinstance(x,str) or not x.strip() for x in ids) or len(ids)!=len(set(ids)):
        raise ControlDesignError("member IDs must be unique and non-empty")
    for m in members:
        _req(m,("function","evidence_id","source_revision"),f"member {m.get('member_id')}")
    interfaces=d.get("interfaces")
    if not isinstance(interfaces,list) or not interfaces: raise ControlDesignError("interfaces must be non-empty")
    iids=[i.get("interface_id") for i in interfaces]
    if any(not isinstance(x,str) or not x.strip() for x in iids) or len(iids)!=len(set(iids)):
        raise ControlDesignError("interface IDs must be unique and non-empty")
    types=set()
    for i in interfaces:
        _req(i,("interface_type","from_member_id","to_member_id","definition","evidence_id","source_revision"),"interface")
        if i["from_member_id"] not in ids or i["to_member_id"] not in ids or i["from_member_id"]==i["to_member_id"]:
            raise ControlDesignError("interface endpoints must reference distinct declared members")
        types.add(i["interface_type"])
    missing=REQUIRED_CONTROL_INTERFACES-types
    if missing: raise ControlDesignError(f"missing control interfaces: {sorted(missing)}")
    return {"candidate_id":d["candidate_id"],"control_type":d["control_type"],
      "member_count":len(members),"interface_count":len(interfaces),
      "missing_interface_types":[],"physical_control_verified":False}

def validate_state_table(rows):
    if not isinstance(rows,list) or len(rows)!=4: raise ControlDesignError("exactly four command rows are required")
    expected={"start":("stopped_zero","running"),"stop":("running","stopped_retained"),
      "resume":("stopped_retained","running"),"reset":("stopped_retained","stopped_zero")}
    commands=[r.get("command") for r in rows]
    if set(commands)!=REQUIRED_FUNCTIONS or len(set(commands))!=4:
        raise ControlDesignError("start, stop, resume and reset must each appear exactly once")
    for r in rows:
        cmd=r["command"]
        if (r.get("from_state"),r.get("to_state"))!=expected[cmd]:
            raise ControlDesignError(f"invalid state definition for {cmd}")
        _req(r,("actuation_sequence","completion_condition","evidence_id"),cmd)
    return {"command_count":4,"state_table_valid":True}

def validate_running_reset_interlock(record):
    _req(record,("candidate_id","physical_interlock_type","blocking_member_id",
       "blocked_motion","proof_test_id","evidence_id","source_revision"),"interlock")
    if record["candidate_id"] not in ("CW","CL"): raise ControlDesignError("unknown candidate")
    if record["blocked_motion"]!="reset_hammer_contact": raise ControlDesignError("interlock must block reset hammer contact")
    return {"interlock_definition_complete":True,"physical_interlock_pass":False,
      "proof_test_required":True,"note":"Definition completeness is not a successful physical test."}

def compare_candidates(column_wheel, cam_lever):
    a=validate_control_definition(column_wheel); b=validate_control_definition(cam_lever)
    if a["candidate_id"]!="CW" or b["candidate_id"]!="CL":
        raise ControlDesignError("comparison requires CW then CL")
    return {"candidates":["CW","CL"],"winner_selected":False,
      "comparison_status":"STRUCTURAL_COMPARISON_ONLY",
      "candidate_summaries":{"CW":a,"CL":b},
      "required_evidence":["indexed-state repeatability","actuation force versus travel",
        "partial-pusher-actuation behavior","clutch and brake phase margin",
        "reset interlock proof","wear and lubrication assessment","assembly/service repeatability"],
      "decision_authorized":False}

def evaluate_control_review(record):
    _req(record,("review_id","candidate_id","test_procedure_revision","configuration_revision",
       "measurement_boundary","instrument_register_id","review_status"),"review")
    if record["candidate_id"] not in ("CW","CL"): raise ControlDesignError("unknown candidate")
    required={"actuation_force_travel","state_repeatability","partial_actuation",
      "clutch_phase","retention_phase","reset_interlock","wear_inspection","serviceability"}
    measures=record.get("measurements")
    if not isinstance(measures,list) or set(measures)!=required:
        raise ControlDesignError("review must include every required measurement domain")
    if record["review_status"] not in ("draft","reviewed","approved"): raise ControlDesignError("invalid review status")
    return {"review_id":record["review_id"],"measurement_count":len(measures),
      "review_approved":record["review_status"]=="approved","architecture_selected":False}

