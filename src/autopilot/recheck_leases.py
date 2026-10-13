"""Atomic SQLite worker leases for scheduled rechecks; no provider side effects."""
import sqlite3
from datetime import datetime,timedelta,timezone
from uuid import uuid4

class RecheckLeases:
    def __init__(self,db_path):
        self.db_path=db_path
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS recheck_leases (
                tenant_id TEXT NOT NULL,parent_sid TEXT NOT NULL,
                lease_token TEXT NOT NULL,expires_at TEXT NOT NULL,
                PRIMARY KEY (tenant_id,parent_sid))""")

    @staticmethod
    def stamp(value):
        if not isinstance(value,datetime) or value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timezone-aware timestamp required")
        return value.astimezone(timezone.utc).isoformat()

    def claim(self,tenant_id,parent_sid,*,now,lease_seconds=120):
        stamp=self.stamp(now)
        if not tenant_id or not parent_sid or not isinstance(lease_seconds,int) or isinstance(lease_seconds,bool) or not 1<=lease_seconds<=3600:
            raise ValueError("invalid lease")
        token=uuid4().hex
        expiry=self.stamp(now+timedelta(seconds=lease_seconds))
        with sqlite3.connect(self.db_path,timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("""SELECT status,next_due FROM provider_rechecks
                WHERE tenant_id=? AND parent_sid=?""",(tenant_id,parent_sid)).fetchone()
            if row is None or row[0]!="pending" or row[1]>stamp:
                return None
            lease=db.execute("""SELECT expires_at FROM recheck_leases
                WHERE tenant_id=? AND parent_sid=?""",(tenant_id,parent_sid)).fetchone()
            if lease and lease[0]>stamp:
                return None
            db.execute("""INSERT INTO recheck_leases(tenant_id,parent_sid,lease_token,expires_at)
                VALUES(?,?,?,?) ON CONFLICT(tenant_id,parent_sid) DO UPDATE SET
                lease_token=excluded.lease_token,expires_at=excluded.expires_at""",
                (tenant_id,parent_sid,token,expiry))
        return token

    def release(self,tenant_id,parent_sid,token):
        with sqlite3.connect(self.db_path) as db:
            result=db.execute("""DELETE FROM recheck_leases
                WHERE tenant_id=? AND parent_sid=? AND lease_token=?""",
                (tenant_id,parent_sid,token))
            return result.rowcount==1

    def owns(self,tenant_id,parent_sid,token,*,now):
        stamp=self.stamp(now)
        with sqlite3.connect(self.db_path) as db:
            row=db.execute("""SELECT expires_at FROM recheck_leases
                WHERE tenant_id=? AND parent_sid=? AND lease_token=?""",
                (tenant_id,parent_sid,token)).fetchone()
        return row is not None and row[0]>stamp
