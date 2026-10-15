"""Entirely fictional, provider-neutral history adapter.

Useful for contract tests of a second adapter without another paid provider.
Never represents authentic telephone events, consent or billable delivery.
"""
from .universal_gateway import CallHistory


class FictionalHistoryAdapter:
    provider = "fictional"

    def __init__(self, tenant_id: str, fixtures: dict[str, tuple[str, ...]]):
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("tenant binding required")
        if type(fixtures) is not dict:
            raise ValueError("fixture map required")
        for parent, children in fixtures.items():
            if (not isinstance(parent, str) or not parent
                    or not isinstance(children, tuple)
                    or any(not isinstance(c, str) or not c for c in children)):
                raise ValueError("invalid fixture")
        self.tenant_id = tenant_id
        self._fixtures = dict(fixtures)

    def enumerate_children(self, parent_id: str, *, page_size: int,
                           max_pages: int, max_legs: int) -> CallHistory:
        children = self._fixtures.get(parent_id)
        if children is None:
            return CallHistory(self.provider, self.tenant_id, parent_id, (),
                               False, "unknown_parent", 0)
        if len(children) != len(set(children)):
            return CallHistory(self.provider, self.tenant_id, parent_id, (),
                               False, "duplicate_child", 0)
        pages = max(1, (len(children) + page_size - 1) // page_size)
        if pages > max_pages or len(children) > max_legs:
            return CallHistory(self.provider, self.tenant_id, parent_id, (),
                               False, "read_limit_exceeded", min(pages, max_pages))
        return CallHistory(self.provider, self.tenant_id, parent_id,
                           tuple(sorted(children)), True, "fixture_exhaustion", pages)
