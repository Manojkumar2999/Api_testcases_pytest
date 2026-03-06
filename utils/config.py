"""
Stripe API configuration and constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.stripe.com/v1"
STRIPE_SECRET_KEY = os.getenv("STRIPE_TEST_SECRET_KEY", "")

# Stripe test card tokens (see https://docs.stripe.com/testing)
TEST_CARDS = {
    "visa_success": "pm_card_visa",
    "mastercard_success": "pm_card_mastercard",
    "declined_generic": "pm_card_visa_chargeDeclined",
    "declined_insufficient": "pm_card_visa_chargeDeclinedInsufficientFunds",
    "declined_expired": "pm_card_visa_chargeDeclinedExpiredCard",
    "declined_cvc": "pm_card_visa_chargeDeclinedIncorrectCvc",
    "declined_processing": "pm_card_visa_chargeDeclinedProcessingError",
}

# ISO 4217 currency codes (subset for validation)
VALID_CURRENCIES = {
    "usd", "eur", "gbp", "jpy", "cad", "aud", "chf", "cny",
    "inr", "mxn", "brl", "sgd", "hkd", "nzd", "sek", "nok",
    "dkk", "pln", "krw", "thb", "try", "zar",
}
