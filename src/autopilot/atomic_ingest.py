"""Atomic offline Twilio callback ingest. No outbound side effects."""
import hashlib
import json
import sqlite3
from datetime import datetime
from typing import Mapping
from .twilio_adapter import authenticate_twilio_voice_form
from .call_journal import CallJournal, JournalResult
from .parent_routing import ParentCallRouting
from .event_integrity import EventIntegrity
from .provisioning import NumberProvisioning

class AtomicCallIngest:
    def __init__(self, db_path: str):
        self.db_path=db_path
        # All three components must share the exact same SQLite database.
        ParentCallRouting(db_path)
        CallJournal(db_path)
        EventIntegrity(db_path)
        NumberProvisioning(db_path)

    def record(self, *, tenant_id: str | None, provisioned_number: str | None,
               url: str, params: Mapping[str,str], signature: str,
               auth_token: str, event_key: str, received_at: datetime,
               validator=None, provider_account_sid: str | None = None) -> JournalResult:
        if not event_key or received_at.tzinfo is None:
            return JournalResult(False,"invalid_metadata")
        call=authenticate_twilio_voice_form(url,params,signature,auth_token,validator=validator)
        if call is None:
            return JournalResult(False,"invalid_signature_or_event")
        parent=params.get("ParentCallSid","")
        if parent and (not parent.startswith("CA") or len(parent)!=34 or parent==call.call_sid):
            return JournalResult(False,"invalid_parent_sid")
        canonical=json.dumps(dict(params),sort_keys=True,separators=(",",":"),ensure_ascii=True)
        digest=hashlib.sha256(canonical.encode()).hexdigest()
        with sqlite3.connect(self.db_path,timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            if parent:
                route=db.execute("SELECT tenant_id FROM parent_routes WHERE call_sid=?",(parent,)).fetchone()
                if not route:
                    return JournalResult(False,"unknown_parent")
                tenant=route[0]
                existing=db.execute("SELECT parent_sid,tenant_id FROM child_routes WHERE call_sid=?",
                                    (call.call_sid,)).fetchone()
                if existing and existing!=(parent,tenant):
                    return JournalResult(False,"child_conflict")
                if not existing:
                    db.execute("INSERT INTO child_routes VALUES(?,?,?)",(call.call_sid,parent,tenant))
            else:
                if not tenant_id or not provisioned_number or call.destination!=provisioned_number:
                    return JournalResult(False,"invalid_parent_provisioning")
                tenant=tenant_id
                if not provider_account_sid or not db.execute("""SELECT 1 FROM provisioned_numbers WHERE phone_number=? AND tenant_id=? AND provider_account_sid=? AND enabled=1""",(provisioned_number,tenant,provider_account_sid)).fetchone():
                    return JournalResult(False,"unverified_provisioning")
                existing=db.execute("SELECT tenant_id,destination FROM parent_routes WHERE call_sid=?",
                                    (call.call_sid,)).fetchone()
                if existing and existing!=(tenant,provisioned_number):
                    return JournalResult(False,"parent_conflict")
                if not existing:
                    db.execute("INSERT INTO parent_routes VALUES(?,?,?)",
                               (call.call_sid,tenant,provisioned_number))
            old=db.execute("SELECT fingerprint FROM event_fingerprints WHERE tenant_id=? AND event_key=?",
                           (tenant,event_key)).fetchone()
            if old:
                if old[0]!=digest:
                    db.execute("""INSERT OR IGNORE INTO event_conflicts VALUES(?,?,?,?)""",
                               (tenant,event_key,digest,old[0]))
                    return JournalResult(False,"payload_conflict")
                return JournalResult(False,"duplicate")
            db.execute("INSERT INTO event_fingerprints VALUES(?,?,?)",(tenant,event_key,digest))
            db.execute("""INSERT INTO twilio_call_events
                (tenant_id,event_key,call_sid,parent_sid,call_status,received_at)
                VALUES(?,?,?,?,?,?)""",
                (tenant,event_key,call.call_sid,parent,call.call_status,received_at.isoformat()))
            return JournalResult(True,"recorded")
