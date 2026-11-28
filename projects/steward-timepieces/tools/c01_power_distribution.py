"""WP-64 measured chronograph power distribution and dynamic load analysis.

This module reduces explicit, traceable measurements. It does not simulate
watch dynamics, infer missing torque/efficiency, or certify reserve/rate.
"""
from __future__ import annotations
from math import isfinite, pi
from typing import Any

def _num(v: Any, name: str, *, positive: bool = False, nonnegative: bool = False) -> float:
    try:
        x=float(v)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not isfinite(x): raise ValueError(f"{name} must be finite")
    if positive and x<=0: raise ValueError(f"{name} must be positive")
    if nonnegative and x<0: raise ValueError(f"{name} must be non-negative")
    return x

def _id(v: Any, name: str) -> str:
    if not isinstance(v,str) or not v.strip(): raise ValueError(f"{name} must be a non-empty identifier")
    return v

def shaft_power_w(torque_nm: Any, speed_rpm: Any) -> float:
    torque=_num(torque_nm,"torque_nm",nonnegative=True)
    speed=_num(speed_rpm,"speed_rpm",nonnegative=True)
    return torque*speed*2*pi/60

def integrate_power_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    """Trapezoidal integration of measured power versus elapsed seconds."""
    if not isinstance(samples,list) or len(samples)<2:
        raise ValueError("at least two power samples are required")
    points=[]
    for i,row in enumerate(samples):
        t=_num(row.get("time_s"),f"samples[{i}].time_s",nonnegative=True)
        p=_num(row.get("power_w"),f"samples[{i}].power_w",nonnegative=True)
        points.append((t,p))
    if any(b[0]<=a[0] for a,b in zip(points,points[1:])):
        raise ValueError("sample times must be strictly increasing")
    energy=sum((b[0]-a[0])*(a[1]+b[1])/2 for a,b in zip(points,points[1:]))
    return {"duration_s":points[-1][0]-points[0][0],"energy_j":energy,
            "mean_power_w":energy/(points[-1][0]-points[0][0]),
            "peak_sampled_power_w":max(p for _,p in points),
            "integration":"trapezoidal_between_measured_samples",
            "does_not_establish_unobserved_transients":True}

def _series(data: dict[str,Any], label: str) -> tuple[dict[str,str],list[dict[str,float]]]:
    meta={k:_id(data.get(k),f"{label}.{k}") for k in
          ("movement_revision","boundary_id","interval_id","test_condition_id","reserve_state_id")}
    rows=data.get("samples")
    if not isinstance(rows,list) or len(rows)<2: raise ValueError(f"{label}.samples requires at least two points")
    clean=[]
    for i,row in enumerate(rows):
        clean.append({"time_s":_num(row.get("time_s"),f"{label}.time_s",nonnegative=True),
                      "power_w":_num(row.get("power_w"),f"{label}.power_w",nonnegative=True)})
    if any(b["time_s"]<=a["time_s"] for a,b in zip(clean,clean[1:])):
        raise ValueError(f"{label} sample times must be strictly increasing")
    meta["evidence_id"]=_id(data.get("evidence_id"),f"{label}.evidence_id")
    return meta,clean

def compare_chronograph_conditions(stopped: dict[str,Any], running: dict[str,Any]) -> dict[str,Any]:
    """Paired off/on comparison; exact common time grid required."""
    m0,a=_series(stopped,"stopped")
    m1,b=_series(running,"running")
    if {k:v for k,v in m0.items() if k != "evidence_id"} != {k:v for k,v in m1.items() if k != "evidence_id"}:
        raise ValueError("stopped/running movement, boundary, interval, condition and reserve state must match")
    if [x["time_s"] for x in a] != [x["time_s"] for x in b]:
        raise ValueError("stopped/running samples must share identical timestamps")
    deltas=[{"time_s":x["time_s"],"incremental_power_w":y["power_w"]-x["power_w"]}
            for x,y in zip(a,b)]
    duration=a[-1]["time_s"]-a[0]["time_s"]
    incremental_energy=sum((deltas[i+1]["time_s"]-deltas[i]["time_s"])*
        (deltas[i]["incremental_power_w"]+deltas[i+1]["incremental_power_w"])/2
        for i in range(len(deltas)-1))
    return {"metadata":{k:v for k,v in m0.items() if k != "evidence_id"},\n            "stopped_evidence_id":m0["evidence_id"],"running_evidence_id":m1["evidence_id"],\n            "incremental_power_samples":deltas,
            "incremental_energy_j":incremental_energy,
            "mean_incremental_power_w":incremental_energy/duration,
            "peak_sampled_incremental_power_w":max(x["incremental_power_w"] for x in deltas),
            "interpretation":"paired measured difference; not an extrapolated reserve penalty"}

def evaluate_supply_demand(data: dict[str,Any]) -> dict[str,Any]:
    """Compare synchronized supply/demand at the same declared interface."""
    boundary=_id(data.get("boundary_id"),"boundary_id")
    state=_id(data.get("operating_state_id"),"operating_state_id")
    revision=_id(data.get("movement_revision"),"movement_revision")
    supply=_num(data.get("supply_power_w"),"supply_power_w",nonnegative=True)
    demand=_num(data.get("demand_power_w"),"demand_power_w",nonnegative=True)
    if not data.get("supply_evidence_id") or not data.get("demand_evidence_id"):
        raise ValueError("supply and demand evidence IDs are required")
    margin=supply-demand
    return {"boundary_id":boundary,"operating_state_id":state,"movement_revision":revision,
            "supply_power_w":supply,"demand_power_w":demand,"power_margin_w":margin,
            "supply_to_demand_ratio":None if demand==0 else supply/demand,
            "measured_margin_nonnegative":margin>=0,
            "does_not_prove_dynamic_transient_capacity":True}

def aggregate_load_ledger(loads: list[dict[str,Any]]) -> dict[str,Any]:
    if not isinstance(loads,list) or not loads: raise ValueError("loads must be a non-empty list")
    ids=[_id(x.get("load_id"),"load_id") for x in loads]
    if len(ids)!=len(set(ids)): raise ValueError("duplicate load IDs are prohibited")
    common={}
    for key in ("movement_revision","boundary_id","interval_id","test_condition_id","reserve_state_id"):
        vals={_id(x.get(key),key) for x in loads}
        if len(vals)!=1: raise ValueError(f"all loads must share {key}")
        common[key]=next(iter(vals))
    total=0.0
    rows=[]
    for x in loads:
        if not x.get("evidence_id"): raise ValueError("each load requires evidence_id")
        p=_num(x.get("power_w"),f"{x['load_id']}.power_w",nonnegative=True)
        total+=p
        rows.append({"load_id":x["load_id"],"power_w":p,"evidence_id":x["evidence_id"]})
    return {**common,"loads":rows,"total_power_w":total,"double_count_guard":"unique_load_ids"}

def analyze_event_window(samples: list[dict[str,Any]], event_start_s: Any,
                         event_end_s: Any) -> dict[str,Any]:
    """Integrate a sampled event window; boundaries must be actual sample times."""
    if not isinstance(samples,list) or len(samples)<2: raise ValueError("at least two samples required")
    clean=[{"time_s":_num(x.get("time_s"),"time_s",nonnegative=True),
            "power_w":_num(x.get("power_w"),"power_w",nonnegative=True)} for x in samples]
    if any(b["time_s"]<=a["time_s"] for a,b in zip(clean,clean[1:])):
        raise ValueError("sample times must be strictly increasing")
    start=_num(event_start_s,"event_start_s",nonnegative=True)
    end=_num(event_end_s,"event_end_s",positive=True)
    if end<=start: raise ValueError("event_end_s must exceed event_start_s")
    times=[x["time_s"] for x in clean]
    if start not in times or end not in times: raise ValueError("event boundaries must coincide with measured samples; no interpolation")
    i,j=times.index(start),times.index(end)
    result=integrate_power_samples(clean[i:j+1])
    return {**result,"event_start_s":start,"event_end_s":end,
            "event_boundary_basis":"measured samples only"}

def evaluate_timekeeping_delta(off: dict[str,Any], on: dict[str,Any],
                               max_abs_rate_delta_s_day: Any,
                               min_amplitude_deg: Any | None = None) -> dict[str,Any]:
    """Compare measured amplitude/rate deltas to caller-approved limits."""
    required=("movement_revision","test_condition_id","reserve_state_id","evidence_id")
    for key in required:
        if _id(off.get(key),f"off.{key}") != _id(on.get(key),f"on.{key}"):
            raise ValueError(f"off/on {key} must match")
    off_rate=_num(off.get("rate_s_day"),"off.rate_s_day")
    on_rate=_num(on.get("rate_s_day"),"on.rate_s_day")
    off_amp=_num(off.get("amplitude_deg"),"off.amplitude_deg",positive=True)
    on_amp=_num(on.get("amplitude_deg"),"on.amplitude_deg",positive=True)
    limit=_num(max_abs_rate_delta_s_day,"max_abs_rate_delta_s_day",nonnegative=True)
    delta=on_rate-off_rate
    result={"rate_delta_s_day":delta,"absolute_rate_delta_s_day":abs(delta),
            "rate_delta_within_supplied_limit":abs(delta)<=limit,
            "amplitude_delta_deg":on_amp-off_amp,
            "off_amplitude_deg":off_amp,"on_amplitude_deg":on_amp,
            "acceptance_is_provisional_until_approved":True}
    if min_amplitude_deg is not None:
        floor=_num(min_amplitude_deg,"min_amplitude_deg",positive=True)
        result["on_amplitude_meets_supplied_floor"]=on_amp>=floor
    else: result["on_amplitude_meets_supplied_floor"]=None
    return result

def analyze(data: dict[str,Any]) -> dict[str,Any]:
    """Integrated evidence reducer for a matched chronograph operating case."""
    stopped=data.get("chronograph_stopped")
    running=data.get("chronograph_running")
    comparison=compare_chronograph_conditions(stopped,running)
    supply_demand=evaluate_supply_demand(data.get("supply_demand"))
    ledger=aggregate_load_ledger(data.get("load_ledger"))
    return {"schema":"steward.c01.wp64.power-distribution.v1",
            "chronograph_increment":comparison,
            "supply_demand":supply_demand,
            "load_ledger":ledger,
            "physical_power_sufficiency_certified":False,
            "reserve_duration_estimated":False,
            "timekeeping_acceptance_granted":False,
            "limitations":[
                "Measured steady-state power does not prove transient torque capacity.",
                "Sampling can miss short impulses; bandwidth and sensor response require qualification.",
                "No missing losses, efficiency, reserve hours or oscillator response are inferred.",
                "Only matched movement revision, boundary, interval, test condition and reserve state are comparable."
            ]}
