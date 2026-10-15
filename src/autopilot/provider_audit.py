"""Read-only provider comparison with local journal; never authorizes SMS."""
from dataclasses import dataclass
from .call_journal import CallJournal
from .call_replay import assess_call_history
from .child_enumeration import enumerate_child_calls
from .paged_child_calls import enumerate_pages

@dataclass(frozen=True)
class ProviderAudit:
    consistent: bool
    reason: str
    checked_legs: int

def audit_parent_call(*, journal: CallJournal, provider_client,
                      tenant_id: str, parent_sid: str, fetch_page=None, sdk_pager=None) -> ProviderAudit:
    """Compare recorded legs with REST data; unknown completeness fails closed."""
    review=assess_call_history(journal,tenant_id,parent_sid)
    if not review.ready_for_review:
        return ProviderAudit(False,review.reason,0)
    with journal._connect() as db:
        rows=db.execute("""SELECT DISTINCT call_sid,parent_sid FROM twilio_call_events
            WHERE tenant_id=? AND (call_sid=? OR parent_sid=?)""",
            (tenant_id,parent_sid,parent_sid)).fetchall()
    try:
        parent=provider_client.fetch_call_snapshot(parent_sid)
        if parent.sid!=parent_sid or parent.parent_sid is not None:
            return ProviderAudit(False,"provider_parent_mismatch",1)
        if parent.status!="no-answer":
            return ProviderAudit(False,"provider_parent_status_mismatch",1)
        if sdk_pager is not None:
            enumerated=sdk_pager.enumerate_all(parent_sid)
            if not enumerated.complete:
                return ProviderAudit(False,"enumeration_"+enumerated.reason,1)
        elif fetch_page is not None:
            enumerated=enumerate_pages(fetch_page,parent_sid)
            if not enumerated.complete:
                return ProviderAudit(False,"enumeration_"+enumerated.reason,1)
        else:
            enumerated=enumerate_child_calls(provider_client,parent_sid)
            if not enumerated.complete and enumerated.reason!="pagination_completeness_unverified":
                return ProviderAudit(False,"enumeration_"+enumerated.reason,1)
        local_children={sid for sid, _ in rows if sid!=parent_sid}
        remote_children=set(enumerated.child_sids)
        if remote_children-local_children:
            return ProviderAudit(False,"provider_children_missing_from_journal",1)
        if local_children-remote_children:
            return ProviderAudit(False,"journal_children_missing_from_provider",1)
        checked=1
        for sid, recorded_parent in rows:
            if sid==parent_sid: continue
            child=provider_client.fetch_call_snapshot(sid)
            checked+=1
            if child.sid!=sid or child.parent_sid!=parent_sid:
                return ProviderAudit(False,"provider_child_link_mismatch",checked)
            if child.status in ("completed","in-progress"):
                return ProviderAudit(False,"provider_child_may_have_answered",checked)
            if child.status not in ("no-answer","busy","failed","canceled"):
                return ProviderAudit(False,"provider_child_unresolved",checked)
        # REST snapshots alone cannot establish that every child leg was enumerated.
        return ProviderAudit(False,"provider_leg_completeness_unverified",checked)
    except Exception:
        return ProviderAudit(False,"provider_fetch_failed",0)
