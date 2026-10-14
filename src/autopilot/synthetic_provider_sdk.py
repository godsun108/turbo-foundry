"""Deterministic in-memory Twilio-shaped SDK sandbox.

No Twilio SDK dependency, HTTP, SMS, credentials, customer data or billing.
Only synthetic call SIDs and tenant-bound account fixtures are permitted.
This exercises the *existing* TwilioCallPager and worker without pretending
that network interoperability or provider authorization has been proven.
"""
from dataclasses import dataclass


def _sid(value, prefix):
    if (not isinstance(value, str) or len(value) != 34
            or not value.startswith(prefix)
            or not all(ch in "0123456789abcdefABCDEF" for ch in value[2:])):
        raise ValueError("synthetic SID must be a well-formed hexadecimal Twilio-shaped ID")
    return value


@dataclass(frozen=True)
class SyntheticCall:
    sid: str
    account_sid: str
    parent_call_sid: str


class SimulatedProviderError(Exception):
    def __init__(self, status):
        super().__init__("synthetic provider response")
        self.status = status


class _Page:
    def __init__(self, service, parent, size, index):
        self._service, self._parent, self._size, self._index = service, parent, size, index
        end = index + size
        self._items = service._calls[parent][index:end]
        self.next_page_url = "sandbox-next" if end < len(service._calls[parent]) else None

    def __iter__(self):
        return iter(self._items)

    def next_page(self):
        if self.next_page_url is None:
            return None
        return self._service._next_page(self._parent, self._size, self._index + self._size)


class _Calls:
    def __init__(self, service):
        self._service = service

    def page(self, *, parent_call_sid, page_size):
        service = self._service
        service._check_request(parent_call_sid, page_size)
        return service._next_page(parent_call_sid, page_size, 0)


class SyntheticTwilioClient:
    """Twilio-shaped *read-only* client; never use in place of live account proof.

    This intentionally lacks create/send APIs and refuses unknown parent SIDs.
    Account IDs are supplied by trusted fixture setup, not by a request handler.
    """

    def __init__(self, account_sid: str, fixtures: dict[str, tuple[str, ...]],
                 *, fail_page: int | None = None, fail_status: int = 503):
        self.account_sid = _sid(account_sid, "AC")
        if type(fixtures) is not dict:
            raise ValueError("fixtures must be a dictionary")
        self._calls = {}
        for parent, child_sids in fixtures.items():
            _sid(parent, "CA")
            if not isinstance(child_sids, tuple):
                raise ValueError("children must be a tuple")
            if len(child_sids) > 10000 or len(set(child_sids)) != len(child_sids):
                raise ValueError("invalid or duplicate children")
            for child in child_sids:
                _sid(child, "CA")
                if child == parent:
                    raise ValueError("parent cannot be its own child")
            self._calls[parent] = tuple(
                SyntheticCall(child, self.account_sid, parent) for child in child_sids
            )
        if fail_page is not None and (type(fail_page) is not int or fail_page < 1):
            raise ValueError("invalid failure page")
        if fail_status not in (401, 403, 429, 500, 502, 503, 504):
            raise ValueError("invalid synthetic failure status")
        self.fail_page = fail_page
        self.fail_status = fail_status
        self.page_requests = 0
        self.calls = _Calls(self)

    def _check_request(self, parent, size):
        _sid(parent, "CA")
        if parent not in self._calls:
            raise PermissionError("unknown or unbound parent call")
        if type(size) is not int or not 1 <= size <= 1000:
            raise ValueError("invalid page size")

    def _next_page(self, parent, size, offset):
        self._check_request(parent, size)
        self.page_requests += 1
        if self.fail_page == self.page_requests:
            raise SimulatedProviderError(self.fail_status)
        return _Page(self, parent, size, offset)
