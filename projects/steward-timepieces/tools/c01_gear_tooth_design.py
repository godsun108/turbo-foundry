"""Evidence-gated involute spur-gear geometry and mesh screening for C-01.

External, parallel-axis, involute spur gears only. Outputs are analytical
screening data, not a certified gear design or manufacturing tooth profile.
"""
from __future__ import annotations
from math import acos, cos, isfinite, pi, sin, sqrt, tan
from fractions import Fraction

class GearDesignInputError(ValueError):
    pass

def _positive(v, name):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v) or v <= 0:
        raise GearDesignInputError(f"{name} must be finite and positive")
    return float(v)

def _finite(v, name):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v):
        raise GearDesignInputError(f"{name} must be finite")
    return float(v)

def _provenance(evidence_id, source_revision):
    if not isinstance(evidence_id, str) or not evidence_id.strip():
        raise GearDesignInputError("evidence_id is required")
    if not isinstance(source_revision, str) or not source_revision.strip():
        raise GearDesignInputError("source_revision is required")

def involute_function(angle_rad):
    """Involute function inv(alpha)=tan(alpha)-alpha; angle in radians."""
    a = _finite(angle_rad, "angle_rad")
    if not 0 <= a < pi/2:
        raise GearDesignInputError("angle_rad must be in [0, pi/2)")
    return tan(a) - a

def gear_parameters(*, module_mm, teeth, pressure_angle_deg, addendum_coefficient,
                    dedendum_coefficient, profile_shift, evidence_id, source_revision):
    _provenance(evidence_id, source_revision)
    m = _positive(module_mm, "module_mm")
    if isinstance(teeth, bool) or not isinstance(teeth, int) or teeth < 1:
        raise GearDesignInputError("teeth must be a positive integer")
    alpha_deg = _finite(pressure_angle_deg, "pressure_angle_deg")
    if not 0 < alpha_deg < 45:
        raise GearDesignInputError("pressure_angle_deg must be between 0 and 45 degrees for this model")
    ha = _positive(addendum_coefficient, "addendum_coefficient")
    hf = _positive(dedendum_coefficient, "dedendum_coefficient")
    x = _finite(profile_shift, "profile_shift")
    alpha = alpha_deg*pi/180
    rp = m*teeth/2
    rb = rp*cos(alpha)
    ra = rp + m*(ha+x)
    rf = rp - m*(hf-x)
    if ra <= rb:
        raise GearDesignInputError("addendum radius must exceed base radius for involute tip geometry")
    if rf <= 0:
        raise GearDesignInputError("root radius must be positive")
    alpha_a = acos(max(-1.0, min(1.0, rb/ra)))
    theta_pitch = pi/(2*teeth) + 2*x*tan(alpha) + involute_function(alpha) - involute_function(alpha_a)
    tip_thickness = 2*ra*theta_pitch
    return {
        "module_mm":m,"teeth":teeth,"pressure_angle_deg":alpha_deg,
        "addendum_coefficient":ha,"dedendum_coefficient":hf,"profile_shift":x,
        "pitch_radius_mm":rp,"base_radius_mm":rb,"addendum_radius_mm":ra,
        "root_radius_mm":rf,"pitch_diameter_mm":2*rp,"base_diameter_mm":2*rb,
        "addendum_diameter_mm":2*ra,"root_diameter_mm":2*rf,
        "base_pitch_mm":pi*m*cos(alpha),
        "tip_pressure_angle_deg":alpha_a*180/pi,
        "calculated_tip_thickness_mm":tip_thickness,
        "evidence_id":evidence_id,"source_revision":source_revision,
        "geometry_class":"ANALYTICAL_INVOLUTE_SCREENING"
    }

def involute_points(*, base_radius_mm, addendum_radius_mm, flank_points=16):
    """One involute flank from base circle to addendum circle, local XY coordinates."""
    rb = _positive(base_radius_mm,"base_radius_mm")
    ra = _positive(addendum_radius_mm,"addendum_radius_mm")
    if ra <= rb:
        raise GearDesignInputError("addendum radius must exceed base radius")
    if isinstance(flank_points,bool) or not isinstance(flank_points,int) or flank_points < 2 or flank_points > 1000:
        raise GearDesignInputError("flank_points must be an integer from 2 to 1000")
    tmax=sqrt((ra/rb)**2-1)
    points=[]
    for i in range(flank_points):
        t=tmax*i/(flank_points-1)
        x=rb*(cos(t)+t*sin(t))
        y=rb*(sin(t)-t*cos(t))
        points.append((x,y))
    return {"points_xy_mm":points,"point_count":len(points),
            "profile_status":"SINGLE_INVOLUTE_FLANK_ONLY_NOT_COMPLETE_TOOTH"}

def external_mesh_screen(*, gear_a, gear_b, center_distance_mm=None,
                         minimum_contact_ratio=None, evidence_id=None, source_revision=None):
    """Analytical transverse contact ratio and undercut screening for external spur pair."""
    for g in (gear_a,gear_b):
        for key in ("module_mm","teeth","pressure_angle_deg","base_radius_mm","addendum_radius_mm","profile_shift"):
            if key not in g: raise GearDesignInputError(f"gear missing {key}")
    m1=_positive(gear_a["module_mm"],"gear_a.module_mm")
    m2=_positive(gear_b["module_mm"],"gear_b.module_mm")
    if abs(m1-m2)>1e-12: raise GearDesignInputError("compatible equal module required")
    alpha_a = _finite(gear_a["pressure_angle_deg"], "gear_a.pressure_angle_deg")
    alpha_b = _finite(gear_b["pressure_angle_deg"], "gear_b.pressure_angle_deg")
    if abs(alpha_a-alpha_b)>1e-12:
        raise GearDesignInputError("matching reference pressure angles are required")
    z1,z2=gear_a["teeth"],gear_b["teeth"]
    if any(isinstance(z,bool) or not isinstance(z,int) or z<1 for z in (z1,z2)):
        raise GearDesignInputError("tooth counts must be positive integers")
    a0=(m1*(z1+z2))/2
    a=a0 if center_distance_mm is None else _positive(center_distance_mm,"center_distance_mm")
    rb1=_positive(gear_a["base_radius_mm"],"gear_a.base_radius_mm")
    rb2=_positive(gear_b["base_radius_mm"],"gear_b.base_radius_mm")
    ra1=_positive(gear_a["addendum_radius_mm"],"gear_a.addendum_radius_mm")
    ra2=_positive(gear_b["addendum_radius_mm"],"gear_b.addendum_radius_mm")
    if a <= rb1+rb2: raise GearDesignInputError("center distance must exceed sum of base radii")
    alpha_w=acos(max(-1.0,min(1.0,(rb1+rb2)/a)))
    path=sqrt(ra1**2-rb1**2)+sqrt(ra2**2-rb2**2)-a*sin(alpha_w)
    base_pitch=pi*m1*cos(radians(gear_a["pressure_angle_deg"]))
    if path <= 0:
        raise GearDesignInputError("non-positive path of contact; pair geometry is not viable under this model")
    eps=path/base_pitch
    out={
      "nominal_reference_center_distance_mm":a0,
      "evaluated_center_distance_mm":a,
      "working_pressure_angle_deg":alpha_w*180/pi,
      "transverse_contact_ratio":eps,
      "base_pitch_mm":base_pitch,
      "path_of_contact_mm":path,
      "screening_status":"CALCULATED_NOT_CERTIFIED"
    }
    # Classical zero-shift, standard full-depth rack estimate only.
    alpha_deg=_finite(gear_a["pressure_angle_deg"],"pressure_angle_deg")
    alpha=alpha_deg*pi/180
    for label,g in (("gear_a",gear_a),("gear_b",gear_b)):
        z=g["teeth"]; x=_finite(g["profile_shift"],f"{label}.profile_shift")
        zmin=2/(sin(alpha)**2)
        out[label+"_zero_shift_undercut_screen"]={
          "theoretical_min_teeth_zero_shift_full_depth":zmin,
          "actual_teeth":z,
          "profile_shift":x,
          "zero_shift_screen":"POTENTIAL_UNDERCUT_RISK" if z<zmin and x<=0 else "NOT_FLAGGED_BY_SIMPLE_ZERO_SHIFT_SCREEN",
          "limitation":"not a substitute for rack-generation/interference analysis"
        }
    if minimum_contact_ratio is not None:
        threshold=_positive(minimum_contact_ratio,"minimum_contact_ratio")
        out["contact_ratio_threshold"]=threshold
        out["contact_ratio_screen"]="BELOW_THRESHOLD" if eps<threshold else "AT_OR_ABOVE_THRESHOLD"
    if evidence_id is not None or source_revision is not None:
        _provenance(evidence_id,source_revision)
        out["evidence_id"]=evidence_id; out["source_revision"]=source_revision
    return out

def backlash_record(*, target_backlash_mm, measured_backlash_mm, tolerance_mm,
                    evidence_id, source_revision):
    """Compare an explicitly approved target with a measured backlash result."""
    _provenance(evidence_id,source_revision)
    target=_finite(target_backlash_mm,"target_backlash_mm")
    measured=_finite(measured_backlash_mm,"measured_backlash_mm")
    tol=_positive(tolerance_mm,"tolerance_mm")
    if target<0 or measured<0: raise GearDesignInputError("backlash values must be nonnegative")
    error=measured-target
    return {"target_backlash_mm":target,"measured_backlash_mm":measured,
            "deviation_mm":error,"tolerance_mm":tol,
            "status":"WITHIN_DECLARED_TOLERANCE" if abs(error)<=tol else "OUTSIDE_DECLARED_TOLERANCE",
            "evidence_id":evidence_id,"source_revision":source_revision}

def radians(degrees):
    return degrees*pi/180
