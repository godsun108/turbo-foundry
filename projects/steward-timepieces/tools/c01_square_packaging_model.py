"""C-01 square architecture comparison model.

This is a qualitative subsystem-allocation model, not a dimensional CAD model.
It intentionally contains no invented component dimensions or coordinates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_SUBSYSTEMS = (
    "barrel", "going_train", "balance_escapement", "automatic_winding",
    "chronograph_drive_coupling", "chronograph_control_reset",
    "elapsed_counters", "weekday_date_calendar", "motion_works_hand_stack",
)

CANDIDATES = {
    "SQ-A": {
        "name": "Rounded-square plate / circular mechanical elements",
        "principle": "Rounded-square structural envelope; circular mechanisms retain geometry suited to their function.",
        "allocation": {
            "barrel": "Movement-side; position TBD from energy path and service access",
            "going_train": "Movement-side; wheel centers and topology TBD",
            "balance_escapement": "Movement-side perimeter region; shock and regulator access TBD",
            "automatic_winding": "Rotor plane; full sweep and winding works TBD",
            "chronograph_drive_coupling": "Movement-side; drive take-off and coupling position TBD",
            "chronograph_control_reset": "Movement-side; pusher/control interface TBD",
            "elapsed_counters": "Dial-side or movement-side according to selected counter train; TBD",
            "weekday_date_calendar": "Dial-side display with drive/indexing interfaces; disc geometry TBD",
            "motion_works_hand_stack": "Central display axis provisionally retained; arbor stack TBD",
        },
        "dominant_constraints": [
            "Fit circular functional elements within rounded-square plate and bridge envelope",
            "Preserve rotor sweep, balance protection and service access",
            "Avoid treating corner volume as usable until component envelopes are known",
        ],
    },
    "SQ-B": {
        "name": "Square-organized movement architecture",
        "principle": "Subsystems deliberately organized around a square plan while functional wheels and oscillators remain mechanically appropriate shapes.",
        "allocation": {
            "barrel": "Dedicated square-plan energy zone; exact side/corner assignment TBD",
            "going_train": "Purpose-organized train corridor; topology and transfer stages TBD",
            "balance_escapement": "Dedicated protected regulator zone; location and shock path TBD",
            "automatic_winding": "Rotor plane integrated with square plan; sweep and winding efficiency TBD",
            "chronograph_drive_coupling": "Dedicated chronograph zone; drive take-off and coupling TBD",
            "chronograph_control_reset": "Control zone aligned to pusher interfaces; lever path TBD",
            "elapsed_counters": "Quadrant-aligned counter zones; drive paths TBD",
            "weekday_date_calendar": "Calendar display and indexing zone; disc and corrector paths TBD",
            "motion_works_hand_stack": "Central display axis provisionally retained; arbor stack TBD",
        },
        "dominant_constraints": [
            "Potential extra transfer gearing and interfaces",
            "Rotor sweep and balance protection may compete with visual quadrant organization",
            "Do not impose symmetry where it harms train efficiency or serviceability",
        ],
    },
    "SQ-C": {
        "name": "Circular mechanical core / square outer architecture",
        "principle": "Geometry-sensitive timekeeping core concentrated centrally; square outer structure supports display and interfaces.",
        "allocation": {
            "barrel": "Core region; exact position and barrel-to-train path TBD",
            "going_train": "Core region; conventional relationships retained only if verified",
            "balance_escapement": "Protected core region; access and shock path TBD",
            "automatic_winding": "Rotor plane around or over core; sweep and clearances TBD",
            "chronograph_drive_coupling": "Core-to-outer interface; drive path and losses TBD",
            "chronograph_control_reset": "Outer structural/control zone; linkage and service access TBD",
            "elapsed_counters": "Outer display zones; transfer gearing and counter supports TBD",
            "weekday_date_calendar": "Outer dial-side zone; calendar disc and indexing interfaces TBD",
            "motion_works_hand_stack": "Central display axis provisionally retained; arbor stack TBD",
        },
        "dominant_constraints": [
            "Core-to-outer interfaces may add parts and alignment requirements",
            "Outer structure must be functional and serviceable, not decorative only",
            "Verify counter/calendar drive losses and axial packaging",
        ],
    },
}

INTERFACES = (
    ("rotor", "winding works", "Winding torque path, direction strategy, bearing and sweep"),
    ("winding works", "barrel", "Winding input, slipping/overwind behavior and service"),
    ("barrel", "going train", "Torque delivery, arbor support and energy reserve"),
    ("going train", "balance / escapement", "Impulse demand, rate stability and amplitude"),
    ("going train", "chronograph drive", "Take-off arbor, loading and stopped/running states"),
    ("chronograph drive", "coupling", "Engagement, drag, hand jump and wear"),
    ("control", "coupling / brake / reset", "Start-stop-reset sequence, pusher force and reset alignment"),
    ("chronograph drive", "elapsed counters", "Counter ratios, carry/indexing and torque"),
    ("going train", "calendar", "Calendar drive, changeover load and indexing"),
    ("calendar", "weekday/date displays", "Disc support, jumper force, correction and safe setting"),
    ("motion works", "central hand stack", "Coaxial arbors, friction, height and hand clearances"),
    ("movement", "case / crown / pushers", "Casing supports, stem axis, pusher sealing and extraction"),
)

def build_model() -> dict:
    candidates = {}
    for key, candidate in CANDIDATES.items():
        candidates[key] = {
            "name": candidate["name"],
            "principle": candidate["principle"],
            "allocation": candidate["allocation"],
            "dominant_constraints": candidate["dominant_constraints"],
            "subsystem_coverage": sorted(candidate["allocation"]),
            "missing_subsystems": sorted(set(REQUIRED_SUBSYSTEMS) - set(candidate["allocation"])),
            "geometry_status": "TBD",
            "coordinates": None,
            "dimensions": None,
            "performance_claims": None,
        }
    return {
        "schema": "steward.c01.square-packaging-comparison.v1",
        "document_status": "conceptual subsystem allocation; not CAD",
        "units": None,
        "datum": "No square-case datum or dimensions approved",
        "evidence_policy": "No component dimensions, coordinates, ratios, torque or performance values are inferred.",
        "functional_baseline": [
            "automatic mechanical winding", "hours and minutes", "weekday",
            "day-of-month 1-31", "central chronograph seconds",
            "elapsed-minute counter", "elapsed-hour counter", "running seconds",
        ],
        "scope_exclusions": ["month display", "moon phase", "planetary indications"],
        "required_subsystems": list(REQUIRED_SUBSYSTEMS),
        "interfaces_requiring_resolution": [
            {"from": a, "to": b, "engineering_question": q, "status": "TBD"}
            for a, b, q in INTERFACES
        ],
        "candidates": candidates,
        "decision": "No candidate selected; evidence and dimensional packaging required.",
    }


def render_svg(model: dict, output: Path) -> None:
    """Render a qualitative block diagram; boxes are not to scale."""
    width, height = 1500, 760
    cols = ["SQ-A", "SQ-B", "SQ-C"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="35" y="42" font-family="sans-serif" font-size="25" font-weight="bold">STEWARD C-01 — Square architecture comparison</text>',
        '<text x="35" y="70" font-family="sans-serif" font-size="15">Qualitative subsystem allocation only — boxes are not to scale; no geometry or fit is implied.</text>',
    ]
    labels = [
        "Energy: barrel + winding", "Timekeeping: train + regulator",
        "Chronograph: drive + control", "Displays: counters + calendar",
        "Central motion works / hand stack",
    ]
    descriptions = {
        "SQ-A": ["Rounded-square plate", "Circular mechanisms", "Shared plate-side chrono", "Dial-side display interfaces", "Central axis TBD"],
        "SQ-B": ["Square-plan energy zone", "Purpose-organized train", "Dedicated chrono zone", "Quadrant-aligned displays", "Central axis TBD"],
        "SQ-C": ["Core energy zone", "Circular mechanical core", "Core-to-outer chrono", "Outer display interfaces", "Central axis TBD"],
    }
    col_x = [35, 535, 1035]
    for col, x in zip(cols, col_x):
        parts.append(f'<text x="{x}" y="120" font-family="sans-serif" font-size="22" font-weight="bold">{col} — {model["candidates"][col]["name"]}</text>')
        for i, label in enumerate(labels):
            y = 155 + i * 105
            parts.append(f'<rect x="{x}" y="{y}" width="420" height="76" rx="12" fill="#edf2f7" stroke="#526273" stroke-width="2"/>')
            parts.append(f'<text x="{x+14}" y="{y+27}" font-family="sans-serif" font-size="15" font-weight="bold">{label}</text>')
            parts.append(f'<text x="{x+14}" y="{y+53}" font-family="sans-serif" font-size="14">{descriptions[col][i]}</text>')
        parts.append(f'<text x="{x}" y="710" font-family="sans-serif" font-size="14">All coordinates / dimensions: TBD</text>')
    parts.append("</svg>")
    output.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="build/c01-square-packaging")
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    model = build_model()
    (out / "c01-square-packaging-comparison.json").write_text(
        json.dumps(model, indent=2) + "\n", encoding="utf-8"
    )
    render_svg(model, out / "c01-square-architecture-comparison.svg")
    print(f"Wrote qualitative C-01 square packaging comparison to {out}")


if __name__ == "__main__":
    main()
