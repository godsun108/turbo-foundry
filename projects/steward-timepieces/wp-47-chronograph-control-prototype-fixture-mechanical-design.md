# WP-47 — Chronograph Control Prototype Fixture Mechanical Design

- **Document ID:** SEB-C01-WP-47
- **Revision:** A — initial controlled issue
- **Status:** Parametric fixture architecture and CAD input contract; no physical dimensions released
- **Project:** STEWARD C-01
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_control_fixture.py`
- **Synthetic regression tests:** `tools/test_c01_control_fixture.py`
- **Predecessors:** WP-22, WP-23, WP-24, WP-35, WP-36, WP-40, WP-43, WP-44 and WP-46

## 1. Purpose and boundary

WP-47 converts the WP-46 test-bench concept into a controlled parametric mechanical fixture definition. The fixture is intended to support comparable evaluation of the unresolved column-wheel (CW) and cam/lever (CL) chronograph control candidates.

The architecture uses a common structural base and two separately defined, interchangeable candidate carriers. The carriers are alternatives: they are not intended to be installed simultaneously. A common instrument reference structure supports the pusher actuator, inline force transducer, independent travel sensor and optical observation system. A removable guard envelope is represented in the CAD source for design review.

This is an engineering definition framework, not a dimensioned fixture drawing, finished CAD solid, machining package, validated test rig or authorization to build. No dimensions, material, fastener, sensor model, actuator, movement size, hole pattern, fit, load rating or safety rating is selected by this document. Synthetic values in unit tests are software fixtures only.

## 2. Design requirements

| ID | Requirement | Verification |
|---|---|---|
| WP47-REQ-01 | Common base supports repeatable installation of either candidate carrier | Datum and interface inspection |
| WP47-REQ-02 | CW and CL carriers have independent controlled identities and geometry | Carrier register and configuration audit |
| WP47-REQ-03 | Candidate exchange preserves the common instrument reference frame | Datum-transfer and repeatability study |
| WP47-REQ-04 | Pusher actuator force path is aligned with the approved pusher axis | Measured axis offset and angular alignment |
| WP47-REQ-05 | Force transducer is located in the pusher force path without unmeasured bypass | Load-path inspection and calibration check |
| WP47-REQ-06 | Travel is measured independently of actuator command | Independent displacement channel |
| WP47-REQ-07 | Optical access permits observation without interfering with moving parts | Visibility and clearance review |
| WP47-REQ-08 | Guarding and safe actuator disengagement are provided | Approved hazard review and guarded test |
| WP47-REQ-09 | Every physical feature has evidence and source revision | Geometry provenance audit |
| WP47-REQ-10 | Fixture does not distort the movement or candidate control assembly | Mounting-load and distortion verification |

## 3. Functional architecture

### 3.1 Common structural base

The base is the master fixture structure. It provides:
- controlled primary datum surfaces and a repeatable origin;
- explicit mounting interfaces for the candidate carrier;
- attachment interfaces for the instrument-support frame;
- access for inspection, installation and removal;
- a defined interface to the laboratory bench or secondary support.

The base outline, thickness, top plane, mounting holes and any reliefs must come from an approved fixture drawing or controlled CAD revision. The base must be checked for stiffness, local bearing stress, flatness, mounting distortion, vibration response and repeatability. A visual envelope model is not a stiffness calculation.

### 3.2 Interchangeable candidate carriers

Two carrier configurations are required:
- **CW carrier:** holds the column-wheel candidate subassembly.
- **CL carrier:** holds the cam/lever candidate subassembly.

Each carrier has a unique ID, revision, explicit outline, axial position, mounting-hole register, locating/registration scheme and source provenance. Candidate-specific geometry remains isolated to the carrier wherever practicable. Shared actuator and sensor coordinates are referenced to the common fixture datum, not re-established by eye after each exchange.

The carrier-to-base interface requires a controlled locating strategy. Candidate approaches include a deterministic datum/locator scheme with separate clamping fasteners, but locator type, quantity, dimensions, material and tolerances are deliberately not selected. The design must avoid using fastener clearance as the sole precision location method unless an approved analysis justifies it.

The movement or mechanism article must be supported at approved structural mounting points. Clamping must not load a thin plate, distort pivots, alter gear mesh, preload a bridge or change the pusher axis. The carrier must not use the movement itself as a structural bridge between unrelated fixture supports.

### 3.3 Instrument reference structure

The actuator and measurement instruments mount to a common reference structure tied to the base datum. The structure must provide:
- adjustment during setup;
- positive locking after alignment;
- sufficient stiffness for the approved force and travel envelope;
- access for calibration artifacts and sensor replacement;
- a documented method to re-establish alignment after carrier exchange.

The final frame type, section, material, joints and adjustment mechanism require load and stiffness analysis. No frame section or material is selected here.

### 3.4 Pusher actuator and force path

The nominal measurement chain is:

`actuator → force transducer → pusher contact tip → case pusher/stem → candidate control mechanism`

The force transducer must be in series with the applied force path. Mechanical stops, actuator bearings, guides, cables or fixture contact must not create an unmeasured parallel force path. The pusher contact tip must be replaceable and must not introduce a lateral force or damage the case/stem interface.

The actuator axis is aligned to the approved pusher axis. The software supports an explicit axis-offset and angular-tolerance check only when those tolerances are supplied. The tolerances must be derived from the actual pusher geometry, fixture stiffness and measurement uncertainty; WP-47 assigns no numeric values.

Actuator travel command is not the measured pusher travel. A separate displacement sensor measures actual stem/contact displacement relative to a stable datum. Actuator compliance, transducer deflection, fixture flexure, tip compliance and backlash must be measured or included in the uncertainty budget.

### 3.5 Optical observation

Optical access is required for the control member, indexing element, clutch command, retention member, reset hammer/heart interface and chronograph output as applicable to the selected candidate. The fixture should permit repeatable camera location, focus, illumination and calibration target placement.

A viewing aperture or transparent guard panel may be considered after the hazard review. Optical markers must not add meaningful mass, friction or contact to moving members. Camera mounts, line of sight, magnification and lighting remain sourced inputs.

### 3.6 Guarding and safe disengagement

The guard design must contain or prevent access to relevant moving parts and provide a safe means to remove actuator input. Guard geometry, material, retention, access interlocks and any transparent panel require a documented hazard assessment and approval. The CAD envelope is only a placeholder boundary for review; it is not a certified protective enclosure.

The physical interlock proof procedure remains governed by WP-46. No running-reset test may proceed solely because the WP-47 geometry model validates.

## 4. Datum and coordinate strategy

The fixture shall establish a controlled fixture datum frame independent of the movement's internal coordinate system:
- **Fixture datum A:** primary mounting plane.
- **Fixture datum B:** primary in-plane locating reference.
- **Fixture datum C:** secondary in-plane locating reference.
- **Fixture origin:** intersection/realization defined by the approved datum scheme.
- **Actuator axis:** a measured line expressed in the fixture frame.
- **Sensor axes:** independently measured and related to the same frame.

Datum feature geometry, GD&T, flatness, perpendicularity, locator positions and transfer uncertainty must be assigned on the released drawing. The WP-14/WP-20 movement XY convention remains separate; a controlled transform between fixture and movement frames must be documented for each carrier configuration.

No fixture coordinate is assumed to equal a C-01 arbor coordinate. WP-23 and WP-24 remain the controlled sources for movement axes and supports. WP-21 M0 remains the movement axial datum and must not be conflated with fixture datum A.

## 5. Parametric CAD input contract

`tools/c01_control_fixture.py` accepts a configuration with:
- fixture ID, revision and global evidence/source revision;
- common base polygon, thickness, top Z and mounting-hole records;
- exactly one CW and one CL carrier, each with its own polygon, thickness, top Z, mounting-hole records, registration-scheme ID and provenance;
- instrument mounts for pusher actuator, force transducer, travel sensor and optical view, each with origin, axis, envelope radius/length and provenance;
- optional explicit actuator/force-sensor axis-offset and angular tolerances;
- a guard envelope defined by minimum/maximum XYZ coordinates and provenance.

The validator checks input completeness, unique identifiers, positive dimensions, polygon validity, required roles, provenance, and optional actuator/force-transducer alignment. It does not infer missing dimensions. The OpenSCAD generator creates a common base, alternative carrier envelope modules, instrument cylinders and a disabled-by-default guard envelope. The output is an editable source model, not a rendered or validated solid.

### 5.1 Alignment calculations

For two supplied axis lines with points (p_1,p_2) and unit direction vectors (u,v), the shortest separation is calculated from the cross product when the lines are not parallel:

[
d=rac{|(p_2-p_1)cdot(u	imes v)|}{|u	imes v|}
]

For parallel lines, perpendicular point-to-line distance is used. The unsigned angular difference treats an axis and its reverse as the same geometric line:

[
	heta=cos^{-1}(|ucdot v|)
]

The software compares these results only against explicitly supplied limits. A passing geometric check is not proof that the transducer is in series with the force path, that the actuator is free of side load, or that the structure is sufficiently stiff.

## 6. Mechanical design analyses required before release

The following are mandatory design activities, not calculations claimed complete by this package:

1. **Base and frame stiffness:** deflection under the maximum approved actuator load and all relevant mounting conditions.
2. **Carrier stiffness:** local bending and contact deformation at mechanism support points.
3. **Datum transfer:** repeatability and uncertainty after CW/CL carrier exchange.
4. **Pusher alignment:** angular and offset tolerance stack, including case/stem variation.
5. **Force-path integrity:** parasitic load paths, guide friction, actuator compliance and transducer mounting.
6. **Travel measurement:** sensor alignment, cosine error, reference stability and compliance correction.
7. **Vibration and dynamics:** fixture resonance and sensor bandwidth over the approved test profile.
8. **Fasteners and locators:** preload, slip, bearing stress, repeatability and service access.
9. **Guarding:** hazard analysis, access prevention, safe actuator disengagement and inspection access.
10. **Thermal effects:** differential expansion where it materially affects alignment or measurement.
11. **Optical system:** calibration, field of view, lighting, time synchronization and obstruction check.
12. **Movement integrity:** evidence that fixture mounting does not distort the plate, bridge, pivots, gear mesh or case/pusher interface.

Analysis inputs must be sourced from the actual candidate geometry, material certificates, supplier data, measured loads and approved requirements. No material strength, elastic modulus, load, safety factor, deflection or tolerance is invented here.

## 7. Assembly and configuration control

The controlled assembly sequence shall be defined after the design is dimensioned:
1. inspect and identify the base and instrument frame;
2. establish and verify fixture datums;
3. install the selected carrier and record its revision;
4. install the movement/mechanism article at approved support interfaces;
5. verify carrier location and article distortion;
6. install actuator, force transducer and travel sensor;
7. align and lock the instrument reference structure;
8. verify optical view and guard fit;
9. perform calibration/zero checks and independent setup review;
10. release only the specific approved test procedure and article configuration.

Each CW/CL changeover creates a new configuration record. Record carrier serial/revision, article ID, locator and fastener condition, instrument IDs, alignment results, calibration references and setup photographs. Do not reuse a previous alignment result after disassembly unless the approved repeatability study permits it.

## 8. Acceptance criteria and hold points

| Hold point | Acceptance evidence |
|---|---|
| H0 — Requirements | Approved test requirements, article interfaces and force/travel envelope |
| H1 — Geometry | Controlled base, carrier, actuator, sensor and guard geometry with provenance |
| H2 — Structural | Stiffness, stress, mounting distortion and fastener/locator analysis |
| H3 — Metrology | Calibration, alignment, uncertainty and datum-transfer study |
| H4 — Safety | Approved guarding, hazard assessment and stop/disengagement method |
| H5 — CAD review | Independent review of model, drawings, tolerances and assembly access |
| H6 — Fixture qualification | Inspection and repeatability evidence using approved artifacts |
| H7 — Test release | Specific article, procedure, operator and safety approvals under WP-46 |

The following values remain TBD until approved evidence exists: base envelope, thickness, material, carrier dimensions, locator/fastener design, pusher-axis position, actuator stroke, force range, sensor ranges, alignment tolerances, stiffness limits, vibration limits, guard geometry and acceptance thresholds.

Passing the software validator does not pass any physical hold point. No construction, prototype testing or running-reset interlock test is authorized by WP-47.

## 9. Verification and software execution

Run the synthetic regression tests from the tools directory:

```sh
python -m unittest test_c01_control_fixture.py
```

The tests exercise:
- CW/CL carrier completeness;
- provenance and geometry validation;
- actuator/force-transducer axis alignment screening;
- behavior when alignment tolerances are absent;
- OpenSCAD source generation and disabled guard preview.

All test geometry and numeric values are synthetic fixtures used only to test software behavior. They are not C-01 or physical fixture dimensions.

## 10. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial parametric fixture architecture, CAD input contract and mechanical release gates | Pending engineering review |

**Release statement:** WP-47 defines a traceable parametric fixture architecture. It does not provide dimensioned manufacturing drawings, certify mechanical fit or safety, select CW/CL, freeze C-01, or authorize construction or physical testing.
