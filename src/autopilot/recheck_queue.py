"""Durable bounded provider recheck scheduling; no network or SMS side effects."""
import sqlite3
from datetime import datetime, timedelta, timezone

class RecheckQueue:
    def __init__(self,db_path: str):
        self.db_path=db_path
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS provider_rechecks (
                tenant_id TEXT NOT NULL,parent_sid TEXT NOT NULL,
                attempts INTEGER NOT NULL,max_attempts INTEGER NOT NULL,
                next_due TEXT NOT NULL,status TEXT NOT NULL,
                last_reason TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (tenant_id,parent_sid))""")

    @staticmethod
    def _stamp(value):
        if not isinstance(value,datetime) or value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timezone-aware timestamp required")
        return value.astimezone(timezone.utc).isoformat()

    def schedule(self,tenant_id,parent_sid,*,now,max_attempts=4):
        stamp=self._stamp(now)
        if not tenant_id or not parent_sid or not isinstance(max_attempts,int) or isinstance(max_attempts,bool) or not 1<=max_attempts<=10:
            raise ValueError("invalid schedule")
        with sqlite3.connect(self.db_path) as db:
            cursor=db.execute("""INSERT OR IGNORE INTO provider_rechecks
                (tenant_id,parent_sid,attempts,max_attempts,next_due,status)
                VALUES (?,?,0,?,?,'pending')""",(tenant_id,parent_sid,max_attempts,stamp))
            return cursor.rowcount==1

    def due(self,*,now,limit=20):
        stamp=self._stamp(now)
        if not isinstance(limit,int) or isinstance(limit,bool) or not 1<=limit<=100:
            raise ValueError("invalid limit")
        with sqlite3.connect(self.db_path) as db:
            return db.execute("""SELECT tenant_id,parent_sid,attempts,max_attempts
                FROM provider_rechecks WHERE status='pending' AND next_due<=?
                ORDER BY next_due,tenant_id,parent_sid LIMIT ?""",(stamp,limit)).fetchall()

    def record_attempt(self,tenant_id,parent_sid,*,now,reason,completed=False,base_delay_seconds=60):
        stamp=self._stamp(now)
        if not isinstance(reason,str) or not reason or not isinstance(base_delay_seconds,int) or isinstance(base_delay_seconds,bool) or not 1<=base_delay_seconds<=3600:
            raise ValueError("invalid attempt")
        with sqlite3.connect(self.db_path) as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("""SELECT attempts,max_attempts,status,next_due FROM provider_rechecks
                WHERE tenant_id=? AND parent_sid=?""",(tenant_id,parent_sid)).fetchone()
            if row is None or row[2]!='pending' or row[3]>stamp:
                return False
            attempts=row[0]+1
            status='complete' if completed else ('exhausted' if attempts>=row[1] else 'pending')
            delay=min(base_delay_seconds*2**(attempts-1),3600)
            next_due=(now.astimezone(timezone.utc)+timedelta(seconds=delay)).isoformat()
            db.execute("""UPDATE provider_rechecks SET attempts=?,status=?,next_due=?,last_reason=?
                WHERE tenant_id=? AND parent_sid=?""",
                (attempts,status,next_due,reason,tenant_id,parent_sid))
        return True
