"""The sales catalog never represents concept products as live."""
import unittest
from src.autopilot.commercial_catalog import (
    OFFERS, AutomationOffer, can_claim_live, public_offers,
)


class CommercialCatalogTests(unittest.TestCase):
    def test_unique_ids_and_complete_discovery_fields(self):
        self.assertEqual(len({offer.slug for offer in OFFERS}), len(OFFERS))
        for offer in OFFERS:
            for field in ("title", "buyer", "problem", "proposed_outcome",
                          "qualifying_question", "proof_required"):
                self.assertTrue(getattr(offer, field).strip())

    def test_concept_products_not_in_default_public_catalog(self):
        self.assertEqual([x.slug for x in public_offers()],
                         ["missed-call-recovery"])
        self.assertEqual(len(public_offers(include_concepts=True)), 5)

    def test_no_unverified_product_claimed_live(self):
        self.assertFalse(any(can_claim_live(x) for x in OFFERS))
        self.assertTrue(can_claim_live(
            AutomationOffer("live", "Live", "Buyer", "Problem", "Outcome",
                            "Question?", "Proof", "validated_live")))
        self.assertFalse(can_claim_live(OFFERS[0]))


if __name__ == "__main__":
    unittest.main()
