"""
Credit Management — Check Balance and Buy Credits with USDC

Agents can autonomously manage their API credits:
  - Check current balance and tier
  - Buy verification credits with on-chain USDC (25 credits per 1 USDC)
  - Buy merchant credits for discount code generation

Supported USDC payment chains:
  Ethereum (1), Base (8453), Polygon (137), Arbitrum (42161),
  Optimism (10), BNB Chain (56), Avalanche (43114), Solana ("solana")

Platform wallets:
  EVM:    0xAd982CB19aCCa2923Df8F687C0614a7700255a23
  Solana: 6a1mLjefhvSJX1sEX8PTnionbE9DqoYjU6F6bNkT4Ydr

Usage:
    export INSUMER_API_KEY="insr_live_YOUR_KEY_HERE"
    python credits_flow.py
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

HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


# ── Step 1: Check current credit balance ─────────────────────────

print("=== Step 1: Check Credit Balance ===\n")

result = requests.get(f"{BASE_URL}/v1/credits", headers=HEADERS).json()

if result["ok"]:
    data = result["data"]
    print(f"  Credits:     {data['apiKeyCredits']}")
    print(f"  Tier:        {data['tier']}")
    print(f"  Daily limit: {data['dailyLimit']} reads/day")

    # Pricing reference
    print("\n  Pricing:")
    print("    Attestation:       1 credit  ($0.04)")
    print("    Attestation+proof: 2 credits ($0.08)")
    print("    Trust profile:     3 credits ($0.12)")
    print("    Trust+proof:       6 credits ($0.24)")
else:
    print(f"  Error: {result['error']['message']}")
    sys.exit(1)


# ── Step 2: Buy verification credits with USDC ──────────────────

print("\n=== Step 2: Buy Verification Credits (USDC) ===\n")
print("To buy credits, send USDC to the platform wallet and submit the tx hash.\n")

# This example shows the API call structure.
# In production, your agent would:
#   1. Send USDC on-chain to the platform wallet
#   2. Get the transaction hash
#   3. Submit it here for credit top-up

EXAMPLE_TX = "0x0000000000000000000000000000000000000000000000000000000000000000"

print("  Example API call (dry run — use a real tx hash in production):\n")
print(f"  POST {BASE_URL}/v1/credits/buy")
print(f"  Body: {{")
print(f'    "txHash": "{EXAMPLE_TX}",')
print(f'    "chainId": 8453,   // Base')
print(f'    "amount": 5         // 5 USDC = 125 credits')
print(f"  }}")

print("\n  Platform wallets:")
print("    EVM:    0xAd982CB19aCCa2923Df8F687C0614a7700255a23")
print("    Solana: 6a1mLjefhvSJX1sEX8PTnionbE9DqoYjU6F6bNkT4Ydr")

print("\n  Supported chains:")
chains = [
    ("Ethereum", 1), ("Base", 8453), ("Polygon", 137),
    ("Arbitrum", 42161), ("Optimism", 10), ("BNB Chain", 56),
    ("Avalanche", 43114), ("Solana", "solana"), ("XRPL", "xrpl"),
]
for name, chain_id in chains:
    print(f"    {name} (chainId: {chain_id})")

print("\n  Rate: 25 credits per 1 USDC | Minimum: 5 USDC (125 credits)")


# ── Step 3: Buy merchant credits ─────────────────────────────────

print("\n\n=== Step 3: Buy Merchant Credits (USDC) ===\n")
print("Merchant credits are consumed by /v1/verify, /v1/acp/discount, /v1/ucp/discount.\n")

MERCHANT_ID = "demo-coffee-shop"

print(f"  Example API call:")
print(f"  POST {BASE_URL}/v1/merchants/{MERCHANT_ID}/credits")
print(f"  Body: {{")
print(f'    "txHash": "0x...",')
print(f'    "chainId": 8453,')
print(f'    "amount": 10        // 10 USDC = 250 merchant credits')
print(f"  }}")


# ── Autonomous agent flow ────────────────────────────────────────

print("\n\n=== Full Autonomous Credit Management Flow ===\n")
print("An agent can maintain its own credit balance without human intervention:\n")
print("  1. GET  /v1/credits           — check remaining credits")
print("  2. If low, send USDC on-chain — agent initiates transfer")
print("  3. POST /v1/credits/buy       — submit tx hash, receive credits")
print("  4. Continue making API calls   — attestations, trust profiles, discounts")
print("\nSame pattern works for merchant credits via POST /v1/merchants/{id}/credits")
print("\nThis enables fully autonomous agent commerce with no human billing cycle.")
