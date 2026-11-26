# C-01 Parametric Dial Layout — Generator 01

**Revision:** 0.1  
**Status:** Initial executable 2D concept generator  
**Branch:** `steward/c-01-movement-foundation`

## Purpose

Provide a repeatable, editable starting point for comparing dial arrangements A, B and C in a shared normalized coordinate system. This is the first executable parametric layout artifact for C-01.

## Files

- `tools/c01_dial_layout.py` — standard-library Python SVG generator.
- `tools/test_c01_dial_layout.py` — unit tests.
- Generated outputs are written to `build/c01-layouts/` when run locally; generated output files are not source-of-truth engineering data.

## Coordinate model

- Dial center is the origin.
- +X points to 3 o'clock.
- +Y points to 12 o'clock.
- Coordinates are normalized to opening radius R=1.
- SVG display scale is a rendering parameter only; it does not represent millimetres.
- No case diameter, dial diameter, shaft location, subdial diameter, window dimension or tolerance is assumed.

The script stores candidate register and calendar centers as normalized points. These values are visual study inputs only and must be replaced by measured or CAD-verified coordinates before dimensional design.

## Candidate treatment

| Candidate | Register concept | Calendar concept |
|---|---|---|
| A | 12 / 6 / 9 | Paired day/date at 3 |
| B | 3 / 6 / 9 | Paired day/date at 12 |
| C | 12 / 6 / 9 | Compact paired day/date near 12 |

Candidate C deliberately flags the possible overlap between the upper register and calendar zone. The overlap is a packaging question to resolve, not a claim of fit.

## Run

From the tools directory:

```bash
python c01_dial_layout.py --output-dir ../../build/c01-layouts
python -m unittest test_c01_dial_layout.py
```

The generator writes three SVG sheets. A future CAD adapter may consume the same normalized coordinate data after a case/dial envelope and real shaft axes are approved.

## Next increments

1. Add explicit aperture, subdial, scale and hand-sweep envelopes.
2. Add constraint checks for overlaps and edge clearances.
3. Add case, pusher, stem and crown keep-out zones.
4. Import verified shaft-axis coordinates from a controlled reference drawing or C-01 CAD model.
5. Convert normalized values to millimetres only after the dial-opening diameter is approved.
6. Link the dial layout to the movement-side plate and bridge skeleton.

## Engineering integrity

This generator is a parametric visual-layout tool, not mechanical CAD. It does not calculate gear trains, torque, component thickness, Z-stack clearances, manufacturing tolerances or physical fit. The generated drawings are schematic and must not be used for manufacturing.
