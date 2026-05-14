"""
lib/website_scanner.py — Business Intelligence Scanner

The "wow" engine. Given a prospect's website URL:
  1. Fetches and reads the website content
  2. Extracts business profile (industry, services, size signals, pain points)
  3. Recommends the specific PluggedIN modules they need and WHY
  4. Generates personalised example outputs for each agent
  5. Estimates ROI (leads recovered, hours saved, revenue protected)
  6. Auto-configures the WhatsApp agent from what it found

Called by:
  - POST /scan/business → dashboard Business Scan view
  - demo_flow.launch_demo() when a URL is provided
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ─────────────────────────────────────────────
# MODULE CATALOGUE
# Maps module numbers to names and what they do
# ─────────────────────────────────────────────

MODULES = {
    1:  {"name": "Presence Agent",       "icon": "📞", "channel": "Voice + WhatsApp",  "tagline": "24/7 AI receptionist — never miss a lead"},
    2:  {"name": "Lead Generation",      "icon": "🎯", "channel": "Outbound",           "tagline": "Finds and contacts qualified prospects automatically"},
    3:  {"name": "WhatsApp Assistant",   "icon": "💬", "channel": "WhatsApp",           "tagline": "Two-way customer conversations, lead qualification, bookings"},
    4:  {"name": "Content Machine",      "icon": "✍️",  "channel": "Content",            "tagline": "LinkedIn posts, emails, case studies — published automatically"},
    5:  {"name": "Competitor Intel",     "icon": "🔍", "channel": "Research",           "tagline": "Monitors competitors weekly — pricing, launches, reviews"},
    6:  {"name": "Market Scout",         "icon": "🌍", "channel": "Trade Intel",        "tagline": "Surfaces trade signals and buyer intent in real time"},
    7:  {"name": "Reviews Agent",        "icon": "⭐", "channel": "Reputation",         "tagline": "Monitors and responds to Google reviews automatically"},
    8:  {"name": "Job Hunter",           "icon": "💼", "channel": "Recruitment",        "tagline": "Finds and applies to relevant opportunities daily"},
    9:  {"name": "Retention Agent",      "icon": "🔄", "channel": "WhatsApp + CRM",    "tagline": "Loyalty stamps, churn detection, win-back campaigns"},
    10: {"name": "CEO Briefing",         "icon": "🌅", "channel": "Voice + WhatsApp",  "tagline": "Daily briefing call — what happened, what needs you"},
    11: {"name": "TradeBridge",          "icon": "🤝", "channel": "B2B Brokerage",     "tagline": "Connects African suppliers to global buyers — 2-3% commission"},
    12: {"name": "Creative Studio",      "icon": "🎨", "channel": "Design + Video",    "tagline": "Ad creatives, video scripts, brand assets on demand"},
    13: {"name": "Website Builder",      "icon": "🌐", "channel": "Web + Netlify",     "tagline": "Animated website live on Netlify in minutes — copy, design, deploy"},
}

# Pain signals that map to modules
PAIN_SIGNAL_MAP = {
    "no website":            [13],
    "website outdated":      [13],
    "no online presence":    [13, 4],
    "missed calls":          [1, 3, 10],
    "no reviews":            [7],
    "bad reviews":           [7],
    "competitor":            [5],
    "leads":                 [1, 2, 3],
    "content":               [4],
    "social media":          [4],
    "loyalty":               [9],
    "retention":             [9],
    "whatsapp":              [3],
    "booking":               [1, 3],
    "trade":                 [6, 11],
    "export":                [11],
    "import":                [11],
    "africa":                [6, 11],
    "restaurant":            [1, 3, 7, 9],
    "legal":                 [1, 3, 10],
    "real estate":           [1, 2, 3, 7],
    "construction":          [1, 2, 5],
    "healthcare":            [1, 3, 7, 9],
    "logistics":             [1, 6, 11],
    "consulting":            [1, 2, 4, 10],
    "recruitment":           [8],
    "hiring":                [8],
}


# ─────────────────────────────────────────────
# WEBSITE FETCHER
# ─────────────────────────────────────────────

def fetch_website(url: str, timeout: int = 12) -> str:
    """
    Fetch and extract readable text from a website.
    Returns cleaned text content (no HTML tags).
    """
    if not url.startswith("http"):
        url = "https://" + url

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PluggedIN-Scanner/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    }

    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        html = r.text

        # Strip HTML tags — simple but effective for most sites
        import re
        text = re.sub(r'<script[^>]*>[\s\S]*?</script>', ' ', html)
        text = re.sub(r'<style[^>]*>[\s\S]*?</style>', ' ', text)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # Truncate to ~3000 chars — enough for Claude to understand the business
        return text[:3000]

    except Exception as e:
        print(f"[Scanner] Fetch error for {url}: {e}")
        return ""


# ─────────────────────────────────────────────
# INTELLIGENCE EXTRACTOR
# ─────────────────────────────────────────────

def extract_business_profile(url: str, raw_text: str) -> dict:
    """
    Uses Claude to extract structured business intelligence from website text.
    Returns a profile dict with industry, services, size, pain signals, etc.
    """
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are analysing a business website to extract intelligence for an AI agency pitch.

Website URL: {url}
Website content: {raw_text[:2500]}

Extract and return a JSON object with exactly these fields:
{{
  "business_name": "name of the business",
  "industry": "primary industry (e.g. Legal, Real Estate, Restaurant, Healthcare, Construction, Logistics, Consulting, Retail, Technology, Other)",
  "location": "city/country if detectable, else empty string",
  "services": ["list", "of", "main", "services", "max 5"],
  "team_size_signal": "small (1-10) / medium (10-50) / large (50+) / unknown",
  "pain_signals": ["list of business pain points visible on the site — e.g. 'no live chat', 'no WhatsApp', 'manual booking', 'no reviews shown', 'no 24/7 support' — max 5"],
  "strengths": ["list of what they're doing well — max 3"],
  "target_customer": "who their customers are in one sentence",
  "missed_opportunity": "the single biggest revenue opportunity they're missing, in one punchy sentence",
  "tone": "professional / friendly / luxury / budget / technical",
  "has_whatsapp": true or false,
  "has_online_booking": true or false,
  "has_reviews_section": true or false
}}

Return ONLY valid JSON. No explanation, no markdown, no code blocks."""

    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text.strip()
        # Strip markdown if present
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"[Scanner] Profile extraction error: {e}")
        return {
            "business_name": url.split("//")[-1].split("/")[0].replace("www.", "").split(".")[0].title(),
            "industry": "General",
            "location": "",
            "services": [],
            "team_size_signal": "unknown",
            "pain_signals": ["no 24/7 support", "manual lead handling"],
            "strengths": [],
            "target_customer": "local businesses and consumers",
            "missed_opportunity": "Losing leads outside office hours with no automated follow-up",
            "tone": "professional",
            "has_whatsapp": False,
            "has_online_booking": False,
            "has_reviews_section": False,
        }


# ─────────────────────────────────────────────
# MODULE RECOMMENDER
# ─────────────────────────────────────────────

def recommend_modules(profile: dict) -> list[dict]:
    """
    Based on the business profile, recommend the 3-5 most impactful modules.
    Returns a ranked list with personalised rationale and example outputs.
    """
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    modules_catalogue = json.dumps(MODULES, indent=2)
    profile_json = json.dumps(profile, indent=2)

    prompt = f"""You are a senior AI consultant recommending AI agents to a business.

Business Profile:
{profile_json}

Available AI Modules:
{modules_catalogue}

Select the 3-5 most impactful modules for THIS specific business. For each module return:
- Why it's critical for their specific situation (not generic — reference their industry/pain/services)
- A concrete example output the agent would produce for them (make it feel real and specific to their business)
- Estimated monthly impact (e.g. "£2,400 in recovered leads" or "12 hours saved per week")
- Priority: "essential" / "high" / "recommended"

Return a JSON array:
[
  {{
    "module_id": 1,
    "name": "Presence Agent",
    "icon": "📞",
    "priority": "essential",
    "why": "personalised reason referencing their specific situation",
    "example_output": "a realistic, specific example of what this agent would produce or say for their business",
    "monthly_impact": "specific impact estimate",
    "setup_time": "30 seconds / 5 minutes / 30 minutes"
  }}
]

Order by impact, highest first. Return ONLY valid JSON array."""

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"[Scanner] Module recommendation error: {e}")
        # Fallback — always recommend the core three
        return [
            {
                "module_id": 1, "name": "Presence Agent", "icon": "📞",
                "priority": "essential",
                "why": f"Every business in {profile.get('industry','your industry')} loses leads outside office hours. This stops that.",
                "example_output": f"'Hi! Thanks for reaching out to {profile.get('business_name','us')}. How can I help you today?'",
                "monthly_impact": "Recover 30-40% of after-hours leads",
                "setup_time": "30 seconds",
            },
            {
                "module_id": 3, "name": "WhatsApp Assistant", "icon": "💬",
                "priority": "essential",
                "why": "Your customers are on WhatsApp. The AI handles their enquiries 24/7, qualifies them, and books them in.",
                "example_output": "'I can book you in for a consultation on Thursday at 2pm. Can I take your name?'",
                "monthly_impact": "Save 15 hours/week on customer messages",
                "setup_time": "30 seconds",
            },
            {
                "module_id": 7, "name": "Reviews Agent", "icon": "⭐",
                "priority": "high",
                "why": "Reviews are the first thing customers check. The AI monitors and responds to every review professionally.",
                "example_output": "'Thank you so much for your kind words! We're thrilled you had a great experience.'",
                "monthly_impact": "Protect and grow online reputation",
                "setup_time": "5 minutes",
            },
        ]


# ─────────────────────────────────────────────
# ROI CALCULATOR
# ─────────────────────────────────────────────

def estimate_roi(profile: dict, recommended_modules: list) -> dict:
    """
    Generate a simple ROI estimate based on industry and team size.
    Used in the proposal card.
    """
    industry = profile.get("industry", "General").lower()
    size     = profile.get("team_size_signal", "small")

    # Baseline assumptions by industry
    baselines = {
        "legal":       {"avg_lead_value": 800,  "missed_leads_pct": 35, "hours_saved_week": 12},
        "real estate": {"avg_lead_value": 1200, "missed_leads_pct": 40, "hours_saved_week": 15},
        "healthcare":  {"avg_lead_value": 250,  "missed_leads_pct": 30, "hours_saved_week": 10},
        "restaurant":  {"avg_lead_value": 80,   "missed_leads_pct": 20, "hours_saved_week": 8},
        "construction":{"avg_lead_value": 2000, "missed_leads_pct": 30, "hours_saved_week": 10},
        "logistics":   {"avg_lead_value": 1500, "missed_leads_pct": 25, "hours_saved_week": 12},
        "consulting":  {"avg_lead_value": 1000, "missed_leads_pct": 35, "hours_saved_week": 15},
        "retail":      {"avg_lead_value": 150,  "missed_leads_pct": 20, "hours_saved_week": 8},
    }

    b = baselines.get(industry, {"avg_lead_value": 500, "missed_leads_pct": 30, "hours_saved_week": 10})

    # Estimate leads recovered per month (assuming ~20 enquiries/month for small biz)
    monthly_enquiries = {"small": 20, "medium": 60, "large": 150}.get(size, 20)
    leads_recovered   = int(monthly_enquiries * b["missed_leads_pct"] / 100)
    revenue_recovered = leads_recovered * b["avg_lead_value"]
    hours_saved_month = b["hours_saved_week"] * 4

    return {
        "leads_recovered_monthly":   leads_recovered,
        "revenue_protected_monthly": revenue_recovered,
        "hours_saved_monthly":       hours_saved_month,
        "monthly_cost":              397,
        "monthly_roi_multiple":      round(revenue_recovered / 397, 1) if revenue_recovered > 0 else "∞",
        "annual_value":              revenue_recovered * 12,
    }


# ─────────────────────────────────────────────
# AUTO-CONFIG GENERATOR
# ─────────────────────────────────────────────

def generate_agent_config(profile: dict) -> dict:
    """
    Generate a ready-to-use WhatsApp agent config from the scanned business profile.
    This is the Auto-Build from Website feature — one URL → fully configured agent.
    """
    name     = profile.get("business_name", "the business")
    industry = profile.get("industry", "General")
    services = profile.get("services", [])
    tone     = profile.get("tone", "professional but warm")

    # Build FAQs from services
    faqs = []
    for svc in services[:4]:
        faqs.append({
            "question": f"Do you offer {svc.lower()}?",
            "answer":   f"Yes! {svc} is one of our core services. I'd be happy to tell you more or arrange a consultation."
        })

    faqs.append({
        "question": "How do I get started?",
        "answer":   f"The easiest way is to book a free consultation. I can arrange that for you right now."
    })

    return {
        "business_name":  name,
        "industry":       industry,
        "tone":           tone,
        "business_hours": "Monday to Friday, 9am to 6pm",
        "faqs":           faqs,
        "auto_configured_from": "website scan",
        "configured_at":  datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────
# MAIN — FULL SCAN
# ─────────────────────────────────────────────

def scan_business(url: str, deep: bool = False) -> dict:
    """
    Full business scan pipeline. Call this from the API.

    deep=True: runs the Claude-powered deep assessment (higher quality, extra API call)

    Returns a complete intelligence report:
    {
        "url": ...,
        "profile": {...},
        "first_principles": {...},      ← NEW: ICP, intent signals, leverage points, max ROI play
        "recommended_modules": [...],
        "roi": {...},
        "agent_config": {...},
        "architecture": {...},          ← NEW: CEO agent blueprint for this business
        "scanned_at": "...",
    }
    """
    print(f"[Scanner] Scanning {url}...")

    # Step 1: Fetch website
    raw_text = fetch_website(url)
    if not raw_text:
        return {"error": f"Could not fetch {url} — site may be blocking scrapers", "url": url}

    # Step 2: Extract business profile
    print(f"[Scanner] Extracting business profile...")
    profile = extract_business_profile(url, raw_text)
    print(f"[Scanner] Profile: {profile.get('business_name')} ({profile.get('industry')})")

    # Step 3: First principles assessment  ← NEW
    print(f"[Scanner] Running first principles assessment...")
    from lib.first_principles import run_first_principles, run_deep_assessment
    fp = run_first_principles(profile)
    if deep or fp.get("readiness_score", 0) >= 60:
        print(f"[Scanner] High readiness — running deep assessment...")
        deep_insights = run_deep_assessment(profile, fp)
        fp["deep_insights"] = deep_insights

    # Step 4: Recommend modules (enhanced by leverage points from first principles)
    print(f"[Scanner] Recommending modules...")
    modules = recommend_modules(profile)

    # Merge module IDs from leverage points not already in recommendations
    leverage_module_ids = set(lp.get("module_id") for lp in fp.get("leverage_points", []) if lp.get("module_id"))
    existing_module_ids = set(m.get("module_id") for m in modules)
    for mod_id in leverage_module_ids - existing_module_ids:
        if mod_id and mod_id in MODULES:
            mod_info = MODULES[mod_id]
            modules.append({
                "module_id":      mod_id,
                "name":           mod_info["name"],
                "icon":           mod_info["icon"],
                "priority":       "high",
                "why":            f"Identified as a leverage point from first principles analysis for {profile.get('industry')} businesses.",
                "example_output": f"{mod_info['tagline']}",
                "monthly_impact": "See ROI estimates below",
                "setup_time":     "5 minutes",
            })

    # Step 5: Estimate ROI
    roi = estimate_roi(profile, modules)

    # Step 6: Generate agent config
    config = generate_agent_config(profile)

    # Step 7: Build CEO architecture blueprint  ← NEW
    print(f"[Scanner] Building CEO architecture blueprint...")
    try:
        from lib.agent_creator import run_ceo_architecture
        architecture = run_ceo_architecture(profile, fp)
    except Exception as e:
        print(f"[Scanner] Architecture error (non-fatal): {e}")
        architecture = None

    result = {
        "url":                url,
        "profile":            profile,
        "first_principles":   fp,
        "recommended_modules": modules,
        "roi":                roi,
        "agent_config":       config,
        "architecture":       architecture,
        "scanned_at":         datetime.utcnow().isoformat(),
    }

    print(f"[Scanner] Scan complete — {len(modules)} modules, readiness: {fp.get('readiness_score')}%, ROI: {roi['monthly_roi_multiple']}x")
    return result


# ─────────────────────────────────────────────
# MULTI-SOURCE SCAN
# Website + description → unified profile
# ─────────────────────────────────────────────

def scan_from_description(description: str) -> dict:
    """
    Scan a business from a free-text description instead of a URL.
    Useful when: prospect describes their business verbally,
    or when website is not available.
    """
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are analysing a business description to extract intelligence for an AI agency pitch.

Business description: {description}

Extract and return a JSON object with exactly these fields:
{{
  "business_name": "name of the business (or 'Unknown Business' if not stated)",
  "industry": "primary industry",
  "location": "city/country if mentioned, else empty string",
  "services": ["list", "of", "main", "services", "max 5"],
  "team_size_signal": "small / medium / large / unknown",
  "pain_signals": ["pain points visible from the description — max 5"],
  "strengths": ["what they seem to be doing well — max 3"],
  "target_customer": "who their customers are",
  "missed_opportunity": "biggest revenue opportunity they're missing",
  "tone": "professional / friendly / luxury / budget / technical",
  "has_whatsapp": false,
  "has_online_booking": false,
  "has_reviews_section": false
}}

Return ONLY valid JSON."""

    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        profile = json.loads(text)
    except Exception as e:
        print(f"[Scanner] Description scan error: {e}")
        profile = {
            "business_name": "Unknown Business",
            "industry": "General",
            "location": "",
            "services": [],
            "team_size_signal": "small",
            "pain_signals": ["manual processes", "no automation"],
            "strengths": [],
            "target_customer": "local businesses and consumers",
            "missed_opportunity": "No AI automation in place",
            "tone": "professional",
            "has_whatsapp": False,
            "has_online_booking": False,
            "has_reviews_section": False,
        }

    # Run the same analysis pipeline as a URL scan
    from lib.first_principles import run_first_principles
    fp      = run_first_principles(profile)
    modules = recommend_modules(profile)
    roi     = estimate_roi(profile, modules)
    config  = generate_agent_config(profile)

    return {
        "source":             "description",
        "profile":            profile,
        "first_principles":   fp,
        "recommended_modules": modules,
        "roi":                roi,
        "agent_config":       config,
        "scanned_at":         datetime.utcnow().isoformat(),
    }


def scan_multi(
    url: str = None,
    description: str = None,
) -> dict:
    """
    Multi-source scan: combine URL + description into one unified profile.
    Each source enriches the profile — more sources = sharper recommendations.
    """
    profiles = []

    if url:
        raw_text = fetch_website(url)
        if raw_text:
            profiles.append(extract_business_profile(url, raw_text))

    if description:
        desc_result = scan_from_description(description)
        profiles.append(desc_result.get("profile", {}))

    if not profiles:
        return {"error": "No data sources provided or all failed"}

    # Merge profiles — first source wins for most fields, others fill gaps
    merged = profiles[0].copy()
    for p in profiles[1:]:
        for key, val in p.items():
            if not merged.get(key) and val:
                merged[key] = val
            elif key == "pain_signals" and isinstance(val, list):
                existing = set(merged.get("pain_signals", []))
                merged["pain_signals"] = list(existing | set(val))[:6]
            elif key == "services" and isinstance(val, list):
                existing = set(merged.get("services", []))
                merged["services"] = list(existing | set(val))[:5]

    # Run the full analysis on the merged profile
    from lib.first_principles import run_first_principles
    fp      = run_first_principles(merged)
    modules = recommend_modules(merged)
    roi     = estimate_roi(merged, modules)
    config  = generate_agent_config(merged)

    try:
        from lib.agent_creator import run_ceo_architecture
        architecture = run_ceo_architecture(merged, fp)
    except Exception as e:
        print(f"[Scanner] Architecture error (non-fatal): {e}")
        architecture = None

    return {
        "sources":            {"url": url, "description": bool(description)},
        "profile":            merged,
        "first_principles":   fp,
        "recommended_modules": modules,
        "roi":                roi,
        "agent_config":       config,
        "architecture":       architecture,
        "scanned_at":         datetime.utcnow().isoformat(),
    }
