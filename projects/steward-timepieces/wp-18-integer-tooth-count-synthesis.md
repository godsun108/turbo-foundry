# STEWARD C-01 — WP-18 Integer Tooth-Count Synthesis

**Document ID:** C01-WP-18  
**Revision:** 0.1  
**Status:** Bounded mathematical candidate generator; no physical gear design selected  
**Branch:** `steward/c-01-movement-foundation`  
**Predecessors:** WP-10 Gear Train; WP-15 Gear-Train Topology; WP-17 Chronograph Kinematics  
**Next gate:** approved source speed, target output, watch-scale tooth-form constraints, movement envelope and reviewed CAD candidates

## 1. Purpose

WP-18 adds a reproducible search tool for integer tooth-count combinations that approximate a required chronograph speed ratio. It is the first synthesis step between WP-17's target kinematics and a future physical gear-train design.

The search is intentionally bounded and transparent. It enumerates external spur-gear pairs and one- or two-stage compound paths using only user-supplied search bounds. It does not choose C-01 tooth counts or certify any candidate as buildable.

## 2. Inputs and assumptions

Required inputs:
- target speed-ratio magnitude;
- minimum and maximum tooth count;
- minimum and maximum allowed stage-ratio magnitude;
- maximum permitted fractional ratio error;
- maximum number of results.

Optional input:
- module in millimetres, used only to calculate a preliminary external-gear pitch-center distance.

No default search bounds are silently applied. The caller must supply every search constraint.

### Mathematical assumptions
- Each stage is a simple external spur-gear mesh.
- Gear tooth counts are positive integers.
- Each stage ratio magnitude is driver teeth divided by driven teeth.
- Each external mesh reverses rotation direction.
- Two-stage compound paths represent the driven wheel of stage one and driver wheel of stage two as rigidly coupled on a common intermediate arbor.
- A supplied module applies to both gears within each mesh pair.
- Stage ratios multiply to produce the compound path ratio.

The current model does not synthesize internal gears, bevel gears, noncircular gears, idlers with independent placement, or more than two meshes.

## 3. Governing equations

For an external gear pair:

[
\left|\frac{n_{out}}{n_{in}}\right|=\frac{z_{driver}}{z_{driven}}
]

and the output direction reverses.

For a two-stage compound path:

[
|R_{total}|=\frac{z_1}{z_2}\times\frac{z_3}{z_4}
]

The intermediate wheels (z_2) and (z_3) must be rigidly coupled on the same arbor for this compound relationship to apply.

For target ratio (R_t) and candidate ratio (R_c), fractional absolute error is:

[
e=\frac{|R_c-R_t|}{R_t}
]

A candidate is retained only if (e) is no greater than the explicitly supplied maximum error.

If a common module (m) is supplied, the preliminary pitch-center distance for one external pair is:

[
a=\frac{m(z_{driver}+z_{driven})}{2}
]

This is not a center-distance tolerance or a complete geometry calculation. It assumes compatible module and standard pitch geometry; it says nothing about addendum modification, backlash, profile shift, tooth form or interference.

## 4. Search method

The calculator:
1. validates all explicit bounds;
2. enumerates all external driver/driven pairs inside the tooth-count and stage-ratio limits;
3. evaluates each pair as a one-stage candidate;
4. sorts pair ratios exactly using rational arithmetic;
5. for each first stage, searches nearby second-stage ratios around the ideal residual ratio;
6. retains only candidates inside the supplied fractional-error limit;
7. ranks by exact ratio error, then fewer stages, then deterministic tooth-count ordering;
8. returns no more than the requested result count.

The search is deterministic. It does not use floating-point ranking for the tooth ratio.

## 5. Direction and compound-shaft control

Every external mesh reverses direction. A single-stage candidate therefore rotates opposite to its input; a two-stage candidate rotates in the same direction as its input.

The intermediate compound arbor assumption must be represented in a future train diagram and checked against the actual plate/bridge layout. This mathematical search does not determine whether the wheels can physically share an arbor or whether their axes can be positioned at valid center distances.

## 6. Executable model

Files:
- `tools/c01_tooth_synthesis.py`
- `tools/test_c01_tooth_synthesis.py`

The model returns exact rational ratios and errors, stage tooth counts, direction, optional preliminary pitch-center distance, search bounds, candidate count and explicit limitations.

### Verification command

From `projects/steward-timepieces/tools`:

```bash
python -m unittest test_c01_tooth_synthesis.py
```

Tests use synthetic tooth counts and search ranges to verify arithmetic and validation. They are test fixtures only, not proposed C-01 wheel or pinion sizes.

## 7. Acceptance criteria

| ID | Criterion | Evidence |
|---|---|---|
| WP18-SYN-01 | All tooth counts are positive integers within supplied bounds | Unit tests and input audit |
| WP18-SYN-02 | Stage ratios are exact rational values | Fraction-based tests |
| WP18-SYN-03 | Compound ratio equals product of stage ratios | Two-stage unit test |
| WP18-SYN-04 | Direction is correct for odd/even external mesh count | Direction tests |
| WP18-SYN-05 | Candidate error is within the explicit user-supplied tolerance | Filter tests |
| WP18-SYN-06 | Optional pitch-center distance uses supplied module and tooth counts | Formula test |
| WP18-SYN-07 | No physical feasibility claim is inferred from ratio fit | Document/model review |
| WP18-SYN-08 | Search bounds and all candidate assumptions are returned with results | Output schema review |

## 8. Engineering limitations and required downstream checks

A mathematical candidate is not a gear design. Before any candidate can be promoted, engineering must establish:
- escapement/chronograph source speed and torque;
- actual gear type, tooth form, module, pressure angle and profile;
- minimum pinion tooth count and undercut/interference assessment;
- contact ratio, tooth strength, wear and lubrication;
- backlash, endshake, pivot and bearing requirements;
- exact center distances and tolerance stack;
- plate/bridge and adjacent-component clearance;
- common-arbor feasibility and assembly sequence;
- hand/register direction and zero alignment;
- mesh efficiency, clutch drag and indexing transients;
- service access, replaceability and inspection criteria;
- prototype test results under relevant temperature and orientation conditions.

No generic minimum tooth count is declared safe for C-01. Minimum tooth count is a search input that must be approved by the gear-design engineer based on the selected tooth system.

## 9. Revision control

| Revision | Date | Change | Status |
|---|---|---|---|
| 0.1 | 2026-11-26 | Initial integer tooth-count candidate generator, unit tests, equations, acceptance criteria and downstream checks | Preliminary; review required |

## 10. Current decision status

- Search framework: **defined**.
- Integer candidate generation: **implemented for one- and two-stage external meshes**.
- C-01 target ratio per train path: **requires approved source speed and output target**.
- Tooth-count bounds: **must be explicitly supplied**.
- Module: **not selected**.
- Tooth form and pressure angle: **not selected**.
- Center distances: **not established**.
- Undercut, strength, wear and interference: **not evaluated**.
- Candidate gear train: **not selected**.
- CAD and prototype: **not created**.

---
**Engineering integrity statement:** WP-18 is a bounded mathematical search aid. It is not a physical gear design, watch-scale feasibility proof, dimensioned drawing, CAD model, manufacturing specification or validated movement.
