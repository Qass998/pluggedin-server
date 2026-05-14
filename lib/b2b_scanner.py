"""
b2b_scanner.py — PluggedIN Vendor & Partnership Scanner
Scans global B2B platforms to find distributor deals, white-label products,
and creative income plays using Apify actors + TinyFish browsing.

Platforms covered:
  - Alibaba.com (cloud9_ai/alibaba-scraper)
  - 1688.com / Chinese manufacturers (devcake/1688-com-supplier-scraper)
  - Global Sources (piotrv1001/global-sources-product-scraper)
  - Alibaba products by category (devcake/alibaba-products-scraper)
  - Amazon BSR tracking (sovereigntaylor/amazon-bsr-tracker) — FREE
  - Accio by Alibaba (TinyFish browsing — JS-rendered)
  - Europages, TradeIndia (TinyFish browsing)

Output: structured vendor/product leads scored and written to Airtable:VendorLeads
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
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE_PLUGGEDIN")

APIFY_BASE = "https://api.apify.com/v2"
AIRTABLE_BASE_URL = "https://api.airtable.com/v0"

# ─────────────────────────────────────────────
# APIFY RUNNER
# ─────────────────────────────────────────────

def _run_apify_actor(actor_id: str, input_data: dict, timeout_secs: int = 120) -> list:
    """Run an Apify actor and return results as a list of dicts."""
    headers = {"Authorization": f"Bearer {APIFY_TOKEN}", "Content-Type": "application/json"}

    # Start the actor run
    run_url = f"{APIFY_BASE}/acts/{actor_id}/runs"
    resp = requests.post(run_url, headers=headers, json=input_data, timeout=30)
    resp.raise_for_status()
    run_id = resp.json()["data"]["id"]

    # Poll until finished
    status_url = f"{APIFY_BASE}/actor-runs/{run_id}"
    elapsed = 0
    while elapsed < timeout_secs:
        time.sleep(5)
        elapsed += 5
        status_resp = requests.get(status_url, headers=headers, timeout=10)
        status = status_resp.json()["data"]["status"]
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break

    if status != "SUCCEEDED":
        print(f"[b2b_scanner] Actor {actor_id} finished with status: {status}")
        return []

    # Fetch dataset
    dataset_id = resp.json()["data"]["defaultDatasetId"]
    dataset_url = f"{APIFY_BASE}/datasets/{dataset_id}/items?limit=100"
    data_resp = requests.get(dataset_url, headers=headers, timeout=30)
    return data_resp.json() if data_resp.ok else []


# ─────────────────────────────────────────────
# TINYFISH BROWSER (for JS-heavy sites like Accio)
# ─────────────────────────────────────────────

def _tinyfish_fetch(url: str, extract_prompt: str) -> dict:
    """Use TinyFish to browse a JS-rendered page and extract structured data."""
    if not TINYFISH_API_KEY:
        return {"error": "TINYFISH_API_KEY not set"}

    headers = {
        "Authorization": f"Bearer {TINYFISH_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "prompt": extract_prompt,
        "format": "json"
    }
    try:
        resp = requests.post("https://api.tinyfish.io/v1/extract", headers=headers, json=payload, timeout=45)
        return resp.json() if resp.ok else {"error": resp.text}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# PLATFORM SCANNERS
# ─────────────────────────────────────────────

def scan_alibaba(keywords: list[str], max_results: int = 50) -> list[dict]:
    """
    Scan Alibaba.com for wholesale supplier opportunities.
    Uses devcake/alibaba-products-scraper ($0.001/result, 96.3% success).
    Returns list of product/supplier dicts.
    """
    results = []
    for keyword in keywords:
        print(f"[alibaba] Scanning: {keyword}")
        raw = _run_apify_actor(
            actor_id="devcake/alibaba-products-scraper",
            input_data={
                "searchQuery": keyword,
                "maxResults": max_results,
                "filterVerifiedSuppliers": True,
                "filterTradeAssurance": True,
            }
        )
        for item in raw:
            results.append({
                "platform": "Alibaba",
                "keyword": keyword,
                "product_name": item.get("title", ""),
                "supplier_name": item.get("supplier", {}).get("name", "") if isinstance(item.get("supplier"), dict) else item.get("supplier", ""),
                "price_range": item.get("price", ""),
                "moq": item.get("minOrder", ""),
                "verified": item.get("isVerified", False),
                "trade_assurance": item.get("tradeAssurance", False),
                "rating": item.get("rating", 0),
                "orders": item.get("orders", 0),
                "url": item.get("url", ""),
                "image_url": item.get("image", ""),
                "scanned_at": datetime.utcnow().isoformat(),
            })
    return results


def scan_1688(keywords: list[str], max_results: int = 30) -> list[dict]:
    """
    Scan 1688.com for Chinese manufacturer sourcing.
    Direct factory prices — before Alibaba middleman markup.
    Uses devcake/1688-com-supplier-scraper ($0.005/result, 97.6% success).
    Best for: white-label plays, private label at factory cost.
    """
    results = []
    for keyword in keywords:
        print(f"[1688] Scanning: {keyword}")
        raw = _run_apify_actor(
            actor_id="devcake/1688-com-supplier-scraper",
            input_data={
                "searchKeyword": keyword,
                "maxResults": max_results,
                "filterGoldSuppliers": True,
            }
        )
        for item in raw:
            results.append({
                "platform": "1688_China",
                "keyword": keyword,
                "supplier_name": item.get("name", ""),
                "products": item.get("mainProducts", ""),
                "quality_score": item.get("qualityScore", 0),
                "annual_revenue": item.get("annualRevenue", ""),
                "staff_count": item.get("staffCount", ""),
                "location": item.get("location", ""),
                "established": item.get("established", ""),
                "url": item.get("url", ""),
                "contact_url": item.get("contactUrl", ""),
                "scanned_at": datetime.utcnow().isoformat(),
            })
    return results


def scan_global_sources(keywords: list[str], max_results: int = 30) -> list[dict]:
    """
    Scan GlobalSources.com — premium B2B marketplace.
    Often has suppliers not on Alibaba. Good for electronics, fashion, home.
    Uses piotrv1001/global-sources-product-scraper ($0.002/result).
    """
    results = []
    for keyword in keywords:
        print(f"[global_sources] Scanning: {keyword}")
        raw = _run_apify_actor(
            actor_id="piotrv1001/global-sources-product-scraper",
            input_data={
                "keyword": keyword,
                "maxItems": max_results,
            }
        )
        for item in raw:
            results.append({
                "platform": "GlobalSources",
                "keyword": keyword,
                "product_name": item.get("title", ""),
                "supplier_name": item.get("supplierName", ""),
                "price_range": item.get("price", ""),
                "moq": item.get("moq", ""),
                "badge": item.get("badge", ""),
                "exhibition_info": item.get("exhibitionInfo", ""),
                "url": item.get("url", ""),
                "image_url": item.get("imageUrl", ""),
                "scanned_at": datetime.utcnow().isoformat(),
            })
    return results


def scan_amazon_bsr(categories: list[str]) -> list[dict]:
    """
    Scan Amazon Best Seller Rankings — FREE actor.
    Reveals what's ALREADY selling. Cross-reference with Alibaba source price
    to identify white-label margin plays.
    Uses sovereigntaylor/amazon-bsr-tracker (FREE, 99.8% success).
    """
    results = []
    for category in categories:
        print(f"[amazon_bsr] Scanning category: {category}")
        raw = _run_apify_actor(
            actor_id="sovereigntaylor/amazon-bsr-tracker",
            input_data={
                "categories": [category],
                "marketplace": "amazon.co.uk",  # UK marketplace
                "maxProducts": 50,
            }
        )
        for item in raw:
            results.append({
                "platform": "Amazon_BSR",
                "category": category,
                "product_name": item.get("title", ""),
                "brand": item.get("brand", ""),
                "bsr_rank": item.get("bsr", 0),
                "price": item.get("price", ""),
                "rating": item.get("rating", 0),
                "review_count": item.get("reviewCount", 0),
                "seller_count": item.get("sellerCount", 0),
                "asin": item.get("asin", ""),
                "url": item.get("url", ""),
                "sales_estimate": item.get("salesEstimate", ""),
                "scanned_at": datetime.utcnow().isoformat(),
            })
    return results


def scan_accio(keywords: list[str]) -> list[dict]:
    """
    Scan Accio by Alibaba — AI-powered B2B sourcing platform.
    JS-rendered so uses TinyFish browser. Accio often surfaces
    newer suppliers and trending product categories.
    URL: accio.com/search?q={keyword}
    """
    results = []
    extract_prompt = """
    Extract all product/supplier listings visible on this page.
    For each listing return:
    - product_name: the product title
    - supplier_name: supplier or manufacturer name
    - price: price or price range shown
    - moq: minimum order quantity
    - location: country or city of supplier
    - url: product or supplier URL if visible
    Return as a JSON array of objects.
    """
    for keyword in keywords:
        print(f"[accio] Scanning: {keyword}")
        url = f"https://www.accio.com/search?q={keyword.replace(' ', '+')}"
        data = _tinyfish_fetch(url, extract_prompt)
        items = data if isinstance(data, list) else data.get("results", [])
        for item in items:
            results.append({
                "platform": "Accio",
                "keyword": keyword,
                "product_name": item.get("product_name", ""),
                "supplier_name": item.get("supplier_name", ""),
                "price_range": item.get("price", ""),
                "moq": item.get("moq", ""),
                "location": item.get("location", ""),
                "url": item.get("url", ""),
                "scanned_at": datetime.utcnow().isoformat(),
            })
    return results


def scan_europages(keywords: list[str], region: str = "europe") -> list[dict]:
    """
    Scan Europages — European B2B directory.
    Best for: EU-made products (easier UK/EU import than China),
    exclusive regional distribution deals, premium positioning.
    Uses TinyFish browser.
    """
    results = []
    extract_prompt = """
    Extract all company/supplier listings on this page.
    For each return:
    - company_name: name of the business
    - products: what they make or sell
    - country: their country
    - description: brief description
    - contact_url: URL to their profile
    Return as a JSON array.
    """
    for keyword in keywords:
        print(f"[europages] Scanning: {keyword}")
        url = f"https://www.europages.co.uk/en/search?q={keyword.replace(' ', '+')}"
        data = _tinyfish_fetch(url, extract_prompt)
        items = data if isinstance(data, list) else data.get("results", [])
        for item in items:
            results.append({
                "platform": "Europages",
                "keyword": keyword,
                "company_name": item.get("company_name", ""),
                "products": item.get("products", ""),
                "country": item.get("country", ""),
                "description": item.get("description", ""),
                "url": item.get("contact_url", ""),
                "scanned_at": datetime.utcnow().isoformat(),
            })
    return results


def scan_tradeindia(keywords: list[str]) -> list[dict]:
    """
    Scan TradeIndia — Indian B2B marketplace.
    Best for: textiles, pharmaceuticals, spices, handicrafts, IT services.
    India has strong English-language suppliers = easier to correspond with.
    Uses TinyFish browser.
    """
    results = []
    extract_prompt = """
    Extract all product or supplier listings on this page.
    For each return:
    - product_name: title
    - company_name: supplier name
    - price: price shown
    - location: city/state in India
    - url: link to listing
    Return as a JSON array.
    """
    for keyword in keywords:
        print(f"[tradeindia] Scanning: {keyword}")
        url = f"https://www.tradeindia.com/search.html?q={keyword.replace(' ', '+')}"
        data = _tinyfish_fetch(url, extract_prompt)
        items = data if isinstance(data, list) else data.get("results", [])
        for item in items:
            results.append({
                "platform": "TradeIndia",
                "keyword": keyword,
                "product_name": item.get("product_name", ""),
                "company_name": item.get("company_name", ""),
                "price_range": item.get("price", ""),
                "location": item.get("location", ""),
                "url": item.get("url", ""),
                "scanned_at": datetime.utcnow().isoformat(),
            })
    return results


# ─────────────────────────────────────────────
# OPPORTUNITY SCORER
# ─────────────────────────────────────────────

def score_vendor_opportunity(item: dict, amazon_bsr_data: list[dict] = None) -> dict:
    """
    Score a vendor/product opportunity 0-100.
    Dimensions:
      - Demand signal (0-25): Is there a proven market? Amazon BSR, order count, ratings
      - Margin potential (0-25): Price gap between source and UK retail
      - Exclusivity / distribution play (0-20): Can we get exclusive regional rights?
      - Barrier to entry (0-15): How hard is it to replicate?
      - Speed to revenue (0-15): How fast can we start selling?

    Returns item dict with score + recommendation added.
    """
    score = 0
    reasons = []

    # Demand signal
    orders = int(str(item.get("orders", 0)).replace("+", "").replace(",", "") or 0)
    rating = float(item.get("rating", 0) or 0)
    bsr_rank = int(item.get("bsr_rank", 9999) or 9999)

    if orders > 1000 or bsr_rank < 500:
        score += 25
        reasons.append("Strong demand signal")
    elif orders > 200 or bsr_rank < 2000:
        score += 15
        reasons.append("Moderate demand signal")
    elif orders > 50 or bsr_rank < 5000:
        score += 8
        reasons.append("Early demand signal")

    # Margin potential — crude estimate from price
    price_str = str(item.get("price_range", item.get("price", "0")))
    try:
        # Extract first number from price string
        import re
        numbers = re.findall(r"[\d.]+", price_str.replace(",", ""))
        source_price = float(numbers[0]) if numbers else 0
        # Estimate UK retail at 3-5x source price
        estimated_retail = source_price * 4
        estimated_margin = estimated_retail - source_price
        if estimated_margin > 50:
            score += 25
            reasons.append(f"High margin potential (~£{estimated_margin:.0f}/unit)")
        elif estimated_margin > 20:
            score += 15
            reasons.append(f"Moderate margin (~£{estimated_margin:.0f}/unit)")
        elif estimated_margin > 5:
            score += 8
            reasons.append(f"Thin margin (~£{estimated_margin:.0f}/unit)")
    except Exception:
        pass

    # Exclusivity — 1688 and direct EU suppliers score higher
    platform = item.get("platform", "")
    if platform in ("1688_China", "Europages"):
        score += 20
        reasons.append("Direct manufacturer — exclusivity deal possible")
    elif platform in ("GlobalSources", "TradeIndia"):
        score += 12
        reasons.append("Less-tapped platform — fewer UK competitors")
    elif platform == "Accio":
        score += 8
        reasons.append("Newer platform — early mover advantage")

    # Barrier to entry
    verified = item.get("verified", False) or item.get("trade_assurance", False)
    moq_str = str(item.get("moq", "1000"))
    moq_nums = re.findall(r"\d+", moq_str.replace(",", "")) if 'moq_str' in dir() else []
    moq = int(moq_nums[0]) if moq_nums else 500
    if moq < 50:
        score += 15
        reasons.append("Low MOQ — low capital requirement")
    elif moq < 200:
        score += 10
        reasons.append("Manageable MOQ")
    elif moq < 500:
        score += 5
        reasons.append("Mid MOQ")

    # Speed to revenue
    if platform == "Amazon_BSR":
        score += 15
        reasons.append("Already selling on Amazon — direct FBA play")
    elif platform in ("Alibaba", "Accio"):
        score += 10
        reasons.append("Drop-ship or FBA launch possible within 2-4 weeks")
    elif platform in ("Europages", "TradeIndia"):
        score += 7
        reasons.append("Requires outreach first — 2-6 week lag")

    # Recommendation
    if score >= 70:
        recommendation = "PURSUE — Brief Qassim, initiate contact"
    elif score >= 50:
        recommendation = "MONITOR — Watch for 2 weeks, check demand trend"
    else:
        recommendation = "DISCARD — Low score"

    return {
        **item,
        "opportunity_score": score,
        "score_reasons": " | ".join(reasons),
        "recommendation": recommendation,
    }


# ─────────────────────────────────────────────
# CROSS-REFERENCE ENGINE
# ─────────────────────────────────────────────

def cross_reference_alibaba_amazon(alibaba_results: list[dict], amazon_results: list[dict]) -> list[dict]:
    """
    Find products that appear on BOTH Alibaba (cheap source) AND Amazon BSR (proven demand).
    These are the golden plays: proven demand + known source price.
    Calculates real margin based on actual data.
    """
    plays = []
    for amz in amazon_results:
        amz_title = amz.get("product_name", "").lower()
        amz_price_str = str(amz.get("price", "0")).replace("£", "").replace("$", "").replace(",", "")
        try:
            amz_price = float(amz_price_str.split("-")[0].strip()) if amz_price_str else 0
        except Exception:
            amz_price = 0

        for ali in alibaba_results:
            ali_title = ali.get("product_name", "").lower()
            # Simple keyword overlap check
            amz_words = set(amz_title.split())
            ali_words = set(ali_title.split())
            overlap = len(amz_words & ali_words)

            if overlap >= 2 and amz_price > 0:
                ali_price_str = str(ali.get("price_range", "0")).replace("$", "").replace("£", "").replace(",", "")
                try:
                    import re
                    ali_nums = re.findall(r"[\d.]+", ali_price_str)
                    ali_price = float(ali_nums[0]) if ali_nums else 0
                except Exception:
                    ali_price = 0

                if ali_price > 0 and amz_price > ali_price:
                    margin = amz_price - ali_price
                    margin_pct = (margin / amz_price) * 100

                    plays.append({
                        "play_type": "White-Label / FBA",
                        "amazon_product": amz.get("product_name"),
                        "amazon_bsr": amz.get("bsr_rank"),
                        "amazon_price_gbp": amz_price,
                        "amazon_reviews": amz.get("review_count"),
                        "amazon_url": amz.get("url"),
                        "alibaba_product": ali.get("product_name"),
                        "alibaba_supplier": ali.get("supplier_name"),
                        "alibaba_source_price": ali_price,
                        "alibaba_url": ali.get("url"),
                        "estimated_margin_gbp": round(margin, 2),
                        "estimated_margin_pct": round(margin_pct, 1),
                        "opportunity_score": min(100, int(margin_pct * 1.5)),
                        "recommendation": "PURSUE — FBA white-label play" if margin_pct > 50 else "MONITOR",
                    })

    # Sort by margin descending
    plays.sort(key=lambda x: x.get("estimated_margin_gbp", 0), reverse=True)
    return plays


# ─────────────────────────────────────────────
# AIRTABLE LOGGING
# ─────────────────────────────────────────────

def log_to_airtable(opportunities: list[dict], table: str = "VendorLeads") -> dict:
    """Write scored vendor opportunities to Airtable."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE:
        print("[airtable] Missing credentials — skipping log")
        return {"logged": 0}

    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    url = f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/{table}"
    logged = 0

    for opp in opportunities:
        if opp.get("opportunity_score", 0) < 50:
            continue  # only log ≥50 score to keep Airtable clean

        record = {
            "fields": {
                "Platform": opp.get("platform", ""),
                "ProductName": opp.get("product_name", opp.get("amazon_product", "")),
                "SupplierName": opp.get("supplier_name", opp.get("alibaba_supplier", "")),
                "PriceRange": str(opp.get("price_range", opp.get("alibaba_source_price", ""))),
                "MOQ": str(opp.get("moq", "")),
                "Score": opp.get("opportunity_score", 0),
                "ScoreReasons": opp.get("score_reasons", opp.get("recommendation", "")),
                "Recommendation": opp.get("recommendation", ""),
                "URL": opp.get("url", opp.get("alibaba_url", "")),
                "ScannedAt": opp.get("scanned_at", datetime.utcnow().isoformat()),
                "Status": "New",
            }
        }
        resp = requests.post(url, headers=headers, json=record, timeout=15)
        if resp.ok:
            logged += 1
        else:
            print(f"[airtable] Log failed: {resp.text[:100]}")

    return {"logged": logged, "total": len(opportunities)}


# ─────────────────────────────────────────────
# FULL DAILY SCAN (called by orchestrator)
# ─────────────────────────────────────────────

SCAN_CONFIG = {
    # Keywords to scan across all platforms
    "alibaba_keywords": [
        "home organisation products",
        "pet accessories wholesale",
        "health supplements private label",
        "kitchen gadgets wholesale",
        "eco-friendly packaging",
        "beauty tools private label",
        "fitness equipment wholesale",
        "garden tools wholesale",
        "phone accessories wholesale",
        "baby products wholesale",
    ],
    "china_1688_keywords": [
        "home storage solutions",
        "pet products factory",
        "health supplement OEM",
        "kitchen tools manufacturer",
    ],
    "global_sources_keywords": [
        "smart home devices",
        "sustainable products",
        "personal care devices",
        "outdoor equipment",
    ],
    "amazon_bsr_categories": [
        "Kitchen & Home",
        "Health & Personal Care",
        "Sports & Outdoors",
        "Pet Supplies",
        "Baby",
    ],
    "accio_keywords": [
        "trending products 2025",
        "white label health products",
        "dropship products high margin",
    ],
    "europages_keywords": [
        "food manufacturer distributor UK",
        "cosmetics private label Europe",
        "sustainable packaging supplier",
    ],
    "tradeindia_keywords": [
        "organic spices export",
        "textiles wholesale India",
        "herbal supplements manufacturer",
    ],
}


def run_daily_scan(dry_run: bool = False) -> dict:
    """
    Full daily vendor & partnership scan. Called by orchestrator at 05:15.
    Runs all platform scanners, scores results, cross-references,
    logs ≥50 scores to Airtable:VendorLeads.
    Returns summary dict for CEO agent.
    """
    print(f"\n[b2b_scanner] Starting daily scan — {date.today()} {'(DRY RUN)' if dry_run else ''}")
    all_results = []

    # 1. Alibaba scan
    ali_results = scan_alibaba(SCAN_CONFIG["alibaba_keywords"], max_results=20)
    all_results.extend(ali_results)
    print(f"[alibaba] Found {len(ali_results)} products")

    # 2. 1688 Chinese manufacturers
    china_results = scan_1688(SCAN_CONFIG["china_1688_keywords"], max_results=15)
    all_results.extend(china_results)
    print(f"[1688] Found {len(china_results)} suppliers")

    # 3. Global Sources
    gs_results = scan_global_sources(SCAN_CONFIG["global_sources_keywords"], max_results=15)
    all_results.extend(gs_results)
    print(f"[global_sources] Found {len(gs_results)} products")

    # 4. Amazon BSR (FREE) — proof of demand
    amz_results = scan_amazon_bsr(SCAN_CONFIG["amazon_bsr_categories"])
    all_results.extend(amz_results)
    print(f"[amazon_bsr] Found {len(amz_results)} BSR products")

    # 5. Accio (TinyFish)
    accio_results = scan_accio(SCAN_CONFIG["accio_keywords"])
    all_results.extend(accio_results)
    print(f"[accio] Found {len(accio_results)} products")

    # 6. Europages (EU suppliers)
    eu_results = scan_europages(SCAN_CONFIG["europages_keywords"])
    all_results.extend(eu_results)
    print(f"[europages] Found {len(eu_results)} suppliers")

    # 7. TradeIndia
    india_results = scan_tradeindia(SCAN_CONFIG["tradeindia_keywords"])
    all_results.extend(india_results)
    print(f"[tradeindia] Found {len(india_results)} suppliers")

    # Score all results
    scored = [score_vendor_opportunity(item, amz_results) for item in all_results]

    # Cross-reference Alibaba + Amazon BSR for white-label plays
    white_label_plays = cross_reference_alibaba_amazon(ali_results, amz_results)
    print(f"[cross_ref] Found {len(white_label_plays)} white-label plays")

    # Filter high-score opportunities
    high_score = [r for r in scored if r.get("opportunity_score", 0) >= 70]
    medium_score = [r for r in scored if 50 <= r.get("opportunity_score", 0) < 70]

    print(f"\n[b2b_scanner] Results: {len(high_score)} PURSUE | {len(medium_score)} MONITOR | {len(white_label_plays)} white-label plays")

    # Log to Airtable
    if not dry_run:
        log_result = log_to_airtable(scored + white_label_plays)
        print(f"[airtable] Logged {log_result['logged']} opportunities")
    else:
        log_result = {"logged": 0, "note": "dry run"}

    # Return summary for CEO agent
    return {
        "date": str(date.today()),
        "total_scanned": len(all_results),
        "pursue_count": len(high_score),
        "monitor_count": len(medium_score),
        "white_label_plays": len(white_label_plays),
        "top_opportunities": high_score[:5],
        "top_white_label": white_label_plays[:3],
        "airtable_logged": log_result.get("logged", 0),
    }


# ─────────────────────────────────────────────
# TARGETED SCANS (called on demand)
# ─────────────────────────────────────────────

def scan_niche(niche: str, platforms: list[str] = None) -> list[dict]:
    """
    On-demand scan of a specific niche across chosen platforms.
    Example: scan_niche("bamboo products", platforms=["alibaba", "amazon", "europages"])
    """
    if platforms is None:
        platforms = ["alibaba", "amazon", "europages"]

    results = []

    if "alibaba" in platforms:
        results.extend(scan_alibaba([niche]))
    if "amazon" in platforms:
        results.extend(scan_amazon_bsr([niche]))
    if "1688" in platforms:
        results.extend(scan_1688([niche]))
    if "global_sources" in platforms:
        results.extend(scan_global_sources([niche]))
    if "europages" in platforms:
        results.extend(scan_europages([niche]))
    if "tradeindia" in platforms:
        results.extend(scan_tradeindia([niche]))
    if "accio" in platforms:
        results.extend(scan_accio([niche]))

    scored = [score_vendor_opportunity(item) for item in results]
    scored.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)
    return scored


def find_distributor_plays(country: str, categories: list[str]) -> list[dict]:
    """
    Find exclusive distributor/import plays from a specific country.
    Looks for manufacturers who want UK/EU distribution partners.
    Best targets: Morocco, Turkey, India, Vietnam, Mexico.
    """
    results = []

    # Country-specific platform mapping
    country_platforms = {
        "india": "tradeindia",
        "china": "1688",
        "europe": "europages",
        "global": "global_sources",
    }

    country_lower = country.lower()
    platform = country_platforms.get(country_lower, "alibaba")

    for category in categories:
        search_term = f"{category} manufacturer {country} export UK distributor"
        if platform == "tradeindia":
            results.extend(scan_tradeindia([search_term]))
        elif platform == "1688":
            results.extend(scan_1688([search_term]))
        elif platform == "europages":
            results.extend(scan_europages([search_term]))
        else:
            results.extend(scan_alibaba([search_term]))

    # Boost score for distributor-specific plays
    for r in results:
        r["play_type"] = "Exclusive Distributor"
        r["opportunity_score"] = min(100, r.get("opportunity_score", 0) + 10)

    return sorted(results, key=lambda x: x.get("opportunity_score", 0), reverse=True)


# ─────────────────────────────────────────────
# LEAD MINING (dual-use — same scan, PluggedIN clients)
# ─────────────────────────────────────────────

# Signals that a scanned business could be a PluggedIN client
PLUGGEDIN_CLIENT_SIGNALS = {
    "keywords": [
        "uk distributor", "uk supplier", "uk manufacturer", "uk wholesaler",
        "london", "manchester", "birmingham", "leeds", "glasgow",
        "ltd", "limited", "group", "holdings",
    ],
    "categories": [
        "construction", "legal", "solicitor", "plumber", "plumbing",
        "roofing", "landscaping", "restaurant", "hospitality", "logistics",
        "healthcare", "dental", "medical", "real estate", "estate agent",
    ],
    "platforms": ["Europages", "GlobalSources"],  # more likely to have UK businesses
}


def _is_pluggedin_prospect(item: dict) -> bool:
    """
    Check if a scanned B2B listing looks like a PluggedIN client prospect.
    We're looking for UK-based businesses that could benefit from AI automation.
    """
    text = " ".join([
        str(item.get("company_name", "")),
        str(item.get("supplier_name", "")),
        str(item.get("product_name", "")),
        str(item.get("products", "")),
        str(item.get("description", "")),
        str(item.get("location", "")),
        str(item.get("country", "")),
    ]).lower()

    # Must be UK-based or Europages (EU = closer to UK sales)
    platform = item.get("platform", "")
    is_uk = any(kw in text for kw in ["uk", "united kingdom", "england", "london", "manchester", "birmingham"])
    is_eu_platform = platform in ("Europages", "GlobalSources")

    if not (is_uk or is_eu_platform):
        return False

    # Must match a category PluggedIN serves
    return any(cat in text for cat in PLUGGEDIN_CLIENT_SIGNALS["categories"])


def _score_pluggedin_prospect(item: dict) -> int:
    """
    Score a prospect 0-100 for likelihood of becoming a PluggedIN client.
    Higher = better fit.
    """
    score = 0
    text = " ".join([str(v) for v in item.values()]).lower()

    # Category fit
    high_value_categories = ["legal", "solicitor", "mortgage", "dental", "medical", "construction"]
    mid_value_categories = ["plumbing", "restaurant", "logistics", "landscaping", "roofing"]
    if any(c in text for c in high_value_categories):
        score += 40  # LegalMatch/CareConnect verticals = £200-2000/lead
    elif any(c in text for c in mid_value_categories):
        score += 25  # PlumbRight/BuildConnect verticals = £25-300/lead

    # UK presence
    if any(kw in text for kw in ["london", "manchester", "birmingham", "leeds", "glasgow"]):
        score += 20

    # Size signals
    if any(kw in text for kw in ["group", "holdings", "ltd", "limited", "plc"]):
        score += 15

    # Has contact info
    if item.get("url") or item.get("email"):
        score += 15

    # Multi-location / established
    if any(kw in text for kw in ["established", "since", "years", "branches", "nationwide"]):
        score += 10

    return min(100, score)


def mine_pluggedin_leads(scan_results: list[dict] = None, dry_run: bool = False) -> dict:
    """
    From B2B scan data, extract businesses that are potential PluggedIN clients.
    These go into Airtable:Leads (not VendorLeads) with source="B2BScan".

    PluggedIN sells: AI receptionist, pipeline agent, retention, stock intel.
    Target: UK businesses spending money on admin, missing calls, losing leads.

    Runs automatically after run_daily_scan().
    """
    # If no data passed, do a targeted scan for UK businesses
    if not scan_results:
        print("[lead_mining] Running targeted UK business scan...")
        scan_results = []
        uk_targets = [
            "UK construction company",
            "UK solicitor law firm",
            "UK plumbing heating company",
            "UK dental practice",
            "UK restaurant hospitality",
            "UK logistics distribution company",
        ]
        scan_results.extend(scan_europages(uk_targets))
        scan_results.extend(scan_global_sources(["UK supplier manufacturer"]))

    # Filter to PluggedIN prospects
    prospects = [item for item in scan_results if _is_pluggedin_prospect(item)]

    # Score them
    scored_prospects = []
    for p in prospects:
        score = _score_pluggedin_prospect(p)
        if score >= 40:  # only log meaningful prospects
            scored_prospects.append({**p, "prospect_score": score})

    scored_prospects.sort(key=lambda x: x.get("prospect_score", 0), reverse=True)
    print(f"[lead_mining] Found {len(scored_prospects)} PluggedIN prospect leads from B2B scan")

    logged = 0
    if not dry_run and scored_prospects and AIRTABLE_TOKEN and AIRTABLE_BASE:
        headers = {
            "Authorization": f"Bearer {AIRTABLE_TOKEN}",
            "Content-Type": "application/json"
        }
        url = f"{AIRTABLE_BASE_URL}/{AIRTABLE_BASE}/Leads"

        for prospect in scored_prospects[:20]:  # cap at 20/day
            # Map to our Leads table schema
            text = " ".join([str(v) for v in prospect.values()]).lower()

            # Determine vertical
            if any(c in text for c in ["legal", "solicitor"]):
                vertical = "LegalMatch"
            elif any(c in text for c in ["dental", "medical", "healthcare"]):
                vertical = "CareConnect"
            elif any(c in text for c in ["construction", "roofing", "landscaping"]):
                vertical = "BuildConnect"
            elif any(c in text for c in ["plumb", "heating", "boiler"]):
                vertical = "PlumbRight"
            elif any(c in text for c in ["restaurant", "cafe", "hospitality"]):
                vertical = "Hospitality"
            else:
                vertical = "General"

            record = {
                "fields": {
                    "Vertical": vertical,
                    "Name": prospect.get("company_name", prospect.get("supplier_name", "Unknown")),
                    "Need": "AI automation — receptionist, pipeline, retention",
                    "Score": prospect.get("prospect_score", 0),
                    "Status": "Qualified",
                    "Notes": (
                        f"Source: B2B Scan ({prospect.get('platform', 'Unknown')}) | "
                        f"URL: {prospect.get('url', 'N/A')} | "
                        f"Products/Services: {str(prospect.get('products', prospect.get('description', '')))[:200]}"
                    ),
                }
            }
            resp = requests.post(url, headers=headers, json=record, timeout=15)
            if resp.ok:
                logged += 1

    return {
        "prospects_found": len(prospects),
        "prospects_scored": len(scored_prospects),
        "logged": logged,
        "top_prospects": scored_prospects[:3],
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--niche", type=str, help="Scan a specific niche")
    parser.add_argument("--country", type=str, help="Find distributor plays from a country")
    args = parser.parse_args()

    if args.niche:
        results = scan_niche(args.niche)
        print(json.dumps(results[:10], indent=2))
    elif args.country:
        results = find_distributor_plays(args.country, ["health products", "food", "textiles"])
        print(json.dumps(results[:10], indent=2))
    else:
        summary = run_daily_scan(dry_run=args.dry_run)
        print(json.dumps(summary, indent=2))
