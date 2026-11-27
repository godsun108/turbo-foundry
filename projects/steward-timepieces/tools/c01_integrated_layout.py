"""Integrated, evidence-gated STEWARD C-01 movement layout model.

This is a functional component/interface register with optional geometric
candidate data. No component coordinates, dimensions, materials or architecture
are invented. Geometry is evaluated only when complete explicit inputs exist.
"""
from __future__ import annotations

from typing import Any

try:
    from c01_layout_geometry import evaluate_component_clearances, evaluate_gear_mesh
except ImportError:  # package-style import
    from .c01_layout_geometry import evaluate_component_clearances, evaluate_gear_mesh


COMPONENTS = [
    ("barrel", "mainspring barrel and barrel arbor", "energy"),
    ("automatic_rotor", "oscillating automatic winding rotor", "winding"),
    ("winding_reverser", "automatic winding reversing/reduction works", "winding"),
    ("center_wheel", "going-train center wheel and arbor", "going_train"),
    ("third_wheel", "going-train third wheel and arbor", "going_train"),
    ("fourth_wheel", "going-train fourth wheel and seconds interface", "going_train"),
    ("escapement", "escape wheel and pallet assembly", "regulation"),
    ("balance", "balance, hairspring and shock protection envelope", "regulation"),
    ("motion_works", "motion works and setting interface", "time_display"),
    ("hour_minute_hands", "central hour and minute display stack", "time_display"),
    ("running_seconds", "continuous running-seconds display", "time_display"),
    ("chrono_drive", "chronograph drive take-off and reduction train", "chronograph"),
    ("chrono_clutch", "chronograph coupling/clutch candidate", "chronograph"),
    ("chrono_control", "start/stop/reset control mechanism", "chronograph"),
    ("chrono_brake", "chronograph seconds brake", "chronograph"),
    ("chrono_seconds", "central chronograph seconds arbor and hand", "chronograph"),
    ("chrono_30m", "30-minute elapsed-time totalizer", "chronograph"),
    ("chrono_12h", "12-hour elapsed-time totalizer", "chronograph"),
    ("chrono_reset", "heart cams, hammers and reset interfaces", "chronograph"),
    ("calendar_drive", "calendar drive and indexing works", "calendar"),
    ("weekday_display", "weekday disc/window and jumper interface", "calendar"),
    ("date_display", "day-of-month disc/window and jumper interface", "calendar"),
    ("main_plate", "main plate structural and bearing datum", "structure"),
    ("bridges", "bridge and cock structural envelopes", "structure"),
    ("case_interface", "stem, casing supports, pushers and caseback envelope", "case"),
]

INTERFACES = [
    ("barrel", "center_wheel", "energy", "going-train input; exact wheel/pinion mesh TBD"),
    ("center_wheel", "third_wheel", "energy", "going-train mesh TBD"),
    ("third_wheel", "fourth_wheel", "energy", "going-train mesh TBD"),
    ("fourth_wheel", "escapement", "energy", "escape-wheel drive path; topology TBD"),
    ("automatic_rotor", "winding_reverser", "energy", "rotor input"),
    ("winding_reverser", "barrel", "energy", "winding output"),
    ("fourth_wheel", "running_seconds", "indication", "seconds display take-off TBD"),
    ("center_wheel", "motion_works", "indication", "motion-works input TBD"),
    ("motion_works", "hour_minute_hands", "indication", "central time display"),
    ("fourth_wheel", "chrono_drive", "candidate_energy", "candidate source only; no source selected"),
    ("chrono_drive", "chrono_clutch", "energy", "drive interface TBD"),
    ("chrono_control", "chrono_clutch", "control", "start/stop coupling command"),
    ("chrono_control", "chrono_brake", "control", "brake command"),
    ("chrono_clutch", "chrono_seconds", "energy", "central chronograph seconds output"),
    ("chrono_clutch", "chrono_30m", "energy", "30-minute totalizer drive interface TBD"),
    ("chrono_clutch", "chrono_12h", "energy", "12-hour totalizer drive interface TBD"),
    ("chrono_control", "chrono_reset", "control", "reset actuation"),
    ("chrono_reset", "chrono_seconds", "reset", "zero-return interface"),
    ("chrono_reset", "chrono_30m", "reset", "zero-return interface"),
    ("chrono_reset", "chrono_12h", "reset", "zero-return interface"),
    ("center_wheel", "calendar_drive", "candidate_energy", "calendar take-off TBD"),
    ("calendar_drive", "weekday_display", "indication", "weekday indexing interface TBD"),
    ("calendar_drive", "date_display", "indication", "date indexing interface TBD"),
]

DISPLAY_ALTERNATIVES = {
    "A": {
        "description": "30-minute register at 12; 12-hour register at 6; running seconds at 9; weekday/date at 3.",
        "status": "candidate_not_selected",
    },
    "B": {
        "description": "30-minute register at 3; 12-hour register at 6; running seconds at 9; weekday/date at 12.",
        "status": "candidate_not_selected",
    },
    "C": {
        "description": "Registers at 12, 6 and 9; compact paired calendar near 12.",
        "status": "candidate_not_selected",
    },
}

PACKAGING_FAMILIES = [
    {
        "id": "horizontal_lateral",
        "description": "Chronograph works arranged predominantly in the main movement plane.",
        "status": "candidate_not_selected",
    },
    {
        "id": "vertical_coaxial",
        "description": "Selected chronograph elements share axes or occupy additional axial layers.",
        "status": "candidate_not_selected",
    },
    {
        "id": "hybrid_layered",
        "description": "Mixed planar and axial placement to balance footprint, stack height and service access.",
        "status": "candidate_not_selected",
    },
]


def build_baseline() -> dict[str, Any]:
    """Return functional baseline without fabricated physical placements."""
    return {
        "schema": "steward.c01.integrated-layout.v1",
        "status": "functional architecture baseline; physical layout not dimensioned",
        "coordinate_system": {
            "xy_origin": "movement/dial center",
            "positive_x": "3 o'clock",
            "positive_y": "12 o'clock",
            "units": "mm only when supplied from controlled geometry",
            "z_datum": "single controlled axial datum required; not yet assigned",
        },
        "components": [
            {"id": ident, "function": function, "zone": zone,
             "xy_mm": None, "envelope_radius_mm": None,
             "z_interval_mm": None, "evidence": "TBD", "source_revision": None}
            for ident, function, zone in COMPONENTS
        ],
        "interfaces": [
            {"from": source, "to": target, "type": kind, "definition": note}
            for source, target, kind, note in INTERFACES
        ],
        "display_alternatives": DISPLAY_ALTERNATIVES,
        "packaging_families": PACKAGING_FAMILIES,
        "open_decisions": [
            "chronograph take-off: fourth-wheel/seconds arbor or dedicated drive",
            "clutch: vertical friction or horizontal/lateral coupling",
            "control: column wheel or cam/lever",
            "30-minute and 12-hour totalizers: continuous or jumping",
            "dial arrangement: A, B or C",
            "month window: separate scope decision; not included in this C-01 baseline",
            "case/movement envelope, axial datum and plate/bridge split",
        ],
    }


def validate_interfaces(components: list[dict[str, Any]],
                        interfaces: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [item.get("id") for item in components]
    if any(not isinstance(value, str) or not value for value in ids):
        raise ValueError("every component requires a non-empty id")
    if len(ids) != len(set(ids)):
        raise ValueError("component ids must be unique")
    known = set(ids)
    seen = set()
    for index, edge in enumerate(interfaces):
        source, target = edge.get("from"), edge.get("to")
        if source not in known or target not in known:
            raise ValueError(f"interface {index} references an unknown component")
        if source == target:
            raise ValueError(f"interface {index} cannot connect a component to itself")
        key = (source, target, edge.get("type"))
        if key in seen:
            raise ValueError("duplicate interface")
        seen.add(key)
    return {
        "component_count": len(ids),
        "interface_count": len(interfaces),
        "all_interface_endpoints_resolve": True,
        "functional_graph_only": True,
    }


def evaluate_candidate(data: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a proposed integrated register; incomplete geometry is not evaluable."""
    components = data.get("components")
    interfaces = data.get("interfaces")
    if not isinstance(components, list) or not components:
        raise ValueError("components must be a non-empty list")
    if not isinstance(interfaces, list):
        raise ValueError("interfaces must be a list")
    graph = validate_interfaces(components, interfaces)
    required_ids = {item[0] for item in COMPONENTS}
    supplied_ids = {item["id"] for item in components}
    missing_roles = sorted(required_ids - supplied_ids)

    geometric = []
    incomplete = []
    for item in components:
        keys = ("x_mm", "y_mm", "envelope_radius_mm", "z_min_mm", "z_max_mm", "layer")
        if all(key in item and item[key] is not None for key in keys):
            geometric.append({
                "id": item["id"], "x_mm": item["x_mm"], "y_mm": item["y_mm"],
                "envelope_radius_mm": item["envelope_radius_mm"],
                "z_min_mm": item["z_min_mm"], "z_max_mm": item["z_max_mm"],
                "layer": item["layer"],
            })
        else:
            incomplete.append(item["id"])

    geometry = evaluate_component_clearances(geometric) if geometric else None
    meshes = [evaluate_gear_mesh(mesh) for mesh in data.get("gear_meshes", [])]
    complete = not missing_roles and not incomplete
    return {
        "schema": "steward.c01.integrated-layout-evaluation.v1",
        "candidate_id": data.get("candidate_id", "unnamed_candidate"),
        "functional_graph": graph,
        "missing_required_component_ids": missing_roles,
        "components_missing_geometry": sorted(incomplete),
        "geometric_component_count": len(geometric),
        "component_clearance_evaluation": geometry,
        "gear_mesh_evaluations": meshes,
        "geometry_status": "evaluated_subset_only" if geometry else "not_evaluable",
        "completeness_status": "complete_register" if complete else "incomplete_register",
        "overall_fit_status": "not_certified",
        "interference_detected_in_evaluated_subset": (
            geometry["has_envelope_interference"] if geometry else None
        ),
        "limitations": [
            "Only supplied component envelopes and axial intervals are evaluated.",
            "Missing geometry is not interpreted as clearance or successful fit.",
            "Gear mesh checks require explicit tooth counts, module, XY centers and tolerance.",
            "No swept motion, detailed tooth profiles, tolerance stack, deflection or assembly simulation.",
            "Functional interfaces are not assertions of literal shaft adjacency or selected power topology.",
        ],
    }
