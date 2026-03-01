"""
Attestation Flow — Boolean On-Chain Verification

Verify any combination of on-chain conditions in a single call:
  - token_balance: does this wallet hold >= N tokens?
  - nft_ownership: does this wallet hold an NFT from this collection?
  - eas_attestation: does this wallet have a verified credential (KYC, Passport)?
  - farcaster_id: does this wallet have a Farcaster identity?

Each condition returns a signed boolean — never raw balances.
Optional Merkle storage proofs for trustless verification.

Usage:
    export INSUMER_API_KEY="insr_live_YOUR_KEY_HERE"
    python attest_flow.py
"""

import os
import sys
import requests

BASE_URL = "https://us-central1-insumer-merchant.cloudfunctions.net/insumerApi"
API_KEY = os.environ.get("INSUMER_API_KEY", "")
WALLET = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # vitalik.eth

if not API_KEY:
    print("Set INSUMER_API_KEY environment variable first.")
    print("Get a free key: https://insumermodel.com/developers/#pricing")
    sys.exit(1)

HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


def attest(conditions, wallet=WALLET, proof=None):
    """Run on-chain attestation. Returns signed boolean results."""
    payload = {"wallet": wallet, "conditions": conditions}
    if proof:
        payload["proof"] = proof
    resp = requests.post(f"{BASE_URL}/v1/attest", headers=HEADERS, json=payload)
    return resp.json()


def print_results(result):
    """Print attestation results."""
    if not result["ok"]:
        print(f"  Error: {result['error']['message']}")
        return

    att = result["data"]["attestation"]
    print(f"  Pass: {att['pass']}")
    print(f"  ID:   {att['id']}")

    for r in att["results"]:
        status = "PASS" if r["met"] else "FAIL"
        print(f"  [{status}] {r.get('label', r['type'])} (chain {r['chainId']})")

    print(f"\n  Signed: kid={result['data']['kid']}")
    print(f"  Sig:    {result['data']['sig'][:40]}...")
    print(f"  Credits used: {result['meta']['creditsCharged']}")
    print(f"  Credits left: {result['meta']['creditsRemaining']}")


# ── Example 1: Multi-chain token balance check ──────────────────

print("=== Example 1: Multi-Chain Token Balance ===\n")

result = attest([
    {
        "type": "token_balance",
        "contractAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "chainId": 1,
        "threshold": 100,
        "decimals": 6,
        "label": "USDC >= 100 on Ethereum",
    },
    {
        "type": "token_balance",
        "contractAddress": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "chainId": 8453,
        "threshold": 50,
        "decimals": 6,
        "label": "USDC >= 50 on Base",
    },
])

print_results(result)


# ── Example 2: NFT ownership ────────────────────────────────────

print("\n\n=== Example 2: NFT Ownership ===\n")

result = attest([
    {
        "type": "nft_ownership",
        "contractAddress": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
        "chainId": 1,
        "label": "Bored Ape Yacht Club holder",
    },
])

print_results(result)


# ── Example 3: EAS attestation (Coinbase KYC) ───────────────────

print("\n\n=== Example 3: EAS Attestation — Coinbase KYC ===\n")

result = attest([
    {
        "type": "eas_attestation",
        "template": "coinbase_verified_account",
        "label": "Coinbase KYC verified",
    },
])

print_results(result)


# ── Example 4: Farcaster identity ────────────────────────────────

print("\n\n=== Example 4: Farcaster Identity ===\n")

result = attest([
    {
        "type": "farcaster_id",
        "chainId": 10,
        "label": "Has Farcaster ID on Optimism",
    },
])

print_results(result)


# ── Example 5: Combined conditions (all 4 types in one call) ────

print("\n\n=== Example 5: Combined — All 4 Condition Types ===\n")

result = attest([
    {
        "type": "token_balance",
        "contractAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "chainId": 1,
        "threshold": 100,
        "decimals": 6,
        "label": "USDC >= 100 on Ethereum",
    },
    {
        "type": "nft_ownership",
        "contractAddress": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
        "chainId": 1,
        "label": "BAYC holder",
    },
    {
        "type": "eas_attestation",
        "template": "coinbase_verified_account",
        "label": "Coinbase KYC",
    },
    {
        "type": "farcaster_id",
        "chainId": 10,
        "label": "Farcaster ID",
    },
])

print_results(result)


# ── Example 6: Merkle storage proof ─────────────────────────────

print("\n\n=== Example 6: Merkle Storage Proof ===\n")
print("(Adds EIP-1186 proof for trustless verification — 2 credits)\n")

result = attest(
    [
        {
            "type": "token_balance",
            "contractAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "chainId": 1,
            "threshold": 100,
            "decimals": 6,
            "label": "USDC >= 100 on Ethereum (with proof)",
        },
    ],
    proof="merkle",
)

if result["ok"]:
    print_results(result)
    proof_data = result["data"]["attestation"]["results"][0].get("proof", {})
    if proof_data.get("available"):
        print(f"\n  Merkle proof included:")
        print(f"    Block:        {proof_data['blockNumber']}")
        print(f"    Storage slot: {proof_data['mappingSlot']}")
        print(f"    Account proof nodes: {len(proof_data['accountProof'])}")
        print(f"    Storage proof nodes: {len(proof_data['storageProof'][0]['proof'])}")
        print(f"    Raw balance (hex): {proof_data['storageProof'][0]['value']}")
    else:
        reason = proof_data.get("reason", "unknown")
        print(f"\n  Merkle proof unavailable: {reason}")
else:
    print_results(result)


# ── Example 7: XRPL — native XRP balance ──────────────────────

print("\n\n=== Example 7: XRPL — Native XRP Balance ===\n")

XRPL_WALLET = "rG1QQv2nh2gr7RCZ1P8YYcBUKCCN633jCn"

result = requests.post(
    f"{BASE_URL}/v1/attest",
    headers=HEADERS,
    json={
        "xrplWallet": XRPL_WALLET,
        "conditions": [
            {
                "type": "token_balance",
                "contractAddress": "native",
                "chainId": "xrpl",
                "threshold": 100,
                "label": "XRP >= 100",
            },
        ],
    },
).json()

print_results(result)


# ── Example 8: XRPL — RLUSD trust line token ──────────────────

print("\n\n=== Example 8: XRPL — RLUSD Trust Line Token ===\n")

result = requests.post(
    f"{BASE_URL}/v1/attest",
    headers=HEADERS,
    json={
        "xrplWallet": XRPL_WALLET,
        "conditions": [
            {
                "type": "token_balance",
                "contractAddress": "rMxCKbEDwqr76QuheSUMdEGf4B9xJ8m5De",
                "chainId": "xrpl",
                "currency": "RLUSD",
                "threshold": 10,
                "label": "RLUSD >= 10 on XRPL",
            },
        ],
    },
).json()

print_results(result)
