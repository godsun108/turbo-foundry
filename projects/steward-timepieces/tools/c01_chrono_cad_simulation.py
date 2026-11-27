"""WP-35 evidence-gated chronograph envelope CAD and motion screening."""
from __future__ import annotations
from math import hypot, isfinite
from typing import Any

def _num(v: Any, name: str, positive: bool = False) -> float:
    if isinstance(v, bool):
        raise ValueError(f"{name} must be numeric")
    try:
        x = float(v)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not isfinite(x) or (positive and x <= 0):
        raise ValueError(f"{name} must be finite" + (" and positive" if positive else ""))
    return x

def validate_assembly(config: dict[str, Any]) -> dict[str, Any]:
    if not config.get("candidate_id") or not config.get("evidence_id") or not config.get("source_revision"):
        raise ValueError("candidate and global provenance are required")
    bodies = config.get("bodies")
    if not isinstance(bodies, list) or not bodies:
        raise ValueError("bodies must be a non-empty list")
    ids = set()
    for b in bodies:
        for f in ("id", "kind", "radius_mm", "z_min_mm", "z_max_mm", "evidence_id", "source_revision"):
            if not b.get(f) and b.get(f) != 0:
                raise ValueError(f"body requires {f}")
        if b["id"] in ids:
            raise ValueError("body IDs must be unique")
        ids.add(b["id"])
        if b["kind"] not in ("fixed", "rotating", "translating", "envelope_only"):
            raise ValueError("unsupported body kind")
        _num(b["radius_mm"], b["id"] + ".radius_mm", True)
        z0, z1 = _num(b["z_min_mm"], "z_min"), _num(b["z_max_mm"], "z_max")
        if z1 <= z0:
            raise ValueError("body axial interval must have positive extent")
        if not isinstance(b.get("poses"), list) or not b["poses"]:
            raise ValueError("each body requires explicit sampled poses")
        for p in b["poses"]:
            _num(p.get("x_mm"), "pose.x")
            _num(p.get("y_mm"), "pose.y")
            _num(p.get("angle_deg", 0), "pose.angle_deg")
    return {"candidate_id": config["candidate_id"], "body_count": len(bodies),
            "geometry_is_explicit": True, "physical_fit_certified": False}

def screen_motion_clearance(config: dict[str, Any]) -> dict[str, Any]:
    validate_assembly(config)
    bodies = config["bodies"]
    # Samples are compared by index; asynchronous trajectories must be resampled
    # to a common time base by the engineer before evaluation.
    count = min(len(b["poses"]) for b in bodies)
    if any(len(b["poses"]) != count for b in bodies):
        raise ValueError("all body trajectories must use the same sample count/time base")
    pairs = []
    for i, a in enumerate(bodies):
        for b in bodies[i+1:]:
            if min(a["z_max_mm"], b["z_max_mm"]) <= max(a["z_min_mm"], b["z_min_mm"]):
                continue
            minimum = None
            min_sample = None
            for k in range(count):
                pa, pb = a["poses"][k], b["poses"][k]
                center = hypot(float(pa["x_mm"])-float(pb["x_mm"]),
                               float(pa["y_mm"])-float(pb["y_mm"]))
                clearance = center-float(a["radius_mm"])-float(b["radius_mm"])
                if minimum is None or clearance < minimum:
                    minimum, min_sample = clearance, k
            pairs.append({"body_a": a["id"], "body_b": b["id"],
                          "minimum_sampled_clearance_mm": minimum,
                          "sample_index": min_sample,
                          "sampled_interference": minimum < 0})
    return {"sample_count": count, "pair_results": pairs,
            "sampled_interference_found": any(p["sampled_interference"] for p in pairs),
            "continuous_motion_proven": False,
            "note": "Sampled circular-envelope screening only; not swept-solid CAD or tolerance certification."}

def generate_envelope_scad(config: dict[str, Any]) -> str:
    validate_assembly(config)
    lines = ["// WP-35 candidate envelope visualization only",
             "// Not a manufacturing model; all geometry is sourced input.",
             f"// Candidate: {config['candidate_id']}",
             f"// Evidence: {config['evidence_id']}",
             f"// Source revision: {config['source_revision']}", "$fn=48;", ""]
    for b in config["bodies"]:
        lines += [f"// {b['id']} | {b['kind']} | {b['evidence_id']}",
                  f"translate([{b['poses'][0]['x_mm']}, {b['poses'][0]['y_mm']}, {b['z_min_mm']}])",
                  f"cylinder(h={float(b['z_max_mm'])-float(b['z_min_mm'])}, r={b['radius_mm']});", ""]
    return "\n".join(lines)

def validate_sequence(sequence: list[dict[str, Any]]) -> dict[str, Any]:
    required = ["stopped_zero", "running", "stopped_retained", "running", "stopped_zero"]
    if not isinstance(sequence, list) or [x.get("state") for x in sequence] != required:
        raise ValueError("sequence must cover zero, start, stop, resume and reset states in order")
    commands = ["initial", "start", "stop", "start", "reset"]
    if [x.get("command") for x in sequence] != commands:
        raise ValueError("commands do not match required functional sequence")
    if sequence[-1].get("reset_interlock_test_id") is None:
        raise ValueError("physical reset interlock test reference required")
    return {"sequence_steps": len(sequence), "logical_sequence_valid": True,
            "physical_sequence_verified": False}
