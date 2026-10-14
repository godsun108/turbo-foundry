"""No-network pilot economics: assumptions are never represented as sales."""
import unittest
from decimal import Decimal
from src.autopilot.pilot_economics import estimate_pilot


class PilotEconomicsTests(unittest.TestCase):
    def test_conservative_booking_and_cost_arithmetic(self):
        result = estimate_pilot(
            missed_calls_per_month=100, eligible_fraction="0.75",
            booking_conversion_fraction="0.20",
            gross_margin_per_booking="120", service_price_per_month="299",
            provider_cost_per_eligible_call="0.10",
            fixed_provider_cost_per_month="30",
        )
        self.assertEqual(result.eligible_missed_calls, 75)
        self.assertEqual(result.recovered_bookings, 15)
        self.assertEqual(result.gross_margin, Decimal("1800"))
        self.assertEqual(result.customer_net_before_other_costs, Decimal("1501.00"))
        self.assertEqual(result.monthly_provider_cost, Decimal("37.50"))
        self.assertEqual(result.provider_gross_contribution, Decimal("261.50"))
        self.assertEqual(result.customer_break_even_bookings, 3)

    def test_zero_eligibility_has_no_implied_revenue(self):
        result = estimate_pilot(
            missed_calls_per_month=100, eligible_fraction=0,
            booking_conversion_fraction=1, gross_margin_per_booking=200,
            service_price_per_month=200, provider_cost_per_eligible_call=0,
        )
        self.assertEqual(result.recovered_bookings, 0)
        self.assertEqual(result.customer_net_before_other_costs, Decimal("-200.00"))

    def test_small_fraction_rounds_down_not_up(self):
        result = estimate_pilot(
            missed_calls_per_month=9, eligible_fraction="0.5",
            booking_conversion_fraction="0.5", gross_margin_per_booking=30,
            service_price_per_month=20, provider_cost_per_eligible_call="0.01",
        )
        self.assertEqual((result.eligible_missed_calls, result.recovered_bookings), (4, 2))

    def test_zero_margin_does_not_claim_break_even(self):
        result = estimate_pilot(
            missed_calls_per_month=10, eligible_fraction=1,
            booking_conversion_fraction=1, gross_margin_per_booking=0,
            service_price_per_month=100, provider_cost_per_eligible_call=0,
        )
        self.assertEqual(result.customer_break_even_bookings, -1)

    def test_rejects_invalid_inputs(self):
        base = dict(missed_calls_per_month=100, eligible_fraction="0.5",
                    booking_conversion_fraction="0.2",
                    gross_margin_per_booking=100, service_price_per_month=100,
                    provider_cost_per_eligible_call="0.05")
        for override in (
            {"missed_calls_per_month": True},
            {"missed_calls_per_month": -1},
            {"eligible_fraction": 1.2},
            {"booking_conversion_fraction": "-0.01"},
            {"gross_margin_per_booking": float("nan")},
            {"service_price_per_month": "-1"},
            {"provider_cost_per_eligible_call": "Infinity"},
        ):
            with self.subTest(override=override), self.assertRaises(ValueError):
                estimate_pilot(**(base | override))


if __name__ == "__main__":
    unittest.main()
