"""Foundry v0 executable OFFLINE missed-call workflow.

Local SQLite + deterministic mock outbox only. No real provider, SMS, network,
PII, activation endpoint or customer authorization is implemented.
"""
import re
import sqlite3
from dataclasses import dataclass
from .universal_business_templates import configure_business

_ID = re.compile(r"^[a-zA-Z0-9_-]{1,80}$")


class WorkflowDenied(ValueError):
    pass


def _valid(value):
    return isinstance(value, str) and _ID.fullmatch(value) is not None


@dataclass(frozen=True)
class MockResult:
    event_id: str
    state: str
    reason: str


class MockMissedCallEngine:
    """One deterministic simulation with tenant-scoped durable event state.

    Contacts are **fictional non-sensitive aliases**, never phone numbers.
    Human/provider consent is not established by a simulated consent flag.
    """

    def __init__(self, db_path):
        self.db_path = db_path
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS mock_contacts (
                tenant TEXT NOT NULL, alias TEXT NOT NULL,
                opted_out INTEGER NOT NULL DEFAULT 0 CHECK(opted_out IN (0,1)),
                PRIMARY KEY(tenant,alias))""")
            db.execute("""CREATE TABLE IF NOT EXISTS mock_events (
                tenant TEXT NOT NULL, event_id TEXT NOT NULL,
                alias TEXT NOT NULL, state TEXT NOT NULL,
                reason TEXT NOT NULL, reply_id TEXT,
                PRIMARY KEY(tenant,event_id),
                CHECK(state IN ('suppressed','pending','sent_mock',
                                'replied','escalated','stopped')))""")
            db.execute("""CREATE TABLE IF NOT EXISTS mock_outbox (
                tenant TEXT NOT NULL, event_id TEXT NOT NULL,
                template TEXT NOT NULL, delivered_mock INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(tenant,event_id))""")
            db.execute("""CREATE TABLE IF NOT EXISTS mock_replies (
                tenant TEXT NOT NULL, reply_id TEXT NOT NULL, event_id TEXT NOT NULL,
                disposition TEXT NOT NULL,
                PRIMARY KEY(tenant,reply_id))""")

    def missed_call(self, *, tenant, industry, event_id, alias,
                    consent_flag=False, during_hours=False):
        if not all(map(_valid, (tenant, event_id, alias))):
            raise WorkflowDenied("fictional aliases only")
        try:
            configure_business(tenant, industry, ("missed-call-recovery",))
        except ValueError as exc:
            raise WorkflowDenied("industry not configured for workflow") from exc
        if type(consent_flag) is not bool or type(during_hours) is not bool:
            raise WorkflowDenied("explicit simulation flags required")
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("""SELECT state FROM mock_events
                WHERE tenant=? AND event_id=?""", (tenant, event_id)).fetchone()
            if row:
                return MockResult(event_id, row[0], "duplicate_event")
            denied = db.execute("""SELECT opted_out FROM mock_contacts
                WHERE tenant=? AND alias=?""", (tenant, alias)).fetchone()
            reason = ("opted_out" if denied and denied[0] else
                      "no_simulated_permission" if not consent_flag else
                      "outside_simulated_hours" if not during_hours else
                      "mock_eligible")
            state = "pending" if reason == "mock_eligible" else "suppressed"
            db.execute("""INSERT INTO mock_events
                (tenant,event_id,alias,state,reason) VALUES (?,?,?,?,?)""",
                (tenant,event_id,alias,state,reason))
            if state == "pending":
                db.execute("""INSERT INTO mock_outbox (tenant,event_id,template)
                    VALUES (?,?,'fictional_follow_up_v0')""", (tenant,event_id))
        return MockResult(event_id,state,reason)

    def flush_mock(self, *, tenant, event_id, simulate_failure=False):
        """Mark a mocked action as simulated, never actually send anything."""
        if not all(map(_valid,(tenant,event_id))) or type(simulate_failure) is not bool:
            raise WorkflowDenied("invalid mock action")
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("""SELECT e.alias,e.state,o.delivered_mock
                FROM mock_events e JOIN mock_outbox o
                ON o.tenant=e.tenant AND o.event_id=e.event_id
                WHERE e.tenant=? AND e.event_id=?""",(tenant,event_id)).fetchone()
            if row is None or row[1] != "pending" or row[2]:
                raise WorkflowDenied("no pending mock message")
            opted = db.execute("""SELECT opted_out FROM mock_contacts
                WHERE tenant=? AND alias=?""", (tenant,row[0])).fetchone()
            if opted and opted[0]:
                db.execute("""UPDATE mock_events SET state='suppressed',
                    reason='opted_out_before_dispatch' WHERE tenant=? AND event_id=?""",
                    (tenant,event_id))
                return MockResult(event_id,"suppressed","opted_out_before_dispatch")
            if simulate_failure:
                return MockResult(event_id,"pending","mock_provider_failure")
            db.execute("""UPDATE mock_outbox SET delivered_mock=1
                WHERE tenant=? AND event_id=?""", (tenant,event_id))
            db.execute("""UPDATE mock_events SET state='sent_mock',reason='mock_sent'
                WHERE tenant=? AND event_id=?""", (tenant,event_id))
        return MockResult(event_id,"sent_mock","mock_sent")

    def reply(self, *, tenant, event_id, reply_id, kind):
        if not all(map(_valid,(tenant,event_id,reply_id))) or kind not in (
                "interested","question","stop"):
            raise WorkflowDenied("unapproved fictional reply")
        with sqlite3.connect(self.db_path,timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            event = db.execute("""SELECT alias,state FROM mock_events
                WHERE tenant=? AND event_id=?""",(tenant,event_id)).fetchone()
            if not event or event[1] != "sent_mock":
                raise WorkflowDenied("no simulated sent message to reply to")
            exists=db.execute("""SELECT 1 FROM mock_replies WHERE tenant=? AND reply_id=?""",
                (tenant,reply_id)).fetchone()
            if exists:
                raise WorkflowDenied("duplicate simulated reply")
            state = "stopped" if kind=="stop" else ("escalated" if kind=="question" else "replied")
            db.execute("""INSERT INTO mock_replies VALUES (?,?,?,?)""",
                       (tenant,reply_id,event_id,kind))
            if kind=="stop":
                db.execute("""INSERT INTO mock_contacts(tenant,alias,opted_out)
                    VALUES(?,?,1) ON CONFLICT(tenant,alias)
                    DO UPDATE SET opted_out=1""",(tenant,event[0]))
            db.execute("""UPDATE mock_events SET state=?,reason=?,reply_id=?
                WHERE tenant=? AND event_id=?""",
                (state,"mock_reply_"+kind,reply_id,tenant,event_id))
            return MockResult(event_id,state,"mock_reply_"+kind)

    def status(self, *, tenant, event_id):
        if not all(map(_valid,(tenant,event_id))):
            raise WorkflowDenied("invalid identifiers")
        with sqlite3.connect(self.db_path) as db:
            row=db.execute("""SELECT state,reason FROM mock_events
                WHERE tenant=? AND event_id=?""",(tenant,event_id)).fetchone()
        return None if not row else MockResult(event_id,*row)
