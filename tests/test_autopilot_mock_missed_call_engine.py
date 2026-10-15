"""Evidence for actual mock workflow steps, tenant isolation and fail-safe logic."""
import tempfile
import unittest
from pathlib import Path

from src.autopilot.mock_missed_call_engine import MockMissedCallEngine, WorkflowDenied


class MockEngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = str(Path(self.temp.name)/"events.sqlite")
        self.engine = MockMissedCallEngine(self.path)

    def begin(self, **updates):
        kw=dict(tenant="garage",industry="automotive",event_id="call-1",
                alias="person-1",consent_flag=True,during_hours=True)
        kw.update(updates)
        return self.engine.missed_call(**kw)

    def test_full_mock_reply_lifecycle(self):
        self.assertEqual(self.begin().state,"pending")
        self.assertEqual(self.begin().reason,"duplicate_event")
        self.assertEqual(self.engine.flush_mock(tenant="garage",event_id="call-1",
                          simulate_failure=True).state,"pending")
        self.assertEqual(self.engine.flush_mock(tenant="garage",event_id="call-1").state,
                         "sent_mock")
        self.assertEqual(self.engine.reply(tenant="garage",event_id="call-1",
                         reply_id="reply-1",kind="interested").state,"replied")
        self.assertEqual(MockMissedCallEngine(self.path).status(
            tenant="garage",event_id="call-1").state,"replied")
        with self.assertRaises(WorkflowDenied):
            self.engine.flush_mock(tenant="garage",event_id="call-1")
        with self.assertRaises(WorkflowDenied):
            self.engine.reply(tenant="garage",event_id="call-1",
                              reply_id="reply-1",kind="interested")

    def test_suppression_and_industry_policy(self):
        for values,reason in [
            (dict(event_id="a",consent_flag=False),"no_simulated_permission"),
            (dict(event_id="b",during_hours=False),"outside_simulated_hours"),
        ]:
            self.assertEqual(self.begin(**values).reason,reason)
        with self.assertRaises(WorkflowDenied):
            self.begin(event_id="c",industry="cleaning")
        with self.assertRaises(WorkflowDenied):
            self.begin(event_id="c",alias="+15551230000")

    def test_opt_out_persists_and_blocks_new_events(self):
        self.begin()
        self.engine.flush_mock(tenant="garage",event_id="call-1")
        self.assertEqual(self.engine.reply(tenant="garage",event_id="call-1",
            reply_id="stop-1",kind="stop").state,"stopped")
        self.assertEqual(self.begin(event_id="call-2").reason,"opted_out")
        second=MockMissedCallEngine(self.path)
        self.assertEqual(second.missed_call(tenant="garage",industry="automotive",
            event_id="call-3",alias="person-1",consent_flag=True,
            during_hours=True).reason,"opted_out")

    def test_opt_out_between_queue_and_dispatch(self):
        self.begin(event_id="call-1")
        self.begin(event_id="call-2")
        self.engine.flush_mock(tenant="garage",event_id="call-1")
        self.engine.reply(tenant="garage",event_id="call-1",
                          reply_id="stop-1",kind="stop")
        self.assertEqual(self.engine.flush_mock(tenant="garage",
                         event_id="call-2").reason,"opted_out_before_dispatch")

    def test_tenant_and_duplicate_isolation(self):
        self.begin()
        self.assertIsNone(self.engine.status(tenant="other",event_id="call-1"))
        self.engine.missed_call(tenant="other",industry="hvac",event_id="call-1",
            alias="person-1",consent_flag=True,during_hours=True)
        self.assertEqual(self.engine.status(tenant="other",event_id="call-1").state,
                         "pending")
        self.engine.flush_mock(tenant="other",event_id="call-1")
        self.engine.reply(tenant="other",event_id="call-1",reply_id="r-1",
                          kind="question")
        self.assertEqual(self.engine.status(tenant="other",event_id="call-1").state,
                         "escalated")
        self.assertEqual(self.engine.status(tenant="garage",event_id="call-1").state,
                         "pending")

    def test_no_real_integrations(self):
        for method in ("send_sms","connect_twilio","create_checkout","activate_live"):
            self.assertFalse(hasattr(self.engine,method))


if __name__ == "__main__":
    unittest.main()
