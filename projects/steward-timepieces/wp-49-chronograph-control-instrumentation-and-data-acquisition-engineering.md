# WP-49 — Chronograph Control Instrumentation and Data Acquisition Engineering

- **Document ID:** SEB-C01-WP-49
- **Revision:** A — initial controlled issue
- **Status:** Measurement architecture and analysis framework; no instruments selected or measurements claimed
- **Project:** STEWARD C-01
- **Branch:** steward/c-01-movement-foundation
- **Software:** tools/c01_data_acquisition.py
- **Synthetic regression tests:** tools/test_c01_data_acquisition.py
- **Predecessors:** WP-30, WP-43, WP-46, WP-47 and WP-48

## 1. Purpose and boundary

WP-49 defines the traceable measurement chain and data-handling architecture for comparative testing of the unresolved column-wheel (CW) and cam/lever (CL) chronograph-control candidates. It converts WP-46 measurement requirements into a channel register, synchronized acquisition contract, raw-data schema, analysis functions and comparison controls.

No instrument model, sampling rate, bandwidth, force/travel range, acceptance limit, measured performance or candidate winner is selected. Numeric examples in software tests are synthetic. This package does not authorize hardware operation or prototype release.

## 2. Measurement objectives and channels

The final channel set is driven by the approved procedure and fastest event that must be resolved. Candidate channels include:

| Channel | Measurand | Unit | Purpose |
|---|---|---|---|
| Pusher force | Axial input force | N | Force/travel curve and actuation effort |
| Pusher travel | Actual stem/contact displacement | mm | Stroke, lost motion and return |
| Control-member position | Angular or linear position | deg or mm | Indexing and state motion |
| Clutch state/position | Position or discrete state | Defined by sensor | Engagement and disengagement |
| Chronograph output | Angular position/speed | deg, rev/min | Start/stop behavior |
| Reset/heart position | Angular position | deg | Reset-to-zero error |
| Event markers | Event timestamp/state | s / defined code | Latency and sequence |
| Temperature | Local ambient/component temperature | °C | Test-condition and drift context |

Each channel must identify sensor, instrument asset, calibration record, measurand, unit, physical location, axis/direction, range, resolution, bandwidth, sample method, calibration status, uncertainty, evidence ID and source revision. This is a candidate channel dictionary, not a declaration that every channel is required or installed.

## 3. Acquisition architecture

### 3.1 Measurement boundaries

The force channel must be in series with the approved pusher load path. The travel channel must measure actual stem/contact displacement relative to a stable fixture datum, independently of actuator command. Optical or encoder channels must observe mechanism motion without introducing material inertia, friction or contact.

Every channel must be related to the WP-47 fixture datum frame. The transform to movement coordinates must be revision-controlled and traceable to the applicable carrier configuration. WP-21 M0 and the WP-14/WP-20 movement XY convention remain separate from fixture datums.

### 3.2 Timebase and synchronization

Preferred architecture is simultaneous acquisition on a shared traceable clock. If independent instruments are used, determine offset and drift against a common reference before and after each run, or at a justified interval. Store raw timestamps unchanged. Store correction coefficients and evidence separately; apply corrections only to derived analysis copies.

For measured offset b and linear drift d relative to reference time:

\[
t_{\mathrm{corrected}} = t_{\mathrm{instrument}} + b + d\,t_{\mathrm{instrument}}
\]

This first-order clock model is not adequate where drift is nonlinear, discontinuous, temperature-dependent or affected by dropped samples. Such cases require a richer synchronization model and evidence.

Sampling must be justified from event duration, sensor bandwidth, anti-alias filtering, required timing uncertainty and transient content. WP-49 assigns no sample rate or filter. Preserve native acquisition rate and filter metadata. Do not upsample raw evidence or treat interpolation as new measured information.

### 3.3 Channel acquisition and integrity

For every channel, record run ID, channel ID, instrument/sensor asset and calibration reference, units, scale, polarity, zero and range, sample rate or event-driven method, timestamp source, filtering, firmware, raw file name/hash/archive location, evidence/source revision, operator, and dropped/clipped/saturated/invalid sample flags.

Native raw files are preserved unchanged. Derived files and analysis outputs receive separate IDs and software revisions. Filtering, resampling, offset correction or event annotation must be reproducible from the raw source and declared transformation settings.

## 4. Required synchronized observations

Collect applicable synchronized signals:
1. Pusher input force and actual travel.
2. Input onset/release and actuator command as separate channels.
3. Control-member/indexing motion.
4. Clutch command and physical engagement observation.
5. Stopped-retention behavior.
6. Chronograph seconds output.
7. Reset hammer/heart-cam motion and final indication.
8. Environmental conditions and operator event markers.

A logical state label is not a substitute for physical observation. Software event markers must be distinguished from sensor-detected events. Running-reset interlock remains a physical verification governed by WP-46; DAQ analysis cannot prove it safe.

## 5. Data schema and run identity

A run manifest must identify run and candidate IDs/revisions; movement article and fixture/carrier IDs/revisions; procedure and measurement-method revisions; test-condition ID; operator/date/time/environment; channel definitions and instrument/calibration records; raw data locations and hashes; synchronization evidence; deviations and prior cycle history; evidence ID and source revision.

The software manifest validator checks required metadata, channel identity, instrument/calibration references, current calibration status, sample method and provenance. It does not verify calibration certificates or instrument suitability.

Raw observations use monotonically increasing timestamps and numeric values with declared units in the channel manifest. Missing, clipped, saturated or dropped samples must be flagged and dispositioned; do not silently interpolate missing evidence.

## 6. Derived calculations

### 6.1 Force/travel characterization

For synchronized samples (x_i,F_i,t_i), derive peak sampled force, travel range and signed work by trapezoidal integration in acquisition order:

\[
W = \sum_i \frac{F_i+F_{i+1}}{2}(x_{i+1}-x_i)
\]

Convert N·mm to joules by dividing by 1000. Because travel may reverse during return, this is signed path work, not automatically dissipated hysteresis energy. Separate loading and return branches using a controlled segmentation rule before calculating loop area. Peak sampled force may miss a transient peak.

The implementation reports signed force-travel work and sampled peak only. It does not filter, correct compliance, estimate uncertainty or segment loading/return.

### 6.2 Timing and event latency

For two uniquely identified events on a corrected common timebase:

\[
\Delta t = t_{\mathrm{target}} - t_{\mathrm{source}}
\]

Report event-detection method, threshold/algorithm revision, timestamp uncertainty and synchronization uncertainty. The software calculates latency after event IDs are supplied; it does not detect events automatically or establish a valid shared timebase.

### 6.3 Reset-to-zero error

For measured angle theta_m and calibrated zero datum theta_0, signed wrapped angular error is:

\[
e_\theta = ((\theta_m-\theta_0+180^\circ)\bmod 360^\circ)-180^\circ
\]

Report every reset observation, signed error, circular mean and uncertainty. The code handles angular wrap and computes a circular mean. It does not establish the zero datum or include optical scale, alignment, parallax, hand width, backlash, settling or calibration uncertainty.

### 6.4 Resampling and interpolation

Interpolation may be used only for derived comparisons within the measured time range and must preserve original samples. Extrapolation is prohibited. Interpolation cannot recover bandwidth or transient detail absent from source acquisition. The helper implements linear interpolation at caller-supplied times and rejects extrapolation.

## 7. CW/CL comparability

A valid comparison requires matched procedure and measurement-method revision; test-condition definition; fixture/revision; movement/article baseline or documented confounder; sensor configuration and calibration state; sampling, filtering and synchronization method; assembly, lubrication, conditioning and cycle history; analysis software and decision rule.

The software comparison helper checks a limited set of declared metadata fields only. Passing metadata is not proof of experimental equivalence. Independent review must address confounders before attributing differences to control architecture.

## 8. Uncertainty and acceptance

Apply WP-48 uncertainty principles. Include channel-specific calibration, repeatability, resolution, dynamic response, synchronization, event detection, alignment, compliance, image scale and processing contributions as applicable. Correlation between channels and shared timebase errors must be treated explicitly; independent RSS must not be used without justification.

Acceptance limits, sample plans, confidence methods and guard bands are approved requirements, not software defaults. Preserve raw traces and report excluded samples with reasons. Indeterminate results remain indeterminate pending approved disposition.

## 9. Data integrity, security and retention

- Preserve native instrument output unchanged and read-only after ingestion.
- Compute and store a cryptographic hash for each native file using an approved archive workflow.
- Store derived data separately with source-file hash, transformation settings and code revision.
- Use UTC timestamps plus explicit timebase identity; retain local time only as supplemental metadata.
- Record software/runtime versions, dependencies, operator actions and review signatures.
- Maintain backup, access control, retention and audit-trail requirements under the project's controlled data policy.
- Never overwrite raw acquisition to correct metadata; issue a versioned correction record.

## 10. Verification and acceptance criteria

The synthetic regression suite checks manifest completeness, calibration-state gating, monotonic timestamps, clock offset/drift correction, bounded interpolation, force-travel integration, angular wrap, reset circular mean, event latency and candidate-comparison metadata.

Physical acceptance requires approved instrument selection and calibration, verified synchronization, characterized bandwidth and compliance, complete raw-data preservation, traceable analysis, uncertainty appropriate to the decision and independent review. No numeric limit is invented here.

## 11. Software execution

From the tools directory, run:

    python -m unittest test_c01_data_acquisition.py

All regression inputs are synthetic, not C-01 measurements or approved instrument settings. Software validation does not authorize physical testing.

## 12. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial instrumentation, synchronization, raw-data and comparative-analysis framework | Pending engineering review |

**Release statement:** WP-49 defines how future chronograph-control evidence is acquired and analyzed. It does not select instruments, demonstrate measurement capability, establish a CW/CL winner, freeze C-01, or authorize prototype construction or physical operation.
