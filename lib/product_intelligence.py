"""
product_intelligence.py — PluggedIN Product Intelligence System
Scans multiple platforms for winning product signals, scores them,
and routes high-scorers to competitor analysis + GTM briefing.

Signal sources:
  - Meta Ad Library (via Apify)
  - TikTok Creative Center (via Apify / TinyFish)
  - Amazon BSR velocity (via Apify)
  - Google Trends (via Apify / SerpAPI)
  - TikTok Shop trending (via Apify)
  - Makuake / Wadiz / Indiegogo (crowdfunding intelligence)
  - Reddit demand signals (passed from market_intel.py)
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("product_intelligence")
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Apify / TinyFish clients
# ---------------------------------------------------------------------------
try:
    from apify_client import ApifyClient
    _apify = ApifyClient(os.getenv("APIFY_TOKEN", ""))
except ImportError:
    _apify = None
    log.warning("apify_client not installed — install with: pip install apify-client")

TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY", "")

# AI client (OpenRouter routing)
try:
    from lib.ai_client import call_ai
except ImportError:
    from ai_client import call_ai

# Airtable
try:
    from lib.airtable_client import upsert_record, get_records
except ImportError:
    try:
        from airtable_client import upsert_record, get_records
    except ImportError:
        def upsert_record(table, fields, match_field=None): pass
        def get_records(table, formula=None): return []

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Minimum thresholds to be worth pursuing
MIN_MONTHLY_SEARCHES = 10_000    # Google search volume
MIN_REDDIT_ENGAGEMENT = 50       # upvotes or comments
MIN_META_AD_COUNT = 5            # ads running = validated demand
MIN_AMAZON_RANK_VELOCITY = 20    # BSR positions gained per week

# Score thresholds
SCORE_HIGH = 70      # → full competitor intel + GTM brief
SCORE_MEDIUM = 45    # → log for watch list
SCORE_LOW = 0        # → discard

# Blue/Purple ocean market examples
BLUE_OCEAN_EXAMPLES = [
    {"product": "teeth whitening strips", "market": "Africa", "reason": "established in US/EU, untapped in Africa"},
    {"product": "caffeine pouches", "market": "MENA", "reason": "nicotine-free stimulant, high demand in Gulf countries"},
    {"product": "collagen powder", "market": "West Africa", "reason": "beauty spend rising, no local brand"},
    {"product": "electrolyte sachets", "market": "Nigeria", "reason": "hot climate, active population, no major brand"},
    {"product": "bamboo toothbrush", "market": "Morocco", "reason": "eco trend growing, gap in market"},
    {"product": "matcha powder", "market": "Saudi Arabia", "reason": "health trend rising, very few SKUs"},
    {"product": "keto snack bars", "market": "UAE", "reason": "high disposable income, low-carb trend growing"},
    {"product": "silicone baby products", "market": "Indonesia", "reason": "young population, safety-conscious parents"},
    {"product": "posture corrector", "market": "India", "reason": "massive WFH population, desk job pain points"},
    {"product": "UV phone sanitiser", "market": "Brazil", "reason": "hygiene awareness post-COVID still high"},
]

# Country ecom opportunity map
COUNTRY_ECOM_MAP = {
    "UK": {
        "platforms": ["amazon_uk", "tiktok_shop_uk", "shopify"],
        "growth_categories": ["health", "beauty", "home", "pet", "sports"],
        "avg_order_value": 35,
        "currency": "GBP",
    },
    "UAE": {
        "platforms": ["amazon_ae", "noon", "shopify"],
        "growth_categories": ["beauty", "health", "luxury", "food"],
        "avg_order_value": 120,
        "currency": "AED",
    },
    "Nigeria": {
        "platforms": ["jumia", "konga", "shopify"],
        "growth_categories": ["electronics", "beauty", "food", "health"],
        "avg_order_value": 45,
        "currency": "NGN",
    },
    "Saudi Arabia": {
        "platforms": ["amazon_sa", "noon", "shopify"],
        "growth_categories": ["health", "beauty", "food", "sports"],
        "avg_order_value": 90,
        "currency": "SAR",
    },
    "India": {
        "platforms": ["amazon_in", "flipkart", "shopify"],
        "growth_categories": ["health", "electronics", "beauty", "home"],
        "avg_order_value": 20,
        "currency": "INR",
    },
    "Morocco": {
        "platforms": ["jumia_ma", "shopify", "instagram_shop"],
        "growth_categories": ["beauty", "health", "fashion"],
        "avg_order_value": 35,
        "currency": "MAD",
    },
}

# ---------------------------------------------------------------------------
# Platform scanners
# ---------------------------------------------------------------------------

def scan_meta_ad_library(keyword: str, countries: list[str] = None, limit: int = 50) -> list[dict]:
    """
    Scrape Meta Ad Library for ads running on a keyword.
    High ad count = validated demand (brands spending = buyers exist).
    Uses Apify actor: apify/facebook-ads-scraper or equivalent.
    """
    if not _apify:
        log.warning("Apify client not available — skipping Meta Ad Library scan")
        return []

    countries = countries or ["GB", "US", "NG", "AE", "SA", "MA", "IN"]
    results = []

    try:
        run = _apify.actor("apify/facebook-ads-scraper").call(run_input={
            "searchTerms": [keyword],
            "countries": countries,
            "adType": "ALL",
            "maxResults": limit,
        })
        items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())
        for item in items:
            results.append({
                "source": "meta_ad_library",
                "keyword": keyword,
                "ad_id": item.get("id", ""),
                "page_name": item.get("page_name", ""),
                "country": item.get("delivery_by_region", [{}])[0].get("region", "") if item.get("delivery_by_region") else "",
                "ad_creative_type": item.get("ad_creative_link_title", ""),
                "cta": item.get("ad_creative_link_caption", ""),
                "platforms": item.get("publisher_platforms", []),
                "start_date": item.get("ad_delivery_start_time", ""),
                "impressions": item.get("impressions", {}).get("lower_bound", 0),
                "raw": item,
            })
    except Exception as e:
        log.error(f"Meta Ad Library scan failed for '{keyword}': {e}")

    return results


def scan_tiktok_creative_center(keyword: str, region: str = "GB", limit: int = 30) -> list[dict]:
    """
    TikTok Creative Center — find trending ads and creative angles.
    Uses Apify actor for TikTok Ads (or TinyFish web scraper as fallback).
    """
    if not _apify:
        return []

    results = []
    try:
        # Try Apify TikTok ads actor
        run = _apify.actor("apify/tiktok-ads-scraper").call(run_input={
            "keyword": keyword,
            "region": region,
            "limit": limit,
        })
        items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())
        for item in items:
            results.append({
                "source": "tiktok_creative_center",
                "keyword": keyword,
                "region": region,
                "video_id": item.get("video_id", ""),
                "advertiser": item.get("advertiser_name", ""),
                "likes": item.get("like_count", 0),
                "comments": item.get("comment_count", 0),
                "shares": item.get("share_count", 0),
                "views": item.get("play_count", 0),
                "cta": item.get("call_to_action", ""),
                "caption": item.get("video_description", ""),
                "industry": item.get("industry", ""),
                "raw": item,
            })
    except Exception as e:
        log.error(f"TikTok Creative Center scan failed for '{keyword}': {e}")

    return results


def scan_amazon_bsr(keyword: str, marketplace: str = "amazon.co.uk", limit: int = 30) -> list[dict]:
    """
    Scan Amazon BSR (Best Sellers Rank) for a keyword.
    Velocity = how fast a product is climbing the BSR list = real demand signal.
    """
    if not _apify:
        return []

    results = []
    try:
        run = _apify.actor("epctex/amazon-product-scraper").call(run_input={
            "keyword": keyword,
            "maxItems": limit,
            "amazonDomain": marketplace,
        })
        items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())
        for item in items:
            bsr = item.get("bestSellerRank", [])
            results.append({
                "source": "amazon_bsr",
                "keyword": keyword,
                "marketplace": marketplace,
                "asin": item.get("asin", ""),
                "title": item.get("title", ""),
                "brand": item.get("brand", ""),
                "price": item.get("price", 0),
                "rating": item.get("stars", 0),
                "review_count": item.get("reviewsCount", 0),
                "bsr_main": bsr[0].get("rank", 9999999) if bsr else 9999999,
                "bsr_category": bsr[0].get("category", "") if bsr else "",
                "monthly_sales_estimate": _estimate_monthly_sales(bsr[0].get("rank", 9999999) if bsr else 9999999),
                "images": item.get("images", [])[:1],
                "raw": item,
            })
    except Exception as e:
        log.error(f"Amazon BSR scan failed for '{keyword}': {e}")

    return results


def scan_google_trends(keyword: str, geo: str = "GB", timeframe: str = "today 3-m") -> dict:
    """
    Check Google Trends trajectory for a keyword.
    Rising trend + high relative interest = momentum product.
    Uses Apify pytrends actor or direct SerpAPI.
    """
    result = {
        "source": "google_trends",
        "keyword": keyword,
        "geo": geo,
        "trend_direction": "unknown",
        "peak_interest": 0,
        "avg_interest": 0,
        "related_queries": [],
        "rising_queries": [],
    }

    if not _apify:
        return result

    try:
        run = _apify.actor("emastra/google-trends-scraper").call(run_input={
            "searchTerms": [keyword],
            "geo": geo,
            "timeRange": timeframe,
            "outputAsTimeSeries": True,
        })
        items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())
        if items:
            data = items[0]
            timeline = data.get("timelineData", [])
            values = [t.get("value", [0])[0] for t in timeline if t.get("value")]
            if values:
                result["peak_interest"] = max(values)
                result["avg_interest"] = sum(values) // len(values)
                # Trend direction: compare last quarter vs first quarter
                mid = len(values) // 2
                first_half = sum(values[:mid]) / max(mid, 1)
                second_half = sum(values[mid:]) / max(len(values) - mid, 1)
                if second_half > first_half * 1.2:
                    result["trend_direction"] = "rising"
                elif second_half < first_half * 0.8:
                    result["trend_direction"] = "declining"
                else:
                    result["trend_direction"] = "stable"
            result["related_queries"] = data.get("relatedQueries", {}).get("top", [])[:5]
            result["rising_queries"] = data.get("relatedQueries", {}).get("rising", [])[:5]
    except Exception as e:
        log.error(f"Google Trends scan failed for '{keyword}': {e}")

    return result


def scan_tiktok_shop_trending(keyword: str, region: str = "GB", limit: int = 30) -> list[dict]:
    """
    Scan TikTok Shop for trending products.
    High GMV velocity = real consumer spend.
    """
    if not _apify:
        return []

    results = []
    try:
        run = _apify.actor("apify/tiktok-shop-scraper").call(run_input={
            "keyword": keyword,
            "region": region,
            "limit": limit,
        })
        items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())
        for item in items:
            results.append({
                "source": "tiktok_shop",
                "keyword": keyword,
                "region": region,
                "product_id": item.get("product_id", ""),
                "title": item.get("title", ""),
                "price": item.get("price", 0),
                "sold_count": item.get("sold_count", 0),
                "revenue_estimate": item.get("price", 0) * item.get("sold_count", 0),
                "commission_rate": item.get("commission_rate", 0),
                "rating": item.get("rating", 0),
                "review_count": item.get("review_count", 0),
                "raw": item,
            })
    except Exception as e:
        log.error(f"TikTok Shop scan failed for '{keyword}': {e}")

    return results


def scan_crowdfunding(keyword: str) -> list[dict]:
    """
    Scan Indiegogo (funded projects) for product-market fit signals.
    Successfully funded = validated demand from real backers.
    Makuake / Wadiz scanned via Apify web scraper actors.
    """
    results = []
    if not _apify:
        return results

    # Indiegogo
    try:
        run = _apify.actor("apify/web-scraper").call(run_input={
            "startUrls": [{"url": f"https://www.indiegogo.com/explore/all?q={keyword}&sort=trending"}],
            "maxPagesPerCrawl": 2,
            "pageFunction": """async function pageFunction(context) {
                const { $ } = context;
                return $('.campaign-card').map((i, el) => ({
                    title: $(el).find('.campaign-card__title').text().trim(),
                    raised: $(el).find('.campaign-card__stats-money').text().trim(),
                    percent: $(el).find('.campaign-card__stats-percent').text().trim(),
                    backers: $(el).find('.campaign-card__stats-backers').text().trim(),
                    url: $(el).find('a').attr('href'),
                })).get();
            }""",
        })
        items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())
        for item in items:
            if isinstance(item, dict) and item.get("title"):
                results.append({
                    "source": "indiegogo",
                    "keyword": keyword,
                    "title": item.get("title", ""),
                    "raised": item.get("raised", ""),
                    "percent_funded": item.get("percent", ""),
                    "backers": item.get("backers", ""),
                    "url": item.get("url", ""),
                })
    except Exception as e:
        log.error(f"Indiegogo scan failed for '{keyword}': {e}")

    return results


def scan_reddit_for_product_demand(keyword: str, subreddits: list[str] = None, limit: int = 20) -> list[dict]:
    """
    Mine Reddit for consumer complaints / "where can I find X" posts.
    High engagement = unmet demand.
    """
    if not _apify:
        return []

    subreddits = subreddits or [
        "UKPersonalFinance", "AskUK", "DIY", "SkincareAddiction",
        "Fitness", "loseit", "Parenting", "dogs", "malegrooming",
    ]

    results = []
    search_query = f"site:reddit.com {keyword} " + " OR ".join([f"r/{s}" for s in subreddits[:5]])

    try:
        run = _apify.actor("parseforge/reddit-posts-scraper").call(run_input={
            "query": keyword,
            "subreddits": subreddits,
            "limit": limit,
            "sort": "relevance",
        })
        items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())
        for item in items:
            results.append({
                "source": "reddit",
                "keyword": keyword,
                "subreddit": item.get("subreddit", ""),
                "title": item.get("title", ""),
                "body": item.get("selftext", "")[:300],
                "upvotes": item.get("score", 0),
                "comments": item.get("num_comments", 0),
                "url": item.get("url", ""),
                "created_utc": item.get("created_utc", 0),
                "engagement": item.get("score", 0) + item.get("num_comments", 0) * 3,
            })
    except Exception as e:
        log.error(f"Reddit demand scan failed for '{keyword}': {e}")

    return results


# ---------------------------------------------------------------------------
# Scoring engine
# ---------------------------------------------------------------------------

def score_product_opportunity(
    keyword: str,
    meta_ads: list[dict],
    tiktok_ads: list[dict],
    amazon_items: list[dict],
    google_trends: dict,
    tiktok_shop: list[dict],
    crowdfunding: list[dict],
    reddit_posts: list[dict],
) -> dict:
    """
    Score a product opportunity 0-100 across all signal sources.

    Scoring weights:
    - Meta Ad Library (20pts): ads running = validated spend
    - TikTok Shop velocity (20pts): real GMV signal
    - Amazon BSR (20pts): established demand
    - Google Trends direction (15pts): momentum
    - Reddit engagement (15pts): organic consumer demand
    - Crowdfunding (10pts): innovation / new category signal
    """
    score = 0
    breakdown = {}

    # 1. Meta Ad Library (20 pts)
    ad_count = len(meta_ads)
    if ad_count >= 50:
        meta_score = 20
    elif ad_count >= 20:
        meta_score = 15
    elif ad_count >= 5:
        meta_score = 10
    elif ad_count >= 1:
        meta_score = 5
    else:
        meta_score = 0
    score += meta_score
    breakdown["meta_ads"] = {"score": meta_score, "ad_count": ad_count}

    # 2. TikTok Shop velocity (20 pts)
    total_tiktok_revenue = sum(i.get("revenue_estimate", 0) for i in tiktok_shop)
    max_sold = max((i.get("sold_count", 0) for i in tiktok_shop), default=0)
    if max_sold >= 10000:
        tiktok_score = 20
    elif max_sold >= 1000:
        tiktok_score = 15
    elif max_sold >= 100:
        tiktok_score = 10
    elif max_sold >= 10:
        tiktok_score = 5
    else:
        tiktok_score = 0
    score += tiktok_score
    breakdown["tiktok_shop"] = {"score": tiktok_score, "max_sold": max_sold, "revenue_estimate": total_tiktok_revenue}

    # 3. Amazon BSR (20 pts)
    if amazon_items:
        best_bsr = min(i.get("bsr_main", 9999999) for i in amazon_items)
        avg_monthly_sales = sum(i.get("monthly_sales_estimate", 0) for i in amazon_items) / len(amazon_items)
        if best_bsr <= 1000:
            amazon_score = 20
        elif best_bsr <= 5000:
            amazon_score = 15
        elif best_bsr <= 20000:
            amazon_score = 10
        elif best_bsr <= 100000:
            amazon_score = 5
        else:
            amazon_score = 0
    else:
        best_bsr = 9999999
        avg_monthly_sales = 0
        amazon_score = 0
    score += amazon_score
    breakdown["amazon"] = {"score": amazon_score, "best_bsr": best_bsr, "avg_monthly_sales": avg_monthly_sales}

    # 4. Google Trends (15 pts)
    trend_dir = google_trends.get("trend_direction", "unknown")
    avg_interest = google_trends.get("avg_interest", 0)
    if trend_dir == "rising" and avg_interest >= 50:
        trends_score = 15
    elif trend_dir == "rising":
        trends_score = 10
    elif trend_dir == "stable" and avg_interest >= 40:
        trends_score = 8
    elif trend_dir == "stable":
        trends_score = 5
    else:
        trends_score = 2
    score += trends_score
    breakdown["google_trends"] = {"score": trends_score, "direction": trend_dir, "avg_interest": avg_interest}

    # 5. Reddit engagement (15 pts)
    total_engagement = sum(p.get("engagement", 0) for p in reddit_posts)
    post_count = len(reddit_posts)
    if total_engagement >= 5000 or post_count >= 15:
        reddit_score = 15
    elif total_engagement >= 1000 or post_count >= 8:
        reddit_score = 10
    elif total_engagement >= 200 or post_count >= 3:
        reddit_score = 5
    else:
        reddit_score = 0
    score += reddit_score
    breakdown["reddit"] = {"score": reddit_score, "post_count": post_count, "total_engagement": total_engagement}

    # 6. Crowdfunding (10 pts)
    cf_count = len(crowdfunding)
    if cf_count >= 5:
        cf_score = 10
    elif cf_count >= 2:
        cf_score = 7
    elif cf_count >= 1:
        cf_score = 4
    else:
        cf_score = 0
    score += cf_score
    breakdown["crowdfunding"] = {"score": cf_score, "campaign_count": cf_count}

    # Classification
    if score >= SCORE_HIGH:
        tier = "HIGH"
        action = "full_gtm"
    elif score >= SCORE_MEDIUM:
        tier = "MEDIUM"
        action = "watchlist"
    else:
        tier = "LOW"
        action = "discard"

    return {
        "keyword": keyword,
        "total_score": score,
        "tier": tier,
        "action": action,
        "breakdown": breakdown,
        "scored_at": datetime.utcnow().isoformat(),
    }


def _estimate_monthly_sales(bsr: int) -> int:
    """Rough BSR → monthly sales estimate for Amazon UK."""
    if bsr <= 100:     return 3000
    if bsr <= 500:     return 1500
    if bsr <= 1000:    return 800
    if bsr <= 5000:    return 300
    if bsr <= 20000:   return 80
    if bsr <= 100000:  return 20
    return 5


# ---------------------------------------------------------------------------
# Blue / Purple Ocean Scanner
# ---------------------------------------------------------------------------

def identify_blue_ocean_opportunities(
    product_category: str,
    source_market: str = "US",
    target_markets: list[str] = None,
) -> list[dict]:
    """
    Find products proven in one market but absent or underserved in another.
    Strategy: proven demand in source market → white space in target market.

    Examples:
    - Teeth whitening: proven US/UK → absent in Africa
    - Caffeine pouches: proven Scandinavia/US → absent in MENA
    - Collagen drinks: proven Asia → untapped in West Africa
    """
    target_markets = target_markets or ["Nigeria", "Ghana", "Morocco", "UAE", "Saudi Arabia", "Indonesia"]

    opportunities = []

    # Scan source market for proven products
    amazon_data = scan_amazon_bsr(product_category, marketplace="amazon.com", limit=20)
    proven_products = [p for p in amazon_data if p.get("bsr_main", 9999999) <= 10000]

    prompt = f"""
You are a market expansion strategist. I have found these proven products in {source_market}:

{json.dumps([{"title": p["title"], "price": p["price"], "monthly_sales": p["monthly_sales_estimate"], "bsr": p["bsr_main"]} for p in proven_products[:10]], indent=2)}

Target markets to assess: {', '.join(target_markets)}

For each target market, identify:
1. Which of these products is currently absent or underserved there?
2. What is the market opportunity size (rough estimate)?
3. What is the key insight (why will it work there)?
4. What are the main barriers to entry?
5. What sourcing approach would work (Alibaba, local manufacturer, white-label)?

Format as JSON array:
[
  {{
    "product": "product name",
    "source_market": "{source_market}",
    "target_market": "country",
    "opportunity_type": "blue_ocean|purple_ocean",
    "market_size_estimate": "£X/month",
    "key_insight": "...",
    "barriers": ["...", "..."],
    "sourcing": "alibaba|local|white_label",
    "urgency": "high|medium|low"
  }}
]

Return ONLY valid JSON.
"""

    response = call_ai(
        task="opportunity",
        system="You are a market expansion strategist identifying blue and purple ocean product opportunities.",
        prompt=prompt,
        max_tokens=2000,
    )

    try:
        raw = response.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)
        opportunities.extend(parsed if isinstance(parsed, list) else [])
    except Exception as e:
        log.error(f"Blue ocean parsing failed: {e}")

    return opportunities


def scan_purple_ocean_examples() -> list[dict]:
    """
    Purple ocean = take existing product + new market + slight repositioning.
    Pre-defined high-conviction plays based on known market gaps.
    """
    purple_plays = []
    for ex in BLUE_OCEAN_EXAMPLES:
        # Check if there are already brands running ads in this market
        meta_data = scan_meta_ad_library(
            keyword=ex["product"],
            countries=[_market_to_country_code(ex["market"])],
            limit=20,
        )
        existing_ad_count = len(meta_data)

        purple_plays.append({
            "product": ex["product"],
            "market": ex["market"],
            "reason": ex["reason"],
            "existing_ad_count": existing_ad_count,
            "competition_level": "low" if existing_ad_count < 5 else "medium" if existing_ad_count < 20 else "high",
            "opportunity_score": max(0, 80 - (existing_ad_count * 2)),  # Less competition = higher score
            "action": "pursue" if existing_ad_count < 10 else "monitor",
        })

    return sorted(purple_plays, key=lambda x: x["opportunity_score"], reverse=True)


def _market_to_country_code(market: str) -> str:
    mapping = {
        "Africa": "NG", "Nigeria": "NG", "Ghana": "GH", "Morocco": "MA",
        "MENA": "AE", "UAE": "AE", "Saudi Arabia": "SA",
        "UK": "GB", "Germany": "DE", "France": "FR",
        "India": "IN", "Indonesia": "ID", "Brazil": "BR",
        "Turkey": "TR", "West Africa": "NG",
    }
    return mapping.get(market, "GB")


# ---------------------------------------------------------------------------
# Product scoring + ICP generation
# ---------------------------------------------------------------------------

def generate_product_icp(
    keyword: str,
    amazon_items: list[dict],
    reddit_posts: list[dict],
    meta_ads: list[dict],
    target_market: str = "UK",
) -> dict:
    """
    Generate a detailed ICP / avatar for a product opportunity.
    Based on: who's buying on Amazon, who's asking on Reddit, what ads say.
    """
    reddit_context = "\n".join([
        f"- [{p['subreddit']}] {p['title']}: {p['body'][:150]}"
        for p in reddit_posts[:10]
    ])

    amazon_context = "\n".join([
        f"- {a['title']} | £{a['price']} | {a['review_count']} reviews | BSR {a['bsr_main']}"
        for a in amazon_items[:5]
    ])

    ad_ctas = list(set([a.get("cta", "") for a in meta_ads if a.get("cta")][:10]))

    prompt = f"""
Based on this market intelligence for "{keyword}" in {target_market}:

AMAZON PRODUCTS:
{amazon_context or "No data"}

REDDIT DEMAND SIGNALS:
{reddit_context or "No data"}

AD CTAs IN USE:
{', '.join(ad_ctas) or "None found"}

Create a detailed ICP (Ideal Customer Profile / Avatar) for the {target_market} market:

Return JSON:
{{
  "product": "{keyword}",
  "market": "{target_market}",
  "avatar_name": "Name them (e.g. Sarah, 32)",
  "age_range": "25-35",
  "gender_skew": "female|male|mixed",
  "income_bracket": "low|middle|high",
  "location_type": "urban|suburban|rural",
  "key_pain_points": ["...", "...", "..."],
  "core_desires": ["...", "...", "..."],
  "objections": ["...", "...", "..."],
  "trigger_moments": ["...", "...", "..."],
  "platforms_they_use": ["TikTok", "Instagram", "..."],
  "trust_signals_that_work": ["...", "...", "..."],
  "price_sensitivity": "low|medium|high",
  "buying_motivation": "primary motivation in one sentence",
  "best_ad_hook": "Best opening hook for a video ad to this person",
  "best_headline": "Best headline for a static image ad"
}}

Return ONLY valid JSON.
"""

    response = call_ai(
        task="product_brief",
        system="You are an expert consumer psychologist and DTC product strategist.",
        prompt=prompt,
        max_tokens=1200,
    )

    try:
        raw = response.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        log.error(f"ICP generation failed: {e}")
        return {}


# ---------------------------------------------------------------------------
# Full product intelligence run
# ---------------------------------------------------------------------------

def run_product_intelligence(
    keyword: str,
    target_markets: list[str] = None,
    dry_run: bool = False,
) -> dict:
    """
    Full product intelligence pipeline for one keyword.
    Returns scored opportunity with ICP + recommended action.
    """
    target_markets = target_markets or ["UK"]
    log.info(f"Running product intelligence for: {keyword}")

    if dry_run:
        log.info("[DRY RUN] Skipping live scans — returning mock result")
        return {
            "keyword": keyword,
            "total_score": 65,
            "tier": "MEDIUM",
            "action": "watchlist",
            "breakdown": {},
            "icp": {},
            "meta_ads_sample": [],
            "tiktok_trending": [],
        }

    # Run all platform scans in sequence
    log.info(f"  → Scanning Meta Ad Library...")
    meta_ads = scan_meta_ad_library(keyword, limit=50)
    time.sleep(2)

    log.info(f"  → Scanning TikTok Creative Center...")
    tiktok_ads = scan_tiktok_creative_center(keyword, region="GB", limit=30)
    time.sleep(2)

    log.info(f"  → Scanning Amazon BSR...")
    amazon_items = scan_amazon_bsr(keyword, limit=20)
    time.sleep(2)

    log.info(f"  → Checking Google Trends...")
    trends = scan_google_trends(keyword, geo="GB")
    time.sleep(2)

    log.info(f"  → Scanning TikTok Shop...")
    tiktok_shop = scan_tiktok_shop_trending(keyword, region="GB", limit=20)
    time.sleep(2)

    log.info(f"  → Checking crowdfunding platforms...")
    crowdfunding = scan_crowdfunding(keyword)
    time.sleep(2)

    log.info(f"  → Mining Reddit demand...")
    reddit_posts = scan_reddit_for_product_demand(keyword)
    time.sleep(2)

    # Score the opportunity
    score_result = score_product_opportunity(
        keyword=keyword,
        meta_ads=meta_ads,
        tiktok_ads=tiktok_ads,
        amazon_items=amazon_items,
        google_trends=trends,
        tiktok_shop=tiktok_shop,
        crowdfunding=crowdfunding,
        reddit_posts=reddit_posts,
    )

    # If high enough score, generate ICP
    icp = {}
    if score_result["total_score"] >= SCORE_MEDIUM:
        log.info(f"  → Score {score_result['total_score']} — generating ICP...")
        icp = generate_product_icp(
            keyword=keyword,
            amazon_items=amazon_items,
            reddit_posts=reddit_posts,
            meta_ads=meta_ads,
            target_market=target_markets[0],
        )

    result = {
        **score_result,
        "icp": icp,
        "meta_ads_count": len(meta_ads),
        "tiktok_shop_top": tiktok_shop[:3] if tiktok_shop else [],
        "amazon_top": amazon_items[:3] if amazon_items else [],
        "google_trends": trends,
        "reddit_sample": reddit_posts[:3] if reddit_posts else [],
        "crowdfunding_sample": crowdfunding[:2] if crowdfunding else [],
    }

    # Log to Airtable if score is worth keeping
    if score_result["total_score"] >= SCORE_MEDIUM:
        _log_to_airtable(result, icp)

    log.info(f"  ✓ {keyword}: score={score_result['total_score']} tier={score_result['tier']} action={score_result['action']}")
    return result


def _log_to_airtable(score_result: dict, icp: dict):
    """Log product opportunity to Airtable:ProductOpportunities."""
    try:
        fields = {
            "Product": score_result["keyword"],
            "TotalScore": score_result["total_score"],
            "Tier": score_result["tier"],
            "Action": score_result["action"],
            "MetaAdCount": score_result.get("meta_ads_count", 0),
            "TikTokShopRevenue": score_result.get("breakdown", {}).get("tiktok_shop", {}).get("revenue_estimate", 0),
            "BestAmazonBSR": score_result.get("breakdown", {}).get("amazon", {}).get("best_bsr", 0),
            "GoogleTrendDirection": score_result.get("breakdown", {}).get("google_trends", {}).get("direction", ""),
            "AvatarName": icp.get("avatar_name", ""),
            "AgeRange": icp.get("age_range", ""),
            "BuyingMotivation": icp.get("buying_motivation", ""),
            "BestAdHook": icp.get("best_ad_hook", ""),
            "BestHeadline": icp.get("best_headline", ""),
            "Status": "New",
            "DiscoveredAt": datetime.utcnow().isoformat(),
        }
        upsert_record("ProductOpportunities", fields, match_field="Product")
    except Exception as e:
        log.error(f"Airtable log failed: {e}")


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------

def run_daily_product_intelligence(
    keywords: list[str] = None,
    include_blue_ocean: bool = True,
    dry_run: bool = False,
) -> dict:
    """
    Daily product intelligence run.
    Scans a list of keywords + runs blue/purple ocean analysis.
    Called from orchestrator at 06:30.
    """
    # Default keywords from various signals
    default_keywords = [
        # Health & wellness
        "collagen powder", "magnesium glycinate", "ashwagandha supplement", "electrolyte sachets",
        # Beauty
        "teeth whitening strips", "vitamin c serum", "retinol cream", "tinted moisturiser",
        # Lifestyle
        "caffeine pouches", "posture corrector", "blue light glasses",
        # Pet
        "dog dental chews", "cat water fountain",
        # Home
        "bamboo bed sheets", "silicone kitchen tools",
    ]

    keywords = keywords or default_keywords
    results = []
    summary = {
        "total_scanned": 0,
        "high_tier": [],
        "medium_tier": [],
        "low_tier": [],
        "blue_ocean_plays": [],
        "ecom_briefs_created": 0,
        "scanned_at": datetime.utcnow().isoformat(),
    }

    log.info(f"=== Daily Product Intelligence: {len(keywords)} keywords ===")

    for keyword in keywords:
        try:
            result = run_product_intelligence(keyword, dry_run=dry_run)
            results.append(result)
            summary["total_scanned"] += 1

            if result["tier"] == "HIGH":
                summary["high_tier"].append({
                    "keyword": keyword,
                    "score": result["total_score"],
                    "best_hook": result.get("icp", {}).get("best_ad_hook", ""),
                })
            elif result["tier"] == "MEDIUM":
                summary["medium_tier"].append({"keyword": keyword, "score": result["total_score"]})
            else:
                summary["low_tier"].append(keyword)

            time.sleep(5)  # Rate limiting between keywords

        except Exception as e:
            log.error(f"Product intelligence failed for '{keyword}': {e}")

    # Blue/Purple ocean analysis
    if include_blue_ocean and not dry_run:
        log.info("Running blue/purple ocean scan...")
        try:
            purple_plays = scan_purple_ocean_examples()
            summary["blue_ocean_plays"] = [
                p for p in purple_plays if p["action"] == "pursue"
            ][:5]
        except Exception as e:
            log.error(f"Blue ocean scan failed: {e}")

    summary["ecom_briefs_created"] = len(summary["high_tier"])
    log.info(f"=== Product Intelligence Complete: {len(summary['high_tier'])} HIGH, {len(summary['medium_tier'])} MEDIUM ===")

    return {"summary": summary, "results": results}
