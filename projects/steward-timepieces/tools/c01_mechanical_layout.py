"""C-01 conceptual mechanical packaging skeleton.

All coordinates are normalized to a provisional dial-opening radius R=1.
This is a 2D reservation map, not CAD and not a clearance/fit validation.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Zone:
    name: str
    layer: str
    x: float
    y: float
    width: float
    height: float
    status: str = "provisional"
    purpose: str = ""

    def bounds(self) -> tuple[float, float, float, float]:
        return (self.x - self.width / 2, self.y - self.height / 2,
                self.x + self.width / 2, self.y + self.height / 2)


@dataclass(frozen=True)
class Candidate:
    name: str
    calendar_note: str
    zones: tuple[Zone, ...]


# Common movement-side zones are deliberately shared by all dial concepts.
# Values are normalized placeholders, not measured component envelopes.
CORE_ZONES = (
    Zone("barrel_reservation", "movement_side", -0.43, 0.24, 0.30, 0.30,
         purpose="Mainspring barrel and immediate service access"),
    Zone("balance_reservation", "movement_side", 0.38, -0.25, 0.26, 0.26,
         purpose="Balance, escapement and shock-setting access"),
    Zone("going_train_corridor", "movement_side", -0.02, 0.02, 0.44, 0.22,
         purpose="Provisional train corridor; wheel centers not defined"),
    Zone("chronograph_reservation", "movement_side", 0.02, -0.37, 0.48, 0.20,
         purpose="Chronograph drive, coupling, control and counters"),
    Zone("rotor_sweep", "rotor_plane", 0.0, 0.0, 0.88, 0.88,
         purpose="Rotor sweep reservation; bearing and mass not defined"),
    Zone("calendar_mechanism", "dial_side", 0.0, 0.32, 0.62, 0.18,
         purpose="Weekday/date discs and indexing; exact disc geometry open"),
)

DIAL_ZONES = {
    "A": (
        Zone("register_30m", "dial_side", 0.0, 0.62, 0.22, 0.22),
        Zone("register_12h", "dial_side", 0.0, -0.58, 0.22, 0.22),
        Zone("running_seconds", "dial_side", -0.58, 0.0, 0.20, 0.20),
        Zone("calendar_display", "dial_side", 0.62, 0.0, 0.26, 0.16),
    ),
    "B": (
        Zone("register_30m", "dial_side", 0.58, 0.0, 0.22, 0.22),
        Zone("register_12h", "dial_side", 0.0, -0.58, 0.22, 0.22),
        Zone("running_seconds", "dial_side", -0.58, 0.0, 0.20, 0.20),
        Zone("calendar_display", "dial_side", 0.0, 0.66, 0.28, 0.16),
    ),
    "C": (
        Zone("register_30m", "dial_side", 0.0, 0.62, 0.22, 0.22),
        Zone("register_12h", "dial_side", 0.0, -0.58, 0.22, 0.22),
        Zone("running_seconds", "dial_side", -0.58, 0.0, 0.20, 0.20),
        Zone("calendar_display", "dial_side", 0.0, 0.69, 0.28, 0.16),
    ),
}

CANDIDATES = {
    key: Candidate(
        key,
        ("Upper calendar/register interaction requires explicit review."
         if key == "C" else "Display reservation only; detailed aperture study remains open."),
        CORE_ZONES + zones,
    )
    for key, zones in DIAL_ZONES.items()
}


def overlaps(a: Zone, b: Zone, epsilon: float = 1e-9) -> bool:
    """2D rectangle intersection on the same conceptual layer only."""
    if a.layer != b.layer:
        return False
    ax0, ay0, ax1, ay1 = a.bounds()
    bx0, by0, bx1, by1 = b.bounds()
    return (ax0 < bx1 - epsilon and ax1 > bx0 + epsilon
            and ay0 < by1 - epsilon and ay1 > by0 + epsilon)


def validate_zone(zone: Zone) -> list[str]:
    errors = []
    if zone.width <= 0 or zone.height <= 0:
        errors.append(f"{zone.name}: width and height must be positive")
    if zone.status not in {"measured", "calculated", "supplier_confirmed", "provisional", "TBD"}:
        errors.append(f"{zone.name}: unsupported evidence status {zone.status!r}")
    return errors


def build_model() -> dict:
    candidates = {}
    for key, candidate in CANDIDATES.items():
        zones = [asdict(z) | {"bounds": z.bounds()} for z in candidate.zones]
        candidates[key] = {
            "calendar_note": candidate.calendar_note,
            "zones": zones,
            "same_layer_overlap_warnings": [
                [a.name, b.name]
                for i, a in enumerate(candidate.zones)
                for b in candidate.zones[i + 1:]
                if overlaps(a, b)
            ],
            "validation_errors": [
                error for zone in candidate.zones for error in validate_zone(zone)
            ],
        }
    return {
        "schema": "steward.c01.mechanical-layout.v1",
        "units": "normalized dial-opening radius (R=1); not millimetres",
        "datum": {
            "origin": "nominal dial/movement center O=(0,0)",
            "x_axis": "+X toward 3 o'clock",
            "y_axis": "+Y toward 12 o'clock",
            "z_datum": "dial plane Z=0; positive Z toward movement side",
            "angle_convention": "positive counter-clockwise viewed from dial side",
        },
        "evidence_policy": {
            "allowed_status": ["measured", "calculated", "supplier_confirmed", "provisional", "TBD"],
            "current_zone_status": "provisional",
            "warning": "No physical fit, collision, stack-height, gear-mesh or clearance conclusion is valid from this normalized 2D model.",
        },
        "shared_arbor_axes": [
            {"name": "central_time_and_chrono_axis", "x": 0.0, "y": 0.0, "status": "TBD"},
            {"name": "calendar_drive_axis", "x": None, "y": None, "status": "TBD"},
            {"name": "barrel_arbor_axis", "x": None, "y": None, "status": "TBD"},
            {"name": "balance_staff_axis", "x": None, "y": None, "status": "TBD"},
        ],
        "candidates": candidates,
    }


def render_svg(candidate_name: str, candidate_data: dict, output: Path) -> None:
    size, scale, center = 800, 300, 400
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<circle cx="{center}" cy="{center}" r="{scale}" fill="none" stroke="#777" stroke-dasharray="5 5"/>',
        f'<line x1="{center-scale}" y1="{center}" x2="{center+scale}" y2="{center}" stroke="#aaa"/>',
        f'<line x1="{center}" y1="{center-scale}" x2="{center}" y2="{center+scale}" stroke="#aaa"/>',
        f'<text x="20" y="28" font-family="sans-serif" font-size="20">C-01 mechanical zone study — candidate {candidate_name}</text>',
        f'<text x="20" y="52" font-family="sans-serif" font-size="12">Normalized concept only; not millimetres or verified fit</text>',
    ]
    for z in candidate_data["zones"]:
        if z["layer"] != "dial_side":
            continue
        x = center + z["x"] * scale - z["width"] * scale / 2
        y = center - z["y"] * scale - z["height"] * scale / 2
        w, h = z["width"] * scale, z["height"] * scale
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#dce8f5" fill-opacity="0.75" stroke="#345"/>')
        parts.append(f'<text x="{x+w/2:.1f}" y="{y+h/2:.1f}" text-anchor="middle" dominant-baseline="middle" font-family="sans-serif" font-size="11">{z["name"]}</text>')
    parts.append(f'<circle cx="{center}" cy="{center}" r="5" fill="#b33"/>')
    parts.append('<text x="410" y="390" font-family="sans-serif" font-size="11">O</text>')
    parts.append("</svg>")
    output.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="build/c01-mechanical-layout")
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    model = build_model()
    (out / "c01-mechanical-layout.json").write_text(
        json.dumps(model, indent=2) + "\n", encoding="utf-8"
    )
    for name, data in model["candidates"].items():
        render_svg(name, data, out / f"candidate-{name.lower()}.svg")
    print(f"Wrote C-01 conceptual layout model and 3 SVGs to {out}")


if __name__ == "__main__":
    main()
