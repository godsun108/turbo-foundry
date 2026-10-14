"""Foundry Universal Gateway v0: read-only, provider-neutral observations.

This boundary deliberately has NO sending, dialing, credentials, network
client creation, or customer-facing API. Only a trusted application process
can bind adapters to accounts/tenants. No automatic fallback across vendors.
"""
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class CallHistory:
    provider: str
    tenant_id: str
    parent_id: str
    child_ids: tuple[str, ...]
    complete: bool
    reason: str
    pages_checked: int


@runtime_checkable
class CallHistoryAdapter(Protocol):
    provider: str
    tenant_id: str
    def enumerate_children(self, parent_id: str, *, page_size: int,
                           max_pages: int, max_legs: int) -> CallHistory: ...


@dataclass(frozen=True)
class GatewayResult:
    accepted: bool
    reason: str
    history: CallHistory | None = None


class ReadOnlyGateway:
    """Tenant/provider scoped registry, with deny-by-default local dispatch.

    Routing context must originate from authenticated service-side records.
    Neither tenant identifiers nor provider choices may be trusted from HTTP.
    Registry instances are process-local and cannot enforce access controls
    against callers with arbitrary Python execution privileges.
    """

    def __init__(self):
        self._routes: dict[tuple[str, str], CallHistoryAdapter] = {}

    def register(self, adapter: CallHistoryAdapter) -> None:
        if (not isinstance(adapter, CallHistoryAdapter)
                or not isinstance(adapter.provider, str)
                or not isinstance(adapter.tenant_id, str)
                or not adapter.provider.strip() or not adapter.tenant_id.strip()
                or len(adapter.provider) > 40 or len(adapter.tenant_id) > 100):
            raise ValueError("invalid provider adapter")
        key = (adapter.tenant_id, adapter.provider)
        if key in self._routes:
            raise ValueError("duplicate provider route")
        self._routes[key] = adapter

    def observe(self, *, trusted_tenant: str, provider: str, parent_id: str,
                page_size: int = 10, max_pages: int = 2,
                max_legs: int = 20) -> GatewayResult:
        if (not isinstance(trusted_tenant, str)
                or not isinstance(provider, str) or not isinstance(parent_id, str)
                or not trusted_tenant or not provider or not parent_id):
            return GatewayResult(False, "invalid_request")
        if (any(type(value) is not int for value in (page_size, max_pages, max_legs))
                or not 1 <= page_size <= 10
                or not 1 <= max_pages <= 2 or not 1 <= max_legs <= 20):
            return GatewayResult(False, "unapproved_read_bounds")
        adapter = self._routes.get((trusted_tenant, provider))
        if adapter is None:
            return GatewayResult(False, "unbound_provider")
        try:
            history = adapter.enumerate_children(
                parent_id, page_size=page_size, max_pages=max_pages,
                max_legs=max_legs)
        except Exception:
            return GatewayResult(False, "provider_adapter_error")
        if (not isinstance(history, CallHistory)
                or history.provider != provider
                or history.tenant_id != trusted_tenant
                or history.parent_id != parent_id
                or type(history.complete) is not bool
                or type(history.pages_checked) is not int
                or history.pages_checked < 0
                or not isinstance(history.reason, str)
                or not isinstance(history.child_ids, tuple)
                or any(not isinstance(item, str) or not item
                       for item in history.child_ids)
                or len(history.child_ids) != len(set(history.child_ids))
                or len(history.child_ids) > max_legs):
            return GatewayResult(False, "invalid_provider_result")
        if not history.complete:
            return GatewayResult(False, history.reason, history)
        if not 1 <= history.pages_checked <= max_pages:
            return GatewayResult(False, "invalid_provider_result")
        return GatewayResult(True, "read_only_history_complete", history)
