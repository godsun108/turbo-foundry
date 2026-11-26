"""C-01 mechanical day/date calendar functional model.

A conventional 1-31 date and seven-day weekday model. This is not a
perpetual calendar and does not encode month lengths or an unsafe time window.
The real mechanism must supply a verified correction-permission interlock.
"""
from __future__ import annotations

from dataclasses import dataclass


WEEKDAYS = (
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
)


@dataclass(frozen=True)
class CalendarState:
    weekday_index: int
    date: int

    def __post_init__(self) -> None:
        if not 0 <= self.weekday_index < 7:
            raise ValueError("weekday_index must be from 0 through 6")
        if not 1 <= self.date <= 31:
            raise ValueError("date must be from 1 through 31")

    @property
    def weekday(self) -> str:
        return WEEKDAYS[self.weekday_index]


def daily_changeover(state: CalendarState) -> CalendarState:
    """Advance weekday and date together by one daily indexing event."""
    return CalendarState((state.weekday_index + 1) % 7, state.date % 31 + 1)


def correct_weekday(state: CalendarState, direction: int,
                    correction_permitted: bool) -> CalendarState:
    _require_correction_permission(correction_permitted)
    _require_direction(direction)
    return CalendarState((state.weekday_index + direction) % 7, state.date)


def correct_date(state: CalendarState, direction: int,
                 correction_permitted: bool) -> CalendarState:
    _require_correction_permission(correction_permitted)
    _require_direction(direction)
    return CalendarState(state.weekday_index, (state.date - 1 + direction) % 31 + 1)


def _require_correction_permission(permitted: bool) -> None:
    if permitted is not True:
        raise ValueError(
            "Calendar correction blocked: caller must establish a mechanism-verified safe state"
        )


def _require_direction(direction: int) -> None:
    if direction not in (-1, 1):
        raise ValueError("Correction direction must be -1 or +1")


def month_end_correction_steps(month_length: int) -> int:
    """Manual date-advance steps to correct a 31-day display after month end."""
    if month_length not in (28, 29, 30, 31):
        raise ValueError("month_length must be 28, 29, 30 or 31")
    return 31 - month_length if month_length < 31 else 0


def calendar_event_energy_per_day(day_indexing_j: float,
                                  date_indexing_j: float,
                                  coincidence: bool = True) -> float:
    """Sum energy for daily event; coincidence flag documents shared timing.

    If events are simultaneous, caller supplies the measured combined event
    energy in both terms? No: provide combined energy as day_indexing_j and
    set date_indexing_j to zero. For independent events, sum both.
    """
    if day_indexing_j < 0 or date_indexing_j < 0:
        raise ValueError("Event energies must be non-negative")
    if coincidence:
        if date_indexing_j != 0:
            raise ValueError(
                "For coincident indexing, supply measured combined energy as day_indexing_j and zero date_indexing_j"
            )
        return day_indexing_j
    return day_indexing_j + date_indexing_j
