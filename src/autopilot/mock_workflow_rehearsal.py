"""Reproducible end-to-end fictional Foundry automation run.

No provider SDK, network calls, payments, phone numbers or real customers.
"""
import json
import tempfile
from pathlib import Path

from .mock_missed_call_engine import MockMissedCallEngine


def execute():
    with tempfile.TemporaryDirectory() as tmp:
        engine=MockMissedCallEngine(str(Path(tmp)/"workflow.sqlite"))
        start=engine.missed_call(
            tenant="fictional-shop",industry="automotive",
            event_id="call-fixture-001",alias="fictional-person-001",
            consent_flag=True,during_hours=True)
        duplicate=engine.missed_call(
            tenant="fictional-shop",industry="automotive",
            event_id="call-fixture-001",alias="fictional-person-001",
            consent_flag=True,during_hours=True)
        failed=engine.flush_mock(tenant="fictional-shop",
                                 event_id="call-fixture-001",simulate_failure=True)
        sent=engine.flush_mock(tenant="fictional-shop",event_id="call-fixture-001")
        stop=engine.reply(tenant="fictional-shop",event_id="call-fixture-001",
                          reply_id="reply-fixture-stop",kind="stop")
        suppressed=engine.missed_call(
            tenant="fictional-shop",industry="automotive",
            event_id="call-fixture-002",alias="fictional-person-001",
            consent_flag=True,during_hours=True)
        persisted=MockMissedCallEngine(engine.db_path).status(
            tenant="fictional-shop",event_id="call-fixture-001")
        checks={
            "eligibility_queued":start.state=="pending",
            "duplicate_idempotent":duplicate.reason=="duplicate_event",
            "mock_failure_preserves_queue":failed.state=="pending",
            "mock_delivery_recorded":sent.state=="sent_mock",
            "stop_acknowledged":stop.state=="stopped",
            "optout_suppresses_future_events":suppressed.reason=="opted_out",
            "state_persists_across_restart":persisted.state=="stopped",
        }
        return {"mode":"fictional_local_sqlite_only","passed":all(checks.values()),
                "checks":checks,"network_requests":0,"messages_sent":0,
                "real_payments_processed":0,"production_ready":False}


def main():
    evidence = execute()
    print(json.dumps(evidence,indent=2,sort_keys=True))
    return 0 if evidence["passed"] else 1


if __name__=="__main__":
    raise SystemExit(main())
