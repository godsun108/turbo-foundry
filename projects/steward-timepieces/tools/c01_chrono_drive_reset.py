"""WP-34 explicit chronograph drive-path and reset-work calculations."""
from fractions import Fraction
from typing import Any

def _q(value: Any, name: str, positive: bool = False) -> Fraction:
    try:
        x = Fraction(str(value))
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise ValueError(f"{name} must be rational") from exc
    if positive and x <= 0:
        raise ValueError(f"{name} must be positive")
    return x

def evaluate_drive_path(source_rpm: Any, stages: list[dict[str, Any]]) -> dict[str, Any]:
    rpm = _q(source_rpm, "source_rpm", True)
    if not isinstance(stages, list) or not stages:
        raise ValueError("at least one explicitly defined mesh stage is required")
    ratio = Fraction(1)
    for i, stage in enumerate(stages):
        for field in ("driver_teeth", "driven_teeth", "mesh_type", "evidence_id"):
            if field not in stage or stage[field] in (None, ""):
                raise ValueError(f"stage {i} requires {field}")
        a, b = stage["driver_teeth"], stage["driven_teeth"]
        if any(isinstance(v, bool) or not isinstance(v, int) or v <= 0 for v in (a, b)):
            raise ValueError("tooth counts must be positive integers")
        if stage["mesh_type"] not in ("external", "internal"):
            raise ValueError("mesh_type must be external or internal")
        ratio *= Fraction(a, b) * (-1 if stage["mesh_type"] == "external" else 1)
    out = rpm * ratio
    return {"source_rpm": str(rpm), "signed_ratio": str(ratio),
            "output_rpm": str(out), "direction": "same" if out > 0 else "opposite",
            "stage_count": len(stages), "candidate_only": True}

def evaluate_branch(source_rpm: Any, stages: list[dict[str, Any]],
                    target_period_seconds: Any, tolerance_fraction: Any) -> dict[str, Any]:
    path = evaluate_drive_path(source_rpm, stages)
    target = Fraction(60, 1) / _q(target_period_seconds, "target_period_seconds", True)
    tolerance = _q(tolerance_fraction, "tolerance_fraction")
    if tolerance < 0 or tolerance >= 1:
        raise ValueError("tolerance_fraction must be in [0,1)")
    actual = abs(Fraction(path["output_rpm"]))
    error = abs(actual - target) / target
    return {**path, "target_rpm": str(target), "absolute_fractional_error": str(error),
            "passes_supplied_tolerance": error <= tolerance}

def reset_work_from_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(samples, list) or len(samples) < 2:
        raise ValueError("at least two measured torque-angle samples are required")
    points = []
    for i, row in enumerate(samples):
        for field in ("angle_rad", "torque_nm", "evidence_id"):
            if field not in row or row[field] in (None, ""):
                raise ValueError(f"sample {i} requires {field}")
        angle = _q(row["angle_rad"], "angle_rad")
        torque = _q(row["torque_nm"], "torque_nm")
        if torque < 0:
            raise ValueError("measured resisting torque cannot be negative")
        if not isinstance(row["evidence_id"], str) or not row["evidence_id"].strip():
            raise ValueError("each sample requires evidence")
        points.append((angle, torque))
    if any(points[i][0] <= points[i-1][0] for i in range(1, len(points))):
        raise ValueError("sample angles must be strictly increasing")
    work = sum((points[i][1] + points[i-1][1]) *
               (points[i][0] - points[i-1][0]) / 2
               for i in range(1, len(points)))
    return {"measured_reset_work_j": str(work), "sample_count": len(points),
            "method": "trapezoidal integration of measured torque versus angle",
            "extrapolated": False}

def compare_reset_energy(reset_work_j: Any, available_energy_j: Any,
                         boundary_id: str, evidence_id: str) -> dict[str, Any]:
    if not boundary_id or not evidence_id:
        raise ValueError("matched measurement boundary and evidence are required")
    work = _q(reset_work_j, "reset_work_j")
    available = _q(available_energy_j, "available_energy_j")
    if work < 0 or available < 0:
        raise ValueError("energies cannot be negative")
    margin = available - work
    return {"reset_work_j": str(work), "available_energy_j": str(available),
            "energy_margin_j": str(margin), "nonnegative_margin": margin >= 0,
            "boundary_id": boundary_id, "evidence_id": evidence_id,
            "losses_and_dynamic_peaks_included": False,
            "note": "Screening comparison only; not a reset-force, dynamic, or reliability proof."}

def validate_reset_definition(record: dict[str, Any]) -> dict[str, Any]:
    fields = ("definition_id", "heart_cam_drawing", "hammer_drawing",
              "zero_datum", "contact_sequence", "spring_return_definition",
              "hand_retention_definition", "clearance_review",
              "tolerance_review", "evidence_id", "review_status")
    for field in fields:
        if not record.get(field):
            raise ValueError(f"{field} is required")
    if record["review_status"] not in ("draft", "reviewed", "approved"):
        raise ValueError("invalid review_status")
    return {"definition_id": record["definition_id"],
            "complete_record": True, "approved": record["review_status"] == "approved",
            "physical_design_certified": False}
