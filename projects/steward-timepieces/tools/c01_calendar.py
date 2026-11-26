"""STEWARD C-01 calendar logic and measurement helpers.

The model represents the user-visible calendar state and correction rules.
It does not model physical date-star geometry, jumper force, calendar torque,
month cams, or the mechanical quickset safety window.
"""
from __future__ import annotations

from math import isfinite
from typing import Any

WEEKDAY_COUNT = 7
DATE_WHEEL_POSITIONS = 31


def _integer(value: Any, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def validate_calendar_state(date: int, weekday: int, month_length: int) -> dict[str, int]:
    """Validate a date/weekday state for a supplied calendar month length."""
    _integer(month_length, "month_length", 28, 31)
    _integer(date, "date", 1, month_length)
    _integer(weekday, "weekday", 0, WEEKDAY_COUNT - 1)
    return {"date": date, "weekday": weekday, "month_length": month_length}


def advance_one_day(date: int, weekday: int, month_length: int) -> dict[str, int | bool]:
    """Advance one calendar day; month rollover is driven by supplied month length."""
    validate_calendar_state(date, weekday, month_length)
    if date == month_length:
        return {
            "date": 1,
            "weekday": (weekday + 1) % WEEKDAY_COUNT,
            "month_rollover": True,
            "manual_correction_required": False,
        }
    return {
        "date": date + 1,
        "weekday": (weekday + 1) % WEEKDAY_COUNT,
        "month_rollover": False,
        "manual_correction_required": False,
    }


def advance_days(date: int, weekday: int, month_length: int, days: int) -> dict[str, int]:
    """Advance within a known month, rolling date to 1 at its supplied month end."""
    validate_calendar_state(date, weekday, month_length)
    _integer(days, "days", 0, 366)
    for _ in range(days):
        state = advance_one_day(date, weekday, month_length)
        date = int(state["date"])
        weekday = int(state["weekday"])
    return {"date": date, "weekday": weekday}


def correct_date(date: int, month_length: int) -> int:
    """Set an independently corrected date display to a valid day in the month."""
    _integer(month_length, "month_length", 28, 31)
    return _integer(date, "date", 1, month_length)


def correct_weekday(weekday: int) -> int:
    """Set an independently corrected weekday display."""
    return _integer(weekday, "weekday", 0, WEEKDAY_COUNT - 1)


def date_wheel_position(date: int) -> int:
    """Return zero-based position on a conventional 31-position date wheel."""
    _integer(date, "date", 1, DATE_WHEEL_POSITIONS)
    return date - 1


def calendar_load_comparison(stopped_energy_j: float, running_energy_j: float,
                             stopped_interval_s: float,
                             running_interval_s: float) -> dict[str, float]:
    """Compare measured calendar-idle and calendar-advance energy over matched intervals.

    Inputs must share the same measurement boundary and controlled test conditions.
    This reports a load delta, not calendar efficiency.
    """
    values = (stopped_energy_j, running_energy_j,
              stopped_interval_s, running_interval_s)
    names = ("stopped_energy_j", "running_energy_j",
             "stopped_interval_s", "running_interval_s")
    checked = []
    for value, name in zip(values, names):
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be numeric") from exc
        if not isfinite(number):
            raise ValueError(f"{name} must be finite")
        checked.append(number)
    off_e, on_e, off_t, on_t = checked
    if off_e < 0 or on_e < 0:
        raise ValueError("energy values must be non-negative")
    if off_t <= 0 or on_t <= 0:
        raise ValueError("intervals must be positive")
    if abs(off_t - on_t) > max(off_t, on_t) * 1e-9:
        raise ValueError("measurement intervals must match")
    return {
        "idle_average_power_w": off_e / off_t,
        "advancing_average_power_w": on_e / on_t,
        "incremental_energy_j": on_e - off_e,
        "incremental_average_power_w": (on_e - off_e) / off_t,
    }
