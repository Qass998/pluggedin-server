"""
lib/icp_gate.py — ICP Confidence Scoring and Gating

Two-stage gate:
  Stage 1 — Score 0-100 across 4 dimensions
  Stage 2 — Gate: <60 discard | 60-79 manual review | ≥80 auto-advance

Pattern from: github.com/eracle/OpenOutreach (confidence gating)
Adapted for: PluggedIN ICP (5-50 staff, Legal/Professional Services/Recruitment, UK/Africa)
"""
from __future__ import annotations
import os
import json
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

AUTO_ADVANCE_THRESHOLD  = 80
MANUAL_REVIEW_THRESHOLD = 60

ICP_TARGETS = {
    "industries":  ["Legal", "Recruitment", "Professional Services", "Healthcare", "Construction",
                    "Logistics", "Real Estate", "Consulting", "Restaurant", "Retail"],
    "size":        {"min": 5, "max": 50},
    "roles":       ["Owner", "Director", "Partner", "Founder", "CEO", "MD", "Manager"],
    "geographies": ["UK", "Nigeria", "Ghana", "Kenya", "Rwanda", "Ireland"],
}


# ─────────────────────────────────────────────
# RULE-BASED SCORER (fast, no API cost)
# ─────────────────────────────────────────────

def score_lead(lead: dict) -> dict:
    """
    Score a lead 0-100 across 4 dimensions.
    Uses rule-based scoring — no API call.

    lead dict keys (any subset):
      industry, employee_count, role, location, signal_type, signal_detail,
      has_website, has_linkedin, has_reviews, technologies
    """
    industry_fit    = _score_industry(lead)
    size_fit        = _score_size(lead)
    role_fit        = _score_role(lead)
    signal_strength = _score_signal(lead)

    total = industry_fit + size_fit + role_fit + signal_strength

    return {
        "total":           total,
        "industry_fit":    industry_fit,
        "size_fit":        size_fit,
        "role_fit":        role_fit,
        "signal_strength": signal_strength,
        "gate":            _gate(total),
        "reasoning":       _build_reasoning(lead, industry_fit, size_fit, role_fit, signal_strength),
    }


def _score_industry(lead: dict) -> int:
    industry = (lead.get("industry") or lead.get("Industry") or "").lower()
    if not industry:
        return 10  # unknown — give benefit of doubt
    for t in ICP_TARGETS["industries"]:
        if t.lower() in industry:
            return 25
    return 0


def _score_size(lead: dict) -> int:
    count = lead.get("employee_count") or lead.get("Employees") or lead.get("Size")
    if count is None:
        return 12  # unknown

    try:
        n = int(str(count).replace("+","").replace(",","").strip().split("-")[0])
    except (ValueError, IndexError):
        return 12

    lo, hi = ICP_TARGETS["size"]["min"], ICP_TARGETS["size"]["max"]
    if lo <= n <= hi:
        return 25
    if n < lo or n > hi * 2:
        return 5
    return 12  # close but outside range


def _score_role(lead: dict) -> int:
    role = (lead.get("role") or lead.get("Role") or lead.get("Title") or lead.get("Job Title") or "").lower()
    if not role:
        return 10
    for r in ICP_TARGETS["roles"]:
        if r.lower() in role:
            return 25
    # Influencer roles
    if any(w in role for w in ["head of", "senior", "lead", "vp", "vice"]):
        return 15
    return 5


def _score_signal(lead: dict) -> int:
    signal = (lead.get("signal_type") or lead.get("Signal") or "").lower()
    detail = (lead.get("signal_detail") or "").lower()

    # Strong signals
    if any(s in signal for s in ["hiring", "job posting", "funding", "expansion"]):
        return 25
    if any(s in signal for s in ["bad review", "complaint", "negative review"]):
        return 20
    if any(s in signal for s in ["leadership change", "new cto", "new ceo"]):
        return 20
    # Medium signals
    if any(s in signal for s in ["news", "award", "event", "conference"]):
        return 15
    # Weak — we found them but no trigger
    if lead.get("has_website") or lead.get("has_linkedin"):
        return 10
    return 5


def _gate(score: int) -> str:
    if score >= AUTO_ADVANCE_THRESHOLD:
        return "auto"
    if score >= MANUAL_REVIEW_THRESHOLD:
        return "review"
    return "discard"


def _build_reasoning(lead, ind, siz, rol, sig) -> str:
    parts = []
    if ind == 25:
        parts.append(f"strong industry fit ({lead.get('industry','?')})")
    elif ind == 0:
        parts.append("industry not in ICP")
    if siz == 25:
        parts.append("ideal company size")
    elif siz == 5:
        parts.append("company size outside ICP range")
    if rol == 25:
        parts.append("decision maker role")
    elif rol == 5:
        parts.append("role unlikely to be decision maker")
    if sig >= 20:
        parts.append(f"strong signal: {lead.get('signal_type','?')}")
    elif sig <= 5:
        parts.append("no intent signal")
    return "; ".join(parts) if parts else "standard scoring"


# ─────────────────────────────────────────────
# AI-ENHANCED SCORER (uses Claude for nuanced cases)
# ─────────────────────────────────────────────

_AI_SCORE_PROMPT = """Score this prospect against the PluggedIN ICP.

ICP criteria:
- Industry: Legal, Recruitment, Professional Services, Healthcare, Construction, Logistics
- Size: 5-50 staff (owner-led)
- Role: Owner, Director, Partner, Founder, CEO, MD
- Pain: Manual processes, missed leads, no automation, high staff costs
- Geography: UK, West Africa

Prospect data:
{lead_json}

Return JSON only:
{{
  "total":           0-100,
  "industry_fit":    0-25,
  "size_fit":        0-25,
  "role_fit":        0-25,
  "signal_strength": 0-25,
  "gate":            "auto | review | discard",
  "reasoning":       "one sentence"
}}"""


def score_lead_ai(lead: dict) -> dict:
    """
    AI-enhanced scoring for leads with rich text fields (LinkedIn bio, company description).
    Falls back to rule-based if API unavailable.
    """
    rule_score = score_lead(lead)

    if not ANTHROPIC_API_KEY:
        return rule_score

    # Only use AI for borderline cases (55-85 range) — saves tokens
    if rule_score["total"] < 55 or rule_score["total"] > 85:
        return rule_score

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": _AI_SCORE_PROMPT.format(
                lead_json=json.dumps({k: v for k, v in lead.items() if v}, indent=2)[:1500]
            )}],
        )
        raw  = resp.content[0].text.strip().replace("```json","").replace("```","")
        data = json.loads(raw)
        data["gate"] = _gate(data.get("total", 0))
        return data
    except Exception as e:
        print(f"[ICPGate] AI score error: {e}")
        return rule_score


# ─────────────────────────────────────────────
# GATE DECISION
# ─────────────────────────────────────────────

def gate_lead(lead_id: str, lead: dict, use_ai: bool = False) -> dict:
    """
    Score a lead and apply the gate. Updates Airtable and returns the decision.
    Returns: {"gate": "auto|review|discard", "score": {...}, "stage": "READY|QUALIFIED|FAILED"}
    """
    score  = score_lead_ai(lead) if use_ai else score_lead(lead)
    gate   = score["gate"]

    from lib.pipeline_state import qualify_lead
    stage = qualify_lead(lead_id, score["total"], auto_advance=(gate == "auto"))

    print(f"[ICPGate] {lead.get('Name') or lead.get('Company','?')} — score {score['total']} ({gate}) → {stage}")
    return {"gate": gate, "score": score, "stage": stage}
