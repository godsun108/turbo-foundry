"""Evidence-controlled component placement register for STEWARD C-01.

Coordinates and envelopes are accepted only as supplied evidence; this module
does not generate or infer physical dimensions or shaft locations.
"""
from __future__ import annotations

from math import isfinite
from typing import Any

EVIDENCE = {"measured", "calculated", "supplier_confirmed", "provisional", "TBD"}
LAYERS = {"dial_side", "main_movement", "rotor_plane", "case_interface", "cross_layer"}
REQUIRED = {"component_id", "system", "layer", "status", "source", "owner"}


def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a finite number") from exc
    if not isfinite(number):
        raise ValueError(f"{field} must be a finite number")
    return number


def validate_placement(item: dict[str, Any]) -> list[str]:
    """Return validation errors; optional geometry must be complete and evidenced."""
    errors = [f"missing {key}" for key in sorted(REQUIRED - item.keys())]
    if errors:
        return errors
    if not str(item["component_id"]).strip():
        errors.append("component_id must be non-empty")
    if item["layer"] not in LAYERS:
        errors.append(f"layer must be one of {sorted(LAYERS)}")
    if item["status"] not in EVIDENCE:
        errors.append(f"status must be one of {sorted(EVIDENCE)}")
    if not str(item["source"]).strip():
        errors.append("source must identify evidence or state 'not assigned'")
    if not str(item["owner"]).strip():
        errors.append("owner must be non-empty")
    xy = (item.get("x_mm"), item.get("y_mm"))
    if (xy[0] is None) != (xy[1] is None):
        errors.append("x_mm and y_mm must be supplied together")
    elif xy[0] is not None:
        try:
            _finite(xy[0], "x_mm")
            _finite(xy[1], "y_mm")
        except ValueError as exc:
            errors.append(str(exc))
        if item["status"] == "TBD":
            errors.append("TBD placement cannot carry assigned XY coordinates")
    z = item.get("z_min_mm"), item.get("z_max_mm")
    if (z[0] is None) != (z[1] is None):
        errors.append("z_min_mm and z_max_mm must be supplied together")
    elif z[0] is not None:
        try:
            z0, z1 = _finite(z[0], "z_min_mm"), _finite(z[1], "z_max_mm")
            if z1 <= z0:
                errors.append("z_max_mm must exceed z_min_mm")
        except ValueError as exc:
            errors.append(str(exc))
    envelope = item.get("envelope_mm")
    if envelope is not None:
        if not isinstance(envelope, dict) or not {"x", "y", "z"} <= envelope.keys():
            errors.append("envelope_mm requires positive x, y and z dimensions")
        else:
            for axis in ("x", "y", "z"):
                try:
                    if _finite(envelope[axis], f"envelope_mm.{axis}") <= 0:
                        errors.append(f"envelope_mm.{axis} must be positive")
                except ValueError as exc:
                    errors.append(str(exc))
    return errors


def validate_register(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate unique component IDs and report geometry evidence completeness."""
    errors: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        for error in validate_placement(item):
            errors.append(f"item {index}: {error}")
        component_id = str(item.get("component_id", "")).strip()
        if component_id and component_id in seen:
            errors.append(f"duplicate component_id: {component_id}")
        seen.add(component_id)
    assigned = sum(item.get("x_mm") is not None and item.get("y_mm") is not None for item in items)
    return {
        "schema": "steward.c01.component-placement.v1",
        "item_count": len(items),
        "xy_assigned_count": assigned,
        "xy_unassigned_count": len(items) - assigned,
        "errors": errors,
        "valid": not errors,
        "release_note": "Register validity is not proof of physical fit, mesh, clearance or manufacturability.",
    }


def conceptual_register() -> list[dict[str, Any]]:
    """Starter register: intentionally no assigned coordinates or dimensions."""
    rows = [
        ("BARREL", "energy_storage", "main_movement"),
        ("CENTER_WHEEL", "going_train", "main_movement"),
        ("THIRD_WHEEL", "going_train", "main_movement"),
        ("FOURTH_WHEEL", "going_train_and_seconds", "main_movement"),
        ("ESCAPE_WHEEL", "escapement", "main_movement"),
        ("BALANCE", "regulator", "main_movement"),
        ("CHRONO_DRIVE", "chronograph", "main_movement"),
        ("CHRONO_CLUTCH", "chronograph", "cross_layer"),
        ("CHRONO_TOTALIZERS", "chronograph", "main_movement"),
        ("CALENDAR_DRIVE", "calendar", "dial_side"),
        ("WEEKDAY_DATE", "calendar_display", "dial_side"),
        ("ROTOR", "automatic_winding", "rotor_plane"),
        ("CENTRAL_HAND_STACK", "display_and_chronograph", "dial_side"),
    ]
    return [{
        "component_id": component_id, "system": system, "layer": layer,
        "status": "TBD", "source": "not assigned", "owner": "C-01 engineering",
        "x_mm": None, "y_mm": None, "z_min_mm": None, "z_max_mm": None,
        "envelope_mm": None,
    } for component_id, system, layer in rows]
