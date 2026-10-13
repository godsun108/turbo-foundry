"""Atomic lease-fenced observation persistence and recheck advancement."""
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from .settlement import Observation

def _stamp(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timezone-aware timestamp required")
    return value.astimezone(timezone.utc).isoformat()

def commit_observation(db_path, tenant_id, parent_sid, lease_token, *,
                       now, observation: Observation, reason="observation_saved",
                       completed=False, base_delay_seconds=60):
    """Return False for stale leases; raise on conflicting evidence, rolling back."""
    stamp=_stamp(now)
    if not tenant_id or not parent_sid or not lease_token:
        raise ValueError("missing identity")
    if not isinstance(observation, Observation) or not observation.pagination_complete:
        raise ValueError("complete provider observation required")
    observed=_stamp(observation.observed_at)
    if observed>stamp:
        raise ValueError("future observation")
    if not isinstance(base_delay_seconds,int) or isinstance(base_delay_seconds,bool) or not 1<=base_delay_seconds<=3600:
        raise ValueError("invalid retry delay")
    if not isinstance(reason,str) or not reason:
        raise ValueError("invalid reason")
    if not isinstance(observation.child_sids,tuple) or any(
            not isinstance(s,str) or not s.startswith("CA") or len(s)!=34
            for s in observation.child_sids):
        raise ValueError("invalid child SIDs")
    if len(set(observation.child_sids))!=len(observation.child_sids):
        raise ValueError("duplicate child SIDs")
    ids=json.dumps(sorted(observation.child_sids))
    with sqlite3.connect(db_path,timeout=10) as db:
        db.execute("BEGIN IMMEDIATE")
        lease=db.execute("""SELECT expires_at FROM recheck_leases
            WHERE tenant_id=? AND parent_sid=? AND lease_token=?""",
            (tenant_id,parent_sid,lease_token)).fetchone()
        if lease is None or lease[0]<=stamp:
            return False
        job=db.execute("""SELECT attempts,max_attempts,status,next_due FROM provider_rechecks
            WHERE tenant_id=? AND parent_sid=?""",(tenant_id,parent_sid)).fetchone()
        if job is None or job[2]!="pending" or job[3]>stamp:
            return False
        prior=db.execute("""SELECT child_sids,pagination_complete FROM provider_observations
            WHERE tenant_id=? AND parent_sid=? AND observed_at=?""",
            (tenant_id,parent_sid,observed)).fetchone()
        if prior is not None and prior!=(ids,1):
            raise ValueError("conflicting observation")
        if prior is None:
            db.execute("""INSERT INTO provider_observations
                (tenant_id,parent_sid,observed_at,child_sids,pagination_complete)
                VALUES (?,?,?,?,1)""",(tenant_id,parent_sid,observed,ids))
        attempts=job[0]+1
        status="complete" if completed else ("exhausted" if attempts>=job[1] else "pending")
        delay=min(base_delay_seconds*2**(attempts-1),3600)
        due=_stamp(now+timedelta(seconds=delay))
        db.execute("""UPDATE provider_rechecks SET attempts=?,status=?,next_due=?,last_reason=?
            WHERE tenant_id=? AND parent_sid=?""",
            (attempts,status,due,reason,tenant_id,parent_sid))
        db.execute("""DELETE FROM recheck_leases
            WHERE tenant_id=? AND parent_sid=? AND lease_token=?""",
            (tenant_id,parent_sid,lease_token))
    return True
