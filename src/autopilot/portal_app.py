"""Minimal Foundry web portal for local/staging PREVIEW only.

Read-only, standard-library WSGI application. No signup persistence, login,
Stripe sessions, provider access, checkout, SMS, or account provisioning.
Intended as a safe integration baseline before adding authenticated APIs.
"""
from dataclasses import asdict
import json
from wsgiref.simple_server import make_server

from .commercial_catalog import OFFERS
from .signup_preview import render_signup_preview

MAX_RESPONSE = 200_000


def _json(data):
    return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")
    headers = [
        ("Cache-Control", "no-store"),
        ("X-Content-Type-Options", "nosniff"),
        ("X-Frame-Options", "DENY"),
        ("Referrer-Policy", "no-referrer"),
        ("Content-Security-Policy",
         "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
         "img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"),
    ]
    if method not in ("GET", "HEAD"):
        response = _json({"error": "read_only_preview"})
        start_response("405 Method Not Allowed", headers + [
            ("Content-Type", "application/json"), ("Allow", "GET, HEAD"),
            ("Content-Length", str(len(response)))])
        return [] if method == "HEAD" else [response]
    if path in ("/", "/preview"):
        response = render_signup_preview().encode("utf-8")
        media = "text/html; charset=utf-8"
        status = "200 OK"
    elif path == "/api/offers":
        response = _json([
            {"slug": item.slug, "title": item.title, "status": item.status,
             "buyer": item.buyer, "proposed_outcome": item.proposed_outcome}
            for item in OFFERS
        ])
        media = "application/json"
        status = "200 OK"
    elif path == "/api/readiness":
        response = _json({
            "deployment": "preview_only",
            "live_checkout": False,
            "signup_submission": False,
            "customer_accounts": False,
            "payment_collection": False,
            "customer_sms": False,
            "service_activation": False,
        })
        media = "application/json"
        status = "200 OK"
    elif path == "/healthz":
        response = _json({"status": "ok", "mode": "preview_only"})
        media = "application/json"
        status = "200 OK"
    else:
        response = _json({"error": "not_found"})
        media = "application/json"
        status = "404 Not Found"
    if len(response) > MAX_RESPONSE:
        raise RuntimeError("unexpected large response")
    start_response(status, headers + [
        ("Content-Type", media), ("Content-Length", str(len(response)))])
    return [] if method == "HEAD" else [response]


def main():
    import os
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8080"))
    if not 0 < port < 65536:
        raise ValueError("invalid port")
    print(f"Foundry PREVIEW ONLY serving {host}:{port}")
    with make_server(host, port, application) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
