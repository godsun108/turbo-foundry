#!/usr/bin/env python3
"""Generate a non-scale topology diagram for STEWARD C-01 WP-SQ-02.

The drawing shows functional zones and drive-path relationships only.
It intentionally contains no physical coordinates, dimensions or fit claims.
"""
from pathlib import Path
import argparse

SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760">
<rect width="1200" height="760" fill="#fbfaf7"/>
<style>
.title{font: bold 27px sans-serif;fill:#222}.sub{font:15px sans-serif;fill:#555}
.head{font:bold 18px sans-serif;fill:#222}.label{font:15px sans-serif;fill:#222}
.small{font:12px sans-serif;fill:#555}.zone{fill:#fff;stroke:#333;stroke-width:2}
.core{fill:#f1eee6;stroke:#333;stroke-width:3}.display{fill:#f7f3e8;stroke:#777;stroke-width:1.7}
.path{stroke:#444;stroke-width:2.2;fill:none;marker-end:url(#arrow)}
.dash{stroke:#777;stroke-width:1.5;stroke-dasharray:7 6;fill:none}
</style>
<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#444"/></marker></defs>
<text x="48" y="48" class="title">STEWARD C-01 — First Integrated Square Layout</text>
<text x="48" y="76" class="sub">WP-SQ-02 · SQ-A working study configuration · topology only · NOT TO SCALE</text>

<!-- movement side -->
<text x="55" y="125" class="head">A. Movement-side functional topology</text>
<rect x="55" y="150" width="500" height="500" rx="70" class="zone"/>
<circle cx="305" cy="400" r="160" class="dash"/>
<text x="305" y="225" text-anchor="middle" class="small">Reference circular core region — conceptual</text>
<rect x="105" y="190" width="150" height="78" rx="12" class="display"/>
<text x="180" y="220" text-anchor="middle" class="label">Barrel</text><text x="180" y="243" text-anchor="middle" class="small">Power source</text>
<rect x="350" y="190" width="155" height="78" rx="12" class="display"/>
<text x="427" y="220" text-anchor="middle" class="label">Automatic works</text><text x="427" y="243" text-anchor="middle" class="small">Rotor / winding</text>
<rect x="205" y="320" width="200" height="100" rx="50" class="core"/>
<text x="305" y="360" text-anchor="middle" class="label">Going train</text><text x="305" y="384" text-anchor="middle" class="small">Train topology TBD</text>
<rect x="100" y="485" width="160" height="82" rx="12" class="display"/>
<text x="180" y="516" text-anchor="middle" class="label">Escapement</text><text x="180" y="540" text-anchor="middle" class="small">Balance / regulator</text>
<rect x="350" y="485" width="160" height="82" rx="12" class="display"/>
<text x="430" y="516" text-anchor="middle" class="label">Chronograph</text><text x="430" y="540" text-anchor="middle" class="small">Drive / coupling / control</text>
<path d="M255 230 L350 230" class="path"/><path d="M427 268 L427 302 L405 340" class="path"/>
<path d="M255 230 L255 300 L275 320" class="path"/><path d="M205 380 L180 485" class="path"/>
<path d="M405 370 L430 485" class="path"/>
<text x="305" y="610" text-anchor="middle" class="small">Dashed circle is a conceptual core boundary, not a measured envelope.</text>

<!-- dial side -->
<text x="635" y="125" class="head">B. Dial-side display and user interface topology</text>
<rect x="635" y="150" width="500" height="500" rx="70" class="zone"/>
<rect x="675" y="190" width="170" height="95" rx="10" class="display"/>
<text x="760" y="225" text-anchor="middle" class="label">30-minute</text><text x="760" y="250" text-anchor="middle" class="small">Chronograph</text>
<rect x="925" y="190" width="170" height="95" rx="10" class="display"/>
<text x="1010" y="225" text-anchor="middle" class="label">Weekday / date</text><text x="1010" y="250" text-anchor="middle" class="small">Calendar</text>
<rect x="675" y="510" width="170" height="95" rx="10" class="display"/>
<text x="760" y="545" text-anchor="middle" class="label">Running seconds</text><text x="760" y="570" text-anchor="middle" class="small">Timekeeping</text>
<rect x="925" y="510" width="170" height="95" rx="10" class="display"/>
<text x="1010" y="545" text-anchor="middle" class="label">12-hour</text><text x="1010" y="570" text-anchor="middle" class="small">Chronograph</text>
<circle cx="885" cy="397" r="72" class="core"/>
<text x="885" y="390" text-anchor="middle" class="label">Central</text><text x="885" y="415" text-anchor="middle" class="small">Time + chrono sec.</text>
<path d="M885 325 L885 285" class="dash"/><path d="M885 469 L885 510" class="dash"/>
<path d="M813 397 L845 397" class="dash"/><path d="M957 397 L925 397" class="dash"/>
<text x="885" y="625" text-anchor="middle" class="small">Square dial candidate D — display destinations only, axes TBD.</text>

<text x="48" y="710" class="sub">No component centers, dimensions, gear ratios, clearances, materials or performance are implied.</text>
</svg>
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="c01-first-square-layout.svg")
    args = parser.parse_args()
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(SVG, encoding="utf-8")
    print(f"Wrote {target}")

if __name__ == "__main__":
    main()
