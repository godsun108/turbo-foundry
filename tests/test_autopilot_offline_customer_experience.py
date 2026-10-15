"""Offline customer experience quality and safety regressions."""
import unittest

from src.autopilot.offline_customer_experience import OfflineCustomerExperience


class CustomerExperienceTests(unittest.TestCase):
    def setUp(self):
        self.engine=OfflineCustomerExperience()

    def ask(self, message, tenant="garage", session="fictional1", industry="automotive", facts=None):
        return self.engine.respond(tenant=tenant,industry=industry,session=session,
                                   message=message,verified_facts=facts)

    def test_truthful_pricing_and_scheduling(self):
        result=self.ask("How much is a brake repair?",facts={"business_name":"Example Garage"})
        self.assertEqual(result.intent,"quote")
        self.assertIn("cannot verify a price",result.message)
        result=self.ask("Can I book tomorrow?")
        self.assertEqual(result.intent,"appointment")
        self.assertIn("cannot see live availability",result.message)
        self.assertFalse(result.verified_booking)
        self.assertFalse(result.real_message_sent)

    def test_urgent_escalation_overrides_booking(self):
        result=self.ask("Can you book me today? There are sparks and smoke",
                        industry="plumbing",session="urgent1")
        self.assertEqual(result.intent,"urgent")
        self.assertEqual(result.disposition,"human_escalation")
        self.assertIn("emergency services",result.message)

    def test_human_and_stop(self):
        self.assertEqual(self.ask("I need a human").intent,"human")
        self.assertEqual(self.ask("STOP").disposition,"closed")
        self.assertEqual(self.ask("book a visit").disposition,"closed")

    def test_tenant_isolation_and_industry_lock(self):
        self.ask("stop")
        self.assertNotEqual(self.ask("book",tenant="other").disposition,"closed")
        with self.assertRaises(ValueError):
            self.ask("hello",industry="hvac")
        self.assertEqual(self.engine.session_status(tenant="garage",session="fictional1")["turns"],1)

    def test_verified_facts_only(self):
        result=self.ask("Hello",facts={"business_name":"Example Garage","services":"Brake inspections"})
        self.assertIn("Brake inspections",result.message)
        with self.assertRaises(ValueError):
            self.ask("Hello",session="another",facts={"price":"$25"})
        with self.assertRaises(ValueError):
            self.ask("Hello",session="another",facts={"secret":"hidden"})

    def test_all_templates_supported(self):
        for industry in ("automotive","hvac","plumbing","landscaping","cleaning","general"):
            result=self.ask("I need an estimate",session=industry,industry=industry)
            self.assertEqual(result.intent,"quote")


if __name__=="__main__":
    unittest.main()
