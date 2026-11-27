"""WP-26 integrated candidate synthesis and cross-register evaluation.

This orchestration layer composes existing WP-18, WP-23, WP-24 and WP-25
calculators. It does not supply defaults or declare a candidate buildable.
"""
from __future__ import annotations

from itertools import product
from typing import Any

try:
    from c01_tooth_synthesis import synthesize
    from c01_going_train import evaluate_outputs
    from c01_arbor_coordinates import evaluate_mesh
    from c01_bearing_architecture import evaluate_candidate as evaluate_supports
    from c01_cad_skeleton import generate_openscad
except ImportError:
    from .c01_tooth_synthesis import synthesize
    from .c01_going_train import evaluate_outputs
    from .c01_arbor_coordinates import evaluate_mesh
    from .c01_bearing_architecture import evaluate_candidate as evaluate_supports
    from .c01_cad_skeleton import generate_openscad


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _unique(items: list[dict[str, Any]], field: str, label: str) -> set[str]:
    values = [_required_text(item.get(field), f"{label}.{field}") for item in items]
    if len(values) != len(set(values)):
        raise ValueError(f"{label} {field} values must be unique")
    return set(values)


def _search_spec(spec: dict[str, Any], common: dict[str, Any]) -> dict[str, Any]:
    merged = dict(common)
    merged.update(spec.get("search", {}))
    for key in ("target_ratio", "min_teeth", "max_teeth", "min_stage_ratio",
                "max_stage_ratio", "max_fractional_error", "max_results"):
        if key not in merged:
            raise ValueError(f"mesh {spec.get('id')} search requires {key}")
    return merged


def _candidate_assignments(mesh_specs: list[dict[str, Any]],
                           common_search: dict[str, Any],
                           max_combinations: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    unique_mesh_ids = _unique(mesh_specs, "id", "mesh_spec")
    del unique_mesh_ids
    options = []
    synthesis_reports = []
    for spec in mesh_specs:
        for field in ("driver_gear_id", "driven_gear_id", "mesh_type",
                      "evidence", "source_revision"):
            _required_text(spec.get(field), f"mesh {spec.get('id')}.{field}")
        if spec["mesh_type"] != "external":
            raise ValueError("WP-26 synthesis currently supports external spur meshes only")
        search = _search_spec(spec, common_search)
        report = synthesize(search)
        synthesis_reports.append({"mesh_id": spec["id"], "synthesis": report})
        if not report["returned_candidates"]:
            return [], synthesis_reports
        options.append(report["returned_candidates"])

    combinations = []
    for selection in product(*options):
        assigned: dict[str, int] = {}
        valid = True
        stage_records = []
        for spec, candidate in zip(mesh_specs, selection):
            if len(candidate["stages"]) != 1:
                # WP-26 mesh specs are individual physical meshes; a compound
                # path is represented by multiple connected mesh specs.
                valid = False
                break
            stage = candidate["stages"][0]
            for gear_id, teeth in ((spec["driver_gear_id"], stage["driver_teeth"]),
                                   (spec["driven_gear_id"], stage["driven_teeth"])):
                if gear_id in assigned and assigned[gear_id] != teeth:
                    valid = False
                    break
                assigned[gear_id] = teeth
            if not valid:
                break
            stage_records.append({
                "mesh_id": spec["id"],
                "driver_gear_id": spec["driver_gear_id"],
                "driven_gear_id": spec["driven_gear_id"],
                "driver_teeth": stage["driver_teeth"],
                "driven_teeth": stage["driven_teeth"],
                "speed_ratio_magnitude": candidate["compound_speed_ratio_magnitude"],
                "module_mm": search.get("module_mm"),
                "mesh_type": spec["mesh_type"],
                "evidence": spec["evidence"],
                "source_revision": spec["source_revision"],
            })
        if valid:
            combinations.append({"gear_tooth_assignments": assigned,
                                 "mesh_schedule": stage_records})
        if len(combinations) >= max_combinations:
            break
    return combinations, synthesis_reports


def evaluate_candidate(data: dict[str, Any]) -> dict[str, Any]:
    """Synthesize and evaluate bounded tooth schedules against supplied registers.

    Required keys:
      candidate_id, provenance, arbors, mesh_specs, common_search,
      input, outputs, max_combinations.
    Optional:
      structural_support (WP-24 input), cad_config (WP-22 input).
    Each arbor needs id, role, component_id, axis_id, evidence,
    source_revision and optional xy_mm.
    """
    if not isinstance(data, dict):
        raise ValueError("candidate data must be an object")
    candidate_id = _required_text(data.get("candidate_id"), "candidate_id")
    provenance = data.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("provenance is required")
    _required_text(provenance.get("evidence"), "provenance.evidence")
    _required_text(provenance.get("source_revision"), "provenance.source_revision")
    arbors = data.get("arbors")
    mesh_specs = data.get("mesh_specs")
    if not isinstance(arbors, list) or not arbors:
        raise ValueError("arbors must be a non-empty list")
    if not isinstance(mesh_specs, list) or not mesh_specs:
        raise ValueError("mesh_specs must be a non-empty list")
    arbor_ids = _unique(arbors, "id", "arbor")
    for arbor in arbors:
        for field in ("role", "component_id", "axis_id", "evidence", "source_revision"):
            _required_text(arbor.get(field), f"arbor {arbor['id']}.{field}")
    max_combinations = data.get("max_combinations")
    if isinstance(max_combinations, bool) or not isinstance(max_combinations, int) or max_combinations <= 0:
        raise ValueError("max_combinations must be a positive integer")

    by_arbor = {item["id"]: item for item in arbors}
    for spec in mesh_specs:
        if spec.get("arbor_a_id") not in arbor_ids or spec.get("arbor_b_id") not in arbor_ids:
            raise ValueError(f"mesh {spec.get('id')} references unknown arbor")
        if spec["arbor_a_id"] == spec["arbor_b_id"]:
            raise ValueError(f"mesh {spec.get('id')} must connect distinct arbors")
        if spec.get("driver_gear_id") == spec.get("driven_gear_id"):
            raise ValueError(f"mesh {spec.get('id')} gear IDs must differ")

    combinations, synthesis_reports = _candidate_assignments(
        mesh_specs, data.get("common_search", {}), max_combinations)
    evaluated = []
    for index, combo in enumerate(combinations, start=1):
        gears = []
        for gear_id, teeth in combo["gear_tooth_assignments"].items():
            spec = next(s for s in mesh_specs
                        if gear_id in {s["driver_gear_id"], s["driven_gear_id"]})
            arbor_id = spec["arbor_a_id"] if gear_id == spec["driver_gear_id"] else spec["arbor_b_id"]
            # Validate the gear/arbor mapping against every occurrence.
            occurrences = []
            for item in mesh_specs:
                if item["driver_gear_id"] == gear_id:
                    occurrences.append(item["arbor_a_id"])
                if item["driven_gear_id"] == gear_id:
                    occurrences.append(item["arbor_b_id"])
            if len(set(occurrences)) != 1:
                raise ValueError(f"gear {gear_id} is assigned to multiple arbors")
            arbor_id = occurrences[0]
            gears.append({"id": gear_id, "arbor_id": arbor_id, "teeth": teeth,
                          "role": "candidate wheel/pinion", "evidence": "derived candidate from explicit bounds",
                          "source_revision": provenance["source_revision"]})
        meshes = [{
            "id": spec["id"], "driver_gear_id": spec["driver_gear_id"],
            "driven_gear_id": spec["driven_gear_id"],
            "mesh_type": spec["mesh_type"], "evidence": spec["evidence"],
            "source_revision": spec["source_revision"],
        } for spec in mesh_specs]
        train = {"arbors": arbors, "gears": gears, "meshes": meshes,
                 "input": data["input"], "outputs": data["outputs"]}
        kinematics = evaluate_outputs(train)

        geometry = []
        for spec in mesh_specs:
            a, b = by_arbor[spec["arbor_a_id"]], by_arbor[spec["arbor_b_id"]]
            stage = next(s for s in combo["mesh_schedule"] if s["mesh_id"] == spec["id"])
            if a.get("xy_mm") is None or b.get("xy_mm") is None or stage.get("module_mm") is None:
                geometry.append({"mesh_id": spec["id"], "status": "not_evaluable_missing_module_or_coordinates"})
                continue
            tolerance = spec.get("center_distance_tolerance_mm")
            if tolerance is None:
                geometry.append({"mesh_id": spec["id"], "status": "not_evaluable_tolerance_not_supplied"})
                continue
            geometry.append(evaluate_mesh({
                "id": spec["id"], "arbor_a_id": spec["arbor_a_id"],
                "arbor_b_id": spec["arbor_b_id"], "module_mm": stage["module_mm"],
                "gear_a_teeth": stage["driver_teeth"], "gear_b_teeth": stage["driven_teeth"],
                "mesh": spec["mesh_type"], "xy_a_mm": a["xy_mm"], "xy_b_mm": b["xy_mm"],
                "center_distance_tolerance_mm": tolerance,
                "evidence": spec["evidence"], "source_revision": spec["source_revision"],
            }))
        evaluated.append({
            "candidate_id": f"{candidate_id}-C{index:03d}",
            "gear_tooth_assignments": combo["gear_tooth_assignments"],
            "mesh_schedule": combo["mesh_schedule"],
            "kinematic_closure": kinematics,
            "center_distance_checks": geometry,
            "kinematic_targets_all_pass_supplied_tolerance": all(
                item["passes_supplied_speed_tolerance"] is True
                for item in kinematics["outputs"]),
            "all_geometry_checks_evaluable_and_pass": bool(geometry) and all(
                item.get("passes_supplied_center_distance_tolerance") is True
                for item in geometry),
        })

    support_result = None
    support_data = data.get("structural_support")
    if support_data is not None:
        support_input = dict(support_data)
        support_input.setdefault("candidate_id", candidate_id)
        support_input.setdefault("provenance", provenance)
        support_result = evaluate_supports(support_input)

    cad_source = None
    if data.get("cad_config") is not None:
        # Only generate from the user's explicitly supplied, validated geometry.
        cad_source = generate_openscad(data["cad_config"])

    return {
        "schema": "steward.c01.integrated-gear-train-candidate.v1",
        "candidate_id": candidate_id,
        "synthesis_reports": synthesis_reports,
        "compatible_candidate_count": len(evaluated),
        "candidate_limit": max_combinations,
        "candidates": evaluated,
        "structural_support_evaluation": support_result,
        "cad_source_generated": cad_source is not None,
        "cad_source": cad_source,
        "status": "candidate_study_only",
        "design_freeze": False,
        "physical_fit_certified": False,
        "limitations": [
            "WP-18 synthesis is restricted to one external spur mesh per declared mesh spec.",
            "Candidate schedules are bounded mathematical combinations, not optimized watch designs.",
            "No module, tooth bounds, source RPM, tolerances, coordinates or bearing dimensions are defaulted.",
            "No undercut, contact ratio, tooth form, strength, backlash, interference, wear or manufacturability proof.",
            "No torque, efficiency, lubrication, dynamic load, amplitude, rate or reserve proof.",
            "Support and CAD results remain input-register checks, not structural or physical certification.",
        ],
    }
