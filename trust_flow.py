"""
Wallet Trust Profiles — Agent-to-Agent Trust Signals

Generate ECDSA-signed trust fact profiles for any EVM wallet.
17 checks across 4 dimensions:
  - Stablecoins: USDC across 7 chains
  - Governance: UNI, AAVE, ARB, OP
  - NFTs: BAYC, Pudgy Penguins, Wrapped CryptoPunks
  - Staking: stETH, rETH, cbETH

Single wallet (3 credits) or batch up to 10 wallets (3 credits/wallet).
Batch mode shares block fetches for 5-8x faster throughput.

Usage:
    export INSUMER_API_KEY="insr_live_YOUR_KEY_HERE"
    python trust_flow.py
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


# ── Example 1: Single wallet trust profile ───────────────────────

print("=== Single Wallet Trust Profile ===\n")

result = requests.post(
    f"{BASE_URL}/v1/trust",
    headers=HEADERS,
    json={"wallet": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"},
).json()

if not result["ok"]:
    print(f"Error: {result['error']['message']}")
    sys.exit(1)

trust = result["data"]["trust"]
summary = trust["summary"]

print(f"Profile ID: {trust['id']}")
print(f"Wallet:     {trust['wallet']}")
print(f"Version:    {trust['conditionSetVersion']}")
print(f"Profiled:   {trust['profiledAt']}")
print(f"Expires:    {trust['expiresAt']}")

print(f"\nSummary: {summary['totalPassed']}/{summary['totalChecks']} checks passed")
print(f"Active dimensions: {summary['dimensionsWithActivity']}/{summary['dimensionsChecked']}")

for dim_name, dim_data in trust["dimensions"].items():
    passed = dim_data["passCount"]
    total = dim_data["total"]
    status = "active" if passed > 0 else "empty"
    print(f"\n  {dim_name.upper()} ({status}): {passed}/{total} passed")

    for check in dim_data["checks"][:3]:  # show first 3
        icon = "PASS" if check["met"] else "FAIL"
        print(f"    [{icon}] {check['label']} (chain {check['chainId']})")

    if len(dim_data["checks"]) > 3:
        print(f"    ... and {len(dim_data['checks']) - 3} more")

print(f"\nSigned: kid={result['data']['kid']}")
print(f"Sig:    {result['data']['sig'][:40]}...")
print(f"Credits: {result['meta']['creditsCharged']} used, {result['meta']['creditsRemaining']} remaining")


# ── Example 2: Batch trust profiles ──────────────────────────────

print("\n\n=== Batch Trust Profiles (3 wallets) ===\n")

wallets = [
    {"wallet": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"},  # vitalik.eth
    {"wallet": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"},  # another known wallet
    {"wallet": "0x1234567890abcdef1234567890abcdef12345678"},  # likely empty
]

batch = requests.post(
    f"{BASE_URL}/v1/trust/batch",
    headers=HEADERS,
    json={"wallets": wallets},
).json()

if not batch["ok"]:
    print(f"Error: {batch['error']['message']}")
    sys.exit(1)

results = batch["data"]["results"]

for i, entry in enumerate(results):
    if "error" in entry:
        print(f"Wallet {i + 1}: ERROR — {entry['error']}")
        continue

    t = entry["trust"]
    s = t["summary"]
    print(f"Wallet {i + 1}: {t['wallet'][:10]}...{t['wallet'][-4:]}")
    print(f"  ID: {t['id']} | {s['totalPassed']}/{s['totalChecks']} passed | {s['dimensionsWithActivity']} active dims")

print(f"\nBatch credits: {batch['meta']['creditsCharged']} used ({batch['meta']['creditsCharged'] // len(wallets)}/wallet)")
print(f"Credits remaining: {batch['meta']['creditsRemaining']}")
