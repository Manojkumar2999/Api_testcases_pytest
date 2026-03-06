"""
Shared PyTest fixtures for the Stripe API test suite.
"""
import pytest
from utils.api_client import StripeClient
from utils.config import STRIPE_SECRET_KEY, TEST_CARDS


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def stripe():
    """Return a configured :class:`StripeClient` instance for the whole session."""
    assert STRIPE_SECRET_KEY.startswith("sk_test_"), (
        "STRIPE_TEST_SECRET_KEY must be a Stripe test-mode secret key "
        "(starts with sk_test_). Set it in a .env file or as an env var."
    )
    return StripeClient()


# ---------------------------------------------------------------------------
# Function-scoped fixtures (create → yield → cleanup)
# ---------------------------------------------------------------------------

@pytest.fixture()
def customer(stripe):
    """Create a test customer and delete it after the test."""
    resp = stripe.create_customer(
        name="Test User",
        email="testuser@example.com",
        phone="+14155551234",
    )
    assert resp.status_code == 200, f"Customer creation failed: {resp.text}"
    data = resp.json()
    yield data
    # Cleanup
    stripe.delete_customer(data["id"])


@pytest.fixture()
def payment_intent(stripe):
    """Create a PaymentIntent (auto-capture) with a Visa test card attached."""
    resp = stripe.create_payment_intent(
        amount=2000,
        currency="usd",
        receipt_email="receipt@example.com",
        **{"payment_method_types[]": "card"},
    )
    assert resp.status_code == 200, f"PaymentIntent creation failed: {resp.text}"
    yield resp.json()


@pytest.fixture()
def manual_capture_payment_intent(stripe):
    """Create a PaymentIntent with capture_method=manual."""
    resp = stripe.create_payment_intent(
        amount=5000,
        currency="usd",
        capture_method="manual",
        **{"payment_method_types[]": "card"},
    )
    assert resp.status_code == 200, f"PaymentIntent creation failed: {resp.text}"
    yield resp.json()


@pytest.fixture()
def confirmed_payment_intent(stripe, manual_capture_payment_intent):
    """Return a PaymentIntent that has been confirmed (status=requires_capture)."""
    pi_id = manual_capture_payment_intent["id"]
    resp = stripe.confirm_payment_intent(
        pi_id,
        payment_method=TEST_CARDS["visa_success"],
    )
    assert resp.status_code == 200, f"Confirm failed: {resp.text}"
    yield resp.json()


@pytest.fixture()
def succeeded_payment_intent(stripe):
    """Create, confirm, and capture a PaymentIntent so its status is 'succeeded'."""
    # Create with auto-capture
    resp = stripe.create_payment_intent(
        amount=3000,
        currency="usd",
        confirm=True,
        payment_method=TEST_CARDS["visa_success"],
        **{"payment_method_types[]": "card"},
    )
    assert resp.status_code == 200, f"PaymentIntent creation failed: {resp.text}"
    yield resp.json()
