"""
Tests for POST /v1/payment_intents/{id}/confirm and /capture — Confirm & Capture Payment.
"""
import pytest
from utils.config import TEST_CARDS


@pytest.mark.payment_intents
class TestConfirmAndCapturePayment:
    """Validate the confirm and capture lifecycle of a PaymentIntent."""

    # -- Confirm -----------------------------------------------------------

    def test_confirm_payment_intent_succeeds(self, stripe, payment_intent):
        """Confirming with a valid test card should succeed."""
        resp = stripe.confirm_payment_intent(
            payment_intent["id"],
            payment_method=TEST_CARDS["visa_success"],
        )
        assert resp.status_code == 200
        data = resp.json()
        # With automatic capture the status goes straight to 'succeeded'
        assert data["status"] == "succeeded"

    def test_confirm_sets_payment_method(self, stripe, payment_intent):
        """After confirm, payment_method should be populated."""
        resp = stripe.confirm_payment_intent(
            payment_intent["id"],
            payment_method=TEST_CARDS["visa_success"],
        )
        data = resp.json()
        assert data["payment_method"] is not None

    # -- Manual Capture ----------------------------------------------------

    def test_manual_capture_flow(self, stripe, confirmed_payment_intent):
        """Capture a previously confirmed manual-capture PaymentIntent."""
        assert confirmed_payment_intent["status"] == "requires_capture"
        resp = stripe.capture_payment_intent(confirmed_payment_intent["id"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "succeeded"
        assert data["amount_received"] == confirmed_payment_intent["amount"]

    def test_capture_before_confirm_fails(self, stripe, payment_intent):
        """Attempting to capture before confirming should fail."""
        resp = stripe.capture_payment_intent(payment_intent["id"])
        # Stripe returns 400 for this invalid transition
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data

    def test_capture_partial_amount(self, stripe, manual_capture_payment_intent):
        """Capture with a smaller amount_to_capture should succeed."""
        pi_id = manual_capture_payment_intent["id"]
        # First confirm
        confirm_resp = stripe.confirm_payment_intent(
            pi_id, payment_method=TEST_CARDS["visa_success"]
        )
        assert confirm_resp.status_code == 200
        assert confirm_resp.json()["status"] == "requires_capture"

        # Capture partial amount (half)
        partial = manual_capture_payment_intent["amount"] // 2
        capture_resp = stripe.capture_payment_intent(
            pi_id, amount_to_capture=partial
        )
        assert capture_resp.status_code == 200
        data = capture_resp.json()
        assert data["status"] == "succeeded"
        assert data["amount_received"] == partial

    def test_capture_more_than_authorized_fails(self, stripe, manual_capture_payment_intent):
        """Capturing more than the authorized amount should return an error."""
        pi_id = manual_capture_payment_intent["id"]
        # Confirm first
        stripe.confirm_payment_intent(
            pi_id, payment_method=TEST_CARDS["visa_success"]
        )
        # Try capturing more than authorized
        over_amount = manual_capture_payment_intent["amount"] + 5000
        resp = stripe.capture_payment_intent(pi_id, amount_to_capture=over_amount)
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data
