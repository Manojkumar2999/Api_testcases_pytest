"""
Stripe API client helper — thin wrapper around requests for Stripe REST calls.
"""
import requests
from utils.config import BASE_URL, STRIPE_SECRET_KEY


class StripeClient:
    """Lightweight HTTP client targeting the Stripe v1 API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or STRIPE_SECRET_KEY
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
        })

    # -- Customers ---------------------------------------------------------

    def create_customer(self, **kwargs) -> requests.Response:
        """POST /v1/customers"""
        return self.session.post(f"{self.base_url}/customers", data=kwargs)

    def get_customer(self, customer_id: str) -> requests.Response:
        """GET /v1/customers/{customer_id}"""
        return self.session.get(f"{self.base_url}/customers/{customer_id}")

    def delete_customer(self, customer_id: str) -> requests.Response:
        """DELETE /v1/customers/{customer_id}"""
        return self.session.delete(f"{self.base_url}/customers/{customer_id}")

    # -- Payment Intents ---------------------------------------------------

    def create_payment_intent(self, **kwargs) -> requests.Response:
        """POST /v1/payment_intents"""
        return self.session.post(f"{self.base_url}/payment_intents", data=kwargs)

    def get_payment_intent(self, pi_id: str) -> requests.Response:
        """GET /v1/payment_intents/{pi_id}"""
        return self.session.get(f"{self.base_url}/payment_intents/{pi_id}")

    def confirm_payment_intent(self, pi_id: str, **kwargs) -> requests.Response:
        """POST /v1/payment_intents/{pi_id}/confirm"""
        return self.session.post(
            f"{self.base_url}/payment_intents/{pi_id}/confirm", data=kwargs
        )

    def capture_payment_intent(self, pi_id: str, **kwargs) -> requests.Response:
        """POST /v1/payment_intents/{pi_id}/capture"""
        return self.session.post(
            f"{self.base_url}/payment_intents/{pi_id}/capture", data=kwargs
        )
