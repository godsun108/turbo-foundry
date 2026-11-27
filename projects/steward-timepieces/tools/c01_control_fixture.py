"""WP-47 parametric fixture input validation and OpenSCAD source generation.

The model creates reviewable fixture envelopes from explicit, traceable inputs.
It does not infer dimensions, certify fit, or authorize hardware construction.
"""
from __future__ import annotations

from math import acos, degrees, isfinite, sqrt
import re
from typing import Any

ARCHITECTURES = {"column_wheel", "cam_lever"}
REQUIRED_MOUNT_ROLES = {
    "pusher_actuator", "force_transducer", "travel_sensor", "optical_view"
}


def _finite(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and isfinite(v)


def _vec(values: Any, size: int, label: str) -> list[float]:
    if not isinstance(values, (list, tuple)) or len(values) != size or not all(_finite(v) for v in values):
        raise ValueError(f"{label} must contain {size} finite numbers")
    return [float(v) for v in values]


def _unit(v: list[float]) -> list[float]:
    n = sqrt(sum(x*x for x in v))
    if n <= 0:
        raise ValueError("axis vector must be nonzero")
    return [x/n for x in v]


def _polygon(points: Any, label: str) -> list[list[float]]:
    if not isinstance(points, list) or len(points) < 3:
        raise ValueError(f"{label} requires at least three XY vertices")
    pts = [_vec(p, 2, label) for p in points]
    if len({tuple(p) for p in pts}) != len(pts):
        raise ValueError(f"{label} has duplicate vertices")
    area2 = sum(pts[i][0]*pts[(i+1)%len(pts)][1] -
                pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))
    if abs(area2) <= 1e-12:
        raise ValueError(f"{label} has zero area")
    return pts


def _validate_holes(holes: list[dict], label: str, errors: list[str]) -> None:
    seen = set()
    for i, h in enumerate(holes):
        try:
            if not h.get("id") or h["id"] in seen:
                raise ValueError("blank or duplicate feature ID")
            seen.add(h["id"])
            _vec(h.get("xy_mm"), 2, "xy_mm")
            if not _finite(h.get("diameter_mm")) or h["diameter_mm"] <= 0:
                raise ValueError("diameter_mm must be positive")
            if not h.get("evidence_id") or not h.get("source_revision"):
                raise ValueError("evidence_id and source_revision are required")
        except (ValueError, TypeError, KeyError) as exc:
            errors.append(f"{label}[{i}]: {exc}")


def _line_distance(p1: list[float], u: list[float],
                   p2: list[float], v: list[float]) -> float:
    cross = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2],
             u[0]*v[1]-u[1]*v[0]]
    cn = sqrt(sum(x*x for x in cross))
    delta = [p2[i]-p1[i] for i in range(3)]
    if cn < 1e-10:
        proj = sum(delta[i]*u[i] for i in range(3))
        residual = [delta[i]-proj*u[i] for i in range(3)]
        return sqrt(sum(x*x for x in residual))
    return abs(sum(delta[i]*cross[i] for i in range(3))) / cn


def _axis_rotation(axis: list[float]) -> tuple[list[float], float]:
    z = [0.0, 0.0, 1.0]
    cross = [z[1]*axis[2]-z[2]*axis[1],
             z[2]*axis[0]-z[0]*axis[2],
             z[0]*axis[1]-z[1]*axis[0]]
    n = sqrt(sum(x*x for x in cross))
    dot = max(-1.0, min(1.0, sum(z[i]*axis[i] for i in range(3))))
    if n < 1e-10:
        return ([1.0, 0.0, 0.0], 0.0 if dot > 0 else 180.0)
    return ([x/n for x in cross], degrees(acos(dot)))


def validate_fixture(config: dict) -> dict:
    errors: list[str] = []
    for key in ("fixture_id", "revision"):
        if not config.get(key):
            errors.append(f"missing {key}")
    prov = config.get("provenance", {})
    if not prov.get("evidence_id") or not prov.get("source_revision"):
        errors.append("fixture-level provenance is required")

    base = config.get("base", {})
    try:
        _polygon(base.get("outline_xy_mm"), "base.outline_xy_mm")
        if not _finite(base.get("thickness_mm")) or base["thickness_mm"] <= 0:
            raise ValueError("base thickness_mm must be positive")
        if not _finite(base.get("top_z_mm")):
            raise ValueError("base top_z_mm must be finite")
        if not base.get("evidence_id") or not base.get("source_revision"):
            raise ValueError("base provenance is required")
        _validate_holes(base.get("mounting_holes", []), "base.mounting_holes", errors)
    except (ValueError, TypeError, KeyError) as exc:
        errors.append(f"base: {exc}")

    carriers = config.get("carriers", [])
    architectures = [c.get("architecture") for c in carriers]
    if len(carriers) != 2 or set(architectures) != ARCHITECTURES:
        errors.append("exactly one column_wheel and one cam_lever carrier are required")
    if len(set(c.get("carrier_id") for c in carriers)) != len(carriers):
        errors.append("carrier IDs must be unique")
    for i, c in enumerate(carriers):
        try:
            if not c.get("carrier_id") or c.get("architecture") not in ARCHITECTURES:
                raise ValueError("carrier ID and recognized architecture required")
            _polygon(c.get("outline_xy_mm"), "carrier.outline_xy_mm")
            if not _finite(c.get("thickness_mm")) or c["thickness_mm"] <= 0:
                raise ValueError("carrier thickness_mm must be positive")
            if not _finite(c.get("top_z_mm")):
                raise ValueError("carrier top_z_mm must be finite")
            if not c.get("evidence_id") or not c.get("source_revision"):
                raise ValueError("carrier provenance required")
            _validate_holes(c.get("mounting_holes", []), f"carriers[{i}].mounting_holes", errors)
            if not c.get("registration_scheme_id"):
                raise ValueError("registration_scheme_id required")
        except (ValueError, TypeError, KeyError) as exc:
            errors.append(f"carriers[{i}]: {exc}")

    mounts = config.get("instrument_mounts", [])
    roles = [m.get("role") for m in mounts]
    if not REQUIRED_MOUNT_ROLES.issubset(set(roles)):
        errors.append(f"missing instrument mount roles: {sorted(REQUIRED_MOUNT_ROLES-set(roles))}")
    if len(set(m.get("mount_id") for m in mounts)) != len(mounts):
        errors.append("instrument mount IDs must be unique")
    normalized = {}
    for i, m in enumerate(mounts):
        try:
            if not m.get("mount_id") or m.get("role") not in REQUIRED_MOUNT_ROLES:
                raise ValueError("mount ID and recognized role required")
            _vec(m.get("origin_xyz_mm"), 3, "origin_xyz_mm")
            axis = _unit(_vec(m.get("axis_xyz"), 3, "axis_xyz"))
            if not _finite(m.get("envelope_radius_mm")) or m["envelope_radius_mm"] <= 0:
                raise ValueError("envelope_radius_mm must be positive")
            if not _finite(m.get("envelope_length_mm")) or m["envelope_length_mm"] <= 0:
                raise ValueError("envelope_length_mm must be positive")
            if not m.get("evidence_id") or not m.get("source_revision"):
                raise ValueError("mount provenance required")
            normalized[m["role"]] = (m, axis)
        except (ValueError, TypeError, KeyError) as exc:
            errors.append(f"instrument_mounts[{i}]: {exc}")

    alignment = config.get("actuator_alignment_tolerance")
    alignment_result = {"evaluated": False, "reason": "explicit alignment tolerances not supplied"}
    if "pusher_actuator" in normalized and "force_transducer" in normalized and alignment:
        try:
            max_offset = alignment["max_axis_offset_mm"]
            max_angle = alignment["max_axis_angle_deg"]
            if not _finite(max_offset) or max_offset < 0 or not _finite(max_angle) or max_angle < 0:
                raise ValueError("alignment tolerances must be finite and nonnegative")
            am, au = normalized["pusher_actuator"]
            fm, fu = normalized["force_transducer"]
            offset = _line_distance(_vec(am["origin_xyz_mm"], 3, "actuator origin"), au,
                                    _vec(fm["origin_xyz_mm"], 3, "force origin"), fu)
            dot = abs(sum(au[j]*fu[j] for j in range(3)))
            angle = degrees(acos(max(-1.0, min(1.0, dot))))
            alignment_result = {
                "evaluated": True, "axis_offset_mm": offset, "axis_angle_deg": angle,
                "within_supplied_tolerances": offset <= max_offset and angle <= max_angle,
                "tolerances": {"max_axis_offset_mm": max_offset, "max_axis_angle_deg": max_angle},
            }
        except (ValueError, TypeError, KeyError) as exc:
            errors.append(f"actuator alignment: {exc}")

    guard = config.get("guard_envelope")
    if not isinstance(guard, dict):
        errors.append("guard_envelope is required")
    else:
        try:
            lo = _vec(guard.get("min_xyz_mm"), 3, "guard min")
            hi = _vec(guard.get("max_xyz_mm"), 3, "guard max")
            if any(hi[j] <= lo[j] for j in range(3)):
                raise ValueError("guard maximums must exceed minimums")
            if not guard.get("evidence_id") or not guard.get("source_revision"):
                raise ValueError("guard provenance required")
        except (ValueError, TypeError, KeyError) as exc:
            errors.append(f"guard_envelope: {exc}")

    return {
        "valid": not errors, "errors": errors,
        "fixture_id": config.get("fixture_id"),
        "carrier_architectures": architectures,
        "actuator_alignment": alignment_result,
        "physical_fit_certified": False,
        "construction_authorized": False,
    }


def _scad_num(v: float) -> str:
    return f"{float(v):.9g}"


def _scad_points(points: list[list[float]]) -> str:
    return "[" + ", ".join("[" + ", ".join(_scad_num(x) for x in p) + "]" for p in points) + "]"


def _hole_cuts(holes: list[dict], z0: float, height: float) -> str:
    return "\n".join(
        f'translate([{_scad_num(h["xy_mm"][0])},{_scad_num(h["xy_mm"][1])},{_scad_num(z0-0.1)}]) '
        f'cylinder(h={_scad_num(height+0.2)}, d={_scad_num(h["diameter_mm"])}, $fn=48);'
        for h in holes
    )


def generate_openscad(config: dict) -> str:
    result = validate_fixture(config)
    if not result["valid"]:
        raise ValueError("fixture input invalid: " + "; ".join(result["errors"]))
    base = config["base"]
    base_bottom = base["top_z_mm"] - base["thickness_mm"]
    lines = [
        "// WP-47 generated envelope model; candidate geometry only.",
        "// Physical fit, stiffness, tolerance, safety and construction are NOT certified.",
        "$fn=48;",
        "show_column_wheel_carrier = false;",
        "show_cam_lever_carrier = false;",
        "module common_base(){",
        "  difference(){",
        f'    translate([0,0,{_scad_num(base_bottom)}]) linear_extrude(height={_scad_num(base["thickness_mm"])}) polygon(points={_scad_points(base["outline_xy_mm"])});',
        "    " + _hole_cuts(base.get("mounting_holes", []), base_bottom, base["thickness_mm"]),
        "  }",
        "}",
    ]
    for c in config["carriers"]:
        name = re.sub(r"[^A-Za-z0-9_]", "_", c["architecture"])
        bottom = c["top_z_mm"] - c["thickness_mm"]
        lines.extend([
            f"module carrier_{name}(){{",
            "  difference(){",
            f'    translate([0,0,{_scad_num(bottom)}]) linear_extrude(height={_scad_num(c["thickness_mm"])}) polygon(points={_scad_points(c["outline_xy_mm"])});',
            "    " + _hole_cuts(c.get("mounting_holes", []), bottom, c["thickness_mm"]),
            "  }",
            "}",
        ])
    lines.extend(["module instrument_envelopes(){"])
    for m in config["instrument_mounts"]:
        axis = _unit(_vec(m["axis_xyz"], 3, "mount axis"))
        rot_axis, rot_angle = _axis_rotation(axis)
        p = _vec(m["origin_xyz_mm"], 3, "mount origin")
        lines.append(
            f'  translate([{",".join(_scad_num(x) for x in p)}]) '
            f'rotate(a={_scad_num(rot_angle)},v=[{",".join(_scad_num(x) for x in rot_axis)}]) '
            f'cylinder(h={_scad_num(m["envelope_length_mm"])},r={_scad_num(m["envelope_radius_mm"])},center=true);'
        )
    lines.extend([
        "}",
        "module guard_envelope(){",
        f'  translate([{",".join(_scad_num(x) for x in config["guard_envelope"]["min_xyz_mm"])}])',
        f'    cube([{",".join(_scad_num(config["guard_envelope"]["max_xyz_mm"][j]-config["guard_envelope"]["min_xyz_mm"][j]) for j in range(3))}],center=false);',
        "}",
        "common_base();",
        "if(show_column_wheel_carrier) carrier_column_wheel();",
        "if(show_cam_lever_carrier) carrier_cam_lever();",
        "instrument_envelopes();",
        "// guard_envelope(); // Enable only after guarding design review.",
    ])
    return "\n".join(lines) + "\n"
