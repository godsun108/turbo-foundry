"""Loopback-only synthetic gateway HTTP rehearsal, not public hosting.

There is no login, session issuance, customer input, deployment, messaging,
payments or provider networking in HTTP routes. A local operator obtains a
short-lived token out of band from privileged setup. Only the server-selected
tenant/provider/parent can be observed, with a persisted default-off stop.
Do NOT bind this app to a public interface or put it behind a reverse proxy.
"""
import json
import os
from wsgiref.simple_server import make_server

from .fictional_history_adapter import FictionalHistoryAdapter
from .gateway_audited_reads import AuditedGatewayReads
from .gateway_local_sessions import LocalGatewaySessions
from .universal_gateway import ReadOnlyGateway
from .worker_control import WorkerControl

HEADERS = [
    ("Content-Type", "application/json; charset=utf-8"),
    ("Cache-Control", "no-store"),
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "no-referrer"),
    ("Content-Security-Policy", "default-src 'none'"),
]


def _reply(start_response, status, data, *, head=False):
    body = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    start_response(status, HEADERS + [("Content-Length", str(len(body)))])
    return [] if head else [body]


class LoopbackSyntheticApp:
    """A narrowly scoped integration harness with no public login endpoint."""

    def __init__(self, sessions: LocalGatewaySessions, control: WorkerControl,
                 *, tenant_id="synthetic-a", provider="fictional", parent_id="call-a"):
        if not isinstance(sessions, LocalGatewaySessions) or not isinstance(control, WorkerControl):
            raise ValueError("trusted local components required")
        if os.path.abspath(sessions.db_path) != os.path.abspath(control.db_path):
            raise ValueError("session and stop gate must share one database")
        self._sessions = sessions
        self._control = control
        self._tenant = tenant_id
        self._provider = provider
        self._parent = parent_id

    def __call__(self, environ, start_response):
        # Never trust forwarded-for or forwarded-host; this app must not be
        # made accessible via a reverse proxy, tunnel or public port.
        if environ.get("REMOTE_ADDR") not in ("127.0.0.1", "::1"):
            return _reply(start_response, "403 Forbidden", {"error": "loopback_only"})
        if (environ.get("HTTP_X_FORWARDED_FOR") or environ.get("HTTP_FORWARDED")
                or environ.get("HTTP_X_FORWARDED_HOST")):
            return _reply(start_response, "403 Forbidden", {"error": "proxy_forbidden"})
        method, path = environ.get("REQUEST_METHOD"), environ.get("PATH_INFO")
        if method not in ("GET", "HEAD"):
            return _reply(start_response, "405 Method Not Allowed", {"error": "read_only"})
        head = method == "HEAD"
        if path == "/healthz":
            return _reply(start_response, "200 OK",
                          {"status": "ok", "mode": "synthetic_loopback_only"}, head=head)
        if path != "/api/history":
            return _reply(start_response, "404 Not Found", {"error": "not_found"}, head=head)
        if environ.get("QUERY_STRING", ""):
            return _reply(start_response, "400 Bad Request",
                          {"error": "query_parameters_forbidden"}, head=head)
        # Never return sensitive history on HEAD; same auth check as GET.
        if not self._control.is_enabled():
            return _reply(start_response, "503 Service Unavailable",
                          {"error": "operator_stop_active"}, head=head)
        auth = environ.get("HTTP_AUTHORIZATION", "")
        if not isinstance(auth, str) or not auth.startswith("Bearer ") or len(auth) != 71:
            return _reply(start_response, "401 Unauthorized",
                          {"error": "invalid_session"}, head=head)
        token = auth[7:]
        from datetime import datetime, timezone
        result = self._sessions.observe(
            token=token, tenant_id=self._tenant,
            provider=self._provider, parent_id=self._parent,
            now=datetime.now(timezone.utc))
        if not result.accepted:
            return _reply(start_response, "403 Forbidden",
                          {"error": "read_denied"}, head=head)
        # Explicitly return counts, not phone numbers, raw child identifiers,
        # account tokens or customer records.
        return _reply(start_response, "200 OK",
                      {"mode": "fictional", "provider": "fictional",
                       "complete": True, "child_count": len(result.history.child_ids)},
                      head=head)


def make_synthetic_app(db_path: str):
    """Privileged local fixture; leaves kill switch OFF and issues no token."""
    gateway = ReadOnlyGateway()
    gateway.register(FictionalHistoryAdapter("synthetic-a",
                                             {"call-a": ("leg-1", "leg-2")}))
    reads = AuditedGatewayReads(db_path, gateway,
                                {"offline-operator": frozenset({"synthetic-a"})})
    try:
        reads.bind_parent(tenant_id="synthetic-a", provider="fictional",
                          parent_id="call-a")
    except __import__("sqlite3").IntegrityError:
        pass
    sessions = LocalGatewaySessions(db_path, reads)
    control = WorkerControl(db_path)
    return LoopbackSyntheticApp(sessions, control), sessions, control


def main():
    # Refuse configurable host binding; always localhost even if HOST is set.
    db_path = os.environ.get("FOUNDRY_SYNTHETIC_DB", "foundry-local-synthetic.sqlite")
    app, _, _ = make_synthetic_app(db_path)
    port = int(os.environ.get("PORT", "8091"))
    if not 1024 <= port <= 65535:
        raise ValueError("non-privileged local port required")
    print(f"Foundry SYNTHETIC loopback rehearsal: http://127.0.0.1:{port}")
    print("Operator stop is disabled by default. No login or token issuance over HTTP.")
    with make_server("127.0.0.1", port, app) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
