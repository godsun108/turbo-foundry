"""Measurement-driven STEWARD C-01 balance/escapement evaluation.

This is a reduction and acceptance-check tool, not a virtual watch.
All measured values and all project-specific acceptance limits are supplied
by the test record. No amplitude, beat-error, rate, or energy limits are
invented here.
"""
from __future__ import annotations

from math import isfinite, pi, sqrt
from typing import Any


def _finite(value: Any, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: Any, name: str) -> float:
    result = _finite(value, name)
    if result <= 0:
        raise ValueError(f"{name} must be positive")
    return result


def balance_frequency_from_inertia_and_stiffness(
    balance_inertia_kg_m2: float,
    hairspring_torsional_stiffness_n_m_per_rad: float,
) -> dict[str, float]:
    """Ideal small-angle oscillator estimate; excludes escapement effects.

    omega_0 = sqrt(kappa / I); f_0 = omega_0 / (2*pi).
    Both inputs must be measured or supplier-confirmed at stated conditions.
    """
    inertia = _positive(balance_inertia_kg_m2, "balance_inertia_kg_m2")
    stiffness = _positive(
        hairspring_torsional_stiffness_n_m_per_rad,
        "hairspring_torsional_stiffness_n_m_per_rad",
    )
    omega = sqrt(stiffness / inertia)
    frequency = omega / (2.0 * pi)
    return {
        "ideal_angular_natural_frequency_rad_s": omega,
        "ideal_natural_frequency_hz": frequency,
        "ideal_full_period_s": 1.0 / frequency,
        "ideal_half_period_s": 0.5 / frequency,
    }


def evaluate_timing_trial(data: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a measured trial against explicit, supplied acceptance limits.

    Required measurements:
      frequency_hz, rate_s_per_day, amplitude_deg, beat_error_ms,
      positional_rate_spread_s_per_day, chronograph_off_rate_s_per_day,
      chronograph_on_rate_s_per_day.

    Required approved limits:
      frequency_target_hz, frequency_tolerance_hz,
      rate_min_s_per_day, rate_max_s_per_day,
      amplitude_min_deg, amplitude_max_deg,
      beat_error_max_ms, positional_rate_spread_max_s_per_day,
      chronograph_rate_delta_max_s_per_day.

    Rate is checked for the selected test state. Chronograph-on/off interaction
    is evaluated separately as the absolute difference between measured rates.
    Limits must be approved for the relevant test method and movement revision.
    """
    measured_fields = (
        "frequency_hz", "rate_s_per_day", "amplitude_deg", "beat_error_ms",
        "positional_rate_spread_s_per_day", "chronograph_off_rate_s_per_day",
        "chronograph_on_rate_s_per_day",
    )
    limit_fields = (
        "frequency_target_hz", "frequency_tolerance_hz",
        "rate_min_s_per_day", "rate_max_s_per_day",
        "amplitude_min_deg", "amplitude_max_deg",
        "beat_error_max_ms", "positional_rate_spread_max_s_per_day",
        "chronograph_rate_delta_max_s_per_day",
    )
    missing = [key for key in measured_fields + limit_fields if key not in data]
    if missing:
        raise ValueError("missing required fields: " + ", ".join(missing))

    m = {key: _finite(data[key], key) for key in measured_fields}
    lim = {key: _finite(data[key], key) for key in limit_fields}

    for key in (
        "frequency_hz", "frequency_target_hz", "frequency_tolerance_hz",
        "amplitude_deg", "amplitude_min_deg", "amplitude_max_deg",
        "beat_error_ms", "beat_error_max_ms",
        "positional_rate_spread_s_per_day",
        "positional_rate_spread_max_s_per_day",
        "chronograph_rate_delta_max_s_per_day",
    ):
        if lim.get(key, m.get(key, 0.0)) < 0:
            raise ValueError(f"{key} must be non-negative")
    if m["frequency_hz"] <= 0 or lim["frequency_target_hz"] <= 0:
        raise ValueError("frequency values must be positive")
    if lim["frequency_tolerance_hz"] <= 0:
        raise ValueError("frequency_tolerance_hz must be positive")
    if lim["rate_min_s_per_day"] > lim["rate_max_s_per_day"]:
        raise ValueError("rate_min_s_per_day cannot exceed rate_max_s_per_day")
    if lim["amplitude_min_deg"] > lim["amplitude_max_deg"]:
        raise ValueError("amplitude_min_deg cannot exceed amplitude_max_deg")
    if lim["beat_error_max_ms"] <= 0:
        raise ValueError("beat_error_max_ms must be positive")
    if lim["positional_rate_spread_max_s_per_day"] <= 0:
        raise ValueError("positional_rate_spread_max_s_per_day must be positive")
    if lim["chronograph_rate_delta_max_s_per_day"] <= 0:
        raise ValueError("chronograph_rate_delta_max_s_per_day must be positive")
    if m["amplitude_deg"] < 0 or m["beat_error_ms"] < 0:
        raise ValueError("amplitude and beat error must be non-negative")
    if m["positional_rate_spread_s_per_day"] < 0:
        raise ValueError("positional rate spread must be non-negative")

    frequency_error = abs(m["frequency_hz"] - lim["frequency_target_hz"])
    chrono_delta = abs(
        m["chronograph_on_rate_s_per_day"] -
        m["chronograph_off_rate_s_per_day"]
    )
    checks = {
        "frequency_within_tolerance": frequency_error <= lim["frequency_tolerance_hz"],
        "rate_within_limits": (
            lim["rate_min_s_per_day"] <= m["rate_s_per_day"] <=
            lim["rate_max_s_per_day"]
        ),
        "amplitude_within_limits": (
            lim["amplitude_min_deg"] <= m["amplitude_deg"] <=
            lim["amplitude_max_deg"]
        ),
        "beat_error_within_limit": m["beat_error_ms"] <= lim["beat_error_max_ms"],
        "positional_spread_within_limit": (
            m["positional_rate_spread_s_per_day"] <=
            lim["positional_rate_spread_max_s_per_day"]
        ),
        "chronograph_interaction_within_limit": (
            chrono_delta <= lim["chronograph_rate_delta_max_s_per_day"]
        ),
    }
    return {
        "model": "steward.c01.balance-escapement.measurement.v1",
        "frequency_error_hz": frequency_error,
        "chronograph_rate_delta_s_per_day": chrono_delta,
        "checks": checks,
        "passed": all(checks.values()),
    }


def evaluate_power_reserve_sweep(
    samples: list[dict[str, Any]],
    approved_amplitude_min_deg: float,
    approved_amplitude_max_deg: float,
    approved_rate_min_s_per_day: float,
    approved_rate_max_s_per_day: float,
) -> dict[str, Any]:
    """Check measured amplitude/rate stability across measured reserve states.

    Each sample requires reserve_state_fraction, amplitude_deg and rate_s_per_day.
    The reserve fraction is a normalized measured state descriptor, not a
    predicted remaining-hours value. The caller supplies approved limits.
    """
    if not samples:
        raise ValueError("at least one measured reserve sample is required")
    amp_min = _finite(approved_amplitude_min_deg, "approved_amplitude_min_deg")
    amp_max = _finite(approved_amplitude_max_deg, "approved_amplitude_max_deg")
    rate_min = _finite(approved_rate_min_s_per_day, "approved_rate_min_s_per_day")
    rate_max = _finite(approved_rate_max_s_per_day, "approved_rate_max_s_per_day")
    if amp_min < 0 or amp_min > amp_max or rate_min > rate_max:
        raise ValueError("invalid approved reserve-sweep limits")

    normalized = []
    for index, sample in enumerate(samples):
        required = ("reserve_state_fraction", "amplitude_deg", "rate_s_per_day")
        missing = [key for key in required if key not in sample]
        if missing:
            raise ValueError(f"sample {index} missing: {', '.join(missing)}")
        reserve = _finite(sample["reserve_state_fraction"], "reserve_state_fraction")
        amplitude = _finite(sample["amplitude_deg"], "amplitude_deg")
        rate = _finite(sample["rate_s_per_day"], "rate_s_per_day")
        if not 0.0 <= reserve <= 1.0:
            raise ValueError("reserve_state_fraction must be between 0 and 1")
        normalized.append({
            "reserve_state_fraction": reserve,
            "amplitude_deg": amplitude,
            "rate_s_per_day": rate,
            "passed": amp_min <= amplitude <= amp_max and rate_min <= rate <= rate_max,
        })
    ordered = sorted(normalized, key=lambda item: item["reserve_state_fraction"])
    return {
        "sample_count": len(ordered),
        "samples": ordered,
        "passed": all(item["passed"] for item in ordered),
        "amplitude_span_deg": (
            max(item["amplitude_deg"] for item in ordered) -
            min(item["amplitude_deg"] for item in ordered)
        ),
        "rate_span_s_per_day": (
            max(item["rate_s_per_day"] for item in ordered) -
            min(item["rate_s_per_day"] for item in ordered)
        ),
    }
