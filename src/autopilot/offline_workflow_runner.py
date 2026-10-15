"""Reusable OFFLINE workflow runner with durable queue, reviews and retries.

Only executes registered synchronous mock callbacks. No network connectors, workers,
authentication, paid services or guaranteed exactly-once external effects.
"""
from dataclasses import dataclass
import re
import sqlite3

_KEY = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


class RunnerDenied(ValueError):
    pass


@dataclass(frozen=True)
class Job:
    tenant: str
    job_id: str
    action: str
    state: str
    attempts: int
    due_at: int


def _key(value):
    return isinstance(value, str) and _KEY.fullmatch(value) is not None


def _time(value):
    return type(value) is int and 0 <= value <= 2**53


class OfflineWorkflowRunner:
    """Trusted-fixture-only scheduler; callbacks execute under local SQLite lock.

    A callback should be a local, deterministic mock without external side effects.
    Neither tenant IDs nor approvals are authenticated. No real dispatch supported.
    """

    def __init__(self, db_path, actions):
        if not isinstance(actions, dict) or not actions or any(
                not _key(name) or not callable(callback)
                for name, callback in actions.items()):
            raise RunnerDenied("explicit mock action registry required")
        self.db_path = db_path
        self._actions = dict(actions)
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS offline_jobs (
                tenant TEXT NOT NULL, job_id TEXT NOT NULL, action TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN
                ('awaiting_review','queued','completed','failed','stopped')),
                attempts INTEGER NOT NULL DEFAULT 0,
                due_at INTEGER NOT NULL,
                needs_review INTEGER NOT NULL CHECK(needs_review IN (0,1)),
                PRIMARY KEY(tenant,job_id))""")
            db.execute("""CREATE TABLE IF NOT EXISTS offline_job_audit (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT, tenant TEXT NOT NULL,
                job_id TEXT NOT NULL, state TEXT NOT NULL, reason TEXT NOT NULL)""")

    def _audit(self, db, tenant, job_id, state, reason):
        db.execute("INSERT INTO offline_job_audit(tenant,job_id,state,reason) VALUES(?,?,?,?)",
                   (tenant,job_id,state,reason))

    def submit(self, *, tenant, job_id, action, due_at, needs_review=True):
        if (not _key(tenant) or not _key(job_id) or action not in self._actions
                or not _time(due_at) or type(needs_review) is not bool):
            raise RunnerDenied("invalid fictional job")
        state = "awaiting_review" if needs_review else "queued"
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM offline_jobs WHERE tenant=? AND job_id=?",
                          (tenant,job_id)).fetchone():
                return False
            db.execute("""INSERT INTO offline_jobs
                (tenant,job_id,action,state,attempts,due_at,needs_review)
                VALUES(?,?,?,?,0,?,?)""",(tenant,job_id,action,state,due_at,int(needs_review)))
            self._audit(db,tenant,job_id,state,"submitted_mock")
        return True

    def approve(self, *, tenant, job_id, fictional_reviewer):
        if not all(_key(x) for x in (tenant,job_id,fictional_reviewer)):
            raise RunnerDenied("fictional reviewer required")
        with sqlite3.connect(self.db_path,timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT name FROM sqlite_master WHERE name=?",
                          ("offline_capabilities",)).fetchone():
                raise RunnerDenied("capability approval required")
            count=db.execute("""UPDATE offline_jobs SET state='queued'
                WHERE tenant=? AND job_id=? AND state='awaiting_review'""",
                (tenant,job_id)).rowcount
            if count != 1:
                raise RunnerDenied("no awaiting mock approval")
            self._audit(db,tenant,job_id,"queued","fictional_review_approved")
        return True

    def stop(self, *, tenant, job_id):
        if not _key(tenant) or not _key(job_id):
            raise RunnerDenied("invalid identity")
        with sqlite3.connect(self.db_path,timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            n=db.execute("""UPDATE offline_jobs SET state='stopped'
                WHERE tenant=? AND job_id=? AND state IN
                ('awaiting_review','queued','failed')""",(tenant,job_id)).rowcount
            if n:
                self._audit(db,tenant,job_id,"stopped","manual_fixture_stop")
            return n==1

    def run_due(self, *, now, limit=10, retry_seconds=60, max_attempts=3):
        if (not _time(now) or type(limit) is not int or not 1 <= limit <= 50
                or type(retry_seconds) is not int or not 1 <= retry_seconds <= 3600
                or type(max_attempts) is not int or not 1 <= max_attempts <= 10):
            raise RunnerDenied("bounded trusted clock and limits required")
        outcomes=[]
        # Serialize local mock callback + transition in one transaction.
        # Never run a network client while holding this lock.
        with sqlite3.connect(self.db_path,timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='mock_claim_jobs'").fetchone():
                raise RunnerDenied("claimed execution mode: legacy dispatch disabled")
            items=db.execute("""SELECT tenant,job_id,action,attempts,due_at
                FROM offline_jobs WHERE state='queued' AND due_at<=?
                ORDER BY due_at,tenant,job_id LIMIT ?""",(now,limit)).fetchall()
            for tenant,job_id,action,attempts,due_at in items:
                try:
                    ok=self._actions[action](tenant=tenant,job_id=job_id)
                    if ok is not True:
                        raise RunnerDenied("mock action not acknowledged")
                    state,reason,next_due="completed","mock_action_completed",due_at
                except Exception:
                    state="failed" if attempts+1>=max_attempts else "queued"
                    reason="mock_retry_exhausted" if state=="failed" else "mock_retry_scheduled"
                    next_due=now+retry_seconds*(2**attempts)
                db.execute("""UPDATE offline_jobs SET state=?,attempts=?,due_at=?
                    WHERE tenant=? AND job_id=?""",
                    (state,attempts+1,next_due,tenant,job_id))
                self._audit(db,tenant,job_id,state,reason)
                outcomes.append((tenant,job_id,state))
        return outcomes

    def status(self, *, tenant, job_id):
        if not _key(tenant) or not _key(job_id):
            raise RunnerDenied("invalid identity")
        with sqlite3.connect(self.db_path) as db:
            row=db.execute("""SELECT action,state,attempts,due_at FROM offline_jobs
                WHERE tenant=? AND job_id=?""",(tenant,job_id)).fetchone()
        return None if row is None else Job(tenant,job_id,*row)
