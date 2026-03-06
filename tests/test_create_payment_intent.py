"""
Tests for POST /v1/payment_intents — Create a Payment Intent.
"""
import pytest
from utils.schemas import PAYMENT_INTENT_SCHEMA
from utils.validators import assert_valid_iso_currency, validate_schema


@pytest.mark.payment_intents
class TestCreatePaymentIntent:
    """Validate PaymentIntent creation via the Stripe API."""

    def test_create_payment_intent_status_200(self, stripe):
        """Creating a PaymentIntent should return HTTP 200."""
        resp = stripe.create_payment_intent(
            amount=1500,
            currency="usd",
            **{"payment_method_types[]": "card"},
        )
        assert resp.status_code == 200

    def test_payment_intent_initial_status(self, payment_intent):
        """New PaymentIntent status should be 'requires_payment_method' or 'requires_confirmation'."""
        valid_statuses = {"requires_payment_method", "requires_confirmation"}
        assert payment_intent["status"] in valid_statuses, (
            f"Unexpected status: {payment_intent['status']}"
        )

    def test_payment_intent_amount_is_integer(self, payment_intent):
        """Amount must be an integer (minor units / cents)."""
        assert isinstance(payment_intent["amount"], int)
        assert payment_intent["amount"] > 0

    def test_payment_intent_currency_is_iso3(self, payment_intent):
        """Currency must be a 3-letter lowercase ISO code."""
        assert_valid_iso_currency(payment_intent["currency"])

    def test_payment_intent_response_schema(self, payment_intent):
        """Full JSON-schema validation."""
        validate_schema(payment_intent, PAYMENT_INTENT_SCHEMA)

    def test_payment_intent_id_prefix(self, payment_intent):
        """PaymentIntent ID should start with 'pi_'."""
        assert payment_intent["id"].startswith("pi_")

    def test_payment_intent_receipt_email(self, payment_intent):
        """The receipt_email field should echo what was sent."""
        assert payment_intent["receipt_email"] == "receipt@example.com"

    def test_payment_intent_livemode_false(self, payment_intent):
        """Test-mode PaymentIntents must have livemode=false."""
        assert payment_intent["livemode"] is False

    def test_payment_intent_with_metadata(self, stripe):
        """Metadata passed at creation should persist."""
        resp = stripe.create_payment_intent(
            amount=999,
            currency="eur",
            **{
                "payment_method_types[]": "card",
                "metadata[order_id]": "ORD-12345",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"]["order_id"] == "ORD-12345"
