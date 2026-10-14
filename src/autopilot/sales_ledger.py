"""Local-only, minimal-data prospect and collected-payment ledger.

No contact PII, outbound messages, invoices, billing integrations or fake income.
A payment is marked collected only with a unique, externally verifiable
reference supplied by a trusted human operator after settlement review.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import sqlite3

STAGES = (
    "researched", "contacted", "replied", "interviewed", "qualified",
    "demoed", "proposal_requested", "pilot_authorized", "paying", "retained",
)
NEXT = {
    "researched": "contacted", "contacted": "replied", "replied": "interviewed",
    "interviewed": "qualified", "qualified": "demoed",
    "demoed": "proposal_requested", "proposal_requested": "pilot_authorized",
    "pilot_authorized": "paying", "paying": "retained",
}


@dataclass(frozen=True)
class PipelineSummary:
    stages: tuple[tuple[str, int], ...]
    collected_revenue_usd: Decimal


class SalesLedger:
    def __init__(self, path: str):
        self.path = path
        with sqlite3.connect(path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS prospect (
                prospect_id TEXT PRIMARY KEY, sector TEXT NOT NULL,
                stage TEXT NOT NULL, source_note TEXT NOT NULL
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS prospect_transition (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id TEXT NOT NULL,
                from_stage TEXT NOT NULL, to_stage TEXT NOT NULL,
                evidence_note TEXT NOT NULL
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS collected_payment (
                payment_reference TEXT PRIMARY KEY, prospect_id TEXT NOT NULL,
                amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
                verification_note TEXT NOT NULL
            )""")

    @staticmethod
    def _note(value, name):
        if not isinstance(value, str) or not value.strip() or len(value) > 500:
            raise ValueError(f"{name} must be a nonblank short string")
        return value.strip()

    def add_prospect(self, prospect_id: str, sector: str, source_note: str):
        prospect_id = self._note(prospect_id, "prospect_id")
        if len(prospect_id) > 80:
            raise ValueError("prospect ID too long")
        sector = self._note(sector, "sector")
        source_note = self._note(source_note, "source_note")
        with sqlite3.connect(self.path) as db:
            db.execute("""INSERT INTO prospect VALUES (?,?,?,?)""",
                       (prospect_id, sector, "researched", source_note))

    def advance(self, prospect_id: str, next_stage: str, evidence_note: str):
        prospect_id = self._note(prospect_id, "prospect_id")
        evidence_note = self._note(evidence_note, "evidence_note")
        if next_stage not in STAGES:
            raise ValueError("unknown stage")
        with sqlite3.connect(self.path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute("SELECT stage FROM prospect WHERE prospect_id=?",
                                 (prospect_id,)).fetchone()
            if current is None or NEXT.get(current[0]) != next_stage:
                raise ValueError("stage transition not permitted")
            if next_stage in ("paying", "retained"):
                payment = db.execute(
                    "SELECT 1 FROM collected_payment WHERE prospect_id=? LIMIT 1",
                    (prospect_id,)).fetchone()
                if payment is None:
                    raise ValueError("paying stage requires verified collected payment record")
            db.execute("UPDATE prospect SET stage=? WHERE prospect_id=?",
                       (next_stage, prospect_id))
            db.execute("""INSERT INTO prospect_transition
                (prospect_id,from_stage,to_stage,evidence_note)
                VALUES (?,?,?,?)""", (prospect_id, current[0], next_stage, evidence_note))

    def record_collected_payment(self, prospect_id: str, reference: str,
                                 amount_usd, verification_note: str):
        """Record an externally settled payment, NEVER initiate/verify one."""
        prospect_id = self._note(prospect_id, "prospect_id")
        reference = self._note(reference, "reference")
        verification_note = self._note(verification_note, "verification_note")
        try:
            amount = Decimal(str(amount_usd))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("invalid amount") from None
        if (not amount.is_finite() or amount <= 0
                or amount.as_tuple().exponent < -2
                or amount * 100 > 2_147_483_647):
            raise ValueError("amount must be positive USD with at most two decimals")
        cents = int(amount * 100)
        with sqlite3.connect(self.path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute("SELECT stage FROM prospect WHERE prospect_id=?",
                                 (prospect_id,)).fetchone()
            if current is None or current[0] not in ("pilot_authorized", "paying", "retained"):
                raise ValueError("authorized pilot stage required")
            db.execute("""INSERT INTO collected_payment
                (payment_reference,prospect_id,amount_cents,verification_note)
                VALUES (?,?,?,?)""", (reference, prospect_id, cents, verification_note))

    def summary(self) -> PipelineSummary:
        with sqlite3.connect(self.path) as db:
            counts = dict(db.execute(
                "SELECT stage,COUNT(*) FROM prospect GROUP BY stage").fetchall())
            total = db.execute(
                "SELECT COALESCE(SUM(amount_cents),0) FROM collected_payment").fetchone()[0]
        return PipelineSummary(
            tuple((stage, counts.get(stage, 0)) for stage in STAGES),
            Decimal(total) / Decimal(100),
        )
