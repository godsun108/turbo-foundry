# WP-54 — Detailed CW and CL Mechanism Component Design

- **Document ID:** SEB-C01-WP-54
- **Revision:** A — initial controlled issue
- **Status:** Evidence-gated component-definition framework; no architecture selected or geometry released
- **Branch:** \`steward/c-01-movement-foundation\`
- **Software:** \`tools/c01_control_component_design.py\`
- **Verification:** \`tools/test_c01_control_component_design.py\`
- **Dependencies:** WP-33, WP-36, WP-37, WP-41, WP-42, WP-44, WP-46 through WP-53

## 1. Purpose and design boundary

WP-54 advances both chronograph control candidates from functional architecture toward component-level engineering definition:

- **CW:** indexed column-wheel control.
- **CL:** cam/lever control.

The purpose is to establish component families, geometric input contracts, interfaces, evidence requirements, parametric CAD handoff and verification criteria. It does **not** select CW or CL, choose one of the four clutch/control combinations, freeze the movement, or authorize a physical prototype.

All dimensions, profiles, spring characteristics, forces, materials, tolerances, clearances, finishes and acceptance limits remain TBD until supported by controlled source evidence and approved requirements. No numerical values in synthetic software tests are C-01 design data.

## 2. Controlled design inputs and units

The executable model accepts explicit millimetre geometry and traceable evidence identifiers. Angular quantities are degrees. Every component carries:
- unique component ID and candidate ID;
- functional role and supported geometry type;
- explicit geometry inputs;
- unit declaration;
- evidence ID and source revision.

Supported preliminary envelope primitives are circle, annulus and closed-by-implicit-closure XY polygon. These are visualization and screening primitives, not complete gear teeth, contact surfaces, spring solids or production drawings.

No default dimensions are supplied. Missing geometry remains undefined; it is not inferred from a nominal watch size or a prior candidate.

## 3. CW component definition — column wheel

The CW component breakdown shall separately identify, where applicable:

1. wheel body and hub;
2. indexing columns or equivalent control features;
3. pivot/bore and axial location interfaces;
4. indexing pin/driver interface;
5. jumper or state-retention interface;
6. control-lever contact surfaces;
7. pusher-to-indexer transmission;
8. clutch, stopped-retention and reset-hammer command interfaces.

### 3.1 Indexing geometry

For an explicitly supplied column count \(N\), indexing radius \(r\), and phase \(\phi\), the framework calculates only equal angular pitch and adjacent-column chord:

\[
\Delta\theta = \frac{360^\circ}{N}, \qquad
c = 2r\sin\left(\frac{\Delta\theta}{2}\right)
\]

This is a geometric relationship, not a selected column count, column diameter, wheel diameter, indexer stroke or jumper design. Actual column shape, height, width, flank geometry, indexing pin path, dwell, locking and phase must be defined from controlled mechanism drawings and verified against the complete state sequence.

Required evidence includes indexing repeatability, incomplete/interrupted actuation behavior, state retention, contact wear, pusher force/travel, phase relationship to clutch and retention, and assembly/service access.

## 4. CL component definition — cam and lever

The CL component breakdown shall separately identify, as applicable:

1. cam or cam plate;
2. follower(s) and follower contact geometry;
3. operating lever(s), pivots and contact pads;
4. state-retention or detent member;
5. return springs and anchors;
6. clutch-command output;
7. stopped-retention command output;
8. reset-hammer command output;
9. pusher input and travel stops.

Cam profile input is represented as an explicitly evidenced ordered XY point set. The current validator checks finite coordinates, unique vertices, nonzero edges and nonzero signed polygon area. It treats the last point as connected to the first. It does not perform curve fitting, self-intersection analysis, curvature continuity, pressure-angle analysis, follower-offset compensation, contact stress, dynamic acceleration or dwell optimization.

The final CL definition must additionally establish follower type, contact normal, pivot coordinates, lever arm geometry, motion law, dwell/state retention, transition timing, interrupted-stroke response, wear and lubrication. These remain open until a controlled profile and kinematic model are supplied.

## 5. Shared components and interfaces

Both candidates retain shared functional requirements for:
- reset hammer(s);
- heart cam(s) for each indicated chronograph axis;
- physical running-reset interlock;
- return behavior and positive state retention;
- common movement and fixture datums.

The interface register requires unique IDs, distinct declared component endpoints, a functional definition, evidence ID and source revision. Required interface types are:
- pusher to control;
- control to clutch;
- control to stopped retention;
- control to reset;
- reset hammer to heart;
- running-reset block.

The register is a minimum functional boundary, not a complete interface-control drawing. Detailed interface records must add coordinate frame, mating geometry, degrees of freedom, motion direction, travel, contact condition, axial stack, tolerance, force boundary, spring/return behavior, lubrication, inspection and verification method when those data are approved.

## 6. Springs, pivots and contact interfaces

### 6.1 Springs

Spring design must be based on an approved geometry/material model or measured force-deflection / torque-angle data with instrument calibration, uncertainty and provenance. The WP-54 utility validates monotonic displacement samples and records their units and source. It deliberately does not fit a spring rate, extrapolate a curve, select a material or determine fatigue life.

For each spring, the controlled design record must define function, end conditions, preload, working range, force/torque envelope, stress/fatigue method, adjustment, retention and inspection criteria.

### 6.2 Pivots and supports

Each pivot/arbor record must link to the WP-21/23/24 datum and support architecture and include approved axis, support member, bearing/jewel interface, diameter, fit, endshake/side-shake requirements, lubrication and inspection references. WP-54 does not assign pivot diameters, bearing fits, jewel sizes or tolerances.

### 6.3 Contact pairs

Column/follower, cam/follower, lever/stop, jumper/indexer, hammer/heart and interlock contact pairs require identified surfaces, material/finish evidence, lubrication, load and motion boundary, wear inspection and acceptance criteria. No friction coefficient, contact pressure, surface finish or wear limit is invented.

## 7. Reset hammer and heart-cam definition

The reset design must account for central chronograph seconds, minute totalizer and hour totalizer. For each axis, drawings must establish:
- approved zero datum and angular orientation;
- heart profile and mounting/anti-slip method;
- hammer face geometry and contact sequence;
- hammer pivot or translation axis;
- full reset travel, return and withdrawal;
- contact and clearance through the full stroke;
- counter indexing/jumper release and re-engagement phase;
- hand/arbor retention and repeatable optical zero measurement.

Common versus separate hammers remains open. A heart cam is not assumed to be a mathematically ideal heart; its actual contour must be supplied as controlled geometry and evaluated for reset behavior. The polygon helper is only an initial contour data contract and does not prove functional heart-cam performance.

## 8. Physical running-reset interlock

The interlock must mechanically prevent reset-hammer actuation while the chronograph is running. Its component definition must identify:
- the member whose motion is blocked;
- the blocking member and its support;
- the protected running state and safe state;
- the force path and pusher overload/partial-stroke behavior;
- clearances and tolerance stack;
- reset availability when stopped;
- inspection points and physical test procedure.

The software record validator can check that the functional definition is populated. It always reports physical verification as false. Only direct inspection and a controlled test on the actual candidate article can establish interlock evidence. A simulated sequence, CAD animation, dashboard status or evidence-ID string is not physical proof.

## 9. Parametric CAD handoff

The module can emit OpenSCAD source for explicit circle, annulus and polygon envelope primitives. It does not render the source or certify:
- complete swept-volume clearance;
- actual cam/follower contact or pressure angle;
- column-wheel indexing and locking;
- spring stress/fatigue;
- gear-tooth contact;
- tolerance stack, deflection or shock performance;
- bearing life, lubrication or serviceability;
- physical fit or manufacturability.

Generated source is an engineering visualization aid only. All geometry must be reviewed against controlled drawings and source evidence before it is used in any physical process.

## 10. Executable model and verification

Files:
- \`tools/c01_control_component_design.py\`
- \`tools/test_c01_control_component_design.py\`

The model provides:
- equal-pitch/chord calculation from explicit CW indexing inputs;
- closed polygon input validation for cam/heart contours;
- component geometry and provenance validation;
- candidate-specific component-role and interface completeness checks;
- spring curve sample validation without spring-rate fitting;
- functional interlock record validation with physical verification explicitly false;
- OpenSCAD envelope source generation from explicit geometry.

Run from the tools directory:

\`\`\`sh
python -m unittest test_c01_control_component_design.py
\`\`\`

The test fixtures are synthetic software fixtures only. They do not represent selected C-01 component counts, dimensions, profiles, spring rates, materials or tolerances.

## 11. Acceptance criteria

| ID | Acceptance criterion | Required evidence |
|---|---|---|
| WP54-AC-01 | CW and CL definitions remain separate, traceable candidates | Candidate configuration records |
| WP54-AC-02 | Every component has unique ID, role, units and provenance | Controlled component register |
| WP54-AC-03 | CW indexing geometry is derived only from approved inputs | Column-wheel drawing and dimensional inspection |
| WP54-AC-04 | CL profile is controlled and contact/kinematics reviewed | Approved cam/follower drawing and motion analysis |
| WP54-AC-05 | Pivots, supports and contact pairs reconcile with structural architecture | WP-21/23/24 interface and tolerance review |
| WP54-AC-06 | Springs have approved load/deflection evidence and fatigue basis | Material, calculation and test records |
| WP54-AC-07 | Reset returns all indicated axes to approved zero | Physical reset repeatability test |
| WP54-AC-08 | Reset is positively blocked while running | Actual-article interlock inspection and test |
| WP54-AC-09 | CAD envelope is traceable to approved geometry | Reviewed CAD source and drawing revisions |
| WP54-AC-10 | Independent review closes candidate-specific risks | Signed design review and disposition |

## 12. Open decisions and release boundary

The following remain unresolved:
- CW versus CL control architecture;
- four clutch/control combinations from WP-33;
- column count and geometry;
- cam profile, follower type and motion law;
- spring types, materials and characteristics;
- pivot/support geometry and fits;
- contact materials, finish and lubrication;
- reset hammer arrangement and heart contours;
- physical running-reset interlock geometry;
- all numerical tolerances and performance limits.

WP-54 does not select a winner, freeze C-01, create a manufacturing BOM, authorize first-article build, or release WP-52 comparative testing. Those gates remain governed by WP-30 through WP-53 and formal design-authority approval.

## 13. Revision history

| Revision | Description | Status |
|---|---|---|
| A | Initial evidence-gated CW/CL component-definition framework | Issued for engineering development |
