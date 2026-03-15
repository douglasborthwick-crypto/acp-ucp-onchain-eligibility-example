# InsumerAPI — On-Chain Verification Examples

Minimal, copy-paste-ready examples for integrating on-chain verification into AI agent commerce flows using [InsumerAPI](https://insumermodel.com/developers/).

**ACP** = OpenAI/Stripe Agentic Commerce Protocol
**UCP** = Google Universal Commerce Protocol

## What's in this repo

### Commerce Protocol Flows

| File | Description |
|------|-------------|
| `acp_flow.py` | ACP discount request with coupon parsing and per-item allocations |
| `ucp_flow.py` | UCP discount request with extension routing and title parsing |
| `validate_code.py` | Merchant-side code validation (no API key needed) |
| `full_agent_flow.py` | End-to-end: discover merchant → check eligibility → get discount → validate code |

### Core Verification

| File | Description |
|------|-------------|
| `attest_flow.py` | Boolean attestation — all 4 condition types + Merkle storage proofs |
| `trust_flow.py` | Wallet trust profiles — single + batch (up to 10 wallets) |
| `compliance_gating.py` | EAS attestation templates — Coinbase KYC, Gitcoin Passport, Farcaster ID |

### Autonomous Agent Operations

| File | Description |
|------|-------------|
| `merchant_onboarding.py` | Full self-serve pipeline: create → configure → publish (zero human input) |
| `credits_flow.py` | Credit management: check balance, buy credits with USDC on-chain |

## Quick start

```bash
# Get a free API key (10 verification credits, instant)
curl -X POST \
  https://api.insumermodel.com/v1/keys/create \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "appName": "my-app", "tier": "free"}'

# Clone
git clone https://github.com/douglasborthwick-crypto/acp-ucp-onchain-eligibility-example.git
cd acp-ucp-onchain-eligibility-example

# Install
pip install requests

# Set your API key
export INSUMER_API_KEY="insr_live_YOUR_KEY_HERE"

# Run any example
python acp_flow.py
python attest_flow.py
python compliance_gating.py
python merchant_onboarding.py
```

## Capabilities covered

### 4 Condition Types (`attest_flow.py`)

| Type | What It Checks | Chains |
|------|---------------|--------|
| `token_balance` | ERC-20/SPL balance >= threshold | All 32 (30 EVM + Solana + XRPL) |
| `nft_ownership` | Holds >= 1 NFT from collection | All 32 (30 EVM + Solana + XRPL) |
| `eas_attestation` | On-chain identity credential via EAS | Ethereum, Base, Optimism, Arbitrum, Polygon, Avalanche |
| `farcaster_id` | Farcaster IdRegistry presence | Optimism |

### 5 Compliance Templates (`compliance_gating.py`)

| Template | Chain | What It Verifies |
|----------|-------|-----------------|
| `coinbase_verified_account` | Base (8453) | Coinbase KYC verification |
| `coinbase_verified_country` | Base (8453) | Coinbase country attestation |
| `coinbase_one` | Base (8453) | Coinbase One membership |
| `gitcoin_passport_score` | Optimism (10) | Gitcoin Passport humanity score >= 20 |
| `gitcoin_passport_active` | Optimism (10) | Active Gitcoin Passport |

### Trust Profile Dimensions (`trust_flow.py`)

| Dimension | Checks | What It Covers |
|-----------|--------|---------------|
| Stablecoins | 7 | USDC across major chains |
| Governance | 4 | UNI, AAVE, ARB, OP |
| NFTs | 3 | BAYC, Pudgy Penguins, Wrapped CryptoPunks |
| Staking | 3 | stETH, rETH, cbETH |
| Solana | 1 | USDC on Solana (optional, requires `solanaWallet`) |
| XRPL | 2 | RLUSD + USDC on XRPL (optional, requires `xrplWallet`) |

### Merchant Onboarding (`merchant_onboarding.py`)

```
Agent                         InsumerAPI
  │                               │
  ├─ POST /v1/merchants ─────────►│  Create merchant (100 free credits)
  ├─ PUT  /v1/merchants/{id}/tokens ►│  Configure token tiers (up to 8 × 4)
  ├─ PUT  /v1/merchants/{id}/nfts ──►│  Configure NFT collections (up to 4)
  ├─ PUT  /v1/merchants/{id}/settings►│  Set discount mode + USDC payments
  ├─ POST /v1/merchants/{id}/directory►│  Publish to directory
  ├─ GET  /v1/merchants/{id}/status ─►│  Verify full configuration
  │                               │
  │  Merchant is now discoverable │
  │  by other AI agents via       │
  │  GET /v1/merchants            │
```

### Commerce Protocol Integration

```
Agent                    InsumerAPI                  Blockchain
  │                          │                           │
  ├─ POST /v1/acp/discount ─►│                           │
  │   (wallet, merchantId)   │── verify token holdings ──►│
  │                          │◄── on-chain state ─────────┤
  │◄── ACP coupon object ────┤                           │
  │    + INSR-XXXXX code     │                           │
  │    + ECDSA signature     │                           │
  │                          │                           │
  │                     Merchant                         │
  │                          │                           │
  ├─ present INSR-XXXXX ────►│                           │
  │                          ├─ GET /v1/codes/INSR-XXXXX │
  │                          │   (no API key needed)     │
  │                          │◄── valid: true, 15% off   │
  │◄── discount applied ─────┤                           │
```

## All endpoints covered

| Endpoint | Auth | Credits | Example File |
|----------|------|---------|-------------|
| `POST /v1/attest` | API key | 1 (2 w/ Merkle) | `attest_flow.py` |
| `POST /v1/trust` | API key | 3 (6 w/ Merkle) | `trust_flow.py` |
| `POST /v1/trust/batch` | API key | 3/wallet | `trust_flow.py` |
| `GET /v1/compliance/templates` | Public | Free | `compliance_gating.py` |
| `GET /v1/credits` | API key | Free | `credits_flow.py` |
| `POST /v1/credits/buy` | API key | — | `credits_flow.py` |
| `POST /v1/acp/discount` | API key | 1 merchant | `acp_flow.py` |
| `POST /v1/ucp/discount` | API key | 1 merchant | `ucp_flow.py` |
| `GET /v1/codes/{code}` | Public | Free | `validate_code.py` |
| `GET /v1/merchants` | API key | Free | `full_agent_flow.py` |
| `GET /v1/merchants/{id}` | API key | Free | `full_agent_flow.py` |
| `GET /v1/discount/check` | API key | Free | `full_agent_flow.py` |
| `POST /v1/merchants` | API key | — | `merchant_onboarding.py` |
| `PUT /v1/merchants/{id}/tokens` | API key | — | `merchant_onboarding.py` |
| `PUT /v1/merchants/{id}/nfts` | API key | — | `merchant_onboarding.py` |
| `PUT /v1/merchants/{id}/settings` | API key | — | `merchant_onboarding.py` |
| `POST /v1/merchants/{id}/directory` | API key | — | `merchant_onboarding.py` |
| `GET /v1/merchants/{id}/status` | API key | — | `merchant_onboarding.py` |
| `POST /v1/merchants/{id}/credits` | API key | — | `credits_flow.py` |

## Handling `rpc_failure` Errors

If the API cannot reach an upstream blockchain data source after retries, it returns HTTP 503 with `error.code: "rpc_failure"`. No attestation is signed, no credits are charged. This is a retryable error — wait 2-5 seconds and retry.

**Important:** `rpc_failure` is NOT a verification failure. Do not treat it as `pass: false`. It means the data source was temporarily unavailable and the API refused to sign an unverified result.

```python
resp = requests.post(f"{BASE_URL}/v1/attest", headers=HEADERS, json=payload)
result = resp.json()

if resp.status_code == 503 and result.get("error", {}).get("code") == "rpc_failure":
    # Retryable — data source temporarily unavailable
    print("Failed sources:", result["error"]["failedConditions"])
    # Wait 2-5s and retry
```

## Cryptographic verification

Every attestation and trust profile is ECDSA P-256 signed. Verify independently:

```bash
npm install insumer-verify
```

```javascript
import { verifyAttestation } from "insumer-verify";

// Pass the full API response envelope {ok, data: {attestation, sig, kid}, meta}
// Do NOT pass response.data — the function expects the outer envelope
const response = await res.json();
const result = await verifyAttestation(response, {
  jwksUrl: "https://insumermodel.com/.well-known/jwks.json"
});
console.log(result.valid); // true
```

## Links

- [API Documentation](https://insumermodel.com/developers/)
- [OpenAPI Spec](https://insumermodel.com/openapi.yaml)
- [AI Agent Verification API guide](https://insumermodel.com/ai-agent-verification-api/)
- [ACP Integration Guide](https://insumermodel.com/blog/acp-discount-endpoint-integration-guide.html)
- [UCP Commerce Tutorial](https://insumermodel.com/blog/on-chain-verification-ai-agent-commerce-tutorial.html)
- [Compliance Gating Guide](https://insumermodel.com/blog/compliance-gating-coinbase-verifications.html)
- [Trust Profiles Guide](https://insumermodel.com/blog/wallet-trust-profiles-agent-to-agent-trust.html)
- [Merkle Proofs Guide](https://insumermodel.com/blog/merkle-proofs-trustless-on-chain-verification.html)
- [MCP Server](https://www.npmjs.com/package/mcp-server-insumer) (25 tools, npm)
- [LangChain SDK](https://pypi.org/project/langchain-insumer/) (25 tools, PyPI)

## License

MIT
