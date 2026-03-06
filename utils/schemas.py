"""
JSON-Schema definitions for Stripe API response validation.
"""

CUSTOMER_SCHEMA = {
    "type": "object",
    "required": ["id", "object", "created", "email", "name", "livemode"],
    "properties": {
        "id": {"type": "string", "pattern": "^cus_"},
        "object": {"type": "string", "enum": ["customer"]},
        "created": {"type": "integer"},
        "email": {"type": ["string", "null"]},
        "name": {"type": ["string", "null"]},
        "phone": {"type": ["string", "null"]},
        "livemode": {"type": "boolean", "enum": [False]},
        "description": {"type": ["string", "null"]},
        "metadata": {"type": "object"},
    },
}

PAYMENT_INTENT_SCHEMA = {
    "type": "object",
    "required": [
        "id", "object", "amount", "currency", "status",
        "created", "livemode",
    ],
    "properties": {
        "id": {"type": "string", "pattern": "^pi_"},
        "object": {"type": "string", "enum": ["payment_intent"]},
        "amount": {"type": "integer", "minimum": 0},
        "amount_received": {"type": "integer", "minimum": 0},
        "currency": {"type": "string", "minLength": 3, "maxLength": 3},
        "status": {
            "type": "string",
            "enum": [
                "requires_payment_method",
                "requires_confirmation",
                "requires_action",
                "processing",
                "requires_capture",
                "canceled",
                "succeeded",
            ],
        },
        "receipt_email": {"type": ["string", "null"]},
        "created": {"type": "integer"},
        "livemode": {"type": "boolean", "enum": [False]},
        "payment_method_types": {
            "type": "array",
            "items": {"type": "string"},
        },
        "capture_method": {
            "type": "string",
            "enum": ["automatic", "automatic_async", "manual"],
        },
        "metadata": {"type": "object"},
    },
}

STRIPE_ERROR_SCHEMA = {
    "type": "object",
    "required": ["error"],
    "properties": {
        "error": {
            "type": "object",
            "required": ["type", "message"],
            "properties": {
                "type": {"type": "string"},
                "message": {"type": "string"},
                "code": {"type": "string"},
                "param": {"type": "string"},
            },
        },
    },
}
