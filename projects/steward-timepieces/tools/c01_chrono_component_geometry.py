"""WP-36 evidence-gated parametric chronograph component geometry and CAD source."""
from __future__ import annotations
from math import isfinite
import re
from typing import Any

_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")

def _n(v: Any, field: str, positive: bool = False) -> float:
    if isinstance(v, bool):
        raise ValueError(f"{field} must be numeric")
    try: x = float(v)
    except (TypeError, ValueError) as exc: raise ValueError(f"{field} must be numeric") from exc
    if not isfinite(x) or (positive and x <= 0):
        raise ValueError(f"{field} must be finite" + (" and positive" if positive else ""))
    return x

def _id(v: Any, field: str) -> str:
    if not isinstance(v, str) or not _ID.fullmatch(v):
        raise ValueError(f"{field} must be a safe identifier")
    return v

def _polygon(points: Any, field: str) -> list[tuple[float,float]]:
    if not isinstance(points, list) or len(points) < 3:
        raise ValueError(f"{field} requires at least three XY vertices")
    out=[]
    for p in points:
        if not isinstance(p,(list,tuple)) or len(p)!=2: raise ValueError(f"{field} vertices must be [x,y]")
        out.append((_n(p[0],field+".x"),_n(p[1],field+".y")))
    if len(set(out)) != len(out): raise ValueError(f"{field} vertices must be unique")
    area=sum(out[i][0]*out[(i+1)%len(out)][1]-out[(i+1)%len(out)][0]*out[i][1] for i in range(len(out)))
    if abs(area)<=1e-12: raise ValueError(f"{field} must enclose non-zero area")
    return out

def validate_component(component: dict[str,Any]) -> dict[str,Any]:
    for f in ("id","role","geometry_type","evidence_id","source_revision"):
        if not component.get(f): raise ValueError(f"component requires {f}")
    _id(component["id"],"component.id")
    if component["geometry_type"] not in ("cylinder","annulus","extruded_polygon"):
        raise ValueError("geometry_type must be cylinder, annulus or extruded_polygon")
    p=component.get("parameters")
    if not isinstance(p,dict): raise ValueError("parameters object is required")
    if component["geometry_type"]=="cylinder":
        _n(p.get("radius_mm"),"radius_mm",True); _n(p.get("height_mm"),"height_mm",True)
    elif component["geometry_type"]=="annulus":
        outer=_n(p.get("outer_radius_mm"),"outer_radius_mm",True)
        inner=_n(p.get("inner_radius_mm"),"inner_radius_mm",True)
        if inner>=outer: raise ValueError("inner radius must be smaller than outer radius")
        _n(p.get("height_mm"),"height_mm",True)
    else:
        _polygon(p.get("outline_xy_mm"),"outline_xy_mm")
        _n(p.get("height_mm"),"height_mm",True)
    pose=component.get("pose")
    if not isinstance(pose,dict): raise ValueError("pose object is required")
    for f in ("x_mm","y_mm","z_mm","rx_deg","ry_deg","rz_deg"):
        _n(pose.get(f), "pose."+f)
    return {"id":component["id"],"role":component["role"],
            "geometry_type":component["geometry_type"],"geometry_complete":True,
            "evidence_id":component["evidence_id"],"source_revision":component["source_revision"]}

def validate_package(package: dict[str,Any]) -> dict[str,Any]:
    for f in ("candidate_id","evidence_id","source_revision"):
        if not package.get(f): raise ValueError(f"package requires {f}")
    parts=package.get("components")
    if not isinstance(parts,list) or not parts: raise ValueError("components must be a non-empty list")
    ids=[]
    for part in parts: validate_component(part); ids.append(part["id"])
    if len(ids)!=len(set(ids)): raise ValueError("component IDs must be unique")
    interfaces=package.get("interfaces",[])
    if not isinstance(interfaces,list): raise ValueError("interfaces must be a list")
    for it in interfaces:
        for f in ("id","component_a","component_b","interface_type","evidence_id","source_revision"):
            if not it.get(f): raise ValueError(f"interface requires {f}")
        _id(it["id"],"interface.id")
        if it["component_a"] not in ids or it["component_b"] not in ids:
            raise ValueError("interface endpoints must reference package components")
        if it["component_a"]==it["component_b"]: raise ValueError("interface endpoints must differ")
    if len({x["id"] for x in interfaces})!=len(interfaces): raise ValueError("interface IDs must be unique")
    return {"candidate_id":package["candidate_id"],"component_count":len(parts),
            "interface_count":len(interfaces),"geometry_complete":True,
            "manufacturing_release":False}

def _f(x: Any) -> str: return format(float(x),".12g")

def generate_component_scad(package: dict[str,Any]) -> str:
    validate_package(package)
    out=["// STEWARD C-01 WP-36 component geometry source",
         "// Candidate geometry only; not a manufacturing drawing.",
         f"// Candidate: {package['candidate_id']}",
         f"// Evidence: {package['evidence_id']}",
         f"// Source revision: {package['source_revision']}","$fn=96;",""]
    for c in package["components"]:
        validate_component(c); p=c["parameters"]; pose=c["pose"]
        out += [f"// {c['id']} | {c['role']} | evidence {c['evidence_id']} | source {c['source_revision']}",
                f"module part_{c['id']}() {{",
                f"  translate([{_f(pose['x_mm'])},{_f(pose['y_mm'])},{_f(pose['z_mm'])}])",
                f"    rotate([{_f(pose['rx_deg'])},{_f(pose['ry_deg'])},{_f(pose['rz_deg'])}]) {{"]
        if c["geometry_type"]=="cylinder":
            out += [f"      cylinder(h={_f(p['height_mm'])},r={_f(p['radius_mm'])},center=true);"]
        elif c["geometry_type"]=="annulus":
            out += [f"      difference() {{ cylinder(h={_f(p['height_mm'])},r={_f(p['outer_radius_mm'])},center=true);",
                    f"        cylinder(h={_f(p['height_mm'])+0.02:.12g},r={_f(p['inner_radius_mm'])},center=true); }}"]
        else:
            pts="["+",".join("["+_f(x)+","+_f(y)+"]" for x,y in _polygon(p["outline_xy_mm"],"outline_xy_mm"))+"]"
            out += [f"      linear_extrude(height={_f(p['height_mm'])},center=true) polygon(points={pts});"]
        out += ["    }","}",""]
    out += ["// Assembly preview calls are intentionally disabled pending engineer review."]
    for c in package["components"]: out.append(f"// part_{c['id']}();")
    return "\n".join(out)+"\n"
