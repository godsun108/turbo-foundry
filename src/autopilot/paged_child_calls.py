"""Explicit page-by-page child-call retrieval; offline, read-only."""
from dataclasses import dataclass

@dataclass(frozen=True)
class PageResult:
    complete: bool
    reason: str
    child_sids: tuple[str,...]
    pages_checked: int

def enumerate_pages(fetch_page, parent_sid: str, *, max_pages: int=10,
                    max_legs: int=100, page_size: int=50) -> PageResult:
    """fetch_page(parent_sid, cursor, page_size) -> (items, next_cursor).

    A null next_cursor explicitly signals exhaustion under the injected
    provider adapter's contract. The caller must verify this contract.
    """
    if not isinstance(parent_sid,str) or not parent_sid.startswith("CA") or len(parent_sid)!=34:
        return PageResult(False,"invalid_parent_sid",(),0)
    if any(not isinstance(v,int) or isinstance(v,bool) or v<1 for v in (max_pages,max_legs,page_size)):
        return PageResult(False,"invalid_bounds",(),0)
    if max_pages>100 or max_legs>10000 or page_size>1000:
        return PageResult(False,"invalid_bounds",(),0)
    cursor=None
    visited=set()
    found=set()
    for page in range(1,max_pages+1):
        try:
            result=fetch_page(parent_sid,cursor,page_size)
        except TimeoutError:
            return PageResult(False,"provider_timeout",tuple(sorted(found)),page)
        except Exception:
            return PageResult(False,"provider_error",tuple(sorted(found)),page)
        if not isinstance(result,tuple) or len(result)!=2:
            return PageResult(False,"malformed_page",tuple(sorted(found)),page)
        items,next_cursor=result
        if not isinstance(items,(list,tuple)) or len(items)>page_size:
            return PageResult(False,"malformed_page",tuple(sorted(found)),page)
        for item in items:
            sid=getattr(item,"sid",None)
            linked=getattr(item,"parent_call_sid",None)
            if not isinstance(sid,str) or not sid.startswith("CA") or len(sid)!=34 or sid==parent_sid:
                return PageResult(False,"invalid_child_sid",tuple(sorted(found)),page)
            if linked!=parent_sid:
                return PageResult(False,"child_parent_mismatch",tuple(sorted(found)),page)
            if sid in found:
                return PageResult(False,"duplicate_child",tuple(sorted(found)),page)
            found.add(sid)
            if len(found)>max_legs:
                return PageResult(False,"leg_limit_exceeded",tuple(sorted(found)),page)
        if next_cursor is None:
            return PageResult(True,"explicit_page_exhaustion",tuple(sorted(found)),page)
        if not isinstance(next_cursor,str) or not next_cursor or next_cursor in visited:
            return PageResult(False,"invalid_or_repeated_cursor",tuple(sorted(found)),page)
        visited.add(next_cursor)
        cursor=next_cursor
    return PageResult(False,"page_limit_exceeded",tuple(sorted(found)),max_pages)
