"""
market_intel.py — PluggedIN Global Market Intelligence Engine
Mines Reddit, country-specific forums, and trade publications to find
what different countries NEED but struggle to source or afford.

This feeds two businesses:
  1. TradeBridge — B2B brokerage (connect buyer + seller, take commission)
  2. SourcedStore — Ecommerce (source products solving real pain points)

Intelligence by country → pain point extraction → product/supplier matching
→ buyer discovery → deal facilitation

Actors used:
  - parseforge/reddit-posts-scraper ($0.003/result, 99.7% success)
  - harvestapi/linkedin-company-search ($0.001/result, 99.8% success)
  - TinyFish (country-specific trade forums, import/export boards)
"""

import os
import json
import time
import requests
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE_PLUGGEDIN")
AIRTABLE_BASE_URL = "https://api.airtable.com/v0"
APIFY_BASE = "https://api.apify.com/v2"


# ─────────────────────────────────────────────
# COUNTRY INTELLIGENCE CONFIG
# ─────────────────────────────────────────────

# Country → subreddits + trade keywords + what they typically need
COUNTRY_INTEL_MAP = {
    "nigeria": {
        "subreddits": ["r/Nigeria", "r/nairaland", "r/Nigeria_economy", "r/Lagos"],
        "trade_keywords": ["supply shortage", "where to buy", "hard to find", "importing", "need supplier"],
        "known_needs": ["construction materials", "generators", "solar panels", "medical equipment", "food processing machinery"],
        "export_strengths": ["crude oil", "cocoa", "sesame", "cashew", "palm oil", "ginger", "timber"],
        "currency": "NGN", "trade_region": "West Africa",
    },
    "ghana": {
        "subreddits": ["r/ghana", "r/accra"],
        "trade_keywords": ["shortage", "sourcing", "import", "need", "looking for supplier"],
        "known_needs": ["cocoa processing equipment", "construction equipment", "agricultural machinery", "textiles"],
        "export_strengths": ["cocoa", "gold", "timber", "shea butter", "cashew", "tuna"],
        "currency": "GHS", "trade_region": "West Africa",
    },
    "morocco": {
        "subreddits": ["r/Morocco", "r/maroc"],
        "trade_keywords": ["importation", "fournisseur", "besoin", "manque", "sourcing"],
        "known_needs": ["electronics", "machinery", "raw materials", "pharmaceutical"],
        "export_strengths": ["phosphates", "argan oil", "sardines", "textiles", "fertilizers", "spices"],
        "currency": "MAD", "trade_region": "North Africa",
    },
    "india": {
        "subreddits": ["r/india", "r/IndiaBusiness", "r/IndiaInvestments", "r/bangalore", "r/mumbai"],
        "trade_keywords": ["sourcing", "supplier needed", "import", "manufacturing", "bulk order"],
        "known_needs": ["electronic components", "chemicals", "crude oil", "machinery", "fertilizers"],
        "export_strengths": ["pharmaceuticals", "IT services", "textiles", "spices", "tea", "rice", "cotton", "gems"],
        "currency": "INR", "trade_region": "South Asia",
    },
    "germany": {
        "subreddits": ["r/germany", "r/de", "r/AskAGerman"],
        "trade_keywords": ["Lieferant", "Bezugsquelle", "import", "Mangel", "supplier"],
        "known_needs": ["raw materials", "rare earth", "agricultural products", "energy alternatives"],
        "export_strengths": ["machinery", "vehicles", "chemicals", "electronics", "pharmaceuticals"],
        "currency": "EUR", "trade_region": "Western Europe",
    },
    "france": {
        "subreddits": ["r/france", "r/paris", "r/FranceEco"],
        "trade_keywords": ["fournisseur", "approvisionnement", "importation", "pénurie", "sourcing"],
        "known_needs": ["food ingredients", "cocoa", "coffee", "agricultural commodities", "textiles"],
        "export_strengths": ["luxury goods", "wine", "aerospace", "pharmaceuticals", "nuclear tech"],
        "currency": "EUR", "trade_region": "Western Europe",
    },
    "uae": {
        "subreddits": ["r/dubai", "r/UAE", "r/abudhabi"],
        "trade_keywords": ["supplier", "import", "sourcing", "bulk", "trade"],
        "known_needs": ["food", "construction materials", "gold", "consumer goods", "technology"],
        "export_strengths": ["oil", "petroleum", "aluminium", "re-export hub for Asia/Africa"],
        "currency": "AED", "trade_region": "Middle East",
    },
    "brazil": {
        "subreddits": ["r/brasil", "r/brdev", "r/investimentos"],
        "trade_keywords": ["importar", "fornecedor", "escassez", "comprar", "sourcing"],
        "known_needs": ["electronics", "machinery", "chemicals", "fertilizers", "pharmaceuticals"],
        "export_strengths": ["soybeans", "coffee", "sugar", "ethanol", "iron ore", "beef", "poultry"],
        "currency": "BRL", "trade_region": "South America",
    },
    "turkey": {
        "subreddits": ["r/Turkey", "r/istanbul", "r/turkish"],
        "trade_keywords": ["tedarik", "ithalat", "kaynak", "supplier", "import"],
        "known_needs": ["natural gas", "crude oil", "gold", "machinery parts"],
        "export_strengths": ["textiles", "automobiles", "electronics", "steel", "chemicals", "hazelnuts", "marble"],
        "currency": "TRY", "trade_region": "Eurasia",
    },
    "uk": {
        "subreddits": ["r/unitedkingdom", "r/AskUK", "r/UKPersonalFinance", "r/entrepreneursUK"],
        "trade_keywords": ["shortage", "supplier", "where to buy", "sourcing", "import"],
        "known_needs": ["construction materials", "food", "energy", "medical supplies", "technology"],
        "export_strengths": ["financial services", "pharmaceuticals", "aerospace", "education", "creative industries"],
        "currency": "GBP", "trade_region": "Western Europe",
    },
    "saudi_arabia": {
        "subreddits": ["r/saudiarabia", "r/Saudi"],
        "trade_keywords": ["supplier", "import", "sourcing", "food supply", "trading"],
        "known_needs": ["food", "water tech", "construction", "defence", "consumer goods"],
        "export_strengths": ["oil", "petrochemicals", "plastics", "fertilizers", "dates"],
        "currency": "SAR", "trade_region": "Middle East",
    },
    "indonesia": {
        "subreddits": ["r/indonesia", "r/Jakarta"],
        "trade_keywords": ["supplier", "impor", "beli", "cari", "sourcing"],
        "known_needs": ["machinery", "chemicals", "steel", "wheat", "technology"],
        "export_strengths": ["palm oil", "coal", "rubber", "coffee", "cocoa", "nickel", "timber"],
        "currency": "IDR", "trade_region": "Southeast Asia",
    },
}

# Trade categories with typical deal sizes and commission ranges
TRADE_CATEGORIES = {
    "agricultural_commodities": {
        "products": ["cocoa", "coffee", "cashew", "sesame", "palm oil", "shea butter", "groundnuts", "soybeans", "rice", "wheat"],
        "typical_deal_size": "£20,000 - £500,000",
        "commission_pct": 2.5,
        "deal_type": "commodity",
        "key_buyers": ["food manufacturers", "chocolate companies", "cosmetics", "confectionery"],
    },
    "construction_materials": {
        "products": ["cement", "steel rebar", "timber", "copper wire", "aluminium", "glass", "tiles", "PVC"],
        "typical_deal_size": "£50,000 - £2,000,000",
        "commission_pct": 2.0,
        "deal_type": "commodity",
        "key_buyers": ["construction companies", "developers", "contractors", "governments"],
    },
    "industrial_machinery": {
        "products": ["generators", "processing equipment", "agricultural machinery", "manufacturing equipment", "solar panels"],
        "typical_deal_size": "£10,000 - £500,000",
        "commission_pct": 3.0,
        "deal_type": "equipment",
        "key_buyers": ["factories", "farms", "utilities", "governments"],
    },
    "pharmaceuticals_health": {
        "products": ["generic medicines", "medical devices", "PPE", "supplements", "vaccines", "diagnostics"],
        "typical_deal_size": "£5,000 - £200,000",
        "commission_pct": 3.5,
        "deal_type": "regulated",
        "key_buyers": ["hospitals", "pharmacies", "NGOs", "governments"],
    },
    "consumer_goods_ecom": {
        "products": ["electronics", "fashion", "home goods", "beauty", "toys", "pet products", "kitchen"],
        "typical_deal_size": "£500 - £50,000",
        "commission_pct": 0,  # margin model, not commission
        "deal_type": "ecommerce",
        "key_buyers": ["direct consumer via Amazon/Shopify/TikTok"],
    },
    "natural_resources": {
        "products": ["timber", "stone", "sand", "clay", "mineral ore", "crude oil", "LNG"],
        "typical_deal_size": "£100,000 - £10,000,000",
        "commission_pct": 1.5,
        "deal_type": "commodity",
        "key_buyers": ["refineries", "manufacturers", "energy companies"],
    },
    "food_ingredients": {
        "products": ["spices", "herbs", "flavourings", "oils", "starches", "emulsifiers", "proteins"],
        "typical_deal_size": "£5,000 - £100,000",
        "commission_pct": 3.0,
        "deal_type": "commodity",
        "key_buyers": ["food manufacturers", "restaurants", "retailers", "wholesalers"],
    },
}


# ─────────────────────────────────────────────
# APIFY RUNNER (shared utility)
# ─────────────────────────────────────────────

def _run_apify_actor(actor_id: str, input_data: dict, timeout_secs: int = 90) -> list:
    headers = {"Authorization": f"Bearer {APIFY_TOKEN}", "Content-Type": "application/json"}
    run_url = f"{APIFY_BASE}/acts/{actor_id}/runs"
    resp = requests.post(run_url, headers=headers, json=input_data, timeout=30)
    resp.raise_for_status()
    run_id = resp.json()["data"]["id"]
    dataset_id = resp.json()["data"]["defaultDatasetId"]

    elapsed = 0
    while elapsed < timeout_secs:
        time.sleep(5)
        elapsed += 5
        status_resp = requests.get(f"{APIFY_BASE}/actor-runs/{run_id}", headers=headers, timeout=10)
        status = status_resp.json()["data"]["status"]
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break

    if status != "SUCCEEDED":
        return []

    data_resp = requests.get(f"{APIFY_BASE}/datasets/{dataset_id}/items?limit=200", headers=headers, timeout=30)
    return data_resp.json() if data_resp.ok else []


def _call_claude_haiku(prompt: str, system: str = "You are a global trade intelligence analyst.", max_tokens: int = 1500) -> str:
    from lib.ai_client import call_ai
    return call_ai("market_intel", system=system, prompt=prompt, max_tokens=max_tokens)


def _tinyfish_fetch(url: str, extract_prompt: str) -> dict:
    if not TINYFISH_API_KEY:
        return {"error": "TINYFISH_API_KEY not set"}
    headers = {"Authorization": f"Bearer {TINYFISH_API_KEY}", "Content-Type": "application/json"}
    payload = {"url": url, "prompt": extract_prompt, "format": "json"}
    try:
        resp = requests.post("https://api.tinyfish.io/v1/extract", headers=headers, json=payload, timeout=45)
        return resp.json() if resp.ok else {"error": resp.text}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# REDDIT DEMAND MINING
# ─────────────────────────────────────────────

def mine_reddit_demand(country: str, max_posts: int = 50) -> list[dict]:
    """
    Scrape Reddit posts from country-specific subreddits.
    Extract demand signals — what people need, can't source, complain about.
    Uses parseforge/reddit-posts-scraper ($0.003/result, 99.7% success).
    """
    config = COUNTRY_INTEL_MAP.get(country.lower())
    if not config:
        print(f"[market_intel] No config for country: {country}")
        return []

    all_posts = []

    for subreddit in config["subreddits"][:3]:  # cap at 3 subreddits per country
        sub_name = subreddit.replace("r/", "")
        print(f"[reddit] Mining {subreddit} for demand signals...")

        for keyword in config["trade_keywords"][:3]:  # cap at 3 keywords
            posts = _run_apify_actor(
                actor_id="parseforge/reddit-posts-scraper",
                input_data={
                    "subreddits": [sub_name],
                    "searchQuery": keyword,
                    "maxPosts": 10,
                    "sort": "relevance",
                }
            )
            for post in posts:
                all_posts.append({
                    "country": country,
                    "subreddit": subreddit,
                    "keyword": keyword,
                    "title": post.get("title", ""),
                    "content": post.get("selftext", post.get("body", ""))[:500],
                    "score": post.get("score", 0),
                    "comments": post.get("numComments", 0),
                    "url": post.get("url", ""),
                    "created": post.get("createdAt", ""),
                })

    return all_posts


def extract_demand_signals(posts: list[dict], country: str) -> list[dict]:
    """
    Use Claude Haiku to extract structured demand signals from raw Reddit posts.
    Returns: list of {product, need_description, urgency, estimated_volume, buyer_type}
    """
    if not posts:
        return []

    config = COUNTRY_INTEL_MAP.get(country.lower(), {})
    known_needs = config.get("known_needs", [])

    # Compile posts into a text block for analysis
    posts_text = "\n---\n".join([
        f"POST: {p['title']}\n{p['content'][:300]}"
        for p in sorted(posts, key=lambda x: x.get("score", 0), reverse=True)[:20]
    ])

    prompt = f"""
You are a global trade intelligence analyst.

Country: {country.upper()}
Known needs for this country: {', '.join(known_needs)}

Below are Reddit posts from {country} subreddits. Extract specific demand signals —
products or commodities that people need, struggle to source, or complain about being expensive/unavailable.

POSTS:
{posts_text}

For each distinct demand signal you find, output:
PRODUCT: [specific product or commodity]
NEED: [what they specifically need / why they can't get it]
URGENCY: [High/Medium/Low]
VOLUME: [estimated scale: tonnes, units, £ value if mentioned]
BUYER_TYPE: [individual / SME / corporation / government]
TRADE_CATEGORY: [agricultural_commodities / construction_materials / industrial_machinery / pharmaceuticals_health / consumer_goods_ecom / natural_resources / food_ingredients]
BROKERAGE_PLAY: [Yes/No — is this a B2B deal we can broker?]
ECOM_PLAY: [Yes/No — could we source and sell this as an ecom product?]
---
(repeat for each signal)

Only include specific, actionable signals. Ignore vague complaints. Focus on scalable opportunities.
Output at minimum 3 signals, maximum 8.
"""

    raw = _call_claude_haiku(prompt, system="You are a precise trade intelligence analyst. Extract only specific, actionable demand signals.")
    signals = []

    for block in raw.split("---"):
        if "PRODUCT:" not in block:
            continue
        lines = {}
        for line in block.strip().split("\n"):
            if ":" in line:
                key, *val = line.split(":")
                lines[key.strip()] = ":".join(val).strip()

        signals.append({
            "country": country,
            "product": lines.get("PRODUCT", ""),
            "need_description": lines.get("NEED", ""),
            "urgency": lines.get("URGENCY", "Medium"),
            "volume": lines.get("VOLUME", "Unknown"),
            "buyer_type": lines.get("BUYER_TYPE", "SME"),
            "trade_category": lines.get("TRADE_CATEGORY", ""),
            "brokerage_play": lines.get("BROKERAGE_PLAY", "No") == "Yes",
            "ecom_play": lines.get("ECOM_PLAY", "No") == "Yes",
            "discovered_at": date.today().isoformat(),
            "source": "Reddit",
        })

    return signals


# ─────────────────────────────────────────────
# TRADE FORUM & B2B BOARD MINING (TinyFish)
# ─────────────────────────────────────────────

TRADE_BOARDS = {
    "made_in_china": "https://www.made-in-china.com/tradeshow/",
    "ec21_buying": "https://www.ec21.com/buying-leads/",
    "tradekey_buyers": "https://www.tradekey.com/buy/",
    "alibaba_rfq": "https://sourcing.alibaba.com/",
    "global_sources_buyers": "https://www.globalsources.com/SOURCES/BUYINGLEADS.HTM",
}

def mine_trade_boards() -> list[dict]:
    """
    Scrape international trade boards for active buying leads.
    These are businesses ACTIVELY looking to buy — hottest possible signal.
    Uses TinyFish browser.
    """
    extract_prompt = """
Extract all buying leads / purchase inquiries visible on this page.
For each buying lead return:
- product: what they want to buy
- quantity: how much (weight, units, value)
- buyer_country: where they're from
- deadline: when they need it
- buyer_type: company type if visible
- contact_url: link to their inquiry
Return as a JSON array.
"""
    all_leads = []

    for board_name, url in TRADE_BOARDS.items():
        print(f"[trade_boards] Mining: {board_name}")
        data = _tinyfish_fetch(url, extract_prompt)
        items = data if isinstance(data, list) else data.get("results", [])

        for item in items:
            if item.get("product"):
                all_leads.append({
                    "source": board_name,
                    "product": item.get("product", ""),
                    "quantity": item.get("quantity", ""),
                    "buyer_country": item.get("buyer_country", ""),
                    "deadline": item.get("deadline", ""),
                    "buyer_type": item.get("buyer_type", ""),
                    "contact_url": item.get("contact_url", ""),
                    "discovered_at": date.today().isoformat(),
                    "brokerage_play": True,
                    "trade_category": _classify_product(item.get("product", "")),
                })

    return all_leads


def _classify_product(product_name: str) -> str:
    """Quick classification of a product into a trade category."""
    p = product_name.lower()
    if any(w in p for w in ["cocoa", "coffee", "cashew", "sesame", "palm", "soya", "rice", "wheat", "corn", "groundnut"]):
        return "agricultural_commodities"
    if any(w in p for w in ["cement", "steel", "timber", "copper", "aluminium", "tile", "brick", "rebar"]):
        return "construction_materials"
    if any(w in p for w in ["machine", "generator", "equipment", "solar", "pump", "motor", "compressor"]):
        return "industrial_machinery"
    if any(w in p for w in ["medicine", "pharmaceutical", "medical", "drug", "health", "ppe", "supplement"]):
        return "pharmaceuticals_health"
    if any(w in p for w in ["spice", "herb", "flavour", "vanilla", "pepper", "ginger", "turmeric", "cinnamon"]):
        return "food_ingredients"
    if any(w in p for w in ["oil", "gas", "ore", "mineral", "coal", "timber", "wood"]):
        return "natural_resources"
    return "consumer_goods_ecom"


# ─────────────────────────────────────────────
# LINKEDIN BUYER DISCOVERY
# ─────────────────────────────────────────────

def find_buyers_on_linkedin(product: str, buyer_types: list[str], countries: list[str]) -> list[dict]:
    """
    Search LinkedIn for companies that would buy a specific product.
    Uses harvestapi/linkedin-company-search ($0.001/result, 99.8% success).
    Returns company profiles with contact details.
    """
    buyers = []

    for buyer_type in buyer_types[:2]:  # cap to control cost
        for country in countries[:3]:
            search_query = f"{product} {buyer_type} {country}"
            print(f"[linkedin] Searching: {search_query}")

            results = _run_apify_actor(
                actor_id="harvestapi/linkedin-company-search",
                input_data={
                    "query": search_query,
                    "maxResults": 10,
                    "country": country,
                }
            )

            for company in results:
                buyers.append({
                    "company_name": company.get("name", ""),
                    "industry": company.get("industry", ""),
                    "location": company.get("location", country),
                    "employee_count": company.get("employeeCount", ""),
                    "website": company.get("website", ""),
                    "linkedin_url": company.get("url", ""),
                    "description": company.get("description", "")[:200],
                    "product_sought": product,
                    "buyer_type": buyer_type,
                    "source": "LinkedIn",
                    "discovered_at": date.today().isoformat(),
                })

    return buyers


# ─────────────────────────────────────────────
# DEMAND SIGNAL AIRTABLE LOGGING
# ─────────────────────────────────────────────

def log_demand_signals(signals: list[dict]) -> dict:
    """Write demand signals to Airtable:DemandSignals."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE:
        return {"logged": 0}

    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
    url = f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/DemandSignals"
    logged = 0

    for signal in signals:
        record = {
            "fields": {
                "Country": signal.get("country", ""),
                "Product": signal.get("product", ""),
                "NeedDescription": signal.get("need_description", ""),
                "Urgency": signal.get("urgency", "Medium"),
                "Volume": signal.get("volume", ""),
                "BuyerType": signal.get("buyer_type", ""),
                "TradeCategory": signal.get("trade_category", ""),
                "BrokeragePlay": signal.get("brokerage_play", False),
                "EcomPlay": signal.get("ecom_play", False),
                "Source": signal.get("source", ""),
                "DiscoveredAt": signal.get("discovered_at", date.today().isoformat()),
                "Status": "New",
            }
        }
        resp = requests.post(url, headers=headers, json=record, timeout=15)
        if resp.ok:
            logged += 1

    return {"logged": logged, "total": len(signals)}


# ─────────────────────────────────────────────
# DAILY MARKET INTELLIGENCE RUN
# ─────────────────────────────────────────────

# Countries to scan each day (rotate to keep costs manageable)
DAILY_COUNTRY_ROTATION = {
    0: ["nigeria", "ghana", "uk"],          # Monday
    1: ["france", "germany", "morocco"],    # Tuesday
    2: ["uae", "saudi_arabia", "india"],    # Wednesday
    3: ["brazil", "turkey", "indonesia"],   # Thursday
    4: ["nigeria", "france", "uk"],         # Friday (revisit top markets)
    5: ["india", "uae"],                    # Saturday (light)
    6: ["germany", "ghana"],                # Sunday (light)
}


def run_daily_market_intel(dry_run: bool = False) -> dict:
    """
    Daily market intelligence run. Called by orchestrator at 04:30.
    Mines Reddit + trade boards for demand signals.
    Feeds into trade_broker.py for matching and deal initiation.
    """
    today_dow = date.today().weekday()
    countries_today = DAILY_COUNTRY_ROTATION.get(today_dow, ["uk", "nigeria"])

    print(f"\n[market_intel] Daily run — scanning {countries_today}")

    all_signals = []

    # Reddit mining per country
    for country in countries_today:
        posts = mine_reddit_demand(country, max_posts=30)
        signals = extract_demand_signals(posts, country)
        all_signals.extend(signals)
        print(f"  [{country}] Found {len(signals)} demand signals from {len(posts)} posts")

    # Trade board mining (active buying leads)
    if not dry_run:
        board_leads = mine_trade_boards()
        all_signals.extend(board_leads)
        print(f"  [trade_boards] Found {len(board_leads)} active buying leads")

    # Log to Airtable
    if not dry_run:
        log_result = log_demand_signals(all_signals)
        print(f"  [airtable] Logged {log_result['logged']} demand signals")
    else:
        log_result = {"logged": 0, "note": "dry_run"}

    # Separate brokerage plays from ecom plays
    brokerage_signals = [s for s in all_signals if s.get("brokerage_play")]
    ecom_signals = [s for s in all_signals if s.get("ecom_play")]

    return {
        "date": str(date.today()),
        "countries_scanned": countries_today,
        "total_signals": len(all_signals),
        "brokerage_signals": len(brokerage_signals),
        "ecom_signals": len(ecom_signals),
        "top_brokerage": brokerage_signals[:5],
        "top_ecom": ecom_signals[:5],
        "airtable_logged": log_result.get("logged", 0),
    }


def get_country_supply_profile(country: str) -> dict:
    """Return what a country is known to export/supply well."""
    config = COUNTRY_INTEL_MAP.get(country.lower(), {})
    return {
        "country": country,
        "export_strengths": config.get("export_strengths", []),
        "trade_region": config.get("trade_region", ""),
        "currency": config.get("currency", ""),
    }


def find_supply_for_demand(product: str) -> list[str]:
    """
    Given a product in demand, return the best source countries.
    Cross-references COUNTRY_INTEL_MAP export strengths.
    """
    product_lower = product.lower()
    supplier_countries = []

    for country, config in COUNTRY_INTEL_MAP.items():
        for export in config.get("export_strengths", []):
            if any(word in export.lower() for word in product_lower.split()):
                supplier_countries.append(country)
                break

    return supplier_countries


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", type=str, help="Mine demand for a specific country")
    parser.add_argument("--product", type=str, help="Find supply countries for a product")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.country:
        posts = mine_reddit_demand(args.country)
        signals = extract_demand_signals(posts, args.country)
        print(json.dumps(signals, indent=2))
    elif args.product:
        countries = find_supply_for_demand(args.product)
        print(f"Best supply countries for '{args.product}': {countries}")
    else:
        summary = run_daily_market_intel(dry_run=args.dry_run)
        print(json.dumps(summary, indent=2))
