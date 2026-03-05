"""
Merchant-Side Code Validation

Validates an INSR-XXXXX discount code at checkout.
No API key required — this endpoint is public.

Usage:
    python validate_code.py INSR-A7K3M
"""

import sys
import requests

BASE_URL = "https://api.insumermodel.com"


def validate_code(code: str) -> dict:
    """Validate an INSR-XXXXX discount code. No auth required."""
    resp = requests.get(f"{BASE_URL}/v1/codes/{code}")
    return resp.json()


# Get code from command line or use example
code = sys.argv[1] if len(sys.argv) > 1 else "INSR-EXAMPLE"

print(f"=== Validating Code: {code} ===\n")

result = validate_code(code)

if not result["ok"]:
    print(f"Error: {result['error']['message']}")
    sys.exit(1)

data = result["data"]

if data["valid"]:
    print(f"Status:   VALID")
    print(f"Merchant: {data['merchantId']}")
    print(f"Discount: {data['discountPercent']}% off")
    print(f"Expires:  {data['expiresAt']}")
    print(f"Created:  {data['createdAt']}")

    # Merchant should verify:
    # 1. data["valid"] is True
    # 2. data["merchantId"] matches their own merchant ID
    # 3. data["expiresAt"] is in the future
    print("\nChecklist:")
    print("  [x] Code is valid")
    print(f"  [ ] Merchant ID matches yours? ({data['merchantId']})")
    print(f"  [ ] Not expired? ({data['expiresAt']})")
else:
    reason = data["reason"]
    print(f"Status: INVALID")
    print(f"Reason: {reason}")

    if reason == "expired":
        print("  The code has passed its 30-minute validity window.")
    elif reason == "already_used":
        print("  This code was already redeemed.")
    elif reason == "not_found":
        print("  No code with this ID exists.")
