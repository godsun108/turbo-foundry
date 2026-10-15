"""Fail-closed checkout-to-fulfillment state machine for Foundry.

Offline only; caller cannot prove a real Stripe payment with input strings.
A separately authenticated verified processor must provide PaymentEvidence.
No service dispatch, SMS, mail, invoices, or payment collection.
"""
from dataclasses import dataclass
from enum import Enum


class State(str, Enum):
    DRAFT = "draft"
    SCOPE_ACCEPTED = "scope_accepted"
    CHECKOUT_PENDING = "checkout_pending"
    PAID_AWAITING_ONBOARDING = "paid_awaiting_onboarding"
    ONBOARDING_REVIEW = "onboarding_review"
    READY_FOR_OPERATOR = "ready_for_operator"
    ACTIVE = "active"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class PaymentEvidence:
    """An internal receipt that must be minted ONLY by a verified server webhook."""
    event_id: str
    checkout_session_id: str
    payment_intent_id: str
    amount_cents: int
    currency: str
    paid: bool


@dataclass(frozen=True)
class Order:
    order_id: str
    offer_id: str
    state: State = State.DRAFT
    expected_amount_cents: int = 0
    expected_currency: str = "usd"
    payment_intent_id: str = ""
    onboarding_complete: bool = False
    operational_approval: bool = False


class TransitionError(ValueError):
    pass


def accept_scope(order: Order, *, agreement_accepted: bool) -> Order:
    if order.state != State.DRAFT or agreement_accepted is not True:
        raise TransitionError("explicit agreement required")
    return Order(**{**vars(order), "state": State.SCOPE_ACCEPTED})


def authorize_test_checkout(order: Order, *, checkout_feature_enabled: bool) -> Order:
    if order.state != State.SCOPE_ACCEPTED or checkout_feature_enabled is not True:
        raise TransitionError("checkout disabled without independent approval")
    if order.expected_amount_cents <= 0:
        raise TransitionError("approved total required")
    return Order(**{**vars(order), "state": State.CHECKOUT_PENDING})


def record_verified_payment(order: Order, receipt: PaymentEvidence,
                            *, trusted_webhook: bool) -> Order:
    if trusted_webhook is not True or not isinstance(receipt, PaymentEvidence):
        raise TransitionError("trusted verified webhook required")
    if order.state != State.CHECKOUT_PENDING:
        raise TransitionError("invalid state or duplicate payment")
    if (not receipt.event_id or not receipt.checkout_session_id
            or not receipt.payment_intent_id
            or receipt.paid is not True
            or type(receipt.amount_cents) is not int
            or receipt.amount_cents != order.expected_amount_cents
            or receipt.currency.lower() != order.expected_currency.lower()):
        raise TransitionError("payment evidence does not match order")
    return Order(**{**vars(order),
                    "state": State.PAID_AWAITING_ONBOARDING,
                    "payment_intent_id": receipt.payment_intent_id})


def complete_onboarding(order: Order, *, fields_validated: bool,
                        authorized_customer: bool) -> Order:
    if (order.state != State.PAID_AWAITING_ONBOARDING
            or fields_validated is not True or authorized_customer is not True):
        raise TransitionError("authorized, validated onboarding required")
    return Order(**{**vars(order), "state": State.ONBOARDING_REVIEW,
                    "onboarding_complete": True})


def approve_fulfillment(order: Order, *, release_gate_verified: bool,
                        operator_approved: bool) -> Order:
    if (order.state != State.ONBOARDING_REVIEW
            or release_gate_verified is not True or operator_approved is not True
            or not order.onboarding_complete or not order.payment_intent_id):
        raise TransitionError("payment, onboarding, operator and release gates required")
    return Order(**{**vars(order), "state": State.READY_FOR_OPERATOR,
                    "operational_approval": True})


def activate(order: Order, *, deployment_verified: bool) -> Order:
    if (order.state != State.READY_FOR_OPERATOR
            or deployment_verified is not True or not order.operational_approval):
        raise TransitionError("deployment verification required before activation")
    return Order(**{**vars(order), "state": State.ACTIVE})
