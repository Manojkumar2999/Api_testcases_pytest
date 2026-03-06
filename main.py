"""
Stripe API Automated Test Suite — Entry Point.

Run the full suite:
    python main.py

Or use pytest directly:
    pytest tests/ -v
    pytest tests/ -v -m customers       # customer tests only
    pytest tests/ -v -m payment_intents  # payment intent tests only
    pytest tests/ -v -m negative         # negative/validation tests only
"""
import sys
import pytest


def main():
    args = [
        "tests/",
        "-v",
        "--tb=short",
    ]
    # Forward any CLI args (e.g. -m customers, -k test_name)
    args.extend(sys.argv[1:])
    exit_code = pytest.main(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
