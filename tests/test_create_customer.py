"""
Tests for POST /v1/customers — Create a Customer.
"""
import pytest
from utils.schemas import CUSTOMER_SCHEMA
from utils.validators import (
    assert_valid_email,
    assert_valid_phone,
    validate_schema,
)


@pytest.mark.customers
class TestCreateCustomer:
    """Validate customer creation via the Stripe API."""

    def test_create_customer_status_200(self, stripe):
        """Creating a customer should return HTTP 200."""
        resp = stripe.create_customer(
            name="Alice Test",
            email="alice@example.com",
            phone="+14155550100",
        )
        assert resp.status_code == 200
        # Cleanup
        stripe.delete_customer(resp.json()["id"])

    def test_customer_id_starts_with_cus(self, customer):
        """The customer ID must start with 'cus_'."""
        assert customer["id"].startswith("cus_"), (
            f"Expected ID prefix 'cus_', got: {customer['id']}"
        )

    def test_customer_email_format(self, customer):
        """The returned email should match a valid email pattern."""
        assert_valid_email(customer["email"])

    def test_customer_phone_format(self, customer):
        """The returned phone should match E.164-ish format."""
        assert_valid_phone(customer["phone"])

    def test_customer_response_schema(self, customer):
        """Full JSON-schema validation of the customer response."""
        validate_schema(customer, CUSTOMER_SCHEMA)

    def test_customer_returned_fields_match_input(self, stripe):
        """Fields sent in the request should appear in the response."""
        payload = {
            "name": "Schema Check",
            "email": "schema@check.com",
            "phone": "+442071234567",
        }
        resp = stripe.create_customer(**payload)
        data = resp.json()
        assert data["name"] == payload["name"]
        assert data["email"] == payload["email"]
        assert data["phone"] == payload["phone"]
        stripe.delete_customer(data["id"])

    def test_customer_livemode_is_false(self, customer):
        """Test-mode customers must have livemode=false."""
        assert customer["livemode"] is False
