"""Single-job read-only provider observation worker; never sends SMS."""
from dataclasses import dataclass
from datetime import datetime, timezone
from .recheck_leases import RecheckLeases
from .observation_store import ObservationStore
from .atomic_observation import commit_observation
from .settlement import Observation, assess_settlement

@dataclass(frozen=True)
class WorkerResult:
    recorded: bool
    settled_for_review: bool
    reason: str

def run_recheck(db_path,tenant_id,parent_sid,*,now: datetime,
                call_ended_at: datetime,pager,lease_seconds=120, clock=None):
    """Process one due job; caller supplies authenticated, account-bound pager."""
    if clock is None:
        clock=lambda: datetime.now(timezone.utc)
    # The same trusted clock must govern claim and completion in production.
    if not isinstance(now,datetime) or now.tzinfo is None or now.utcoffset() is None:
        return WorkerResult(False,False,"invalid_start_clock")
    leases=RecheckLeases(db_path)
    token=leases.claim(tenant_id,parent_sid,now=now,lease_seconds=lease_seconds)
    if token is None:
        return WorkerResult(False,False,"not_claimed")
    try:
        enumerated=pager.enumerate_all(parent_sid)
        finished_at=clock()
        if (not isinstance(finished_at,datetime) or finished_at.tzinfo is None
                or finished_at.utcoffset() is None or finished_at<now):
            # Invalid or backwards clocks cannot validate lease expiry.
            return WorkerResult(False,False,"invalid_completion_clock")
        if not enumerated.complete:
            if leases.finish(tenant_id,parent_sid,token,now=finished_at,
                             reason=enumerated.reason):
                return WorkerResult(False,False,enumerated.reason)
            return WorkerResult(False,False,"lease_lost")
        observation=Observation(finished_at,enumerated.child_sids,True)
        if not commit_observation(db_path,tenant_id,parent_sid,token,now=finished_at,
                                  observation=observation,reason="observation_saved"):
            return WorkerResult(False,False,"lease_lost")
        observations=ObservationStore(db_path).load(tenant_id,parent_sid)
        assessment=assess_settlement(call_ended_at,observations,now=finished_at)
        return WorkerResult(True,assessment.settled_for_review,assessment.reason)
    except Exception:
        # Record the failed attempt through the same lease-fenced retry path.
        try:
            if leases.finish(tenant_id,parent_sid,token,now=clock(),reason="worker_error"):
                return WorkerResult(False,False,"worker_error")
        except Exception:
            pass
        return WorkerResult(False,False,"lease_lost_or_storage_error")
