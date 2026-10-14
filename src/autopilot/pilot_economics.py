"""Conservative, offline pilot economics estimates.

Scenario arithmetic only. Not measured demand, attributable revenue, or
permission to send messages or issue invoices.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


@dataclass(frozen=True)
class PilotEstimate:
    eligible_missed_calls: int
    recovered_bookings: int
    gross_margin: Decimal
    monthly_provider_cost: Decimal
    monthly_service_price: Decimal
    customer_net_before_other_costs: Decimal
    customer_break_even_bookings: int
    provider_gross_contribution: Decimal


def _money(value, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"{name} must be numeric") from None
    if not amount.is_finite() or amount < 0:
        raise ValueError(f"{name} must be a nonnegative finite amount")
    return amount


def estimate_pilot(*, missed_calls_per_month: int, eligible_fraction,
                   booking_conversion_fraction, gross_margin_per_booking,
                   service_price_per_month, provider_cost_per_eligible_call,
                   fixed_provider_cost_per_month=0) -> PilotEstimate:
    """Scenario-only estimate with conservative whole-event rounding down.

    Gross margin per booking must exclude delivery costs already separately
    accounted for; no implied actual customer conversions or sales.
    """
    if type(missed_calls_per_month) is not int or not 0 <= missed_calls_per_month <= 1_000_000:
        raise ValueError("missed_calls_per_month must be a bounded integer")
    eligible_fraction = _money(eligible_fraction, "eligible_fraction")
    booking_conversion_fraction = _money(booking_conversion_fraction, "booking_conversion_fraction")
    if eligible_fraction > 1 or booking_conversion_fraction > 1:
        raise ValueError("fractions must be between zero and one")
    margin = _money(gross_margin_per_booking, "gross_margin_per_booking")
    price = _money(service_price_per_month, "service_price_per_month")
    variable = _money(provider_cost_per_eligible_call, "provider_cost_per_eligible_call")
    fixed = _money(fixed_provider_cost_per_month, "fixed_provider_cost_per_month")
    eligible = int(Decimal(missed_calls_per_month) * eligible_fraction)
    bookings = int(Decimal(eligible) * booking_conversion_fraction)
    customer_value = bookings * margin
    delivery = (fixed + eligible * variable).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    customer_net = (customer_value - price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    contribution = (price - delivery).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    threshold = 0 if price == 0 else (
        int((price / margin).to_integral_value(rounding="ROUND_CEILING"))
        if margin > 0 else -1
    )
    return PilotEstimate(eligible, bookings, customer_value, delivery, price,
                         customer_net, threshold, contribution)
