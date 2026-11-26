"""Generate dimensionless C-01 dial-layout concept sheets.

Coordinates are normalized to the dial-opening radius (R=1). They are not
physical dimensions or verified movement shaft locations. No default case or
dial diameter is assumed.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Candidate:
    key: str
    title: str
    registers: tuple[tuple[str, Point], ...]
    calendars: tuple[tuple[str, Point], ...]
    note: str


CANDIDATES = (
    Candidate(
        "A",
        "Traditional — weekday/date at 3",
        (
            ("30-minute", Point(0.0, 0.48)),
            ("12-hour", Point(0.0, -0.48)),
            ("running seconds", Point(-0.48, 0.0)),
        ),
        (("weekday", Point(0.66, 0.09)), ("date", Point(0.66, -0.09))),
        "Conventional counter arrangement; paired calendar apertures at 3.",
    ),
    Candidate(
        "B",
        "Balanced — weekday/date at 12",
        (
            ("30-minute", Point(0.48, 0.0)),
            ("12-hour", Point(0.0, -0.48)),
            ("running seconds", Point(-0.48, 0.0)),
        ),
        (("weekday", Point(-0.15, 0.78)), ("date", Point(0.15, 0.78))),
        "Registers at 3, 6 and 9; paired calendar apertures at 12.",
    ),
    Candidate(
        "C",
        "Distinctive — compact calendar near 12",
        (
            ("30-minute", Point(0.0, 0.48)),
            ("12-hour", Point(0.0, -0.48)),
            ("running seconds", Point(-0.48, 0.0)),
        ),
        (("weekday", Point(-0.17, 0.82)), ("date", Point(0.17, 0.82))),
        "Traditional counter axes retained; compact calendar zone near 12. "
        "Upper register/calendar overlap is intentionally flagged for review.",
    ),
)


def _svg_text(x: float, y: float, value: str, size: int = 16) -> str:
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="middle" '
        f'font-family="sans-serif" font-size="{size}">{escape(value)}</text>'
    )


def render_candidate(candidate: Candidate, px_per_radius: float = 400.0) -> str:
    """Return an SVG concept sheet; R maps to px_per_radius for display only."""
    if px_per_radius <= 0:
        raise ValueError("px_per_radius must be positive")

    center = 500.0
    radius = px_per_radius

    def xy(point: Point) -> tuple[float, float]:
        return center + point.x * radius, center - point.y * radius

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1120" '
        'viewBox="0 0 1000 1120">',
        '<rect width="100%" height="100%" fill="white"/>',
        _svg_text(500, 42, f"C-01 — Layout {candidate.key}", 25),
        _svg_text(500, 74, candidate.title, 18),
        f'<circle cx="{center}" cy="{center}" r="{radius}" fill="none" '
        'stroke="#222" stroke-width="3"/>',
        f'<circle cx="{center}" cy="{center}" r="{radius * 0.88}" fill="none" '
        'stroke="#aaa" stroke-dasharray="5 7"/>',
        f'<line x1="{center-radius}" y1="{center}" x2="{center+radius}" '
        f'y2="{center}" stroke="#ddd"/>',
        f'<line x1="{center}" y1="{center-radius}" x2="{center}" '
        f'y2="{center+radius}" stroke="#ddd"/>',
        f'<circle cx="{center}" cy="{center}" r="7" fill="#222"/>',
        _svg_text(center, center + 30, "CENTRAL AXIS", 13),
    ]

    for label, point in candidate.registers:
        x, y = xy(point)
        parts.extend([
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="57" fill="none" '
            'stroke="#245b86" stroke-width="3"/>',
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="43" fill="none" '
            'stroke="#8ba9bf" stroke-dasharray="3 4"/>',
            _svg_text(x, y - 3, label, 13),
            _svg_text(x, y + 15, "REGISTER", 10),
        ])

    for label, point in candidate.calendars:
        x, y = xy(point)
        parts.extend([
            f'<rect x="{x-42:.2f}" y="{y-18:.2f}" width="84" height="36" '
            'rx="3" fill="none" stroke="#9a5b20" stroke-width="3"/>',
            _svg_text(x, y + 5, label.upper(), 12),
        ])

    parts.extend([
        _svg_text(500, 960, "SCHEMATIC ONLY — NORMALIZED COORDINATES, R = 1", 17),
        _svg_text(500, 990, "Not a dimensioned dial, shaft map or movement drawing.", 14),
        _svg_text(500, 1030, candidate.note, 13),
        _svg_text(500, 1065, "All positions are provisional visual-layout inputs.", 13),
        "</svg>",
    ])
    return "\n".join(parts)


def write_all(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for candidate in CANDIDATES:
        path = output_dir / f"c01-layout-{candidate.key.lower()}.svg"
        path.write_text(render_candidate(candidate), encoding="utf-8")
        written.append(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("build/c01-layouts"),
        help="Directory for generated SVG concept sheets.",
    )
    args = parser.parse_args()
    for path in write_all(args.output_dir):
        print(path)


if __name__ == "__main__":
    main()
