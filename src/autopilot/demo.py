"""Deterministic offline product demo; no calls, SMS, or customer data."""
import json
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from .missed_call import MissedCall, Policy
from .queue import MessageQueue
from .service import process_missed_call

def run_demo() -> dict:
    now = datetime(2026, 10, 13, 15, tzinfo=timezone.utc)
    policy = Policy("demo-shop", "America/New_York", "+15551234567")
    with tempfile.TemporaryDirectory() as directory:
        queue = MessageQueue(str(Path(directory) / "demo.sqlite"))
        def event(event_id, caller, *, consent=True, opted_out=False):
            return MissedCall(event_id, "demo-shop", caller, policy.approved_number,
                              now, True, consent, opted_out=opted_out)
        examples = [
            ("consented_missed_call", event("call-1", "+15557654321")),
            ("duplicate_callback", event("call-1", "+15557654321")),
            ("no_consent", event("call-2", "+15557654322", consent=False)),
            ("opted_out", event("call-3", "+15557654323", opted_out=True)),
            ("second_eligible_call", event("call-4", "+15557654324")),
        ]
        results = []
        for label, call in examples:
            decision = process_missed_call(call, policy, queue, now)
            results.append({"scenario": label, "status": decision.status, "reason": decision.reason})
        return {
            "mode": "offline_simulation",
            "actual_messages_sent": 0,
            "real_leads_recovered": 0,
            "revenue_generated_usd": 0,
            "scenarios": len(results),
            "simulated_messages": sum(item["status"] == "simulated" for item in results),
            "rejected_events": sum(item["status"] == "rejected" for item in results),
            "results": results,
        }

if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
