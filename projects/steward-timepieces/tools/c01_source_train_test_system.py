"""WP-66 instrumented mainspring/barrel/going-train test-system validation.

Evidence and measurement-plan validation only. No hardware is operated,
no missing measurements are inferred, and no reserve duration is predicted.
"""
from __future__ import annotations
from math import isfinite
from typing import Any

REQUIRED_CHANNELS = {
    "barrel_torque", "barrel_angle_or_state", "barrel_speed",
    "going_train_input_torque", "going_train_input_speed",
    "going_train_output_speed", "balance_amplitude", "rate", "beat_error",
    "temperature", "event_marker",
}
ALLOWED_CANDIDATES = {"column_wheel", "cam_lever"}

def _text(v: Any, name: str) -> str:
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{name} is required")
    return v

def _num(v: Any, name: str, *, positive=False, nonnegative=False) -> float:
    if isinstance(v, bool):
        raise ValueError(f"{name} must be numeric")
    try:
        x = float(v)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not isfinite(x):
        raise ValueError(f"{name} must be finite")
    if positive and x <= 0:
        raise ValueError(f"{name} must be positive")
    if nonnegative and x < 0:
        raise ValueError(f"{name} must be non-negative")
    return x

def validate_channel_register(channels: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(channels, list) or not channels:
        raise ValueError("channels must be a non-empty list")
    ids, kinds = [], set()
    normalized = []
    required = ("channel_id", "measurand", "unit", "boundary_id", "sensor_id",
                "instrument_id", "calibration_record_id", "calibration_status",
                "range_min", "range_max", "resolution", "bandwidth_hz",
                "sample_method", "timebase_id", "evidence_id", "source_revision",
                "loading_assessment_id", "anti_alias_disposition")
    for c in channels:
        for f in required:
            _text(c.get(f), f)
        cid = c["channel_id"]
        ids.append(cid); kinds.add(c["measurand"])
        if c["calibration_status"] != "current":
            raise ValueError(f"{cid}: calibration must be current")
        lo = _num(c["range_min"], f"{cid}.range_min")
        hi = _num(c["range_max"], f"{cid}.range_max")
        _num(c["resolution"], f"{cid}.resolution", positive=True)
        bw = _num(c["bandwidth_hz"], f"{cid}.bandwidth_hz", positive=True)
        if hi <= lo:
            raise ValueError(f"{cid}: range_max must exceed range_min")
        rate = c.get("sample_rate_hz")
        if rate is not None and _num(rate, f"{cid}.sample_rate_hz", positive=True) < 2*bw:
            raise ValueError(f"{cid}: sample rate below Nyquist minimum")
        normalized.append({"channel_id":cid,"measurand":c["measurand"],
                           "boundary_id":c["boundary_id"],"bandwidth_hz":bw})
    if len(ids) != len(set(ids)):
        raise ValueError("channel IDs must be unique")
    missing = REQUIRED_CHANNELS - kinds
    return {"channel_count":len(ids),"measurands":sorted(kinds),
            "missing_measurands":sorted(missing),"channels":normalized,
            "complete_for_full_campaign":not missing}

def validate_campaign(plan: dict[str, Any]) -> dict[str, Any]:
    for f in ("campaign_id","revision","movement_revision","fixture_revision",
              "procedure_revision","test_condition_id","datum_frame_id",
              "timebase_sync_id","uncertainty_budget_id","safety_review_id",
              "approver","source_revision"):
        _text(plan.get(f),f)
    if plan.get("candidate_architecture") not in ALLOWED_CANDIDATES:
        raise ValueError("candidate_architecture must be column_wheel or cam_lever")
    reg = validate_channel_register(plan.get("channels"))
    if not reg["complete_for_full_campaign"]:
        raise ValueError(f"missing campaign measurands: {reg['missing_measurands']}")
    if plan.get("status") != "approved" or plan.get("safety_review_status") != "approved":
        raise ValueError("campaign and safety review must be approved")
    return {"campaign_valid_for_independent_review":True,
            "candidate_architecture":plan["candidate_architecture"],
            "channel_count":reg["channel_count"],
            "hardware_test_authorized":False,"reserve_duration_established":False}

def validate_barrel_curve(samples: list[dict[str, Any]], evidence_id: str,
                          source_revision: str) -> dict[str, Any]:
    _text(evidence_id,"evidence_id"); _text(source_revision,"source_revision")
    if not isinstance(samples,list) or len(samples)<2:
        raise ValueError("at least two measured barrel samples are required")
    out=[]; previous=None; energy=0.0
    for i,s in enumerate(samples):
        angle=_num(s.get("angle_rad"),f"samples[{i}].angle_rad",nonnegative=True)
        torque=_num(s.get("torque_nm"),f"samples[{i}].torque_nm",nonnegative=True)
        if previous is not None:
            if angle <= previous[0]:
                raise ValueError("barrel angle must strictly increase")
            energy += (previous[1]+torque)*0.5*(angle-previous[0])
        out.append({"angle_rad":angle,"torque_nm":torque})
        previous=(angle,torque)
    return {"sample_count":len(out),"integrated_energy_j":energy,
            "evidence_id":evidence_id,"source_revision":source_revision,
            "integration":"trapezoidal_measured_torque_angle",
            "reserve_hours_inferred":False}

def validate_reserve_profile(states: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(states,list) or not states:
        raise ValueError("reserve states must be a non-empty list")
    ids=[]; previous=None; rows=[]
    for i,s in enumerate(states):
        sid=_text(s.get("state_id"),f"states[{i}].state_id"); ids.append(sid)
        fraction=_num(s.get("measured_state_fraction"),f"{sid}.measured_state_fraction",
                      nonnegative=True)
        if fraction>1:
            raise ValueError("measured_state_fraction must be within 0..1")
        _text(s.get("evidence_id"),f"{sid}.evidence_id")
        _text(s.get("source_revision"),f"{sid}.source_revision")
        if previous is not None and fraction >= previous:
            raise ValueError("reserve-state fractions must strictly descend")
        previous=fraction
        for field in ("barrel_torque_nm","barrel_speed_rpm","amplitude_deg","rate_s_per_day"):
            _num(s.get(field),f"{sid}.{field}")
        rows.append({"state_id":sid,"measured_state_fraction":fraction})
    if len(ids)!=len(set(ids)):
        raise ValueError("reserve state IDs must be unique")
    return {"state_count":len(rows),"states":rows,
            "continuous_reserve_curve_inferred":False,
            "hours_remaining_established":False}

def validate_train_speed_series(samples: list[dict[str, Any]], evidence_id: str,
                                source_revision: str) -> dict[str, Any]:
    _text(evidence_id,"evidence_id"); _text(source_revision,"source_revision")
    if not isinstance(samples,list) or len(samples)<2:
        raise ValueError("at least two synchronized samples are required")
    previous=None; rows=[]
    for i,s in enumerate(samples):
        t=_num(s.get("time_s"),f"samples[{i}].time_s",nonnegative=True)
        input_rpm=_num(s.get("input_speed_rpm"),f"samples[{i}].input_speed_rpm",nonnegative=True)
        output_rpm=_num(s.get("output_speed_rpm"),f"samples[{i}].output_speed_rpm",nonnegative=True)
        if previous is not None and t<=previous:
            raise ValueError("sample times must strictly increase")
        previous=t; rows.append({"time_s":t,"input_speed_rpm":input_rpm,
                                 "output_speed_rpm":output_rpm})
    return {"sample_count":len(rows),"samples":rows,"evidence_id":evidence_id,
            "source_revision":source_revision,"ratio_inferred":False}

def validate_energy_comparison(source: dict[str, Any], demand: dict[str, Any]) -> dict[str, Any]:
    fields=("movement_revision","boundary_id","interval_id","test_condition_id",
            "reserve_state_id","timebase_sync_id")
    for label,r in (("source",source),("demand",demand)):
        for f in fields: _text(r.get(f),f"{label}.{f}")
        _text(r.get("evidence_id"),f"{label}.evidence_id")
        _num(r.get("measured_energy_j"),f"{label}.measured_energy_j",nonnegative=True)
    if any(source[f]!=demand[f] for f in fields):
        raise ValueError("source and demand must share revision, boundary, interval and condition")
    if source["evidence_id"]==demand["evidence_id"]:
        raise ValueError("source and demand require distinct evidence records")
    margin=source["measured_energy_j"]-demand["measured_energy_j"]
    return {"measured_energy_difference_j":margin,
            "metadata_matched":True,"physical_power_sufficiency_proven":False,
            "reserve_duration_established":False}

def release_gates(record: dict[str, Any]) -> dict[str, Any]:
    gates=("requirements_approved","movement_configuration_approved",
           "fixture_qualified","instruments_calibrated","channel_register_approved",
           "timebase_verified","uncertainty_budget_approved","procedure_approved",
           "safety_review_approved","independent_review_complete")
    missing=[g for g in gates if record.get(g) is not True]
    return {"ready_for_authority_review":not missing,"open_gates":missing,
            "hardware_test_authorized":False,"prototype_release_authorized":False}
