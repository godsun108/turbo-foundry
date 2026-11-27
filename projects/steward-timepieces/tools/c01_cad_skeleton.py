"""Evidence-gated neutral CAD skeleton generator for STEWARD C-01.

Generates OpenSCAD source only from complete, explicit, traceable geometry.
No dimensions or coordinates are supplied as design defaults.
"""
from __future__ import annotations

from math import isfinite
from typing import Any


def _number(value: Any, field: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not isfinite(result):
        raise ValueError(f"{field} must be finite")
    if positive and result <= 0:
        raise ValueError(f"{field} must be positive")
    return result


def _point(value: Any, field: str) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{field} must be [x_mm, y_mm]")
    return (_number(value[0], field + ".x"), _number(value[1], field + ".y"))


def _polygon(points: Any, field: str) -> list[tuple[float, float]]:
    if not isinstance(points, list) or len(points) < 3:
        raise ValueError(f"{field} requires at least three XY points")
    parsed = [_point(p, field) for p in points]
    if len(set(parsed)) != len(parsed):
        raise ValueError(f"{field} points must be unique")
    area2 = sum(parsed[i][0] * parsed[(i + 1) % len(parsed)][1]
                - parsed[(i + 1) % len(parsed)][0] * parsed[i][1]
                for i in range(len(parsed)))
    if abs(area2) <= 1e-12:
        raise ValueError(f"{field} must enclose non-zero area")
    return parsed


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate explicit plate, bore, bridge and keepout geometry plus provenance."""
    if not isinstance(config, dict):
        raise ValueError("config must be an object")
    if not config.get("candidate_id"):
        raise ValueError("candidate_id is required")
    provenance = config.get("provenance")
    if not isinstance(provenance, dict) or not provenance.get("evidence") or not provenance.get("source_revision"):
        raise ValueError("global provenance requires evidence and source_revision")

    plate = config.get("plate")
    if not isinstance(plate, dict):
        raise ValueError("plate geometry is required")
    outline = _polygon(plate.get("outline_xy_mm"), "plate.outline_xy_mm")
    thickness = _number(plate.get("thickness_mm"), "plate.thickness_mm", positive=True)
    top_z = _number(plate.get("top_z_mm"), "plate.top_z_mm")

    bores = config.get("bearing_bores")
    bridges = config.get("bridges")
    keepouts = config.get("keepouts", [])
    if not isinstance(bores, list) or not isinstance(bridges, list) or not isinstance(keepouts, list):
        raise ValueError("bearing_bores, bridges and keepouts must be lists")

    def unique_ids(items: list[dict[str, Any]], label: str) -> None:
        ids = [item.get("id") for item in items]
        if any(not isinstance(v, str) or not v for v in ids) or len(ids) != len(set(ids)):
            raise ValueError(f"{label} require unique non-empty ids")

    unique_ids(bores, "bearing bores")
    unique_ids(bridges, "bridges")
    unique_ids(keepouts, "keepouts")

    for bore in bores:
        _point(bore.get("xy_mm"), f"bearing bore {bore['id']}.xy_mm")
        _number(bore.get("diameter_mm"), f"bearing bore {bore['id']}.diameter_mm", positive=True)
        if not bore.get("component_id") or not bore.get("axis_id"):
            raise ValueError(f"bearing bore {bore['id']} requires component_id and axis_id")
        if not bore.get("evidence") or not bore.get("source_revision"):
            raise ValueError(f"bearing bore {bore['id']} requires evidence and source_revision")

    for bridge in bridges:
        _polygon(bridge.get("outline_xy_mm"), f"bridge {bridge.get('id')}.outline_xy_mm")
        _number(bridge.get("z_min_mm"), f"bridge {bridge['id']}.z_min_mm")
        _number(bridge.get("z_max_mm"), f"bridge {bridge['id']}.z_max_mm")
        if bridge["z_max_mm"] <= bridge["z_min_mm"]:
            raise ValueError(f"bridge {bridge['id']} must have positive axial extent")
        if not isinstance(bridge.get("supported_components"), list) or not bridge["supported_components"]:
            raise ValueError(f"bridge {bridge['id']} requires supported_components")
        if not bridge.get("evidence") or not bridge.get("source_revision"):
            raise ValueError(f"bridge {bridge['id']} requires evidence and source_revision")

    for item in keepouts:
        _point(item.get("xy_mm"), f"keepout {item.get('id')}.xy_mm")
        _number(item.get("radius_mm"), f"keepout {item['id']}.radius_mm", positive=True)
        _number(item.get("z_min_mm"), f"keepout {item['id']}.z_min_mm")
        _number(item.get("z_max_mm"), f"keepout {item['id']}.z_max_mm")
        if item["z_max_mm"] <= item["z_min_mm"]:
            raise ValueError(f"keepout {item['id']} must have positive axial extent")
        if not item.get("evidence") or not item.get("source_revision"):
            raise ValueError(f"keepout {item['id']} requires evidence and source_revision")

    return {
        "candidate_id": config["candidate_id"],
        "plate_vertex_count": len(outline),
        "bearing_bore_count": len(bores),
        "bridge_count": len(bridges),
        "keepout_count": len(keepouts),
        "geometry_complete_for_skeleton": True,
        "units": "mm",
        "provenance": provenance,
    }


def _fmt(value: float) -> str:
    return format(float(value), ".12g")


def generate_openscad(config: dict[str, Any]) -> str:
    """Return a reviewable OpenSCAD skeleton from validated supplied geometry."""
    validate_config(config)
    plate = config["plate"]
    outline = _polygon(plate["outline_xy_mm"], "plate.outline_xy_mm")
    top_z = _number(plate["top_z_mm"], "plate.top_z_mm")
    thickness = _number(plate["thickness_mm"], "plate.thickness_mm", positive=True)
    bottom_z = top_z - thickness

    def poly(points: list[tuple[float, float]]) -> str:
        return "[" + ", ".join("[" + _fmt(x) + ", " + _fmt(y) + "]" for x, y in points) + "]"

    lines = [
        "// STEWARD C-01 parametric structural CAD skeleton",
        "// Generated only from explicit, traceable candidate geometry.",
        "// Review and validate in CAD; this is not a manufacturing drawing.",
        f"// Candidate: {config['candidate_id']}",
        f"// Evidence: {config['provenance']['evidence']}",
        f"// Source revision: {config['provenance']['source_revision']}",
        "$fn = 64;",
        "",
        "module plate_blank() {",
        f"  translate([0, 0, {_fmt(bottom_z)}])",
        f"    linear_extrude(height = {_fmt(thickness)}) polygon(points = {poly(outline)});",
        "}",
        "",
        "module bearing_bores() {",
    ]
    for bore in config["bearing_bores"]:
        x, y = _point(bore["xy_mm"], "bearing bore xy_mm")
        radius = _number(bore["diameter_mm"], "bearing bore diameter") / 2
        lines.append(
            f"  translate([{_fmt(x)}, {_fmt(y)}, {_fmt(bottom_z - 0.1)}]) "
            f"cylinder(h = {_fmt(thickness + 0.2)}, r = {_fmt(radius)});"
        )
    lines += ["}", "", "module main_plate() {", "  difference() {", "    plate_blank();", "    bearing_bores();", "  }", "}", ""]

    for bridge in config["bridges"]:
        points = _polygon(bridge["outline_xy_mm"], "bridge outline")
        z0 = _number(bridge["z_min_mm"], "bridge z_min_mm")
        z1 = _number(bridge["z_max_mm"], "bridge z_max_mm")
        name = "bridge_" + "".join(c if c.isalnum() else "_" for c in bridge["id"])
        lines += [
            f"module {name}() {{",
            f"  translate([0, 0, {_fmt(z0)}])",
            f"    linear_extrude(height = {_fmt(z1 - z0)}) polygon(points = {poly(points)});",
            "}",
            "",
        ]

    for item in config["keepouts"]:
        x, y = _point(item["xy_mm"], "keepout xy_mm")
        z0, z1 = _number(item["z_min_mm"], "keepout z_min_mm"), _number(item["z_max_mm"], "keepout z_max_mm")
        radius = _number(item["radius_mm"], "keepout radius_mm", positive=True)
        name = "envelope_" + "".join(c if c.isalnum() else "_" for c in item["id"])
        lines += [
            f"module {name}() {{",
            f"  translate([{_fmt(x)}, {_fmt(y)}, {_fmt(z0)}])",
            f"    cylinder(h = {_fmt(z1 - z0)}, r = {_fmt(radius)});",
            "}",
            "",
        ]

    lines += [
        "// Assembly is intentionally not instantiated: bridge/keepout visibility",
        "// and interference review must be selected by the engineer in the CAD viewer.",
        "// Example review calls:",
        "// main_plate();",
    ]
    for bridge in config["bridges"]:
        name = "bridge_" + "".join(c if c.isalnum() else "_" for c in bridge["id"])
        lines.append(f"// {name}();")
    for item in config["keepouts"]:
        name = "envelope_" + "".join(c if c.isalnum() else "_" for c in item["id"])
        lines.append(f"// {name}();")
    return "\n".join(lines) + "\n"
