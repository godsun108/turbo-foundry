"""Conservative replay of authenticated journal evidence; never authorizes SMS."""
from dataclasses import dataclass
from .call_journal import CallJournal

TERMINAL = frozenset({"completed", "no-answer", "busy", "failed", "canceled"})
ACTIVE = frozenset({"queued", "ringing", "in-progress"})

@dataclass(frozen=True)
class ReplayAssessment:
    ready_for_review: bool
    reason: str
    parent_sid: str
    child_count: int

def assess_call_history(journal: CallJournal, tenant_id: str, parent_sid: str) -> ReplayAssessment:
    """Return review readiness only; cannot prove complete provider history."""
    with journal._connect() as db:
        rows = db.execute("""SELECT call_sid,parent_sid,call_status
            FROM twilio_call_events WHERE tenant_id=? AND
            (call_sid=? OR parent_sid=?) ORDER BY received_at,event_key""",
            (tenant_id,parent_sid,parent_sid)).fetchall()
    parent = [status for sid,psid,status in rows if sid==parent_sid and not psid]
    children = {}
    for sid,psid,status in rows:
        if psid==parent_sid and sid!=parent_sid:
            children.setdefault(sid,[]).append(status)
    if not parent:
        return ReplayAssessment(False,"parent_missing",parent_sid,len(children))
    if not children:
        return ReplayAssessment(False,"child_evidence_missing",parent_sid,0)
    if "completed" in parent:
        return ReplayAssessment(False,"parent_completed",parent_sid,len(children))
    if not any(s in TERMINAL for s in parent):
        return ReplayAssessment(False,"parent_nonterminal",parent_sid,len(children))
    for statuses in children.values():
        if "completed" in statuses or "in-progress" in statuses:
            return ReplayAssessment(False,"child_may_have_answered",parent_sid,len(children))
        if not any(s in TERMINAL for s in statuses):
            return ReplayAssessment(False,"child_nonterminal",parent_sid,len(children))
        if any(s in ("queued","ringing") for s in statuses) and not any(s in TERMINAL for s in statuses):
            return ReplayAssessment(False,"child_nonterminal",parent_sid,len(children))
    return ReplayAssessment(True,"candidate_for_manual_review_only",parent_sid,len(children))
