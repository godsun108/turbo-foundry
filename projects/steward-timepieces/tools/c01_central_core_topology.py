#!/usr/bin/env python3
"""STEWARD C-01 central mechanical core topology register.

Exports a machine-readable functional topology and a non-scale schematic.
All nodes are functional roles; no component coordinates or dimensions exist.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

NODES = [
    ("barrel", "Mainspring barrel", "power"),
    ("center", "Center wheel / center arbor", "train"),
    ("third", "Third wheel", "train"),
    ("fourth", "Fourth wheel / seconds arbor", "train"),
    ("escape", "Escape wheel", "regulator"),
    ("pallet", "Pallet fork", "regulator"),
    ("balance", "Balance", "regulator"),
    ("rotor", "Rotor", "automatic"),
    ("winding", "Automatic winding works", "automatic"),
    ("chrono", "Chronograph drive / coupling", "chronograph"),
    ("control", "Chronograph control / brake / reset", "chronograph"),
    ("calendar", "Weekday / date calendar", "calendar"),
    ("hands", "Motion works / central hand stack", "display"),
]
EDGES = [
    ("barrel", "center", "candidate going-train power path"),
    ("center", "third", "candidate gear mesh"),
    ("third", "fourth", "candidate gear mesh"),
    ("fourth", "escape", "candidate gear mesh"),
    ("escape", "pallet", "escapement interaction"),
    ("pallet", "balance", "impulse / regulation"),
    ("rotor", "winding", "automatic winding input"),
    ("winding", "barrel", "barrel winding input"),
    ("center", "hands", "candidate motion-works input; details TBD"),
    ("fourth", "hands", "candidate running-seconds interface; details TBD"),
    ("center", "chrono", "candidate take-off only; not selected"),
    ("fourth", "chrono", "candidate take-off only; not selected"),
    ("chrono", "control", "coupling / brake / reset interaction"),
]

def build_model() -> dict:
    return {
        "schema": "steward.c01.central-core-topology.v1",
        "status": "preliminary topology; not dimensioned CAD",
        "configuration": "SQ-A working study configuration only; SQ-B and SQ-C remain open",
        "datum": {"xy_origin": "nominal display center", "x_positive": "3 o'clock",
                  "y_positive": "12 o'clock", "z_zero": "approved dial plane",
                  "z_positive": "toward movement side", "physical_axes": "TBD"},
        "nodes": [{"id": i, "label": label, "group": group} for i, label, group in NODES],
        "edges": [{"from": a, "to": b, "relationship": rel} for a, b, rel in EDGES],
        "candidate_going_train": ["barrel", "center", "third", "fourth", "escape", "pallet", "balance"],
        "chronograph_takeoff_candidates": ["center", "fourth", "derived_intermediate_stage"],
        "unresolved": [
            "tooth_counts", "gear_ratios", "center_distances", "arbor_coordinates",
            "gear_module", "pressure_angle", "face_width", "materials", "lubrication",
            "barrel_spring_geometry", "torque_profile", "escapement_type",
            "rotor_axis", "rotor_swept_envelope", "clutch_architecture",
            "control_architecture", "counter_advancement", "calendar_geometry",
            "central_hand_stack", "plate_and_bridge_geometry", "clearances", "tolerances"
        ],
        "evidence_policy": "No physical coordinates, dimensions, ratios, torque or performance values are inferred."
    }

def render_svg(model: dict) -> str:
    # Diagram coordinates are page-layout coordinates only, not movement coordinates.
    boxes = [
        (60, 125, "Barrel", "power"),
        (270, 125, "Center wheel", "train"),
        (480, 125, "Third wheel", "train"),
        (690, 125, "Fourth wheel", "train"),
        (900, 125, "Escape wheel", "regulator"),
        (1050, 125, "Pallet / balance", "regulator"),
        (270, 350, "Rotor", "automatic"),
        (480, 350, "Winding works", "automatic"),
        (690, 350, "Chronograph", "chronograph"),
        (900, 350, "Control / reset", "chronograph"),
        (480, 550, "Motion works / hand stack", "display"),
        (900, 550, "Weekday / date", "calendar"),
    ]
    palette = {"power":"#eee7d8","train":"#e5edf5","regulator":"#e9e4f2",
               "automatic":"#e4eee5","chronograph":"#f3e6df","display":"#f5f0dc","calendar":"#e8eeee"}
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="720" viewBox="0 0 1240 720">',
             '<rect width="1240" height="720" fill="#fbfaf7"/>',
             '<style>.t{font:bold 25px sans-serif;fill:#222}.s{font:14px sans-serif;fill:#555}.b{font:15px sans-serif;fill:#222}.n{font:12px sans-serif;fill:#555}</style>',
             '<text x="45" y="45" class="t">C-01 Central Core — Candidate Functional Topology</text>',
             '<text x="45" y="72" class="s">WP-SQ-03 · Diagram positions are schematic only · NOT TO SCALE</text>',
             '<defs><marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0 0 L0 6 L8 3z" fill="#555"/></marker></defs>']
    for x1,x2 in [(210,270),(420,480),(630,690),(840,900),(1050,1050)]:
        if x2 > x1:
            parts.append(f'<path d="M{x1} 165 L{x2-8} 165" stroke="#555" stroke-width="2" fill="none" marker-end="url(#a)"/>')
    for path in ['M420 390 L480 390','M555 350 L555 205','M345 205 L345 550',
                 'M765 205 L765 350']:
        parts.append(f'<path d="{path}" stroke="#777" stroke-width="1.8" stroke-dasharray="6 5" fill="none" marker-end="url(#a)"/>')
    for x,y,label,group in boxes:
        parts.append(f'<rect x="{x}" y="{y}" width="150" height="80" rx="12" fill="{palette[group]}" stroke="#444" stroke-width="1.7"/>')
        parts.append(f'<text x="{x+75}" y="{y+35}" text-anchor="middle" class="b">{label}</text>')
        parts.append(f'<text x="{x+75}" y="{y+59}" text-anchor="middle" class="n">{group.upper()}</text>')
    parts += ['<text x="45" y="680" class="s">Solid arrows: candidate going-train sequence. Dashed arrows: functional interfaces / unresolved alternatives.</text>',
              '<text x="45" y="702" class="n">No wheel centers, gear ratios, physical placement, dimensions or clearances are implied.</text></svg>']
    return "\n".join(parts)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="../../build/c01-central-core-topology")
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    model = build_model()
    (out / "central-core-topology.json").write_text(json.dumps(model, indent=2), encoding="utf-8")
    (out / "central-core-topology.svg").write_text(render_svg(model), encoding="utf-8")
    print(f"Wrote topology model and schematic to {out}")

if __name__ == "__main__":
    main()
