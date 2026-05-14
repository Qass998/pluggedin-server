"""
content_machine.py — PluggedIN Organic Content Machine
Auto-posts creative assets across TikTok, Instagram, Pinterest.
Manages posting calendars by brand/product.
Scans Pinterest for visual style direction (moodboard intelligence — not image theft).
Hand demo video templates via Creatomate.

POSTING STRATEGY:
  TikTok   → Primary. 2-3 posts/day. Short video + text overlay. High organic reach.
  Instagram → Secondary. Reels + Stories + Feed posts. 1-2/day.
  Pinterest → Discovery channel. Product pins drive long-tail traffic. 3-5/day.
  YouTube Shorts → Repurpose best-performing TikTok content. 1/day.

CONTENT TYPES (all original, no copied competitor content):
  1. Hand demo   — real hand holding/using product. Film once, Creatomate overlays text.
  2. Static card — Creatomate template: product + headline + benefit. All formats.
  3. Animated    — Remotion product showcase. No face required.
  4. Text hook   — Bold text-only opener + product reveal. High performing on TikTok.
  5. UGC frame   — Creator's posted content (with permission/Spark Auth) boosted via schedule.

POSTING APIS:
  TikTok   → TikTok for Developers Content Posting API
  Instagram → Meta Graph API (via Business account)
  Pinterest → Pinterest API v5
  Buffer   → Buffer Publish API (fallback scheduler — supports all platforms)
"""

import os
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("content_machine")
logging.basicConfig(level=logging.INFO)

TIKTOK_ACCESS_TOKEN    = os.getenv("TIKTOK_ACCESS_TOKEN", "")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ID  = os.getenv("INSTAGRAM_BUSINESS_ID", "")
PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN", "")
BUFFER_ACCESS_TOKEN    = os.getenv("BUFFER_ACCESS_TOKEN", "")

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
    from lib.airtable_client import upsert_record, get_records
except ImportError:
    try:
        from airtable_client import upsert_record, get_records
    except ImportError:
        def upsert_record(table, fields, match_field=None): pass
        def get_records(table, formula=None): return []

# ---------------------------------------------------------------------------
# Pinterest Visual Intelligence (moodboard, NOT image theft)
# Scans Pinterest to understand WHAT STYLE is working — colours, composition,
# text placement, layout — then we make our OWN creatives inspired by that data.
# We never download or repurpose another person's image.
# ---------------------------------------------------------------------------

def scan_pinterest_visual_trends(
    keyword: str,
    limit: int = 30,
) -> dict:
    """
    Scan Pinterest for visual style intelligence on a product/keyword.
    Extracts: dominant colours, layout patterns, text styles, visual themes.
    Returns: a style brief that guides our Creatomate template design.

    NOTE: We extract METADATA and PATTERNS — not the images themselves.
    We use this to make our own original creatives that follow proven aesthetics.
    """
    if not _apify:
        return {}

    style_data = {
        "keyword": keyword,
        "dominant_themes": [],
        "colour_palettes": [],
        "text_styles": [],
        "layout_patterns": [],
        "top_pin_descriptions": [],
        "scanned_at": datetime.utcnow().isoformat(),
    }

    try:
        run = _apify.actor("apify/pinterest-crawler").call(run_input={
            "startUrls": [{"url": f"https://www.pinterest.com/search/pins/?q={keyword.replace(' ', '+')}&rs=typed"}],
            "maxResults": limit,
        })
        items = list(_apify.dataset(run["defaultDatasetId"]).iterate_items())

        descriptions = []
        for item in items:
            desc = item.get("description", "") or item.get("title", "")
            if desc:
                descriptions.append(desc[:150])

        # AI analysis of the visual patterns described
        if descriptions:
            prompt = f"""
Analyse these Pinterest pin descriptions for "{keyword}" and extract visual style intelligence.
We want to understand what visual STYLE is performing well so we can make our own original creatives.

Descriptions:
{chr(10).join(descriptions[:20])}

Extract:
1. Dominant colour themes (e.g. "clean white backgrounds", "earthy tones", "bold neons")
2. Layout patterns (e.g. "product centred", "before/after split", "ingredient callouts")
3. Text styles (e.g. "minimal text", "bold headline top", "benefit bullets")
4. Visual themes (e.g. "lifestyle context", "clinical/clean", "luxury feel", "natural/organic")
5. Top 3 content angles that appear most (e.g. "transformation", "ingredients", "lifestyle")

Return JSON:
{{
  "dominant_colour_themes": ["...", "...", "..."],
  "layout_patterns": ["...", "...", "..."],
  "text_styles": ["...", "...", "..."],
  "visual_themes": ["...", "...", "..."],
  "top_content_angles": ["...", "...", "..."],
  "creatomate_direction": "One paragraph telling a designer how to set up a Creatomate template for this product based on what's winning on Pinterest"
}}
Return ONLY valid JSON.
"""
            response = call_ai(
                task="market_intel",
                system="You are a visual brand strategist analysing Pinterest trends.",
                prompt=prompt,
                max_tokens=800,
            )
            try:
                raw = response.strip()
                if "```" in raw:
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                parsed = json.loads(raw)
                style_data.update(parsed)
            except Exception:
                style_data["top_pin_descriptions"] = descriptions[:5]

    except Exception as e:
        log.error(f"Pinterest visual scan failed for '{keyword}': {e}")

    return style_data


# ---------------------------------------------------------------------------
# Hand demo video — the highest-converting format
# ---------------------------------------------------------------------------

def generate_hand_demo_brief(
    product: str,
    icp: dict,
    gtm_brief: dict,
) -> dict:
    """
    Generate a hand demo video brief.
    Hand demos are consistently the top-performing organic format on TikTok
    for physical products. No face required — just a hand, the product, and context.

    What to film (can be done with a phone, no studio):
    - Hand picks up product from a flat lay
    - Demonstrates the key use case (30-60 seconds)
    - Text overlay handles all the messaging
    - Creatomate adds headline, benefit callouts, CTA on top of the raw clip
    """
    hook = gtm_brief.get("phase_1_organic", {}).get("video_brief_hook", "")
    pain = icp.get("key_pain_points", [""])[0]
    desire = icp.get("core_desires", [""])[0]

    prompt = f"""
Write a hand demo video brief for "{product}".

Avatar: {icp.get('avatar_name', '')} — {icp.get('buying_motivation', '')}
Pain point: {pain}
Core desire: {desire}
Hook: {hook}

Write a step-by-step filming brief that anyone can follow with just a phone:
1. Setup (what background, what lighting, what props)
2. Shot 1 — opening (3 seconds): what to show
3. Shot 2 — demonstration (15-20 seconds): the key use case
4. Shot 3 — result/reveal (5-10 seconds): before/after or outcome
5. Shot 4 — CTA (3 seconds): product + link/code reminder

Also write the Creatomate text overlay plan:
- Text to show at second 0-3 (hook)
- Text to show during demo
- Text at end (benefit + CTA)

Keep language simple. This brief goes to a creator or to Qassim to film himself.
"""

    brief = call_ai(
        task="outreach",
        system="You write clear, simple video filming briefs for DTC product demos.",
        prompt=prompt,
        max_tokens=600,
    )

    return {
        "product": product,
        "format": "hand_demo",
        "filming_brief": brief,
        "creatomate_template": "video_product_showcase",
        "overlay_plan": {
            "hook_text": hook[:80] if hook else f"You need to try this {product}",
            "demo_text": f"{pain} → solved",
            "cta_text": "Link in bio · Use code for 12% off",
        },
        "setup_notes": {
            "background": "Clean flat surface — marble contact paper, white sheet, or wooden table",
            "lighting": "Ring light or near a window (natural light is best)",
            "props": ["the product", "any accessories that come with it", "relevant lifestyle prop"],
            "phone_angle": "Overhead (bird's eye) or 45° angle — not straight-on",
            "duration": "30-45 seconds raw, Creatomate trims to 15-20s for ads",
        },
        "platforms": ["TikTok", "Instagram Reels", "Pinterest Video"],
        "created_at": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Posting calendar generator
# ---------------------------------------------------------------------------

def build_posting_calendar(
    brand: str,
    product: str,
    creative_assets: dict,
    start_date: datetime = None,
    days: int = 14,
) -> list[dict]:
    """
    Build a 14-day posting calendar for a product launch.
    Distributes creative assets across TikTok, Instagram, Pinterest.
    Ensures the right content type goes to the right platform at the right time.

    Week 1: Organic proof phase (hand demo, static cards, text hooks)
    Week 2: Amplification (best performer gets boosted, creator UGC added)
    """
    start_date = start_date or datetime.utcnow()
    calendar = []

    static_ads = creative_assets.get("static_ads", {})
    video_remotion = creative_assets.get("video_ads", {}).get("remotion_showcase", {})
    video_creatomate = creative_assets.get("video_ads", {}).get("creatomate_product", {})
    voiceover = creative_assets.get("voiceover", {})

    # Content rotation — 14-day plan
    daily_plan = [
        # Day 1
        {"platform": "TikTok",    "type": "hand_demo",      "caption_tone": "hook_question"},
        {"platform": "Instagram", "type": "static_4x5",      "caption_tone": "benefit_led"},
        {"platform": "Pinterest", "type": "static_1x1",      "caption_tone": "descriptive"},
        # Day 2
        {"platform": "TikTok",    "type": "animated_product","caption_tone": "story_led"},
        {"platform": "Instagram", "type": "reels_animated",  "caption_tone": "hook_question"},
        {"platform": "Pinterest", "type": "static_9x16",     "caption_tone": "how_to"},
        # Day 3
        {"platform": "TikTok",    "type": "text_hook",       "caption_tone": "controversial"},
        {"platform": "Instagram", "type": "static_1x1",      "caption_tone": "social_proof"},
        # Day 4
        {"platform": "TikTok",    "type": "hand_demo_v2",    "caption_tone": "problem_agitate"},
        {"platform": "Instagram", "type": "reels_hand_demo", "caption_tone": "benefit_led"},
        {"platform": "Pinterest", "type": "static_4x5",      "caption_tone": "descriptive"},
        # Day 5
        {"platform": "TikTok",    "type": "animated_product","caption_tone": "social_proof"},
        # Day 6
        {"platform": "Pinterest", "type": "static_1x1",      "caption_tone": "how_to"},
        {"platform": "Instagram", "type": "static_9x16",     "caption_tone": "lifestyle"},
        # Day 7 — review day (post best performer again, different caption)
        {"platform": "TikTok",    "type": "best_performer_repost", "caption_tone": "hook_question"},
        {"platform": "Instagram", "type": "static_4x5",      "caption_tone": "story_led"},
        {"platform": "Pinterest", "type": "static_9x16",     "caption_tone": "descriptive"},
        # Day 8-14: creator UGC starts appearing — shift to amplify
        {"platform": "TikTok",    "type": "text_hook",       "caption_tone": "before_after"},
        {"platform": "Instagram", "type": "reels_animated",  "caption_tone": "hook_question"},
        {"platform": "Pinterest", "type": "static_1x1",      "caption_tone": "benefit_led"},
        {"platform": "TikTok",    "type": "hand_demo",       "caption_tone": "story_led"},
        {"platform": "Instagram", "type": "static_4x5",      "caption_tone": "social_proof"},
        {"platform": "TikTok",    "type": "animated_product","caption_tone": "lifestyle"},
        {"platform": "Pinterest", "type": "static_9x16",     "caption_tone": "how_to"},
        {"platform": "TikTok",    "type": "text_hook",       "caption_tone": "controversial"},
        {"platform": "Instagram", "type": "reels_hand_demo", "caption_tone": "benefit_led"},
        {"platform": "Pinterest", "type": "static_4x5",      "caption_tone": "descriptive"},
        {"platform": "TikTok",    "type": "best_performer_repost", "caption_tone": "story_led"},
    ]

    post_date = start_date
    for i, plan in enumerate(daily_plan[:days * 2]):  # ~2 posts/day across platforms
        if i > 0 and i % 3 == 0:
            post_date += timedelta(days=1)

        # Map content type to actual asset URL
        asset_url = _resolve_asset_url(plan["type"], static_ads, video_remotion, video_creatomate)

        calendar.append({
            "brand": brand,
            "product": product,
            "post_date": post_date.strftime("%Y-%m-%d"),
            "post_time": _best_post_time(plan["platform"]),
            "platform": plan["platform"],
            "content_type": plan["type"],
            "asset_url": asset_url,
            "caption_tone": plan["caption_tone"],
            "caption": "",          # Generated in generate_captions()
            "hashtags": [],         # Generated in generate_captions()
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat(),
        })

    return calendar


def _resolve_asset_url(content_type: str, static_ads: dict, video_remotion: dict, video_creatomate: dict) -> str:
    """Map content type string to actual asset URL."""
    type_map = {
        "static_1x1":   static_ads.get("1x1", {}).get("output_url", ""),
        "static_9x16":  static_ads.get("9x16", {}).get("output_url", ""),
        "static_4x5":   static_ads.get("4x5", {}).get("output_url", ""),
        "animated_product": video_remotion.get("output_path", video_creatomate.get("output_url", "")),
        "reels_animated":   video_remotion.get("output_path", ""),
        "reels_hand_demo":  "",   # Filmed manually — URL added when uploaded
        "hand_demo":        "",   # Filmed manually — URL added when uploaded
        "hand_demo_v2":     "",   # Filmed manually — URL added when uploaded
        "text_hook":        video_creatomate.get("output_url", ""),
        "best_performer_repost": "",  # Determined by analytics
    }
    return type_map.get(content_type, "")


def _best_post_time(platform: str) -> str:
    """Return optimal posting time per platform (UK time)."""
    times = {
        "TikTok":    "18:00",   # 6pm UK — peak TikTok scroll time
        "Instagram": "12:00",   # Noon UK — lunch scroll
        "Pinterest": "20:00",   # 8pm UK — evening planning/browsing
        "YouTube":   "15:00",   # 3pm UK
    }
    return times.get(platform, "12:00")


def generate_captions(
    calendar: list[dict],
    product: str,
    icp: dict,
    hashtags_by_niche: list[str] = None,
) -> list[dict]:
    """
    Generate platform-native captions for every post in the calendar.
    Each platform has a different native voice:
    - TikTok: short, punchy, hook first, 3-5 hashtags
    - Instagram: slightly longer, story-led, 15-25 hashtags
    - Pinterest: descriptive, keyword-rich for search, 5-10 hashtags
    """
    hashtags_by_niche = hashtags_by_niche or []
    avatar = icp.get("avatar_name", "")
    pain = icp.get("key_pain_points", [""])[0]
    desire = icp.get("core_desires", [""])[0]

    tone_map = {
        "hook_question":    f"Open with a bold question that makes {avatar} stop scrolling",
        "benefit_led":      f"Lead with the core benefit: solving '{pain}'",
        "story_led":        f"Open with a relatable story about '{pain}' then reveal the solution",
        "controversial":    "Open with a mild hot-take to drive comments",
        "social_proof":     "Lead with a stat or testimonial-style opener",
        "problem_agitate":  f"Name the problem, amplify the frustration, introduce the solution",
        "before_after":     "Before: [problem]. After: [result]",
        "lifestyle":        f"Paint the picture of the life {avatar} wants — then show how this helps",
        "how_to":           "Educational — step by step how to use the product",
        "descriptive":      "Clear, keyword-rich description of the product and its benefits",
    }

    updated = []
    batch_size = 5  # Generate captions in batches to save API calls

    for i in range(0, len(calendar), batch_size):
        batch = calendar[i:i+batch_size]
        posts_to_caption = "\n".join([
            f"Post {j+1}: Platform={p['platform']} | Type={p['content_type']} | Tone={p['caption_tone']}"
            for j, p in enumerate(batch)
        ])

        prompt = f"""
Write captions for these {len(batch)} social media posts about "{product}".

Product: {product}
Avatar: {avatar}
Pain point: {pain}
Core desire: {desire}

Posts:
{posts_to_caption}

For each post, write:
- A platform-native caption (TikTok: 100-150 chars + hook | Instagram: 150-300 chars | Pinterest: 200-400 chars, keyword-rich)
- 3-5 hashtags (TikTok), 15-20 hashtags (Instagram), 5-10 hashtags (Pinterest)

Available hashtags pool: {', '.join(hashtags_by_niche[:20])}

Return as JSON array (one entry per post, in order):
[
  {{
    "post_index": 1,
    "caption": "...",
    "hashtags": ["...", "...", "..."]
  }}
]
Return ONLY valid JSON.
"""

        response = call_ai(
            task="outreach",
            system="You write platform-native social media captions that stop the scroll.",
            prompt=prompt,
            max_tokens=1000,
        )

        try:
            raw = response.strip()
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            captions = json.loads(raw)
            for j, post in enumerate(batch):
                if j < len(captions):
                    post["caption"] = captions[j].get("caption", "")
                    post["hashtags"] = captions[j].get("hashtags", [])
                updated.append(post)
        except Exception:
            updated.extend(batch)

        time.sleep(2)

    return updated


# ---------------------------------------------------------------------------
# Platform posting APIs
# ---------------------------------------------------------------------------

def post_to_tiktok(video_url: str, caption: str, hashtags: list[str] = None) -> dict:
    """
    Post a video to TikTok using TikTok Content Posting API.
    Requires: TikTok Business Account + Content Posting API access.
    Setup: developers.tiktok.com → Create app → Content Posting API
    """
    if not TIKTOK_ACCESS_TOKEN:
        log.warning("TIKTOK_ACCESS_TOKEN not set — logging post for manual upload")
        return {"status": "manual_upload_needed", "video_url": video_url}

    full_caption = caption
    if hashtags:
        full_caption += " " + " ".join([f"#{h.lstrip('#')}" for h in hashtags[:5]])

    try:
        # Step 1: Init upload
        resp = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/video/init/",
            headers={"Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}", "Content-Type": "application/json"},
            json={
                "post_info": {
                    "title": full_caption[:150],
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": video_url,
                },
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        publish_id = data.get("data", {}).get("publish_id", "")
        log.info(f"  TikTok post queued: {publish_id}")
        return {"status": "queued", "publish_id": publish_id, "platform": "TikTok"}
    except Exception as e:
        log.error(f"TikTok post failed: {e}")
        return {"status": "failed", "error": str(e)}


def post_to_instagram(
    image_url: str = "",
    video_url: str = "",
    caption: str = "",
    hashtags: list[str] = None,
    media_type: str = "IMAGE",
) -> dict:
    """
    Post to Instagram via Meta Graph API.
    Requires: Instagram Business Account + Meta Developer App.
    media_type: IMAGE | VIDEO | REELS
    """
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ID:
        log.warning("Instagram credentials not set — logging for manual post")
        return {"status": "manual_upload_needed", "image_url": image_url or video_url}

    full_caption = caption
    if hashtags:
        full_caption += "\n.\n.\n" + " ".join([f"#{h.lstrip('#')}" for h in hashtags[:25]])

    base_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_BUSINESS_ID}"
    headers = {"Authorization": f"Bearer {INSTAGRAM_ACCESS_TOKEN}"}

    try:
        # Step 1: Create media container
        payload = {
            "caption": full_caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        }
        if media_type in ("VIDEO", "REELS"):
            payload["media_type"] = "REELS"
            payload["video_url"] = video_url
        else:
            payload["image_url"] = image_url

        resp = requests.post(f"{base_url}/media", data=payload, timeout=30)
        resp.raise_for_status()
        container_id = resp.json().get("id", "")

        # Step 2: Publish
        time.sleep(3)
        pub_resp = requests.post(
            f"{base_url}/media_publish",
            data={"creation_id": container_id, "access_token": INSTAGRAM_ACCESS_TOKEN},
            timeout=30,
        )
        pub_resp.raise_for_status()
        post_id = pub_resp.json().get("id", "")
        log.info(f"  Instagram post published: {post_id}")
        return {"status": "published", "post_id": post_id, "platform": "Instagram"}
    except Exception as e:
        log.error(f"Instagram post failed: {e}")
        return {"status": "failed", "error": str(e)}


def post_to_pinterest(
    image_url: str,
    title: str,
    description: str,
    link: str = "",
    board_id: str = "",
) -> dict:
    """
    Post a pin to Pinterest via Pinterest API v5.
    Pinterest is a long-tail discovery channel — pins rank in search for months.
    Best for: product discovery, DIY/lifestyle products, home/beauty/health.
    """
    if not PINTEREST_ACCESS_TOKEN:
        log.warning("PINTEREST_ACCESS_TOKEN not set — logging for manual pin")
        return {"status": "manual_upload_needed", "image_url": image_url}

    try:
        resp = requests.post(
            "https://api.pinterest.com/v5/pins",
            headers={
                "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "board_id": board_id or os.getenv("PINTEREST_DEFAULT_BOARD_ID", ""),
                "title": title[:100],
                "description": description[:500],
                "link": link,
                "media_source": {
                    "source_type": "image_url",
                    "url": image_url,
                },
            },
            timeout=30,
        )
        resp.raise_for_status()
        pin_id = resp.json().get("id", "")
        log.info(f"  Pinterest pin created: {pin_id}")
        return {"status": "published", "pin_id": pin_id, "platform": "Pinterest"}
    except Exception as e:
        log.error(f"Pinterest pin failed: {e}")
        return {"status": "failed", "error": str(e)}


def post_via_buffer(
    content_url: str,
    caption: str,
    platform: str,
    scheduled_at: str = None,
    profile_id: str = None,
) -> dict:
    """
    Post via Buffer as fallback scheduler.
    Buffer supports: Instagram, TikTok, Pinterest, LinkedIn, Facebook, Twitter.
    Use when direct API posting isn't set up yet.
    """
    if not BUFFER_ACCESS_TOKEN:
        log.warning("BUFFER_ACCESS_TOKEN not set — manual post needed")
        return {"status": "manual", "platform": platform, "content_url": content_url}

    profile_id = profile_id or os.getenv(f"BUFFER_PROFILE_{platform.upper()}", "")
    if not profile_id:
        log.warning(f"Buffer profile ID for {platform} not set")
        return {"status": "no_profile_id"}

    try:
        payload = {
            "profile_ids": [profile_id],
            "text": caption,
            "media": {"link": content_url},
        }
        if scheduled_at:
            payload["scheduled_at"] = scheduled_at

        resp = requests.post(
            "https://api.bufferapp.com/1/updates/create.json",
            headers={"Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}"},
            data=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        log.info(f"  Buffer post scheduled for {platform}: {data.get('updates', [{}])[0].get('id', '')}")
        return {"status": "scheduled", "platform": platform, "buffer_id": data.get("updates", [{}])[0].get("id", "")}
    except Exception as e:
        log.error(f"Buffer post failed for {platform}: {e}")
        return {"status": "failed", "error": str(e)}


# ---------------------------------------------------------------------------
# Post executor — runs the calendar
# ---------------------------------------------------------------------------

def execute_todays_posts(brand: str, dry_run: bool = False) -> dict:
    """
    Execute all posts scheduled for today from PostingCalendar table.
    Called daily at 09:00 for morning posts, 17:00 for evening posts.
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")
    results = {"posted": 0, "failed": 0, "manual_needed": 0}

    try:
        records = get_records(
            "PostingCalendar",
            formula=f"AND({{Brand}}='{brand}', {{PostDate}}='{today}', {{Status}}='scheduled')"
        )
    except Exception:
        records = []

    for record in records:
        fields = record.get("fields", {})
        platform = fields.get("Platform", "")
        asset_url = fields.get("AssetURL", "")
        caption = fields.get("Caption", "")
        hashtags = fields.get("Hashtags", "").split(",") if fields.get("Hashtags") else []

        if not asset_url:
            log.warning(f"  Skipping post — no asset URL for {platform}")
            results["manual_needed"] += 1
            continue

        if dry_run:
            log.info(f"  [DRY RUN] Would post to {platform}: {asset_url[:60]}")
            results["posted"] += 1
            continue

        result = {}
        try:
            if platform == "TikTok":
                result = post_to_tiktok(video_url=asset_url, caption=caption, hashtags=hashtags)
            elif platform == "Instagram":
                content_type = fields.get("ContentType", "static")
                if "video" in content_type or "reel" in content_type:
                    result = post_to_instagram(video_url=asset_url, caption=caption, hashtags=hashtags, media_type="REELS")
                else:
                    result = post_to_instagram(image_url=asset_url, caption=caption, hashtags=hashtags, media_type="IMAGE")
            elif platform == "Pinterest":
                result = post_to_pinterest(
                    image_url=asset_url,
                    title=caption[:100],
                    description=caption,
                    link=fields.get("ProductURL", ""),
                )
            else:
                result = post_via_buffer(content_url=asset_url, caption=caption, platform=platform)

            if result.get("status") in ("published", "queued", "scheduled"):
                results["posted"] += 1
                _update_post_status(record["id"], "posted", result)
            elif result.get("status") == "manual_upload_needed":
                results["manual_needed"] += 1
                _update_post_status(record["id"], "manual_needed", result)
            else:
                results["failed"] += 1

        except Exception as e:
            log.error(f"Post execution error for {platform}: {e}")
            results["failed"] += 1

    log.info(f"Today's posts: {results['posted']} posted, {results['failed']} failed, {results['manual_needed']} need manual upload")
    return results


def _update_post_status(record_id: str, status: str, result: dict):
    """Update post status in Airtable:PostingCalendar."""
    try:
        upsert_record("PostingCalendar", {
            "Status": status,
            "PostedAt": datetime.utcnow().isoformat(),
            "PostID": result.get("post_id") or result.get("pin_id") or result.get("publish_id") or "",
        }, match_field=None)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Full content machine setup for a new product
# ---------------------------------------------------------------------------

def launch_content_machine(
    brand: str,
    product: str,
    icp: dict,
    gtm_brief: dict,
    creative_assets: dict,
    pinterest_style: dict = None,
    dry_run: bool = False,
) -> dict:
    """
    Full content machine setup for a new product:
    1. Scan Pinterest for visual style direction
    2. Generate hand demo filming brief
    3. Build 14-day posting calendar
    4. Generate captions for all posts
    5. Log calendar to Airtable:PostingCalendar
    6. Log to Airtable:ContentMachines
    """
    log.info(f"=== Launching Content Machine: {brand} / {product} ===")

    # 1. Pinterest visual intelligence
    if not pinterest_style:
        log.info("  → Scanning Pinterest for visual style direction...")
        pinterest_style = scan_pinterest_visual_trends(product, limit=30)

    # 2. Hand demo brief
    log.info("  → Generating hand demo filming brief...")
    hand_demo = generate_hand_demo_brief(product, icp, gtm_brief)

    # 3. Build posting calendar
    log.info("  → Building 14-day posting calendar...")
    calendar = build_posting_calendar(
        brand=brand,
        product=product,
        creative_assets=creative_assets,
        start_date=datetime.utcnow(),
        days=14,
    )

    # 4. Generate captions
    log.info("  → Generating platform-native captions...")
    niche_hashtags = gtm_brief.get("phase_1_organic", {}).get("key_hashtags", [])
    calendar = generate_captions(calendar, product, icp, hashtags_by_niche=niche_hashtags)

    # 5. Log calendar to Airtable
    if not dry_run:
        for post in calendar:
            try:
                upsert_record("PostingCalendar", {
                    "Brand": brand,
                    "Product": product,
                    "PostDate": post["post_date"],
                    "PostTime": post["post_time"],
                    "Platform": post["platform"],
                    "ContentType": post["content_type"],
                    "AssetURL": post["asset_url"],
                    "Caption": post["caption"][:500] if post.get("caption") else "",
                    "Hashtags": ", ".join(post.get("hashtags", [])),
                    "Status": "scheduled",
                    "CreatedAt": post["created_at"],
                }, match_field=None)
            except Exception as e:
                log.error(f"  Calendar log failed: {e}")

    # 6. Log machine to Airtable
    if not dry_run:
        upsert_record("ContentMachines", {
            "Brand": brand,
            "Product": product,
            "Status": "Active",
            "PostsScheduled": len(calendar),
            "PinterestStyleBrief": pinterest_style.get("creatomate_direction", "")[:300],
            "HandDemoBrief": hand_demo["filming_brief"][:300],
            "LaunchedAt": datetime.utcnow().isoformat(),
        }, match_field="Product")

    log.info(f"  ✓ Content machine live: {len(calendar)} posts scheduled over 14 days")
    return {
        "brand": brand,
        "product": product,
        "posts_scheduled": len(calendar),
        "calendar": calendar,
        "hand_demo_brief": hand_demo,
        "pinterest_style": pinterest_style,
    }
