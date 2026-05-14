"""
creative_studio.py — PluggedIN Creative Production Engine
Produces image ads, video ads, and voiceovers for SourcedStore products.

CREATIVE PHILOSOPHY:
  We do NOT generate AI human faces. Everything else is on the table:

  1. Hand + voiceover         — film a hand using the product (phone camera), ElevenLabs VO layered on top.
                                 Consistently one of TikTok's highest-converting formats. No face needed.
  2. Creatomate animated      — product image + motion text callouts + ElevenLabs voiceover.
                                 Runs without filming anything. Deployed in minutes.
  3. Remotion programmatic    — React-rendered animated product showcase. Code-driven, no camera.
  4. UGC from cheap platforms — Billo, Insense, Fiverr, Backstage. Real people, real clips, £15-80/video.
                                 We brief them, they film it, we get the raw file, Creatomate adds overlays.
  5. Spark Ads (TikTok)       — Creator authorises us to boost their already-posted video.
                                 Their face, their voice, our ad budget. Fully legitimate.
  6. Meta Whitelisted Ads     — Creator grants account access. Ad runs from their handle.
  7. Stock footage            — Pexels, Storyblocks — real people in lifestyle scenes, licensed.

UGC SOURCING PLATFORMS (for paid UGC briefs):
  - Billo.app           → £15-40/video. Good for product demos. UK + US creators.
  - Insense.pro         → £50-150/video. Higher quality. Pre-vetted creators.
  - Fiverr              → Search "ugc creator" — £20-80/video. Variable quality, good for volume.
  - Backstage.com       → Real actors/presenters. £50-200/video. Best for polished ads.
  All deliverables: raw .mp4 file → we add Creatomate text overlay + brand elements on top.

WHAT EACH TOOL PRODUCES:
  Creatomate  → Static image ads (1x1, 9x16, 4x5) | Short video ads | UGC frame with overlay
  Remotion    → Animated product showcase | Stats/social proof animations
  ElevenLabs  → Voiceover audio (layered onto hand demo + Creatomate/Remotion videos)
  Hand demo   → Raw clip filmed on phone → Creatomate adds hook text + CTA overlay + voiceover
"""

import os
import json
import time
import logging
import requests
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("creative_studio")
logging.basicConfig(level=logging.INFO)

CREATOMATE_API_KEY  = os.getenv("CREATOMATE_API_KEY", "")
ELEVENLABS_API_KEY  = os.getenv("ELEVENLABS_API_KEY", "")
CREATOMATE_BASE     = "https://api.creatomate.com/v1"
ELEVENLABS_BASE     = "https://api.elevenlabs.io/v1"

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
# Creatomate — template-based image + video rendering
# ---------------------------------------------------------------------------

# Pre-built template IDs (configure in Creatomate dashboard)
# These templates reference product image URLs + text fields only — no human face
CREATOMATE_TEMPLATES = {
    "static_product_1x1":    os.getenv("CREATOMATE_TMPL_STATIC_1X1", ""),
    "static_product_9x16":   os.getenv("CREATOMATE_TMPL_STATIC_9X16", ""),
    "static_product_4x5":    os.getenv("CREATOMATE_TMPL_STATIC_4X5", ""),
    "video_product_reveal":  os.getenv("CREATOMATE_TMPL_VIDEO_REVEAL", ""),
    "video_ugc_frame":       os.getenv("CREATOMATE_TMPL_VIDEO_UGC", ""),   # creator clip + lower third
    "video_testimonial":     os.getenv("CREATOMATE_TMPL_TESTIMONIAL", ""),
    "video_before_after":    os.getenv("CREATOMATE_TMPL_BEFORE_AFTER", ""),
    "video_product_showcase":os.getenv("CREATOMATE_TMPL_SHOWCASE", ""),
}


def render_static_ad_creatomate(
    product: str,
    headline: str,
    subheadline: str,
    cta: str,
    product_image_url: str,
    background_colour: str = "#FFFFFF",
    format: str = "1x1",
    output_format: str = "jpg",
) -> dict:
    """
    Render a static product ad using Creatomate.
    NO human face — product image + text overlays only.

    Returns: render job dict with render_id and output_url when complete.
    """
    if not CREATOMATE_API_KEY:
        log.warning("CREATOMATE_API_KEY not set — returning mock")
        return {
            "status": "mock",
            "product": product,
            "format": format,
            "output_url": f"https://placeholder.com/{product.replace(' ', '-')}-{format}.jpg",
        }

    template_key = f"static_product_{format.replace(':', 'x')}" if ":" in format else f"static_product_{format}"
    template_id = CREATOMATE_TEMPLATES.get(template_key, CREATOMATE_TEMPLATES.get("static_product_1x1", ""))

    if not template_id:
        log.warning(f"No Creatomate template configured for format '{format}' — skipping")
        return {}

    payload = {
        "template_id": template_id,
        "output_format": output_format,
        "modifications": {
            "Headline": headline,
            "Subheadline": subheadline,
            "CTA": cta,
            "ProductImage": product_image_url,
            "BackgroundColour": background_colour,
        },
    }

    try:
        resp = requests.post(
            f"{CREATOMATE_BASE}/renders",
            headers={
                "Authorization": f"Bearer {CREATOMATE_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        render_id = result[0]["id"] if isinstance(result, list) else result.get("id", "")
        log.info(f"  Static ad render queued: {render_id} ({format})")
        return {
            "render_id": render_id,
            "status": "queued",
            "format": format,
            "product": product,
            "template_id": template_id,
            "queued_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error(f"Creatomate static ad render failed: {e}")
        return {}


def render_video_ad_creatomate(
    product: str,
    headline: str,
    hook_line: str,
    benefit_lines: list[str],
    cta: str,
    product_image_url: str,
    voiceover_url: str = "",
    creator_clip_url: str = "",   # optional: creator's TikTok clip (after permission granted)
    template_type: str = "video_product_showcase",
    output_format: str = "mp4",
) -> dict:
    """
    Render a video ad using Creatomate.

    Can be:
    A) Product showcase only (no human) — product images + motion graphics + voiceover
    B) Creator clip framing — creator's actual TikTok video + lower-third text overlay
       (creator_clip_url is their video, provided after they give Spark Ad authorization)

    NOTE: creator_clip_url must be a video the creator has ALREADY posted publicly
    and authorized for Spark Ad / whitelisted use. We do NOT generate human faces.
    """
    if not CREATOMATE_API_KEY:
        log.warning("CREATOMATE_API_KEY not set — returning mock")
        return {
            "status": "mock",
            "product": product,
            "template_type": template_type,
            "output_url": f"https://placeholder.com/{product.replace(' ', '-')}-video.mp4",
        }

    template_id = CREATOMATE_TEMPLATES.get(template_type, "")
    if not template_id:
        log.warning(f"No Creatomate template configured for '{template_type}' — skipping")
        return {}

    modifications = {
        "Headline": headline,
        "HookLine": hook_line,
        "Benefit1": benefit_lines[0] if len(benefit_lines) > 0 else "",
        "Benefit2": benefit_lines[1] if len(benefit_lines) > 1 else "",
        "Benefit3": benefit_lines[2] if len(benefit_lines) > 2 else "",
        "CTA": cta,
        "ProductImage": product_image_url,
    }

    if voiceover_url:
        modifications["Voiceover"] = voiceover_url
    if creator_clip_url:
        modifications["CreatorClip"] = creator_clip_url

    try:
        resp = requests.post(
            f"{CREATOMATE_BASE}/renders",
            headers={
                "Authorization": f"Bearer {CREATOMATE_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"template_id": template_id, "output_format": output_format, "modifications": modifications},
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        render_id = result[0]["id"] if isinstance(result, list) else result.get("id", "")
        log.info(f"  Video ad render queued: {render_id} ({template_type})")
        return {
            "render_id": render_id,
            "status": "queued",
            "template_type": template_type,
            "has_creator_clip": bool(creator_clip_url),
            "has_voiceover": bool(voiceover_url),
            "product": product,
            "queued_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error(f"Creatomate video render failed: {e}")
        return {}


def poll_creatomate_render(render_id: str, max_wait_seconds: int = 120) -> dict:
    """
    Poll Creatomate for render completion.
    Returns the output URL when done.
    """
    if not CREATOMATE_API_KEY or not render_id or render_id == "mock":
        return {"status": "mock", "output_url": ""}

    headers = {"Authorization": f"Bearer {CREATOMATE_API_KEY}"}
    deadline = time.time() + max_wait_seconds

    while time.time() < deadline:
        try:
            resp = requests.get(f"{CREATOMATE_BASE}/renders/{render_id}", headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "")
            if status == "succeeded":
                output_url = data.get("url", "")
                log.info(f"  Render complete: {render_id} → {output_url}")
                return {"status": "succeeded", "output_url": output_url, "render_id": render_id}
            elif status == "failed":
                log.error(f"  Render failed: {render_id} — {data.get('error_message', '')}")
                return {"status": "failed", "render_id": render_id}
            time.sleep(8)
        except Exception as e:
            log.error(f"  Render poll error: {e}")
            time.sleep(10)

    log.warning(f"  Render {render_id} timed out after {max_wait_seconds}s")
    return {"status": "timeout", "render_id": render_id}


# ---------------------------------------------------------------------------
# ElevenLabs — AI Voiceover
# Used for: product explainer narration (voice only, no face)
# Permissible: AI voice is text-to-speech, not image generation
# ---------------------------------------------------------------------------

# Default voices suitable for product ads
ELEVENLABS_VOICES = {
    "male_calm":      os.getenv("ELEVENLABS_VOICE_MALE_CALM", "pNInz6obpgDQGcFmaJgB"),   # Adam
    "female_warm":    os.getenv("ELEVENLABS_VOICE_FEMALE_WARM", "EXAVITQu4vr4xnSDxMaL"), # Bella
    "male_energetic": os.getenv("ELEVENLABS_VOICE_MALE_ENERGY", "VR6AewLTigWG4xSOukaG"), # Arnold
    "female_clear":   os.getenv("ELEVENLABS_VOICE_FEMALE_CLEAR", "ThT5KcBeYPX3keUQqHPh"), # Dorothy
    "arabic_male":    os.getenv("ELEVENLABS_VOICE_ARABIC_MALE", ""),    # configure for MENA campaigns
}


def generate_voiceover(
    script: str,
    voice: str = "female_warm",
    stability: float = 0.5,
    clarity: float = 0.75,
    style: float = 0.0,
) -> dict:
    """
    Generate AI voiceover for a product ad script.
    Returns: mp3 binary + playback URL (if uploaded to S3/Cloudflare).

    This is text-to-speech only — no human image or face generated.
    Used to narrate: product showcases, animated Remotion videos, Creatomate templates.
    """
    if not ELEVENLABS_API_KEY:
        log.warning("ELEVENLABS_API_KEY not set — voiceover skipped")
        return {"status": "skipped", "url": ""}

    voice_id = ELEVENLABS_VOICES.get(voice, ELEVENLABS_VOICES["female_warm"])
    if not voice_id:
        log.warning(f"Voice '{voice}' not configured — using default")
        voice_id = "EXAVITQu4vr4xnSDxMaL"

    try:
        resp = requests.post(
            f"{ELEVENLABS_BASE}/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": script,
                "model_id": "eleven_turbo_v2",
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": clarity,
                    "style": style,
                    "use_speaker_boost": True,
                },
            },
            timeout=30,
        )
        resp.raise_for_status()
        audio_bytes = resp.content
        log.info(f"  Voiceover generated: {len(audio_bytes):,} bytes")

        # Save locally for now — in production, upload to S3/Cloudflare R2
        filename = f"voiceover_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
        output_path = os.path.expanduser(f"~/pluggedin-creative/{filename}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        return {
            "status": "generated",
            "voice": voice,
            "local_path": output_path,
            "script": script[:100],
            "bytes": len(audio_bytes),
            "generated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        log.error(f"ElevenLabs voiceover failed: {e}")
        return {"status": "failed", "error": str(e)}


def generate_voiceover_script(
    product: str,
    icp: dict,
    angle: dict,
    duration_seconds: int = 30,
) -> str:
    """
    AI-generate a voiceover script for a product ad.
    Calibrated for 30-second or 15-second product explainers.
    """
    word_count = duration_seconds * 2.5  # ~150wpm average speaking pace

    prompt = f"""
Write a {duration_seconds}-second voiceover script for a product ad.

Product: {product}
Target avatar: {icp.get('avatar_name', 'someone who needs this')} — {icp.get('buying_motivation', '')}
Key pain point: {icp.get('key_pain_points', [''])[0]}
Core desire: {icp.get('core_desires', [''])[0]}
Marketing angle: {angle.get('angle', '')}
Hook: {angle.get('hook', '')}

Rules:
- Approximately {int(word_count)} words (read at natural pace = {duration_seconds} seconds)
- Start with the hook — grab attention immediately
- Middle: address pain point → introduce product → key benefit
- End: clear CTA (e.g. "Link in bio", "Shop now at [store]", "Tap to order")
- Conversational, not corporate
- No superlatives ("amazing", "incredible", "revolutionary") — keep it real
- No health claims that require clinical evidence

Output the script ONLY — no stage directions, no [brackets], just the spoken words.
"""

    return call_ai(
        task="outreach",
        system="You write authentic, conversational voiceover scripts for DTC product ads.",
        prompt=prompt,
        max_tokens=300,
    ).strip()


# ---------------------------------------------------------------------------
# Remotion — Programmatic animated videos
# Server-side React rendering — no browser needed
# ---------------------------------------------------------------------------

def build_remotion_showcase_config(
    product: str,
    headline: str,
    features: list[str],
    product_image_url: str,
    brand_colour: str = "#000000",
    accent_colour: str = "#FFFFFF",
    cta: str = "Shop Now",
    duration_frames: int = 150,  # 5 seconds at 30fps
) -> dict:
    """
    Build the JSON config for a Remotion product showcase composition.
    This is passed to the Remotion render server to produce an MP4.

    The Remotion template handles:
    - Animated headline entrance
    - Product image zoom/pan
    - Feature bullet callouts (text-only, no face)
    - CTA overlay
    - Brand colour theming

    No human face involved — pure product + motion graphics.
    """
    return {
        "composition": "ProductShowcase",
        "durationInFrames": duration_frames,
        "fps": 30,
        "width": 1080,
        "height": 1920,   # 9:16 for TikTok/Reels
        "props": {
            "product": product,
            "headline": headline,
            "features": features[:3],
            "productImageUrl": product_image_url,
            "brandColour": brand_colour,
            "accentColour": accent_colour,
            "cta": cta,
        },
    }


def render_remotion_video(config: dict, output_path: str = None) -> dict:
    """
    Trigger a Remotion render via the Remotion Lambda render endpoint
    OR via local CLI (`npx remotion render`).

    In production: Remotion Lambda is recommended for serverless rendering.
    Setup: `npx remotion lambda sites create` and `npx remotion lambda functions deploy`

    For local dev/testing: uses npx remotion render if available.
    """
    import subprocess

    output_path = output_path or os.path.expanduser(
        f"~/pluggedin-creative/remotion_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp4"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write config to temp file
    config_path = output_path.replace(".mp4", "-config.json")
    with open(config_path, "w") as f:
        json.dump(config, f)

    # Try Remotion CLI render
    # Assumes Remotion project is at ~/pluggedin-remotion/
    remotion_dir = os.path.expanduser("~/pluggedin-remotion")

    if not os.path.exists(remotion_dir):
        log.warning(f"Remotion project not found at {remotion_dir} — returning config only")
        return {
            "status": "config_only",
            "config": config,
            "config_path": config_path,
            "note": "Remotion project not set up yet. Run setup first.",
        }

    try:
        result = subprocess.run(
            [
                "npx", "remotion", "render",
                config["composition"],
                output_path,
                "--props", config_path,
                "--frames", f"0-{config['durationInFrames']-1}",
            ],
            cwd=remotion_dir,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            log.info(f"  Remotion render complete: {output_path}")
            return {
                "status": "succeeded",
                "output_path": output_path,
                "product": config["props"]["product"],
                "duration_seconds": config["durationInFrames"] / config["fps"],
            }
        else:
            log.error(f"  Remotion render failed: {result.stderr[:500]}")
            return {"status": "failed", "error": result.stderr[:200]}

    except subprocess.TimeoutExpired:
        log.error("  Remotion render timed out")
        return {"status": "timeout"}
    except FileNotFoundError:
        log.warning("  npx/remotion not found — install with: npm install -g @remotion/cli")
        return {"status": "not_installed", "config": config}
    except Exception as e:
        log.error(f"  Remotion render error: {e}")
        return {"status": "failed", "error": str(e)}


def setup_remotion_project():
    """
    One-time setup: scaffold the Remotion project for PluggedIN creative.
    Creates ~/pluggedin-remotion/ with the ProductShowcase composition.
    """
    import subprocess

    remotion_dir = os.path.expanduser("~/pluggedin-remotion")
    if os.path.exists(remotion_dir):
        log.info("Remotion project already exists.")
        return

    log.info("Setting up Remotion project...")
    try:
        subprocess.run(
            ["npm", "create", "video@latest", "pluggedin-remotion", "--", "--template", "hello-world"],
            cwd=os.path.expanduser("~"),
            check=True,
            timeout=120,
        )
        log.info(f"  Remotion project created at {remotion_dir}")
        log.info("  Next: add ProductShowcase composition to src/compositions/")
    except Exception as e:
        log.error(f"  Remotion setup failed: {e}")


# ---------------------------------------------------------------------------
# Spark Ads + Whitelisted Ads strategy
# ---------------------------------------------------------------------------

def generate_spark_ad_authorization_request(
    creator_username: str,
    post_url: str,
    product: str,
    budget_per_day_gbp: int = 20,
) -> dict:
    """
    Generate the Spark Ad authorization request to send to a creator.
    Once they authorize via TikTok's Spark Ad flow, we can boost their post
    as a paid ad — using their face, their voice, their content.
    This is fully legitimate: TikTok built this system for exactly this purpose.

    Creator sees: "Brand X wants to promote your video"
    Creator clicks: Authorize / Decline
    We get: their video runs as a sponsored post under their handle

    No AI-generated faces. No synthetic content. Real creator, real video, real audience.
    """
    prompt = f"""
Write a short, casual message to a TikTok creator asking them to authorize a Spark Ad.

Creator: @{creator_username}
Their post: {post_url}
Product: {product}
Our daily budget: £{budget_per_day_gbp}/day

Context:
- We loved their post about our product
- We want to boost it as a paid ad (Spark Ad) to reach more people
- They KEEP their original post and all its organic views
- They get paid for the authorization (we'll offer £50-150 one-time fee OR extra commission)
- It takes 30 seconds for them to approve via TikTok's own system

Write the DM message. Keep it short (4-5 sentences). Casual tone.
Mention: what we want to do, what they get, how easy it is.
"""

    message = call_ai(
        task="outreach",
        system="You write casual, genuine creator messages that get responses.",
        prompt=prompt,
        max_tokens=200,
    ).strip()

    return {
        "creator": creator_username,
        "post_url": post_url,
        "product": product,
        "authorization_type": "tiktok_spark_ad",
        "proposed_fee": "£50-150 one-time OR bonus commission",
        "budget_per_day": f"£{budget_per_day_gbp}",
        "message": message,
        "tiktok_spark_guide": "https://ads.tiktok.com/help/article/spark-ads-video-authorization",
        "generated_at": datetime.utcnow().isoformat(),
    }


def generate_meta_whitelist_request(
    creator_instagram: str,
    product: str,
) -> dict:
    """
    Generate a Meta (Instagram/Facebook) whitelisted ad partnership request.
    Creator grants us permission to run ads FROM their Instagram account.
    Their face + handle appear in the ad, but we control targeting + budget.
    Completely legitimate — Meta's branded content tool was built for this.

    Creator: goes to Instagram → Settings → Creator → Branded content → Add partner
    We get: run ads from their handle with full targeting control

    This is the primary strategy for Meta ads WITH a human face.
    """
    prompt = f"""
Write a short DM to an Instagram creator asking them to whitelist us as an ad partner.

Creator: @{creator_instagram}
Product: {product}

Context:
- We want to run paid ads using their content (posts they've already made or will make)
- They add us as an "ad partner" in their Instagram settings (takes 2 minutes)
- Their name/handle appears in the ad = more trust, more engagement
- They get paid per post we promote (£100-300/post depending on performance)
- They keep full creative control — we only promote content they approve

Write the DM. Short (4-5 sentences). Conversational. Not corporate.
"""

    message = call_ai(
        task="outreach",
        system="You write casual, genuine creator messages that get responses.",
        prompt=prompt,
        max_tokens=200,
    ).strip()

    return {
        "creator": creator_instagram,
        "product": product,
        "authorization_type": "meta_whitelisted_ads",
        "proposed_fee": "£100-300 per promoted post",
        "message": message,
        "meta_guide": "https://www.facebook.com/business/help/774028066855790",
        "generated_at": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Paid UGC platform briefs
# Real people, real clips, £15-80/video. We brief → they film → we add overlays.
# ---------------------------------------------------------------------------

UGC_PLATFORMS = {
    "billo": {
        "url": "https://billo.app",
        "price_range": "£15-40/video",
        "turnaround": "3-7 days",
        "best_for": "Product demos, unboxing, honest reviews. UK + US creators.",
        "notes": "Good for high volume. Quality is consistent. Brief must be very clear.",
    },
    "insense": {
        "url": "https://insense.pro",
        "price_range": "£50-150/video",
        "turnaround": "5-10 days",
        "best_for": "Higher quality UGC. Pre-vetted creators by niche. Better for beauty/health.",
        "notes": "More expensive but better matching. Good for hero ad testing.",
    },
    "fiverr": {
        "url": "https://fiverr.com/search/gigs?query=ugc+creator",
        "price_range": "£20-80/video",
        "turnaround": "2-5 days",
        "best_for": "Volume testing. Variable quality — order from multiple sellers, keep best.",
        "notes": "Search: 'ugc creator product video'. Filter by reviews + delivery time.",
    },
    "backstage": {
        "url": "https://backstage.com",
        "price_range": "£80-200/video",
        "turnaround": "7-14 days",
        "best_for": "Polished, scripted ads. Real actors/presenters. Better for premium products.",
        "notes": "Post a casting call with brief. Best for products needing articulate spokesperson.",
    },
}


def generate_paid_ugc_briefs(
    product: str,
    icp: dict,
    gtm_brief: dict,
    recommended_angle: dict,
) -> dict:
    """
    Generate UGC creator briefs for paid UGC platforms (Billo, Insense, Fiverr, Backstage).
    These are sent to the platform — a real person films the video, we get the raw .mp4.
    We then add Creatomate text overlays + brand elements on top.

    The brief is the key. A great brief = great content.
    A vague brief = unusable footage.

    WHAT MAKES A GREAT UGC BRIEF:
    - Hook: tell them the FIRST 3 SECONDS exactly (this is where most UGC fails)
    - Keep to real experience: "speak as if recommending to a friend"
    - No scripts to read verbatim — just key points to hit naturally
    - Mention what NOT to say (competitor names, unverified claims)
    - Show 3 examples of videos you love (reference videos from TikTok)
    """
    organic = gtm_brief.get("phase_1_organic", {})
    pain    = icp.get("key_pain_points", [""])[0]
    desire  = icp.get("core_desires", [""])[0]
    hook    = organic.get("video_brief_hook", recommended_angle.get("hook", ""))
    avatar  = icp.get("avatar_name", "someone who needs this")

    prompt = f"""
Write a paid UGC creator brief for "{product}".

This brief is sent to a real person on Billo/Insense/Fiverr.
They will film a 30-60 second honest product video and send us the raw .mp4.

AVATAR: {avatar}
PAIN POINT: {pain}
DESIRE: {desire}
ANGLE: {recommended_angle.get('angle', '')}
FIRST 3 SECONDS HOOK: {hook}

Write the brief with these exact sections:

1. WHAT WE NEED (1 paragraph — what we're making and why)
2. WHO YOU ARE IN THIS VIDEO (the persona: e.g. "a busy mum who tried this and loves it")
3. THE HOOK — FIRST 3 SECONDS (exactly what to say/show first)
4. KEY POINTS TO HIT (3-5 bullet points — natural, not scripted)
5. WHAT NOT TO SAY (competitor names, medical claims, etc.)
6. FORMAT (duration, orientation, lighting notes)
7. EXAMPLE VIDEOS WE LOVE (describe 2-3 TikTok style reference videos)

Keep it conversational. The creator is not a professional actor.
The goal is authentic, not polished.
"""

    brief_text = call_ai(
        task="outreach",
        system="You write clear, practical UGC creator briefs that result in authentic, converting product videos.",
        prompt=prompt,
        max_tokens=800,
    ).strip()

    # Creatomate overlay spec for what we add ON TOP of the raw clip
    overlay_spec = {
        "template": "video_ugc_frame",
        "overlays": {
            "hook_text": hook[:80] if hook else f"My honest review of {product}",
            "lower_third": f"@creatorhandle · Use code for 12% off",
            "cta_end": "Tap to shop · Link in bio",
            "brand_logo": "bottom-right corner, 15% opacity",
        },
        "note": "Raw clip from creator → uploaded to Creatomate as CreatorClip source → template adds overlays",
    }

    return {
        "product": product,
        "creator_brief": brief_text,
        "overlay_spec": overlay_spec,
        "platforms": UGC_PLATFORMS,
        "recommended_order": ["billo", "fiverr"],  # Start here for first tests
        "budget_estimate": {
            "5_videos_test": "£100-200 (Fiverr/Billo mix)",
            "10_videos_scale": "£300-500 (Insense + Fiverr)",
            "hero_ad": "£150-200 (Backstage — one polished piece)",
        },
        "process": [
            "1. Post brief on Billo/Fiverr — request 3-5 videos",
            "2. Receive raw .mp4 files (no editing needed from their side)",
            "3. Upload raw clip to Creatomate → apply overlay template",
            "4. Download finished video → post organically first",
            "5. Track views for 7 days → best performer gets Spark Ad / paid boost",
        ],
        "generated_at": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Full creative production pipeline
# ---------------------------------------------------------------------------

def produce_ad_creative_set(
    product: str,
    icp: dict,
    gtm_brief: dict,
    competitor_analysis: dict,
    product_image_url: str,
    dry_run: bool = False,
) -> dict:
    """
    Full creative production run for one product:
    1. Generate voiceover script
    2. Generate AI voiceover (ElevenLabs) — voice only
    3. Render static image ads (Creatomate) — all 3 formats
    4. Render product showcase video (Remotion) — motion graphics only
    5. Prepare Spark Ad authorization requests for any creators who've posted
    6. Log all outputs to Airtable:CreativeAssets

    Returns: dict of all creative assets produced
    """
    log.info(f"=== Producing creative set for: {product} ===")

    phase1_organic = gtm_brief.get("phase_1_organic", {})
    phase1_static  = gtm_brief.get("phase_1_static_ads", {})
    recommended    = competitor_analysis.get("recommended_angle", {})

    headline    = phase1_static.get("headline", f"The {product} that actually works")
    subheadline = phase1_static.get("subheadline", icp.get("buying_motivation", ""))
    cta         = phase1_static.get("cta_button", "Shop Now")
    hook        = phase1_organic.get("video_brief_hook", recommended.get("hook", ""))
    features    = [
        icp.get("key_pain_points", [""])[0],
        icp.get("core_desires", [""])[0],
        recommended.get("differentiator", ""),
    ]

    assets = {
        "product": product,
        "static_ads": {},
        "video_ads": {},
        "voiceover": {},
        "spark_ad_requests": [],
        "produced_at": datetime.utcnow().isoformat(),
    }

    if dry_run:
        log.info("[DRY RUN] Skipping live renders — returning mock")
        assets["status"] = "dry_run"
        return assets

    # 1. Generate voiceover script + audio
    log.info("  → Generating voiceover script...")
    vo_script = generate_voiceover_script(
        product=product, icp=icp, angle=recommended, duration_seconds=30
    )
    log.info("  → Generating AI voiceover (ElevenLabs)...")
    voiceover = generate_voiceover(script=vo_script, voice="female_warm")
    assets["voiceover"] = {**voiceover, "script": vo_script}
    voiceover_url = voiceover.get("local_path", "")

    # 2. Render static image ads (Creatomate)
    log.info("  → Rendering static ads (Creatomate)...")
    for fmt in ["1x1", "9x16", "4x5"]:
        render_job = render_static_ad_creatomate(
            product=product,
            headline=headline,
            subheadline=subheadline,
            cta=cta,
            product_image_url=product_image_url,
            format=fmt,
        )
        if render_job.get("render_id"):
            time.sleep(2)
            result = poll_creatomate_render(render_job["render_id"], max_wait_seconds=90)
            assets["static_ads"][fmt] = {**render_job, **result}
        else:
            assets["static_ads"][fmt] = render_job

    # 3. Render product showcase video (Remotion — no human face)
    log.info("  → Building Remotion product showcase...")
    remotion_config = build_remotion_showcase_config(
        product=product,
        headline=headline,
        features=[f for f in features if f],
        product_image_url=product_image_url,
        cta=cta,
        duration_frames=150,  # 5 seconds at 30fps
    )
    remotion_result = render_remotion_video(remotion_config)
    assets["video_ads"]["remotion_showcase"] = remotion_result

    # 4. Creatomate video ad (product images + voiceover, no face)
    log.info("  → Rendering Creatomate product video...")
    video_job = render_video_ad_creatomate(
        product=product,
        headline=headline,
        hook_line=hook[:80] if hook else headline,
        benefit_lines=features,
        cta=cta,
        product_image_url=product_image_url,
        voiceover_url=voiceover_url,
        template_type="video_product_showcase",
    )
    if video_job.get("render_id"):
        time.sleep(3)
        video_result = poll_creatomate_render(video_job["render_id"], max_wait_seconds=180)
        assets["video_ads"]["creatomate_product"] = {**video_job, **video_result}
    else:
        assets["video_ads"]["creatomate_product"] = video_job

    # 5. Generate UGC briefs for paid UGC platforms
    log.info("  → Generating paid UGC platform briefs...")
    ugc_briefs = generate_paid_ugc_briefs(
        product=product, icp=icp, gtm_brief=gtm_brief, recommended_angle=recommended
    )
    assets["ugc_briefs"] = ugc_briefs

    # 6. Generate hand demo filming brief
    log.info("  → Generating hand demo brief...")
    try:
        from lib.content_machine import generate_hand_demo_brief
        assets["hand_demo_brief"] = generate_hand_demo_brief(product, icp, gtm_brief)
    except Exception:
        assets["hand_demo_brief"] = {}

    # 7. Save everything to Google Drive
    log.info("  → Saving to Google Drive...")
    brand = gtm_brief.get("brand", "SourcedStore")
    try:
        from lib.google_drive_assets import save_creative_set_to_drive
        drive_result = save_creative_set_to_drive(
            brand=brand,
            product=product,
            creative_assets=assets,
            gtm_brief=gtm_brief,
            hand_demo_brief=assets.get("hand_demo_brief", {}),
        )
        assets["drive_links"] = drive_result.get("saved", {})
        assets["drive_folder"] = f"https://drive.google.com/drive/folders/{drive_result.get('folders', {}).get('product', '')}"
        log.info(f"  ✓ Saved to Drive: {assets.get('drive_folder', 'N/A')}")
    except Exception as e:
        log.error(f"  Drive save failed: {e}")

    # 8. Log to Airtable
    _log_creative_assets_to_airtable(assets)

    log.info(f"  ✓ Creative set complete for: {product}")
    return assets


def process_creator_posts_for_spark_ads(product: str) -> list[dict]:
    """
    Check CreatorPipeline for creators who have posted about this product.
    For each who posted: generate a Spark Ad authorization request.
    These are real humans, real posts — we just want to boost with paid budget.
    """
    try:
        from lib.airtable_client import get_records
    except ImportError:
        try:
            from airtable_client import get_records
        except ImportError:
            return []

    spark_requests = []
    try:
        records = get_records(
            "CreatorPipeline",
            formula=f"AND({{Product}}='{product}', {{OutreachStatus}}='Posted')"
        )
        for record in records:
            fields = record.get("fields", {})
            post_url = fields.get("PostURL", "")
            username = fields.get("Username", "")
            platform = fields.get("Platform", "TikTok")

            if not post_url or not username:
                continue

            if platform.lower() == "tiktok":
                req = generate_spark_ad_authorization_request(
                    creator_username=username,
                    post_url=post_url,
                    product=product,
                )
            else:
                req = generate_meta_whitelist_request(
                    creator_instagram=username,
                    product=product,
                )

            spark_requests.append(req)
    except Exception as e:
        log.error(f"Spark Ad request generation failed: {e}")

    return spark_requests


def _log_creative_assets_to_airtable(assets: dict):
    """Log creative asset URLs to Airtable:CreativeAssets."""
    try:
        static_urls = " | ".join([
            f"{fmt}: {data.get('output_url', 'pending')}"
            for fmt, data in assets.get("static_ads", {}).items()
        ])
        video_url = (
            assets.get("video_ads", {}).get("creatomate_product", {}).get("output_url", "") or
            assets.get("video_ads", {}).get("remotion_showcase", {}).get("output_path", "")
        )

        upsert_record("CreativeAssets", {
            "Product": assets["product"],
            "StaticAdURLs": static_urls[:500],
            "VideoAdURL": video_url[:200],
            "VoiceoverPath": assets.get("voiceover", {}).get("local_path", ""),
            "VoiceoverScript": assets.get("voiceover", {}).get("script", "")[:300],
            "SparkAdRequests": len(assets.get("spark_ad_requests", [])),
            "Status": "Produced",
            "ProducedAt": assets["produced_at"],
        }, match_field="Product")
    except Exception as e:
        log.error(f"Creative assets Airtable log failed: {e}")
