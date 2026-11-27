# WP-51 — Chronograph Control Interactive Evidence Dashboard

- **Document ID:** SEB-C01-WP-51
- **Revision:** A
- **Status:** Interactive review interface — engineering validation pending
- **Project:** STEWARD C-01
- **Branch:** `steward/c-01-movement-foundation`
- **Dashboard:** `dashboard/c01-control-dashboard.html`
- **Predecessors:** WP-45 through WP-50
- **Date:** 2026-11-27

## 1. Purpose

WP-51 defines a browser-based, dependency-free review interface for the CW and CL chronograph control evidence generated under WP-46 through WP-50. The dashboard imports a user-selected JSON export, displays traceable run records and renders selected observations.

The page is a local static artifact. It does not connect to DAQ hardware, call a remote service, upload data, alter source files, or authorize engineering decisions.

## 2. User workflow

1. Complete a controlled acquisition under WP-49 and preserve its raw data and manifest.
2. Prepare a WP-50 run-record JSON array, or a WP-50 dashboard export containing a `run_history` array.
3. Open `dashboard/c01-control-dashboard.html` in a modern browser.
4. Import the JSON file using the file picker.
5. Filter by candidate (CW/CL) and run.
6. Inspect plots and traceability table. Keep each run separate unless an approved analysis plan permits pooling.
7. Export the currently filtered source records as JSON for a controlled downstream review.

The export is a filtered record package, not a signed engineering report and not a replacement for original raw data.

## 3. Input contract

Each run record requires:
- `run_id`
- `candidate_id`
- `procedure_revision`
- `test_condition_id`
- `fixture_revision`
- `evidence_id`
- `source_revision`

Optional display fields:
- `force_travel_samples`: array of `time_s`, `travel_mm`, `force_n`
- `start_stop_latency_s`: array of latency values in seconds
- `reset_observations_deg`: array of measured angles in degrees
- `zero_datum_deg`: calibrated zero reference in degrees
- `state_trials`: array of `expected_state` and `observed_state`

Import accepts either a JSON array of run records or a WP-50 export object with `run_history`. The dashboard rejects missing required provenance and invalid force/travel samples. It is a visualization adapter and does not replace the full WP-49 manifest, calibration records, synchronization evidence, raw-file hashes, instrument metadata or WP-50 analysis calculations.

## 4. Display functions

- Dataset summary: run count, candidate count and state-transition counts.
- Candidate/run filters.
- Force versus travel for a selected run.
- Start/stop latency observations for filtered runs.
- Reset error relative to the supplied zero datum.
- State-transition outcome counts by run.
- Run history with procedure, test condition, fixture, evidence and source identifiers.
- Export of filtered source records.

Charts display imported observations, not invented demonstration data. A blank chart indicates that the selected records do not contain the required field.

## 5. Data integrity and security

- Source JSON is read locally through the browser file picker.
- No network request, telemetry, remote storage or upload function is implemented.
- Imported data remains in page memory for the active session; clearing or closing the page discards it.
- The dashboard does not modify the selected source file.
- Export creates a separate JSON file containing the filtered run records.
- The interface uses text escaping for imported metadata before placing it into the page.
- Raw evidence, native acquisition files and their hashes remain controlled under WP-49.

Do not import sensitive personal information or unapproved confidential data into an unmanaged browser environment. Follow the project's data retention and access controls.

## 6. Engineering limitations

The page does not independently calculate the full WP-50 statistical package. It provides visual inspection and simple display counts; controlled derived calculations remain in `tools/c01_control_analysis.py`. In particular:
- The force/travel plot shows imported samples; it does not infer hysteresis loss, filter transients or correct compliance.
- Latency chart points are individual observations; they are not an acceptance verdict.
- Reset error visualization wraps angle relative to the supplied zero; uncertainty propagation is not performed in the page.
- State charts show expected/observed label matches; they do not prove physical mechanism behavior or running-reset interlock.
- Metadata display is not a complete experimental comparability review.
- No architecture scoring, ranking, recommendation, winner selection, design freeze or prototype release is implemented.

## 7. Acceptance criteria

- Page opens without a build step or third-party dependency.
- JSON array and WP-50 `run_history` import forms are recognized.
- Missing provenance and malformed force/travel samples are rejected with a visible message.
- Candidate and run filters update all panels.
- Charts use imported values and identify engineering units.
- Empty fields produce an explicit empty state, not synthetic content.
- Run history preserves all required provenance identifiers.
- Filtered export contains only the selected source records and retains a neutral decision status.
- No network request, instrument command or automatic architecture decision is present.

## 8. Verification status

This work package was committed and read back from GitHub. Browser execution, cross-browser compatibility, accessibility audit, large-file behavior and human-factors validation remain to be performed. No test results are claimed by this document.

## 9. Revision history

| Revision | Date | Description | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial local interactive dashboard and controlled interface definition | Pending review |

## 10. Release boundary

WP-51 is an engineering review interface only. It does not authorize prototype construction, physical testing, selection of CW or CL, selection of vertical or horizontal clutch architecture, movement design freeze, or production release. The dashboard must continue to display **NO ARCHITECTURE SELECTED** until the WP-45 decision gates and formal design-authority approval are satisfied.
