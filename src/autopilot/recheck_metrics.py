"""Read-only operational snapshot of the local provider recheck queue.

No network, messaging, or job-state mutations. Counts are tenant scoped.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3
import os
from urllib.parse import quote


@dataclass(frozen=True)
class RecheckMetrics:
    pending: int
    due: int
    exhausted: int
    complete: int
    active_leases: int
    expired_leases: int


def snapshot_recheck_metrics(db_path: str, tenant_id: str, *, now: datetime) -> RecheckMetrics:
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("tenant ID required")
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("timezone-aware time required")
    stamp = now.astimezone(timezone.utc).isoformat()
    # Explicitly read-only: never create a schema or an empty replacement DB.
    uri = "file:" + quote(os.path.abspath(db_path), safe="/") + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as db:
        db.execute("BEGIN")
        rows = dict(db.execute(
            "SELECT status, COUNT(*) FROM provider_rechecks WHERE tenant_id=? GROUP BY status",
            (tenant_id,),
        ).fetchall())
        due = db.execute(
            "SELECT COUNT(*) FROM provider_rechecks WHERE tenant_id=? AND status='pending' AND next_due<=?",
            (tenant_id, stamp),
        ).fetchone()[0]
        active = db.execute(
            "SELECT COUNT(*) FROM recheck_leases WHERE tenant_id=? AND expires_at>?",
            (tenant_id, stamp),
        ).fetchone()[0]
        expired = db.execute(
            "SELECT COUNT(*) FROM recheck_leases WHERE tenant_id=? AND expires_at<=?",
            (tenant_id, stamp),
        ).fetchone()[0]
        return RecheckMetrics(
            pending=rows.get("pending", 0),
            due=due,
            exhausted=rows.get("exhausted", 0),
            complete=rows.get("complete", 0),
            active_leases=active,
            expired_leases=expired,
        )
