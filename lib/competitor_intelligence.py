"""
competitor_intelligence.py — PluggedIN Competitor Intelligence
For products scoring ≥70: map ALL competitors, their angles, creative formats,
pricing, ICPs, and identify the GAP we can exploit.

Output: structured GTM brief per product with:
  - Competitor map (who's winning + how)
  - Unused angles (what nobody is saying)
  - Recommended creative angle for PluggedIN
  - Recommended pricing position
  - Recommended launch platform
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("competitor_intelligence")
logging.basicConfig(level=logging.INFO)

try:
    from apify_client import ApifyClient
    _apify = ApifyClient(os.getenv("APIFY_TOKEN", ""))
except ImportError:
    _apify = None

try:
    from lib.ai_client import call_ai
except ImportError:
    from ai_client import call_ai

try:
    from lib.airtable_client import upsert_record
except ImportError:
    try:
        from airtable_client import upsert_record
    except ImportError:
        def upsert_record(table, fields, match_field=None): pass

# ---------------------------------------------------------------------------
# Creative angle taxonomy
# ---------------------------------------------------------------------------

MARKETING_ANGLES = [
    "Before/After transformation",
    "Problem → Agitation → Solution (PAS)",
    "Social proof / testimonial lead",
    "Authority / expert endorsement",
    "Lifestyle aspiration",
    "Fear / risk mitigation",
    "Comparison vs competitor",
    "Unboxing / first impression",
    "Tutorial / how-to demonstration",
    "Challenge / trend participation",
    "Value / price anchor",
    "Urgency / scarcity",
    "Community / belonging",
    "Curiosity / mystery hook",
    "Behind the scenes / authenticity",
    "User-generated content (UGC)",
    "Influencer endorsement",
    "Science / ingredient proof",
]

# ---------------------------------------------------------------------------
# Competitor data collection
# ---------------------------------------------------------------------------

def scan_meta_competitor_ads(keyword: str, country_code: str = "GB", limit: int = 50) -> list[dict]:
    """
    Pull competitor ads from Meta Ad Library for a keyword.
    Extracts: brand, angle, creative type, CTA, running duration.
    """
    if not _apify:
        return []

    ads = []
    try:
        run = _apify.actor("apify/facebook-ads-scraper").call(run_input={
            "searchTerms": [keyword],
            "countries": [country_code],
            "adType": "ALL",
            "maxResults": limit,
        })
        items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())
        for item in items:
            ads.append({
                "brand": item.get("page_name", "Unknown"),
                "ad_id": item.get("id", ""),
                "headline": item.get("ad_creative_link_title", ""),
                "body": item.get("ad_creative_body", "")[:200],
                "cta": item.get("ad_creative_link_caption", ""),
                "media_type": "video" if item.get("ad_creative_video_preview_image_url") else "image",
                "platforms": item.get("publisher_platforms", []),
                "start_date": item.get("ad_delivery_start_time", ""),
                "estimated_reach": item.get("impressions", {}).get("lower_bound", 0),
                "url": item.get("ad_snapshot_url", ""),
            })
    except Exception as e:
        log.error(f"Meta competitor scan failed: {e}")

    return ads


def scan_tiktok_competitor_content(keyword: str, region: str = "GB", limit: int = 30) -> list[dict]:
    """
    Find top TikTok organic + paid content for a keyword.
    Identifies which hooks and formats are winning.
    """
    if not _apify:
        return []

    content = []
    try:
        run = _apify.actor("clockworks/tiktok-scraper").call(run_input={
            "hashtags": [keyword.replace(" ", "")],
            "maxItems": limit,
        })
        items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())
        for item in items:
            content.append({
                "source": "tiktok_organic",
                "creator": item.get("authorMeta", {}).get("name", ""),
                "creator_followers": item.get("authorMeta", {}).get("fans", 0),
                "caption": item.get("text", "")[:200],
                "views": item.get("playCount", 0),
                "likes": item.get("diggCount", 0),
                "comments": item.get("commentCount", 0),
                "shares": item.get("shareCount", 0),
                "engagement_rate": round(
                    (item.get("diggCount", 0) + item.get("commentCount", 0)) /
                    max(item.get("playCount", 1), 1) * 100, 2
                ),
                "duration": item.get("videoMeta", {}).get("duration", 0),
                "hashtags": item.get("hashtags", [])[:5],
                "music": item.get("musicMeta", {}).get("musicName", ""),
                "url": f"https://www.tiktok.com/@{item.get('authorMeta', {}).get('name', '')}",
            })
    except Exception as e:
        log.error(f"TikTok competitor content scan failed: {e}")

    return sorted(content, key=lambda x: x["views"], reverse=True)


def scan_amazon_competitor_listings(keyword: str, marketplace: str = "amazon.co.uk", limit: int = 20) -> list[dict]:
    """
    Scrape Amazon search results for competitor product listings.
    Extracts: pricing, review count, review score, main selling points from bullet points.
    """
    if not _apify:
        return []

    listings = []
    try:
        run = _apify.actor("epctex/amazon-product-scraper").call(run_input={
            "keyword": keyword,
            "maxItems": limit,
            "amazonDomain": marketplace,
        })
        items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())
        for item in items:
            bsr = item.get("bestSellerRank", [])
            listings.append({
                "asin": item.get("asin", ""),
                "brand": item.get("brand", ""),
                "title": item.get("title", ""),
                "price": item.get("price", 0),
                "original_price": item.get("originalPrice", 0),
                "discount_pct": round(
                    (1 - item.get("price", 0) / max(item.get("originalPrice", 1), 1)) * 100
                ) if item.get("originalPrice") else 0,
                "rating": item.get("stars", 0),
                "review_count": item.get("reviewsCount", 0),
                "bsr": bsr[0].get("rank", 0) if bsr else 0,
                "bullet_points": item.get("features", [])[:3],
                "images": item.get("images", [])[:1],
                "amazon_choice": item.get("amazonChoiceAsin", "") == item.get("asin", ""),
                "bestseller_badge": bool(bsr and bsr[0].get("rank", 9999) <= 100),
            })
    except Exception as e:
        log.error(f"Amazon competitor scan failed: {e}")

    return sorted(listings, key=lambda x: x.get("review_count", 0), reverse=True)


def scan_google_shopping_competitors(keyword: str, country: str = "GB") -> list[dict]:
    """
    Google Shopping results = brands spending on paid search.
    Price positioning + ad copy reveals their angle.
    """
    if not _apify:
        return []

    results = []
    try:
        run = _apify.actor("apify/google-shopping-scraper").call(run_input={
            "queries": [keyword],
            "countryCode": country,
            "maxResults": 20,
        })
        items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())
        for item in items:
            results.append({
                "source": "google_shopping",
                "brand": item.get("seller", ""),
                "title": item.get("title", ""),
                "price": item.get("price", ""),
                "description": item.get("description", "")[:150],
                "url": item.get("url", ""),
                "sponsored": item.get("isSponsored", False),
            })
    except Exception as e:
        log.error(f"Google Shopping scan failed: {e}")

    return results


# ---------------------------------------------------------------------------
# AI-powered analysis
# ---------------------------------------------------------------------------

def analyse_competitor_angles(
    keyword: str,
    meta_ads: list[dict],
    tiktok_content: list[dict],
    amazon_listings: list[dict],
    google_shopping: list[dict],
) -> dict:
    """
    Use AI to synthesise all competitor data into:
    1. Map of who's winning and how
    2. Angles being used
    3. Angles NOT being used (the gap)
    4. Recommended angle for PluggedIN
    """
    meta_summary = "\n".join([
        f"- {a['brand']}: '{a['headline']}' | CTA: {a['cta']} | Type: {a['media_type']}"
        for a in meta_ads[:15]
    ])

    tiktok_summary = "\n".join([
        f"- {c['creator']} ({c['creator_followers']:,} followers): {c['views']:,} views | '{c['caption'][:100]}'"
        for c in tiktok_content[:10]
    ])

    amazon_summary = "\n".join([
        f"- {a['brand']}: £{a['price']} | {a['review_count']} reviews | {a['rating']}★ | {' | '.join(a['bullet_points'][:2])}"
        for a in amazon_listings[:8]
    ])

    prompt = f"""
You are a DTC marketing strategist doing a full competitor analysis for "{keyword}".

META ADS RUNNING:
{meta_summary or "No data"}

TOP TIKTOK CONTENT:
{tiktok_summary or "No data"}

AMAZON COMPETITORS:
{amazon_summary or "No data"}

Analyse this competitive landscape and output:

1. DOMINANT ANGLES: What marketing angles are most competitors using?
2. WINNING BRANDS: Who appears to be winning and why?
3. GAPS: What angles are NOT being used? What pain points are not being addressed?
4. CREATIVE FORMAT: What format is winning (video UGC? static image? carousel?)
5. PRICE POSITIONING: What price points are competitors clustering at?
6. RECOMMENDED ANGLE: If I were launching a new brand today, what would be my differentiated angle?

Return as JSON:
{{
  "dominant_angles": ["angle1", "angle2", "angle3"],
  "winning_brands": [
    {{"brand": "...", "why_winning": "...", "weakness": "..."}}
  ],
  "gap_angles": ["gap1", "gap2", "gap3"],
  "winning_creative_format": "video_ugc|static_image|carousel|mixed",
  "price_clusters": {{"budget": "under £X", "mid": "£X-£Y", "premium": "over £Y"}},
  "market_saturation": "low|medium|high",
  "recommended_angle": {{
    "angle": "the specific angle to use",
    "rationale": "why this works",
    "hook": "opening hook for a video",
    "headline": "headline for a static ad",
    "differentiator": "what makes this different from all competitors"
  }},
  "launch_platform": "amazon_uk|tiktok_shop|shopify|all",
  "urgency": "high|medium|low",
  "notes": "any important observations"
}}

Return ONLY valid JSON.
"""

    response = call_ai(
        task="competitor",
        system="You are an expert DTC brand strategist with deep expertise in paid social, Amazon and ecommerce.",
        prompt=prompt,
        max_tokens=1500,
    )

    try:
        raw = response.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        log.error(f"Competitor angle analysis failed: {e}")
        return {}


def build_gtm_brief(
    keyword: str,
    score_result: dict,
    icp: dict,
    competitor_analysis: dict,
    target_market: str = "UK",
) -> dict:
    """
    Assemble the full GTM (Go-To-Market) brief for a product.
    This is the document that drives all subsequent actions:
    - Creator outreach brief
    - Image ad brief
    - TikTok/Instagram organic brief
    - SEO brief (phase 2)
    - Google Ads brief (phase 3)
    """
    launch_phase = competitor_analysis.get("launch_platform", "tiktok_shop")
    saturation = competitor_analysis.get("market_saturation", "medium")

    prompt = f"""
You are a DTC brand launch strategist. Build a complete GTM brief for:

PRODUCT: {keyword}
MARKET: {target_market}
OPPORTUNITY SCORE: {score_result.get('total_score', 0)}/100
MARKET SATURATION: {saturation}

AVATAR:
{json.dumps(icp, indent=2)[:600]}

RECOMMENDED ANGLE: {competitor_analysis.get('recommended_angle', {}).get('angle', 'Not set')}
DIFFERENTIATION: {competitor_analysis.get('recommended_angle', {}).get('differentiator', 'Not set')}
WINNING FORMAT: {competitor_analysis.get('winning_creative_format', 'video_ugc')}
PRICE RANGE: {json.dumps(competitor_analysis.get('price_clusters', {}))}

Return a complete GTM brief as JSON:
{{
  "product": "{keyword}",
  "target_market": "{target_market}",
  "launch_channel": "tiktok_shop|amazon_uk|shopify",
  "phase_1_organic": {{
    "strategy": "organic_creator_seeding",
    "creator_type": "micro (10k-100k) or mid (100k-500k)",
    "creator_niche": "...",
    "content_style": "ugc_review|tutorial|transformation|lifestyle",
    "posting_frequency": "X posts/week",
    "key_hashtags": ["...", "...", "..."],
    "music_direction": "trending or original sound",
    "video_brief_hook": "First 3 seconds: ...",
    "video_brief_body": "Middle 20 seconds: ...",
    "video_brief_cta": "End: ..."
  }},
  "phase_1_static_ads": {{
    "headline": "...",
    "subheadline": "...",
    "body_copy": "...",
    "cta": "...",
    "visual_direction": "product only|lifestyle|before-after|text-overlay",
    "colour_palette": "describe the feel"
  }},
  "phase_2_seo": {{
    "primary_keyword": "...",
    "secondary_keywords": ["...", "...", "..."],
    "content_types": ["blog post", "comparison article", "..."],
    "target_pages": 5,
    "timeline": "months 2-4"
  }},
  "phase_3_paid": {{
    "trigger": "first £500 revenue OR 100 organic saves",
    "google_ads_campaign_type": "shopping|search|performance_max",
    "daily_budget_start": "£10-20",
    "target_roas": "3x",
    "meta_objective": "traffic|sales|ATC"
  }},
  "sourcing": {{
    "platform": "alibaba|1688|local_manufacturer",
    "search_terms": ["...", "...", "..."],
    "target_cogs": "£X per unit",
    "target_sell_price": "£X",
    "target_margin_pct": 50,
    "moq_estimate": "200-500 units",
    "sample_cost": "£50-150"
  }},
  "kpis": {{
    "month_1_target": "X organic views, Y creator posts",
    "month_2_target": "X sales, £Y revenue",
    "month_3_target": "£X MRR",
    "break_even_units": 0
  }},
  "risks": ["...", "...", "..."],
  "next_actions": ["...", "...", "..."]
}}

Return ONLY valid JSON.
"""

    response = call_ai(
        task="product_brief",
        system="You are an expert DTC brand launch strategist who has launched 50+ products.",
        prompt=prompt,
        max_tokens=2000,
    )

    try:
        raw = response.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        log.error(f"GTM brief generation failed: {e}")
        return {}


def generate_static_ad_brief(keyword: str, icp: dict, angle: dict) -> dict:
    """
    Generate a static image ad creative brief.
    For Creatomate rendering — product photography + text overlays, no AI-generated human faces.
    For human faces in video: use Spark Ads (creator's own TikTok post) or
    Meta whitelisted ads (creator grants account access).
    """
    return {
        "product": keyword,
        "ad_type": "static_image",
        "headline": angle.get("headline", icp.get("best_headline", f"The {keyword} that actually works")),
        "subheadline": f"For {icp.get('avatar_name', 'people like you')} who want real results",
        "body_copy": f"{icp.get('key_pain_points', [''])[0]} → {icp.get('core_desires', [''])[0]}",
        "cta_button": "Shop Now",
        "render_via": "creatomate",   # → auto-rendered by creative_studio.py
        "visual_direction": {
            "type": "product_only_with_text_overlay",
            "note": "USE PRODUCT PHOTOGRAPHY ONLY — no AI-generated human faces",
            "background": "clean white or lifestyle context (not human face)",
            "text_placement": "bottom third or left side overlay",
            "font_style": "bold, high contrast",
        },
        "format_sizes": ["1x1 (1080x1080)", "9x16 (1080x1920)", "4x5 (1080x1350)"],
        "colour_note": "Match product packaging colours for brand consistency",
        "legal_note": "No claims that require medical substantiation without evidence",
        "human_face_strategy": {
            "tiktok": "Spark Ads — boost creator's own post (they authorize via TikTok's Spark Ad flow)",
            "instagram": "Meta whitelisted ads — creator grants account access, we control targeting",
            "note": "Real creator faces via their own content. No AI-generated faces. Fully permissible.",
        },
        "video_without_face": {
            "tool": "Remotion + Creatomate",
            "style": "Product reveal → feature callouts → CTA animation",
            "voiceover": "ElevenLabs AI voice (text-to-speech only, no face generated)",
        },
        "created_at": datetime.utcnow().isoformat(),
    }


def generate_video_ad_brief(keyword: str, icp: dict, angle: dict, gtm_brief: dict) -> dict:
    """
    Generate a structured video ad brief covering all creative routes:
    A) No face needed: Remotion animated product showcase + ElevenLabs voiceover
    B) Creator face: Spark Ads (TikTok) / Whitelisted ads (Meta) using creator's OWN posted content
    C) Creatomate: product clips + stock footage + voiceover (no AI face)
    """
    organic = gtm_brief.get("phase_1_organic", {})
    return {
        "product": keyword,
        "ad_type": "video",
        "route_a_no_face": {
            "tool": "Remotion",
            "style": "animated product showcase",
            "duration": "5-15 seconds",
            "elements": ["product image zoom", "feature text callouts", "brand colours", "CTA"],
            "voiceover": "ElevenLabs — female_warm or male_calm voice",
            "hook": angle.get("hook", f"This {keyword} changed everything for me"),
            "use_for": "TikTok Feed, Meta Feed, YouTube Pre-roll",
        },
        "route_b_creator_face": {
            "tool": "Spark Ads (TikTok) / Meta Whitelisted Ads",
            "source": "Creator's own posted content — we boost it, don't create it",
            "authorization": "TikTok: creator approves via Spark Ad code | Meta: branded content partner",
            "fee": "£50-150 one-time authorization fee OR bonus commission",
            "targeting": "We control: audience, budget, bid — Creator controls: content, creative",
            "note": "Real human, real content, real voice. Fully permissible.",
        },
        "route_c_creatomate": {
            "tool": "Creatomate",
            "template": "video_product_showcase or video_ugc_frame",
            "elements": ["product image", "stock footage (non-AI)", "text overlay", "voiceover"],
            "duration": "15-30 seconds",
            "formats": ["9:16 for TikTok/Reels", "1:1 for Meta Feed", "16:9 for YouTube"],
        },
        "content_brief_for_creators": {
            "hook": organic.get("video_brief_hook", angle.get("hook", "")),
            "body": organic.get("video_brief_body", ""),
            "cta": organic.get("video_brief_cta", "Link in bio to shop"),
            "style": organic.get("content_style", "ugc_review"),
            "hashtags": organic.get("key_hashtags", []),
            "music": organic.get("music_direction", "trending sound"),
            "do": ["show the product", "be honest", "show result/benefit", "mention the discount code"],
            "dont": ["make health claims", "use competitor names", "use other brand logos"],
        },
        "icp_reminder": {
            "avatar": icp.get("avatar_name", ""),
            "pain": icp.get("key_pain_points", [""])[0],
            "desire": icp.get("core_desires", [""])[0],
            "trust_signals": icp.get("trust_signals_that_work", []),
        },
        "created_at": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Full competitor intelligence run
# ---------------------------------------------------------------------------

def run_competitor_intelligence(
    keyword: str,
    score_result: dict,
    icp: dict,
    target_market: str = "UK",
    dry_run: bool = False,
) -> dict:
    """
    Full competitor intelligence + GTM brief for one high-scoring product.
    Called when product score >= 70.
    """
    log.info(f"Running competitor intelligence for: {keyword}")

    if dry_run:
        return {
            "keyword": keyword,
            "competitor_analysis": {"recommended_angle": {"angle": "Dry run placeholder"}},
            "gtm_brief": {},
            "static_ad_brief": {},
        }

    country_code = "GB" if target_market == "UK" else _market_to_country_code(target_market)

    # Collect competitor data
    log.info(f"  → Scraping Meta competitor ads...")
    meta_ads = scan_meta_competitor_ads(keyword, country_code=country_code, limit=50)
    time.sleep(2)

    log.info(f"  → Scraping TikTok competitor content...")
    tiktok_content = scan_tiktok_competitor_content(keyword, region=country_code, limit=30)
    time.sleep(2)

    log.info(f"  → Scraping Amazon competitor listings...")
    amazon_listings = scan_amazon_competitor_listings(keyword, limit=20)
    time.sleep(2)

    log.info(f"  → Scraping Google Shopping...")
    google_shopping = scan_google_shopping_competitors(keyword, country=country_code)
    time.sleep(2)

    # AI analysis
    log.info(f"  → Running AI competitor analysis...")
    competitor_analysis = analyse_competitor_angles(
        keyword=keyword,
        meta_ads=meta_ads,
        tiktok_content=tiktok_content,
        amazon_listings=amazon_listings,
        google_shopping=google_shopping,
    )
    time.sleep(2)

    # Build full GTM brief
    log.info(f"  → Building GTM brief...")
    gtm_brief = build_gtm_brief(
        keyword=keyword,
        score_result=score_result,
        icp=icp,
        competitor_analysis=competitor_analysis,
        target_market=target_market,
    )

    # Generate static + video ad briefs
    recommended_angle = competitor_analysis.get("recommended_angle", {})
    static_ad_brief = generate_static_ad_brief(keyword, icp, recommended_angle)
    video_ad_brief  = generate_video_ad_brief(keyword, icp, recommended_angle, gtm_brief)

    # Trigger Creatomate + Remotion + ElevenLabs renders
    # (only if product image URL is available — passed in via score_result or icp)
    product_image_url = score_result.get("product_image_url", "") or icp.get("product_image_url", "")
    creative_assets = {}
    if product_image_url:
        log.info(f"  → Launching creative production (Creatomate + Remotion + ElevenLabs)...")
        try:
            from lib.creative_studio import produce_ad_creative_set, process_creator_posts_for_spark_ads
            creative_assets = produce_ad_creative_set(
                product=keyword,
                icp=icp,
                gtm_brief=gtm_brief,
                competitor_analysis=competitor_analysis,
                product_image_url=product_image_url,
                dry_run=False,
            )
            # Check if any creators have already posted → request Spark Ad authorization
            spark_requests = process_creator_posts_for_spark_ads(product=keyword)
            creative_assets["spark_ad_requests"] = spark_requests
            if spark_requests:
                log.info(f"  → {len(spark_requests)} Spark Ad authorization requests drafted")
        except Exception as e:
            log.error(f"  Creative production error: {e}")
    else:
        log.info(f"  → No product image URL yet — creative production skipped (add later)")

    result = {
        "keyword": keyword,
        "target_market": target_market,
        "competitor_analysis": competitor_analysis,
        "gtm_brief": gtm_brief,
        "static_ad_brief": static_ad_brief,
        "video_ad_brief": video_ad_brief,
        "creative_assets": creative_assets,
        "meta_competitor_count": len(meta_ads),
        "tiktok_top_creator": tiktok_content[0] if tiktok_content else {},
        "amazon_top_competitor": amazon_listings[0] if amazon_listings else {},
        "analysed_at": datetime.utcnow().isoformat(),
    }

    # Save to Airtable
    _log_gtm_brief_to_airtable(result)

    log.info(f"  ✓ Competitor intelligence + creatives complete for: {keyword}")
    return result


def _log_gtm_brief_to_airtable(result: dict):
    """Log GTM brief to Airtable:GTMBriefs."""
    try:
        gtm = result.get("gtm_brief", {})
        ca = result.get("competitor_analysis", {})
        fields = {
            "Product": result["keyword"],
            "TargetMarket": result.get("target_market", "UK"),
            "LaunchChannel": gtm.get("launch_channel", ""),
            "RecommendedAngle": ca.get("recommended_angle", {}).get("angle", ""),
            "Differentiator": ca.get("recommended_angle", {}).get("differentiator", ""),
            "MarketSaturation": ca.get("market_saturation", ""),
            "WinningFormat": ca.get("winning_creative_format", ""),
            "VideoHook": gtm.get("phase_1_organic", {}).get("video_brief_hook", ""),
            "StaticHeadline": result.get("static_ad_brief", {}).get("headline", ""),
            "SourcingPlatform": gtm.get("sourcing", {}).get("platform", ""),
            "TargetMarginPct": gtm.get("sourcing", {}).get("target_margin_pct", 0),
            "Month3Target": gtm.get("kpis", {}).get("month_3_target", ""),
            "NextActions": " | ".join(gtm.get("next_actions", [])[:3]),
            "Status": "Ready",
            "CreatedAt": datetime.utcnow().isoformat(),
        }
        upsert_record("GTMBriefs", fields, match_field="Product")
    except Exception as e:
        log.error(f"GTM brief Airtable log failed: {e}")


def _market_to_country_code(market: str) -> str:
    mapping = {
        "UK": "GB", "Nigeria": "NG", "Ghana": "GH", "Morocco": "MA",
        "UAE": "AE", "Saudi Arabia": "SA", "India": "IN",
        "Indonesia": "ID", "Brazil": "BR", "Turkey": "TR",
        "Germany": "DE", "France": "FR",
    }
    return mapping.get(market, "GB")
