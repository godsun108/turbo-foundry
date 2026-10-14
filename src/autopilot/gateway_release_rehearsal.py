"""Offline gateway lifecycle evidence; no sockets or provider access."""
import json
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .gateway_loopback_app import make_synthetic_app


def execute():
    results = {}
    def require(name, ok):
        results[name] = bool(ok)
    def get(app, token):
        replies = []
        env = dict(REQUEST_METHOD="GET", PATH_INFO="/api/history",
                   REMOTE_ADDR="127.0.0.1", HTTP_HOST="127.0.0.1",
                   QUERY_STRING="", HTTP_AUTHORIZATION="Bearer " + token)
        body = b"".join(app(env, lambda status, headers: replies.append(status)))
        return replies[0], json.loads(body)
    with tempfile.TemporaryDirectory() as temp:
        db = str(Path(temp) / "rehearsal.sqlite")
        app, sessions, control = make_synthetic_app(db)
        token = sessions.issue("offline-operator", now=datetime.now(timezone.utc))
        require("default_disabled", get(app, token)[0].startswith("503"))
        control.set_enabled(True)
        status, response = get(app, token)
        require("authorized_fictional_read", status.startswith("200")
                and response.get("child_count") == 2)
        control.set_enabled(False)
        require("stop_denies_read", get(app, token)[0].startswith("503"))
        control.set_enabled(True)
        app2, sessions2, control2 = make_synthetic_app(db)
        require("restart_fails_closed", not control2.is_enabled()
                and get(app2, token)[0].startswith("503"))
        control2.set_enabled(True)
        require("restart_recovery", get(app2, token)[0].startswith("200"))
        sessions2.revoke(token)
        require("revoked_session_denied", get(app2, token)[0].startswith("403"))
        replacement = sessions2.issue("offline-operator", now=datetime.now(timezone.utc))
        with sqlite3.connect(db) as connection:
            connection.execute("DROP TABLE gateway_read_audit")
        require("audit_storage_failure_denied", get(app2, replacement)[0].startswith("403"))
    return {
        "schema_version": 1,
        "mode": "offline_in_process_fictional_only",
        "checks": results,
        "passed": all(results.values()),
        "live_provider_connected": False,
        "messages_sent": 0,
        "payments_processed": 0,
        "public_deployment": False,
        "production_ready": False,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    evidence = execute()
    output = json.dumps(evidence, sort_keys=True, indent=2) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
