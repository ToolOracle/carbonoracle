# 🌿 CarbonOracle

**CO2 & Climate Intelligence MCP Server** — 11 tools | Part of [ToolOracle](https://tooloracle.io)

[![CarbonOracle MCP server](https://glama.ai/mcp/servers/ToolOracle/carbonoracle/badges/card.svg)](https://glama.ai/mcp/servers/ToolOracle/carbonoracle)

## Connect
```bash
npx -y mcp-remote https://tooloracle.io/carbon/mcp/
```

## Tools

| Tool | Credits | Description |
|------|---------|-------------|
| `carbon_eu_ets_price` | 2u | Live EU Emissions Trading System price (EUR/tCO2) |
| `carbon_grid_intensity` | 2u | Real-time electricity grid carbon intensity by country (gCO2/kWh) |
| `carbon_grid_compare` | 3u | Compare carbon intensity across 20+ countries |
| `carbon_ember_country` | 2u | Annual electricity carbon intensity for any country (Ember Climate 2024) |
| `carbon_ember_eu_ranking` | 3u | EU country ranking by electricity carbon intensity |
| `carbon_footprint` | 1u | Estimate product/activity footprint: laptop, flight, bitcoin tx, beef, etc. |
| `carbon_blockchain` | 1u | Carbon intensity of major blockchains (Ethereum, Bitcoin, Polygon, XRPL...) |
| `carbon_chain` | 2u | Deep carbon data for any of 50 blockchains by symbol |
| `carbon_chain_ranking` | 3u | Rank all 50 chains by carbon footprint, filter by MiCA Art.66 |
| `carbon_vechain` | 2u | VeChain deep profile — DNV ISO14040/14044 certified, PoA, MiCA Art.66 |
| `health_check` | free | Status, backend connectivity, tool list |

## Highlights

- **EU ETS Live**: Real-time European carbon allowance price (€73/tCO2)
- **50 Blockchains**: Bitcoin (1,513 kWh/tx) vs VeChain (0.00024 kWh/tx) vs Ethereum PoS (0.006 kWh/tx)
- **VeChain DNV Certified**: Only blockchain with ISO14040/14044 independent lifecycle certification
- **Real-time UK Grid**: Live carbon intensity from National Grid ESO
- **Ember Climate Data**: 100+ countries, annual electricity CO2 intensity

## Example

```json
// carbon_eu_ets_price
{
  "eua_price_eur": 73.25,
  "unit": "EUR/tCO2",
  "market": "EU ETS Phase 4"
}

// carbon_chain { "symbol": "VET" }
{
  "chain": "VeChain",
  "green_status": "EXCELLENT",
  "co2_tonnes_year": 1.61,
  "energy_per_tx_kwh": 0.000243,
  "certification": "DNV ISO14040/14044",
  "mica_art66_supported": true
}

// carbon_chain_ranking { "mica_art66_only": true, "top_n": 5 }
{
  "ranking": [
    { "rank": 1, "chain": "Polygon", "green_status": "EXCELLENT" },
    { "rank": 2, "chain": "Ethereum", "green_status": "EXCELLENT" },
    { "rank": 3, "chain": "VeChain", "green_status": "EXCELLENT", "certification": "DNV ISO14040/14044" }
  ]
}
```

## Pricing (1 unit = $0.01)

| Tier | Price | Units/Month |
|------|-------|-------------|
| Free | $0 | 50 |
| Starter | $49/mo | 500 |
| Pro | $149/mo | 2,000 |
| Agency | $349/mo | 6,000 |
| x402 | per call | unlimited |

## x402 Pay-per-Call

Autonomous AI agents pay with USDC on Base via the x402 protocol — no account, no API key.

- Endpoint: `https://tooloracle.io/x402/carbon/mcp/`
- Wallet: `0x4a4B1F45a00892542ac62562D1F2C62F579E4945`

## Data Sources

| Backend | Data |
|---------|------|
| EU ETS API | European carbon allowance prices |
| National Grid ESO | Real-time UK grid carbon intensity |
| Ember Climate | Annual electricity CO2 data, 100+ countries |
| VeChainStats | Live VeChain chain metrics |
| Chain Carbon Monitor | 50 blockchain carbon profiles |

## Part of ToolOracle

[tooloracle.io](https://tooloracle.io) — 11 products, 101 tools, all MCP-native.

## License

MIT