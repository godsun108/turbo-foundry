"""Evidence-gated STEWARD C-01 chronograph architecture trade evaluator.

Scores and weights must be supplied by an approved review team. This module
never assigns a preferred architecture or supplies design scores by default.
Synthetic unit-test fixtures are not C-01 design evidence.
"""
from __future__ import annotations
from math import isfinite
from typing import Any


def _number(value: Any, label: str, *, low: float | None = None,
            high: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    result = float(value)
    if low is not None and result < low:
        raise ValueError(f"{label} must be >= {low}")
    if high is not None and result > high:
        raise ValueError(f"{label} must be <= {high}")
    return result


def evaluate_trade(criteria: list[dict[str, Any]],
                   candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate weighted totals only for fully evidenced, complete candidates.

    Criterion fields: id, weight (0..1), source, acceptance_basis.
    Candidate fields: id, scores mapping criterion id -> integer/float 1..5,
    evidence mapping criterion id -> non-empty source description.
    Scores are reviewer judgements, not measured performance unless the
    evidence record explicitly identifies the measurement and test revision.
    """
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("criteria must be a non-empty list")
    if not isinstance(candidates, list) or len(candidates) < 2:
        raise ValueError("at least two candidates are required for comparison")
    ids: set[str] = set()
    total_weight = 0.0
    for item in criteria:
        if not isinstance(item, dict):
            raise ValueError("each criterion must be an object")
        cid = item.get("id")
        if not isinstance(cid, str) or not cid.strip() or cid in ids:
            raise ValueError("criterion IDs must be unique non-empty strings")
        ids.add(cid)
        weight = _number(item.get("weight"), f"{cid}.weight", low=0, high=1)
        if not isinstance(item.get("source"), str) or not item["source"].strip():
            raise ValueError(f"{cid} requires a traceable source")
        if not isinstance(item.get("acceptance_basis"), str) or not item["acceptance_basis"].strip():
            raise ValueError(f"{cid} requires an acceptance basis")
        total_weight += weight
    if abs(total_weight - 1.0) > 1e-9:
        raise ValueError("criterion weights must sum to 1.0")

    candidate_ids: set[str] = set()
    results = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("each candidate must be an object")
        candidate_id = candidate.get("id")
        if not isinstance(candidate_id, str) or not candidate_id.strip() or candidate_id in candidate_ids:
            raise ValueError("candidate IDs must be unique non-empty strings")
        candidate_ids.add(candidate_id)
        scores, evidence = candidate.get("scores"), candidate.get("evidence")
        if not isinstance(scores, dict) or not isinstance(evidence, dict):
            raise ValueError(f"{candidate_id} requires scores and evidence mappings")
        missing = ids - set(scores)
        if missing:
            raise ValueError(f"{candidate_id} missing scores: {', '.join(sorted(missing))}")
        extra = set(scores) - ids
        if extra:
            raise ValueError(f"{candidate_id} has unknown scores: {', '.join(sorted(extra))}")
        total = 0.0
        for criterion in criteria:
            cid = criterion["id"]
            score = _number(scores[cid], f"{candidate_id}.{cid}", low=1, high=5)
            if not isinstance(evidence.get(cid), str) or not evidence[cid].strip():
                raise ValueError(f"{candidate_id}.{cid} requires evidence")
            total += score * float(criterion["weight"])
        results.append({"candidate_id": candidate_id, "weighted_score": total})
    results.sort(key=lambda row: (-row["weighted_score"], row["candidate_id"]))
    return {
        "results": results,
        "ranking_is_provisional": True,
        "approval_required": True,
        "note": "Weighted score is a decision aid, not proof of technical suitability.",
    }
