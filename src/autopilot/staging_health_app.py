"""Foundry isolated staging process: startup and health only.

Not a customer API, provider service or public web app. No network clients,
database, secrets, tenant details or operator endpoints. Loopback bind only.
"""
import json
import os
from wsgiref.simple_server import make_server


def application(environ, start_response):
    # Explicitly reject reverse proxies and nonloopback network clients.
    if environ.get("REMOTE_ADDR") not in ("127.0.0.1", "::1"):
        code, result = "403 Forbidden", {"error": "loopback_only"}
    elif any(environ.get(key) for key in (
        "HTTP_FORWARDED", "HTTP_X_FORWARDED_FOR",
        "HTTP_X_FORWARDED_HOST", "HTTP_X_FORWARDED_PROTO",
    )):
        code, result = "403 Forbidden", {"error": "proxy_forbidden"}
    elif environ.get("HTTP_HOST") not in (
        "127.0.0.1", "localhost", "[::1]",
        "127.0.0.1:8094", "localhost:8094",
    ):
        code, result = "403 Forbidden", {"error": "host_not_allowed"}
    elif environ.get("REQUEST_METHOD") not in ("GET", "HEAD"):
        code, result = "405 Method Not Allowed", {"error": "read_only"}
    elif environ.get("PATH_INFO") != "/healthz" or environ.get("QUERY_STRING"):
        code, result = "404 Not Found", {"error": "not_found"}
    else:
        code, result = "200 OK", {
            "status": "ready_for_offline_rehearsal",
            "mode": "loopback_health_only",
            "live_provider_connected": False,
            "live_service_ready": False,
            "customer_checkout_enabled": False,
            "communications_enabled": False,
        }
    body = json.dumps(result, sort_keys=True).encode("utf-8")
    start_response(code, [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store"),
        ("X-Content-Type-Options", "nosniff"),
        ("X-Frame-Options", "DENY"),
    ])
    return [] if environ.get("REQUEST_METHOD") == "HEAD" else [body]


def main():
    # Never accept HOST from the environment or expose a public service.
    port_text = os.environ.get("FOUNDRY_LOCAL_HEALTH_PORT", "8094")
    if not port_text.isdecimal() or not 1024 <= int(port_text) <= 65535:
        raise ValueError("invalid local health port")
    port = int(port_text)
    print("Foundry offline health-only process on localhost; not production-ready")
    with make_server("127.0.0.1", port, application) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
