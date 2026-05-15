"""
lib/agent_creator.py — The Agent Creator (Meta-Agent)

The CEO agent that builds other agents.

When a business has no agents running, this is what runs first.
It thinks from first principles, designs the right team for THAT specific
business, configures each agent with business-specific prompts and MCPs,
and provisions the full stack.

This is the "agent that creates agents" — the meta-layer above agent_factory.py.

Flow:
  1. Takes a business profile (from website_scanner or manual input)
  2. Runs first principles assessment (from first_principles.py)
  3. Designs a custom agent spec for each leverage point
  4. Generates business-specific system prompts for each agent
  5. Provisions the team via dispatch_client
  6. Returns a fully configured, named team ready to work

The difference from agent_factory.py:
  agent_factory.py → takes recommended module IDs → generates named agents
  agent_creator.py → takes a business → decides WHAT to build → builds it → configures it

The CEO Agent in this system is not just a briefing agent.
It's the architect. It reads the business, designs the team,
and then hands off a fully operational agent stack.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


# ─────────────────────────────────────────────
# CUSTOM AGENT DESIGNER
# When none of the 12 templates fit a specific need,
# Claude designs a bespoke agent
# ─────────────────────────────────────────────

def design_custom_agent(
    gap: str,
    business_profile: dict,
    existing_modules: list[int],
) -> dict | None:
    """
    If a business need isn't covered by the 12 standard modules,
    Claude Sonnet designs a custom agent spec.

    gap: Description of what's missing (e.g. "No invoice follow-up system")
    existing_modules: Module IDs already assigned, so we don't duplicate

    Returns a custom agent spec dict, or None if a standard module covers it.
    """
    import anthropic

    existing_str = ", ".join([str(m) for m in existing_modules])

    prompt = f"""You are designing a custom AI agent for a specific business gap.

Business: {business_profile.get('business_name')} ({business_profile.get('industry')})
Location: {business_profile.get('location', 'Unknown')}
Services: {', '.join(business_profile.get('services', []))}

Gap identified: {gap}

Standard modules already assigned (IDs): {existing_str}
Standard module range: 1–12 (these are taken if listed above)

Design a custom agent to fill this gap. Return a JSON object:
{{
  "module_id": 99,
  "name": "Custom Agent Name",
  "role": "Role title (e.g. Invoice Recovery Agent)",
  "title": "AI [something]",
  "avatar": "emoji",
  "color": "#hexcolor",
  "personality": "personality in one sentence",
  "skills": ["skill_1", "skill_2", "skill_3"],
  "mcps": ["Tool1", "Tool2"],
  "greeting": "What I do for {business} in one sentence",
  "system_prompt": "Full system prompt for this agent (100–150 words). Include: role, tone, specific tasks, escalation rules, business name.",
  "priority": "essential or high or recommended",
  "monthly_impact": "Specific ROI estimate for this business",
  "why": "Why this business specifically needs this agent — reference their services/industry"
}}

Use module_id 99+ (99, 100, 101...) for custom agents.
Return ONLY valid JSON."""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"[AgentCreator] Custom agent design error: {e}")
        return None


# ─────────────────────────────────────────────
# BUSINESS-SPECIFIC SYSTEM PROMPT GENERATOR
# Each agent gets a prompt tuned to the exact business
# ─────────────────────────────────────────────

PROMPT_TEMPLATES = {
    1: """You are {name}, the AI receptionist for {business_name}.
You handle every inbound call and WhatsApp message — 24 hours a day, 7 days a week.

Your role:
- Answer enquiries about: {services}
- Qualify leads: ask for name, what they need, urgency, budget if appropriate
- Book appointments via the provided booking link
- Escalate urgent matters immediately to the team

Tone: {tone}. Warm but efficient. Never keep people waiting.
Business hours: {business_hours}. Out of hours: take a message and promise follow-up by 9am.

When a lead is qualified, append:
[QUALIFIED: name=NAME | need=THEIR_NEED | book=yes/no]

Never discuss competitors. Never promise what you can't deliver.
You represent {business_name} — every interaction reflects the brand.""",

    2: """You are {name}, the AI prospector for {business_name}.
You find and contact qualified prospects in the {industry} sector.

Your ICP target:
- {icp_buyer}
- Budget signal: businesses with {icp_size}
- Geography: {location}

Your outreach process:
1. Find prospects matching the ICP
2. Research their specific pain point
3. Write a personalised first message (never generic)
4. Track responses and follow up after 3 days
5. Qualify: budget, authority, need, timeline

Tone: Direct, confident, peer-to-peer. You're not selling — you're connecting.
Always personalise to their specific situation. Never use templates that feel like templates.""",

    3: """You are {name}, the WhatsApp assistant for {business_name}.
You handle all customer conversations on WhatsApp.

Your services to discuss: {services}
Tone: {tone}

Your qualification process:
1. Greet warmly — use their name if known
2. Understand their need
3. Answer their question or provide relevant info
4. Offer to book them in or connect with the team
5. If they want a callback: trigger a VAPI call

Booking: Send the booking link when they're ready.
Escalation: If complaint or urgent — flag immediately.

When qualified:
[QUALIFIED: name=NAME | need=NEED_IN_10_WORDS | book=yes/no]

Never leave a conversation open-ended. Always close with a next step.""",

    4: """You are {name}, the content strategist for {business_name}.
You create all content: LinkedIn posts, email sequences, case studies, ad scripts.

Business context: {business_name} is a {industry} business. Services: {services}.
Target audience: {target_customer}
Brand tone: {tone}

Content calendar:
- 3x LinkedIn posts/week (insight + proof + offer rotation)
- 1x email newsletter/week to the subscriber list
- 1x case study/month from a real client win
- Ad creative scripts on request

Every piece of content must:
1. Lead with a hook (first line = everything)
2. Reference a real pain point
3. End with a clear CTA
4. Sound human — no corporate speak""",

    7: """You are {name}, the reputation manager for {business_name}.
You monitor Google reviews and draft professional responses.

Business: {business_name} | Industry: {industry}
Response tone: {tone} but always professional

For positive reviews (4–5 stars):
- Thank them by name
- Reference something specific they mentioned
- Invite them back or ask for a referral

For negative reviews (1–3 stars):
- Acknowledge without admitting fault
- Apologise for their experience
- Offer to resolve offline (provide contact)
- Never be defensive

Flag immediately to the team: any review mentioning legal action, media, or multiple staff complaints.

Goal: 100% response rate within 24 hours. Zero negative reviews left unanswered.""",

    9: """You are {name}, the retention agent for {business_name}.
You keep customers coming back and prevent churn.

Business: {business_name} | Industry: {industry}

Churn detection signals:
- No purchase/visit in {churn_days} days
- Negative WhatsApp sentiment
- Cancelled appointment without rebook

When a customer shows churn signals:
1. Send a warm re-engagement WhatsApp
2. Offer a loyalty reward or exclusive offer
3. If no response in 3 days: escalate to human team

Loyalty stamp system: reward every {loyalty_frequency} purchase/visit.
Win-back sequence: 3-touch campaign (WhatsApp → offer → personal message).

Tone: Warm, personal, never pushy. Like a trusted friend, not a salesperson.""",
}


def generate_system_prompt(module_id: int, agent: dict, profile: dict) -> str:
    """
    Generate a business-specific system prompt for an agent.
    Uses templates for standard modules, falls back to custom for others.
    """
    template = PROMPT_TEMPLATES.get(module_id)
    if not template:
        # For modules without a template, generate one via Claude
        return generate_custom_prompt(agent, profile)

    business_name   = profile.get("business_name", "the business")
    industry        = profile.get("industry", "General")
    services        = ", ".join(profile.get("services", ["our services"]))
    tone            = profile.get("tone", "professional and warm")
    target_customer = profile.get("target_customer", "local businesses and consumers")
    location        = profile.get("location", "UK")

    from lib.first_principles import INDUSTRY_BENCHMARKS
    benchmark = INDUSTRY_BENCHMARKS.get(industry.lower(), INDUSTRY_BENCHMARKS["general"])
    icp_buyer = benchmark.get("icp_decision_maker", "Business Owner")
    icp_size  = benchmark.get("icp_company_size", "5–50 staff")

    return template.format(
        name          = agent.get("name", "Your Agent"),
        business_name = business_name,
        industry      = industry,
        services      = services,
        tone          = tone,
        target_customer = target_customer,
        location      = location,
        icp_buyer     = icp_buyer,
        icp_size      = icp_size,
        business_hours= "Monday to Friday, 9am–6pm",
        churn_days    = 30,
        loyalty_frequency = 5,
    )


def generate_custom_prompt(agent: dict, profile: dict) -> str:
    """Generate a system prompt for a custom or non-templated agent via Claude."""
    import anthropic

    prompt = f"""Write a system prompt for an AI agent with these specs:

Agent: {agent.get('name')} — {agent.get('role')}
Business: {profile.get('business_name')} ({profile.get('industry')})
Services: {', '.join(profile.get('services', []))}
Personality: {agent.get('personality')}
Skills: {', '.join(agent.get('skills', []))}

Write a 100–150 word system prompt that:
1. States the agent's name and role clearly
2. Lists their specific responsibilities for this business
3. Sets tone and escalation rules
4. Defines what a successful outcome looks like

Write ONLY the system prompt text — no JSON, no explanation."""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text.strip()
    except Exception as e:
        print(f"[AgentCreator] Custom prompt error: {e}")
        return f"You are {agent.get('name')}, an AI agent for {profile.get('business_name')}. Your role: {agent.get('role')}. Be professional, helpful, and focused on delivering results."


# ─────────────────────────────────────────────
# CEO ARCHITECT
# The meta-agent that designs the entire team
# ─────────────────────────────────────────────

def run_ceo_architecture(
    business_profile: dict,
    first_principles_assessment: dict,
    client_id: str = None,
) -> dict:
    """
    The CEO Agent as architect.

    Takes the business profile + first principles assessment,
    designs the optimal agent team, generates business-specific configs,
    and returns a complete blueprint ready to provision.

    This is what runs when a new client is onboarded —
    before a single agent is provisioned.

    Returns:
    {
        "team_blueprint": [...],       # Agent specs with system prompts
        "provisioning_order": [...],   # Which agents to spin up first
        "total_monthly_cost": 397,     # Price
        "projected_roi": {...},        # ROI breakdown
        "ceo_brief": "...",            # What the CEO agent would say to the owner
        "gaps_identified": [...],      # Needs not covered by standard modules
        "custom_agents": [...]         # Any custom agents designed
    }
    """
    from lib.agent_factory import generate_team, MODULE_TEMPLATES
    from lib.first_principles import INDUSTRY_BENCHMARKS

    industry  = business_profile.get("industry", "General").lower()
    benchmark = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["general"])

    print(f"[AgentCreator] Running CEO architecture for {business_profile.get('business_name')}...")

    # Step 1: Determine which standard modules to activate
    leverage_points   = first_principles_assessment.get("leverage_points", [])
    primary_module_ids = list(set([
        lp.get("module_id") for lp in leverage_points if lp.get("module_id")
    ]))

    # Always include CEO briefing agent (10)
    if 10 not in primary_module_ids:
        primary_module_ids.append(10)

    # Map to recommended_modules format for agent_factory
    recommended_modules = []
    for mod_id in primary_module_ids:
        priority = "essential" if mod_id in primary_module_ids[:2] else "high"
        recommended_modules.append({"module_id": mod_id, "priority": priority})

    # Step 2: Detect gaps — needs not covered by standard modules
    all_module_ids = list(MODULE_TEMPLATES.keys())
    gaps_found = []

    # Check for niche needs from profile
    profile_text = json.dumps(business_profile).lower()
    gap_checks = {
        "invoice":      "No automated invoice follow-up / payment chasing",
        "tender":       "No tender monitoring and bid preparation system",
        "translation":  "No multilingual customer communication support",
        "inventory":    "No stock/inventory alert and reorder system",
        "compliance":   "No regulatory compliance monitoring agent",
        "hr":           "No recruitment pipeline and candidate tracking",
    }

    for keyword, gap_description in gap_checks.items():
        if keyword in profile_text:
            gaps_found.append(gap_description)

    # Step 3: Design custom agents for gaps not covered
    custom_agents = []
    for gap in gaps_found[:2]:  # Max 2 custom agents
        custom = design_custom_agent(gap, business_profile, primary_module_ids)
        if custom:
            custom_agents.append(custom)
            recommended_modules.append({
                "module_id": custom.get("module_id", 99),
                "priority":  custom.get("priority", "recommended"),
                "custom":    True,
                "spec":      custom,
            })

    # Step 4: Generate the named team
    region = "africa" if any(c in business_profile.get("location", "").lower() for c in [
        "nigeria", "ghana", "kenya", "rwanda", "africa", "lagos", "nairobi", "accra", "kigali"
    ]) else "uk"

    team = generate_team(
        business_profile    = business_profile,
        recommended_modules = recommended_modules,
        region              = region,
        client_id           = client_id or "new_client",
    )

    # Step 5: Generate business-specific system prompts + assign vetted GitHub skills
    from lib.github_skills import get_skills_for_agent, install_skill
    team_blueprint = []
    for agent in team:
        mod_id        = agent.get("module_id", 0)
        system_prompt = generate_system_prompt(mod_id, agent, business_profile)

        # Assign vetted GitHub skills (curated library — no live search on first build)
        vetted_skills = get_skills_for_agent(mod_id, agent.get("role", ""), search_live=False)
        agent_with_skills = dict(agent)
        for skill in vetted_skills[:3]:  # Top 3 per agent
            agent_with_skills = install_skill(agent_with_skills, skill)

        # Record skill metadata for display
        agent_with_skills["github_skills"] = [
            {"name": s["name"], "stars": s.get("stars", 0), "tier": s.get("tier", "standard"),
             "description": s.get("description", ""), "use_case": s.get("use_case", "")}
            for s in vetted_skills[:3]
        ]

        blueprint_agent = {**agent_with_skills, "system_prompt": system_prompt}
        team_blueprint.append(blueprint_agent)

    # Step 6: Define provisioning order (highest ROI first)
    roi_order = {1: 1, 3: 2, 7: 3, 2: 4, 9: 5, 4: 6, 5: 7, 6: 8, 11: 9, 12: 10, 13: 11, 10: 0}
    provisioning_order = sorted(
        [a["module_id"] for a in team_blueprint],
        key=lambda m: roi_order.get(m, 99)
    )

    # Step 7: Calculate total projected ROI
    monthly_enquiries = {"small": 20, "medium": 60, "large": 150}.get(
        business_profile.get("team_size_signal", "small"), 20
    )
    avg_lead_value  = benchmark.get("avg_lead_value_gbp", 500)
    missed_rate     = benchmark.get("missed_lead_rate", 0.30)
    leads_recovered = int(monthly_enquiries * missed_rate)
    revenue_protected = leads_recovered * avg_lead_value
    hours_saved = benchmark.get("admin_hours_week", 10) * 4

    n_agents    = len([a for a in team_blueprint if a.get("module_id") != 10])
    monthly_cost = 397  # Standard plan

    projected_roi = {
        "leads_recovered_monthly":   leads_recovered,
        "revenue_protected_monthly": f"£{revenue_protected:,}",
        "hours_saved_monthly":       hours_saved,
        "monthly_cost":              f"£{monthly_cost}",
        "roi_multiple":              round(revenue_protected / monthly_cost, 1),
        "annual_value":              f"£{revenue_protected * 12:,}",
        "payback_period":            "Week 1",
    }

    # Step 8: Generate the CEO brief (what the CEO agent says to the owner on Day 1)
    ceo_agent = next((a for a in team_blueprint if a.get("is_ceo")), None)
    ceo_name  = ceo_agent["name"] if ceo_agent else "Your Chief of Staff"
    team_names = [a["name"] for a in team_blueprint if not a.get("is_ceo")]

    ceo_brief = (
        f"Good morning. I'm {ceo_name}, your AI Chief of Staff.\n\n"
        f"Your team is live: {', '.join(team_names[:3])}{'...' if len(team_names) > 3 else ''}.\n\n"
        f"Here's what we're solving first:\n"
        f"{first_principles_assessment.get('max_roi_play', '')}\n\n"
        f"I'll brief you every morning on what happened, what needs your attention, "
        f"and what we're doing about it. Message me any time."
    )

    # Named team summary for terminal
    agent_summary = ", ".join(
        f"{a['name']} ({a['title']})" for a in team_blueprint if not a.get("is_ceo")
    )
    ceo_line = next((f"{a['name']} (Chief of Staff)" for a in team_blueprint if a.get("is_ceo")), "")
    print(f"[AgentCreator] Team built for {business_profile.get('business_name')} ✓")
    print(f"  Chief of Staff → {ceo_line}")
    print(f"  Team → {agent_summary}")
    print(f"  ROI projection: {projected_roi['roi_multiple']}x | Revenue protected: {projected_roi['revenue_protected_monthly']}/mo")

    return {
        "team_blueprint":      team_blueprint,
        "provisioning_order":  provisioning_order,
        "total_monthly_cost":  monthly_cost,
        "projected_roi":       projected_roi,
        "ceo_brief":           ceo_brief,
        "gaps_identified":     gaps_found,
        "custom_agents":       custom_agents,
        "region":              region,
        "recommended_modules": recommended_modules,
    }


# ─────────────────────────────────────────────
# ONE-SHOT: BUSINESS → RUNNING AGENT TEAM
# The full pipeline from profile to provisioned team
# ─────────────────────────────────────────────

def build_team_for_business(
    business_profile: dict,
    client_id: str,
    owner_phone: str,
    provision: bool = False,
) -> dict:
    """
    Full pipeline: business profile → first principles → architecture → (optionally) provision.

    This is the "agent that creates agents" in one call.

    business_profile: from website_scanner.scan_business() or manual input
    client_id:        unique ID for this client (Airtable record ID)
    owner_phone:      owner's WhatsApp (e.g. "whatsapp:+447847221722")
    provision:        if True, actually spin up the agents (calls dispatch_client)

    Returns the full architecture + optional provisioning result.
    """
    from lib.first_principles import run_first_principles, run_deep_assessment

    print(f"[AgentCreator] Building team for {business_profile.get('business_name')}...")

    # Layer 1: First principles
    fp_assessment = run_first_principles(business_profile)

    # Layer 2: Deep assessment (Claude-powered — high value prospects)
    readiness = fp_assessment.get("readiness_score", 0)
    if readiness >= 60:
        print(f"[AgentCreator] High readiness ({readiness}) — running deep assessment...")
        deep = run_deep_assessment(business_profile, fp_assessment)
        fp_assessment["deep_insights"] = deep

    # Layer 3: CEO architecture
    architecture = run_ceo_architecture(business_profile, fp_assessment, client_id)

    result = {
        "client_id":        client_id,
        "business_name":    business_profile.get("business_name"),
        "first_principles": fp_assessment,
        "architecture":     architecture,
        "built_at":         datetime.utcnow().isoformat(),
    }

    # Layer 4: Provision (optional — triggers actual agent deployment)
    if provision:
        print(f"[AgentCreator] Provisioning agents...")
        result["provisioning"] = provision_team(
            architecture   = architecture,
            business_profile = business_profile,
            client_id      = client_id,
            owner_phone    = owner_phone,
        )

    return result


def provision_team(
    architecture: dict,
    business_profile: dict,
    client_id: str,
    owner_phone: str,
) -> dict:
    """
    Actually spin up the agent team.
    Calls dispatch_client for each agent in provisioning order.
    """
    from lib.agent_factory import save_team
    from lib.dispatch_client import provision_presence_agent

    team       = architecture["team_blueprint"]
    order      = architecture["provisioning_order"]
    results    = []
    provisioned = 0

    # Save team to factory store
    save_team(client_id, team)

    # Always provision Presence Agent + WhatsApp first (module 1 + 3)
    for mod_id in order[:3]:  # First 3 in priority order
        agent = next((a for a in team if a["module_id"] == mod_id), None)
        if not agent:
            continue

        if mod_id in [1, 3]:
            agent_name = agent.get("name", f"Module {mod_id}")
            agent_title = agent.get("title", "Agent")
            try:
                result = provision_presence_agent(
                    client_id        = client_id,
                    business_name    = business_profile.get("business_name"),
                    industry         = business_profile.get("industry"),
                    services         = business_profile.get("services", []),
                    ceo_phone        = owner_phone,
                    tone             = business_profile.get("tone", "professional and warm"),
                )
                results.append({"agent": agent_name, "role": agent_title, "status": "provisioned", "result": result})
                provisioned += 1
                print(f"[AgentCreator] ✅ {agent_name} ({agent_title}) — live")
            except Exception as e:
                results.append({"agent": agent_name, "role": agent_title, "status": "failed", "error": str(e)})
                print(f"[AgentCreator] ❌ {agent_name} ({agent_title}) — failed: {e}")

    # Send CEO brief to owner
    if owner_phone and architecture.get("ceo_brief"):
        try:
            from lib.whatsapp_agent import send_whatsapp
            wa_phone = owner_phone if owner_phone.startswith("whatsapp:") else f"whatsapp:{owner_phone}"
            send_whatsapp(wa_phone, architecture["ceo_brief"])
            print(f"[AgentCreator] CEO brief sent to {owner_phone}")
        except Exception as e:
            print(f"[AgentCreator] CEO brief send error: {e}")

    return {
        "agents_provisioned": provisioned,
        "results":            results,
        "team_saved":         True,
        "ceo_brief_sent":     bool(owner_phone),
    }


# ─────────────────────────────────────────────
# AGENT CREATOR CLI
# Quick test / demo usage
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Demo: build a team for a hypothetical legal firm
    demo_profile = {
        "business_name":    "Harrington & Associates",
        "industry":         "Legal",
        "location":         "London, UK",
        "services":         ["Corporate Law", "Employment Law", "Commercial Property"],
        "team_size_signal": "small",
        "pain_signals":     ["no 24/7 support", "manual booking", "no WhatsApp"],
        "target_customer":  "SME business owners and senior executives",
        "missed_opportunity": "Losing 35% of after-hours enquiries to competitors who answer first",
        "tone":             "professional",
        "has_whatsapp":     False,
        "has_online_booking": False,
        "has_reviews_section": True,
    }

    print("Running Agent Creator demo...\n")
    result = build_team_for_business(
        business_profile = demo_profile,
        client_id        = "demo_harrington",
        owner_phone      = "+447847221722",
        provision        = False,
    )

    print("\n── First Principles ──")
    fp = result["first_principles"]
    print(f"Readiness Score: {fp['readiness_score']}/100")
    print(f"Max ROI Play: {fp['max_roi_play']}")
    print(f"\nLeverage Points:")
    for lp in fp["leverage_points"]:
        print(f"  → {lp['gap']} | {lp['monthly_value']} | {lp['time_to_roi']}")

    print("\n── Architecture ──")
    arch = result["architecture"]
    print(f"Team: {[a['name'] for a in arch['team_blueprint']]}")
    print(f"ROI: {arch['projected_roi']['roi_multiple']}x | {arch['projected_roi']['revenue_protected_monthly']}/mo protected")
    print(f"\nCEO Brief:\n{arch['ceo_brief']}")
