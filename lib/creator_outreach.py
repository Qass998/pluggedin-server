"""
creator_outreach.py — PluggedIN Creator Seeding Pipeline
Organic-first strategy: seed products to real micro/mid creators,
pay commission on resulting sales. NO AI-generated human faces.

Philosophy:
  - Real creators > AI-generated content
  - Micro (10k-100k followers): high engagement, authentic audience
  - Mid (100k-500k followers): broader reach, still relatable
  - Seed first (send free product) → earn trust → offer affiliate commission
  - Track organic views BEFORE any paid ad spend
  - Only scale with ads once you have proven organic content

Platforms:
  - TikTok (primary — highest organic reach for product content)
  - Instagram Reels (secondary — lifestyle + beauty)
  - YouTube Shorts (tertiary — review / unboxing content)

Commission model:
  - 10-15% commission on sales they generate
  - Tracked via unique discount code per creator
  - Monthly payments via bank transfer / PayPal
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("creator_outreach")
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
    from lib.vendor_outreach import send_email, log_outreach
except ImportError:
    try:
        from vendor_outreach import send_email, log_outreach
    except ImportError:
        def send_email(to, subject, body): log.info(f"[MOCK EMAIL] → {to}: {subject}")
        def log_outreach(record): pass

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

COMMISSION_RATE = 0.12          # 12% default affiliate commission
MIN_ENGAGEMENT_RATE = 0.03      # 3% minimum (avg is 1-3%, micro often 5-10%)
MIN_FOLLOWERS_MICRO = 10_000
MAX_FOLLOWERS_MICRO = 100_000
MIN_FOLLOWERS_MID = 100_000
MAX_FOLLOWERS_MID = 500_000

CREATOR_NICHES = {
    "health_wellness": ["#healthtok", "#wellnesstok", "#supplementstack", "#fitnesstok", "#healthylifestyle"],
    "beauty_skincare": ["#skincare", "#skincarecheck", "#beautytok", "#glowup", "#skincareroutine"],
    "lifestyle": ["#lifestyletok", "#dayinmylife", "#productreview", "#amazonfinds", "#tiktokmademebuyit"],
    "fitness": ["#fitnessmotivation", "#gymtok", "#workoutroutine", "#fittok"],
    "food_nutrition": ["#foodtok", "#nutrition", "#mealprep", "#healthyfood"],
    "parenting": ["#parentingtips", "#momtok", "#dadtok", "#babytok"],
    "pet": ["#dogtok", "#cattok", "#petsoftiktok", "#petcare"],
    "home_living": ["#hometok", "#homeorganisation", "#cleaningtok", "#interiordesign"],
    "sustainable_living": ["#sustainableliving", "#ecofriendly", "#zerowaste", "#greenliving"],
    "mena_lifestyle": ["#arabiclifestyle", "#dubaifood", "#saudiarabia", "#uae"],
    "africa_lifestyle": ["#naijatiktok", "#nigeriancreator", "#ghanatiktok", "#africantiktok"],
    "uk_lifestyle": ["#uktiktok", "#londonlife", "#ukfinds", "#uklifestyle"],
}

# ---------------------------------------------------------------------------
# Creator discovery
# ---------------------------------------------------------------------------

def find_creators_by_niche(
    product_keyword: str,
    niche: str,
    region: str = "GB",
    tier: str = "micro",
    limit: int = 20,
) -> list[dict]:
    """
    Find TikTok creators who post content relevant to a product niche.
    Uses Apify TikTok scraper to find creators by hashtag.

    Returns creators with follower count, engagement rate, email (if visible),
    contact method, and a relevance score.
    """
    if not _apify:
        log.warning("Apify not available — creator discovery skipped")
        return []

    hashtags = CREATOR_NICHES.get(niche, [f"#{product_keyword.replace(' ', '')}"])
    creators = []
    seen_usernames = set()

    for hashtag in hashtags[:3]:  # Check top 3 hashtags for this niche
        try:
            run = _apify.actor("clockworks/tiktok-scraper").call(run_input={
                "hashtags": [hashtag.lstrip("#")],
                "maxItems": limit * 2,
                "proxyConfiguration": {"useApifyProxy": True},
            })
            items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())

            for item in items:
                author = item.get("authorMeta", {})
                username = author.get("name", "")
                if not username or username in seen_usernames:
                    continue
                seen_usernames.add(username)

                followers = author.get("fans", 0)
                hearts = author.get("heart", 0)
                videos = author.get("video", 1)

                # Filter by tier
                if tier == "micro" and not (MIN_FOLLOWERS_MICRO <= followers <= MAX_FOLLOWERS_MICRO):
                    continue
                if tier == "mid" and not (MIN_FOLLOWERS_MID <= followers <= MAX_FOLLOWERS_MID):
                    continue

                # Estimate engagement rate
                avg_views = item.get("playCount", 0)
                avg_likes = item.get("diggCount", 0)
                eng_rate = round(avg_likes / max(followers, 1), 4)

                if eng_rate < MIN_ENGAGEMENT_RATE:
                    continue  # Skip low-engagement creators

                bio = author.get("signature", "")
                email = _extract_email_from_bio(bio)

                creators.append({
                    "username": username,
                    "profile_url": f"https://www.tiktok.com/@{username}",
                    "followers": followers,
                    "tier": tier,
                    "avg_views_this_post": avg_views,
                    "engagement_rate": eng_rate,
                    "niche": niche,
                    "hashtag_found_on": hashtag,
                    "bio": bio[:200],
                    "email": email,
                    "has_email": bool(email),
                    "contact_method": "email" if email else "dm",
                    "region_guess": _guess_region_from_bio(bio),
                    "hearts_total": hearts,
                    "relevance_score": _score_creator_relevance(product_keyword, bio, niche, followers, eng_rate),
                })

            time.sleep(3)

        except Exception as e:
            log.error(f"Creator discovery failed for {hashtag}: {e}")

    # Sort by relevance score
    creators = sorted(creators, key=lambda x: x["relevance_score"], reverse=True)
    return creators[:limit]


def find_instagram_creators(
    product_keyword: str,
    niche: str,
    region: str = "GB",
    limit: int = 15,
) -> list[dict]:
    """
    Find Instagram creators for a product niche.
    Uses Apify Instagram hashtag scraper.
    """
    if not _apify:
        return []

    hashtags = CREATOR_NICHES.get(niche, [f"#{product_keyword.replace(' ', '')}"])
    creators = []
    seen = set()

    for hashtag in hashtags[:2]:
        try:
            run = _apify.actor("apify/instagram-hashtag-scraper").call(run_input={
                "hashtags": [hashtag.lstrip("#")],
                "resultsLimit": limit * 2,
            })
            items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())

            for item in items:
                owner = item.get("ownerUsername", "")
                if not owner or owner in seen:
                    continue
                seen.add(owner)

                followers = item.get("ownerFollowersCount", 0)
                if not (MIN_FOLLOWERS_MICRO <= followers <= MAX_FOLLOWERS_MID):
                    continue

                likes = item.get("likesCount", 0)
                eng_rate = round(likes / max(followers, 1), 4)

                if eng_rate < MIN_ENGAGEMENT_RATE:
                    continue

                creators.append({
                    "platform": "instagram",
                    "username": owner,
                    "profile_url": f"https://www.instagram.com/{owner}",
                    "followers": followers,
                    "tier": "micro" if followers <= MAX_FOLLOWERS_MICRO else "mid",
                    "engagement_rate": eng_rate,
                    "niche": niche,
                    "contact_method": "dm",
                    "email": None,
                    "has_email": False,
                    "relevance_score": _score_creator_relevance(product_keyword, "", niche, followers, eng_rate),
                })

            time.sleep(3)
        except Exception as e:
            log.error(f"Instagram creator discovery failed for {hashtag}: {e}")

    return sorted(creators, key=lambda x: x["relevance_score"], reverse=True)[:limit]


def _extract_email_from_bio(bio: str) -> Optional[str]:
    """Extract email from creator bio."""
    import re
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(pattern, bio)
    return matches[0] if matches else None


def _guess_region_from_bio(bio: str) -> str:
    """Roughly guess creator region from bio keywords."""
    bio_lower = bio.lower()
    if any(kw in bio_lower for kw in ["london", "uk", "england", "scotland", "wales"]):
        return "UK"
    if any(kw in bio_lower for kw in ["dubai", "uae", "abu dhabi"]):
        return "UAE"
    if any(kw in bio_lower for kw in ["lagos", "nigeria", "abuja"]):
        return "Nigeria"
    if any(kw in bio_lower for kw in ["riyadh", "jeddah", "saudi"]):
        return "Saudi Arabia"
    if any(kw in bio_lower for kw in ["accra", "ghana", "kumasi"]):
        return "Ghana"
    if any(kw in bio_lower for kw in ["us", "usa", "new york", "los angeles", "miami"]):
        return "US"
    return "Unknown"


def _score_creator_relevance(
    product_keyword: str,
    bio: str,
    niche: str,
    followers: int,
    eng_rate: float,
) -> float:
    """
    Score creator relevance 0-100.
    Weights: niche match (40%) + engagement rate (35%) + follower count (25%).
    """
    # Niche match (40 pts)
    keyword_lower = product_keyword.lower()
    bio_lower = bio.lower()
    niche_score = 40 if keyword_lower in bio_lower else 20

    # Engagement rate (35 pts): 5%+ = 35, 3-5% = 25, 1-3% = 10
    if eng_rate >= 0.05:
        eng_score = 35
    elif eng_rate >= 0.03:
        eng_score = 25
    else:
        eng_score = 10

    # Follower count sweet spot (25 pts): 30k-80k = best for seeding
    if 30_000 <= followers <= 80_000:
        follower_score = 25
    elif 10_000 <= followers <= 150_000:
        follower_score = 18
    else:
        follower_score = 10

    return niche_score + eng_score + follower_score


# ---------------------------------------------------------------------------
# Outreach email generation
# ---------------------------------------------------------------------------

def draft_creator_outreach_email(
    creator: dict,
    product_keyword: str,
    gtm_brief: dict,
    outreach_type: str = "initial",
) -> dict:
    """
    Draft a personalised outreach email to a creator.
    Tone: casual, genuine, not corporate.
    Offer: free product in exchange for honest review + 12% commission.

    NOTE: We are NOT asking for AI-generated content involving human faces.
    We're inviting creators to make their own authentic content.
    """
    sourcing = gtm_brief.get("sourcing", {})
    sell_price = sourcing.get("target_sell_price", "£25")

    if outreach_type == "initial":
        subject_line = f"Free {product_keyword} for you to try + 12% commission"
        tone_prompt = "casual, genuine, excited. NOT corporate or salesy. Like a friend in the industry reaching out."
    elif outreach_type == "followup":
        subject_line = f"Still interested in the {product_keyword} collab?"
        tone_prompt = "friendly follow-up. Brief. Acknowledging they're busy."
    else:
        subject_line = f"Final message about {product_keyword} collaboration"
        tone_prompt = "closing the loop, no pressure, leaving the door open."

    prompt = f"""
Write a DM/email to a {creator.get('tier', 'micro')} creator (@{creator.get('username', 'creator')})
about a product collaboration for "{product_keyword}".

OUTREACH TYPE: {outreach_type}
TONE: {tone_prompt}

Context:
- We're a UK brand (PluggedIN/SourcedStore) launching {product_keyword}
- Product sells for {sell_price}
- We want to send them a FREE product, no strings attached
- If they like it and post, they get 12% commission on every sale from their unique code
- They keep full creative control — we don't script them
- This is an organic-first strategy, not a paid ad campaign

Creator profile:
- Username: @{creator.get('username', '')}
- Followers: {creator.get('followers', 0):,}
- Niche: {creator.get('niche', '')}
- Platform: {creator.get('platform', 'TikTok')}

Write a SHORT message (3-5 sentences maximum for DM, 5-7 sentences for email).
Start with their name reference or a genuine comment about their content style.
Do NOT use phrases like "I hope this email finds you well" or "I am reaching out".
End with a clear, easy response request.

Format:
SUBJECT: {subject_line}
---
[message body]
"""

    response = call_ai(
        task="outreach",
        system="You write authentic, non-corporate creator outreach that gets responses.",
        prompt=prompt,
        max_tokens=400,
    )

    # Parse subject and body
    lines = response.strip().split("\n")
    subject = subject_line  # fallback
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("SUBJECT:"):
            subject = line.replace("SUBJECT:", "").strip()
        if line.strip() == "---":
            body_start = i + 1
            break

    body = "\n".join(lines[body_start:]).strip()
    if not body:
        body = response.strip()

    return {
        "creator_username": creator.get("username", ""),
        "creator_email": creator.get("email", ""),
        "platform": creator.get("platform", "TikTok"),
        "contact_method": creator.get("contact_method", "dm"),
        "subject": subject,
        "body": body,
        "outreach_type": outreach_type,
        "product": product_keyword,
        "generated_at": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Seeding pipeline management
# ---------------------------------------------------------------------------

def log_creator_to_pipeline(creator: dict, product: str, outreach: dict):
    """Log creator to Airtable:CreatorPipeline."""
    try:
        fields = {
            "Username": creator.get("username", ""),
            "Platform": creator.get("platform", "TikTok"),
            "ProfileURL": creator.get("profile_url", ""),
            "Followers": creator.get("followers", 0),
            "Tier": creator.get("tier", "micro"),
            "EngagementRate": creator.get("engagement_rate", 0),
            "Niche": creator.get("niche", ""),
            "Product": product,
            "HasEmail": creator.get("has_email", False),
            "ContactMethod": creator.get("contact_method", "dm"),
            "OutreachStatus": "OutreachDrafted",
            "OutreachType": outreach.get("outreach_type", "initial"),
            "RelevanceScore": creator.get("relevance_score", 0),
            "Region": creator.get("region_guess", "Unknown"),
            "DiscoveredAt": datetime.utcnow().isoformat(),
            "NextAction": "Send outreach",
            "NextActionDue": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d"),
        }
        upsert_record("CreatorPipeline", fields, match_field="Username")
    except Exception as e:
        log.error(f"Creator pipeline log failed: {e}")


def send_creator_outreach(outreach: dict, dry_run: bool = False) -> bool:
    """
    Send outreach to a creator.
    Via email if available, otherwise logs for manual DM.
    """
    if dry_run:
        log.info(f"[DRY RUN] Would send to @{outreach['creator_username']}: {outreach['subject']}")
        return True

    if outreach.get("contact_method") == "email" and outreach.get("creator_email"):
        try:
            send_email(
                to=outreach["creator_email"],
                subject=outreach["subject"],
                body=outreach["body"],
            )
            log.info(f"  ✓ Email sent to @{outreach['creator_username']}")
            return True
        except Exception as e:
            log.error(f"Email send failed for @{outreach['creator_username']}: {e}")
            return False
    else:
        # Log for manual DM
        log.info(f"  → Manual DM needed for @{outreach['creator_username']} (no email found)")
        _log_manual_dm_queue(outreach)
        return True


def _log_manual_dm_queue(outreach: dict):
    """Log creators who need manual DM to Airtable:ManualDMQueue."""
    try:
        upsert_record("ManualDMQueue", {
            "Username": outreach["creator_username"],
            "Platform": outreach["platform"],
            "Product": outreach["product"],
            "MessageDraft": outreach["body"][:500],
            "Status": "Pending",
            "CreatedAt": datetime.utcnow().isoformat(),
        }, match_field="Username")
    except Exception as e:
        log.error(f"Manual DM queue log failed: {e}")


def check_creator_pipeline_followups() -> list[dict]:
    """
    Check existing creators in pipeline for required follow-up actions.
    Called daily at 06:30 alongside product intelligence.
    """
    actions_needed = []

    try:
        records = get_records("CreatorPipeline", formula="NOT({OutreachStatus} = 'Closed')")
        today = datetime.utcnow().date()

        for record in records:
            fields = record.get("fields", {})
            username = fields.get("Username", "")
            status = fields.get("OutreachStatus", "")
            next_action_due_str = fields.get("NextActionDue", "")

            try:
                next_action_due = datetime.strptime(next_action_due_str, "%Y-%m-%d").date() if next_action_due_str else today
            except Exception:
                next_action_due = today

            if next_action_due > today:
                continue  # Not yet due

            if status == "OutreachDrafted":
                actions_needed.append({
                    "username": username,
                    "action": "send_initial_outreach",
                    "record_id": record.get("id", ""),
                    "product": fields.get("Product", ""),
                    "contact_method": fields.get("ContactMethod", "dm"),
                })

            elif status == "OutreachSent":
                days_since = (today - next_action_due).days + 5
                if days_since >= 5:
                    actions_needed.append({
                        "username": username,
                        "action": "send_followup",
                        "record_id": record.get("id", ""),
                        "product": fields.get("Product", ""),
                        "contact_method": fields.get("ContactMethod", "dm"),
                    })

            elif status == "FollowupSent":
                days_since = (today - next_action_due).days + 5
                if days_since >= 5:
                    actions_needed.append({
                        "username": username,
                        "action": "final_attempt",
                        "record_id": record.get("id", ""),
                        "product": fields.get("Product", ""),
                        "contact_method": fields.get("ContactMethod", "dm"),
                    })

            elif status == "ProductSent":
                actions_needed.append({
                    "username": username,
                    "action": "check_posting_status",
                    "record_id": record.get("id", ""),
                    "product": fields.get("Product", ""),
                })

            elif status == "Posted":
                actions_needed.append({
                    "username": username,
                    "action": "track_performance",
                    "record_id": record.get("id", ""),
                    "product": fields.get("Product", ""),
                    "platform": fields.get("Platform", "TikTok"),
                })

    except Exception as e:
        log.error(f"Creator pipeline follow-up check failed: {e}")

    return actions_needed


def generate_unique_discount_code(creator_username: str, product: str) -> str:
    """Generate a unique discount code for affiliate tracking."""
    clean_username = creator_username.upper().replace(".", "")[:6]
    clean_product = "".join([w[0] for w in product.split()[:2]]).upper()
    return f"{clean_product}{clean_username}12"  # e.g., CWSARAH12 (12% off)


# ---------------------------------------------------------------------------
# Organic content performance tracking
# ---------------------------------------------------------------------------

def track_creator_post_performance(
    creator_username: str,
    post_url: str,
    platform: str = "TikTok",
) -> dict:
    """
    Track views, likes, comments, shares for a creator's post.
    This data is compiled BEFORE any ad spend decision.
    If organic performance is good → scale with paid ads.
    If poor → try different creator or angle first.
    """
    if not _apify:
        return {}

    performance = {
        "creator": creator_username,
        "platform": platform,
        "post_url": post_url,
        "views": 0,
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "saves": 0,
        "engagement_rate": 0,
        "organic_score": 0,
        "recommendation": "insufficient_data",
        "tracked_at": datetime.utcnow().isoformat(),
    }

    try:
        if platform.lower() == "tiktok":
            run = _apify.actor("clockworks/tiktok-scraper").call(run_input={
                "urls": [post_url],
                "maxItems": 1,
            })
            items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())
            if items:
                item = items[0]
                views = item.get("playCount", 0)
                likes = item.get("diggCount", 0)
                comments = item.get("commentCount", 0)
                shares = item.get("shareCount", 0)
                performance.update({
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "engagement_rate": round((likes + comments) / max(views, 1), 4),
                })

        # Organic score: views relative to creator tier
        views = performance["views"]
        if views >= 100_000:
            performance["organic_score"] = 90
            performance["recommendation"] = "scale_with_ads"
        elif views >= 30_000:
            performance["organic_score"] = 70
            performance["recommendation"] = "boost_this_post"
        elif views >= 10_000:
            performance["organic_score"] = 50
            performance["recommendation"] = "monitor_more_posts"
        elif views >= 1_000:
            performance["organic_score"] = 30
            performance["recommendation"] = "try_different_angle"
        else:
            performance["organic_score"] = 10
            performance["recommendation"] = "try_different_creator"

    except Exception as e:
        log.error(f"Performance tracking failed for {post_url}: {e}")

    return performance


def compile_organic_performance_report(product: str) -> dict:
    """
    Compile all organic performance data for a product before ad spend decision.
    This is the gate before any paid advertising begins.
    """
    try:
        records = get_records("CreatorPipeline", formula=f"AND({{Product}}='{product}', {{OutreachStatus}}='Posted')")
    except Exception:
        records = []

    total_views = 0
    total_engagement = 0
    top_posts = []
    recommendation = "keep_organic"

    for record in records:
        fields = record.get("fields", {})
        post_url = fields.get("PostURL", "")
        if not post_url:
            continue

        perf = track_creator_post_performance(
            creator_username=fields.get("Username", ""),
            post_url=post_url,
            platform=fields.get("Platform", "TikTok"),
        )

        total_views += perf.get("views", 0)
        total_engagement += perf.get("likes", 0) + perf.get("comments", 0)
        top_posts.append(perf)

    # Decision gate
    if total_views >= 200_000:
        recommendation = "scale_with_paid_ads"
    elif total_views >= 50_000:
        recommendation = "boost_top_posts_then_ads"
    elif total_views >= 10_000:
        recommendation = "continue_organic_seeding"
    else:
        recommendation = "test_different_angle"

    report = {
        "product": product,
        "total_organic_views": total_views,
        "total_engagement": total_engagement,
        "posts_tracked": len(top_posts),
        "top_posts": sorted(top_posts, key=lambda x: x.get("views", 0), reverse=True)[:3],
        "recommendation": recommendation,
        "ready_for_ads": recommendation in ["scale_with_paid_ads", "boost_top_posts_then_ads"],
        "compiled_at": datetime.utcnow().isoformat(),
    }

    log.info(f"Organic performance for '{product}': {total_views:,} views → {recommendation}")
    return report


# ---------------------------------------------------------------------------
# Full daily creator outreach run
# ---------------------------------------------------------------------------

def run_daily_creator_outreach(
    product_keyword: str,
    gtm_brief: dict,
    target_niches: list[str] = None,
    creators_per_day: int = 10,
    dry_run: bool = False,
) -> dict:
    """
    Daily creator outreach pipeline:
    1. Find relevant micro/mid creators on TikTok + Instagram
    2. Draft personalised outreach for each
    3. Send via email (or queue for manual DM)
    4. Log to Airtable:CreatorPipeline
    5. Check existing pipeline for follow-ups

    Max 10 outreaches per day (quality over quantity).
    """
    log.info(f"=== Daily Creator Outreach: {product_keyword} ===")

    target_niches = target_niches or _guess_niches_for_product(product_keyword)
    results = {
        "product": product_keyword,
        "creators_found": 0,
        "outreach_sent": 0,
        "email_sent": 0,
        "dm_queued": 0,
        "followups_triggered": 0,
        "ran_at": datetime.utcnow().isoformat(),
    }

    # 1. Find new creators
    all_creators = []
    for niche in target_niches[:2]:
        log.info(f"  → Finding micro creators in niche: {niche}")
        tiktok_creators = find_creators_by_niche(product_keyword, niche, tier="micro", limit=8)
        all_creators.extend(tiktok_creators)
        time.sleep(3)

        log.info(f"  → Finding Instagram creators in niche: {niche}")
        ig_creators = find_instagram_creators(product_keyword, niche, limit=5)
        all_creators.extend(ig_creators)
        time.sleep(3)

    results["creators_found"] = len(all_creators)

    # 2. Take top N by relevance score
    top_creators = sorted(all_creators, key=lambda x: x.get("relevance_score", 0), reverse=True)
    top_creators = top_creators[:creators_per_day]

    # 3. Draft + send outreach
    for creator in top_creators:
        try:
            outreach = draft_creator_outreach_email(
                creator=creator,
                product_keyword=product_keyword,
                gtm_brief=gtm_brief,
                outreach_type="initial",
            )

            sent = send_creator_outreach(outreach, dry_run=dry_run)
            if sent:
                results["outreach_sent"] += 1
                if creator.get("has_email"):
                    results["email_sent"] += 1
                else:
                    results["dm_queued"] += 1

            log_creator_to_pipeline(creator, product_keyword, outreach)

        except Exception as e:
            log.error(f"Creator outreach failed for @{creator.get('username', '?')}: {e}")

    # 4. Check existing pipeline for follow-ups
    log.info("  → Checking pipeline for follow-ups...")
    followup_actions = check_creator_pipeline_followups()
    for action in followup_actions[:5]:  # Cap at 5 follow-ups per day
        try:
            if action["action"] in ["send_followup", "final_attempt"]:
                creator_stub = {
                    "username": action["username"],
                    "platform": "TikTok",
                    "has_email": False,
                    "contact_method": action.get("contact_method", "dm"),
                }
                outreach_type = "followup" if action["action"] == "send_followup" else "final"
                followup = draft_creator_outreach_email(
                    creator=creator_stub,
                    product_keyword=action["product"],
                    gtm_brief=gtm_brief,
                    outreach_type=outreach_type,
                )
                send_creator_outreach(followup, dry_run=dry_run)
                results["followups_triggered"] += 1
        except Exception as e:
            log.error(f"Follow-up failed for @{action.get('username', '?')}: {e}")

    log.info(f"=== Creator Outreach Complete: {results['outreach_sent']} sent, {results['followups_triggered']} follow-ups ===")
    return results


def _guess_niches_for_product(product_keyword: str) -> list[str]:
    """Guess relevant creator niches based on product keyword."""
    keyword_lower = product_keyword.lower()
    matched = []

    niche_keywords = {
        "health_wellness": ["supplement", "vitamin", "collagen", "protein", "health", "wellness", "magnesium", "ashwagandha"],
        "beauty_skincare": ["serum", "moisturiser", "skincare", "beauty", "whitening", "glow", "retinol", "skin"],
        "fitness": ["workout", "gym", "fitness", "protein", "pre-workout", "posture", "exercise"],
        "food_nutrition": ["food", "nutrition", "keto", "snack", "diet", "matcha", "caffeine"],
        "lifestyle": ["gadget", "tech", "home", "life", "glasses", "light"],
        "pet": ["dog", "cat", "pet", "animal"],
        "home_living": ["home", "organis", "clean", "kitchen", "bamboo", "silicone"],
        "uk_lifestyle": ["uk", "british", "england"],
        "mena_lifestyle": ["dubai", "arabic", "halal", "mena", "gulf"],
        "africa_lifestyle": ["nigeria", "ghana", "africa", "naija"],
    }

    for niche, kws in niche_keywords.items():
        if any(kw in keyword_lower for kw in kws):
            matched.append(niche)

    return matched[:3] if matched else ["lifestyle", "health_wellness"]
