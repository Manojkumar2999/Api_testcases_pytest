# Stripe API Automated Test Suite

Automated PyTest suite that validates key behaviors of the Stripe **test-mode** API.

## Project Structure

```
autoCheck/
├── main.py                          # Entry point (runs pytest)
├── pytest.ini                       # PyTest configuration & markers
├── requirements.txt                 # Python dependencies
├── .env.example                     # Template for env vars
├── utils/
│   ├── __init__.py
│   ├── config.py                    # Base URL, API key, test cards
│   ├── api_client.py                # StripeClient HTTP wrapper
│   ├── schemas.py                   # JSON-Schema definitions
│   └── validators.py                # Reusable assertion helpers
└── tests/
    ├── __init__.py
    ├── conftest.py                  # Shared fixtures (customer, PI, etc.)
    ├── test_create_customer.py      # POST /customers
    ├── test_fetch_customer.py       # GET /customers/{id}
    ├── test_create_payment_intent.py# POST /payment_intents
    ├── test_confirm_capture_payment.py  # confirm + capture flow
    ├── test_fetch_payment_details.py    # GET /payment_intents/{id}
    └── test_negative_validation.py      # Negative & edge-case tests
```

## Setup

```bash
# 1. Create & activate a virtual env
python -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Stripe test secret key
cp .env.example .env
# Edit .env and replace the placeholder with your sk_test_... key
```

## Running Tests

```bash
# Full suite
python main.py

# Or via pytest directly
pytest tests/ -v

# Run by marker
pytest tests/ -v -m customers
pytest tests/ -v -m payment_intents
pytest tests/ -v -m negative

# Run a specific test
pytest tests/test_create_customer.py::TestCreateCustomer::test_customer_id_starts_with_cus -v

# Generate HTML report
pytest tests/ -v --html=report.html --self-contained-html
```

## Test Coverage Summary

| Area | Tests |
|---|---|
| **Create Customer** | Status 200, ID prefix, email/phone format, schema, field echo, livemode |
| **Fetch Customer** | Existing customer, object type, non-existent ID, invalid ID |
| **Create PaymentIntent** | Status 200, initial status, amount/currency validation, schema, metadata |
| **Confirm & Capture** | Confirm succeeds, manual capture flow, partial capture, capture-before-confirm, over-capture |
| **Fetch PaymentIntent** | 200 response, field match, non-existent ID, status transitions, timestamps |
| **Negative / Validation** | Missing fields, invalid currency, zero/negative amount, declined cards (4 types), processing error, double capture |

## Stripe Test Cards Used

| Card | Token |
|---|---|
| Visa (success) | `pm_card_visa` |
| Generic decline | `pm_card_visa_chargeDeclined` |
| Insufficient funds | `pm_card_visa_chargeDeclinedInsufficientFunds` |
| Expired card | `pm_card_visa_chargeDeclinedExpiredCard` |
| Incorrect CVC | `pm_card_visa_chargeDeclinedIncorrectCvc` |
| Processing error | `pm_card_visa_chargeDeclinedProcessingError` |
