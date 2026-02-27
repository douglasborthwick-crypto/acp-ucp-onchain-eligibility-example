"""
Compliance Gating — KYC, Identity & Credential Verification

Verify real-world credentials on-chain using EAS (Ethereum Attestation Service)
and Farcaster identity. Pre-configured templates eliminate the need to know
raw schema IDs or attester addresses.

Available templates:
  - coinbase_verified_account  — Coinbase KYC (Base, chain 8453)
  - coinbase_verified_country  — Coinbase country verification (Base)
  - coinbase_one               — Coinbase One membership (Base)
  - gitcoin_passport_score     — Gitcoin Passport >= 20 (Optimism, chain 10)
  - gitcoin_passport_active    — Active Gitcoin Passport (Optimism)

Plus direct condition types:
  - farcaster_id               — Farcaster IdRegistry (Optimism)

Usage:
    export INSUMER_API_KEY="insr_live_YOUR_KEY_HERE"
    python compliance_gating.py
"""

import os
import sys
import requests

BASE_URL = "https://us-central1-insumer-merchant.cloudfunctions.net/insumerApi"
API_KEY = os.environ.get("INSUMER_API_KEY", "")
WALLET = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

if not API_KEY:
    print("Set INSUMER_API_KEY environment variable first.")
    print("Get a free key: https://insumermodel.com/developers/#pricing")
    sys.exit(1)

HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


# ── Step 1: Discover available templates ─────────────────────────

print("=== Step 1: List Compliance Templates (Public, No Auth) ===\n")

templates = requests.get(f"{BASE_URL}/v1/compliance/templates").json()

if templates["ok"]:
    for name, info in templates["data"]["templates"].items():
        print(f"  {name}")
        print(f"    Provider: {info['provider']}")
        print(f"    Chain:    {info['chainName']} ({info['chainId']})")
        print(f"    Desc:     {info['description']}")
        print()
else:
    print(f"  Error: {templates['error']['message']}")


# ── Step 2: Coinbase KYC gate ────────────────────────────────────

print("=== Step 2: Coinbase KYC Verification ===\n")
print("Use case: Only allow KYC-verified users to access a service.\n")

result = requests.post(
    f"{BASE_URL}/v1/attest",
    headers=HEADERS,
    json={
        "wallet": WALLET,
        "conditions": [
            {
                "type": "eas_attestation",
                "template": "coinbase_verified_account",
                "label": "Coinbase KYC verified",
            },
        ],
    },
).json()

if result["ok"]:
    att = result["data"]["attestation"]
    kyc_passed = att["results"][0]["met"]
    print(f"  KYC verified: {kyc_passed}")
    print(f"  Attestation ID: {att['id']}")

    if kyc_passed:
        print("  -> Grant access to restricted service")
    else:
        print("  -> Redirect to Coinbase verification flow")
else:
    print(f"  Error: {result['error']['message']}")


# ── Step 3: Multi-credential compliance check ────────────────────

print("\n\n=== Step 3: Multi-Credential Compliance (Single Call) ===\n")
print("Use case: Require KYC + Gitcoin humanity score + Farcaster identity.\n")

result = requests.post(
    f"{BASE_URL}/v1/attest",
    headers=HEADERS,
    json={
        "wallet": WALLET,
        "conditions": [
            {
                "type": "eas_attestation",
                "template": "coinbase_verified_account",
                "label": "Coinbase KYC",
            },
            {
                "type": "eas_attestation",
                "template": "gitcoin_passport_score",
                "label": "Gitcoin Passport score >= 20",
            },
            {
                "type": "farcaster_id",
                "chainId": 10,
                "label": "Farcaster identity",
            },
        ],
    },
).json()

if result["ok"]:
    att = result["data"]["attestation"]
    print(f"  Overall pass: {att['pass']}")

    for r in att["results"]:
        status = "PASS" if r["met"] else "FAIL"
        print(f"  [{status}] {r['label']}")

    all_passed = att["pass"]
    if all_passed:
        print("\n  -> Full compliance: KYC + humanity + social identity verified")
    else:
        failed = [r["label"] for r in att["results"] if not r["met"]]
        print(f"\n  -> Missing credentials: {', '.join(failed)}")

    print(f"\n  Signed: kid={result['data']['kid']}")
    print(f"  Credits: {result['meta']['creditsCharged']} used")
else:
    print(f"  Error: {result['error']['message']}")


# ── Step 4: Country-specific gating ──────────────────────────────

print("\n\n=== Step 4: Country-Specific Access ===\n")
print("Use case: Restrict service to verified Coinbase users with country attestation.\n")

result = requests.post(
    f"{BASE_URL}/v1/attest",
    headers=HEADERS,
    json={
        "wallet": WALLET,
        "conditions": [
            {
                "type": "eas_attestation",
                "template": "coinbase_verified_country",
                "label": "Coinbase country verified",
            },
            {
                "type": "eas_attestation",
                "template": "coinbase_one",
                "label": "Coinbase One member",
            },
        ],
    },
).json()

if result["ok"]:
    att = result["data"]["attestation"]
    for r in att["results"]:
        status = "PASS" if r["met"] else "FAIL"
        print(f"  [{status}] {r['label']}")
else:
    print(f"  Error: {result['error']['message']}")

print(f"\n  Credits remaining: {result['meta']['creditsRemaining']}")
