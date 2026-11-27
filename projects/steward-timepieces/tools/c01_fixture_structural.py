"""WP-48 structural screening and metrology qualification calculations.
Inputs must be measured or approved engineering data with provenance.
Beam equations are idealized screening models, not FEA or certification.
"""
from __future__ import annotations
import math

class FixtureEngineeringError(ValueError):
    pass

def _num(value, name, positive=False, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise FixtureEngineeringError(f"{name} must be finite numeric")
    if positive and value <= 0: raise FixtureEngineeringError(f"{name} must be positive")
    if nonnegative and value < 0: raise FixtureEngineeringError(f"{name} must be nonnegative")
    return float(value)

def _provenance(record):
    if not isinstance(record.get("evidence_id"), str) or not record["evidence_id"].strip():
        raise FixtureEngineeringError("evidence_id is required")
    if not isinstance(record.get("source_revision"), str) or not record["source_revision"].strip():
        raise FixtureEngineeringError("source_revision is required")

def beam_screen(load_n, span_mm, elastic_modulus_mpa, second_moment_mm4,
                extreme_fiber_mm, support_case, evidence_id, source_revision):
    """Euler-Bernoulli point-load screen: cantilever end or simply-supported center."""
    f=_num(load_n,"load_n",nonnegative=True); length=_num(span_mm,"span_mm",positive=True)
    e=_num(elastic_modulus_mpa,"elastic_modulus_mpa",positive=True)
    inertia=_num(second_moment_mm4,"second_moment_mm4",positive=True)
    c=_num(extreme_fiber_mm,"extreme_fiber_mm",positive=True)
    if support_case not in {"cantilever_end","simply_supported_center"}:
        raise FixtureEngineeringError("unsupported support_case")
    if not evidence_id or not source_revision: raise FixtureEngineeringError("provenance required")
    if support_case=="cantilever_end":
        delta=f*length**3/(3*e*inertia); moment=f*length
    else:
        delta=f*length**3/(48*e*inertia); moment=f*length/4
    stress=moment*c/inertia
    return {"support_case":support_case,"load_n":f,"span_mm":length,"deflection_mm":delta,
      "linear_stiffness_n_per_mm":(f/delta if delta else math.inf),
      "nominal_bending_stress_mpa":stress,"evidence_id":evidence_id,"source_revision":source_revision,
      "model":"small-deflection Euler-Bernoulli beam, ideal boundary conditions",
      "limitations":["No shear deformation, local contact stress, joint slip, fastener compliance or stress concentration.",
      "No fatigue, buckling, vibration, dynamic amplification, material allowable or safety factor.",
      "Actual fixture geometry and boundary conditions require independent engineering review."]}

def compliance_correction(measured_travel_mm,force_n,fixture_compliance_mm_per_n,evidence_id,source_revision):
    travel=_num(measured_travel_mm,"measured_travel_mm",nonnegative=True)
    force=_num(force_n,"force_n",nonnegative=True)
    compliance=_num(fixture_compliance_mm_per_n,"fixture_compliance_mm_per_n",nonnegative=True)
    if not evidence_id or not source_revision: raise FixtureEngineeringError("provenance required")
    flex=force*compliance
    if flex>travel: raise FixtureEngineeringError("estimated fixture deflection exceeds measured travel")
    return {"measured_travel_mm":travel,"estimated_fixture_deflection_mm":flex,
      "corrected_mechanism_travel_mm":travel-flex,"evidence_id":evidence_id,"source_revision":source_revision,
      "sign_convention":"same-direction fixture deflection is subtracted",
      "limitations":["Valid only for declared load path and measured compliance.",
      "Hysteresis, nonlinear compliance, side loading and dynamic effects need separate evidence."]}

def uncertainty_budget(components,coverage_factor,evidence_id,source_revision):
    if not isinstance(components,list) or not components: raise FixtureEngineeringError("components must be non-empty")
    k=_num(coverage_factor,"coverage_factor",positive=True)
    if not evidence_id or not source_revision: raise FixtureEngineeringError("budget provenance required")
    ids=set(); total=0.0; clean=[]
    for i,item in enumerate(components):
        ident=item.get("component_id")
        if not ident or ident in ids: raise FixtureEngineeringError(f"component {i} has blank or duplicate ID")
        ids.add(ident); value=_num(item.get("standard_uncertainty"),f"{ident}.standard_uncertainty",nonnegative=True)
        _provenance(item); total+=value*value
        clean.append({"component_id":ident,"standard_uncertainty":value,
          "evidence_id":item["evidence_id"],"source_revision":item["source_revision"]})
    combined=math.sqrt(total)
    return {"components":clean,"combined_standard_uncertainty":combined,"coverage_factor":k,
      "expanded_uncertainty":k*combined,"combination":"RSS; assumes independent contributions",
      "evidence_id":evidence_id,"source_revision":source_revision,
      "limitations":["Correlated inputs require covariance terms; not handled by this RSS calculation.",
      "Coverage probability depends on distributions, degrees of freedom and selected factor."]}

def guardband_result(measured_value,expanded_uncertainty,lower_limit,upper_limit,evidence_id,source_revision):
    value=_num(measured_value,"measured_value"); u=_num(expanded_uncertainty,"expanded_uncertainty",nonnegative=True)
    low=_num(lower_limit,"lower_limit"); high=_num(upper_limit,"upper_limit")
    if low>high: raise FixtureEngineeringError("lower_limit must not exceed upper_limit")
    if not evidence_id or not source_revision: raise FixtureEngineeringError("provenance required")
    interval=[value-u,value+u]
    if interval[0]>=low and interval[1]<=high: status="pass"
    elif interval[1]<low or interval[0]>high: status="fail"
    else: status="indeterminate"
    return {"status":status,"measured_value":value,"uncertainty_interval":interval,
      "approved_limits":[low,high],"evidence_id":evidence_id,"source_revision":source_revision,
      "rule":"pass only when full expanded-uncertainty interval lies within approved limits"}

def datum_transfer_repeatability(observations,evidence_id,source_revision):
    if not isinstance(observations,list) or len(observations)<2:
        raise FixtureEngineeringError("at least two observations required")
    values=[_num(v,f"observation[{i}]") for i,v in enumerate(observations)]
    mean=sum(values)/len(values); variance=sum((v-mean)**2 for v in values)/(len(values)-1)
    return {"observation_count":len(values),"mean":mean,"sample_standard_deviation":math.sqrt(variance),
      "minimum":min(values),"maximum":max(values),"range":max(values)-min(values),
      "evidence_id":evidence_id,"source_revision":source_revision,
      "limitations":["Scalar repeatability only; does not establish datum accuracy or full 3D registration.",
      "Resolution, calibration, environmental effects and outliers require review."]}

def validate_qualification_packet(packet):
    errors=[]
    for key in ("fixture_id","configuration_revision","evidence_id","source_revision"):
        if not packet.get(key): errors.append(f"missing {key}")
    for section in ("base_analysis","carrier_analysis","datum_transfer","force_path","metrology","guard_review","independent_review"):
        record=packet.get(section)
        if not isinstance(record,dict): errors.append(f"missing {section}"); continue
        if record.get("status")!="approved": errors.append(f"{section} is not approved")
        if not record.get("evidence_id") or not record.get("source_revision"):
            errors.append(f"{section} lacks evidence provenance")
    return {"complete_for_review":not errors,"errors":errors,"fixture_physically_qualified":False,
      "test_release_authorized":False,"note":"Packet completeness is not physical qualification or authorization."}
