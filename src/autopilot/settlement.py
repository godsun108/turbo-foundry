"""Conservative offline call-history settlement assessment."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

@dataclass(frozen=True)
class Observation:
    observed_at: datetime
    child_sids: tuple[str, ...]
    pagination_complete: bool

@dataclass(frozen=True)
class Settlement:
    settled_for_review: bool
    reason: str

def assess_settlement(call_ended_at: datetime, observations: tuple[Observation, ...],
                      *, now: datetime, minimum_age_seconds: int=300,
                      observation_gap_seconds: int=120) -> Settlement:
    """Settlement permits review only, never message authorization."""
    times=[call_ended_at,now]+[o.observed_at for o in observations]
    if any(not isinstance(t,datetime) or t.tzinfo is None or t.utcoffset() is None for t in times):
        return Settlement(False,"invalid_timestamp")
    if any(not isinstance(v,int) or isinstance(v,bool) or v<1
           for v in (minimum_age_seconds,observation_gap_seconds)):
        return Settlement(False,"invalid_policy")
    ended=call_ended_at.astimezone(timezone.utc)
    current=now.astimezone(timezone.utc)
    if ended>current:
        return Settlement(False,"future_call_end")
    if current-ended<timedelta(seconds=minimum_age_seconds):
        return Settlement(False,"call_too_recent")
    if len(observations)<2:
        return Settlement(False,"insufficient_observations")
    ordered=sorted(observations,key=lambda o:o.observed_at)
    if any(o.observed_at.astimezone(timezone.utc)>current or
           o.observed_at.astimezone(timezone.utc)<ended for o in ordered):
        return Settlement(False,"observation_outside_window")
    if any(not o.pagination_complete for o in ordered):
        return Settlement(False,"incomplete_pagination")
    if any(len(set(o.child_sids))!=len(o.child_sids) for o in ordered):
        return Settlement(False,"duplicate_child_sid")
    first,last=ordered[0],ordered[-1]
    if last.observed_at-first.observed_at<timedelta(seconds=observation_gap_seconds):
        return Settlement(False,"observations_too_close")
    if any(set(o.child_sids)!=set(first.child_sids) for o in ordered):
        return Settlement(False,"changing_child_set")
    return Settlement(True,"stable_history_for_review_only")
