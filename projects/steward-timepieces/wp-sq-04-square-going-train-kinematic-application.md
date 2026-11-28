# WP-SQ-04 — Square C-01 Going-Train Kinematic Application

- **Document ID:** SEB-C01-WP-SQ-04
- **Revision:** 0.1
- **Status:** Application-layer definition; no C-01 train selected
- **Branch:** `steward/c-01-movement-foundation`
- **Dependencies:** WP-SQ-03, WP-18, WP-25, WP-26, WP-38 and WP-39
- **Software:** `tools/c01_square_train_application.py`
- **Verification:** `tools/test_c01_square_train_application.py`

## 1. Purpose

WP-SQ-04 applies the existing engineering toolchain to the square C-01 going-train hypothesis. It deliberately does **not** create another tooth-count generator or kinematic solver.

WP-18 already supplies bounded integer tooth synthesis. WP-25 already calculates exact-rational arbor/gear/mesh path ratios, direction and output speed. WP-26 integrates candidate meshes with shared-gear consistency and structural/CAD handoff. WP-38 performs limited involute geometry screening. WP-39 ranks bounded ordered gear-train candidates. This package connects that existing capability to the square-core functional path and enforces candidate provenance.

## 2. Functional path

The WP-SQ-03 hypothesis is:

`barrel → center → third → fourth/seconds → escape wheel`

Pallet fork and balance are regulator interactions, not downstream gear arbors. The sequence is a functional hypothesis only. SQ-A remains a working study configuration; SQ-B and SQ-C remain open. No physical coordinates, dimensions, center distances or component positions are inferred.

## 3. Application method

The adapter accepts explicit arbor, gear and mesh registers and delegates all ideal kinematic calculations to WP-25. It requires the declared path to map the exact WP-SQ-03 functional order. It checks that every arbor, gear and mesh carries the candidate's declared evidence class and source revision, preventing accidental mixing of unrelated evidence.

For each mesh, WP-25 applies the signed ideal relationship:
- external mesh: (R_i=-z_{driver}/z_{driven})
- internal mesh: (R_i=+z_{driver}/z_{driven})

For the complete path, (R_{total}=prod_i R_i) and (n_{out}=n_{in}R_{total}). Target speed for a display period (T) is (60/T) rpm. The application reports fractional speed error but does not apply an acceptance tolerance.

## 4. Required inputs

Candidate ID, evidence class, source revision, arbor register, gear register with explicit positive integer tooth counts, mesh register with explicit mesh types, ordered functional arbor path, input RPM and target output period are mandatory. No values are defaulted.

## 5. Acceptance criteria

| ID | Criterion | Evidence |
|---|---|---|
| SQ04-AC-01 | Path matches WP-SQ-03 barrel-center-third-fourth-escape hypothesis | Input validation |
| SQ04-AC-02 | Arbor, gear and mesh references resolve | WP-25 validation |
| SQ04-AC-03 | Tooth counts and mesh types are explicit | WP-25 validation |
| SQ04-AC-04 | Input RPM and target period are explicit | Input validation |
| SQ04-AC-05 | Exact ratio, direction and output RPM are reported | WP-25 calculation |
| SQ04-AC-06 | Evidence and revision are consistent across candidate | Provenance validation |
| SQ04-AC-07 | No tolerance is applied without approved requirement | Output review |
| SQ04-AC-08 | No physical-fit or performance claim is inferred | Engineering review |

## 6. Verification

Run from `projects/steward-timepieces/tools`:

```sh
python -m unittest test_c01_square_train_application.py
```

Five regression tests use deliberately synthetic tooth counts, mesh records and input speed. They check exact-ratio delegation, path rejection, missing input, provenance mismatch and non-selection safeguards. These fixtures are **not C-01 design data**. Tests are authored but have not been executed.

## 7. Limitations and next evidence

This application establishes ideal kinematics only. It does not establish barrel speed/torque over wind state, actual escapement event convention, gear module/tooth form/profile shift, center-distance tolerance, undercut/contact ratio/interference/strength, bearing loads, lubrication/efficiency, gear inertia, chronograph disturbance, physical fit, rate, amplitude or reserve. The 60–70 hour reserve aspiration remains unverified.

The next meaningful design inputs are a measured/approved barrel speed profile, selected train topology, tooth-system constraints, plate/bridge datums and an approved output error budget. Candidate schedules can then be evaluated through WP-26/WP-38/WP-39 and independently reviewed.

## 8. Revision control

| Revision | Change | Disposition |
|---|---|---|
| 0.1 | Square-core kinematic application layer reusing WP-25 with provenance contract and synthetic regression fixtures | Preliminary; review required |

**Disposition:** No train, tooth schedule, gear system or physical architecture is selected. No design freeze, manufacture, merge or deployment is authorized.
