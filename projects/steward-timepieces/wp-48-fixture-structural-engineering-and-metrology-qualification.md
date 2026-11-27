# WP-48 — Fixture Structural Engineering and Metrology Qualification

- **Document ID:** SEB-C01-WP-48
- **Revision:** A — initial controlled issue
- **Status:** Engineering calculation and qualification framework; no fixture qualification claimed
- **Project:** STEWARD C-01
- **Branch:** steward/c-01-movement-foundation
- **Software:** tools/c01_fixture_structural.py
- **Synthetic regression tests:** tools/test_c01_fixture_structural.py
- **Predecessors:** WP-30, WP-43, WP-46 and WP-47

## 1. Purpose

WP-48 defines the structural and metrology evidence required before the WP-47 chronograph-control test fixture can be relied upon for comparative CW/CL measurements. The objective is to separate actual mechanism behavior from fixture flexure, datum-transfer error, actuator misalignment, sensor uncertainty, joint motion and measurement-system effects.

This package supplies traceable calculation functions and qualification gates. It does not contain actual fixture dimensions, material properties, measured forces, instrument calibration data, uncertainty values or physical test results. Synthetic test numbers exist only to exercise software behavior.

## 2. Scope and boundaries

Included:
- preliminary beam-deflection and bending-stress screening for explicitly declared idealized support cases;
- fixture-compliance correction of measured travel under an explicit sign convention;
- datum-transfer repeatability statistics from repeated observations;
- independent standard-uncertainty combination by root-sum-square (RSS);
- guard-banded acceptance with pass/fail/indeterminate outcomes;
- qualification-packet completeness validation;
- structural, interface, metrology and independent-review evidence requirements.

Not included:
- finite-element analysis, contact/nonlinear analysis, full frame or carrier model;
- material selection, allowables, fatigue life, fastener preload or joint-slip design;
- vibration modal analysis or dynamic actuator/load-cell response;
- calibration of instruments or a real-world uncertainty budget;
- proof of fixture stiffness, datum accuracy, guard safety or movement integrity;
- permission to perform physical tests.

## 3. Requirements and verification

| ID | Requirement | Verification evidence |
|---|---|---|
| WP48-REQ-01 | Base/frame deflection shall be bounded under the approved load envelope | Controlled structural analysis and physical correlation |
| WP48-REQ-02 | Candidate carrier deflection shall not materially alter mechanism geometry | Carrier analysis and article distortion measurement |
| WP48-REQ-03 | CW/CL carrier exchange shall preserve the common datum frame | Repeated datum-transfer study |
| WP48-REQ-04 | Fasteners and locators shall remain stable under the approved load envelope | Joint analysis and inspection |
| WP48-REQ-05 | Pusher load path shall not contain an unmeasured bypass | Physical load-path verification |
| WP48-REQ-06 | Fixture compliance shall be measured or included in travel uncertainty | Compliance calibration and correction record |
| WP48-REQ-07 | Force and displacement channels shall have traceable calibration | Instrument certificates and in-situ checks |
| WP48-REQ-08 | Combined measurement uncertainty shall be reported with stated assumptions | Approved uncertainty budget |
| WP48-REQ-09 | Measurement acceptance shall use approved limits and guard-banding | WP-48 evaluation record |
| WP48-REQ-10 | Movement article shall not be distorted by fixture mounting | Before/after dimensional and functional comparison |
| WP48-REQ-11 | Guard and hazard review shall be approved | Signed safety review |
| WP48-REQ-12 | Qualification requires independent review | Signed review record and configuration traceability |

## 4. Structural analysis basis

### 4.1 Load definition

The design load cases must be derived from WP-46 approved procedures and measured or approved actuator envelopes. At minimum, assess quasi-static pusher actuation, maximum approved force/travel, off-axis loading, actuator stop/release/fault conditions, carrier exchange, and sensor/camera support loads where relevant.

Do not use an assumed pusher force or synthetic software fixture as a design load. Each load case requires a unique ID, load vector, point/area of application, boundary-condition definition, evidence ID and source revision.

### 4.2 Preliminary beam screening

For an ideal Euler-Bernoulli beam with elastic modulus E, second moment of area I, span L, point load F, and extreme-fiber distance c:

Cantilever with end load:

\[
\delta = \frac{FL^3}{3EI}, \qquad \sigma_{\max} = \frac{FLc}{I}
\]

Simply supported beam with center point load:

\[
\delta = \frac{FL^3}{48EI}, \qquad \sigma_{\max} = \frac{FLc}{4I}
\]

With F in N, L and c in mm, E in N/mm² (MPa), and I in mm⁴, deflection is mm and nominal bending stress is MPa.

The software implements only these two idealized cases. The boundary condition must match a defensible representation of the real support. These equations do not account for shear deformation, plate action, torsion, local bearing/contact, stress concentrations, joints, fastener flexibility, preload, slip, buckling, fatigue, vibration, dynamic amplification or material allowables. They are not a substitute for full structural analysis.

### 4.3 Required detailed analyses

Before structural acceptance, produce:
1. Base plate and support-frame analysis, including bending and torsion.
2. Carrier plate analysis with candidate-specific load application and mounting interfaces.
3. Locator, fastener, clamp and joint analysis, including slip and bearing.
4. Local contact/stress review at mechanism support points.
5. Deflection at actuator, force transducer, travel sensor and optical reference mounts.
6. Modal/dynamic review where actuator frequency content or camera exposure makes it relevant.
7. Thermal sensitivity assessment where expansion affects alignment.
8. Physical verification using a traceable load and displacement setup.

Material modulus and strength values must come from identified material specifications, certificates or controlled supplier data at the applicable condition. Generic handbook values are not released design inputs without engineering approval.

## 5. Fixture compliance and travel correction

The displacement channel must measure actual pusher/stem travel relative to a stable reference. Measured displacement may include fixture, transducer, actuator, tip and contact compliance.

For separately measured fixture compliance Cf in mm/N and applied force F:

\[
\delta_f = F C_f
\]

Under the explicit convention that fixture deflection occurs in the same direction as measured travel:

\[
x_{\mathrm{mechanism}} = x_{\mathrm{measured}} - \delta_f
\]

The software implements this declared scalar correction. It rejects a correction larger than measured travel. It does not correct nonlinear compliance, hysteresis, side load, dynamic behavior, changing boundary conditions or multiple coupled compliance paths. Compliance calibration must use the same configuration, load path, direction and relevant range as the test, or quantify transfer uncertainty.

## 6. Datum-transfer repeatability

The common base and interchangeable carriers must preserve a common actuator/sensor reference frame after removal and reinstallation.

For each controlled datum characteristic:
- perform repeated independent carrier removal/reinstallation cycles;
- record raw readings, instrument ID, calibration, operator, temperature, fixture/carrier revision and setup condition;
- calculate mean, sample standard deviation, min/max and range;
- evaluate directional bias and 3D coordinate transformation separately;
- compare observed variation against approved datum-transfer limits and measurement uncertainty.

The software helper reports scalar descriptive statistics only. It does not establish 3D accuracy, geometric tolerances, datum alignment or a pass result. The test plan must define repetition count and acceptance limits based on the measurement objective; WP-48 invents neither.

## 7. Metrology and uncertainty budget

### 7.1 Required measurement channels

The qualification record shall identify force transducer/signal conditioner, displacement sensor/reference structure, data acquisition/sampling clock, optical measurement/camera scale and timebase, temperature measurement, calibration artifacts, fixture compliance setup, and alignment/datum-transfer equipment as applicable.

Each instrument record requires unique ID, range, resolution, calibration status/due date, uncertainty, procedure revision and evidence source. No instrument model is selected.

### 7.2 Uncertainty contributors

Consider calibration uncertainty, resolution/quantization, repeatability/reproducibility, linearity/hysteresis, alignment/cosine error, fixture and sensor mounting compliance, datum-transfer variation, temperature/drift, sampling/time synchronization, data processing/interpolation, and operator/setup effects.

Convert contributors to standard uncertainties for the same measurand and unit before combination. For independent contributions ui:

\[
u_c = \sqrt{\sum_i u_i^2}, \qquad U = k u_c
\]

The code implements RSS and a caller-supplied coverage factor k. Independence must be justified. Correlated inputs require covariance terms and a more complete budget; this implementation does not handle covariance. The coverage factor alone does not guarantee a particular coverage probability without distribution and degrees-of-freedom assumptions.

### 7.3 Guard-banded decision rule

For measured result y, expanded uncertainty U, and approved interval [L,H], evaluate [y-U, y+U].

- **Pass:** the full uncertainty interval lies inside approved limits.
- **Fail:** the full uncertainty interval lies outside approved limits.
- **Indeterminate:** the uncertainty interval overlaps a limit without being fully inside or fully outside.

Indeterminate results require review, improved measurement capability, or separately approved disposition. Do not silently round or remove uncertainty to force a pass. The code uses this three-state rule and requires explicit limits and evidence references.

## 8. Movement distortion and interface integrity

The fixture shall not change movement functional geometry by mounting force. Before/after checks must address plate flatness and local distortion, bridge seating and clamp preload effects, arbor/pivot freedom and endshake where applicable, gear mesh/backlash, pusher axis/case-stem alignment, and baseline chronograph/timekeeping behavior.

Approved support points and dimensions must trace to controlled movement drawings/models (WP-21 through WP-24 and relevant detailed mechanism packages). A fixture fit check alone is not proof that the movement remains undistorted.

## 9. Qualification packet and release gates

The controlled packet must include fixture/carrier drawings and CAD revisions; load cases and structural calculations; material and fastener specifications; joint/locator and mounting-distortion review; fixture compliance calibration; datum-transfer data; instrument register and calibration records; uncertainty budget; force-path and sensor alignment inspection; guard/hazard review; independent review and open-item disposition.

The software completeness screen requires approved, provenance-backed records for base analysis, carrier analysis, datum transfer, force path, metrology, guard review and independent review. Even a complete packet returns fixture_physically_qualified=false and test_release_authorized=false. An authorized engineering authority must review and release the physical configuration.

## 10. Acceptance criteria

Numerical limits remain controlled inputs and are intentionally TBD. Acceptance requires all approved load cases evaluated; deflection and stress within approved project limits with stated margin and uncertainty; no unapproved joint slip, permanent set or movement distortion; datum-transfer variation within approved limits; calibrated and traceable force/displacement chains; uncertainty fit for the measurement decision; validated compliance correction; approved safety/guard requirements; and configuration-matched independent review.

No numerical force, stiffness, stress, deflection, uncertainty, repeatability, material, safety factor or acceptance limit is created by this work package.

## 11. Software and synthetic verification

Run from the tools directory:

\`\`\`sh
python -m unittest test_c01_fixture_structural.py
\`\`\`

The synthetic regression suite exercises idealized cantilever and simply-supported beam calculations; invalid boundary-condition rejection; compliance correction and over-correction rejection; RSS uncertainty combination and duplicate-ID rejection; guard-banded pass/fail/indeterminate outcomes; scalar datum-transfer statistics; and fail-closed qualification-packet completeness.

All test values are synthetic and are not fixture design inputs or physical test results.

## 12. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial structural-screening, compliance, datum-repeatability and metrology qualification framework | Pending engineering review |

**Release statement:** WP-48 provides calculation methods and qualification gates. It does not demonstrate that the WP-47 fixture is structurally adequate, metrologically qualified, safe, or ready for physical chronograph testing. C-01 remains unfrozen and no physical test is authorized by this document.
