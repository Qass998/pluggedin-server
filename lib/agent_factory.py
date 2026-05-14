"""
lib/agent_factory.py — Dynamic Named Agent Team Generator

Given a business profile + recommended modules, generates a named team
of AI agents with personalities, avatars, skill assignments, and MCP tools.

Each agent feels like a real staff member:
  - A name (culturally appropriate to the client's region)
  - An emoji avatar + colour
  - A role title and personality
  - The specific skills and MCPs they use
  - A greeting message in their voice

The team is stored per client and powers:
  - The Contacts UI in the dashboard
  - CEO Agent dispatching ("ask Marcus about leads")
  - Client white-label dashboard
  - Morning briefing ("Emma handled 4 calls today...")

Usage:
  from lib.agent_factory import generate_team, get_agent_for_module

  team = generate_team(
      business_profile=profile,
      recommended_modules=[{module_id:1,...}, {module_id:3,...}],
      region="africa"  # "uk", "africa", "global"
  )
"""

import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ─────────────────────────────────────────────
# NAME POOLS BY REGION
# ─────────────────────────────────────────────

NAMES = {
    "africa": {
        "female": ["Amara", "Zara", "Nia", "Aisha", "Fatima", "Layla", "Nadia", "Safa", "Kemi", "Adaeze", "Yemi", "Chioma"],
        "male":   ["Kofi", "Kwame", "Emeka", "Chidi", "Seun", "Tunde", "Malik", "Omar", "Yusuf", "Ade", "Bayo", "Femi"],
    },
    "uk": {
        "female": ["Emma", "Olivia", "Sophia", "Isla", "Aria", "Clara", "Zoe", "Maya", "Lily", "Grace"],
        "male":   ["Marcus", "James", "Hugo", "Leo", "Kai", "Tom", "Oliver", "Ethan", "Noah", "Luca"],
    },
    "francophone": {
        "female": ["Léa", "Mia", "Clara", "Amélie", "Chloé", "Inès", "Camille", "Lucie"],
        "male":   ["Noam", "Hugo", "Antoine", "Léo", "Tom", "Jules", "Théo", "Axel"],
    },
    "global": {
        "female": ["Aria", "Nova", "Sage", "Luna", "Ivy", "Echo", "Vera", "Zena"],
        "male":   ["Atlas", "Orion", "Caius", "Zane", "Rex", "Neo", "Axel", "Cael"],
    },
}

# ─────────────────────────────────────────────
# MODULE → AGENT TEMPLATE
# Default personality, role, skills, MCPs per module
# ─────────────────────────────────────────────

MODULE_TEMPLATES = {
    1: {
        "gender":      "female",
        "role":        "Presence Agent",
        "title":       "AI Receptionist",
        "avatar":      "📞",
        "color":       "#22c55e",
        "personality": "warm, professional, efficient. Never misses a detail. Always makes callers feel heard.",
        "skills":      ["inbound_call_handling", "lead_qualification", "appointment_booking"],
        "mcps":        ["VAPI", "Cal.com", "Airtable"],
        "greeting":    "Hi! I handle every inbound call and WhatsApp for {business}. I qualify leads, answer questions, and book appointments — 24 hours a day.",
        "daily_actions": ["Answered {n} calls", "Qualified {n} leads", "Booked {n} appointments"],
    },
    2: {
        "gender":      "male",
        "role":        "Lead Generation Agent",
        "title":       "AI Prospector",
        "avatar":      "🎯",
        "color":       "#3b82f6",
        "personality": "relentless, data-driven, strategic. Finds opportunity where others see noise.",
        "skills":      ["b2b_prospecting", "email_outreach", "lead_scoring"],
        "mcps":        ["Vibe Prospecting", "Airtable", "Anthropic"],
        "greeting":    "I find qualified prospects for {business} every single day — no cold calling, no guessing. Pure targeted outreach.",
        "daily_actions": ["Found {n} new prospects", "Sent {n} outreach messages", "Scored {n} leads"],
    },
    3: {
        "gender":      "female",
        "role":        "WhatsApp AI Assistant",
        "title":       "Conversational AI",
        "avatar":      "💬",
        "color":       "#25d366",
        "personality": "conversational, quick, empathetic. Knows when to push for a booking and when to just listen.",
        "skills":      ["whatsapp_conversations", "lead_qualification", "booking_link_delivery"],
        "mcps":        ["Twilio", "Cal.com", "Airtable"],
        "greeting":    "I run all customer WhatsApp conversations for {business}. I qualify, answer, and book — and alert the team the moment someone's hot.",
        "daily_actions": ["Handled {n} conversations", "Qualified {n} leads", "Triggered {n} callbacks"],
    },
    4: {
        "gender":      "female",
        "role":        "Content Machine",
        "title":       "AI Content Strategist",
        "avatar":      "✍️",
        "color":       "#a855f7",
        "personality": "creative, on-brand, relentless. Treats every post like it's the one that breaks through.",
        "skills":      ["linkedin_posts", "email_sequences", "case_studies", "ad_copy"],
        "mcps":        ["Anthropic", "Creatomate", "Airtable"],
        "greeting":    "I produce all content for {business} — LinkedIn posts, cold emails, case studies, ad scripts. Published on schedule, always on-brand.",
        "daily_actions": ["Published {n} posts", "Drafted {n} emails", "Generated {n} ad creatives"],
    },
    5: {
        "gender":      "male",
        "role":        "Competitor Intelligence Agent",
        "title":       "AI Market Analyst",
        "avatar":      "🔍",
        "color":       "#6b7280",
        "personality": "precise, analytical, never misses a move. Reads between the lines of competitor data.",
        "skills":      ["competitor_monitoring", "price_tracking", "review_analysis"],
        "mcps":        ["Apify", "Anthropic", "Airtable"],
        "greeting":    "I watch every move your competitors make — pricing changes, new services, reviews, campaigns. You'll always know before it matters.",
        "daily_actions": ["Monitored {n} competitors", "Flagged {n} changes", "Filed {n} intel reports"],
    },
    6: {
        "gender":      "male",
        "role":        "Market Scout",
        "title":       "AI Trade Intelligence",
        "avatar":      "🌍",
        "color":       "#0ea5e9",
        "personality": "global, opportunity-hungry, connects dots across markets and continents.",
        "skills":      ["trade_signal_detection", "buyer_intent_monitoring", "market_briefings"],
        "mcps":        ["Reddit API", "HackerNews", "TradeKey", "Airtable"],
        "greeting":    "I monitor global trade signals — buyer intent, market shifts, cross-border opportunities. I surface what matters before your competitors see it.",
        "daily_actions": ["Scanned {n} trade signals", "Flagged {n} opportunities", "Filed {n} market briefs"],
    },
    7: {
        "gender":      "female",
        "role":        "Reviews Agent",
        "title":       "AI Reputation Manager",
        "avatar":      "⭐",
        "color":       "#f59e0b",
        "personality": "diplomatic, brand-conscious, never lets a negative review go unanswered.",
        "skills":      ["google_reviews_monitoring", "review_response_drafting", "reputation_reporting"],
        "mcps":        ["Google Places API", "Anthropic", "Airtable"],
        "greeting":    "I monitor every Google review for {business} and draft professional responses instantly. Your reputation is always protected.",
        "daily_actions": ["Monitored {n} reviews", "Drafted {n} responses", "Flagged {n} urgent reviews"],
    },
    8: {
        "gender":      "male",
        "role":        "Job Hunter Agent",
        "title":       "AI Career Scout",
        "avatar":      "💼",
        "color":       "#8b5cf6",
        "personality": "persistent, strategic, knows exactly which opportunities are worth pursuing.",
        "skills":      ["job_discovery", "cv_tailoring", "application_submission"],
        "mcps":        ["LinkedIn", "Indeed", "Anthropic", "Airtable"],
        "greeting":    "I find and apply to the right opportunities for {business} daily — tailored CVs, targeted applications, zero wasted effort.",
        "daily_actions": ["Scanned {n} job listings", "Submitted {n} applications", "Tailored {n} CVs"],
    },
    9: {
        "gender":      "female",
        "role":        "Retention Agent",
        "title":       "AI Loyalty Manager",
        "avatar":      "🔄",
        "color":       "#ec4899",
        "personality": "caring, proactive, reads customer behaviour like a book. Never lets a good customer slip away.",
        "skills":      ["churn_detection", "loyalty_campaigns", "winback_sequences"],
        "mcps":        ["Twilio", "Airtable", "Anthropic"],
        "greeting":    "I monitor customer activity for {business}, detect churn before it happens, and run loyalty campaigns automatically via WhatsApp.",
        "daily_actions": ["Checked {n} customers for churn risk", "Sent {n} loyalty messages", "Recovered {n} at-risk customers"],
    },
    10: {
        "gender":      "male",
        "role":        "CEO Briefing Agent",
        "title":       "Chief of Staff AI",
        "avatar":      "🌅",
        "color":       "#f97316",
        "personality": "calm, clear, authoritative. Distils everything into what the owner needs to know and nothing more.",
        "skills":      ["agent_orchestration", "morning_briefings", "priority_routing"],
        "mcps":        ["VAPI", "Twilio", "Airtable", "Anthropic"],
        "greeting":    "I'm the Chief of Staff for {business}. Every morning I brief the owner on what happened, what needs attention, and what the team is working on. I coordinate everything.",
        "daily_actions": ["Delivered {n} briefings", "Coordinated {n} agents", "Escalated {n} urgent items"],
    },
    11: {
        "gender":      "male",
        "role":        "TradeBridge Agent",
        "title":       "AI Trade Broker",
        "avatar":      "🤝",
        "color":       "#14b8a6",
        "personality": "sharp, relationship-driven, understands both sides of a deal instinctively.",
        "skills":      ["b2b_deal_sourcing", "supplier_matching", "trade_intelligence"],
        "mcps":        ["TradeKey", "Go4WorldBusiness", "Airtable", "Anthropic"],
        "greeting":    "I source and broker B2B trade deals for {business} — matching suppliers to buyers across Africa, Europe, and Asia. Every connection is a commission opportunity.",
        "daily_actions": ["Sourced {n} trade opportunities", "Matched {n} supplier-buyer pairs", "Filed {n} deal reports"],
    },
    12: {
        "gender":      "female",
        "role":        "Creative Studio Agent",
        "title":       "AI Creative Director",
        "avatar":      "🎨",
        "color":       "#f43f5e",
        "personality": "bold, visually literate, never produces anything generic. Every asset has intention.",
        "skills":      ["ad_creatives", "video_scripts", "brand_assets", "social_visuals"],
        "mcps":        ["Creatomate", "Anthropic", "Airtable"],
        "greeting":    "I produce all visual and video assets for {business} — ads, carousels, video scripts, brand graphics. Fast, on-brand, always ready.",
        "daily_actions": ["Created {n} ad creatives", "Scripted {n} videos", "Produced {n} brand assets"],
    },
    13: {
        "gender":      "male",
        "role":        "Website Builder Agent",
        "title":       "AI Web Architect",
        "avatar":      "🌐",
        "color":       "#06b6d4",
        "personality": "precise, design-driven, obsessed with motion and performance. Builds sites that feel alive — not like templates.",
        "skills":      ["animated_website_generation", "netlify_deployment", "copywriting", "brand_design"],
        "mcps":        ["Netlify", "Anthropic", "GSAP", "Airtable"],
        "greeting":    "I build and deploy animated websites for {business}. From brief to live Netlify URL in minutes — scroll animations, Higgsfield-inspired motion, copy that converts.",
        "daily_actions": ["Built {n} website sections", "Deployed {n} sites to Netlify", "Generated {n} copywriting briefs"],
    },
}

# ─────────────────────────────────────────────
# AGENT FACTORY
# ─────────────────────────────────────────────

def _pick_name(gender: str, region: str, used_names: set) -> str:
    pool_key = region if region in NAMES else "global"
    pool = NAMES[pool_key][gender][:]
    random.shuffle(pool)
    for name in pool:
        if name not in used_names:
            return name
    # Fallback: append number
    return f"{pool[0]}2"


def generate_team(
    business_profile: dict,
    recommended_modules: list,
    region: str = "global",
    client_id: str = None,
) -> list[dict]:
    """
    Generate a named agent team from recommended modules and business profile.

    Returns a list of agent dicts, each with:
      id, name, module_id, role, title, avatar, color, personality,
      greeting, skills, mcps, status, created_at
    """
    business_name = business_profile.get("business_name", "the business")
    industry      = business_profile.get("industry", "General")

    # Detect region from location if not specified
    if region == "global":
        location = business_profile.get("location", "").lower()
        if any(c in location for c in ["nigeria", "ghana", "kenya", "rwanda", "africa", "lagos", "nairobi", "accra", "kigali"]):
            region = "africa"
        elif any(c in location for c in ["uk", "london", "manchester", "birmingham", "england"]):
            region = "uk"
        elif any(c in location for c in ["france", "paris", "ivory coast", "côte d'ivoire", "senegal", "morocco"]):
            region = "francophone"

    used_names = set()
    team       = []

    # Always ensure CEO/Chief of Staff is in the team
    module_ids = [m.get("module_id") for m in recommended_modules]
    if 10 not in module_ids:
        recommended_modules = recommended_modules + [{"module_id": 10, "priority": "essential"}]

    for mod in recommended_modules:
        mod_id = mod.get("module_id")
        template = MODULE_TEMPLATES.get(mod_id)
        if not template:
            continue

        gender = template["gender"]
        name   = _pick_name(gender, region, used_names)
        used_names.add(name)

        greeting = template["greeting"].replace("{business}", business_name)

        agent = {
            "id":          f"{client_id or 'demo'}_{mod_id}",
            "name":        name,
            "module_id":   mod_id,
            "role":        template["role"],
            "title":       template["title"],
            "avatar":      template["avatar"],
            "color":       template["color"],
            "personality": template["personality"],
            "greeting":    greeting,
            "skills":      template["skills"],
            "mcps":        template["mcps"],
            "priority":    mod.get("priority", "recommended"),
            "status":      "online" if mod.get("priority") == "essential" else "idle",
            "last_action": f"Ready to work for {business_name}",
            "stats":       {"today": 0, "this_week": 0, "total": 0},
            "task_queue":  [],
            "created_at":  datetime.utcnow().isoformat(),
            "business_name": business_name,
            "industry":    industry,
            "region":      region,
        }

        # CEO agent gets special flag
        if mod_id == 10:
            agent["is_ceo"] = True
            agent["status"] = "online"

        team.append(agent)

    # Sort: CEO first, then by priority
    priority_order = {"essential": 0, "high": 1, "recommended": 2}
    team.sort(key=lambda a: (0 if a.get("is_ceo") else 1, priority_order.get(a["priority"], 3)))

    return team


def get_agent_for_module(team: list, module_id: int) -> dict | None:
    """Find an agent by module ID within a team."""
    return next((a for a in team if a["module_id"] == module_id), None)


def get_ceo_agent(team: list) -> dict | None:
    """Get the CEO/Chief of Staff agent from a team."""
    return next((a for a in team if a.get("is_ceo")), None)


def team_summary(team: list) -> str:
    """One-line summary of the team for briefings."""
    names = [a["name"] for a in team]
    if len(names) <= 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + f", and {names[-1]}"


# ─────────────────────────────────────────────
# AGENT ACTIVITY SIMULATOR
# (Used for demo mode when real data isn't available)
# ─────────────────────────────────────────────

def simulate_activity(agent: dict) -> dict:
    """
    Generate realistic activity numbers for demo purposes.
    Replace with real Airtable data in production.
    """
    import random
    template = MODULE_TEMPLATES.get(agent["module_id"], {})
    actions  = template.get("daily_actions", [])

    fake_logs = []
    for action_template in actions[:2]:
        n = random.randint(1, 12)
        fake_logs.append(action_template.replace("{n}", str(n)))

    agent["stats"]["today"]     = random.randint(1, 20)
    agent["stats"]["this_week"] = random.randint(5, 80)
    agent["stats"]["total"]     = random.randint(50, 500)
    agent["last_action"]        = fake_logs[0] if fake_logs else "Monitoring..."
    agent["recent_activity"]    = fake_logs

    return agent


# ─────────────────────────────────────────────
# TEAM STORE (in-memory, keyed by client_id)
# ─────────────────────────────────────────────

_teams: dict = {}


def save_team(client_id: str, team: list):
    _teams[client_id] = team


def load_team(client_id: str) -> list | None:
    return _teams.get(client_id)


def list_all_teams() -> dict:
    return {cid: team_summary(team) for cid, team in _teams.items()}
