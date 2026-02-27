# ACP & UCP On-Chain Eligibility Verification Examples

Minimal, copy-paste-ready examples for integrating on-chain token-holder discounts into AI agent commerce flows using [InsumerAPI](https://insumermodel.com/developers/).

**ACP** = OpenAI/Stripe Agentic Commerce Protocol
**UCP** = Google Universal Commerce Protocol

Both endpoints verify token holdings on-chain across 31 blockchains, then return a signed discount code in the requested protocol format. Same verification, different response shape.

## What's in this repo

| File | Description |
|------|-------------|
| `acp_flow.py` | ACP discount request with coupon parsing and per-item allocations |
| `ucp_flow.py` | UCP discount request with extension routing and title parsing |
| `validate_code.py` | Merchant-side code validation (no API key needed) |
| `full_agent_flow.py` | End-to-end: discover merchant → check eligibility → get discount → validate code |

## Quick start

```bash
# Clone
git clone https://github.com/douglasborthwick-crypto/acp-ucp-onchain-eligibility-example.git
cd acp-ucp-onchain-eligibility-example

# Install
pip install requests

# Set your API key (free tier: 10 credits)
export INSUMER_API_KEY="insr_live_YOUR_KEY_HERE"

# Run any example
python acp_flow.py
python ucp_flow.py
python validate_code.py
python full_agent_flow.py
```

## Get an API key

Free tier includes 10 verification credits. No credit card required.

→ [Get your key](https://insumermodel.com/developers/#pricing)

## How it works

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

## Endpoints used

| Endpoint | Auth | Credits | Description |
|----------|------|---------|-------------|
| `POST /v1/acp/discount` | API key | 1 merchant credit | ACP-format discount with coupon objects |
| `POST /v1/ucp/discount` | API key | 1 merchant credit | UCP-format discount with title + extension |
| `GET /v1/codes/{code}` | None | Free | Validate an INSR-XXXXX code |
| `GET /v1/merchants` | None | Free | Browse merchant directory |
| `GET /v1/discount/check` | None | Free | Check eligibility (no code generated) |

## Response formats

**ACP** returns coupon objects compatible with Stripe checkout:
```json
{
  "coupon": { "id": "insumer-insr-a7k3m", "name": "Token Holder Discount (15% off)", "percent_off": 15 },
  "start": "2026-02-27T12:00:00.000Z",
  "end": "2026-02-27T12:30:00.000Z"
}
```

**UCP** returns title strings with the `dev.ucp.shopping.discount` extension:
```json
{
  "title": "Token Holder Discount - 15% Off",
  "extension": "dev.ucp.shopping.discount"
}
```

Both include an ECDSA P-256 signature (`sig` + `kid`) for cryptographic verification.

## Links

- [API Documentation](https://insumermodel.com/developers/)
- [OpenAPI Spec](https://insumermodel.com/openapi.yaml)
- [ACP Integration Guide](https://insumermodel.com/blog/acp-discount-endpoint-integration-guide.html)
- [UCP Commerce Tutorial](https://insumermodel.com/blog/on-chain-verification-ai-agent-commerce-tutorial.html)
- [MCP Server](https://www.npmjs.com/package/mcp-server-insumer) (23 tools, npm)
- [LangChain SDK](https://pypi.org/project/langchain-insumer/) (19 tools, PyPI)

## License

MIT
