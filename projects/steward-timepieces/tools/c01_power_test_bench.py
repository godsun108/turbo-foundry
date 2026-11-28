"""WP-65 evidence-gated chronograph power test-bench and instrumentation system.

Validates measurement plans and supplied records. It does not select hardware,
operate a bench, certify measurement capability, or authorize prototype tests.
"""
from __future__ import annotations
from math import isfinite, sqrt
from typing import Any

REQUIRED_CHANNEL_FIELDS = {
    "channel_id", "measurand", "unit", "measurement_boundary",
    "sensor_id", "instrument_id", "calibration_record_id",
    "calibration_status", "range_min", "range_max", "resolution",
    "bandwidth_hz", "sampling_method", "timebase_id",
    "evidence_id", "source_revision",
}
ALLOWED_ARCHITECTURES = {"column_wheel", "cam_lever"}
REQUIRED_POWER_MEASURANDS = {
    "torque", "rotational_speed", "barrel_torque_or_state",
    "balance_amplitude", "rate", "beat_error", "event_marker",
}

def _text(v: Any, name: str) -> str:
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{name} is required")
    return v

def _num(v: Any, name: str, *, positive=False, nonnegative=False) -> float:
    if isinstance(v, bool):
        raise ValueError(f"{name} must be finite numeric")
    try:
        x = float(v)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be finite numeric") from exc
    if not isfinite(x):
        raise ValueError(f"{name} must be finite numeric")
    if positive and x <= 0:
        raise ValueError(f"{name} must be positive")
    if nonnegative and x < 0:
        raise ValueError(f"{name} must be non-negative")
    return x

def validate_channel(channel: dict[str, Any]) -> dict[str, Any]:
    missing = REQUIRED_CHANNEL_FIELDS - set(channel)
    if missing:
        raise ValueError(f"channel missing fields: {sorted(missing)}")
    cid = _text(channel["channel_id"], "channel_id")
    for field in ("measurand", "unit", "measurement_boundary", "sensor_id",
                  "instrument_id", "calibration_record_id", "calibration_status",
                  "sampling_method", "timebase_id", "evidence_id", "source_revision"):
        _text(channel[field], f"{cid}.{field}")
    if channel["calibration_status"] != "current":
        raise ValueError(f"{cid}: calibration must be current for a released plan")
    lo = _num(channel["range_min"], f"{cid}.range_min")
    hi = _num(channel["range_max"], f"{cid}.range_max")
    resolution = _num(channel["resolution"], f"{cid}.resolution", positive=True)
    bandwidth = _num(channel["bandwidth_hz"], f"{cid}.bandwidth_hz", positive=True)
    if hi <= lo or resolution > hi - lo:
        raise ValueError(f"{cid}: invalid range or resolution")
    sample_rate = channel.get("sample_rate_hz")
    if sample_rate is not None:
        sample_rate = _num(sample_rate, f"{cid}.sample_rate_hz", positive=True)
        if sample_rate < 2 * bandwidth:
            raise ValueError(f"{cid}: sample rate is below the Nyquist minimum for declared bandwidth")
    if not channel.get("anti_alias_filter_id"):
        raise ValueError(f"{cid}: anti_alias_filter_id or documented filter disposition is required")
    if not channel.get("loading_assessment_id"):
        raise ValueError(f"{cid}: sensor loading assessment is required")
    return {"channel_id": cid, "measurand": channel["measurand"],
            "unit": channel["unit"], "measurement_boundary": channel["measurement_boundary"],
            "sample_rate_hz": sample_rate, "bandwidth_hz": bandwidth,
            "calibration_record_id": channel["calibration_record_id"],
            "channel_valid": True}

def validate_channel_register(channels: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(channels, list) or not channels:
        raise ValueError("channels must be a non-empty list")
    rows = [validate_channel(c) for c in channels]
    ids = [r["channel_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("channel IDs must be unique")
    return {"valid": True, "channel_count": len(rows), "channels": rows,
            "measurement_system_qualified": False}

def validate_power_measurement_plan(plan: dict[str, Any]) -> dict[str, Any]:
    for field in ("plan_id", "revision", "movement_revision", "fixture_revision",
                  "procedure_revision", "test_condition_id", "measurement_boundary",
                  "uncertainty_budget_id", "safety_review_id", "approver"):
        _text(plan.get(field), field)
    arch = plan.get("candidate_architecture")
    if arch not in ALLOWED_ARCHITECTURES:
        raise ValueError("candidate_architecture must be column_wheel or cam_lever")
    reg = validate_channel_register(plan.get("channels"))
    measurands = {c["measurand"] for c in reg["channels"]}
    missing = REQUIRED_POWER_MEASURANDS - measurands
    if missing:
        raise ValueError(f"power plan missing required measurands: {sorted(missing)}")
    if plan.get("status") != "approved":
        raise ValueError("plan must be approved before a hardware test can be considered")
    if plan.get("safety_review_status") != "approved":
        raise ValueError("safety review must be approved")
    return {"valid_for_independent_release_review": True,
            "candidate_architecture": arch, "channel_count": reg["channel_count"],
            "hardware_test_authorized": False,
            "measurement_system_qualified": False}

def validate_timebase_sync(sync: dict[str, Any]) -> dict[str, Any]:
    for field in ("sync_id", "reference_timebase_id", "method", "evidence_id", "source_revision"):
        _text(sync.get(field), field)
    offset = _num(sync.get("measured_offset_s"), "measured_offset_s")
    drift = _num(sync.get("measured_drift_s_per_s"), "measured_drift_s_per_s")
    uncertainty = _num(sync.get("expanded_time_uncertainty_s"), "expanded_time_uncertainty_s",
                       nonnegative=True)
    if sync.get("verification_status") != "verified":
        raise ValueError("timebase synchronization must be verified")
    return {"sync_id": sync["sync_id"], "offset_s": offset, "drift_s_per_s": drift,
            "expanded_time_uncertainty_s": uncertainty,
            "raw_timestamps_preserved": sync.get("raw_timestamps_preserved") is True,
            "sync_verified": True}

def combine_uncertainty(budget: dict[str, Any]) -> dict[str, Any]:
    _text(budget.get("measurand"), "measurand")
    _text(budget.get("unit"), "unit")
    _text(budget.get("method_reference"), "method_reference")
    if budget.get("independence_justified") is not True:
        raise ValueError("RSS combination requires an explicit justified independence assumption")
    parts = budget.get("components")
    if not isinstance(parts, list) or not parts:
        raise ValueError("at least one uncertainty component is required")
    ids, total = set(), 0.0
    for part in parts:
        pid = _text(part.get("component_id"), "component_id")
        if pid in ids:
            raise ValueError("uncertainty component IDs must be unique")
        ids.add(pid)
        u = _num(part.get("standard_uncertainty"), f"{pid}.standard_uncertainty",
                 nonnegative=True)
        sensitivity = _num(part.get("sensitivity_coefficient", 1), f"{pid}.sensitivity_coefficient")
        _text(part.get("source_or_rationale"), f"{pid}.source_or_rationale")
        total += (u * sensitivity) ** 2
    uc = sqrt(total)
    k = _num(budget.get("coverage_factor"), "coverage_factor", positive=True)
    return {"combined_standard_uncertainty": sqrt(total), "coverage_factor": k,
            "expanded_uncertainty": k * uc, "unit": budget["unit"],
            "independence_assumption": "explicitly_justified",
            "approved": budget.get("approved") is True}

def validate_raw_channel_samples(samples: list[dict[str, Any]], channel_id: str) -> dict[str, Any]:
    _text(channel_id, "channel_id")
    if not isinstance(samples, list) or len(samples) < 2:
        raise ValueError("at least two raw samples are required")
    clean, previous = [], None
    for index, row in enumerate(samples):
        t = _num(row.get("time_s"), f"{channel_id}[{index}].time_s", nonnegative=True)
        value = _num(row.get("value"), f"{channel_id}[{index}].value")
        if previous is not None and t <= previous:
            raise ValueError("raw sample timestamps must strictly increase")
        previous = t
        clean.append({"time_s": t, "value": value})
    return {"channel_id": channel_id, "samples": clean,
            "raw_samples_unchanged_by_validator": True}

def validate_run_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    for field in ("run_id", "candidate_id", "candidate_architecture", "candidate_revision",
                  "movement_revision", "fixture_revision", "procedure_revision",
                  "test_condition_id", "reserve_state_id", "boundary_id", "interval_id",
                  "timebase_sync_id", "raw_data_uri", "raw_data_sha256", "evidence_id",
                  "source_revision", "operator_id", "started_at_utc"):
        _text(manifest.get(field), field)
    if manifest["candidate_architecture"] not in ALLOWED_ARCHITECTURES:
        raise ValueError("invalid candidate architecture")
    digest = manifest["raw_data_sha256"].lower()
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("raw_data_sha256 must be a 64-character hexadecimal SHA-256")
    if manifest.get("raw_data_immutable") is not True:
        raise ValueError("raw evidence must be preserved immutable")
    return {"valid": True, "run_id": manifest["run_id"],
            "candidate_architecture": manifest["candidate_architecture"],
            "raw_data_integrity_declared": True, "test_authorized": False}

def validate_matched_pair(stopped: dict[str, Any], running: dict[str, Any]) -> dict[str, Any]:
    fields = ("movement_revision", "fixture_revision", "procedure_revision",
              "test_condition_id", "reserve_state_id", "boundary_id", "interval_id",
              "timebase_sync_id")
    for label, record in (("stopped", stopped), ("running", running)):
        for field in fields:
            _text(record.get(field), f"{label}.{field}")
    if any(stopped[f] != running[f] for f in fields):
        raise ValueError("stopped/running records must share configuration, boundary and condition")
    if stopped.get("run_id") == running.get("run_id"):
        raise ValueError("stopped and running records require distinct run IDs")
    if stopped.get("candidate_architecture") != running.get("candidate_architecture"):
        raise ValueError("paired records must refer to the same candidate architecture")
    return {"comparable_metadata": True, "candidate_architecture": stopped["candidate_architecture"],
            "physical_comparability_proven": False}

def release_review_gates(record: dict[str, Any]) -> dict[str, Any]:
    required = ("requirements_approved", "configuration_approved", "procedure_approved",
                "instrument_calibration_current", "uncertainty_budget_approved",
                "timebase_verified", "safety_review_approved", "independent_review_complete")
    missing = [field for field in required if record.get(field) is not True]
    return {"ready_for_authority_review": not missing, "open_gates": missing,
            "hardware_test_authorized": False, "prototype_release_authorized": False}
