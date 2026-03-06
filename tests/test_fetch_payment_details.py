"""
Tests for GET /v1/payment_intents/{id} — Fetch Payment Details.
"""
import time
import pytest
from utils.config import TEST_CARDS


@pytest.mark.payment_intents
class TestFetchPaymentDetails:
    """Validate fetching PaymentIntent details from the Stripe API."""

    def test_fetch_payment_intent_returns_200(self, stripe, payment_intent):
        """GETting a known PaymentIntent should return 200."""
        resp = stripe.get_payment_intent(payment_intent["id"])
        assert resp.status_code == 200

    def test_fetch_payment_intent_fields_match(self, stripe, payment_intent):
        """Fetched data should match what was created."""
        resp = stripe.get_payment_intent(payment_intent["id"])
        data = resp.json()
        assert data["id"] == payment_intent["id"]
        assert data["amount"] == payment_intent["amount"]
        assert data["currency"] == payment_intent["currency"]

    def test_fetch_nonexistent_payment_intent(self, stripe):
        """Fetching a non-existing PaymentIntent should return 404."""
        resp = stripe.get_payment_intent("pi_nonexistent000000")
        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data

    # -- Status transitions -----------------------------------------------

    def test_status_transition_created_to_succeeded(self, stripe):
        """Track a PaymentIntent through created → confirmed → succeeded."""
        # Step 1 — Create
        create_resp = stripe.create_payment_intent(
            amount=4000,
            currency="usd",
            **{"payment_method_types[]": "card"},
        )
        assert create_resp.status_code == 200
        pi = create_resp.json()
        assert pi["status"] == "requires_payment_method"

        # Step 2 — Confirm (auto capture)
        confirm_resp = stripe.confirm_payment_intent(
            pi["id"], payment_method=TEST_CARDS["visa_success"]
        )
        assert confirm_resp.status_code == 200
        confirmed = confirm_resp.json()
        assert confirmed["status"] == "succeeded"

        # Step 3 — Fetch and verify
        fetch_resp = stripe.get_payment_intent(pi["id"])
        fetched = fetch_resp.json()
        assert fetched["status"] == "succeeded"
        assert fetched["amount_received"] == 4000

    def test_verify_captured_amount(self, stripe, succeeded_payment_intent):
        """After auto-capture, amount_received should equal amount."""
        resp = stripe.get_payment_intent(succeeded_payment_intent["id"])
        data = resp.json()
        assert data["amount_received"] == data["amount"]

    def test_verify_created_timestamp(self, stripe, payment_intent):
        """The 'created' timestamp should be a reasonable epoch value."""
        resp = stripe.get_payment_intent(payment_intent["id"])
        data = resp.json()
        now = int(time.time())
        # Created within the last 60 seconds
        assert now - data["created"] < 60, (
            f"Timestamp too old: {data['created']} vs now={now}"
        )

    def test_manual_capture_status_transition(self, stripe):
        """Manual capture: created → requires_capture → succeeded."""
        # Create
        resp = stripe.create_payment_intent(
            amount=7500,
            currency="usd",
            capture_method="manual",
            **{"payment_method_types[]": "card"},
        )
        pi = resp.json()
        assert pi["status"] == "requires_payment_method"

        # Confirm
        confirm_resp = stripe.confirm_payment_intent(
            pi["id"], payment_method=TEST_CARDS["visa_success"]
        )
        confirmed = confirm_resp.json()
        assert confirmed["status"] == "requires_capture"

        # Capture
        capture_resp = stripe.capture_payment_intent(pi["id"])
        captured = capture_resp.json()
        assert captured["status"] == "succeeded"
        assert captured["amount_received"] == 7500
