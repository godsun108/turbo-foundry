"""Read-only Twilio SDK page adapter; requires authenticated client injection."""
from dataclasses import dataclass

@dataclass(frozen=True)
class TwilioPage:
    items: tuple
    next_cursor: str | None

class TwilioCallPager:
    """Uses Twilio Call list page objects, not list(limit) truncation guesses."""
    def __init__(self, client, account_sid: str):
        if not isinstance(account_sid,str) or not account_sid.startswith("AC") or len(account_sid)!=34:
            raise ValueError("invalid account SID")
        self.client=client
        self.account_sid=account_sid

    def fetch_page(self,parent_sid: str,cursor: str | None,page_size: int):
        if not isinstance(parent_sid,str) or not parent_sid.startswith("CA") or len(parent_sid)!=34:
            raise ValueError("invalid parent SID")
        if not isinstance(page_size,int) or isinstance(page_size,bool) or not 1<=page_size<=1000:
            raise ValueError("invalid page size")
        # A cursor is an opaque next-page URL supplied by the Twilio SDK.
        # Reject caller-controlled URLs; only SDK-generated next pages are supported.
        if cursor is not None:
            raise ValueError("opaque cursor continuation requires SDK page state")
        page=self.client.calls.page(parent_call_sid=parent_sid,page_size=page_size)
        records=tuple(page)
        for call in records:
            if getattr(call,"account_sid",None)!=self.account_sid:
                raise ValueError("call account mismatch")
            if getattr(call,"parent_call_sid",None)!=parent_sid:
                raise ValueError("call parent mismatch")
        if getattr(page,"next_page_url",None):
            raise ValueError("SDK continuation not yet implemented")
        return records,None
