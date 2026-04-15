# 🌿 CarbonOracle

**ESG & Carbon Intelligence MCP Server** — 11 tools | Part of [ToolOracle](https://tooloracle.io)

![Tools](https://img.shields.io/badge/MCP_Tools-11-10B898?style=flat-square)
![Status](https://img.shields.io/badge/Status-Live-00C853?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)
![Tier](https://img.shields.io/badge/Tier-Free-2196F3?style=flat-square)

## Quick Connect

```bash
# Claude Desktop / Cursor / Windsurf
npx -y mcp-remote https://tooloracle.io/carbon/mcp/
```

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "carbonoracle": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://tooloracle.io/carbon/mcp/"]
    }
  }
}
```

## Tools (11)

| Tool | Description |
|------|-------------|
| `carbon_eu_ets_price` | Live EU Emissions Trading System price (EUA in EUR and USD) |
| `carbon_grid_intensity` | Real-time electricity grid carbon intensity by country (gCO2/kWh) |
| `carbon_grid_compare` | Compare electricity carbon intensity across 20+ countries |
| `carbon_ember_country` | Annual electricity carbon intensity from Ember Climate data |
| `carbon_ember_eu_ranking` | EU country ranking by electricity carbon intensity |
| `carbon_footprint` | Carbon footprint estimation for common products and activities |
| `carbon_blockchain` | Carbon intensity of major blockchain networks (gCO2/tx) |
| `carbon_chain` | Detailed carbon footprint for any specific blockchain |
| `carbon_chain_ranking` | Rank all 50 blockchains by carbon footprint |
| `carbon_vechain` | VeChain deep carbon profile (DNV ISO14040/14044 certified) |
| `health_check` | Service health status |

## Pricing

| Tier | Rate Limit | Price |
|------|-----------|-------|
| Free | 100 calls/day | $0 |
| Pro | 1,100 units/month | $49/month |
| Agent | 5,500 units/month | $299/month |
| x402 | Pay per call | $0.01/call USDC on Base |

> Free tier includes all tools with rate limiting. Register with `kya_register` for 500 welcome units.

## Part of ToolOracle

CarbonOracle is one of **100+ MCP servers** in the [ToolOracle](https://tooloracle.io) ecosystem — self-serve MCP infrastructure for AI agents with 1,200+ tools across 8 categories.

## Links

- 🌐 Live: `https://tooloracle.io/carbon/mcp/`
- 📚 Docs: [tooloracle.io/docs](https://tooloracle.io/docs)
- 🏠 Platform: [tooloracle.io](https://tooloracle.io)

---

*Built by [FeedOracle Technologies](https://feedoracle.io) — Evidence by Design*
