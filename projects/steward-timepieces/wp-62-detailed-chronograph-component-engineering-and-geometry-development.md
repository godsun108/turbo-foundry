# WP-62 — Detailed Chronograph Component Engineering and Geometry Development

- **Document ID:** SEB-C01-WP-62
- **Revision:** A — initial controlled issue
- **Status:** Component engineering register and dimensional-screening framework; no C-01 component geometry approved
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_component_engineering.py`
- **Verification:** `tools/test_c01_component_engineering.py`
- **Dependencies:** WP-20, WP-21, WP-27 through WP-30, WP-34, WP-37 through WP-41, WP-54, WP-57 through WP-61

## 1. Purpose

WP-62 advances WP-61's integrated functional assembly register into controlled component-level engineering definition. It establishes traceable component records, candidate applicability, engineering families, dimensional registers, interface references, analysis references and maturity states. It provides two explicit-input calculations:
- dimensional limit intervals from nominal size and bilateral tolerance magnitudes;
- worst-case diametral journal/bore clearance from finished-size limits.

It does not generate missing geometry or choose dimensions, materials, profiles, tooth counts, clearances, fits or manufacturing processes. CW and CL remain separate unselected candidates.

## 2. Component engineering boundary

The register covers these component families:

| Family | Included component roles |
|---|---|
| Drive train | Drive source, coupling and transmission members |
| Clutch | Engagement/disengagement components |
| Arbor | Central chronograph seconds arbor and rotating supports |
| Counter | Minute and hour totalizer mechanisms |
| Retention | Stopped-train brake/detent/equivalent |
| Control | Column-wheel or cam/lever mechanism |
| Reset | Reset hammer(s) and heart cams |
| Interlock | Positive running-reset block |
| External input | Pusher and case-side command interface |
| Structure | Main plate and bridges |
| Bearing | Jewel/bearing, pivot and support interfaces |

Each component must have a unique ID, functional role, family, candidate scope (shared/CW/CL), function statement, geometry definition, geometry/material/manufacturing maturity, drawing reference, evidence ID and source revision. A role register is not a bill of materials: a role may map to a physical component only when the controlled component record explicitly defines it.

## 3. Candidate configuration control

The engineering package carries two independent component configurations:
- **CW:** requires `column_wheel_control`.
- **CL:** requires `cam_lever_control`.

Both must match the same requirements, movement datum and interface-baseline revisions. Shared components are explicitly marked `candidate_scope=shared`; candidate-specific components must match their configuration. This prevents a CW-only part from silently entering the CL configuration.

The package validator preserves open decisions and always reports architecture selected = false, design frozen = false and manufacturing release authorized = false.

## 4. Dimensional register and calculations

Every dimension record identifies a unique dimension ID, characteristic, unit, nominal value, lower and upper deviation magnitudes, drawing reference, evidence ID, source revision and status. The model supports mm, degrees, N, N·mm, N/mm, g, mm³ and mg. The allowed unit list is a data-integrity check, not a declaration that any unit or dimension is selected for C-01.

For nominal dimension (d), lower deviation magnitude (t_L) and upper deviation magnitude (t_U):

[
d_{min}=d-t_L,qquad d_{max}=d+t_U
]

Positive-only dimensions can require (d_{min}>0). The software does not select tolerances or determine functional suitability.

### 4.1 Journal/bore clearance screening

Given finished shaft limits (D_{s,min},D_{s,max}) and bore limits (D_{b,min},D_{b,max}):

[
C_{min}=D_{b,min}-D_{s,max}
]
[
C_{max}=D_{b,max}-D_{s,min}
]

Negative clearance indicates potential interference within the supplied size limits; positive clearance indicates diametral clearance. This arithmetic does not establish correct horological pivot fit, oil retention, endshake, side shake, thermal behavior, bearing load capacity, wear life or manufacturability. Inputs must come from an approved drawing/specification and traceable measurement or supplier evidence.

## 5. Component-specific engineering definition requirements

### 5.1 Drive source and coupling
Define source arbor identity, direction, speed evidence, coupling geometry, engagement travel, axial/radial location, torque boundary, lubrication and service access. The source arbor and take-off remain open; no source RPM is assumed.

### 5.2 Clutch
For each vertical-friction and horizontal/lateral candidate, define driving/driven members, contact geometry, axial/radial stack, engagement/disengagement sequence, return behavior, drag when disengaged, running load and start disturbance. Do not assume one clutch topology is selected.

### 5.3 Central chronograph seconds arbor
Define arbor shoulders, pivots, bearing spans, wheel/hub attachment, hand fitting, heart-cam interface, axial retention, endshake/side-shake requirements, concentricity and balance. The 1 revolution/minute indication remains a functional target; actual gear train and source remain unselected.

### 5.4 Minute and hour totalizers
For each register independently, define the branch source, gear/index train, arbor, hand attachment, indication convention, reset heart, phase datum, retention and support. Continuous versus jumping remains open for both. A jumping design requires event cadence, indexing impulse, jumper, anti-bounce, phase and transient-load engineering; average-speed ratios alone are insufficient.

### 5.5 Stopped-train retention
Define candidate brake/detent/equivalent, contact pair, engagement and release sequence, holding requirement, wear, lubrication and interaction with clutch and reset. No implementation or holding force is selected.

### 5.6 CW and CL control candidates
CW definition includes wheel/hub, indexing features, pivot, indexer, jumper, dwell/locking geometry and command outputs. CL definition includes cam profile, follower, lever pivots, detent, lost motion, command outputs and return elements. Both require pusher, clutch, retention, reset and interlock interfaces. WP-33/WP-45/WP-54 decision gates remain controlling; WP-62 does not score or choose a winner.

### 5.7 Reset hammer and heart cams
Define each indication's zero datum, heart-cam mounting and profile, hammer contact face, pivot/translation, contact order, return path, clearances and reset repeatability. Common versus separate hammers remains open. Reset while running must be physically blocked and leave the chronograph running; software validation is not proof.

### 5.8 Pusher and running-reset interlock
Define case-to-movement input path, pusher travel/force, seals, stops, return spring, partial actuation, interrupted stroke and positive interlock geometry. Physical interlock verification remains a mandatory test gate.

### 5.9 Plate, bridges and bearing supports
Reference WP-21 datums and WP-23 arbor coordinates. Define support locations, bearing/pivot interfaces, bridge stiffness evidence, fasteners, axial stack, assembly sequence, access and serviceability. No support span, bearing dimensions or structural properties are assumed.

## 6. Evidence and maturity states

Geometry status: not_started, concept, candidate, reviewed or approved.
Material status: TBD, candidate, reviewed or approved.
Manufacturing status: not_started, process_study, candidate, reviewed or approved.
Dimension status: TBD, candidate, reviewed or approved.

An approved status must be supported by the project's controlled review and evidence process; the validator checks record completeness, not the truth or sufficiency of approval. Empty dimension registers are permitted and reported as not dimensioned. No component is promoted automatically.

## 7. Verification and acceptance

The WP-62 software checks:
- both candidate packages and common baseline revisions;
- complete required functional role coverage;
- shared versus candidate-specific applicability;
- unique component and dimension IDs;
- valid units, tolerance intervals and maturity states;
- traceable interface endpoints and analysis references;
- retained open decisions;
- explicit-input journal/bore clearance arithmetic.

Nine synthetic regression tests are included. Synthetic fixture dimensions are software test values only and are not C-01 design inputs.

Run from the tools directory:

```bash
python -m unittest test_c01_component_engineering.py
```

No test execution, CAD rendering, component fit or physical verification is claimed here.

## 8. Required next engineering evidence

The next controlled inputs should be approved source-arbor and going-train interface data; chosen prototype article class; movement datum realization; component drawings and dimension/tolerance schedules; candidate-specific clutch/control geometry; counter indication decisions; bearing and pivot specifications; measured load/torque data; materials and process qualification; and verified physical reset-interlock evidence.

## 9. Release boundary

WP-62 does not certify gear strength/contact, bearing life, spring behavior, dynamic response, torque capacity, energy reserve, rate performance, shock resistance, durability, manufacturability or safety. It does not authorize prototype build, physical testing, design freeze, manufacturing release, merge or deployment.

**Release statement:** WP-62 is a development-branch component engineering framework. C-01 has no approved component geometry or dimension schedule. CW and CL remain unselected; all numerical design inputs require controlled evidence and design-authority approval.
