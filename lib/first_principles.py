"""
lib/first_principles.py — First Principles Business Assessment Engine

When we scan a business, this runs BEFORE agent recommendations.
We think like a strategic consultant, not a feature seller.

Framework:
  1. ICP Definition        — who exactly are their buyers?
  2. Buying Intent Signals — what proves a prospect is ready?
  3. Org Role Mapping      — what human roles do agents replace or amplify?
  4. Revenue Leverage      — where is maximum ROI hiding?
  5. Strategic Play        — the one move that unlocks everything else
  6. Agent Blueprint       — which agents, in what order, for what reason

Output powers:
  - Business Scan results (dashboard)
  - Agent Creator (which agents to build)
  - CEO Agent briefings (business-specific intel)
  - Sales proposal (personalised pitch)
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


# ─────────────────────────────────────────────
# INDUSTRY BENCHMARKS
# Used to anchor ROI estimates in real data
# ─────────────────────────────────────────────

INDUSTRY_BENCHMARKS = {
    "legal": {
        "avg_lead_value_gbp":   800,
        "missed_lead_rate":     0.35,
        "admin_hours_week":     15,
        "review_impact_score":  "high",
        "primary_channel":      "phone + email",
        "peak_loss_window":     "after 6pm and weekends",
        "icp_decision_maker":   "Managing Partner / Partner",
        "icp_company_size":     "5–50 staff",
        "common_pain":          "Partners doing admin. Leads falling through after hours.",
        "quick_win":            "Presence Agent covers after-hours — ROI in week 1",
    },
    "real estate": {
        "avg_lead_value_gbp":   1200,
        "missed_lead_rate":     0.40,
        "admin_hours_week":     18,
        "review_impact_score":  "very high",
        "primary_channel":      "portals + WhatsApp",
        "peak_loss_window":     "evenings and weekends (when buyers browse)",
        "icp_decision_maker":   "Director / Senior Negotiator",
        "icp_company_size":     "3–30 staff",
        "common_pain":          "Rightmove leads not followed up fast enough. Competitors call first.",
        "quick_win":            "Presence + WhatsApp Agent — instant response beats competitors",
    },
    "healthcare": {
        "avg_lead_value_gbp":   300,
        "missed_lead_rate":     0.30,
        "admin_hours_week":     12,
        "review_impact_score":  "very high",
        "primary_channel":      "phone + online booking",
        "peak_loss_window":     "out of hours and during consultations",
        "icp_decision_maker":   "Clinic Manager / Practice Owner",
        "icp_company_size":     "2–20 staff",
        "common_pain":          "Phone lines busy during appointments. Patients go elsewhere.",
        "quick_win":            "Presence Agent + online booking — no more missed appointments",
    },
    "restaurant": {
        "avg_lead_value_gbp":   80,
        "missed_lead_rate":     0.25,
        "admin_hours_week":     8,
        "review_impact_score":  "critical",
        "primary_channel":      "Google + Instagram + phone",
        "peak_loss_window":     "lunch rush and evenings",
        "icp_decision_maker":   "Owner / Manager",
        "icp_company_size":     "5–50 staff",
        "common_pain":          "Bad reviews unanswered. Reservations lost when phone busy.",
        "quick_win":            "Reviews Agent + WhatsApp reservations — protect reputation first",
    },
    "construction": {
        "avg_lead_value_gbp":   2500,
        "missed_lead_rate":     0.30,
        "admin_hours_week":     10,
        "review_impact_score":  "high",
        "primary_channel":      "referrals + Google",
        "peak_loss_window":     "site hours (can't answer phone on site)",
        "icp_decision_maker":   "MD / Contracts Manager",
        "icp_company_size":     "5–100 staff",
        "common_pain":          "Missing calls while on site. Quoting process slow. Competitors undercutting.",
        "quick_win":            "Presence Agent — never miss a £10k+ project enquiry while on site",
    },
    "logistics": {
        "avg_lead_value_gbp":   1500,
        "missed_lead_rate":     0.25,
        "admin_hours_week":     12,
        "review_impact_score":  "medium",
        "primary_channel":      "email + phone + trade platforms",
        "peak_loss_window":     "early morning dispatch windows",
        "icp_decision_maker":   "Operations Manager / MD",
        "icp_company_size":     "10–200 staff",
        "common_pain":          "Manual tracking updates. Clients calling for status. Missed trade opportunities.",
        "quick_win":            "Market Scout + TradeBridge — find the loads before competitors do",
    },
    "consulting": {
        "avg_lead_value_gbp":   1000,
        "missed_lead_rate":     0.35,
        "admin_hours_week":     15,
        "review_impact_score":  "medium",
        "primary_channel":      "LinkedIn + referrals",
        "peak_loss_window":     "between client engagements (BD neglect)",
        "icp_decision_maker":   "C-Suite / VP / Director",
        "icp_company_size":     "varies — target £5M+ revenue businesses",
        "common_pain":          "BD falls off during delivery. No content presence. Referrals drying up.",
        "quick_win":            "Lead Gen + Content Machine — pipeline never dries up again",
    },
    "retail": {
        "avg_lead_value_gbp":   150,
        "missed_lead_rate":     0.20,
        "admin_hours_week":     8,
        "review_impact_score":  "high",
        "primary_channel":      "Google + Instagram + walk-in",
        "peak_loss_window":     "weekend browsing online",
        "icp_decision_maker":   "Owner / Store Manager",
        "icp_company_size":     "1–30 staff",
        "common_pain":          "Loyalty falling. Online reviews mixed. Instagram not converting.",
        "quick_win":            "Retention Agent — loyalty stamps and win-back sequences pay immediately",
    },
    "general": {
        "avg_lead_value_gbp":   500,
        "missed_lead_rate":     0.30,
        "admin_hours_week":     10,
        "review_impact_score":  "medium",
        "primary_channel":      "phone + web",
        "peak_loss_window":     "out of hours",
        "icp_decision_maker":   "Business Owner / Director",
        "icp_company_size":     "5–50 staff",
        "common_pain":          "Wearing too many hats. Leads not followed up. No systems.",
        "quick_win":            "Presence Agent — instant leverage with zero headcount",
    },
}


# ─────────────────────────────────────────────
# BUYING INTENT SIGNAL DETECTOR
# Reads pain signals from the profile and maps them to
# concrete buying intent evidence
# ─────────────────────────────────────────────

INTENT_SIGNAL_MAP = {
    "no 24/7 support":           {"signal": "Losing leads out of hours — high urgency", "strength": "strong"},
    "manual booking":            {"signal": "Admin bottleneck — paying for human time", "strength": "strong"},
    "no whatsapp":               {"signal": "Missing the #1 SME customer channel", "strength": "strong"},
    "no live chat":              {"signal": "Website visitors bouncing silently", "strength": "medium"},
    "no reviews shown":          {"signal": "Social proof gap — losing trust-based decisions", "strength": "medium"},
    "bad reviews":               {"signal": "Reputation bleeding — immediate damage control needed", "strength": "urgent"},
    "no crm":                    {"signal": "Leads falling through cracks with no tracking", "strength": "strong"},
    "manual lead handling":      {"signal": "Scaling is impossible — bottleneck is human capacity", "strength": "strong"},
    "no content presence":       {"signal": "Invisible online — competitors stealing mindshare", "strength": "medium"},
    "no email list":             {"signal": "No owned audience — dependent on paid channels", "strength": "medium"},
    "job posting for receptionist": {"signal": "About to pay £25k/yr for what AI does for £400/mo", "strength": "urgent"},
    "job posting for admin":     {"signal": "Scaling with headcount — AI is 10x cheaper", "strength": "urgent"},
    "high volume enquiries":     {"signal": "Revenue ceiling is staff capacity, not demand", "strength": "strong"},
    "competitor growing":        {"signal": "Market moving — urgency to act now", "strength": "medium"},
    "export":                    {"signal": "Africa/global trade play — TradeBridge opportunity", "strength": "medium"},
    "africa":                    {"signal": "WhatsApp-first market — different playbook needed", "strength": "strong"},
}


def detect_intent_signals(profile: dict) -> list[dict]:
    """
    Map pain signals from the profile to buying intent evidence.
    Returns list of {signal, strength, implication} dicts.
    """
    pain_signals = [p.lower() for p in profile.get("pain_signals", [])]
    detected = []

    for keyword, intent in INTENT_SIGNAL_MAP.items():
        if any(keyword in p for p in pain_signals):
            detected.append({
                "keyword":     keyword,
                "signal":      intent["signal"],
                "strength":    intent["strength"],
                "implication": f"This business is {'urgently' if intent['strength'] == 'urgent' else 'clearly'} ready to pay for a solution.",
            })

    # Always add general signals based on what's missing
    if not profile.get("has_whatsapp"):
        detected.append({
            "keyword":     "missing whatsapp",
            "signal":      "No WhatsApp presence in a WhatsApp-first market",
            "strength":    "strong",
            "implication": "Their customers are trying to reach them on WhatsApp and failing.",
        })
    if not profile.get("has_online_booking"):
        detected.append({
            "keyword":     "no online booking",
            "signal":      "100% of bookings require human intervention",
            "strength":    "medium",
            "implication": "Every appointment is a potential missed opportunity if staff are busy.",
        })

    # Sort: urgent → strong → medium
    order = {"urgent": 0, "strong": 1, "medium": 2}
    detected.sort(key=lambda x: order.get(x["strength"], 3))

    return detected[:5]  # Top 5 signals


# ─────────────────────────────────────────────
# ICP DEFINER
# Who exactly are their buyers?
# ─────────────────────────────────────────────

def define_icp(profile: dict, benchmark: dict) -> dict:
    """
    Define the Ideal Customer Profile for this business
    and the ICP for who THEY should be targeting with agents.
    """
    industry  = profile.get("industry", "General").lower()
    location  = profile.get("location", "")
    size      = profile.get("team_size_signal", "small")
    services  = profile.get("services", [])

    # Who are THEIR customers (who the agents will talk to)
    customer_icp = {
        "who":          profile.get("target_customer", "local businesses and consumers"),
        "channel":      benchmark.get("primary_channel", "phone + web"),
        "peak_time":    benchmark.get("peak_loss_window", "out of hours"),
        "decision_trigger": "Need + trust signal (reviews/presence) + speed of response",
        "lost_to":      "Competitors who answer faster, or they give up entirely",
    }

    # Who WE should pitch (who is the buyer of PluggedIN)
    pluggedin_icp = {
        "decision_maker": benchmark.get("icp_decision_maker", "Business Owner"),
        "company_size":   benchmark.get("icp_company_size", "5–50 staff"),
        "pain_threshold": f"Losing {int(benchmark.get('missed_lead_rate', 0.30) * 100)}%+ of leads",
        "budget_signal":  f"Already paying staff to do what agents do. £{benchmark.get('admin_hours_week', 10) * 15 * 4:,}/mo in admin cost alone.",
        "urgency_trigger": benchmark.get("common_pain", "Wearing too many hats"),
        "location":       location or "UK / West Africa",
        "tech_maturity":  "Low to medium — looking for simple, not complex",
    }

    return {
        "their_customer": customer_icp,
        "our_buyer":      pluggedin_icp,
    }


# ─────────────────────────────────────────────
# ORG ROLE MAPPER
# What human roles do agents replace or amplify?
# ─────────────────────────────────────────────

ROLE_TO_MODULE = {
    "Receptionist":        {"module_id": 1,  "cost_gbp_month": 1800, "agent_cost": 397, "saving": "£1,403/mo"},
    "Admin Assistant":     {"module_id": 1,  "cost_gbp_month": 1600, "agent_cost": 397, "saving": "£1,203/mo"},
    "Sales/BD Rep":        {"module_id": 2,  "cost_gbp_month": 2500, "agent_cost": 397, "saving": "£2,103/mo"},
    "Social Media Manager":{"module_id": 4,  "cost_gbp_month": 2000, "agent_cost": 397, "saving": "£1,603/mo"},
    "Marketing Manager":   {"module_id": 4,  "cost_gbp_month": 2800, "agent_cost": 397, "saving": "£2,403/mo"},
    "Customer Service Rep":{"module_id": 3,  "cost_gbp_month": 1700, "agent_cost": 397, "saving": "£1,303/mo"},
    "Market Analyst":      {"module_id": 6,  "cost_gbp_month": 3000, "agent_cost": 397, "saving": "£2,603/mo"},
    "Reputation Manager":  {"module_id": 7,  "cost_gbp_month": 1500, "agent_cost": 397, "saving": "£1,103/mo"},
    "Recruiter":           {"module_id": 8,  "cost_gbp_month": 2500, "agent_cost": 397, "saving": "£2,103/mo"},
    "Loyalty/CRM Manager": {"module_id": 9,  "cost_gbp_month": 2000, "agent_cost": 397, "saving": "£1,603/mo"},
    "Trade Broker":        {"module_id": 11, "cost_gbp_month": 3500, "agent_cost": 397, "saving": "£3,103/mo"},
    "Creative Director":   {"module_id": 12, "cost_gbp_month": 3500, "agent_cost": 397, "saving": "£3,103/mo"},
}

INDUSTRY_ROLES = {
    "legal":        ["Receptionist", "Admin Assistant", "Marketing Manager"],
    "real estate":  ["Receptionist", "Customer Service Rep", "Social Media Manager"],
    "healthcare":   ["Receptionist", "Admin Assistant", "Customer Service Rep"],
    "restaurant":   ["Customer Service Rep", "Social Media Manager", "Reputation Manager"],
    "construction": ["Receptionist", "Sales/BD Rep", "Market Analyst"],
    "logistics":    ["Customer Service Rep", "Market Analyst", "Trade Broker"],
    "consulting":   ["Sales/BD Rep", "Marketing Manager", "Creative Director"],
    "retail":       ["Customer Service Rep", "Social Media Manager", "Loyalty/CRM Manager"],
    "general":      ["Receptionist", "Admin Assistant", "Sales/BD Rep"],
}


def map_org_roles(profile: dict) -> list[dict]:
    """
    Map the roles this business likely has (or needs) to the agents that replace them.
    Returns a list of role → agent mappings with cost comparison.
    """
    industry = profile.get("industry", "General").lower()
    roles    = INDUSTRY_ROLES.get(industry, INDUSTRY_ROLES["general"])

    mapped = []
    for role_name in roles:
        role_data = ROLE_TO_MODULE.get(role_name)
        if role_data:
            mapped.append({
                "human_role":    role_name,
                "module_id":     role_data["module_id"],
                "human_cost":    f"£{role_data['cost_gbp_month']:,}/mo",
                "agent_cost":    f"£{role_data['agent_cost']}/mo",
                "monthly_saving": role_data["saving"],
                "leverage":      f"Agent works 24/7, never calls in sick, handles {10 if role_data['module_id'] in [1,3] else 5}x the volume",
            })

    return mapped


# ─────────────────────────────────────────────
# REVENUE LEVERAGE IDENTIFIER
# Where is the money hiding?
# ─────────────────────────────────────────────

def identify_leverage_points(profile: dict, benchmark: dict) -> list[dict]:
    """
    Identify the specific revenue leverage points for this business.
    Each point has a gap, an agent solution, and a monetised impact.
    """
    industry         = profile.get("industry", "General").lower()
    size             = profile.get("team_size_signal", "small")
    avg_lead_value   = benchmark.get("avg_lead_value_gbp", 500)
    missed_rate      = benchmark.get("missed_lead_rate", 0.30)
    admin_hours_week = benchmark.get("admin_hours_week", 10)

    monthly_enquiries = {"small": 20, "medium": 60, "large": 150}.get(size, 20)
    leads_lost        = int(monthly_enquiries * missed_rate)
    revenue_lost      = leads_lost * avg_lead_value
    admin_cost_month  = admin_hours_week * 4 * 15  # £15/hr assumption

    leverage_points = []

    # Always: after-hours lead loss
    leverage_points.append({
        "gap":          f"~{leads_lost} leads/month lost {benchmark.get('peak_loss_window', 'after hours')}",
        "root_cause":   "No one available to respond. Prospect moves to next option.",
        "agent":        "Presence Agent (Module 1)",
        "monthly_value": f"£{revenue_lost:,}",
        "confidence":   "high",
        "time_to_roi":  "Week 1",
        "module_id":    1,
    })

    # Admin burden
    leverage_points.append({
        "gap":          f"£{admin_cost_month:,}/mo spent on admin that agents do automatically",
        "root_cause":   "Manual booking, follow-up, and qualification eating staff hours.",
        "agent":        "WhatsApp Assistant (Module 3)",
        "monthly_value": f"£{admin_cost_month:,} saved",
        "confidence":   "high",
        "time_to_roi":  "Month 1",
        "module_id":    3,
    })

    # Industry-specific
    if industry in ["legal", "real estate", "healthcare", "construction"]:
        leverage_points.append({
            "gap":          "No proactive lead generation — pipeline depends on referrals only",
            "root_cause":   "No systematic outbound. BD is reactive, not proactive.",
            "agent":        "Lead Generation Agent (Module 2)",
            "monthly_value": f"£{int(avg_lead_value * 3):,}+ from new pipeline",
            "confidence":   "medium",
            "time_to_roi":  "Month 2–3",
            "module_id":    2,
        })

    if profile.get("has_reviews_section") is False or industry in ["restaurant", "healthcare", "retail"]:
        leverage_points.append({
            "gap":          "Online reputation not actively managed — losing trust-based decisions",
            "root_cause":   "Reviews go unanswered. Negative ones dominate search impression.",
            "agent":        "Reviews Agent (Module 7)",
            "monthly_value": f"£{int(monthly_enquiries * avg_lead_value * 0.10):,} in protected revenue",
            "confidence":   "medium",
            "time_to_roi":  "Month 1",
            "module_id":    7,
        })

    if industry in ["logistics", "construction", "consulting"]:
        leverage_points.append({
            "gap":          "No content presence — invisible to ideal clients searching online",
            "root_cause":   "BD is people-dependent. When people are busy, content stops.",
            "agent":        "Content Machine (Module 4)",
            "monthly_value": "2–3 inbound leads/month from owned content",
            "confidence":   "medium",
            "time_to_roi":  "Month 3",
            "module_id":    4,
        })

    # Sort by confidence then time_to_roi
    order = {"high": 0, "medium": 1, "low": 2}
    leverage_points.sort(key=lambda x: order.get(x["confidence"], 2))

    return leverage_points[:4]


# ─────────────────────────────────────────────
# STRATEGIC MAXIMUM ROI PLAY
# The one move that unlocks the most value
# ─────────────────────────────────────────────

def determine_max_roi_play(profile: dict, leverage_points: list, benchmark: dict) -> str:
    """
    Determine the single most impactful play for this business.
    This is the opener in the pitch — the moment that lands.
    """
    industry     = profile.get("industry", "General").lower()
    business_name = profile.get("business_name", "this business")
    top_leverage  = leverage_points[0] if leverage_points else {}

    plays = {
        "legal":       f"Install the Presence Agent this week. Every missed call after 6pm is a potential £{benchmark.get('avg_lead_value_gbp', 800):,} case going to a competitor. {business_name} is leaking revenue every evening and weekend.",
        "real estate": f"The fastest-responding agent wins the lead in property. {business_name} needs to be first — not second — on every Rightmove and WhatsApp enquiry. One Presence Agent pays for itself with a single transaction.",
        "healthcare":  f"Patients who can't get through will book elsewhere. {business_name} needs a 24/7 front desk that never puts anyone on hold. The Presence Agent covers every consultation slot, every evening.",
        "restaurant":  f"A single bad review without a response costs {business_name} 10 bookings. Install the Reviews Agent first — protect the reputation, then build. The Retention Agent keeps regulars coming back automatically.",
        "construction":f"{business_name}'s team is on site — they can't answer phones. Every missed call is a missed project worth £{benchmark.get('avg_lead_value_gbp', 2500):,}+. The Presence Agent answers, qualifies, and books the quote automatically.",
        "logistics":   f"{business_name} is competing on speed and relationships. Market Scout surfaces loads and trade deals before competitors see them. TradeBridge turns connections into commission. This is a revenue line, not a cost.",
        "consulting":  f"{business_name}'s pipeline dries up during delivery. Lead Gen + Content Machine run BD on autopilot — so when one engagement ends, the next is already qualified and warm.",
        "retail":      f"Customer acquisition costs 5x more than retention. {business_name}'s loyalty programme should run on autopilot — stamps, win-backs, re-engagement. The Retention Agent pays for itself in the first month.",
    }

    return plays.get(industry, (
        f"{business_name} is leaving money on the table every hour staff aren't available. "
        f"The Presence Agent recovers {top_leverage.get('monthly_value', '£3,000+')} in lost leads per month — "
        f"that's the first move. Everything else compounds from there."
    ))


# ─────────────────────────────────────────────
# FULL FIRST PRINCIPLES ASSESSMENT
# The complete strategic picture
# ─────────────────────────────────────────────

def run_first_principles(profile: dict) -> dict:
    """
    Full first principles assessment for a business profile.
    This is the strategic layer that sits above module recommendations.

    Returns:
    {
        "icp":              {...},
        "intent_signals":   [...],
        "org_role_map":     [...],
        "leverage_points":  [...],
        "max_roi_play":     "...",
        "readiness_score":  0–100,
        "recommended_entry_point": {module_id, name, reason}
    }
    """
    industry  = profile.get("industry", "General").lower()
    benchmark = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["general"])

    # Run each analysis layer
    icp            = define_icp(profile, benchmark)
    intent_signals = detect_intent_signals(profile)
    role_map       = map_org_roles(profile)
    leverage       = identify_leverage_points(profile, benchmark)
    max_play       = determine_max_roi_play(profile, leverage, benchmark)

    # Score readiness to buy (0–100)
    urgency_weights = {"urgent": 30, "strong": 15, "medium": 8}
    raw_score = sum(urgency_weights.get(s["strength"], 0) for s in intent_signals)
    readiness = min(100, raw_score + 20)  # +20 baseline for any business that got scanned

    # Recommend the entry point (lowest friction, fastest ROI)
    entry = leverage[0] if leverage else {"module_id": 1, "agent": "Presence Agent"}
    entry_point = {
        "module_id": entry.get("module_id", 1),
        "name":      entry.get("agent", "Presence Agent"),
        "reason":    entry.get("gap", "Fastest path to ROI"),
        "time_to_roi": entry.get("time_to_roi", "Week 1"),
    }

    return {
        "icp":                    icp,
        "intent_signals":         intent_signals,
        "org_role_map":           role_map,
        "leverage_points":        leverage,
        "max_roi_play":           max_play,
        "readiness_score":        readiness,
        "recommended_entry_point": entry_point,
        "benchmark":              {
            "avg_lead_value":     f"£{benchmark['avg_lead_value_gbp']:,}",
            "missed_lead_rate":   f"{int(benchmark['missed_lead_rate'] * 100)}%",
            "admin_hours_week":   f"{benchmark['admin_hours_week']} hrs/week",
            "quick_win":          benchmark["quick_win"],
        },
    }


# ─────────────────────────────────────────────
# CLAUDE-ENHANCED ASSESSMENT
# When we want deeper insight than the rule-based analysis
# ─────────────────────────────────────────────

def run_deep_assessment(profile: dict, first_principles: dict) -> dict:
    """
    Optional: Use Claude Sonnet to produce a deeper, more nuanced assessment.
    Supplements the rule-based analysis with qualitative reasoning.
    Called when high-value prospects justify the extra API call.
    """
    import anthropic

    profile_json     = json.dumps(profile, indent=2)
    principles_json  = json.dumps(first_principles, indent=2)

    prompt = f"""You are a senior AI consultant doing a first principles analysis for a PluggedIN AI agency pitch.

Business Profile:
{profile_json}

Initial Analysis:
{principles_json}

Your task: Go deeper. Think from first principles about this specific business.

Return a JSON object:
{{
  "strategic_insight": "The one thing about this business that changes the entire approach — what most people would miss",
  "icp_refinement": "Specific refinement of who their ideal customer is — more precise than the initial analysis",
  "hidden_leverage": "A leverage point not obvious from the surface — a second-order opportunity",
  "objection_preempt": "The most likely objection from the decision-maker and how to pre-empt it",
  "competitive_moat": "How AI agents create a moat for this business specifically — not generic",
  "week_1_action": "The single most impactful action in week 1 — specific to this business",
  "6_month_vision": "What this business looks like in 6 months with the full agent stack running"
}}

Be specific, direct, and bold. Reference their industry, services, and pain signals. No generic advice.
Return ONLY valid JSON."""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"[FirstPrinciples] Deep assessment error: {e}")
        return {
            "strategic_insight": first_principles.get("max_roi_play", ""),
            "week_1_action":     first_principles.get("recommended_entry_point", {}).get("reason", ""),
            "6_month_vision":    "Full agent stack running — lead gen, qualification, content, retention all on autopilot.",
        }
