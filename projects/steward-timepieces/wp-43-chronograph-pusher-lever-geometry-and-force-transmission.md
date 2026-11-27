# WP-43 — Chronograph Pusher, Lever Geometry and Force-Transmission Engineering

- **Document ID:** SEB-C01-WP-43
- **Revision:** A — initial controlled issue
- **Status:** Parametric force/travel framework; no physical dimensions or force limits released
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_pusher_force.py`
- **Verification:** `tools/test_c01_pusher_force.py`
- **Dependencies:** WP-30, WP-32, WP-34, WP-35, WP-36, WP-37, WP-40, WP-41, WP-42

## 1. Purpose and boundary

WP-43 defines the mechanical force path from case pusher to chronograph control members and the calculation interfaces needed to evaluate lever geometry, force multiplication, lost motion, travel and measured actuation work.

It applies to both WP-42 candidates:
- CW: pusher → transmission → indexer/column-wheel actuation → state retention.
- CL: pusher → transmission → cam/follower or state-setting actuation → detent/dwell retention.

Both candidates must also command the clutch, stopped-train restraint and reset hammer through their control levers. The actual topology, number of stages, pivots, contact points, dimensions, forces, spring rates, materials and tolerances remain unselected.

The model's rigid-lever equations are preliminary quasi-static screening relations. They do not model flexure, frictional contact, non-linear cams, side loading, impact, dynamic inertia, pin-slot geometry or elastic deformation.

## 2. System boundary and functional path

The controlled force path shall be drawn from the external case interface to the final commanded member:

1. pusher cap/contact surface;
2. case pusher stem and guide;
3. sealing and return elements, where used;
4. internal contact or transmission member;
5. lever stage(s), pivots and supports;
6. indexing/cam actuation member;
7. state-retention feature;
8. clutch command lever;
9. stopped-retention command lever;
10. reset command lever and running-state interlock.

A candidate may combine functions in a single member only when the component and interface registers document the shared role and its failure consequences. Pusher input must not bypass the positive running-reset interlock.

## 3. Geometry and datum requirements

Every lever stage must identify:
- pivot axis and its WP-21/WP-23 structural datum reference;
- input contact point and output contact point;
- effective perpendicular input and output moment arms at the evaluated pose;
- contact direction and permitted motion;
- input/output member IDs and source revision;
- lever thickness, bearing/support arrangement and axial stack when established;
- stop positions, clearances and full-stroke envelope;
- measured or drawing-derived evidence for each geometric value.

For a simple rigid lever with perpendicular forces and small angular motion:

`MA = r_in / r_out`

where `r_in` and `r_out` are the perpendicular moment arms from pivot to force lines of action.

Ideal output travel is:

`x_out = x_in / MA`

If input-side lost motion is measured at the same input coordinate:

`x_out = (x_in - x_lost) / MA`

The force estimate with an explicitly supplied overall efficiency is:

`F_out = F_in × MA × η`

These equations apply only to the stated simple lever geometry and evaluated pose. A changing moment arm requires a position-dependent model or measured force/travel curve. Do not treat a single ratio as valid throughout a cam or compound linkage stroke without proof.

## 4. Multi-stage transmission

For a chain of ideal rigid lever stages, the screening force ratio is the product of each stage's moment-arm ratio:

`MA_total = Π(r_in,i / r_out,i)`

With explicitly supplied stage efficiencies:

`F_out,screen = F_in × MA_total × Πη_i`

Travel conversion is the inverse only for compatible ideal kinematics and must account for each stage's lost motion at the correct local coordinate. The WP-43 software computes the force-ratio screen for a chain; it deliberately does not infer total travel from a chain when intermediate lost motion and coordinate transforms have not been defined.

Efficiencies must come from measurement or a traceable engineering source. The software does not insert a default efficiency.

## 5. Force-travel work and return behavior

For measured input force `F(x)`, quasi-static work is:

`W = ∫ F(x) dx`

The executable model applies trapezoidal integration to supplied samples with strictly increasing travel. Since 1 N·mm = 0.001 J, the output is converted to joules.

Measure loading and unloading curves separately when hysteresis or return behavior matters. Do not combine them into one curve. Record:
- instrument ID and calibration;
- force sensor axis and alignment;
- travel datum and zero procedure;
- loading/unloading direction and speed;
- sampling rate and filtering;
- temperature, orientation and lubrication state;
- configuration and source revision;
- uncertainty budget and repeat count.

A measured quasi-static work value is not peak force, impact energy, dynamic actuation margin or spring fatigue qualification.

## 6. Candidate-specific requirements

### 6.1 Column-wheel candidate

Define the pusher-to-indexer stroke and force path; indexing contact; overtravel stop; jumper engagement; anti-double-step behavior; and return path. Demonstrate that a partial stroke cannot leave an unstable intermediate index or command unintended clutch/reset movement.

The pusher transmission must not rely on friction alone to establish the index state. The final indexed state and retention feature must be positively verified.

### 6.2 Cam/lever candidate

Define the pusher-to-cam/follower or cam-driving linkage, effective moment arms through the full stroke, dwell transitions, follower contact and detent behavior. Identify any point at which the mechanism can stall on a ramp or become self-locking.

Where force ratio changes with cam angle, produce a position-dependent force/travel model or instrumented prototype curve. A single constant lever ratio is not sufficient to represent a non-linear cam profile.

### 6.3 Common output commands

For each candidate, map control output travel and force requirements to:
- clutch engagement and disengagement;
- stopped-train restraint engagement and release;
- reset hammer enable, travel and withdrawal;
- positive running-state reset block;
- return springs and state retention.

No output force requirement is invented. Each receiving subsystem must provide an approved force/travel envelope or measured interface curve before a numerical pusher design can be closed.

## 7. Case and sealing interface

The external pusher must be evaluated with its case tube, guide, seals, return spring and retention method as a system. Required evidence includes:
- pusher axis and case datum;
- usable external and internal travel;
- hard-stop locations and overtravel protection;
- seal compression and friction curve from supplier or measurement;
- ingress-protection test method and case qualification;
- accidental actuation and impact considerations;
- service/removal access and replacement method.

Seal friction must be included in measured input force, not silently assigned to the internal lever. Case water resistance is not established by this mechanism study.

## 8. Tolerance, clearance and failure analysis

The geometry package must evaluate pivot position, arm lengths, contact radii, pin/slot clearance, axial stack, pusher guide alignment and hard-stop variation. Use WP-37 tolerance methods where the stack is defined; use WP-35/WP-40 envelope and motion screening where trajectories are available.

Failure modes to assess:
- pusher binding or excessive side load;
- inadequate usable stroke;
- lost motion or excessive backlash;
- overtravel or stop impact;
- pivot/support wear or looseness;
- return failure or sluggish release;
- incomplete index/cam transition;
- unintended simultaneous clutch and reset command;
- reset interlock bypass or failure;
- seal drag variation and water-ingress failure.

No tolerance or acceptance value is assigned without an approved drawing, supplier specification or test requirement.

## 9. Executable calculation model

Files:
- `tools/c01_pusher_force.py`
- `tools/test_c01_pusher_force.py`

Functions:
- simple lever force/travel screening from supplied moment arms, efficiency, force, travel and lost motion;
- multi-stage ideal force-ratio screening with explicit stage efficiencies;
- trapezoidal integration of measured force-travel data;
- geometry/provenance completeness check for pusher paths.

The model rejects non-finite or non-positive dimensions, efficiency outside (0,1], negative force/travel and non-monotonic measurement samples. It does not calculate stress, deflection, bearing loads, contact pressure, fatigue, dynamic impact or case sealing.

Run from the tools directory:

```sh
python -m unittest test_c01_pusher_force.py
```

Fixtures are synthetic arithmetic tests, not C-01 dimensions or measured force data.

## 10. Verification and acceptance criteria

| ID | Criterion | Required evidence |
|---|---|---|
| WP43-AC-01 | Complete pusher-to-command force path | Controlled member/interface register |
| WP43-AC-02 | Each lever stage has pivot, input/output contacts and evidence | Drawing and datum review |
| WP43-AC-03 | Force/travel calculations use correct perpendicular moment arms | Independent calculation review |
| WP43-AC-04 | Lost motion and hard stops are accounted for | Dimensional inspection and stroke test |
| WP43-AC-05 | Loading/unloading curves are measured separately where hysteresis exists | Calibrated force/travel report |
| WP43-AC-06 | CW indexing completes without half-index/double-step | Instrumented partial/full stroke test |
| WP43-AC-07 | CL follower/cam transitions remain controlled across stroke | Instrumented profile/force test |
| WP43-AC-08 | Clutch, retention and reset outputs meet approved interface envelopes | WP-42/WP-41 interface test |
| WP43-AC-09 | Running reset interlock cannot be bypassed by pusher travel | Physical proof test |
| WP43-AC-10 | Case pusher, guide, seals and stops are qualified as an assembly | Case qualification record |
| WP43-AC-11 | Tolerance, wear, service and independent review gates pass | WP-30/WP-32 controlled evidence |

## 11. Revision control and disposition

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial pusher force-path, lever geometry and measured force/travel engineering framework | Pending independent engineering review |

**Disposition:** WP-43 establishes calculation and verification methods for the pusher and lever system. No lever arrangement, case pusher dimension, force, spring, material, tolerance or performance limit is selected. Both WP-42 control candidates remain open. C-01 remains unfrozen and is not released for manufacture.
