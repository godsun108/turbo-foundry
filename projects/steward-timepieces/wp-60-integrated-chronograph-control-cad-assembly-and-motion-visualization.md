# WP-60 — Integrated Chronograph Control CAD Assembly and Motion Visualization

- **Document ID:** SEB-C01-WP-60
- **Revision:** A — initial controlled issue
- **Status:** Evidence-gated sampled-motion visualization framework; no C-01 motion or geometry approved
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_motion_visualization.py`
- **Tests:** `tools/test_c01_motion_visualization.py`
- **Viewer:** `dashboard/c01-motion-viewer.html`
- **Dependencies:** WP-14, WP-20, WP-21, WP-22, WP-36, WP-40, WP-44, WP-54, WP-55, WP-57, WP-58 and WP-59

## 1. Purpose

WP-60 establishes a controlled handoff from WP-59 parametric assembly definitions and WP-44/WP-55 sampled motion analysis into an interactive browser viewer. It keeps two independent control candidates:
- **CW:** column-wheel control.
- **CL:** cam/lever control.

The viewer presents four requested operating conditions: stopped at zero, running, stopped with elapsed time retained, and resetting. Each condition is represented by explicit, time-stamped component poses. The reset sequence must include a supplied resetting frame followed by a supplied stopped-at-zero frame.

This is a data-driven visualization—not a kinematics solver, physics simulation, animation inferred from mechanism principles, or proof that a physical mechanism works.

## 2. Architecture and preservation of decisions

CW and CL remain separate configurations. The input package requires matching common requirements, movement datum and interface-baseline revisions. Each candidate retains its own configuration revision, component geometry, frame samples, evidence and source provenance.

No architecture or clutch is selected. WP-33/WP-45/WP-56 decisions remain open, including:
- vertical friction clutch versus horizontal/lateral coupling;
- column-wheel versus cam/lever;
- source arbor and going-train take-off;
- counter branch topology and continuous/jumping counters;
- stopped-train retention;
- common versus separate reset hammers;
- display arrangement, movement envelope and case interface.

The viewer and validator never authorize design freeze, prototype assembly, physical testing or manufacture.

## 3. Operating-state presentation

| State ID | Meaning | Required source data |
|---|---|---|
| `stopped_zero` | Chronograph stopped and indications at the declared zero datum | Explicit pose for every displayed component |
| `running` | Chronograph running | Explicit sampled poses; no speed or motion inferred |
| `stopped_retained` | Chronograph stopped while elapsed indication is retained | Explicit retained positions |
| `resetting` | Reset mechanism moving from retained indication toward zero | Explicit sampled reset poses |

Required sequence: initial `stopped_zero`, running, stopped-retained, resetting, then a later `stopped_zero` frame. Additional frames within a state are allowed. Frame timestamps must strictly increase. The software does not prescribe duration, angular travel, motion law, pusher timing, reset force or return spring behavior.

A valid state label is not evidence of physical operation. In particular, the running-reset interlock remains subject to WP-30/WP-46 physical verification and the WP-41/WP-42 control requirements.

## 4. Input data contract

The JSON package contains:
- package ID, revision, owner, evidence ID and source revision;
- common requirements, datum and interface-baseline revisions;
- separate CW and CL candidate records;
- candidate configuration revision, evidence/source references and units (seconds, millimetres);
- component IDs, roles, geometry descriptors, drawing references, status and provenance;
- strictly time-ordered frames with unique frame IDs and state labels;
- exactly one pose per declared component in every frame;
- pose translation X/Y, angular position, and Z minimum/maximum.

The viewer supports neutral top-view descriptors from WP-59: cylinder, annulus and extruded XY polygon. The validator checks geometry completeness and positive dimensions. Geometry is rendered as a 2D XY envelope with component orientation; the supplied Z span is displayed as metadata. This is not a complete 3D assembly rendering.

No default component, dimension, coordinate, material, pose, motion sample, time step or acceptance limit is populated. Empty/unavailable design inputs remain absent until sourced and approved.

## 5. Validation and playback behavior

The Python validator checks:
1. Both candidate packages exist and their common baseline revisions match.
2. Candidate IDs and units are correct.
3. Component IDs are unique and each component has geometry, drawing reference, status, evidence and source revision.
4. Frame IDs are unique, timestamps strictly increase and all four states are present.
5. Every frame contains exactly one complete pose for every component.
6. The reset sequence returns to a later stopped-at-zero frame.
7. No candidate is selected, no design is frozen and no manufacturing release is authorized.

The browser viewer imports a JSON file locally, permits CW/CL selection, supports play/pause, previous/next and direct frame scrubbing. Playback advances only through supplied samples. It does not interpolate between frames or invent intermediate poses. The viewer makes no network request and does not upload imported data.

## 6. Visualization conventions

The viewer uses a top-down XY projection. The component geometry is centered at the supplied pose and rotated by the supplied angle. The component's Z interval is not used to infer collision or occlusion; the displayed Z span is contextual metadata only.

A component outline is a neutral envelope. For example, a cylinder descriptor does not imply a gear wheel, and a polygon descriptor does not imply a validated cam or heart-cam profile. Detailed teeth, contact faces, followers, springs, pivots, bearing supports and case/dial features must be supplied from separately controlled CAD data.

## 7. Verification and acceptance criteria

| ID | Acceptance criterion |
|---|---|
| AC-01 | Both CW and CL candidates validate independently against one common baseline |
| AC-02 | All four requested states are represented with a valid reset-to-zero sequence |
| AC-03 | Frame timestamps are strictly increasing and component poses are complete |
| AC-04 | Geometry, pose, drawing and evidence/source references are preserved |
| AC-05 | Viewer candidate selection, sample scrubbing and sequential playback operate only on supplied frames |
| AC-06 | Missing, duplicate or malformed records are rejected rather than silently repaired |
| AC-07 | No interpolation, kinematic solution, physical clearance certification or design selection is claimed |
| AC-08 | No design freeze, prototype release or manufacturing authorization is emitted |

Synthetic unit-test fixtures validate software behavior only. They are not C-01 design data, dimensions, component proposals, measured motion or acceptance results.

Run the validator tests from the tools directory:

```bash
python -m unittest test_c01_motion_visualization.py
```

The HTML viewer should be opened locally and exercised with a separately prepared, controlled JSON package. No test execution or browser compatibility result is claimed by this document.

## 8. Engineering limitations and next evidence

WP-60 does not:
- solve kinematics or generate motion from constraints;
- interpolate or extrapolate component positions;
- simulate forces, torque, friction, spring behavior, impact or energy;
- calculate swept-solid or continuous collision clearance;
- certify fit, tolerances, assembly access, shock resistance, wear or service life;
- verify physical reset interlock or chronograph performance;
- generate detailed manufacturing CAD or release drawings.

Before a design review can rely on this visualization, engineers must supply approved datum realization, candidate geometry and drawing revisions, measured or independently validated motion samples, synchronized measurement evidence, uncertainty and processing records, and independent review. Physical acceptance remains governed by WP-30, WP-31, WP-32 and the controlled prototype/test release process.

## 9. Revision and release record

| Revision | Change | Status |
|---|---|---|
| A | Initial two-candidate sampled-motion package validator, browser viewer and synthetic regression tests | Framework only; no C-01 motion or geometry released |

**Release statement:** WP-60 is a development-branch engineering visualization framework. It does not select CW or CL, select a clutch, freeze C-01, prove physical operation, certify clearance, or authorize assembly, testing or manufacture.
