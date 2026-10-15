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

    def enumerate_all(self, parent_sid: str, *, page_size: int = 50,
                      max_pages: int = 10, max_legs: int = 100):
        """Use only SDK-managed next_page(); never follow user-provided URLs.

        Returns PageResult. Provider consistency and answer evidence remain separate.
        """
        from .paged_child_calls import PageResult
        if not isinstance(parent_sid,str) or not parent_sid.startswith("CA") or len(parent_sid)!=34:
            return PageResult(False,"invalid_parent_sid",(),0)
        if any(not isinstance(v,int) or isinstance(v,bool) or v<1
               for v in (page_size,max_pages,max_legs)):
            return PageResult(False,"invalid_bounds",(),0)
        if page_size>1000 or max_pages>100 or max_legs>10000:
            return PageResult(False,"invalid_bounds",(),0)
        seen=set()
        try:
            page=self.client.calls.page(parent_call_sid=parent_sid,page_size=page_size)
            for index in range(1,max_pages+1):
                if page is None:
                    return PageResult(False,"missing_page",tuple(sorted(seen)),index)
                records=tuple(page)
                if len(records)>page_size:
                    return PageResult(False,"oversized_page",tuple(sorted(seen)),index)
                for call in records:
                    sid=getattr(call,"sid",None)
                    if getattr(call,"account_sid",None)!=self.account_sid:
                        return PageResult(False,"account_mismatch",tuple(sorted(seen)),index)
                    if getattr(call,"parent_call_sid",None)!=parent_sid:
                        return PageResult(False,"parent_mismatch",tuple(sorted(seen)),index)
                    if not isinstance(sid,str) or not sid.startswith("CA") or len(sid)!=34 or sid==parent_sid:
                        return PageResult(False,"invalid_child_sid",tuple(sorted(seen)),index)
                    if sid in seen:
                        return PageResult(False,"duplicate_child",tuple(sorted(seen)),index)
                    seen.add(sid)
                    if len(seen)>max_legs:
                        return PageResult(False,"leg_limit_exceeded",tuple(sorted(seen)),index)
                next_url=getattr(page,"next_page_url",None)
                if next_url is None:
                    return PageResult(True,"sdk_page_exhaustion",tuple(sorted(seen)),index)
                if not isinstance(next_url,str) or not next_url:
                    return PageResult(False,"invalid_next_page_marker",tuple(sorted(seen)),index)
                if index==max_pages:
                    return PageResult(False,"page_limit_exceeded",tuple(sorted(seen)),index)
                next_method=getattr(page,"next_page",None)
                if not callable(next_method):
                    return PageResult(False,"missing_sdk_next_page",tuple(sorted(seen)),index)
                page=next_method()
        except TimeoutError:
            return PageResult(False,"provider_timeout",tuple(sorted(seen)),0)
        except Exception as exc:
            status=getattr(exc,"status",None)
            if status is None:
                status=getattr(exc,"status_code",None)
            if status==429:
                reason="provider_rate_limited"
            elif status in (500,502,503,504):
                reason="provider_temporarily_unavailable"
            elif status in (401,403):
                reason="provider_auth_failed"
            else:
                reason="provider_error"
            return PageResult(False,reason,tuple(sorted(seen)),0)
        return PageResult(False,"page_limit_exceeded",tuple(sorted(seen)),max_pages)
