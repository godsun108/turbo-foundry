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
    leases=RecheckLeases(db_path)
    token=leases.claim(tenant_id,parent_sid,now=now,lease_seconds=lease_seconds)
    if token is None:
        return WorkerResult(False,False,"not_claimed")
    try:
        enumerated=pager.enumerate_all(parent_sid)
        finished_at=clock()
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
        # No provider error can authorize messaging. Release only our own lease.
        leases.release(tenant_id,parent_sid,token)
        return WorkerResult(False,False,"worker_error")
