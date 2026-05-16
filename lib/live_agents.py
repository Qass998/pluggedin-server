"""
lib/live_agents.py — PluggedIN Live: In-House Agent Runner

Runs PluggedIN's OWN businesses autonomously.
Called by APScheduler daily and by /live/run/{agent_id} endpoints.

Agents:
  opportunity_engine   — scans all sources, scores niches 0-100, escalates ≥70
  digital_products     — daily ecommerce/digital product intelligence
  lead_gen             — finds + outreaches SME prospects for PluggedIN pipeline
  agritrade            — matches African commodity buyers/sellers
  creator_outreach     — micro-influencer outreach for active products
  market_scout         — Reddit/HN/TradeKey signals (free)
  knowledge            — knowledge acquisition from YouTube/Reddit/blogs

All results log to Airtable and surface in /results/* endpoints.
"""
from __future__ import annotations
import os
import json
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("live_agents")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
_OPPORTUNITY_SCORE_THRESHOLD = 70


# ─────────────────────────────────────────────────────────────────────────────
# OPPORTUNITY ENGINE
# Scans all market sources, scores each niche 0-100.
# Anything ≥70 goes into the briefing for Qassim.
# ─────────────────────────────────────────────────────────────────────────────

def run_opportunity_engine(dry_run: bool = False) -> dict:
    """
    Full opportunity scan:
    1. Market scout (Reddit/HN/TradeKey) for trade signals
    2. Product intelligence for ecommerce demand signals
    3. Claude scores and ranks everything
    4. Logs to Airtable, returns briefing dict
    """
    log.info("[OpportunityEngine] Starting daily scan")
    results = {
        "agent": "opportunity_engine",
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "market_signals": [],
        "product_signals": [],
        "top_opportunities": [],
        "briefing": "",
        "ok": False,
    }

    # 1. Market Scout — free, no API key needed
    try:
        from lib.market_scout import run_scout
        scout_data = run_scout(topic_key=None, source="all", log_airtable=not dry_run)
        signals = scout_data.get("signals", []) if isinstance(scout_data, dict) else []
        results["market_signals"] = signals[:20]
        log.info(f"[OpportunityEngine] Market scout: {len(signals)} signals")
    except Exception as e:
        log.error(f"[OpportunityEngine] Market scout failed: {e}")

    # 2. Product Intelligence — digital/ecom products
    try:
        from lib.product_intelligence import run_daily_product_intelligence
        prod_data = run_daily_product_intelligence(dry_run=dry_run)
        high = prod_data.get("high_tier", [])
        medium = prod_data.get("medium_tier", [])
        results["product_signals"] = high + medium[:5]
        log.info(f"[OpportunityEngine] Product scan: {len(high)} high-tier, {len(medium)} medium")
    except Exception as e:
        log.error(f"[OpportunityEngine] Product intelligence failed: {e}")

    # 3. Score and rank with Claude
    if ANTHROPIC_API_KEY and (results["market_signals"] or results["product_signals"]):
        try:
            results["top_opportunities"] = _score_opportunities_with_claude(
                results["market_signals"], results["product_signals"]
            )
        except Exception as e:
            log.error(f"[OpportunityEngine] Claude scoring failed: {e}")
            results["top_opportunities"] = _fallback_rank(results["product_signals"])

    # 4. Build briefing
    top = [o for o in results["top_opportunities"] if o.get("score", 0) >= _OPPORTUNITY_SCORE_THRESHOLD]
    results["briefing"] = _build_opportunity_briefing(top)
    results["ok"] = True

    # 5. Log to Airtable
    if not dry_run:
        _log_opportunities_to_airtable(results["top_opportunities"])

    log.info(f"[OpportunityEngine] Done — {len(top)} opportunities scored ≥{_OPPORTUNITY_SCORE_THRESHOLD}")
    return results


def _score_opportunities_with_claude(market_signals: list, product_signals: list) -> list:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are the PluggedIN Opportunity Engine. Score these market signals and product opportunities.

MARKET SIGNALS (from Reddit/HN/TradeKey):
{json.dumps(market_signals[:10], indent=2)[:2000]}

PRODUCT OPPORTUNITIES (from Amazon/TikTok/Meta):
{json.dumps(product_signals[:10], indent=2)[:2000]}

Score each distinct opportunity 0-100 using these dimensions (20pts each):
1. Demand signal strength (multiple platforms = 20, single = 10)
2. Competition level (emerging niche = 20, saturated = 5)
3. Margin potential (digital/lead gen = 20, commodity = 5)
4. Agent buildability with PluggedIN stack (fully automatable = 20)
5. Speed to first revenue (7 days = 20, 90+ days = 5)

Return JSON array (top 5 only):
[{{"name":"opportunity name","score":0-100,"type":"ecom|digital|lead_gen|trade|content","margin_model":"how we make money","speed":"days to first revenue","reasoning":"2 sentences"}}]

Return ONLY valid JSON."""

    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip().replace("```json", "").replace("```", "")
    return json.loads(raw)


def _fallback_rank(product_signals: list) -> list:
    return [
        {
            "name": s.get("keyword", "Unknown"),
            "score": s.get("score", 50),
            "type": "ecom",
            "margin_model": "Dropshipping or digital equivalent",
            "speed": "30 days",
            "reasoning": "Rule-based scoring (Claude unavailable)",
        }
        for s in product_signals[:5]
    ]


def _build_opportunity_briefing(top: list) -> str:
    if not top:
        return "No opportunities scored ≥70 today. Market is quiet."
    lines = [f"OPPORTUNITIES ABOVE THRESHOLD ({len(top)} found):\n"]
    for i, o in enumerate(top, 1):
        lines.append(
            f"{i}. {o.get('name')} — Score: {o.get('score')}/100\n"
            f"   Type: {o.get('type')} | Model: {o.get('margin_model')}\n"
            f"   Speed to revenue: {o.get('speed')}\n"
            f"   Why: {o.get('reasoning')}\n"
        )
    return "\n".join(lines)


def _log_opportunities_to_airtable(opportunities: list):
    try:
        from lib.airtable_client import AirtableClient
        at = AirtableClient(
            os.getenv("AIRTABLE_TOKEN", ""),
            os.getenv("AIRTABLE_BASE_PLUGGEDIN", ""),
        )
        for opp in opportunities:
            at.create_record("Opportunities", {
                "Name":          opp.get("name", ""),
                "Score":         opp.get("score", 0),
                "Type":          opp.get("type", ""),
                "Margin Model":  opp.get("margin_model", ""),
                "Speed":         opp.get("speed", ""),
                "Reasoning":     opp.get("reasoning", ""),
                "Status":        "Pending" if opp.get("score", 0) >= _OPPORTUNITY_SCORE_THRESHOLD else "Monitoring",
                "Discovered At": datetime.now(timezone.utc).isoformat(),
            })
    except Exception as e:
        log.error(f"[OpportunityEngine] Airtable log failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# DIGITAL PRODUCTS AGENT
# Focused daily scan for ecom/digital product winners.
# ─────────────────────────────────────────────────────────────────────────────

def run_digital_products(dry_run: bool = False) -> dict:
    """
    Scans Amazon, TikTok Shop, Meta Ads, Gumroad for winning products.
    High-tier results go to Airtable + morning briefing.
    """
    log.info("[DigitalProducts] Starting daily scan")
    try:
        from lib.product_intelligence import run_daily_product_intelligence
        result = run_daily_product_intelligence(dry_run=dry_run)
        high = result.get("high_tier", [])
        log.info(f"[DigitalProducts] {len(high)} HIGH-tier products found")
        return {"agent": "digital_products", "ok": True, "result": result,
                "ran_at": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        log.error(f"[DigitalProducts] Failed: {e}")
        return {"agent": "digital_products", "ok": False, "error": str(e),
                "ran_at": datetime.now(timezone.utc).isoformat()}


# ─────────────────────────────────────────────────────────────────────────────
# LEAD GEN AGENT
# Finds SME prospects for PluggedIN's own pipeline.
# Not client work — this finds Qassim's own clients.
# ─────────────────────────────────────────────────────────────────────────────

def run_lead_gen(dry_run: bool = False) -> dict:
    """
    Scrapes directories and enriches leads for PluggedIN's own ICP:
    Legal / Professional Services / Recruitment, UK, 5-50 staff.
    Scores via ICP gate, logs READY leads to Airtable.
    """
    log.info("[LeadGen] Starting PluggedIN pipeline run")
    results = {
        "agent": "lead_gen",
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "leads_found": 0,
        "leads_qualified": 0,
        "outreach_drafted": 0,
        "ok": False,
    }

    PLUGGEDIN_ICP = {
        "industries": ["Legal", "Recruitment", "Professional Services", "Consulting"],
        "locations":  ["London", "Manchester", "Birmingham", "Leeds", "Bristol"],
        "size_range": "5-50 staff",
    }

    try:
        # Try B2B scanner first (free, no Apify needed)
        from lib.b2b_scanner import scan_b2b_directories
        prospects = scan_b2b_directories(
            industries=PLUGGEDIN_ICP["industries"],
            locations=PLUGGEDIN_ICP["locations"],
            limit=30,
            dry_run=dry_run,
        )
        log.info(f"[LeadGen] B2B scanner found {len(prospects)} prospects")
    except Exception as e:
        log.warning(f"[LeadGen] B2B scanner failed ({e}), trying creator outreach module")
        prospects = []

    # Score each lead through ICP gate
    qualified = []
    try:
        from lib.icp_gate import score_lead, gate_lead
        for p in prospects:
            score = score_lead(p)
            if score.get("gate") in ("auto", "review"):
                p["ICP Score"] = score["total"]
                p["Gate"] = score["gate"]
                qualified.append(p)
    except Exception as e:
        log.error(f"[LeadGen] ICP gate failed: {e}")
        qualified = prospects[:5]

    results["leads_found"] = len(prospects)
    results["leads_qualified"] = len(qualified)

    # Draft outreach for qualified leads
    if qualified and ANTHROPIC_API_KEY and not dry_run:
        try:
            drafted = _draft_pluggedin_outreach(qualified[:10])
            results["outreach_drafted"] = drafted
        except Exception as e:
            log.error(f"[LeadGen] Outreach drafting failed: {e}")

    # Log to Airtable
    if not dry_run and qualified:
        _log_pluggedin_leads(qualified)

    results["ok"] = True
    log.info(f"[LeadGen] Done — {results['leads_qualified']} qualified, {results['outreach_drafted']} outreach drafted")
    return results


def _draft_pluggedin_outreach(leads: list) -> int:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    drafted = 0
    for lead in leads:
        try:
            prompt = f"""Write a cold outreach message for PluggedIN to send to this prospect.

PluggedIN deploys AI agent teams that run a business's entire growth function.
Tagline: "We don't sell software. We deploy outcomes. Your AI team starts Monday."

Prospect:
Name/Company: {lead.get('Name') or lead.get('Company', 'Unknown')}
Industry: {lead.get('Industry', 'Professional Services')}
Location: {lead.get('Location', 'UK')}
Role: {lead.get('Role', 'Owner/Director')}
Signal: {lead.get('signal_type', 'Found via directory')}

Rules: Max 3 sentences. Warm. Reference their specific situation. No jargon. No "I hope this finds you well."
End with a soft CTA to a 15-minute call.

Return ONLY the message text."""

            resp = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            lead["Outreach Draft"] = resp.content[0].text.strip()
            drafted += 1
        except Exception:
            pass
    return drafted


def _log_pluggedin_leads(leads: list):
    try:
        from lib.airtable_client import AirtableClient
        at = AirtableClient(
            os.getenv("AIRTABLE_TOKEN", ""),
            os.getenv("AIRTABLE_BASE_PLUGGEDIN", ""),
        )
        for lead in leads:
            at.create_record("Leads", {
                **{k: v for k, v in lead.items() if isinstance(v, (str, int, float, bool))},
                "Client":   "pluggedin",
                "Stage":    "QUALIFIED",
                "Added At": datetime.now(timezone.utc).isoformat(),
            })
    except Exception as e:
        log.error(f"[LeadGen] Airtable log failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# AGRITRADE AGENT
# Matches African commodity producers with global buyers.
# ─────────────────────────────────────────────────────────────────────────────

def run_agritrade(dry_run: bool = False) -> dict:
    """
    Runs the commodity brokerage pipeline:
    1. Scrape TradeKey/EC21/Go4WB for demand signals
    2. Match to known suppliers
    3. Draft broker introduction letters
    4. Log deals to Airtable
    """
    log.info("[AgriTrade] Starting daily brokerage run")
    try:
        from lib.trade_broker import run_daily_brokerage, get_brokerage_ceo_summary

        # Get market signals first
        market_summary = None
        try:
            from lib.market_scout import run_scout
            scout = run_scout(topic_key="africa_china", source="b2b", log_airtable=False)
            market_summary = scout if isinstance(scout, dict) else {}
        except Exception:
            pass

        result = run_daily_brokerage(market_intel_summary=market_summary, dry_run=dry_run)
        summary = get_brokerage_ceo_summary()
        log.info(f"[AgriTrade] Done — {result.get('deals_matched', 0)} matches, {result.get('intros_sent', 0)} introductions")
        return {
            "agent": "agritrade",
            "ok": True,
            "result": result,
            "ceo_summary": summary,
            "ran_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        log.error(f"[AgriTrade] Failed: {e}")
        return {"agent": "agritrade", "ok": False, "error": str(e),
                "ran_at": datetime.now(timezone.utc).isoformat()}


# ─────────────────────────────────────────────────────────────────────────────
# CREATOR OUTREACH AGENT
# Micro-influencer outreach for PluggedIN's active ecom products.
# ─────────────────────────────────────────────────────────────────────────────

def run_creator_outreach(product_keyword: str = "AI business tools", dry_run: bool = False) -> dict:
    """
    Finds micro/mid creators on TikTok + Instagram and sends outreach.
    Runs after digital_products to target the day's best opportunities.
    """
    log.info(f"[CreatorOutreach] Starting for: {product_keyword}")
    try:
        from lib.creator_outreach import run_daily_creator_outreach

        # Minimal GTM brief — real one would come from product_intelligence output
        gtm_brief = {
            "product": product_keyword,
            "hook": f"How {product_keyword} is changing the game",
            "target_audience": "UK SME owners, 25-45",
            "commission_rate": "15%",
            "discount_code_prefix": "PLUGGEDIN",
        }

        result = run_daily_creator_outreach(
            product_keyword=product_keyword,
            gtm_brief=gtm_brief,
            creators_per_day=10,
            dry_run=dry_run,
        )
        log.info(f"[CreatorOutreach] Done — {result.get('outreach_sent', 0)} sent, {result.get('dm_queued', 0)} queued")
        return {"agent": "creator_outreach", "ok": True, "result": result,
                "ran_at": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        log.error(f"[CreatorOutreach] Failed: {e}")
        return {"agent": "creator_outreach", "ok": False, "error": str(e),
                "ran_at": datetime.now(timezone.utc).isoformat()}


# ─────────────────────────────────────────────────────────────────────────────
# MARKET SCOUT
# Free signal scraping — Reddit, HN, TradeKey, EC21.
# ─────────────────────────────────────────────────────────────────────────────

def run_market_scout(topic: str = "all", dry_run: bool = False) -> dict:
    log.info(f"[MarketScout] Running — topic: {topic}")
    try:
        from lib.market_scout import run_scout
        result = run_scout(topic_key=None if topic == "all" else topic,
                           source="all", log_airtable=not dry_run)
        signals = result.get("signals", []) if isinstance(result, dict) else []
        log.info(f"[MarketScout] Done — {len(signals)} signals")
        return {"agent": "market_scout", "ok": True, "signals": signals,
                "ran_at": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        log.error(f"[MarketScout] Failed: {e}")
        return {"agent": "market_scout", "ok": False, "error": str(e),
                "ran_at": datetime.now(timezone.utc).isoformat()}


# ─────────────────────────────────────────────────────────────────────────────
# DAILY FULL CYCLE
# Called by APScheduler at 05:00 UTC.
# Runs all agents, collects results, feeds into morning briefing.
# ─────────────────────────────────────────────────────────────────────────────

LIVE_AGENT_MAP = {
    "opportunity_engine": run_opportunity_engine,
    "digital_products":   run_digital_products,
    "lead_gen":           run_lead_gen,
    "agritrade":          run_agritrade,
    "creator_outreach":   run_creator_outreach,
    "market_scout":       run_market_scout,
}


def run_agent(agent_id: str, dry_run: bool = False, **kwargs) -> dict:
    """Run a single live agent by ID. Used by /live/run/{agent_id}."""
    fn = LIVE_AGENT_MAP.get(agent_id)
    if not fn:
        return {"agent": agent_id, "ok": False,
                "error": f"Unknown agent: {agent_id}. Valid: {list(LIVE_AGENT_MAP.keys())}"}
    return fn(dry_run=dry_run, **kwargs)


def run_daily_cycle(dry_run: bool = False) -> dict:
    """
    Full daily cycle — called at 05:00 UTC by APScheduler.
    Runs: market_scout → opportunity_engine → digital_products → lead_gen → agritrade
    Returns combined results dict for the morning briefing.
    """
    log.info("=" * 60)
    log.info("[DailyCycle] Starting PluggedIN Live daily cycle")
    log.info("=" * 60)

    cycle_results = {
        "cycle_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "agents": {},
    }

    # Run in logical order — scout feeds opportunity engine
    run_order = [
        ("market_scout",       lambda: run_market_scout(dry_run=dry_run)),
        ("opportunity_engine", lambda: run_opportunity_engine(dry_run=dry_run)),
        ("digital_products",   lambda: run_digital_products(dry_run=dry_run)),
        ("lead_gen",           lambda: run_lead_gen(dry_run=dry_run)),
        ("agritrade",          lambda: run_agritrade(dry_run=dry_run)),
    ]

    for agent_id, fn in run_order:
        log.info(f"[DailyCycle] Running {agent_id}...")
        try:
            result = fn()
            cycle_results["agents"][agent_id] = {
                "ok": result.get("ok", False),
                "summary": _summarise_agent_result(agent_id, result),
            }
        except Exception as e:
            cycle_results["agents"][agent_id] = {"ok": False, "summary": f"Error: {e}"}
            log.error(f"[DailyCycle] {agent_id} crashed: {e}")

    cycle_results["finished_at"] = datetime.now(timezone.utc).isoformat()
    cycle_results["ok"] = all(v["ok"] for v in cycle_results["agents"].values())

    log.info("[DailyCycle] Complete")
    _log_cycle_to_airtable(cycle_results)
    return cycle_results


def _summarise_agent_result(agent_id: str, result: dict) -> str:
    if not result.get("ok"):
        return f"Failed: {result.get('error', 'unknown error')}"
    if agent_id == "market_scout":
        return f"{len(result.get('signals', []))} signals captured"
    if agent_id == "opportunity_engine":
        top = [o for o in result.get("top_opportunities", []) if o.get("score", 0) >= _OPPORTUNITY_SCORE_THRESHOLD]
        return f"{len(top)} opportunities scored ≥{_OPPORTUNITY_SCORE_THRESHOLD}"
    if agent_id == "digital_products":
        r = result.get("result", {})
        return f"{len(r.get('high_tier', []))} HIGH-tier products found"
    if agent_id == "lead_gen":
        return f"{result.get('leads_qualified', 0)} leads qualified, {result.get('outreach_drafted', 0)} drafted"
    if agent_id == "agritrade":
        r = result.get("result", {})
        return f"{r.get('deals_matched', 0)} deals matched, {r.get('intros_sent', 0)} intros sent"
    return "Done"


def _log_cycle_to_airtable(cycle: dict):
    try:
        from lib.airtable_client import AirtableClient
        at = AirtableClient(
            os.getenv("AIRTABLE_TOKEN", ""),
            os.getenv("AIRTABLE_BASE_AGENCY", ""),
        )
        summary_lines = [f"{k}: {v['summary']}" for k, v in cycle["agents"].items()]
        at.create_record("Agent Reports", {
            "Module":    "PluggedIN Live Daily Cycle",
            "Status":    "done" if cycle.get("ok") else "partial",
            "Action":    "daily_cycle",
            "Message":   "\n".join(summary_lines),
            "Ran At":    cycle["started_at"],
        })
    except Exception as e:
        log.error(f"[DailyCycle] Airtable log failed: {e}")
