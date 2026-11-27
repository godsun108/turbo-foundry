"""Evidence-gated nominal gear, arbor, bearing and tolerance calculations for STEWARD C-01.

This module deliberately calculates only from explicit inputs. It is not a gear
strength, tooth-form, bearing-life, manufacturability or physical-fit solver.
"""
from __future__ import annotations
from math import cos, radians, isfinite
from fractions import Fraction

class EngineeringInputError(ValueError):
    pass

def _finite_positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
        raise EngineeringInputError(f"{name} must be finite and > 0")
    return float(value)

def _finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise EngineeringInputError(f"{name} must be finite")
    return float(value)

def validate_provenance(record):
    if not isinstance(record, dict):
        raise EngineeringInputError("record must be a mapping")
    for key in ("evidence_id", "source_revision"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise EngineeringInputError(f"{key} is required")

def gear_geometry(*, module_mm, teeth, pressure_angle_deg, evidence_id, source_revision,
                  profile_shift=None, addendum_coefficient=None, dedendum_coefficient=None):
    """Return nominal spur-gear reference geometry; no tooth profile is generated."""
    validate_provenance({"evidence_id": evidence_id, "source_revision": source_revision})
    m = _finite_positive(module_mm, "module_mm")
    if isinstance(teeth, bool) or not isinstance(teeth, int) or teeth < 1:
        raise EngineeringInputError("teeth must be a positive integer")
    alpha = _finite(pressure_angle_deg, "pressure_angle_deg")
    if not 0 < alpha < 90:
        raise EngineeringInputError("pressure_angle_deg must be between 0 and 90")
    d = m * teeth
    result = {
        "module_mm": m, "teeth": teeth, "pressure_angle_deg": alpha,
        "pitch_diameter_mm": d, "pitch_radius_mm": d / 2,
        "base_diameter_mm": d * cos(radians(alpha)),
        "evidence_id": evidence_id, "source_revision": source_revision,
        "tooth_form_status": "NOT_GENERATED"
    }
    optional = (("profile_shift", profile_shift), ("addendum_coefficient", addendum_coefficient),
                ("dedendum_coefficient", dedendum_coefficient))
    for name, value in optional:
        if value is not None:
            result[name] = _finite(value, name)
    if addendum_coefficient is not None:
        x = 0.0 if profile_shift is None else _finite(profile_shift, "profile_shift")
        result["addendum_diameter_mm"] = d + 2*m*(addendum_coefficient + x)
    if dedendum_coefficient is not None:
        x = 0.0 if profile_shift is None else _finite(profile_shift, "profile_shift")
        result["dedendum_diameter_mm"] = d - 2*m*(dedendum_coefficient - x)
    return result

def mesh_center_distance(*, gear_a, gear_b, mesh_type, center_distance_tolerance_mm=None):
    """Nominal reference center distance for explicitly declared standard spur meshes."""
    if mesh_type not in ("external", "internal"):
        raise EngineeringInputError("mesh_type must be external or internal")
    for g in (gear_a, gear_b):
        if not isinstance(g, dict) or "module_mm" not in g or "teeth" not in g:
            raise EngineeringInputError("each gear needs module_mm and teeth")
    ma = _finite_positive(gear_a["module_mm"], "gear_a.module_mm")
    mb = _finite_positive(gear_b["module_mm"], "gear_b.module_mm")
    if ma != mb:
        raise EngineeringInputError("matching module is required for this nominal mesh calculation")
    za, zb = gear_a["teeth"], gear_b["teeth"]
    if any(isinstance(z, bool) or not isinstance(z, int) or z < 1 for z in (za, zb)):
        raise EngineeringInputError("tooth counts must be positive integers")
    if mesh_type == "internal" and za <= zb:
        raise EngineeringInputError("internal gear tooth count must exceed pinion tooth count")
    center = ma * (za + zb) / 2 if mesh_type == "external" else ma * (za - zb) / 2
    out = {"mesh_type": mesh_type, "nominal_center_distance_mm": center,
           "nominal_only": True}
    if center_distance_tolerance_mm is not None:
        out["center_distance_tolerance_mm"] = _finite_positive(center_distance_tolerance_mm, "center_distance_tolerance_mm")
        out["acceptance_status"] = "REQUIRES_MEASURED_OR_DESIGNED_CENTER_DISTANCE"
    return out

def signed_ratio(meshes):
    """Exact signed speed ratio for ordered simple meshes; external reverses direction."""
    ratio = Fraction(1, 1)
    for mesh in meshes:
        driver, driven = mesh.get("driver_teeth"), mesh.get("driven_teeth")
        if any(isinstance(z, bool) or not isinstance(z, int) or z < 1 for z in (driver, driven)):
            raise EngineeringInputError("each mesh needs positive integer driver_teeth and driven_teeth")
        kind = mesh.get("mesh_type")
        if kind not in ("external", "internal"):
            raise EngineeringInputError("mesh_type must be external or internal")
        ratio *= Fraction(driver, driven) * (-1 if kind == "external" else 1)
    return {"output_over_input": ratio, "decimal": float(ratio)}

def fit_clearance(*, bore_min_mm, bore_max_mm, shaft_min_mm, shaft_max_mm,
                  evidence_id, source_revision):
    """Worst-case diametral clearance interval from explicit size limits."""
    validate_provenance({"evidence_id": evidence_id, "source_revision": source_revision})
    vals = {k: _finite_positive(v, k) for k, v in {
        "bore_min_mm": bore_min_mm, "bore_max_mm": bore_max_mm,
        "shaft_min_mm": shaft_min_mm, "shaft_max_mm": shaft_max_mm}.items()}
    if vals["bore_min_mm"] > vals["bore_max_mm"] or vals["shaft_min_mm"] > vals["shaft_max_mm"]:
        raise EngineeringInputError("minimum size must not exceed maximum size")
    return {
        "minimum_diametral_clearance_mm": vals["bore_min_mm"] - vals["shaft_max_mm"],
        "maximum_diametral_clearance_mm": vals["bore_max_mm"] - vals["shaft_min_mm"],
        "evidence_id": evidence_id, "source_revision": source_revision,
        "fit_classification": "NOT_ASSIGNED"
    }

def tolerance_stack(terms):
    """Worst-case signed linear stack. Each term: nominal_mm, tolerance_plus_mm, tolerance_minus_mm, sign."""
    if not isinstance(terms, list) or not terms:
        raise EngineeringInputError("terms must be a non-empty list")
    nominal = low = high = 0.0
    for term in terms:
        n = _finite(term.get("nominal_mm"), "nominal_mm")
        plus = _finite(term.get("tolerance_plus_mm"), "tolerance_plus_mm")
        minus = _finite(term.get("tolerance_minus_mm"), "tolerance_minus_mm")
        sign = term.get("sign", 1)
        if plus < 0 or minus < 0 or sign not in (-1, 1):
            raise EngineeringInputError("tolerances must be nonnegative and sign must be -1 or 1")
        nominal += sign*n
        if sign == 1:
            low += n-minus; high += n+plus
        else:
            low -= n+plus; high -= n-minus
    return {"nominal_mm": nominal, "worst_case_min_mm": low,
            "worst_case_max_mm": high, "method": "ARITHMETIC_WORST_CASE"}

def validate_arbor_register(arbors, supports):
    if not isinstance(arbors, list) or not isinstance(supports, list):
        raise EngineeringInputError("arbors and supports must be lists")
    ids = [a.get("arbor_id") for a in arbors]
    if any(not isinstance(x, str) or not x for x in ids) or len(ids) != len(set(ids)):
        raise EngineeringInputError("arbor IDs must be non-empty and unique")
    support_ids = set()
    for s in supports:
        validate_provenance(s)
        sid, aid = s.get("support_id"), s.get("arbor_id")
        if not sid or sid in support_ids or aid not in ids:
            raise EngineeringInputError("support IDs must be unique and reference a declared arbor")
        support_ids.add(sid)
        if s.get("support_type") not in ("jewel_bearing", "bushing", "plain_bearing", "other"):
            raise EngineeringInputError("unsupported or missing support_type")
        for field in ("bore_diameter_mm", "shaft_diameter_mm"):
            _finite_positive(s.get(field), field)
        if s.get("axial_position_mm") is not None:
            _finite(s["axial_position_mm"], "axial_position_mm")
    return {"arbor_count": len(arbors), "support_count": len(supports),
            "status": "REGISTER_VALIDATION_ONLY"}

def validate_axial_stack(planes):
    """Validate explicit axial planes and return interval overlaps; no inferred clearance."""
    if not isinstance(planes, list):
        raise EngineeringInputError("planes must be a list")
    seen = set()
    normalized = []
    for p in planes:
        pid = p.get("plane_id")
        if not isinstance(pid, str) or not pid or pid in seen:
            raise EngineeringInputError("plane IDs must be unique")
        seen.add(pid); validate_provenance(p)
        z0 = _finite(p.get("z_min_mm"), "z_min_mm")
        z1 = _finite(p.get("z_max_mm"), "z_max_mm")
        if z1 < z0:
            raise EngineeringInputError("z_max_mm must be >= z_min_mm")
        normalized.append((pid, z0, z1))
    overlaps = []
    for i, a in enumerate(normalized):
        for b in normalized[i+1:]:
            overlaps.append({"plane_a": a[0], "plane_b": b[0],
                             "overlap_mm": max(0.0, min(a[2], b[2])-max(a[1], b[1]))})
    return {"pairwise_intervals": overlaps, "clearance_certified": False}
