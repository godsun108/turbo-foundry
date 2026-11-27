"""WP-50 traceable chronograph-control test analysis.

This module transforms supplied WP-49 observations into dashboard-ready summaries.
It does not ingest instruments, alter raw evidence, set acceptance limits, or select
an architecture. All input records remain caller-owned and provenance is carried
into every derived result.
"""
from __future__ import annotations
import math
import statistics

class AnalysisError(ValueError):
    pass

def _finite(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise AnalysisError(f"{label} must be finite numeric")
    return float(value)

def _provenance(record):
    for field in ("run_id", "candidate_id", "procedure_revision", "test_condition_id",
                  "fixture_revision", "evidence_id", "source_revision"):
        if not record.get(field):
            raise AnalysisError(f"missing provenance field: {field}")

def descriptive_statistics(values):
    if not isinstance(values, (list, tuple)) or not values:
        raise AnalysisError("at least one observation is required")
    xs = [_finite(v, "observation") for v in values]
    return {
        "count": len(xs),
        "mean": statistics.fmean(xs),
        "median": statistics.median(xs),
        "minimum": min(xs),
        "maximum": max(xs),
        "sample_standard_deviation": statistics.stdev(xs) if len(xs) > 1 else None,
        "range": max(xs) - min(xs),
    }

def expanded_uncertainty_interval(value, standard_uncertainty, coverage_factor,
                                  independent_components_confirmed):
    x = _finite(value, "value")
    u = _finite(standard_uncertainty, "standard_uncertainty")
    k = _finite(coverage_factor, "coverage_factor")
    if u < 0 or k <= 0:
        raise AnalysisError("uncertainty must be nonnegative and coverage factor positive")
    if independent_components_confirmed is not True:
        raise AnalysisError("RSS/expanded interval requires explicit independence confirmation")
    expanded = k * u
    return {"value": x, "standard_uncertainty": u, "coverage_factor": k,
            "expanded_uncertainty": expanded, "lower": x-expanded, "upper": x+expanded,
            "method": "k times supplied combined standard uncertainty; coverage interpretation is caller-defined"}

def force_travel_curve(samples, run_id, evidence_id, source_revision):
    if not isinstance(samples, list) or len(samples) < 2:
        raise AnalysisError("at least two force/travel samples are required")
    points, work_n_mm = [], 0.0
    previous_time = None
    for i, row in enumerate(samples):
        t = _finite(row.get("time_s"), f"sample[{i}].time_s")
        x = _finite(row.get("travel_mm"), f"sample[{i}].travel_mm")
        f = _finite(row.get("force_n"), f"sample[{i}].force_n")
        if f < 0:
            raise AnalysisError("force must be nonnegative")
        if previous_time is not None and t <= previous_time:
            raise AnalysisError("sample times must strictly increase")
        previous_time = t
        points.append({"time_s": t, "travel_mm": x, "force_n": f})
    for a, b in zip(points, points[1:]):
        work_n_mm += (a["force_n"] + b["force_n"]) * 0.5 * (b["travel_mm"] - a["travel_mm"])
    return {
        "run_id": run_id, "points": points,
        "peak_sampled_force_n": max(p["force_n"] for p in points),
        "travel_min_mm": min(p["travel_mm"] for p in points),
        "travel_max_mm": max(p["travel_mm"] for p in points),
        "signed_path_work_j": work_n_mm / 1000.0,
        "evidence_id": evidence_id, "source_revision": source_revision,
        "limitations": ["Signed path integral; loading and return branches are not automatically separated.",
                        "Sampled peak may miss transients; no filtering, compliance correction, or uncertainty propagation."]
    }

def event_latency_summary(values_s):
    result = descriptive_statistics(values_s)
    result["unit"] = "s"
    return result

def reset_repeatability(observations_deg, zero_datum_deg):
    if not isinstance(observations_deg, list) or not observations_deg:
        raise AnalysisError("reset observations are required")
    zero = _finite(zero_datum_deg, "zero_datum_deg")
    errors = [(((_finite(v, "reset angle") - zero + 180.0) % 360.0) - 180.0)
              for v in observations_deg]
    sx = sum(math.sin(math.radians(v)) for v in errors)
    cx = sum(math.cos(math.radians(v)) for v in errors)
    mean = math.degrees(math.atan2(sx, cx))
    return {
        "count": len(errors), "signed_errors_deg": errors,
        "circular_mean_error_deg": mean,
        "maximum_absolute_error_deg": max(abs(v) for v in errors),
        "sample_standard_deviation_deg": statistics.stdev(errors) if len(errors) > 1 else None,
        "zero_datum_deg": zero,
        "limitations": ["No zero-datum, optical-scale, alignment, hand-width, settling, or calibration uncertainty."]
    }

def state_transition_reliability(trials, z_value):
    if not isinstance(trials, list) or not trials:
        raise AnalysisError("state-transition trials are required")
    z = _finite(z_value, "z_value")
    if z <= 0:
        raise AnalysisError("z_value must be positive")
    passed = 0
    for trial in trials:
        if not isinstance(trial.get("expected_state"), str) or not isinstance(trial.get("observed_state"), str):
            raise AnalysisError("each trial needs expected_state and observed_state")
        passed += trial["expected_state"] == trial["observed_state"]
    n, p = len(trials), passed / len(trials)
    denom = 1.0 + z*z/n
    center = (p + z*z/(2*n))/denom
    half = z*math.sqrt((p*(1-p)/n) + z*z/(4*n*n))/denom
    return {"trials": n, "successful_transitions": passed, "failed_transitions": n-passed,
            "observed_success_fraction": p, "wilson_interval": [max(0.0, center-half), min(1.0, center+half)],
            "z_value": z, "interval_method": "Wilson score; confidence interpretation depends on caller-supplied z",
            "note": "A software state match is not physical proof of a running-reset interlock."}

def validate_matched_runs(run_a, run_b):
    _provenance(run_a)
    _provenance(run_b)
    fields = ("procedure_revision", "test_condition_id", "fixture_revision")
    mismatches = [field for field in fields if run_a.get(field) != run_b.get(field)]
    if run_a.get("candidate_id") == run_b.get("candidate_id"):
        mismatches.append("candidate_id must differ for a candidate comparison")
    return {"metadata_match": not mismatches, "mismatches": mismatches,
            "run_ids": [run_a["run_id"], run_b["run_id"]],
            "candidate_ids": [run_a["candidate_id"], run_b["candidate_id"]],
            "note": "Metadata match is necessary but not sufficient; review article, calibration, conditioning, assembly, operator, and other confounders."}

def analyze_run(run, z_value):
    _provenance(run)
    out = {"run_id": run["run_id"], "candidate_id": run["candidate_id"],
           "procedure_revision": run["procedure_revision"], "test_condition_id": run["test_condition_id"],
           "fixture_revision": run["fixture_revision"], "evidence_id": run["evidence_id"],
           "source_revision": run["source_revision"]}
    if run.get("force_travel_samples"):
        out["force_travel"] = force_travel_curve(run["force_travel_samples"], run["run_id"],
                                                  run["evidence_id"], run["source_revision"])
    if run.get("start_stop_latency_s"):
        out["start_stop_latency"] = event_latency_summary(run["start_stop_latency_s"])
    if run.get("reset_observations_deg"):
        out["reset_repeatability"] = reset_repeatability(run["reset_observations_deg"],
                                                          run["zero_datum_deg"])
    if run.get("state_trials"):
        out["state_reliability"] = state_transition_reliability(run["state_trials"], z_value)
    return out

def build_dashboard(run_records, z_value):
    if not isinstance(run_records, list) or not run_records:
        raise AnalysisError("at least one run record is required")
    analyzed = [analyze_run(run, z_value) for run in run_records]
    candidates = {}
    for row in analyzed:
        candidates.setdefault(row["candidate_id"], []).append(row)
    return {
        "schema": "STEWARD-C01-WP50-DASHBOARD-1",
        "run_count": len(analyzed),
        "candidate_count": len(candidates),
        "candidate_runs": candidates,
        "run_history": analyzed,
        "decision_status": "NO_ARCHITECTURE_SELECTED",
        "limitations": [
            "Dashboard values are derived only from supplied observations and provenance.",
            "No acceptance limits, weights, architecture scores, or winner are inferred.",
            "Runs are not pooled across unmatched conditions; candidate-level summaries require a separately approved analysis plan.",
            "No physical interlock, safety, fit, durability, or prototype-release conclusion is made."
        ]
    }
