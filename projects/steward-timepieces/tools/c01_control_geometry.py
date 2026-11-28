"""WP-58 evidence-gated chronograph control geometry and dimensioning tools.

All geometry is explicit input in mm/degrees with provenance. No defaults are
C-01 dimensions. Calculations are nominal/screening only, not CAD certification.
"""
from __future__ import annotations
import math

class GeometryDefinitionError(ValueError):
    pass

CANDIDATES={"column_wheel","cam_lever"}
REQUIRED_DATUMS={"M0","XY_ORIGIN","Z_REFERENCE","ANGULAR_ZERO"}
REQUIRED_FEATURE_ROLES={
 "control_axis","pusher_contact","clutch_command_contact","retention_contact",
 "reset_command_contact","reset_hammer_pivot","heart_cam_axis","interlock_contact",
 "return_element_anchor","structural_support_reference"
}
REQUIRED_GEOMETRY_CLASSES={"component_envelope","axis_and_pivot","working_profile",
 "contact_interface","spring_interface","axial_stack","clearance_pair"}
def _text(v,n):
 if not isinstance(v,str) or not v.strip(): raise GeometryDefinitionError(f"{n} is required")
 return v
def _num(v,n):
 if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
  raise GeometryDefinitionError(f"{n} must be finite numeric")
 return float(v)
def _positive(v,n):
 x=_num(v,n)
 if x<=0: raise GeometryDefinitionError(f"{n} must be positive")
 return x
def _nonnegative(v,n):
 x=_num(v,n)
 if x<0: raise GeometryDefinitionError(f"{n} must be non-negative")
 return x

def validate_datums(datums):
 if not isinstance(datums,list) or not datums: raise GeometryDefinitionError("datums required")
 ids=[_text(d.get("datum_id"),"datum_id") for d in datums]
 if len(ids)!=len(set(ids)) or set(ids)!=REQUIRED_DATUMS:
  raise GeometryDefinitionError("exactly the four required datum references must be defined")
 for d in datums:
  for f in ("definition","realization_method","evidence_id","source_revision","approval_reference"):
   _text(d.get(f),f"datum.{f}")
  if d.get("status") not in ("proposed","reviewed","approved"):
   raise GeometryDefinitionError("invalid datum status")
 return {"datum_ids":sorted(ids),"all_approved":all(d["status"]=="approved" for d in datums)}

def validate_dimensions(dimensions):
 if not isinstance(dimensions,list) or not dimensions: raise GeometryDefinitionError("dimension register required")
 ids=[_text(d.get("dimension_id"),"dimension_id") for d in dimensions]
 if len(ids)!=len(set(ids)): raise GeometryDefinitionError("dimension IDs must be unique")
 for d in dimensions:
  for f in ("component_id","characteristic","unit","evidence_id","source_revision","drawing_ref"):
   _text(d.get(f),f"dimension.{f}")
  if d["unit"] not in ("mm","deg","N","N_mm","N_per_mm"):
   raise GeometryDefinitionError("unsupported controlled engineering unit")
  nominal=_num(d.get("nominal"),"nominal")
  lower=_nonnegative(d.get("lower_deviation"),"lower_deviation")
  upper=_nonnegative(d.get("upper_deviation"),"upper_deviation")
  if d.get("deviation_convention")!="bilateral_magnitudes":
   raise GeometryDefinitionError("deviations must be explicit bilateral magnitudes")
  lo,hi=nominal-lower,nominal+upper
  if d.get("require_positive") is True and lo<=0:
   raise GeometryDefinitionError("dimension tolerance interval crosses or reaches zero")
  if d.get("status") not in ("tbd","candidate","reviewed","approved"):
   raise GeometryDefinitionError("invalid dimension status")
 return {"dimension_count":len(ids),"dimension_ids":ids,
  "approved_dimensions":sum(d["status"]=="approved" for d in dimensions)}

def validate_features(features, datum_ids):
 if not isinstance(features,list) or not features: raise GeometryDefinitionError("feature register required")
 ids=[_text(f.get("feature_id"),"feature_id") for f in features]
 if len(ids)!=len(set(ids)): raise GeometryDefinitionError("feature IDs must be unique")
 roles={f.get("role") for f in features}
 missing=REQUIRED_FEATURE_ROLES-roles
 if missing: raise GeometryDefinitionError(f"missing feature roles: {sorted(missing)}")
 for f in features:
  for k in ("component_id","role","datum_id","evidence_id","source_revision","definition"):
   _text(f.get(k),f"feature.{k}")
  if f["datum_id"] not in datum_ids: raise GeometryDefinitionError("feature references unknown datum")
  p=f.get("position_mm")
  if not isinstance(p,dict): raise GeometryDefinitionError("position_mm required")
  for axis in ("x","y","z"): _num(p.get(axis),f"position.{axis}")
  if f.get("orientation_deg") is not None: _num(f["orientation_deg"],"orientation_deg")
  if f.get("status") not in ("tbd","candidate","reviewed","approved"):
   raise GeometryDefinitionError("invalid feature status")
 return {"feature_count":len(ids),"roles_present":sorted(roles),"missing_roles":[]}

def tolerance_interval(nominal, lower_deviation, upper_deviation):
 n=_num(nominal,"nominal"); lo=_nonnegative(lower_deviation,"lower_deviation")
 hi=_nonnegative(upper_deviation,"upper_deviation")
 return (n-lo,n+hi)

def worst_case_stack(terms, evidence_id, source_revision):
 _text(evidence_id,"evidence_id"); _text(source_revision,"source_revision")
 if not isinstance(terms,list) or not terms: raise GeometryDefinitionError("stack terms required")
 low=high=0.0
 for t in terms:
  _text(t.get("dimension_id"),"dimension_id")
  sign=t.get("sign")
  if sign not in (-1,1): raise GeometryDefinitionError("stack sign must be -1 or +1")
  a,b=tolerance_interval(t.get("nominal"),t.get("lower_deviation"),t.get("upper_deviation"))
  if sign==1: low+=a; high+=b
  else: low-=b; high-=a
 return {"lower":low,"upper":high,"nominal_midpoint":(low+high)/2,
  "term_count":len(terms),"method":"arithmetic_worst_case","evidence_id":evidence_id,
  "source_revision":source_revision,"correlation_model":"not_assumed"}

def circle_clearance(center_a, radius_a, center_b, radius_b):
 if not isinstance(center_a,(list,tuple)) or len(center_a)!=2: raise GeometryDefinitionError("center_a must be XY")
 if not isinstance(center_b,(list,tuple)) or len(center_b)!=2: raise GeometryDefinitionError("center_b must be XY")
 ax,ay=(_num(center_a[0],"ax"),_num(center_a[1],"ay"))
 bx,by=(_num(center_b[0],"bx"),_num(center_b[1],"by"))
 ra=_nonnegative(radius_a,"radius_a"); rb=_nonnegative(radius_b,"radius_b")
 center=math.hypot(bx-ax,by-ay)
 return {"center_distance_mm":center,"nominal_signed_clearance_mm":center-ra-rb,
  "overlap_or_contact":center-ra-rb<=0,
  "limitation":"2D circular envelope only; axial separation and swept motion not evaluated"}

def lever_geometry(input_arm_mm, output_arm_mm, input_angle_deg, output_angle_deg,
                   input_travel_mm, lost_motion_mm=0.0):
 ri=_positive(input_arm_mm,"input_arm_mm"); ro=_positive(output_arm_mm,"output_arm_mm")
 ai=math.radians(_num(input_angle_deg,"input_angle_deg"))
 ao=math.radians(_num(output_angle_deg,"output_angle_deg"))
 travel=_positive(input_travel_mm,"input_travel_mm")
 lost=_nonnegative(lost_motion_mm,"lost_motion_mm")
 if lost>=travel: raise GeometryDefinitionError("lost motion must be less than input travel")
 # Effective perpendicular moment arms for planar point-force geometry.
 mi=ri*abs(math.sin(ai)); mo=ro*abs(math.sin(ao))
 if mi<=0 or mo<=0: raise GeometryDefinitionError("lever force line has zero effective moment arm")
 return {"input_effective_arm_mm":mi,"output_effective_arm_mm":mo,
  "ideal_force_ratio":mi/mo,"ideal_output_travel_mm":(travel-lost)*mo/mi,
  "input_travel_mm":travel,"lost_motion_mm":lost,
  "assumption":"rigid planar lever, quasi-static, no friction or elastic deflection"}

def validate_spring_interface(record):
 for f in ("interface_id","component_id","anchor_feature_id","moving_feature_id",
           "spring_type","evidence_id","source_revision","drawing_ref"):
  _text(record.get(f),f"spring.{f}")
 if record["anchor_feature_id"]==record["moving_feature_id"]:
  raise GeometryDefinitionError("spring anchor and moving feature must differ")
 if record.get("status") not in ("tbd","candidate","reviewed","approved"):
  raise GeometryDefinitionError("invalid spring interface status")
 endpoints=record.get("endpoint_coordinates_mm")
 if not isinstance(endpoints,list) or len(endpoints)!=2:
  raise GeometryDefinitionError("two explicit spring endpoint coordinates required")
 for p in endpoints:
  if not isinstance(p,dict): raise GeometryDefinitionError("spring endpoint must be object")
  for a in ("x","y","z"): _num(p.get(a),f"spring endpoint {a}")
 if record.get("spring_rate_n_per_mm") is not None:
  _positive(record["spring_rate_n_per_mm"],"spring_rate_n_per_mm")
 if record.get("preload_n") is not None: _nonnegative(record["preload_n"],"preload_n")
 return {"interface_id":record["interface_id"],"endpoint_distance_mm":math.dist(
  [endpoints[0]["x"],endpoints[0]["y"],endpoints[0]["z"]],
  [endpoints[1]["x"],endpoints[1]["y"],endpoints[1]["z"]]),
  "spring_rate_defined":record.get("spring_rate_n_per_mm") is not None,
  "preload_defined":record.get("preload_n") is not None}

def validate_profile(points):
 if not isinstance(points,list) or len(points)<3: raise GeometryDefinitionError("profile needs at least three XY points")
 pts=[]
 for p in points:
  if not isinstance(p,(list,tuple)) or len(p)!=2: raise GeometryDefinitionError("profile point must be XY")
  pts.append((_num(p[0],"profile.x"),_num(p[1],"profile.y")))
 if len(set(pts))!=len(pts): raise GeometryDefinitionError("profile vertices must be unique")
 def orient(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 def on(a,b,p): return min(a[0],b[0])<=p[0]<=max(a[0],b[0]) and min(a[1],b[1])<=p[1]<=max(a[1],b[1]) and abs(orient(a,b,p))<1e-12
 def intersect(a,b,c,d):
  o1,o2,o3,o4=orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
  if o1*o2<0 and o3*o4<0: return True
  return (abs(o1)<1e-12 and on(a,b,c)) or (abs(o2)<1e-12 and on(a,b,d)) or (abs(o3)<1e-12 and on(c,d,a)) or (abs(o4)<1e-12 and on(c,d,b))
 n=len(pts)
 for i in range(n):
  a,b=pts[i],pts[(i+1)%n]
  for j in range(i+1,n):
   if j==i or j==(i+1)%n or (j+1)%n==i: continue
   if intersect(a,b,pts[j],pts[(j+1)%n]): raise GeometryDefinitionError("profile self-intersects")
 area=sum(pts[i][0]*pts[(i+1)%n][1]-pts[(i+1)%n][0]*pts[i][1] for i in range(n))/2
 if abs(area)<1e-12: raise GeometryDefinitionError("profile area must be nonzero")
 return {"vertex_count":n,"signed_area_mm2":area,"self_intersection_detected":False}

def evaluate_candidate_geometry(package):
 cid=package.get("candidate_id")
 if cid not in CANDIDATES: raise GeometryDefinitionError("candidate_id invalid")
 for f in ("package_id","configuration_revision","requirements_revision","evidence_id","source_revision","owner"):
  _text(package.get(f),f"package.{f}")
 datums=validate_datums(package.get("datums"))
 datum_ids={d["datum_id"] for d in package["datums"]}
 dims=validate_dimensions(package.get("dimensions"))
 features=validate_features(package.get("features"),datum_ids)
 spring=package.get("spring_interfaces")
 if not isinstance(spring,list): raise GeometryDefinitionError("spring_interfaces list required")
 spring_results=[validate_spring_interface(s) for s in spring]
 profiles=package.get("profiles")
 if not isinstance(profiles,list): raise GeometryDefinitionError("profiles list required")
 profile_results=[]
 for p in profiles:
  for f in ("profile_id","component_id","evidence_id","source_revision","drawing_ref"):
   _text(p.get(f),f"profile.{f}")
  profile_results.append({"profile_id":p["profile_id"],**validate_profile(p.get("points_mm"))})
 clearances=package.get("clearance_pairs")
 if not isinstance(clearances,list): raise GeometryDefinitionError("clearance_pairs list required")
 clearance_results=[]
 for c in clearances:
  for f in ("pair_id","evidence_id","source_revision","axial_review_ref"):
   _text(c.get(f),f"clearance.{f}")
  if c.get("axial_overlap_reviewed") is not True:
   raise GeometryDefinitionError("clearance pair requires explicit axial-overlap review")
  clearance_results.append({"pair_id":c["pair_id"],**circle_clearance(
   c.get("center_a_mm"),c.get("radius_a_mm"),c.get("center_b_mm"),c.get("radius_b_mm"))})
 return {"candidate_id":cid,"datum_summary":datums,"dimension_summary":dims,
  "feature_summary":features,"spring_interface_results":spring_results,
  "profile_results":profile_results,"clearance_results":clearance_results,
  "geometry_record_valid":True,"all_datums_approved":datums["all_approved"],
  "physical_fit_certified":False,"tolerance_compliance_certified":False,
  "motion_contact_certified":False,"manufacturing_release_authorized":False,
  "limitations":["nominal geometry only where not otherwise specified",
   "circle envelopes do not represent complete solids","no swept-volume or dynamic contact solver",
   "no strength, fatigue, wear, lubrication, shock or manufacturing capability analysis",
   "no physical fit or tolerance compliance certification"]}

def evaluate_geometry_set(packet):
 for f in ("geometry_set_id","revision","evidence_id","source_revision","owner"):
  _text(packet.get(f),f"geometry_set.{f}")
 baseline=packet.get("common_baseline")
 if not isinstance(baseline,dict): raise GeometryDefinitionError("common baseline required")
 for f in ("requirements_revision","movement_datum_revision","interface_baseline_revision"):
  _text(baseline.get(f),f"baseline.{f}")
 packages=packet.get("candidates")
 if not isinstance(packages,dict) or set(packages)!=CANDIDATES:
  raise GeometryDefinitionError("both CW and CL geometry packages required")
 results={}
 for cid in sorted(CANDIDATES):
  p=packages[cid]
  if p.get("requirements_revision")!=baseline["requirements_revision"]:
   raise GeometryDefinitionError("candidate requirements baseline mismatch")
  if p.get("movement_datum_revision")!=baseline["movement_datum_revision"]:
   raise GeometryDefinitionError("candidate datum baseline mismatch")
  if p.get("interface_baseline_revision")!=baseline["interface_baseline_revision"]:
   raise GeometryDefinitionError("candidate interface baseline mismatch")
  results[cid]=evaluate_candidate_geometry(p)
 return {"geometry_set_id":packet["geometry_set_id"],"candidate_results":results,
  "common_baseline_match":True,"both_geometry_records_valid":True,
  "physical_equivalence_proven":False,"architecture_selected":False,
  "clutch_selected":False,"design_frozen":False,"manufacturing_release_authorized":False}
