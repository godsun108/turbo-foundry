"""Offline authenticated callback routing + journal, with no outbound effects."""
from datetime import datetime
from typing import Mapping
from .call_journal import CallJournal, JournalResult
from .parent_routing import ParentCallRouting

def record_routed_callback(
    *, routing: ParentCallRouting, journal: CallJournal,
    tenant_id: str | None, provisioned_number: str | None,
    url: str, params: Mapping[str,str], signature: str,
    auth_token: str, event_key: str, received_at: datetime,
    validator=None,
) -> JournalResult:
    """Register parent or route child; reject before journal on any ambiguity."""
    parent=params.get("ParentCallSid","")
    if parent:
        routed=routing.route_child(url=url,params=dict(params),signature=signature,
                                  auth_token=auth_token,validator=validator)
        if not routed.accepted:
            return JournalResult(False,routed.reason)
        tenant=routed.tenant_id
        # A child may dial an agent number; journal validation must use its
        # authenticated destination after tenant is resolved from the parent.
        destination=params.get("To","")
    else:
        if not tenant_id or not provisioned_number:
            return JournalResult(False,"missing_parent_provisioning")
        routed=routing.register_parent(tenant_id=tenant_id,provisioned_number=provisioned_number,
                                      url=url,params=dict(params),signature=signature,
                                      auth_token=auth_token,validator=validator)
        if not routed.accepted:
            return JournalResult(False,routed.reason)
        tenant=routed.tenant_id
        destination=provisioned_number
    return journal.record_signed_callback(
        tenant_id=tenant,provisioned_destination=destination,
        url=url,params=params,signature=signature,auth_token=auth_token,
        event_key=event_key,received_at=received_at,validator=validator)
