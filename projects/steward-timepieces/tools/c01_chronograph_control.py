"""C-01 abstract two-pusher chronograph control-state model.

This is a functional state-machine specification, not a cam profile,
column-wheel geometry, lever drawing, or proof of mechanical feasibility.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ChronographState(str, Enum):
    STOPPED_ZERO = "stopped_zero"
    RUNNING = "running"
    STOPPED_ELAPSED = "stopped_elapsed"


class Button(str, Enum):
    START_STOP = "start_stop"
    RESET = "reset"


@dataclass(frozen=True)
class ControlOutputs:
    state: ChronographState
    clutch_engaged: bool
    brake_applied: bool
    reset_hammers_active: bool
    counters_held: bool


def transition(state: ChronographState, button: Button) -> ChronographState:
    """Return the required functional state after a valid pusher actuation."""
    if button == Button.START_STOP:
        if state == ChronographState.RUNNING:
            return ChronographState.STOPPED_ELAPSED
        return ChronographState.RUNNING
    if button == Button.RESET:
        if state == ChronographState.RUNNING:
            raise ValueError("Reset actuation is prohibited while chronograph is running")
        return ChronographState.STOPPED_ZERO
    raise ValueError(f"Unsupported button: {button}")


def outputs_for(state: ChronographState) -> ControlOutputs:
    if state == ChronographState.RUNNING:
        return ControlOutputs(state, True, False, False, False)
    if state == ChronographState.STOPPED_ELAPSED:
        return ControlOutputs(state, False, True, False, True)
    return ControlOutputs(state, False, True, False, True)


def sequence(events: list[str]) -> list[str]:
    """Evaluate named button events and return state after each event."""
    state = ChronographState.STOPPED_ZERO
    states = [state.value]
    for event in events:
        state = transition(state, Button(event))
        states.append(state.value)
    return states
