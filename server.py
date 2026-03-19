#!/usr/bin/env python3
"""
CarbonOracle — CO2 & Climate Intelligence MCP Server v1.0.0
Port 7001 | Part of ToolOracle Whitelabel MCP Platform

11 Tools:
  1. carbon_eu_ets_price     — Live EU Emissions Trading System (EUA) price in EUR/tCO2
  2. carbon_grid_intensity   — Real-time electricity grid carbon intensity by country
  3. carbon_grid_compare     — Compare carbon intensity across multiple countries
  4. carbon_ember_country    — Annual electricity carbon intensity by country (Ember data)
  5. carbon_ember_eu_ranking — EU country ranking by electricity carbon intensity
  6. carbon_footprint        — Estimate product/activity carbon footprint (kg CO2e)
  7. carbon_blockchain       — Carbon intensity of major blockchain networks
  8. health_check            — Status, API connectivity, tool list

Backend: Live EU ETS, National Grid ESO (UK), Ember Climate, Climatiq
"""
import os
import sys
import json
import logging
import aiohttp
from datetime import datetime, timezone

sys.path.insert(0, "/root/whitelabel")
from shared.utils.mcp_base import WhitelabelMCPServer

logger = logging.getLogger("CarbonOracle")

# ── Backend URLs ─────────────────────────────────────────────
BASE = "http://127.0.0.1"
ETS   = f"{BASE}:5175/api/v1/eu-ets"
EMBER = f"{BASE}:5170/api/v1/ember"
GRID  = f"{BASE}:5102"
CLIM  = f"{BASE}:5110/api/v1/climatiq"
CMON  = f"{BASE}:5070/api/v1/carbon"   # Chain Carbon Monitor (50 chains)

# ── HTTP Helper ───────────────────────────────────────────────
async def get(url: str) -> dict:
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    return await r.json()
                return {"error": f"HTTP {r.status}"}
    except Exception as e:
        return {"error": str(e)}

def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── Tool Handlers ─────────────────────────────────────────────

async def tool_eu_ets_price(args: dict) -> dict:
    """Live EU ETS carbon allowance price."""
    d = await get(f"{ETS}/price")
    if d.get("error"):
        return {"error": d["error"]}
    data = d.get("data", d)
    return {
        "tool": "carbon_eu_ets_price",
        "timestamp": ts(),
        "eua_price_eur": data.get("eua_price_eur"),
        "unit": "EUR/tCO2",
        "market": data.get("market", "EU ETS Phase 4"),
        "currency": "EUR",
        "source": "EU ETS",
        "summary": f"EU carbon allowance (EUA): €{data.get('eua_price_eur')} per tonne CO2"
    }

async def tool_grid_intensity(args: dict) -> dict:
    """Real-time grid carbon intensity for a country."""
    country = args.get("country", "GB").upper()
    if country in ("UK", "GB", "GBR"):
        d = await get(f"{GRID}/uk/now")
        if d.get("error"):
            return {"error": d["error"]}
        return {
            "tool": "carbon_grid_intensity",
            "timestamp": ts(),
            "country": "GB",
            "country_name": "United Kingdom",
            "intensity_gco2_kwh": d.get("intensity_gco2"),
            "forecast_gco2_kwh": d.get("forecast"),
            "index": d.get("index"),
            "unit": "gCO2/kWh",
            "realtime": True,
            "source": "National Grid ESO (carbonintensity.org.uk)",
            "summary": f"UK grid: {d.get('intensity_gco2')} gCO2/kWh ({d.get('index', 'unknown')})"
        }
    else:
        d = await get(f"{GRID}/country/{country}")
        if d.get("error"):
            return {"error": f"Country {country} not supported. Use GB/UK for UK real-time data."}
        data = d.get("data", d)
        return {
            "tool": "carbon_grid_intensity",
            "timestamp": ts(),
            "country": country,
            "intensity_gco2_kwh": data.get("intensity_gco2", data.get("co2_gkwh")),
            "renewable_pct": data.get("renewable_pct"),
            "unit": "gCO2/kWh",
            "source": "Grid Carbon API",
            "summary": f"{country} grid: {data.get('intensity_gco2', data.get('co2_gkwh'))} gCO2/kWh"
        }

async def tool_grid_compare(args: dict) -> dict:
    """Compare carbon intensity across multiple countries."""
    d = await get(f"{GRID}/compare")
    if d.get("error"):
        return {"error": d["error"]}
    countries = d.get("data", [])
    # Sort by intensity
    countries_sorted = sorted(countries, key=lambda x: x.get("intensity_gco2", 999))
    return {
        "tool": "carbon_grid_compare",
        "timestamp": ts(),
        "countries": countries_sorted,
        "cleanest": countries_sorted[0] if countries_sorted else None,
        "dirtiest": countries_sorted[-1] if countries_sorted else None,
        "count": len(countries_sorted),
        "unit": "gCO2/kWh",
        "source": "Grid Carbon API",
        "summary": f"Compared {len(countries_sorted)} countries. Cleanest: {countries_sorted[0].get('country')} ({countries_sorted[0].get('intensity_gco2')} gCO2/kWh)" if countries_sorted else "No data"
    }

async def tool_ember_country(args: dict) -> dict:
    """Annual electricity carbon intensity by country (Ember Climate data)."""
    iso = args.get("iso", "DEU").upper()
    # Normalize common codes
    mapping = {"DE": "DEU", "FR": "FRA", "UK": "GBR", "GB": "GBR",
               "ES": "ESP", "IT": "ITA", "PL": "POL", "NL": "NLD",
               "SE": "SWE", "NO": "NOR", "AT": "AUT", "CH": "CHE",
               "US": "USA", "CN": "CHN"}
    iso = mapping.get(iso, iso)
    d = await get(f"{EMBER}/intensity/{iso}")
    if d.get("error"):
        return {"error": d["error"]}
    data = d.get("data", d)
    return {
        "tool": "carbon_ember_country",
        "timestamp": ts(),
        "country": data.get("country"),
        "iso": data.get("iso"),
        "co2_intensity_gkwh": data.get("co2_intensity_gkwh"),
        "renewable_pct": data.get("renewable_pct"),
        "fossil_pct": data.get("fossil_pct"),
        "year": data.get("year"),
        "unit": "gCO2/kWh",
        "source": "Ember Climate 2024",
        "summary": f"{data.get('country')}: {data.get('co2_intensity_gkwh')} gCO2/kWh ({data.get('renewable_pct')}% renewable) — {data.get('year')}"
    }

async def tool_ember_eu_ranking(args: dict) -> dict:
    """EU country ranking by electricity carbon intensity."""
    top_n = min(args.get("top_n", 10), 27)
    d = await get(f"{EMBER}/eu-summary")
    if d.get("error"):
        return {"error": d["error"]}
    countries = d.get("data", {}).get("countries", [])
    # Sort ascending (cleanest first)
    countries_sorted = sorted(countries, key=lambda x: x.get("co2_gkwh", 999))
    top = countries_sorted[:top_n]
    return {
        "tool": "carbon_ember_eu_ranking",
        "timestamp": ts(),
        "ranking": [
            {"rank": i+1, "country": c.get("country"), "iso": c.get("iso"),
             "co2_gkwh": c.get("co2_gkwh"), "year": c.get("year")}
            for i, c in enumerate(top)
        ],
        "total_countries": len(countries),
        "unit": "gCO2/kWh",
        "source": "Ember Climate 2024",
        "summary": f"Top {len(top)} cleanest EU grids. #1: {top[0].get('country')} ({top[0].get('co2_gkwh')} gCO2/kWh)" if top else "No data"
    }

async def tool_carbon_footprint(args: dict) -> dict:
    """Estimate carbon footprint for common products/activities."""
    # Built-in estimates (kg CO2e) — industry standard averages
    ESTIMATES = {
        "laptop": {"kg_co2e": 300, "category": "Electronics", "note": "Lifecycle manufacturing + 3yr use"},
        "smartphone": {"kg_co2e": 70, "category": "Electronics", "note": "Lifecycle manufacturing + 2yr use"},
        "tshirt": {"kg_co2e": 6.5, "category": "Clothing", "note": "Cotton, global avg supply chain"},
        "jeans": {"kg_co2e": 33, "category": "Clothing", "note": "Cotton denim production"},
        "flight_short": {"kg_co2e": 255, "category": "Transport", "note": "Economy, <1500km, per passenger"},
        "flight_long": {"kg_co2e": 1950, "category": "Transport", "note": "Economy, intercontinental, per passenger"},
        "car_year": {"kg_co2e": 4600, "category": "Transport", "note": "Average petrol car, 15,000km/yr"},
        "ev_year": {"kg_co2e": 900, "category": "Transport", "note": "Electric vehicle, EU grid avg"},
        "beef_kg": {"kg_co2e": 60, "category": "Food", "note": "Per kg beef, global avg"},
        "chicken_kg": {"kg_co2e": 6, "category": "Food", "note": "Per kg chicken"},
        "bitcoin_tx": {"kg_co2e": 0.7, "category": "Crypto", "note": "Per transaction, PoW estimate 2024"},
        "ethereum_tx": {"kg_co2e": 0.002, "category": "Crypto", "note": "Per transaction, post-Merge PoS"},
        "streaming_hour": {"kg_co2e": 0.036, "category": "Digital", "note": "Per hour HD video streaming"},
        "email": {"kg_co2e": 0.004, "category": "Digital", "note": "Per email with attachment"},
    }
    product = args.get("product", "").lower().strip()
    quantity = max(1, args.get("quantity", 1))

    if product in ESTIMATES:
        est = ESTIMATES[product]
        total = round(est["kg_co2e"] * quantity, 2)
        return {
            "tool": "carbon_footprint",
            "timestamp": ts(),
            "product": product,
            "quantity": quantity,
            "kg_co2e_per_unit": est["kg_co2e"],
            "total_kg_co2e": total,
            "category": est["category"],
            "note": est["note"],
            "equivalent_eu_ets_eur": round(total / 1000 * 73.25, 4),
            "source": "Industry standard lifecycle averages",
            "summary": f"{quantity}x {product}: {total} kg CO2e (≈ €{round(total/1000*73.25, 3)} at current EUA price)"
        }
    else:
        available = list(ESTIMATES.keys())
        return {
            "tool": "carbon_footprint",
            "error": f"Unknown product '{product}'",
            "available_products": available,
            "tip": "Use one of the available products, or request quantity > 1"
        }

async def tool_blockchain_carbon(args: dict) -> dict:
    """Carbon intensity of major blockchain networks."""
    d = await get(f"{GRID}/blockchain/ethereum")
    chains = {
        "ethereum": {"gco2_tx": 0.002, "consensus": "PoS", "note": "Post-Merge (Sep 2022), ~99.95% reduction"},
        "bitcoin": {"gco2_tx": 700, "consensus": "PoW", "note": "Energy-intensive mining, varies with grid mix"},
        "polygon": {"gco2_tx": 0.0003, "consensus": "PoS", "note": "Highly efficient, carbon offset program"},
        "solana": {"gco2_tx": 0.0006, "consensus": "PoS/PoH", "note": "Very efficient consensus mechanism"},
        "xrpl": {"gco2_tx": 0.0008, "consensus": "Federated", "note": "Carbon-neutral, federated consensus"},
        "gnosis": {"gco2_tx": 0.0002, "consensus": "PoS", "note": "Sidechain, low energy footprint"},
    }
    chain = args.get("chain", "ethereum").lower()
    if chain in chains:
        c = chains[chain]
        return {
            "tool": "carbon_blockchain",
            "timestamp": ts(),
            "chain": chain,
            "gco2_per_tx": c["gco2_tx"],
            "unit": "gCO2/transaction",
            "consensus": c["consensus"],
            "note": c["note"],
            "comparison_vs_bitcoin": round(c["gco2_tx"] / chains["bitcoin"]["gco2_tx"] * 100, 4),
            "source": "Crypto Carbon Ratings Institute + Chain reports",
            "summary": f"{chain}: {c['gco2_tx']} gCO2/tx ({c['consensus']}) — {c['note']}"
        }
    else:
        return {
            "tool": "carbon_blockchain",
            "all_chains": chains,
            "error": f"Chain '{chain}' not found",
            "available": list(chains.keys())
        }

async def tool_health(args: dict) -> dict:
    """CarbonOracle health check."""
    ets_ok = not (await get(f"{ETS}/health")).get("error")
    ember_ok = not (await get(f"{EMBER}/health")).get("error")
    grid_ok = not (await get(f"{GRID}/health")).get("error")
    return {
        "status": "healthy" if all([ets_ok, ember_ok, grid_ok]) else "degraded",
        "product": "CarbonOracle",
        "version": "1.0.0",
        "platform": "ToolOracle",
        "backends": {
            "eu_ets": "ok" if ets_ok else "degraded",
            "ember_climate": "ok" if ember_ok else "degraded",
            "carbon_grid": "ok" if grid_ok else "degraded",
        },
        "tools": 8,
        "timestamp": ts()
    }


async def tool_chain_carbon(args: dict) -> dict:
    """Carbon data for any specific blockchain."""
    symbol = args.get("symbol", "ETH").upper()
    d = await get(f"{CMON}/chain/{symbol}")
    if d.get("error") or not d.get("chain"):
        # Try summary to find it
        return {"error": f"Chain '{symbol}' not found. Use carbon_chain_ranking to see all 50 available chains."}
    return {
        "tool": "carbon_chain",
        "timestamp": ts(),
        "chain": d.get("chain"),
        "symbol": d.get("symbol"),
        "category": d.get("category"),
        "consensus": d.get("consensus"),
        "green_status": d.get("green_status"),
        "green_score": d.get("green_score"),
        "co2_tonnes_year": d.get("co2_tonnes_year"),
        "energy_per_tx_kwh": d.get("energy_per_tx_kwh"),
        "renewable_energy_pct": d.get("renewable_energy_percent"),
        "ghg_scope": d.get("ghg_scope"),
        "tx_24h": d.get("tx_24h"),
        "certification": d.get("certification"),
        "mica_art66_supported": d.get("mica_art66_supported"),
        "data_quality": d.get("data_quality"),
        "data_source": d.get("data_source"),
        "source": "Chain Carbon Monitor v2.0",
        "summary": f"{d.get('chain')} ({symbol}): {d.get('green_status')} — {d.get('co2_tonnes_year',0):.4f}t CO2/yr, {d.get('energy_per_tx_kwh')} kWh/tx. {('DNV certified.' if d.get('certification') else '')}"
    }

async def tool_chain_ranking(args: dict) -> dict:
    """Rank all 50 blockchains by carbon footprint."""
    d = await get(f"{CMON}/chains")
    if d.get("error"):
        return {"error": d["error"]}
    chains = d.get("chains", [])
    
    # Filter options
    filter_status = args.get("filter_status")  # EXCELLENT, HIGH_IMPACT, CRITICAL
    mica_only = args.get("mica_art66_only", False)
    top_n = min(args.get("top_n", 20), 50)
    
    if filter_status:
        chains = [c for c in chains if c.get("green_status") == filter_status.upper()]
    if mica_only:
        chains = [c for c in chains if c.get("mica_art66_supported")]
    
    # Sort: cleanest first (by co2_tonnes_year, then green_score desc)
    chains_sorted = sorted(chains, 
        key=lambda x: (x.get("co2_tonnes_year", 0), -x.get("green_score", 0)))
    top = chains_sorted[:top_n]
    
    return {
        "tool": "carbon_chain_ranking",
        "timestamp": ts(),
        "total_chains": len(chains),
        "showing": len(top),
        "ranking": [
            {
                "rank": i+1,
                "chain": c.get("chain"),
                "symbol": c.get("symbol"),
                "green_status": c.get("green_status"),
                "green_score": c.get("green_score"),
                "co2_tonnes_year": c.get("co2_tonnes_year"),
                "energy_per_tx_kwh": c.get("energy_per_tx_kwh"),
                "consensus": c.get("consensus"),
                "certification": c.get("certification"),
                "mica_art66": c.get("mica_art66_supported"),
            }
            for i, c in enumerate(top)
        ],
        "filters_applied": {
            "status": filter_status,
            "mica_art66_only": mica_only
        },
        "source": "Chain Carbon Monitor v2.0 (50 chains)",
        "summary": f"Top {len(top)} cleanest chains. #1: {top[0].get('chain')} ({top[0].get('green_status')})" if top else "No chains found"
    }

async def tool_vechain(args: dict) -> dict:
    """VeChain deep carbon profile — DNV ISO14040/14044 certified."""
    d = await get(f"{CMON}/chain/VET")
    if not d.get("chain"):
        return {"error": "VeChain data unavailable"}
    return {
        "tool": "carbon_vechain",
        "timestamp": ts(),
        "chain": "VeChain",
        "symbol": "VET",
        "consensus": d.get("consensus"),
        "certification": d.get("certification"),
        "certification_note": "DNV ISO14040/14044 — independent lifecycle carbon assessment, gold standard",
        "green_status": d.get("green_status"),
        "green_score": d.get("green_score"),
        "co2_tonnes_year": d.get("co2_tonnes_year"),
        "energy_kwh_year": d.get("energy_kwh_year"),
        "energy_per_tx_kwh": d.get("energy_per_tx_kwh"),
        "renewable_energy_pct": d.get("renewable_energy_percent"),
        "validators": d.get("validators"),
        "tx_24h": d.get("tx_24h"),
        "ghg_scope_1_pct": d.get("ghg_scope", {}).get("s1_pct"),
        "ghg_scope_2_pct": d.get("ghg_scope", {}).get("s2_pct"),
        "ghg_scope_2_tonnes": d.get("ghg_scope", {}).get("s2_t"),
        "ghg_scope_3_pct": d.get("ghg_scope", {}).get("s3_pct"),
        "mica_art66_supported": d.get("mica_art66_supported"),
        "data_quality": d.get("data_quality"),
        "use_cases": [
            "Supply chain carbon tracking",
            "Product lifecycle ESG reporting",
            "CSRD Scope 3 evidence",
            "Green NFT / carbon credit tokenization"
        ],
        "source": f"VeChainStats API — {d.get('data_source')}",
        "summary": (
            f"VeChain: {d.get('green_status')}, {d.get('co2_tonnes_year',0):.2f}t CO2/yr total. "
            f"{d.get('energy_per_tx_kwh')} kWh/tx. "
            f"DNV ISO14040/14044 certified. MiCA Art.66: {'Yes' if d.get('mica_art66_supported') else 'No'}."
        )
    }

# ── Server Setup ──────────────────────────────────────────────
server = WhitelabelMCPServer(
    product_name="CarbonOracle",
    product_slug="carbon",
    version="1.0.0",
    port_mcp=7001,
    port_health=7002,
)

server.register_tool(
    name="carbon_eu_ets_price",
    description="Live EU Emissions Trading System price. Returns EUA (EU Allowance) price in EUR per tonne CO2. Essential for carbon cost calculations and CSRD reporting.",
    parameters={"type": "object", "properties": {}},
    handler=tool_eu_ets_price,
    credits=2,
)
server.register_tool(
    name="carbon_grid_intensity",
    description="Real-time electricity grid carbon intensity by country in gCO2/kWh. UK: live from National Grid ESO. Other countries: latest grid data. Use for scope 2 emissions, green computing decisions.",
    parameters={"type": "object", "properties": {
        "country": {"type": "string", "description": "Country code: GB/UK for real-time UK, or DE/FR/NO/SE/CH etc.", "default": "GB"}
    }},
    handler=tool_grid_intensity,
    credits=2,
)
server.register_tool(
    name="carbon_grid_compare",
    description="Compare electricity carbon intensity across 20+ countries. Ranked from cleanest to dirtiest. Useful for data center location decisions and scope 2 reporting.",
    parameters={"type": "object", "properties": {}},
    handler=tool_grid_compare,
    credits=3,
)
server.register_tool(
    name="carbon_ember_country",
    description="Annual electricity carbon intensity for any country from Ember Climate data (2024). Includes renewable %, fossil %, gCO2/kWh. Covers 100+ countries.",
    parameters={"type": "object", "properties": {
        "iso": {"type": "string", "description": "ISO country code: DEU, FRA, USA, CHN, GBR etc. Also accepts 2-letter: DE, FR, US", "default": "DEU"}
    }, "required": ["iso"]},
    handler=tool_ember_country,
    credits=2,
)
server.register_tool(
    name="carbon_ember_eu_ranking",
    description="EU country ranking by electricity carbon intensity (Ember Climate 2024). Shows cleanest to dirtiest EU grids. Useful for sustainability benchmarking.",
    parameters={"type": "object", "properties": {
        "top_n": {"type": "integer", "description": "Number of countries to return (max 27)", "default": 10}
    }},
    handler=tool_ember_eu_ranking,
    credits=3,
)
server.register_tool(
    name="carbon_footprint",
    description="Estimate carbon footprint (kg CO2e) for common products and activities: laptop, smartphone, flight, car, beef, bitcoin transaction, streaming hour, email, and more.",
    parameters={"type": "object", "properties": {
        "product": {"type": "string", "description": "Product or activity: laptop, smartphone, tshirt, jeans, flight_short, flight_long, car_year, ev_year, beef_kg, chicken_kg, bitcoin_tx, ethereum_tx, streaming_hour, email"},
        "quantity": {"type": "integer", "description": "Number of units (default 1)", "default": 1}
    }, "required": ["product"]},
    handler=tool_carbon_footprint,
    credits=1,
)
server.register_tool(
    name="carbon_blockchain",
    description="Carbon intensity of major blockchain networks in gCO2 per transaction. Covers Ethereum (PoS), Bitcoin (PoW), Polygon, Solana, XRPL, Gnosis. Useful for Web3 sustainability reporting.",
    parameters={"type": "object", "properties": {
        "chain": {"type": "string", "description": "Blockchain: ethereum, bitcoin, polygon, solana, xrpl, gnosis", "default": "ethereum"}
    }},
    handler=tool_blockchain_carbon,
    credits=1,
)
server.register_tool(
    name="health_check",
    description="CarbonOracle health status. Returns backend connectivity, tool list, version.",
    parameters={"type": "object", "properties": {}},
    handler=tool_health,
    credits=0,
)
server.register_tool(
    name="carbon_chain",
    description="Carbon footprint data for any specific blockchain by symbol. Returns green_status, gCO2/yr, kWh/tx, GHG scope breakdown, certification, MiCA Art.66 flag. Covers 50 chains including Ethereum, Bitcoin, Solana, VeChain, Polygon, XRPL, Cardano and more.",
    parameters={"type": "object", "properties": {
        "symbol": {"type": "string", "description": "Chain symbol: ETH, BTC, VET, SOL, MATIC, ADA, XRP, BNB, AVAX, DOT, ARB, OP etc.", "default": "ETH"}
    }, "required": ["symbol"]},
    handler=tool_chain_carbon,
    credits=2,
)
server.register_tool(
    name="carbon_chain_ranking",
    description="Rank all 50 blockchains by carbon footprint from cleanest to most polluting. Filter by green_status (EXCELLENT/HIGH_IMPACT/CRITICAL) or MiCA Art.66 compliance. Essential for ESG chain selection and sustainability reporting.",
    parameters={"type": "object", "properties": {
        "top_n": {"type": "integer", "description": "Number of chains to return (max 50)", "default": 20},
        "filter_status": {"type": "string", "description": "Filter by status: EXCELLENT, HIGH_IMPACT, CRITICAL"},
        "mica_art66_only": {"type": "boolean", "description": "Show only MiCA Art.66 supported chains", "default": False}
    }},
    handler=tool_chain_ranking,
    credits=3,
)
server.register_tool(
    name="carbon_vechain",
    description="VeChain deep carbon profile. The only major blockchain with DNV ISO14040/14044 certification (gold standard lifecycle assessment). Proof of Authority consensus, 101 validators. Used for supply chain ESG, CSRD Scope 3, carbon credit tokenization. MiCA Art.66 supported.",
    parameters={"type": "object", "properties": {}},
    handler=tool_vechain,
    credits=2,
)

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run())
