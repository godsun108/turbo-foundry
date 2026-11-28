# WP-55 — Detailed Mechanical Motion and Contact Analysis

- **Document ID:** SEB-C01-WP-55
- **Revision:** A — initial controlled issue
- **Status:** Evidence-gated sampled analysis framework; no motion law or contact design approved
- **Branch:** \`steward/c-01-movement-foundation\`
- **Software:** \`tools/c01_motion_contact_analysis.py\`
- **Verification:** \`tools/test_c01_motion_contact_analysis.py\`
- **Dependencies:** WP-33, WP-41 through WP-54

## 1. Purpose and boundary

WP-55 defines a traceable analysis path for the unresolved column-wheel (CW) and cam/lever (CL) control candidates. It develops the next engineering layer after WP-54's component input contracts:
- sampled member motion and axial-aware envelope relationships;
- signed gap/contact-band/penetration screening;
- planar velocity, acceleration and angular-velocity estimates;
- event-order and event-interval analysis;
- explicit lever moment calculation from supplied force vectors;
- candidate data comparability checks.

The model is not a multibody dynamics engine, frictional contact solver, finite-element model, flexible-body analysis, full CAD swept-volume solver or physical test. It cannot establish contact force, wear, impact stress, vibration, noise, fatigue, operating life, physical fit or prototype readiness.

## 2. Candidate scope

The same analysis contract applies independently to:
- **CW:** column-wheel indexing member, indexer, jumper, operating levers and state-retention members.
- **CL:** cam/follower, operating levers, detent/state-retention members and return elements.

Shared analysis boundaries include pusher input, clutch command, stopped-train retention, reset-hammer command, heart-cam return and running-reset interlock. The four WP-33 clutch/control combinations remain unresolved. Motion data from different candidate configurations must not be pooled as if they were identical.

## 3. Input contract and traceability

A motion package requires:
- candidate ID and configuration revision;
- time unit (seconds) and length unit (millimetres);
- package evidence ID and source revision;
- strictly increasing time samples;
- uniquely identified bodies;
- body role, supported envelope type, radius and provenance;
- one XY position, angular position and axial interval per body per time sample.

Angular input is in degrees and must be supplied as a continuous/unwrapped series when differentiating. Geometry, sample rate, time window, positions and orientations are never defaulted. A missing pose or source remains an explicit gap in the analysis record.

## 4. Sampled envelope gap and contact screening

For two circular XY envelopes with radii \(r_A\) and \(r_B\), center separation \(d\), and overlapping axial intervals:

\[
g = d-r_A-r_B
\]

Interpretation:
- \(g>0\): positive sampled envelope gap;
- \(g=0\): nominal envelope tangency;
- \(g<0\): sampled envelope penetration.

Pairs whose axial intervals do not overlap are excluded at that sample. The report records each sample, minimum signed gap, maximum sampled penetration, and number of samples within the caller-supplied contact band.

This is only a coarse geometric envelope screen. A negative gap may indicate an invalid candidate pose or an intentionally overlapping abstract envelope; it is not a calculated elastic contact state. A positive gap between sampled instants does not rule out collision between samples. The model does not calculate normal force, friction, contact patch, Hertz stress, local curvature, surface roughness or wear.

## 5. Kinematic differentiation

For sampled position \(x_i\) at time \(t_i\), the utility estimates velocity using finite differences:

\[
v_i \approx \frac{x_{i+1}-x_{i-1}}{t_{i+1}-t_{i-1}}
\]

Endpoint estimates use one-sided differences. Acceleration is estimated by differentiating the velocity samples. Angular velocity is calculated from the supplied continuous/unwrapped angle series.

These are descriptive estimates sensitive to sample spacing and measurement noise. No smoothing, filtering, curve fitting, dynamic model or uncertainty propagation is applied. They are not suitable as an acceptance result until the measurement chain, sampling strategy, uncertainty and processing method are approved.

## 6. Event timing and sequence

Candidate-specific events may include:
- pusher input begins;
- indexer advances or cam follower transitions;
- state-retention member releases or locks;
- clutch command changes;
- stopped-train restraint changes;
- reset hammer is enabled or withdrawn;
- interlock blocks reset while running.

WP-55 checks that a caller-specified event list exists and occurs in the specified strictly increasing order. It reports measured intervals between consecutive events. It does not set an expected duration, dwell, timing tolerance or preferred motion law. Those values require approved requirements and synchronized physical or validated simulation evidence.

The event sequence must be reviewed for incomplete pusher strokes, interrupted actuation, overlapping commands, rebound, bounce, ambiguous state, clutch phase, retention phase and hammer clearance.

## 7. Lever moment screening

For a planar force vector \(\mathbf{F}\) applied at position \(\mathbf{r}\) relative to a declared pivot:

\[
M_z = r_xF_y-r_yF_x
\]

The tool reports signed moment in N·mm and N·m from explicit coordinates and force components. This is a statics arithmetic check only. It does not solve a linkage, include friction or compliance, determine spring forces, calculate dynamic equilibrium, or infer user pusher force.

All pivot/contact coordinates and force measurements must carry datum, calibration, uncertainty and source evidence in the controlling engineering record.

## 8. Candidate comparison rules

The metadata comparison helper checks configuration revision and declared units. A successful result means only that the supplied metadata fields match. It does not prove that:
- the mechanisms are physically equivalent;
- fixtures or boundary conditions match;
- sample clocks are synchronized;
- instrument calibration or uncertainty is comparable;
- load, lubrication, temperature, wear state or assembly condition match.

Use WP-49/WP-50 data acquisition and analysis controls and WP-52's paired experimental protocol for physical comparisons. Preserve separate run IDs and raw evidence.

## 9. Required analysis campaigns

### 9.1 CW motion campaign

Capture and review:
- wheel/indexer angular motion and index completion;
- column/follower or lever engagement path;
- jumper release, advance and re-lock sequence;
- state retention under interrupted and partial input;
- clutch and stopped-retention command timing;
- reset-hammer enable/withdrawal timing;
- running-reset interlock block sequence.

### 9.2 CL motion campaign

Capture and review:
- cam angle and follower displacement;
- follower contact continuity and any separation;
- lever pivot motion and output travel;
- dwell/state-retention behavior;
- transition timing and return motion;
- clutch and stopped-retention command timing;
- reset-hammer enable/withdrawal timing;
- running-reset interlock block sequence.

The model currently accepts sampled body envelopes and event records. It does not yet calculate a cam's theoretical follower displacement from profile geometry or solve a column-wheel indexer path. Those require explicit mechanism topology, constraints, contact geometry and a validated solver.

### 9.3 Shared reset and interlock campaign

For all indicated chronograph axes, establish zero datum, hammer approach, contact order, return, withdrawal and clearance. For running reset, demonstrate that the actual physical mechanism prevents reset contact while running and remains in the running state. CAD, sampled envelope checks and software state machines cannot replace physical interlock inspection and test.

## 10. Executable model and verification

Files:
- \`tools/c01_motion_contact_analysis.py\`
- \`tools/test_c01_motion_contact_analysis.py\`

The model provides:
- evidence-gated motion package validation;
- sampled circle-envelope gap/contact/penetration screening;
- finite-difference kinematic descriptors;
- event order and interval analysis;
- explicit planar lever moment calculation;
- metadata-only candidate comparability.

Run from the tools directory:

\`\`\`sh
python -m unittest test_c01_motion_contact_analysis.py
\`\`\`

The test fixtures are synthetic and are not C-01 geometry, motion, force, contact, timing or test data.

## 11. Acceptance criteria

| ID | Acceptance criterion | Required evidence |
|---|---|---|
| WP55-AC-01 | Each candidate has a controlled motion package and configuration revision | Approved input register |
| WP55-AC-02 | All bodies and samples have traceable geometry and provenance | Source drawings and measurement records |
| WP55-AC-03 | Sampled envelope gaps and axial overlaps are reviewed | Analysis report and geometry review |
| WP55-AC-04 | Motion derivatives use approved sampling and processing | Calibrated synchronized measurement procedure |
| WP55-AC-05 | Required events occur in approved order and timing windows | Physical or validated simulation event records |
| WP55-AC-06 | Lever moments use traceable pivot, contact and force inputs | Approved load path and instrument records |
| WP55-AC-07 | Partial/interrupted actuation produces a defined safe state | Controlled physical test |
| WP55-AC-08 | Reset is blocked while running on the actual mechanism | Physical interlock inspection and test |
| WP55-AC-09 | CW/CL comparisons use matched conditions and uncertainty | WP-49/WP-50/WP-52 records |
| WP55-AC-10 | Independent review closes motion/contact risks | Signed engineering review |

No numeric acceptance thresholds are assigned in WP-55.

## 12. Open items and release boundary

Still open:
- CW/CL architecture selection;
- column count, indexing topology and motion law;
- cam contour, follower type, contact law and dwell;
- lever pivots, arm lengths and clearances;
- spring characteristics and return behavior;
- clutch and stopped-retention timing;
- reset hammer arrangement and heart-cam contours;
- physical running-reset interlock geometry;
- contact materials, finish, lubrication and wear limits;
- all numerical performance and acceptance limits.

WP-55 does not select an architecture, prove physical contact, certify clearance, freeze C-01, authorize manufacture or release a test campaign. Physical validation remains governed by approved first-article configuration, fixture qualification and WP-52 test authorization.

## 13. Revision history

| Revision | Description | Status |
|---|---|---|
| A | Initial evidence-gated sampled motion/contact analysis framework | Issued for engineering development |
