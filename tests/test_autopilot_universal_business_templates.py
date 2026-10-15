"""Universal Business Engine: same core catalog across industries."""
import unittest
from src.autopilot.universal_business_templates import (
    TEMPLATES, ALLOWED_AUTOMATIONS, configure_business, get_template,
)
from src.autopilot.commercial_catalog import OFFERS


class UniversalBusinessTemplatesTests(unittest.TestCase):
    def test_every_template_uses_existing_common_catalog(self):
        known = {offer.slug for offer in OFFERS}
        self.assertEqual(len({item.slug for item in TEMPLATES}), len(TEMPLATES))
        self.assertGreaterEqual(len(TEMPLATES), 5)
        for item in TEMPLATES:
            self.assertEqual(item.status, "discovery_only")
            self.assertTrue(item.qualifying_question)
            self.assertTrue(item.operational_notes)
            self.assertTrue(set(item.example_workflows) <= known)
            self.assertTrue(set(item.example_workflows) <= ALLOWED_AUTOMATIONS)

    def test_industries_reuse_identical_automation_contract(self):
        first = configure_business("shop-1", "automotive")
        second = configure_business("shop-2", "hvac")
        self.assertEqual(first.status, "discovery_only")
        self.assertEqual(second.status, "discovery_only")
        self.assertIn("missed-call-recovery", first.workflows)
        self.assertIn("missed-call-recovery", second.workflows)
        self.assertNotEqual(first.profile_id, second.profile_id)

    def test_selection_is_per_business_not_a_new_engine(self):
        p = configure_business("landscape-1", "landscaping",
                               ("lead-intake",))
        self.assertEqual(p.workflows, ("lead-intake",))
        self.assertEqual(p.template_slug, "landscaping")

    def test_invalid_or_unsafe_profiles_fail_closed(self):
        cases = (
            ("bad space", "hvac", None),
            ("good", "nonexistent", None),
            ("good", "hvac", ()),
            ("good", "hvac", ("send-sms",)),
            ("good", "automotive", ("lead-intake", "lead-intake")),
            ("good", "landscaping", ("missed-call-recovery",)),
            ("good", "hvac", ["lead-intake"]),
        )
        for profile_id, template, workflows in cases:
            with self.subTest(case=(profile_id, template, workflows)):
                with self.assertRaises(ValueError):
                    configure_business(profile_id, template, workflows)
        with self.assertRaises(ValueError):
            get_template("unknown")

    def test_no_activation_or_payment_fields(self):
        profile = configure_business("client-test", "general")
        self.assertFalse(hasattr(profile, "enabled"))
        self.assertFalse(hasattr(profile, "payment_method"))
        self.assertFalse(hasattr(profile, "credentials"))


if __name__ == "__main__":
    unittest.main()
