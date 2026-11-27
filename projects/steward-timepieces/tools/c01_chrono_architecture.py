"""WP-33 chronograph trade-study and functional sequence validators."""
from __future__ import annotations
from fractions import Fraction
from typing import Any

CANDIDATES = {"A": ("vertical", "column_wheel"),
              "B": ("vertical", "cam_lever"),
              "C": ("horizontal", "column_wheel"),
              "D": ("horizontal", "cam_lever")}
REQUIRED_CRITERIA = {"start_disturbance", "running_energy", "packaging",
                     "state_reliability", "reset_repeatability",
                     "wear_life", "serviceability", "manufacturability"}

def _required(r: dict[str, Any], fields: tuple[str, ...], label: str) -> None:
    for f in fields:
        if f not in r or r[f] is None or (isinstance(r[f], str) and not r[f].strip()):
            raise ValueError(f"{label}.{f} is required")

def validate_candidates(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(rows, list) or len(rows) != 4:
        raise ValueError("exactly four declared architecture combinations are required")
    ids = [r.get("candidate_id") for r in rows]
    if set(ids) != set(CANDIDATES) or len(set(ids)) != 4:
        raise ValueError("candidate IDs must be A, B, C and D exactly once")
    for r in rows:
        _required(r, ("clutch", "control", "status", "evidence_register_id"), r["candidate_id"])
        expected = CANDIDATES[r["candidate_id"]]
        if (r["clutch"], r["control"]) != expected:
            raise ValueError(f"candidate {r['candidate_id']} does not match controlled definition")
        if r["status"] not in ("candidate", "selected_for_prototype", "rejected", "deferred"):
            raise ValueError("invalid candidate status")
    return {"candidate_count": 4, "winner_selected": False,
            "candidate_ids": sorted(ids)}

def evaluate_trade_study(criteria: list[dict[str, Any]],
                         scores: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("criteria must be non-empty")
    names = [c.get("criterion_id") for c in criteria]
    if len(set(names)) != len(names) or set(names) != REQUIRED_CRITERIA:
        raise ValueError("criteria must cover the required set exactly once")
    weights: dict[str, Fraction] = {}
    for c in criteria:
        _required(c, ("weight", "definition", "approval_record_id"), c["criterion_id"])
        try:
            weights[c["criterion_id"]] = Fraction(str(c["weight"]))
        except (ValueError, ZeroDivisionError):
            raise ValueError("criterion weights must be rational numbers")
        if weights[c["criterion_id"]] < 0:
            raise ValueError("criterion weights cannot be negative")
        if not c["approval_record_id"].strip():
            raise ValueError("each criterion requires approval evidence")
    if sum(weights.values(), Fraction(0)) != 1:
        raise ValueError("approved criterion weights must sum exactly to 1")
    if not isinstance(scores, list) or len(scores) != 4:
        raise ValueError("scores must contain all four candidates")
    candidate_ids = [s.get("candidate_id") for s in scores]
    if set(candidate_ids) != set(CANDIDATES) or len(set(candidate_ids)) != 4:
        raise ValueError("scores must cover candidates A-D exactly once")
    totals = {}
    for row in scores:
        _required(row, ("criterion_scores", "evidence_ids", "review_status"), row["candidate_id"])
        if row["review_status"] != "approved":
            raise ValueError("all candidate score rows require approved review")
        values = row["criterion_scores"]
        evidence = row["evidence_ids"]
        if set(values) != REQUIRED_CRITERIA or set(evidence) != REQUIRED_CRITERIA:
            raise ValueError("each criterion requires one score and one evidence ID")
        total = Fraction(0)
        for key, weight in weights.items():
            score = values[key]
            if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 5:
                raise ValueError("scores must be integers from 1 through 5")
            if not isinstance(evidence[key], str) or not evidence[key].strip():
                raise ValueError("each score requires traceable evidence")
            total += weight * score
        totals[row["candidate_id"]] = total
    ranked = sorted(totals, key=lambda key: (-totals[key], key))
    tie = len(ranked) > 1 and totals[ranked[0]] == totals[ranked[1]]
    return {"scores": {k: str(v) for k, v in totals.items()},
            "provisional_ranking": ranked, "top_score_tie": tie,
            "decision_authorized": False,
            "note": "Scoring is advisory; design authority approval and prototype verification remain mandatory."}

def validate_state_transition(current: str, command: str, result: str,
                              physical_interlock_evidence: str | None = None) -> dict[str, Any]:
    allowed = {("stopped_zero", "start"): "running",
               ("running", "stop"): "stopped_retained",
               ("stopped_retained", "start"): "running",
               ("stopped_retained", "reset"): "stopped_zero"}
    if current == "running" and command == "reset":
        if physical_interlock_evidence is None or not physical_interlock_evidence.strip():
            raise ValueError("reset-while-running rejection requires physical interlock evidence")
        if result != "running":
            raise ValueError("reset command while running must leave the chronograph running")
        return {"accepted": True, "state": "running", "reset_blocked": True}
    expected = allowed.get((current, command))
    if expected is None or result != expected:
        raise ValueError("invalid chronograph state transition")
    return {"accepted": True, "state": result, "reset_blocked": False}

def validate_measurement_plan(plan: dict[str, Any]) -> dict[str, Any]:
    _required(plan, ("plan_id", "candidate_id", "test_condition",
        "measurement_boundary", "instrument_ids", "sampling_method",
        "acceptance_reference", "procedure_revision", "review_status"), "measurement_plan")
    if plan["candidate_id"] not in CANDIDATES:
        raise ValueError("unknown candidate")
    required = ("start_hand_jump", "steady_running_load", "off_state_drag",
        "pusher_force_travel", "reset_zero_error", "repeat_cycle_reliability",
        "wear_inspection", "assembly_service_time", "base_rate_delta")
    measurements = plan.get("measurements")
    if not isinstance(measurements, list) or set(measurements) != set(required):
        raise ValueError("measurement plan must cover all required measurements exactly")
    if plan["review_status"] not in ("draft", "approved"):
        raise ValueError("invalid review status")
    return {"plan_id": plan["plan_id"], "measurement_count": len(measurements),
            "approved": plan["review_status"] == "approved"}

