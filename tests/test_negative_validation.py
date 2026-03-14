"""
Negative & Input Validation Tests.

Covers:
- Missing / invalid fields
- Invalid currency
- Stripe test-card declines
- Invalid state transitions
"""
import pytest
from utils.config import TEST_CARDS
from utils.schemas import STRIPE_ERROR_SCHEMA
from utils.validators import validate_schema


@pytest.mark.negative
class TestCustomerNegativeCases:
    """Negative tests for the Customer API."""

    def test_create_customer_missing_email_still_succeeds(self, stripe):
        """Stripe allows creating a customer without an email (email is optional)."""
        resp = stripe.create_customer(name="No Email User")
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] is None
        stripe.delete_customer(data["id"])

    def test_create_customer_invalid_email_format(self, stripe):
        """Stripe does NOT reject malformed emails server-side — verify behavior."""
        resp = stripe.create_customer(
            name="Bad Email",
            email="not-an-email",
        )
        # Stripe accepts free-form email; validate we document this behavior
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "not-an-email"
        stripe.delete_customer(data["id"])

    def test_create_customer_empty_name(self, stripe):
        """Name is optional; an empty string should be accepted."""
        resp = stripe.create_customer(name="", email="empty@name.com")
        assert resp.status_code == 200
        data = resp.json()
        stripe.delete_customer(data["id"])


@pytest.mark.negative
class TestPaymentIntentNegativeCases:
    """Negative tests for the PaymentIntent API."""

    def test_create_intent_invalid_currency(self, stripe):
        """An invalid / unknown currency code should return 400."""
        resp = stripe.create_payment_intent(
            amount=1000,
            currency="zzz",
            **{"payment_method_types[]": "card"},
        )
        assert resp.status_code == 400
        data = resp.json()
        validate_schema(data, STRIPE_ERROR_SCHEMA)
        assert data["error"]["type"] == "invalid_request_error"

    def test_create_intent_zero_amount(self, stripe):
        """Amount=0 should be rejected (must be >= 50 for USD)."""
        resp = stripe.create_payment_intent(
            amount=0,
            currency="usd",
            **{"payment_method_types[]": "card"},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data

    def test_create_intent_negative_amount(self, stripe):
        """A negative amount should be rejected."""
        resp = stripe.create_payment_intent(
            amount=-500,
            currency="usd",
            **{"payment_method_types[]": "card"},
        )
        assert resp.status_code == 400

    def test_create_intent_missing_amount(self, stripe):
        """Omitting the amount field should return 400."""
        resp = stripe.create_payment_intent(
            currency="usd",
            **{"payment_method_types[]": "card"},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data

    def test_create_intent_missing_currency(self, stripe):
        """Omitting currency should return 400."""
        resp = stripe.create_payment_intent(
            amount=1000,
            **{"payment_method_types[]": "card"},
        )
        assert resp.status_code == 400

    def test_confirm_without_payment_method(self, stripe, payment_intent):
        """Confirming without providing a payment_method should fail."""
        resp = stripe.confirm_payment_intent(payment_intent["id"])
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data


@pytest.mark.negative
class TestStripeDeclineSimulation:
    """Use Stripe test card tokens to simulate declines and errors."""

    @pytest.mark.parametrize(
        "card_token, expected_decline_code",
        [
            (TEST_CARDS["declined_generic"], "card_declined"),
            (TEST_CARDS["declined_insufficient"], "card_declined"),
            (TEST_CARDS["declined_expired"], "card_declined"),
            (TEST_CARDS["declined_cvc"], "card_declined"),
        ],
        ids=["generic_decline", "insufficient_funds", "expired_card", "incorrect_cvc"],
    )
    def test_declined_card(self, stripe, card_token, expected_decline_code):
        """Attempting to pay with a declined test card should yield an error."""
        resp = stripe.create_payment_intent(
            amount=2000,
            currency="usd",
            confirm=True,
            payment_method=card_token,
            **{"payment_method_types[]": "card"},
        )
        # Stripe returns 402 for card errors
        assert resp.status_code == 402, (
            f"Expected 402 for declined card, got {resp.status_code}"
        )
        data = resp.json()
        assert data["error"]["type"] == "card_error"
        assert data["error"]["code"] == expected_decline_code

    def test_processing_error_card(self, stripe):
        """The processing-error test card should trigger a card_error."""
        resp = stripe.create_payment_intent(
            amount=2000,
            currency="usd",
            confirm=True,
            payment_method=TEST_CARDS["declined_processing"],
            **{"payment_method_types[]": "card"},
        )
        assert resp.status_code == 402
        data = resp.json()
        assert data["error"]["type"] == "card_error"

    def test_double_capture_fails(self, stripe):
        """Capturing an already-captured PaymentIntent should fail."""
        # Create + confirm with manual capture
        create_resp = stripe.create_payment_intent(
            amount=3000,
            currency="usd",
            capture_method="manual",
            **{"payment_method_types[]": "card"},
        )
        pi = create_resp.json()
        stripe.confirm_payment_intent(
            pi["id"], payment_method=TEST_CARDS["visa_success"]
        )
        # First capture
        first = stripe.capture_payment_intent(pi["id"])
        assert first.status_code == 200

        # Second capture should fail
        second = stripe.capture_payment_intent(pi["id"])
        assert second.status_code == 400
        assert "error" in second.json()
