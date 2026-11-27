"""Evidence-gated C-01 master datum and structural layout register.

No dimensions, coordinates, plate thicknesses, bearing sizes or bridge counts
are assigned. Evaluation operates only on explicit, traceable supplied values.
"""
from __future__ import annotations

from math import isfinite
from typing import Any

DATUMS = [
    ("M0", "master axial datum", "controlled reference plane; physical realization TBD"),
    ("DIAL", "dial reference plane", "dial-side stack reference; offset from M0 TBD"),
    ("PLATE_TOP", "main-plate upper face", "structural reference; offset from M0 TBD"),
    ("PLATE_BOTTOM", "main-plate lower face", "structural reference; offset from M0 TBD"),
    ("BRIDGE_UNDERSIDE", "bridge underside plane", "bridge clearance reference; offset TBD"),
    ("BRIDGE_TOP", "bridge upper face", "movement height reference; offset TBD"),
    ("ROTOR_PLANE", "automatic rotor operating plane", "rotor clearance reference; offset TBD"),
    ("CASEBACK_INNER", "caseback inner surface", "case interface reference; offset TBD"),
]

ZONES = [
    "main_plate", "going_train", "regulation", "chronograph",
    "calendar_dial_side", "automatic_winding", "dial_display", "case_interface",
]

REQUIRED_BEARING_FIELDS = ("id", "component_id", "axis_id", "support_type", "evidence", "source_revision")
REQUIRED_BRIDGE_FIELDS = ("id", "zone", "supported_components", "evidence", "source_revision")


def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a finite number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a finite number") from exc
    if not isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def build_baseline() -> dict[str, Any]:
    """Return datum/structure control registers with all physical values TBD."""
    return {
        "schema": "steward.c01.structure-layout.v1",
        "status": "preliminary structural architecture; geometry not assigned",
        "units": "mm when controlled source geometry is supplied",
        "master_datum_id": "M0",
        "datums": [
            {"id": ident, "name": name, "definition": definition,
             "z_mm": None, "evidence": "TBD", "source_revision": None}
            for ident, name, definition in DATUMS
        ],
        "zones": [{"id": zone, "geometry_status": "TBD"} for zone in ZONES],
        "bearing_axes": [],
        "bridges": [],
        "stack_intervals": [],
        "open_items": [
            "physical realization and sign convention for M0",
            "approved movement and case envelope",
            "main-plate and bridge partition and thicknesses",
            "bearing/arbor coordinates, support type and endshake",
            "rotor, balance and hairspring dynamic envelopes",
            "chronograph clutch/control and counter support arrangement",
            "calendar/dial-side clearances and hand-stack heights",
            "fastener locations, tool access and service sequence",
            "materials, tolerances, thermal effects, deflection and lubrication",
        ],
    }


def _unique(items: list[dict[str, Any]], field: str, label: str) -> set[str]:
    values = [item.get(field) for item in items]
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"every {label} requires a non-empty {field}")
    if len(values) != len(set(values)):
        raise ValueError(f"{label} {field} values must be unique")
    return set(values)


def validate_register(data: dict[str, Any], known_component_ids: set[str] | None = None) -> dict[str, Any]:
    datums = data.get("datums")
    bearings = data.get("bearing_axes")
    bridges = data.get("bridges")
    if not isinstance(datums, list) or not datums:
        raise ValueError("datums must be a non-empty list")
    if not isinstance(bearings, list) or not isinstance(bridges, list):
        raise ValueError("bearing_axes and bridges must be lists")
    datum_ids = _unique(datums, "id", "datum")
    if data.get("master_datum_id") not in datum_ids:
        raise ValueError("master_datum_id must reference a declared datum")
    bearing_ids = _unique(bearings, "id", "bearing axis") if bearings else set()
    bridge_ids = _unique(bridges, "id", "bridge") if bridges else set()

    for item in datums:
        if item.get("z_mm") is not None:
            _finite(item["z_mm"], f"datum {item['id']} z_mm")
            if not item.get("evidence") or not item.get("source_revision"):
                raise ValueError(f"datum {item['id']} requires evidence and source_revision")

    for item in bearings:
        missing = [key for key in REQUIRED_BEARING_FIELDS if key not in item or item[key] in (None, "")]
        if missing:
            raise ValueError(f"bearing axis {item['id']} missing: {', '.join(missing)}")
        if known_component_ids is not None and item["component_id"] not in known_component_ids:
            raise ValueError(f"bearing axis {item['id']} references unknown component")
        if item.get("xy_mm") is not None:
            xy = item["xy_mm"]
            if not isinstance(xy, (list, tuple)) or len(xy) != 2:
                raise ValueError(f"bearing axis {item['id']} xy_mm must be [x, y]")
            _finite(xy[0], "x_mm")
            _finite(xy[1], "y_mm")
        if item.get("z_interval_mm") is not None:
            interval = item["z_interval_mm"]
            if not isinstance(interval, (list, tuple)) or len(interval) != 2:
                raise ValueError("bearing z_interval_mm must be [min, max]")
            lo, hi = (_finite(interval[0], "z_min_mm"), _finite(interval[1], "z_max_mm"))
            if hi <= lo:
                raise ValueError("bearing z interval must have positive extent")

    for item in bridges:
        missing = [key for key in REQUIRED_BRIDGE_FIELDS if key not in item or item[key] in (None, "")]
        if missing:
            raise ValueError(f"bridge {item['id']} missing: {', '.join(missing)}")
        if item["zone"] not in ZONES:
            raise ValueError(f"bridge {item['id']} has unknown zone")
        if not isinstance(item["supported_components"], list) or not item["supported_components"]:
            raise ValueError(f"bridge {item['id']} requires supported_components")
        if known_component_ids is not None:
            unknown = set(item["supported_components"]) - known_component_ids
            if unknown:
                raise ValueError(f"bridge {item['id']} references unknown components: {sorted(unknown)}")

    return {
        "datum_count": len(datums),
        "bearing_axis_count": len(bearing_ids),
        "bridge_count": len(bridge_ids),
        "master_datum_resolves": True,
        "all_supplied_references_resolve": True,
    }


def evaluate_stack(intervals: list[dict[str, Any]]) -> dict[str, Any]:
    """Check explicitly supplied axial intervals; touching faces are zero clearance."""
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list")
    ids = _unique(intervals, "id", "stack interval") if intervals else set()
    normalized = []
    for item in intervals:
        if not item.get("evidence") or not item.get("source_revision"):
            raise ValueError(f"stack interval {item['id']} requires evidence and source_revision")
        lo = _finite(item.get("z_min_mm"), f"{item['id']} z_min_mm")
        hi = _finite(item.get("z_max_mm"), f"{item['id']} z_max_mm")
        if hi <= lo:
            raise ValueError(f"stack interval {item['id']} must have positive extent")
        normalized.append((item["id"], item.get("zone"), lo, hi))
    overlaps = []
    for i, first in enumerate(normalized):
        for second in normalized[i + 1:]:
            if first[1] == second[1] and min(first[3], second[3]) > max(first[2], second[2]):
                overlaps.append({"a": first[0], "b": second[0], "zone": first[1],
                                 "overlap_mm": min(first[3], second[3]) - max(first[2], second[2])})
    return {
        "interval_count": len(ids),
        "overlaps": overlaps,
        "overlap_detected": bool(overlaps),
        "status": "candidate_interval_check_only",
        "limitations": [
            "Only supplied intervals in the same declared zone are compared.",
            "Different zones may still physically intersect; zone labels are not proof of separation.",
            "No tolerance stack, deflection, thermal growth, swept motion or assembly access is evaluated.",
        ],
    }


def evaluate_candidate(data: dict[str, Any], known_component_ids: set[str] | None = None) -> dict[str, Any]:
    """Validate structural registers and evaluate optional axial stack intervals."""
    summary = validate_register(data, known_component_ids)
    stack = evaluate_stack(data.get("stack_intervals", []))
    required_datum_ids = {item[0] for item in DATUMS}
    supplied_datum_ids = {item["id"] for item in data["datums"]}
    missing_datums = sorted(required_datum_ids - supplied_datum_ids)
    return {
        "schema": "steward.c01.structure-layout-evaluation.v1",
        "register_summary": summary,
        "missing_reference_datums": missing_datums,
        "stack_evaluation": stack,
        "structural_geometry_status": "not_evaluable" if not data["bearing_axes"] and not data["bridges"] else "register_only",
        "overall_fit_status": "not_certified",
        "limitations": [
            "A bearing-axis register entry does not establish a bearing size, fit or load capacity.",
            "A bridge register entry does not establish bridge geometry, stiffness or fastener design.",
            "No physical CAD, finite-element, tolerance or serviceability certification is produced.",
        ],
    }
