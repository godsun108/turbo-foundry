"""Durable authenticated callback journal; records evidence, never sends SMS."""
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping
from .twilio_adapter import authenticate_twilio_voice_form

@dataclass(frozen=True)
class JournalResult:
    recorded: bool
    reason: str

class CallJournal:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS twilio_call_events (
                tenant_id TEXT NOT NULL, event_key TEXT NOT NULL,
                call_sid TEXT NOT NULL, parent_sid TEXT NOT NULL,
                call_status TEXT NOT NULL, received_at TEXT NOT NULL,
                PRIMARY KEY (tenant_id,event_key)
            )""")

    def _connect(self):
        return sqlite3.connect(self.db_path, timeout=10)

    def record_signed_callback(
        self, *, tenant_id: str, provisioned_destination: str,
        url: str, params: Mapping[str,str], signature: str,
        auth_token: str, event_key: str, received_at: datetime,
        validator=None,
    ) -> JournalResult:
        if not tenant_id or not event_key or received_at.tzinfo is None:
            return JournalResult(False,"invalid_journal_metadata")
        call = authenticate_twilio_voice_form(url,params,signature,auth_token,validator=validator)
        if call is None:
            return JournalResult(False,"invalid_signature_or_event")
        if call.destination != provisioned_destination:
            return JournalResult(False,"unprovisioned_destination")
        parent = params.get("ParentCallSid","")
        if parent and (not parent.startswith("CA") or len(parent)!=34):
            return JournalResult(False,"invalid_parent_sid")
        with self._connect() as db:
            inserted=db.execute("""INSERT OR IGNORE INTO twilio_call_events
                (tenant_id,event_key,call_sid,parent_sid,call_status,received_at)
                VALUES(?,?,?,?,?,?)""",
                (tenant_id,event_key,call.call_sid,parent,call.call_status,received_at.isoformat()))
            return JournalResult(inserted.rowcount==1,
                                 "recorded" if inserted.rowcount==1 else "duplicate")

    def list_events(self, tenant_id: str, call_sid: str):
        with self._connect() as db:
            return db.execute("""SELECT event_key,call_status,parent_sid
                FROM twilio_call_events WHERE tenant_id=? AND call_sid=?
                ORDER BY received_at,event_key""",(tenant_id,call_sid)).fetchall()
