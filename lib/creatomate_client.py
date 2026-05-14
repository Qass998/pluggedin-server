"""
PluggedIN Python Wrappers
lib/creatomate_client.py

Creatomate wrapper for AI-powered ad and video generation.
Handles: video ads, image ads, voiceover, stock footage,
         platform formatting, branding templates.
Agent calls these methods directly.
Never writes raw Creatomate API calls.
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
CREATOMATE_API_KEY = os.getenv("CREATOMATE_API_KEY")
BASE_URL = "https://api.creatomate.com/v1"

HEADERS = {
    "Authorization": f"Bearer {CREATOMATE_API_KEY}",
    "Content-Type": "application/json"
}

# Platform format presets
PLATFORM_FORMATS = {
    "linkedin": {"width": 1200, "height": 628, "aspect": "16:9"},
    "instagram": {"width": 1080, "height": 1080, "aspect": "1:1"},
    "tiktok": {"width": 1080, "height": 1920, "aspect": "9:16"},
    "facebook": {"width": 1200, "height": 628, "aspect": "16:9"},
    "youtube": {"width": 1920, "height": 1080, "aspect": "16:9"},
    "stories": {"width": 1080, "height": 1920, "aspect": "9:16"}
}


def render_video_ad(template_id: str, modifications: dict,
                    platform: str = "linkedin",
                    webhook_url: str = None) -> dict:
    """
    Render a video ad from a Creatomate template.
    Returns render job with URL when complete.

    Example:
    result = render_video_ad(
        template_id="your-template-id",
        modifications={
            "headline": "Stop chasing cases. AI finds them for you.",
            "subheadline": "Gromatic automates your entire pipeline.",
            "cta": "Book a Demo",
            "logo_url": "https://gromatic.com/logo.png"
        },
        platform="linkedin"
    )
    """
    fmt = PLATFORM_FORMATS.get(platform, PLATFORM_FORMATS["linkedin"])

    payload = {
        "template_id": template_id,
        "modifications": modifications,
        "max_width": fmt["width"],
        "max_height": fmt["height"]
    }

    if webhook_url:
        payload["webhook_url"] = webhook_url

    response = requests.post(
        f"{BASE_URL}/renders",
        headers=HEADERS,
        json=payload
    )

    renders = response.json()
    if isinstance(renders, list) and renders:
        render_id = renders[0].get("id")
        return _poll_render(render_id)

    return response.json()


def render_image_ad(template_id: str, modifications: dict,
                    platform: str = "linkedin") -> dict:
    """
    Render a static image ad from a Creatomate template.
    Returns render job with image URL when complete.

    Example:
    result = render_image_ad(
        template_id="your-image-template-id",
        modifications={
            "headline": "Your AI team starts Monday.",
            "background_color": "#0A0A0A",
            "accent_color": "#6366F1"
        },
        platform="instagram"
    )
    """
    fmt = PLATFORM_FORMATS.get(platform, PLATFORM_FORMATS["linkedin"])

    payload = {
        "template_id": template_id,
        "modifications": modifications,
        "max_width": fmt["width"],
        "max_height": fmt["height"],
        "output_format": "jpg"
    }

    response = requests.post(
        f"{BASE_URL}/renders",
        headers=HEADERS,
        json=payload
    )

    renders = response.json()
    if isinstance(renders, list) and renders:
        render_id = renders[0].get("id")
        return _poll_render(render_id)

    return response.json()


def generate_ad_set(client_name: str, hook: str, service: str,
                    cta: str, logo_url: str = None,
                    platforms: list = None,
                    video_template_id: str = None,
                    image_template_id: str = None) -> list:
    """
    Generate a full ad set across multiple platforms.
    Returns list of renders with URLs for each platform.

    Example:
    ads = generate_ad_set(
        client_name="Gromatic",
        hook="Stop chasing cases. Let AI find them.",
        service="AI-powered housing disrepair pipeline",
        cta="Book a free demo",
        logo_url="https://gromatic.com/logo.png",
        platforms=["linkedin", "instagram", "tiktok"]
    )
    """
    platforms = platforms or ["linkedin", "instagram"]
    results = []

    modifications = {
        "client_name": client_name,
        "headline": hook,
        "service": service,
        "cta": cta
    }
    if logo_url:
        modifications["logo_url"] = logo_url

    for platform in platforms:
        if video_template_id:
            result = render_video_ad(
                video_template_id, modifications, platform
            )
            result["platform"] = platform
            result["type"] = "video"
            results.append(result)

        if image_template_id:
            result = render_image_ad(
                image_template_id, modifications, platform
            )
            result["platform"] = platform
            result["type"] = "image"
            results.append(result)

    return results


def list_templates() -> list:
    """
    List all templates in your Creatomate project.
    Returns template names and IDs.

    Example:
    templates = list_templates()
    # Use template IDs in render calls above
    """
    response = requests.get(
        f"{BASE_URL}/templates",
        headers=HEADERS
    )

    templates = response.json()
    return [
        {
            "id": t.get("id"),
            "name": t.get("name"),
            "type": t.get("output_format"),
            "width": t.get("width"),
            "height": t.get("height")
        }
        for t in templates
    ]


def get_render_status(render_id: str) -> dict:
    """
    Check the status of an in-progress render.
    Status: planned → rendering → succeeded / failed

    Example:
    status = get_render_status("render-id-here")
    """
    response = requests.get(
        f"{BASE_URL}/renders/{render_id}",
        headers=HEADERS
    )
    return response.json()


def _poll_render(render_id: str, max_wait: int = 120) -> dict:
    """
    Poll a render job until complete.
    Returns the finished render with URL.
    """
    elapsed = 0
    while elapsed < max_wait:
        time.sleep(5)
        elapsed += 5

        response = requests.get(
            f"{BASE_URL}/renders/{render_id}",
            headers=HEADERS
        )
        data = response.json()
        status = data.get("status")

        if status == "succeeded":
            return {
                "status": "succeeded",
                "url": data.get("url"),
                "render_id": render_id
            }

        if status == "failed":
            return {
                "status": "failed",
                "error": data.get("error_message", "Unknown error"),
                "render_id": render_id
            }

    return {"status": "timeout", "render_id": render_id}
