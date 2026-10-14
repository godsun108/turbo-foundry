"""Offline SDK compatibility and worker fencing integration tests."""
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.autopilot.synthetic_provider_sdk import SyntheticTwilioClient
from src.autopilot.twilio_paging import TwilioCallPager
from src.autopilot.recheck_queue import RecheckQueue
from src.autopilot.recheck_leases import RecheckLeases
from src.autopilot.recheck_worker import run_recheck
from src.autopilot.worker_control import WorkerControl
from src.autopilot.observation_store import ObservationStore

ACCOUNT = "AC" + "a" * 32
OTHER_ACCOUNT = "AC" + "e" * 32
PARENT = "CA" + "b" * 32
OTHER_PARENT = "CA" + "f" * 32
CHILD_A = "CA" + "c" * 32
CHILD_B = "CA" + "d" * 32
NOW = datetime(2026, 10, 14, 16, tzinfo=timezone.utc)


class SyntheticProviderTests(unittest.TestCase):
    def test_multpage_complete_with_account_binding(self):
        sdk = SyntheticTwilioClient(ACCOUNT, {PARENT: (CHILD_A, CHILD_B)})
        result = TwilioCallPager(sdk, ACCOUNT).enumerate_all(PARENT, page_size=1)
        self.assertTrue(result.complete)
        self.assertEqual(result.reason, "sdk_page_exhaustion")
        self.assertEqual(result.pages_checked, 2)
        self.assertEqual(result.child_sids, (CHILD_A, CHILD_B))
        self.assertEqual(sdk.page_requests, 2)

    def test_cross_account_and_unknown_parent_fail_closed(self):
        sdk = SyntheticTwilioClient(ACCOUNT, {PARENT: (CHILD_A,)})
        mismatched = TwilioCallPager(sdk, OTHER_ACCOUNT).enumerate_all(PARENT)
        self.assertFalse(mismatched.complete)
        self.assertEqual(mismatched.reason, "account_mismatch")
        unknown = TwilioCallPager(sdk, ACCOUNT).enumerate_all(OTHER_PARENT)
        self.assertFalse(unknown.complete)
        self.assertEqual(unknown.reason, "provider_error")

    def test_outage_and_rate_limit_not_treated_as_exhaustion(self):
        for status, reason in ((503, "provider_temporarily_unavailable"),
                               (429, "provider_rate_limited"),
                               (403, "provider_auth_failed")):
            with self.subTest(status=status):
                sdk = SyntheticTwilioClient(
                    ACCOUNT, {PARENT: (CHILD_A, CHILD_B,)},
                    fail_page=2, fail_status=status)
                result = TwilioCallPager(sdk, ACCOUNT).enumerate_all(
                    PARENT, page_size=1)
                self.assertFalse(result.complete)
                self.assertEqual(result.reason, reason)
                self.assertEqual(sdk.page_requests, 2)

    def test_bounds_and_fixture_validation(self):
        with self.assertRaises(ValueError):
            SyntheticTwilioClient(ACCOUNT, {PARENT: (PARENT,)})
        with self.assertRaises(ValueError):
            SyntheticTwilioClient(ACCOUNT, {PARENT: (CHILD_A, CHILD_A)})
        with self.assertRaises(ValueError):
            SyntheticTwilioClient(ACCOUNT, {PARENT: [CHILD_A]})
        sdk = SyntheticTwilioClient(ACCOUNT, {PARENT: (CHILD_A, CHILD_B)})
        result = TwilioCallPager(sdk, ACCOUNT).enumerate_all(
            PARENT, page_size=1, max_pages=1)
        self.assertEqual(result.reason, "page_limit_exceeded")

    def test_offline_worker_records_review_only_then_stop_blocks_sdk(self):
        with tempfile.TemporaryDirectory() as folder:
            db = str(Path(folder) / "rehearsal.db")
            RecheckQueue(db).schedule("synthetic-tenant", PARENT, now=NOW)
            RecheckLeases(db)
            store = ObservationStore(db)
            control = WorkerControl(db)
            sdk = SyntheticTwilioClient(ACCOUNT, {PARENT: (CHILD_A, CHILD_B)})
            pager = TwilioCallPager(sdk, ACCOUNT)
            control.set_enabled(True, actor="synthetic-test", reason="offline rehearsal", now=NOW)
            first = run_recheck(db, "synthetic-tenant", PARENT,
                                now=NOW, call_ended_at=NOW - timedelta(minutes=20),
                                pager=pager, clock=lambda: NOW, enabled=True,
                                control=control)
            self.assertTrue(first.recorded)
            self.assertFalse(first.settled_for_review)
            self.assertEqual(sdk.page_requests, 1)
            self.assertEqual(len(store.load("synthetic-tenant", PARENT)), 1)
            control.set_enabled(False, actor="synthetic-test", reason="offline stop", now=NOW)
            later = NOW + timedelta(minutes=3)
            blocked = run_recheck(db, "synthetic-tenant", PARENT,
                                  now=later, call_ended_at=NOW - timedelta(minutes=20),
                                  pager=pager, clock=lambda: later, enabled=True,
                                  control=WorkerControl(db))
            self.assertEqual(blocked.reason, "worker_disabled")
            self.assertEqual(sdk.page_requests, 1)
            self.assertEqual(len(store.load("synthetic-tenant", PARENT)), 1)

    def test_rate_limited_worker_retries_without_observation(self):
        with tempfile.TemporaryDirectory() as folder:
            db = str(Path(folder) / "rehearsal.db")
            RecheckQueue(db).schedule("synthetic-tenant", PARENT, now=NOW)
            RecheckLeases(db)
            store = ObservationStore(db)
            control = WorkerControl(db)
            sdk = SyntheticTwilioClient(ACCOUNT, {PARENT: (CHILD_A,)},
                                        fail_page=1, fail_status=429)
            control.set_enabled(True)
            result = run_recheck(
                db, "synthetic-tenant", PARENT, now=NOW,
                call_ended_at=NOW - timedelta(minutes=20),
                pager=TwilioCallPager(sdk, ACCOUNT), clock=lambda: NOW,
                enabled=True, control=control)
            self.assertFalse(result.recorded)
            self.assertEqual(result.reason, "provider_rate_limited")
            self.assertEqual(len(store.load("synthetic-tenant", PARENT)), 0)


if __name__ == "__main__":
    unittest.main()
