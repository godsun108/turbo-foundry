"""SQLite storage for authenticated provider pagination observations."""
import json
import sqlite3
from datetime import datetime, timezone
from .settlement import Observation

class ObservationStore:
    def __init__(self,db_path: str):
        self.db_path=db_path
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS provider_observations (
                tenant_id TEXT NOT NULL,
                parent_sid TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                child_sids TEXT NOT NULL,
                pagination_complete INTEGER NOT NULL,
                PRIMARY KEY (tenant_id,parent_sid,observed_at)
            )""")

    def append(self,tenant_id: str,parent_sid: str,observation: Observation) -> bool:
        if not tenant_id or not parent_sid or not isinstance(observation,Observation):
            raise ValueError("invalid observation identity")
        stamp=observation.observed_at
        if not isinstance(stamp,datetime) or stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone aware")
        if not observation.pagination_complete:
            raise ValueError("incomplete pagination cannot be recorded as settled observation")
        if len(set(observation.child_sids))!=len(observation.child_sids):
            raise ValueError("duplicate child SID")
        normalized=stamp.astimezone(timezone.utc).isoformat()
        ids=json.dumps(sorted(observation.child_sids))
        with sqlite3.connect(self.db_path) as db:
            existing=db.execute("""SELECT child_sids,pagination_complete FROM provider_observations
                WHERE tenant_id=? AND parent_sid=? AND observed_at=?""",
                (tenant_id,parent_sid,normalized)).fetchone()
            if existing is not None:
                if existing!=(ids,1):
                    raise ValueError("conflicting observation at same timestamp")
                return False
            db.execute("""INSERT INTO provider_observations
                (tenant_id,parent_sid,observed_at,child_sids,pagination_complete)
                VALUES (?,?,?,?,1)""",(tenant_id,parent_sid,normalized,ids))
        return True

    def load(self,tenant_id: str,parent_sid: str) -> tuple[Observation,...]:
        with sqlite3.connect(self.db_path) as db:
            rows=db.execute("""SELECT observed_at,child_sids,pagination_complete
                FROM provider_observations WHERE tenant_id=? AND parent_sid=?
                ORDER BY observed_at""",(tenant_id,parent_sid)).fetchall()
        return tuple(Observation(datetime.fromisoformat(t),tuple(json.loads(s)),bool(c))
                     for t,s,c in rows)
