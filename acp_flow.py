"""
ACP Discount Flow — OpenAI/Stripe Agentic Commerce Protocol

Verifies on-chain token holdings and returns the discount in ACP format
with coupon objects, applied/rejected arrays, and per-item allocations.

Usage:
    export INSUMER_API_KEY="insr_live_YOUR_KEY_HERE"
    python acp_flow.py
"""

import os
import sys
import requests

BASE_URL = "https://us-central1-insumer-merchant.cloudfunctions.net/insumerApi"
API_KEY = os.environ.get("INSUMER_API_KEY", "")

if not API_KEY:
    print("Set INSUMER_API_KEY environment variable first.")
    print("Get a free key: https://insumermodel.com/developers/#pricing")
    sys.exit(1)


def acp_discount(merchant_id: str, wallet: str, items: list | None = None) -> dict:
    """Request an ACP-format discount for a wallet at a merchant."""
    payload = {"merchantId": merchant_id, "wallet": wallet}
    if items:
        payload["items"] = items

    resp = requests.post(
        f"{BASE_URL}/v1/acp/discount",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json=payload,
    )
    return resp.json()


# --- Example 1: Basic ACP discount ---

print("=== Basic ACP Discount ===\n")

result = acp_discount(
    merchant_id="demo-coffee-shop",
    wallet="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
)

if not result["ok"]:
    print(f"Error: {result['error']['message']}")
    sys.exit(1)

discounts = result["data"]["discounts"]

if discounts["applied"]:
    coupon = discounts["applied"][0]["coupon"]
    code = discounts["codes"][0]
    expiry = discounts["applied"][0]["end"]
    sig = result["data"]["verification"]["sig"]

    print(f"Discount: {coupon['percent_off']}% off")
    print(f"Coupon:   {coupon['name']}")
    print(f"Code:     {code}")
    print(f"Expires:  {expiry}")
    print(f"Signed:   {sig[:40]}...")
else:
    reason = discounts["rejected"][0]["reason"]
    print(f"Not eligible: {reason}")

print(f"\nCredits used: {result['meta']['creditsCharged']}")
print(f"Credits left: {result['meta']['creditsRemaining']}")


# --- Example 2: ACP with per-item allocations ---

print("\n\n=== ACP with Per-Item Allocations ===\n")

result = acp_discount(
    merchant_id="demo-coffee-shop",
    wallet="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    items=[
        {"path": "cart/espresso", "amount": 450},
        {"path": "cart/croissant", "amount": 350},
        {"path": "cart/water", "amount": 200},
    ],
)

if result["ok"] and result["data"]["discounts"]["applied"]:
    entry = result["data"]["discounts"]["applied"][0]
    print(f"Total discount: ${entry.get('amount', 0) / 100:.2f}")

    if "allocations" in entry:
        print("Per-item breakdown:")
        for alloc in entry["allocations"]:
            print(f"  {alloc['path']}: -${alloc['amount'] / 100:.2f}")
