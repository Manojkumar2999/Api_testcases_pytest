"""
Tests for GET /v1/customers/{customer_id} — Fetch Customer Details.
"""
import pytest


@pytest.mark.customers
class TestFetchCustomer:
    """Validate fetching customer details from the Stripe API."""

    def test_fetch_existing_customer(self, stripe, customer):
        """Fetching a known customer should return 200 with correct data."""
        resp = stripe.get_customer(customer["id"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == customer["id"]
        assert data["email"] == customer["email"]
        assert data["name"] == customer["name"]

    def test_fetch_customer_object_type(self, stripe, customer):
        """The object field should be 'customer'."""
        resp = stripe.get_customer(customer["id"])
        data = resp.json()
        assert data["object"] == "customer"

    def test_fetch_nonexistent_customer_returns_error(self, stripe):
        """Fetching a non-existing customer ID should return 404."""
        resp = stripe.get_customer("cus_nonexistent000000")
        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data
        assert data["error"]["type"] == "invalid_request_error"

    def test_fetch_invalid_customer_id_format(self, stripe):
        """An obviously bad customer ID should return an error."""
        resp = stripe.get_customer("invalid_id_!@#")
        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data
