"""Twilio-to-Foundry read-only call history adapter.

Accepts a previously constructed SDK pager from a trusted local runtime.
Does not create SDK credentials or connect to any provider by itself.
"""
from .universal_gateway import CallHistory


class TwilioHistoryAdapter:
    provider = "twilio"

    def __init__(self, *, tenant_id: str, pager):
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("tenant binding required")
        from .twilio_paging import TwilioCallPager
        if not isinstance(pager, TwilioCallPager):
            raise ValueError("TwilioCallPager required")
        self.tenant_id = tenant_id
        self._pager = pager

    def enumerate_children(self, parent_id: str, *, page_size: int,
                           max_pages: int, max_legs: int) -> CallHistory:
        result = self._pager.enumerate_all(
            parent_id, page_size=page_size, max_pages=max_pages,
            max_legs=max_legs)
        return CallHistory(
            provider=self.provider, tenant_id=self.tenant_id,
            parent_id=parent_id, child_ids=result.child_sids,
            complete=result.complete, reason=result.reason,
            pages_checked=result.pages_checked,
        )
