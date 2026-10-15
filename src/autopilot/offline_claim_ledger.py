"""Crash-aware offline job claiming and receipts; never executes external effects.

Lease expiry quarantines ambiguous work instead of automatically replaying it.
All timestamps and worker identities are trusted fictional test inputs.
"""
from dataclasses import dataclass
import re
import sqlite3

_ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


class ClaimDenied(ValueError):
    pass


def _id(value):
    return isinstance(value, str) and _ID.fullmatch(value) is not None


def _clock(value):
    return type(value) is int and 0 <= value <= 2**53


@dataclass(frozen=True)
class Claim:
    tenant: str
    job_id: str
    token: str
    lease_until: int


class OfflineClaimLedger:
    """Local SQLite receipt ledger for simulations; no real action execution."""

    def __init__(self, db_path):
        self.db_path = db_path
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS mock_claim_jobs (
                tenant TEXT NOT NULL, job_id TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN
                    ('queued','claimed','completed','uncertain','cancelled')),
                due_at INTEGER NOT NULL, lease_until INTEGER,
                token TEXT, receipt TEXT,
                PRIMARY KEY(tenant,job_id))""")

    def submit(self, *, tenant, job_id, due_at):
        if not _id(tenant) or not _id(job_id) or not _clock(due_at):
            raise ClaimDenied("invalid fictional job")
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            return db.execute("""INSERT OR IGNORE INTO mock_claim_jobs
                (tenant,job_id,state,due_at) VALUES (?,?,'queued',?)""",
                (tenant,job_id,due_at)).rowcount == 1

    def claim(self, *, tenant, job_id, worker_token, now, lease_seconds=30):
        if (not all(_id(x) for x in (tenant,job_id,worker_token))
                or not _clock(now) or type(lease_seconds) is not int
                or not 1 <= lease_seconds <= 3600
                or not _clock(now+lease_seconds)):
            raise ClaimDenied("invalid claim")
        with sqlite3.connect(self.db_path,timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            updated=db.execute("""UPDATE mock_claim_jobs SET state='claimed',
                token=?,lease_until=? WHERE tenant=? AND job_id=?
                AND state='queued' AND due_at<=?""",
                (worker_token,now+lease_seconds,tenant,job_id,now)).rowcount
            if updated != 1:
                raise ClaimDenied("job unavailable or already claimed")
        return Claim(tenant,job_id,worker_token,now+lease_seconds)

    def complete(self, *, claim, receipt, now):
        if (not isinstance(claim,Claim) or not _id(claim.tenant)
                or not _id(claim.job_id) or not _id(claim.token)
                or not _id(receipt) or not _clock(now)):
            raise ClaimDenied("invalid mock receipt")
        with sqlite3.connect(self.db_path,timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            changed=db.execute("""UPDATE mock_claim_jobs SET
                state='completed',receipt=?,token=NULL,lease_until=NULL
                WHERE tenant=? AND job_id=? AND state='claimed'
                AND token=? AND lease_until>?""",
                (receipt,claim.tenant,claim.job_id,claim.token,now)).rowcount
            if changed != 1:
                raise ClaimDenied("stale, expired or already completed claim")
        return True

    def quarantine_expired(self, *, now):
        if not _clock(now):
            raise ClaimDenied("invalid trusted time")
        with sqlite3.connect(self.db_path,timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            return db.execute("""UPDATE mock_claim_jobs SET state='uncertain',
                token=NULL,lease_until=NULL WHERE state='claimed'
                AND lease_until<=?""",(now,)).rowcount

    def cancel(self, *, tenant, job_id):
        if not _id(tenant) or not _id(job_id):
            raise ClaimDenied("invalid identity")
        with sqlite3.connect(self.db_path,timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            return db.execute("""UPDATE mock_claim_jobs SET state='cancelled'
                WHERE tenant=? AND job_id=? AND state='queued'""",
                (tenant,job_id)).rowcount == 1

    def status(self, *, tenant, job_id):
        if not _id(tenant) or not _id(job_id):
            raise ClaimDenied("invalid identity")
        with sqlite3.connect(self.db_path) as db:
            row=db.execute("""SELECT state,receipt FROM mock_claim_jobs
                WHERE tenant=? AND job_id=?""",(tenant,job_id)).fetchone()
        return None if row is None else {"state":row[0],"mock_receipt":row[1]}
