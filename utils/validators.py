"""
Reusable validation helpers for the test suite.
"""
import re
from jsonschema import validate, ValidationError


def validate_schema(instance: dict, schema: dict) -> None:
    """Validate *instance* against a JSON-Schema *schema*.

    Raises ``AssertionError`` with a human-readable message on failure.
    """
    try:
        validate(instance=instance, schema=schema)
    except ValidationError as exc:
        raise AssertionError(f"Schema validation failed: {exc.message}") from exc


def assert_valid_email(email: str) -> None:
    """Assert that *email* looks like a valid e-mail address."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    assert re.match(pattern, email), f"Invalid email format: {email}"


def assert_valid_phone(phone: str) -> None:
    """Assert that *phone* matches E.164-ish format (+<digits>)."""
    pattern = r"^\+?[1-9]\d{1,14}$"
    assert re.match(pattern, phone), f"Invalid phone format: {phone}"


def assert_valid_iso_currency(currency: str) -> None:
    """Assert *currency* is a 3-letter lowercase ISO 4217 code."""
    assert (
        isinstance(currency, str) and len(currency) == 3 and currency.islower()
    ), f"Invalid ISO currency code: {currency}"
