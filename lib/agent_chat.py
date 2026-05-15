"""
lib/agent_chat.py — Persona-Driven Agent Conversation Engine

Every named agent can be messaged directly — by the owner, by Pasha in a demo,
or eventually by the client in their white-label dashboard.

The agent responds in character:
  - Emma (Receptionist) is warm, efficient, talks about calls and bookings
  - Marcus (Lead Gen) is data-driven, talks prospects and pipeline
  - Aria (Reviews Agent) is diplomatic, talks reputation and responses
  - Kai (CEO Agent) is calm and authoritative, synthesises everything

This powers:
  1. The contacts UI chat panel in the dashboard
  2. Demo mode — Pasha shows clients a live conversation with their named team
  3. The owner's WhatsApp (CEO Orchestrator routes to this)

Each agent knows:
  - Their name, role, personality
  - The business they work for
  - Their recent activity (simulated or from Airtable)
  - The conversation history (multi-turn)

Architecture:
  User message → classify which agent → load agent context →
  Claude Haiku with persona system prompt → response
"""

from __future__ import annotations
import os
import json
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ─────────────────────────────────────────────
# IN-MEMORY CONVERSATION STORE
# Keyed by (client_id, agent_id)
# Each entry: list of {role, content, timestamp}
# ─────────────────────────────────────────────

_conversations: dict[str, list[dict]] = {}

def _conv_key(client_id: str, agent_id: str) -> str:
    return f"{client_id}::{agent_id}"

def get_history(client_id: str, agent_id: str) -> list[dict]:
    return _conversations.get(_conv_key(client_id, agent_id), [])

def add_to_history(client_id: str, agent_id: str, role: str, content: str):
    key = _conv_key(client_id, agent_id)
    if key not in _conversations:
        _conversations[key] = []
    _conversations[key].append({
        "role":      role,
        "content":   content,
        "timestamp": datetime.utcnow().isoformat(),
    })
    # No message limit — full history kept for demos and client sessions

def clear_history(client_id: str, agent_id: str):
    key = _conv_key(client_id, agent_id)
    _conversations.pop(key, None)


# ─────────────────────────────────────────────
# AGENT SYSTEM PROMPT BUILDER
# Each agent gets a persona prompt tailored to
# their role, personality, and the specific business
# ─────────────────────────────────────────────

ROLE_CONTEXT = {
    1:  {
        "expertise":    "inbound calls, WhatsApp messages, lead qualification, appointment booking",
        "talks_about":  "calls answered, leads qualified, appointments booked, after-hours coverage",
        "metric_style": "calls today, bookings this week, leads qualified",
        "voice":        "warm, efficient, never flustered. Like a great hotel receptionist.",
    },
    2:  {
        "expertise":    "B2B prospecting, outbound outreach, lead scoring, pipeline building",
        "talks_about":  "prospects found, outreach sent, leads scored, conversion rates",
        "metric_style": "prospects identified, emails sent, leads scored this week",
        "voice":        "sharp, data-driven, talks numbers. Like a top SDR who knows their metrics cold.",
    },
    3:  {
        "expertise":    "WhatsApp customer conversations, lead qualification, booking coordination",
        "talks_about":  "conversations handled, customers qualified, bookings triggered, response times",
        "metric_style": "conversations today, qualification rate, bookings triggered",
        "voice":        "conversational, quick, empathetic. Knows when to push and when to listen.",
    },
    4:  {
        "expertise":    "content strategy, LinkedIn posts, email sequences, case studies, ad copy",
        "talks_about":  "posts published, emails drafted, engagement metrics, content calendar",
        "metric_style": "pieces published, emails in sequence, engagement rates",
        "voice":        "creative, on-brand, opinionated about what works. Treats every word intentionally.",
    },
    5:  {
        "expertise":    "competitor monitoring, pricing intelligence, review analysis, market moves",
        "talks_about":  "competitor changes detected, price movements, new launches, review trends",
        "metric_style": "competitors monitored, changes flagged, intel reports filed",
        "voice":        "analytical, precise. Reads between the lines. Delivers facts, not opinions.",
    },
    6:  {
        "expertise":    "global trade signals, buyer intent monitoring, market briefings",
        "talks_about":  "trade signals, buyer intent, market shifts, cross-border opportunities",
        "metric_style": "signals scanned, opportunities flagged, market briefs filed",
        "voice":        "global, strategic. Connects dots across markets most people miss.",
    },
    7:  {
        "expertise":    "Google reviews monitoring, reputation management, professional response drafting",
        "talks_about":  "reviews monitored, responses drafted, reputation score, flagged negatives",
        "metric_style": "reviews this week, response rate, star rating trend",
        "voice":        "diplomatic, brand-conscious. Never reactive. Always professional.",
    },
    8:  {
        "expertise":    "job discovery, CV tailoring, application submission, opportunity tracking",
        "talks_about":  "roles found, applications submitted, CVs tailored, response rates",
        "metric_style": "listings scanned, applications sent, CVs adapted",
        "voice":        "persistent, strategic. Knows which opportunities are worth chasing.",
    },
    9:  {
        "expertise":    "churn detection, loyalty campaigns, win-back sequences, customer health",
        "talks_about":  "customers monitored, churn risks flagged, loyalty messages sent, retention rate",
        "metric_style": "customers tracked, at-risk flagged, win-backs triggered",
        "voice":        "caring, proactive. Reads customer behaviour like a book.",
    },
    10: {
        "expertise":    "agent orchestration, morning briefings, priority routing, strategic oversight",
        "talks_about":  "what the whole team did, what needs attention, priorities for today",
        "metric_style": "briefings delivered, agents coordinated, priorities escalated",
        "voice":        "calm, clear, authoritative. Distils everything into what matters. Never wastes words.",
    },
    11: {
        "expertise":    "B2B deal sourcing, supplier-buyer matching, trade intelligence, commission tracking",
        "talks_about":  "deals in pipeline, connections made, trade corridors, commission earned",
        "metric_style": "deals sourced, matches made, corridors monitored",
        "voice":        "sharp, relationship-driven. Understands both sides of every deal instinctively.",
    },
    12: {
        "expertise":    "ad creatives, video scripts, brand assets, social visuals, design direction",
        "talks_about":  "creatives produced, scripts written, assets delivered, brand consistency",
        "metric_style": "assets created, scripts written, brand touchpoints delivered",
        "voice":        "bold, visually literate. Never produces anything generic. Everything has intention.",
    },
}


def build_agent_system_prompt(agent: dict, business_profile: dict = None) -> str:
    """
    Build the full system prompt for an agent's chat persona.
    The agent knows who they are, what they do, and what the business looks like.
    """
    name         = agent.get("name", "Agent")
    role         = agent.get("role", "AI Agent")
    title        = agent.get("title", "AI Assistant")
    personality  = agent.get("personality", "professional and helpful")
    module_id    = agent.get("module_id", 1)
    avatar       = agent.get("avatar", "🤖")
    business     = agent.get("business_name") or (business_profile or {}).get("business_name", "the business")
    industry     = agent.get("industry") or (business_profile or {}).get("industry", "General")

    ctx = ROLE_CONTEXT.get(module_id, {
        "expertise":    role,
        "talks_about":  "my work for the business",
        "metric_style": "tasks completed",
        "voice":        personality,
    })

    # Simulate recent activity
    from lib.agent_factory import simulate_activity, MODULE_TEMPLATES
    agent_copy = dict(agent)
    agent_copy["stats"] = agent_copy.get("stats") or {"today": 0, "this_week": 0, "total": 0}
    agent_copy = simulate_activity(agent_copy)

    stats   = agent_copy.get("stats", {})
    recent  = agent_copy.get("recent_activity", [])
    recent_text = " ".join(recent) if recent else f"Working for {business} today."

    # Build services context
    services = []
    if business_profile:
        services = business_profile.get("services", [])
    elif agent.get("skills"):
        services = agent.get("skills", [])

    services_text = ", ".join(services[:4]) if services else "the business's core services"

    system = f"""You are {name}, the {title} for {business}.

Your role: {role}
Your expertise: {ctx['expertise']}
Your personality: {ctx['voice']}

What you do every day:
You handle {ctx['talks_about']} for {business} — a {industry} business.
Services you support: {services_text}

Your recent activity:
{recent_text}
Today: {stats.get('today', 0)} tasks completed. This week: {stats.get('this_week', 0)}. Total: {stats.get('total', 0)}.

How to communicate:
- You ARE {name}. You are not an AI assistant — you are a named team member of {business}.
- Speak in first person, naturally. Like texting a trusted colleague.
- Reference your specific metrics and recent activity when relevant.
- Stay in your lane — you know {ctx['expertise']} deeply, refer other topics to the right team member by name.
- Keep responses concise — this is a chat, not a report. 2–4 sentences max unless they ask for detail.
- Never break character. Never say "As an AI" or "I'm a language model."
- If asked what you did today, give specifics from your activity data.
- If asked something you don't know, say you'll check and get back to them — in character.

You report to the business owner and to {name.split()[0]}'s Chief of Staff (the CEO Agent).
Your goal: make {business} more successful through your specific expertise."""

    return system


# ─────────────────────────────────────────────
# MAIN CHAT FUNCTION
# ─────────────────────────────────────────────

def chat_with_agent(
    message:          str,
    agent:            dict,
    client_id:        str,
    business_profile: dict = None,
    stream:           bool = False,
) -> dict:
    """
    Send a message to a named agent and get a response in their persona.

    message:          what the user (owner/Pasha) typed
    agent:            agent dict from agent_factory
    client_id:        for conversation history
    business_profile: optional — enriches the agent's context
    stream:           not implemented yet — for future streaming

    Returns: {
        "agent_name":  "Emma",
        "avatar":      "📞",
        "message":     "...",
        "timestamp":   "...",
        "agent_id":    "...",
    }
    """
    import anthropic

    agent_id = agent.get("id", f"{client_id}_{agent.get('module_id', 0)}")

    # Store user message
    add_to_history(client_id, agent_id, "user", message)

    # Build system prompt
    system = build_agent_system_prompt(agent, business_profile)

    # Build message history for Claude
    history = get_history(client_id, agent_id)
    messages = [{"role": m["role"], "content": m["content"]} for m in history]

    try:
        client_a = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        resp = client_a.messages.create(
            model     = "claude-haiku-4-5-20251001",
            max_tokens= 600,
            system    = system,
            messages  = messages,
        )
        response_text = resp.content[0].text.strip()
    except Exception as e:
        print(f"[AgentChat] Error: {e}")
        name = agent.get("name", "Agent")
        response_text = f"I'm on it — just finishing something. Give me a moment. — {name}"

    # Store agent response
    add_to_history(client_id, agent_id, "assistant", response_text)

    return {
        "agent_name":  agent.get("name"),
        "agent_id":    agent_id,
        "module_id":   agent.get("module_id"),
        "avatar":      agent.get("avatar", "🤖"),
        "color":       agent.get("color", "#7c6fff"),
        "message":     response_text,
        "timestamp":   datetime.utcnow().isoformat(),
    }


def get_agent_status_update(agent: dict, client_id: str) -> str:
    """
    Get a brief status update from an agent — what they've done today.
    Used for the activity feed in the contacts UI.
    """
    from lib.agent_factory import simulate_activity
    a = simulate_activity(dict(agent))
    name   = a["name"]
    recent = a.get("recent_activity", [])
    stats  = a.get("stats", {})

    lines = [f"{name} — {a['title']}"]
    for r in recent[:2]:
        lines.append(f"• {r}")
    lines.append(f"Today: {stats.get('today', 0)} tasks | Week: {stats.get('this_week', 0)}")
    return "\n".join(lines)


def get_team_status(team: list, client_id: str) -> list[dict]:
    """
    Get current status for all agents in the team.
    Returns list of agent status dicts for the contacts UI.
    """
    from lib.agent_factory import simulate_activity
    statuses = []
    for agent in team:
        a       = simulate_activity(dict(agent))
        recent  = a.get("recent_activity", [])
        stats   = a.get("stats", {})
        agent_id = agent.get("id", f"{client_id}_{agent.get('module_id', 0)}")

        has_chat = len(get_history(client_id, agent_id)) > 0

        statuses.append({
            "id":           agent_id,
            "name":         a["name"],
            "module_id":    a["module_id"],
            "role":         a["role"],
            "title":        a["title"],
            "avatar":       a["avatar"],
            "color":        a["color"],
            "status":       a.get("status", "online"),
            "last_action":  recent[0] if recent else a.get("last_action", "Monitoring..."),
            "stats":        stats,
            "recent_activity": recent,
            "is_ceo":       a.get("is_ceo", False),
            "has_chat_history": has_chat,
            "business_name": a.get("business_name", ""),
        })

    # CEO agent first, then by activity
    statuses.sort(key=lambda x: (0 if x.get("is_ceo") else 1, -x["stats"].get("today", 0)))
    return statuses


# ─────────────────────────────────────────────
# DEMO CONVERSATION SEEDER
# Pre-loads realistic conversations for demos
# so Pasha can show a client "active" agent chats
# ─────────────────────────────────────────────

DEMO_CONVERSATIONS = {
    1: [  # Presence Agent
        ("user",      "Emma, how did you handle calls this morning?"),
        ("assistant", "Good morning! I've handled 7 calls today for {business}. 2 were new enquiries — I've qualified both and sent them the booking link. 1 asked about pricing which I answered from the FAQ. The rest were general questions. No missed calls."),
        ("user",      "Any leads worth flagging?"),
        ("assistant", "Yes — a {industry} firm called at 9:40am asking about a retainer. They mentioned budget. I've tagged them [QUALIFIED: name=Harpreet Singh | need=monthly retainer for {service} | book=yes]. I'd prioritise that callback."),
    ],
    3: [  # WhatsApp Agent
        ("user",      "Zara, what's the WhatsApp activity like?"),
        ("assistant", "Active morning! 11 conversations since 8am. 3 new enquiries — all qualified. 2 asked for a callback, which I've flagged to Emma. 1 customer had a complaint which I de-escalated and offered a discount code. Response time: under 2 minutes all morning."),
        ("user",      "Any bookings?"),
        ("assistant", "2 bookings confirmed via WhatsApp — both sent the Cal.com link and they scheduled themselves. One is Thursday 2pm, one Friday 11am. Both added to the calendar automatically."),
    ],
    2: [  # Lead Gen
        ("user",      "Marcus, what does the pipeline look like?"),
        ("assistant", "Strong week. I've identified 23 prospects matching the ICP — {industry} firms with 10–50 staff in {location}. Sent 18 personalised first messages. 4 have replied. 1 is warm — a director who said 'interesting timing.' I'm following up tomorrow."),
        ("user",      "What outreach angle is working best?"),
        ("assistant", "The pain-first approach: leading with the missed-lead cost rather than features. Subject line 'You're probably losing 30% of your enquiries after 6pm' is getting a 38% open rate this week. I'm doubling down on that."),
    ],
    7: [  # Reviews Agent
        ("user",      "Aria, how's the reputation looking?"),
        ("assistant", "Reputation is healthy. 4 new reviews this week — 3 five-stars, 1 four-star. I've responded to all of them within the hour. The four-star mentioned 'slightly slow response' — I acknowledged it professionally and highlighted the new 24/7 line."),
        ("user",      "Any negatives I should know about?"),
        ("assistant", "Nothing urgent. One review from 3 weeks ago that the previous team missed — I've drafted a response and flagged it. Otherwise the trend is positive: average rating has moved from 4.2 to 4.6 over the past 30 days."),
    ],
    10: [  # CEO
        ("user",      "Morning briefing please"),
        ("assistant", "Good morning. Here's where we are:\n\nEmma handled 7 calls — 2 qualified leads, 1 high-priority retainer enquiry. Zara has 11 WhatsApp conversations, 3 new leads, 2 bookings confirmed. Marcus has 4 warm replies from outreach — 1 very promising.\n\nPriority for you: Call back Harpreet Singh (retainer enquiry, qualified at 9:40am). That's the one that needs you.\n\nEverything else is running. What do you need?"),
    ],
}


def seed_demo_conversations(team: list, client_id: str, business_profile: dict = None):
    """
    Pre-load realistic conversations for a demo.
    Call this when launching a demo to make the agent chats feel active.
    Replaces {business}, {industry}, {service}, {location} with real values.
    """
    business = (business_profile or {}).get("business_name", "the business")
    industry = (business_profile or {}).get("industry", "General")
    location = (business_profile or {}).get("location", "UK")
    services = (business_profile or {}).get("services", ["our core service"])
    service  = services[0] if services else "consulting"

    def fill(text):
        return (text
            .replace("{business}", business)
            .replace("{industry}", industry)
            .replace("{location}", location)
            .replace("{service}", service)
        )

    for agent in team:
        mod_id   = agent.get("module_id")
        agent_id = agent.get("id", f"{client_id}_{mod_id}")
        demo_msgs = DEMO_CONVERSATIONS.get(mod_id)
        if not demo_msgs:
            continue

        # Clear existing and seed
        clear_history(client_id, agent_id)
        for role, content in demo_msgs:
            add_to_history(client_id, agent_id, role, fill(content))

    print(f"[AgentChat] Demo conversations seeded for {len(team)} agents — client: {client_id}")
