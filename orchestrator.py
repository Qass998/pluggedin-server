"""
orchestrator.py — PluggedIN Daily Conductor
Runs the entire agent stack in sequence.
Agents communicate via Airtable (the message bus).
Briefing delivered to Qassim via WhatsApp at 07:00.

Usage:
  python orchestrator.py                             # full daily run
  python orchestrator.py --phase briefing            # briefing only
  python orchestrator.py --agent knowledge           # single agent
  python orchestrator.py --agent product_research    # product research only
  python orchestrator.py --agent trade_broker        # trade broker only
  python orchestrator.py --agent vendor              # vendor scanner only
  python orchestrator.py --dry-run                   # no sends/calls

Schedule (set in crontab -e):
  0  4 * * * cd ~/Documents/AI-Agency/PluggedIN && python orchestrator.py --phase intelligence
  30 6 * * * cd ~/Documents/AI-Agency/PluggedIN && python orchestrator.py --phase ceo
  0  7 * * * cd ~/Documents/AI-Agency/PluggedIN && python orchestrator.py --phase briefing

Phase timeline:
  04:00 — Knowledge Agent        (trends, insights)
  04:30 — Trade Broker Intel     (Reddit demand signals, 12 countries)
  05:00 — Trade Broker Match     (deal matching, commission estimates)
  05:15 — Vendor Scanner         (B2B platform scan, client leads)
  06:30 — Product Research       (Meta/TikTok/Amazon/Reddit scoring, competitor intel, creator outreach)
  07:00 — CEO Agents + Chief     (per-domain reports → WhatsApp briefing)

Airtable tables:
  KnowledgeLog, Leads, Opportunities, Products
  DemandSignals, BrokerageDeals, EcomSourcingBriefs
  VendorLeads, VendorOutreach
  ProductOpportunities, GTMBriefs, CreatorPipeline, ManualDMQueue
  CEOReports
"""

import os
import sys
import json
import time
import argparse
import traceback
from datetime import datetime, date

from dotenv import load_dotenv
load_dotenv()

import requests

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

AIRTABLE_TOKEN      = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE       = os.getenv("AIRTABLE_BASE_PLUGGEDIN")
QASSIM_PHONE        = os.getenv("QASSIM_PHONE")
TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM         = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY")
ANTHROPIC_API_KEY   = os.getenv("ANTHROPIC_API_KEY")  # kept as fallback

DRY_RUN = "--dry-run" in sys.argv

# ─────────────────────────────────────────────
# MODEL ROUTING
# Every task routes to the right model.
# Kimi handles bulk reading (huge context, cheap).
# Claude handles judgment, synthesis, client-facing output.
# Haiku handles fast data tasks and logging.
# All routed via OpenRouter — single key, automatic failover.
# ─────────────────────────────────────────────

MODELS = {
    # Strategic / client-facing — needs judgment
    "chief":          "anthropic/claude-sonnet-4-6",
    "ceo":            "anthropic/claude-haiku-4-5",
    "broker":         "anthropic/claude-sonnet-4-6",
    "outreach":       "anthropic/claude-haiku-4-5",

    # Bulk reading / large context — Kimi excels here
    "knowledge":      "moonshotai/kimi-k2",
    "market_intel":   "moonshotai/kimi-k2",
    "competitor":     "moonshotai/kimi-k2",
    "product_brief":  "moonshotai/kimi-k2",

    # Fast data tasks — cheap and quick
    "scoring":        "anthropic/claude-haiku-4-5",
    "logging":        "anthropic/claude-haiku-4-5",
    "opportunity":    "anthropic/claude-haiku-4-5",
}

# Fallback chain: if primary fails, try these in order
FALLBACK_CHAIN = [
    "anthropic/claude-haiku-4-5",
    "moonshotai/kimi-k2",
    "openai/gpt-4o-mini",           # last resort
]

OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"


# ─────────────────────────────────────────────
# CORE AI CALLER — OpenRouter with fallback
# ─────────────────────────────────────────────

def call_model(
    task: str,
    system: str,
    prompt: str,
    max_tokens: int = 1500,
    model_override: str = None,
) -> str:
    """
    Call the appropriate model via OpenRouter.
    Automatically falls back if primary model fails.
    task: key from MODELS dict (e.g. "chief", "knowledge", "scoring")
    """
    primary_model = model_override or MODELS.get(task, MODELS["scoring"])
    api_key = OPENROUTER_API_KEY or ANTHROPIC_API_KEY

    if not api_key:
        raise ValueError("No API key set. Add OPENROUTER_API_KEY to .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://pluggedin.ai",   # OpenRouter attribution
        "X-Title": "PluggedIN OS",
    }

    models_to_try = [primary_model] + [m for m in FALLBACK_CHAIN if m != primary_model]

    for attempt, model in enumerate(models_to_try):
        try:
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": prompt},
                ],
            }

            # If OpenRouter key not set, fall back to Anthropic SDK directly
            if not OPENROUTER_API_KEY and ANTHROPIC_API_KEY:
                return _call_anthropic_direct(model, system, prompt, max_tokens)

            resp = requests.post(OPENROUTER_BASE, headers=headers, json=payload, timeout=60)

            if resp.ok:
                result = resp.json()
                text = result["choices"][0]["message"]["content"].strip()
                if attempt > 0:
                    log(f"[model] Used fallback: {model} (primary {primary_model} failed)")
                return text

            # Rate limit — wait and retry same model once
            if resp.status_code == 429:
                log(f"[model] Rate limited on {model}, waiting 10s...")
                time.sleep(10)
                resp2 = requests.post(OPENROUTER_BASE, headers=headers, json=payload, timeout=60)
                if resp2.ok:
                    return resp2.json()["choices"][0]["message"]["content"].strip()

            log(f"[model] {model} returned {resp.status_code} — trying next")

        except Exception as e:
            log(f"[model] {model} error: {e} — trying next")
            continue

    raise RuntimeError(f"All models failed for task '{task}'. Check API keys and connectivity.")


def _call_anthropic_direct(model: str, system: str, prompt: str, max_tokens: int) -> str:
    """Direct Anthropic API fallback (no OpenRouter)."""
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    # Map OpenRouter model names back to Anthropic names
    model_map = {
        "anthropic/claude-sonnet-4-6": "claude-sonnet-4-6",
        "anthropic/claude-haiku-4-5":  "claude-haiku-4-5-20251001",
    }
    anthropic_model = model_map.get(model, "claude-haiku-4-5-20251001")
    response = client.messages.create(
        model=anthropic_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


# Legacy alias — existing agent code calls call_claude(), keep it working
def call_claude(model: str, system: str, prompt: str, max_tokens: int = 1500) -> str:
    """
    Backwards-compatible wrapper. Routes via OpenRouter.
    Model string can be Anthropic native name or OpenRouter format.
    """
    # Map legacy Anthropic model names to task keys
    task_map = {
        "claude-haiku-4-5-20251001": "scoring",
        "claude-sonnet-4-6":         "chief",
        "claude-haiku-4-5":          "scoring",
    }
    task = task_map.get(model, "scoring")
    return call_model(task=task, system=system, prompt=prompt, max_tokens=max_tokens)


# ─────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────

def log(msg: str):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    # Also write to log file
    try:
        log_dir = os.path.expanduser("~/pluggedin-logs")
        os.makedirs(log_dir, exist_ok=True)
        with open(f"{log_dir}/daily.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except Exception:
        pass


def airtable_write(table: str, fields: dict) -> dict:
    """Write a record to Airtable."""
    if DRY_RUN:
        log(f"[DRY RUN] Would write to {table}: {json.dumps(fields, indent=2)}")
        return {"id": "dry_run"}
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/{table}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
    r = requests.post(url, json={"fields": fields}, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()


def airtable_read(table: str, filter_formula: str = None, max_records: int = 100) -> list:
    """Read records from Airtable."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/{table}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    params = {"maxRecords": max_records}
    if filter_formula:
        params["filterByFormula"] = filter_formula
    r = requests.get(url, headers=headers, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("records", [])


def send_whatsapp(to: str, message: str):
    """Send WhatsApp message via Twilio."""
    if DRY_RUN:
        log(f"[DRY RUN] Would send WhatsApp to {to}:\n{message}")
        return
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    requests.post(url, data={
        "From": TWILIO_FROM,
        "To": f"whatsapp:{to}",
        "Body": message,
    }, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=15)
    log(f"WhatsApp sent to {to}")


# ─────────────────────────────────────────────
# PHASE 1: INTELLIGENCE (04:00)
# ─────────────────────────────────────────────

def run_knowledge_agent():
    """
    Knowledge Acquisition Agent.
    Pulls insights from monitored sources.
    Writes to Airtable: KnowledgeLog.
    """
    log("Running Knowledge Agent...")

    # Read agent file for context
    try:
        with open("live/agents/knowledge-agent.md", "r") as f:
            agent_context = f.read()
    except FileNotFoundError:
        agent_context = "Extract actionable insights from the sources provided."

    # Read sources (simplified — in production, use TinyFish to actually browse)
    # For now: generate synthetic intelligence update as a test
    prompt = f"""
You are the Knowledge Acquisition Agent for PluggedIN.
Today is {date.today().isoformat()}.

Based on your knowledge of current trends in:
- B2B lead generation
- Ecommerce (dropshipping and digital products)
- African commodity trade
- YouTube growth strategies
- AI automation for SMEs

Extract the 5 most actionable insights that PluggedIN agents should know today.
Format as:
NICHE: [niche name]
INSIGHT: [specific, actionable, with numbers where possible]
SOURCE: [type of source this would come from]
ACTION: [what agent should do differently based on this]
---
(repeat for each insight)
"""

    insights = call_model(
        task="scoring",
        system="You are the Knowledge Acquisition Agent. Extract specific, actionable insights only. No generic advice.",
        prompt=prompt,
        max_tokens=1500
    )

    # Write to Airtable
    airtable_write("KnowledgeLog", {
        "Date": date.today().isoformat(),
        "Source": "Automated daily scan",
        "Niche": "All",
        "InsightsExtracted": 5,
        "FilesUpdated": "memory/semantic/",
        "Notes": insights[:1000]  # Airtable field limit
    })

    log("Knowledge Agent complete.")
    return insights


def run_market_intel_and_brokerage():
    """
    Global Trade Broker Agent — TradeBridge + SourcedStore.
    04:30: Mine demand signals from Reddit (12 countries) + trade boards.
    05:00: Match demand to supply, log deals, draft outreach emails.
    Two businesses: B2B commission brokerage + ecom sourcing.
    """
    log("Running Global Trade Broker Agent (Market Intel + Brokerage)...")
    try:
        from lib.market_intel import run_daily_market_intel
        from lib.trade_broker import run_daily_brokerage, get_brokerage_ceo_summary

        # Phase A: Market intelligence
        intel_summary = run_daily_market_intel(dry_run=DRY_RUN)
        log(f"Market Intel: {intel_summary.get('total_signals', 0)} signals "
            f"({intel_summary.get('brokerage_signals', 0)} brokerage, "
            f"{intel_summary.get('ecom_signals', 0)} ecom)")

        # Phase B: Brokerage deal matching + ecom briefs
        broker_summary = run_daily_brokerage(market_intel_summary=intel_summary, dry_run=DRY_RUN)
        log(f"Brokerage: {broker_summary.get('deals_matched', 0)} deals matched | "
            f"£{broker_summary.get('new_commission_potential', 0):,.0f} new commission potential | "
            f"{broker_summary.get('ecom_briefs_created', 0)} ecom briefs")

        # CEO report
        pipeline = get_brokerage_ceo_summary()
        airtable_write("CEOReports", {
            "Domain": "TradeBridge",
            "Business": "TradeBridge + SourcedStore",
            "Date": date.today().isoformat(),
            "Summary": (
                f"Countries scanned: {', '.join(intel_summary.get('countries_scanned', []))}. "
                f"Demand signals: {intel_summary.get('total_signals', 0)} total "
                f"({intel_summary.get('brokerage_signals', 0)} brokerage / "
                f"{intel_summary.get('ecom_signals', 0)} ecom). "
                f"Deals matched: {broker_summary.get('deals_matched', 0)}. "
                f"Pipeline: {pipeline.get('active_deals', 0)} active | "
                f"£{pipeline.get('pipeline_commission_gbp', 0):,.0f} commission potential. "
                f"Ecom briefs: {broker_summary.get('ecom_briefs_created', 0)} new."
            ),
            "Revenue": 0,
            "LeadsFound": broker_summary.get("deals_matched", 0),
            "ActionsCompleted": broker_summary.get("emails_drafted", 0),
            "Flags": f"{pipeline.get('hot_deals', 0)} deals in active negotiation" if pipeline.get("hot_deals", 0) > 0 else "None",
        })

        log("Global Trade Broker Agent complete.")
        return {"intel": intel_summary, "broker": broker_summary}

    except Exception as e:
        log(f"Trade broker error: {e}")
        traceback.print_exc()
        return {}


def run_vendor_scanner():
    """
    Vendor & Partnership Agent.
    Scans global B2B platforms for sourcing deals, white-label plays, distributor
    opportunities, AND mines PluggedIN client leads from the same data.
    Writes to Airtable: VendorLeads, VendorOutreach, Leads (client prospects).
    Runs at 05:15.
    """
    log("Running Vendor & Partnership Agent...")

    try:
        from lib.b2b_scanner import run_daily_scan, mine_pluggedin_leads
        from lib.vendor_outreach import run_outreach_from_scan, run_followup_sequence, get_outreach_summary

        # Full B2B platform scan
        summary = run_daily_scan(dry_run=DRY_RUN)

        # Mine PluggedIN client leads from the same scan data
        client_leads = mine_pluggedin_leads(dry_run=DRY_RUN)

        # Run outreach for top vendor opportunities
        if summary.get("top_opportunities") and not DRY_RUN:
            outreach = run_outreach_from_scan(
                scan_results=summary["top_opportunities"],
                play_type="exclusive_distributor",
                max_emails=8,
                dry_run=DRY_RUN,
            )
        else:
            outreach = {"sent": 0, "manual_contact_needed": 0}

        # Run follow-up emails for existing pipeline
        followups = run_followup_sequence(dry_run=DRY_RUN)

        # Get full outreach pipeline stats
        pipeline = get_outreach_summary()

        # Write CEO report
        airtable_write("CEOReports", {
            "Domain": "VendorPartnerships",
            "Business": "B2B Scanner",
            "Date": date.today().isoformat(),
            "Summary": (
                f"Scanned {summary.get('total_scanned', 0)} products across 7 platforms. "
                f"Found {summary.get('pursue_count', 0)} pursue-worthy deals, "
                f"{summary.get('white_label_plays', 0)} white-label plays. "
                f"Sent {outreach.get('sent', 0)} outreach emails + "
                f"{followups.get('followups_sent', 0)} follow-ups. "
                f"Pipeline: {pipeline.get('interested', 0)} interested suppliers. "
                f"Mined {client_leads.get('logged', 0)} potential PluggedIN client leads."
            ),
            "Revenue": 0,
            "ActionsCompleted": outreach.get("sent", 0) + followups.get("followups_sent", 0),
            "Flags": str(summary.get("top_white_label", ""))[:500],
        })

        log(f"Vendor Agent complete — {summary.get('pursue_count', 0)} deals, {outreach.get('sent', 0)} emails, {client_leads.get('logged', 0)} client leads")
        return summary

    except Exception as e:
        log(f"Vendor scanner error: {e}")
        traceback.print_exc()
        return {}


def run_opportunity_engine():
    """
    Opportunity Engine Agent.
    Scores new business opportunities 0-100.
    Writes to Airtable: Opportunities.
    """
    log("Running Opportunity Engine...")

    prompt = f"""
You are the Opportunity Engine for PluggedIN.
Today is {date.today().isoformat()}.

Identify 3 specific business opportunities PluggedIN could launch or pursue today.
Score each 0-100 using this framework:
- Demand signal (0-20): how clear is evidence of market demand?
- Competition level (0-20): how open is the space?
- Margin potential (0-20): what margin % is achievable?
- Agent buildability (0-20): how fully automated can this be with our stack?
- Speed to revenue (0-20): how fast to first £?

For each opportunity, format exactly as:
OPPORTUNITY: [name]
SCORE: [total/100]
SIGNAL: [specific data point that triggered this]
MODEL: [how PluggedIN makes money]
BUILD_TIME: [hours to deploy]
FIRST_REVENUE: [days to first £]
RECOMMENDATION: [Launch / Monitor / Pass]
---
"""

    opportunities = call_model(
        task="scoring",
        system="You are the Opportunity Engine. Only surface specific, actionable opportunities. No vague suggestions.",
        prompt=prompt,
        max_tokens=1500
    )

    # Parse and write to Airtable (simplified parser)
    blocks = opportunities.split("---")
    for block in blocks:
        if "OPPORTUNITY:" in block:
            lines = {line.split(":")[0].strip(): ":".join(line.split(":")[1:]).strip()
                    for line in block.strip().split("\n") if ":" in line}
            try:
                score = int(lines.get("SCORE", "0").split("/")[0])
                status = "Pending" if score >= 70 else "Monitoring"
                airtable_write("Opportunities", {
                    "Name": lines.get("OPPORTUNITY", "Unknown"),
                    "Score": score,
                    "Source": "Opportunity Engine daily scan",
                    "MarginModel": lines.get("MODEL", ""),
                    "Status": status,
                    "DiscoveredAt": date.today().isoformat(),
                    "Notes": block.strip()[:500]
                })
            except Exception as e:
                log(f"Could not parse opportunity block: {e}")

    log("Opportunity Engine complete.")
    return opportunities


# ─────────────────────────────────────────────
# PHASE 1b: PRODUCT RESEARCH (06:30)
# ─────────────────────────────────────────────

def run_product_research():
    """
    Product Research Agent — SourcedStore intelligence layer.
    06:30: Scan platforms for winning products (Meta, TikTok, Amazon, Reddit, Trends).
    07:00: Run competitor analysis + GTM briefs for HIGH-tier products.
    07:30: Find micro/mid creators and send seeding outreach.

    Input: EcomSourcingBriefs from Trade Broker Agent (already validated demand).
    Output: GTMBriefs, CreatorPipeline, ManualDMQueue, SourceStore CEO report.
    """
    log("Running Product Research Agent...")
    try:
        from lib.product_intelligence import run_daily_product_intelligence
        from lib.competitor_intelligence import run_competitor_intelligence
        from lib.creator_outreach import run_daily_creator_outreach, compile_organic_performance_report

        # ── Step 1: Gather EcomSourcingBriefs from Trade Broker ──
        ecom_briefs = airtable_read(
            "EcomSourcingBriefs",
            filter_formula="AND({Status} = 'New', {CreatedAt} >= TODAY())",
            max_records=10,
        )
        # Convert to keyword list (supplement with defaults)
        brief_keywords = [r["fields"].get("Product", "") for r in ecom_briefs if r["fields"].get("Product")]
        log(f"  → {len(brief_keywords)} EcomSourcingBriefs from Trade Broker as input")

        # ── Step 2: Full product intelligence scan ──
        intel_report = run_daily_product_intelligence(
            keywords=brief_keywords if brief_keywords else None,
            include_blue_ocean=True,
            dry_run=DRY_RUN,
        )

        summary = intel_report.get("summary", {})
        high_tier = summary.get("high_tier", [])
        medium_tier = summary.get("medium_tier", [])
        blue_ocean = summary.get("blue_ocean_plays", [])

        log(f"  → Product Intel: {summary.get('total_scanned', 0)} scanned | "
            f"{len(high_tier)} HIGH | {len(medium_tier)} MEDIUM | {len(blue_ocean)} blue ocean plays")

        # ── Step 3: Competitor intel + GTM brief for HIGH-tier products ──
        gtm_briefs = {}
        for item in high_tier[:3]:  # Cap at 3 full GTM briefs per day
            keyword = item["keyword"]
            try:
                # Find the score result from intel_report
                score_result = next(
                    (r for r in intel_report.get("results", []) if r.get("keyword") == keyword),
                    {"total_score": item.get("score", 70), "tier": "HIGH"}
                )
                icp = score_result.get("icp", {})

                competitor_report = run_competitor_intelligence(
                    keyword=keyword,
                    score_result=score_result,
                    icp=icp,
                    target_market="UK",
                    dry_run=DRY_RUN,
                )
                gtm_briefs[keyword] = competitor_report.get("gtm_brief", {})
                log(f"  ✓ GTM brief ready: {keyword}")
            except Exception as e:
                log(f"  ✗ GTM brief failed for '{keyword}': {e}")

        # ── Step 4: Creator outreach for products with GTM briefs ──
        outreach_totals = {"outreach_sent": 0, "email_sent": 0, "dm_queued": 0, "followups_triggered": 0}
        for keyword, gtm_brief in gtm_briefs.items():
            try:
                outreach_result = run_daily_creator_outreach(
                    product_keyword=keyword,
                    gtm_brief=gtm_brief,
                    creators_per_day=5,  # Split across products
                    dry_run=DRY_RUN,
                )
                for k in outreach_totals:
                    outreach_totals[k] += outreach_result.get(k, 0)
                log(f"  ✓ Creator outreach done: {keyword} ({outreach_result.get('outreach_sent', 0)} sent)")
            except Exception as e:
                log(f"  ✗ Creator outreach failed for '{keyword}': {e}")

        # ── Step 5: Check organic performance for existing products ──
        try:
            posted_products = airtable_read(
                "CreatorPipeline",
                filter_formula="{OutreachStatus} = 'Posted'",
                max_records=20,
            )
            posted_keywords = list(set(r["fields"].get("Product", "") for r in posted_products if r["fields"].get("Product")))
            organic_reports = {}
            for kw in posted_keywords[:2]:  # Check top 2 active products
                organic_reports[kw] = compile_organic_performance_report(product=kw)
                if organic_reports[kw].get("ready_for_ads"):
                    log(f"  🚀 {kw} is ready for paid ads! ({organic_reports[kw].get('total_organic_views', 0):,} organic views)")
        except Exception as e:
            log(f"  Organic performance check skipped: {e}")
            organic_reports = {}

        # ── Step 6: CEO report ──
        top_blue_ocean = blue_ocean[0] if blue_ocean else {}
        top_organic = max(organic_reports.values(), key=lambda x: x.get("total_organic_views", 0)) if organic_reports else {}

        airtable_write("CEOReports", {
            "Domain": "SourcedStore",
            "Business": "Product Research + Creator Seeding",
            "Date": date.today().isoformat(),
            "Summary": (
                f"Scanned {summary.get('total_scanned', 0)} products. "
                f"{len(high_tier)} HIGH tier, {len(medium_tier)} MEDIUM tier. "
                f"GTM briefs built: {len(gtm_briefs)}. "
                f"Creator outreach: {outreach_totals['outreach_sent']} sent "
                f"({outreach_totals['email_sent']} email, {outreach_totals['dm_queued']} DM queue). "
                f"Blue ocean: {len(blue_ocean)} plays identified"
                + (f" — top: {top_blue_ocean.get('product', '')} in {top_blue_ocean.get('market', '')}" if top_blue_ocean else "")
                + (f". Organic views: {top_organic.get('total_organic_views', 0):,} for {top_organic.get('product', '')}"
                   f" → {top_organic.get('recommendation', '')}" if top_organic else "")
                + "."
            ),
            "Revenue": 0,
            "ActionsCompleted": outreach_totals["outreach_sent"] + len(gtm_briefs),
            "Flags": (
                f"READY FOR ADS: {', '.join([k for k, v in organic_reports.items() if v.get('ready_for_ads')])}"
                if any(v.get("ready_for_ads") for v in organic_reports.values())
                else "None"
            ),
        })

        log(f"Product Research Agent complete — {len(high_tier)} HIGH products, {len(gtm_briefs)} GTM briefs, {outreach_totals['outreach_sent']} creator outreaches")
        return {
            "high_tier": high_tier,
            "medium_tier": medium_tier,
            "blue_ocean": blue_ocean,
            "gtm_briefs": list(gtm_briefs.keys()),
            "outreach": outreach_totals,
            "organic_reports": organic_reports,
        }

    except Exception as e:
        log(f"Product Research Agent error: {e}")
        traceback.print_exc()
        return {}


# ─────────────────────────────────────────────
# PHASE 2: CEO AGENTS (06:00)
# ─────────────────────────────────────────────

def compile_lead_gen_ceo_report() -> str:
    """Lead Gen CEO Agent — reads all 6 verticals from Airtable."""
    log("Compiling Lead Gen CEO report...")

    today_filter = f"IS_SAME({{DeliveredAt}}, TODAY(), 'day')"
    delivered_today = airtable_read("Leads", filter_formula=today_filter, max_records=50)
    revenue = sum(r["fields"].get("Price", 0) for r in delivered_today if r["fields"].get("Paid"))
    delivered_count = len(delivered_today)

    prompt = f"""
Generate a CEO Agent briefing block for the Lead Gen department.
Data: {delivered_count} leads delivered today. Revenue: £{revenue}.
Format: 3 sentences max. Include one flag or recommendation if relevant.
Start with "LEAD GEN:"
"""
    summary = call_model(
        task="ceo",
        system="You are the Lead Gen CEO Agent. Be specific. Use numbers.",
        prompt=prompt, max_tokens=200
    )

    airtable_write("CEOReports", {
        "Domain": "Lead Gen",
        "Business": "All Verticals",
        "Date": date.today().isoformat(),
        "Summary": summary,
        "Revenue": revenue,
        "LeadsFound": delivered_count,
        "Flags": "None" if delivered_count > 0 else "No leads delivered today"
    })

    return summary


def compile_ecommerce_ceo_report() -> str:
    """Ecommerce CEO Agent — reads product performance from Airtable."""
    log("Compiling Ecommerce CEO report...")

    products = airtable_read("Products", filter_formula="{Status} = 'Active'", max_records=20)
    total_revenue = sum(r["fields"].get("DailyRevenue", 0) for r in products)

    prompt = f"""
Generate a CEO Agent briefing block for the Ecommerce department.
Active products: {len(products)}. Revenue today: £{total_revenue:.2f}.
Format: 3 sentences max. Flag anything needing attention.
Start with "ECOMMERCE:"
"""
    summary = call_model(
        task="ceo",
        system="You are the Ecommerce CEO Agent. Be specific. Use numbers.",
        prompt=prompt, max_tokens=200
    )

    airtable_write("CEOReports", {
        "Domain": "Ecommerce",
        "Business": "All Products",
        "Date": date.today().isoformat(),
        "Summary": summary,
        "Revenue": total_revenue,
        "Flags": "None"
    })

    return summary


def compile_agritrade_ceo_report() -> str:
    """AgriTrade CEO Agent — reads deal pipeline."""
    log("Compiling AgriTrade CEO report...")

    # In production: read from AgriTrade Deals table
    prompt = """
Generate a CEO Agent briefing block for AgriTrade.
Status: Pipeline being built. No closed deals yet.
Format: 2 sentences. Note what's in progress.
Start with "AGRITRADE:"
"""
    summary = call_model(
        task="ceo",
        system="You are the AgriTrade CEO Agent.",
        prompt=prompt, max_tokens=150
    )

    airtable_write("CEOReports", {
        "Domain": "AgriTrade",
        "Business": "AgriTrade",
        "Date": date.today().isoformat(),
        "Summary": summary,
        "Revenue": 0,
        "Flags": "Pipeline building"
    })

    return summary


def compile_content_ceo_report() -> str:
    """Content CEO Agent — reads YouTube channel stats."""
    log("Compiling Content CEO report...")

    prompt = """
Generate a CEO Agent briefing block for the Content department (YouTube x5 + Pinterest).
Status: Channels being set up. No videos live yet.
Format: 2 sentences. Note what's in progress.
Start with "CONTENT:"
"""
    summary = call_model(
        task="ceo",
        system="You are the Content CEO Agent.",
        prompt=prompt, max_tokens=150
    )

    airtable_write("CEOReports", {
        "Domain": "Content",
        "Business": "YouTube x5",
        "Date": date.today().isoformat(),
        "Summary": summary,
        "Revenue": 0,
        "Flags": "Channels in setup"
    })

    return summary


def compile_vendor_ceo_report() -> str:
    """Vendor & Partnership CEO Agent — reads VendorLeads and VendorOutreach from Airtable."""
    log("Compiling Vendor & Partnership CEO report...")

    pursue_leads = airtable_read("VendorLeads", filter_formula="AND({Score} >= 70, {Status} = 'New')", max_records=20)
    try:
        from lib.vendor_outreach import get_outreach_summary
        pipeline = get_outreach_summary()
    except Exception:
        pipeline = {}

    prompt = f"""
Generate a CEO Agent briefing block for the Vendor & Partnership department.
Data:
- New pursue-worthy opportunities found today: {len(pursue_leads)}
- Suppliers currently interested: {pipeline.get('interested', 0)}
- Deals in conversation: {pipeline.get('in_conversation', 0)}
- Total outreach pipeline: {pipeline.get('total_outreach', 0)} contacts
Format: 3 sentences max. Include top opportunity if any. Flag anything needing Qassim.
Start with "VENDOR:"
"""
    summary = call_model(
        task="ceo",
        system="You are the Vendor & Partnership CEO Agent. Be specific. Use numbers.",
        prompt=prompt, max_tokens=200
    )

    airtable_write("CEOReports", {
        "Domain": "VendorPartnerships",
        "Business": "B2B Deals",
        "Date": date.today().isoformat(),
        "Summary": summary,
        "Revenue": 0,
        "LeadsFound": len(pursue_leads),
        "Flags": f"{pipeline.get('interested', 0)} interested suppliers" if pipeline.get("interested", 0) > 0 else "None",
    })

    return summary


# ─────────────────────────────────────────────
# PHASE 3: CHIEF OF ALL CHIEFS (06:30)
# ─────────────────────────────────────────────

def chief_of_all_chiefs_synthesis() -> str:
    """
    Reads all CEO reports from today.
    Synthesises into the daily WhatsApp briefing for Qassim.
    """
    log("Chief of All Chiefs synthesising...")

    today_filter = f"IS_SAME({{Date}}, TODAY(), 'day')"
    ceo_reports = airtable_read("CEOReports", filter_formula=today_filter, max_records=10)

    if not ceo_reports:
        log("No CEO reports found for today. Using placeholder.")
        combined = "No CEO reports yet — agents are initialising."
    else:
        combined = "\n\n".join([
            f"{r['fields'].get('Domain', 'Unknown')}: {r['fields'].get('Summary', '')}"
            for r in ceo_reports
        ])

    total_revenue = sum(r["fields"].get("Revenue", 0) for r in ceo_reports)

    # Get top opportunity (if any scored >= 70)
    opp_filter = "AND({Score} >= 70, {Status} = 'Pending')"
    top_opps = airtable_read("Opportunities", filter_formula=opp_filter, max_records=2)
    opp_text = ""
    if top_opps:
        for opp in top_opps:
            opp_text += f"\n→ {opp['fields'].get('Name', '')} (Score: {opp['fields'].get('Score', 0)}/100)"

    prompt = f"""
You are the Chief of All Chiefs for PluggedIN — an AI conglomerate.
Today is {date.today().strftime('%A, %d %B %Y')}.

CEO Reports received today:
{combined}

Total portfolio revenue today: £{total_revenue:.2f}

Opportunities flagged (score ≥ 70):{opp_text if opp_text else " None today"}

Write the daily WhatsApp briefing for Qassim.
Rules:
- WhatsApp format (use *bold* and line breaks)
- Maximum 250 words
- Include: each business domain in 1-2 lines, total revenue, top priority, decisions needed
- End with: "Reply *GO* to approve all actions" and "Reply *DECISIONS* to see items needing input"
- Tone: direct, data-driven, confident

Format exactly:
📊 *PluggedIN Live — Daily Briefing*
_{date}_

[domain summaries]

*REVENUE TODAY:* £[X]
*PRIORITY:* [one thing]
*DECISIONS NEEDED:* [N items / None]

---
_Reply *GO* to approve all pending actions_
_Reply *DECISIONS* for items needing your input_
_Reply *PAUSE [business]* to hold any area_
"""

    briefing = call_model(
        task="chief",
        system="You are the Chief of All Chiefs. Synthesise clearly. Be specific. No fluff.",
        prompt=prompt,
        max_tokens=600
    )

    log("Chief of All Chiefs synthesis complete.")
    return briefing


# ─────────────────────────────────────────────
# PHASE 4: DELIVERY (07:00)
# ─────────────────────────────────────────────

def deliver_briefing(briefing: str):
    """Send the daily briefing to Qassim via WhatsApp."""
    log("Delivering briefing to Qassim...")
    if not QASSIM_PHONE:
        log("QASSIM_PHONE not set in .env — printing briefing instead:")
        print("\n" + "="*50)
        print(briefing)
        print("="*50 + "\n")
        return
    send_whatsapp(QASSIM_PHONE, briefing)
    log("Briefing delivered.")


def deliver_client_briefings():
    """
    Send personalised briefings to all active clients.
    Each client gets their own WhatsApp + email showing only their data.
    Runs after Qassim's briefing at 07:00.
    """
    log("Delivering client briefings...")
    try:
        from lib.client_manager import deliver_all_client_briefings
        results = deliver_all_client_briefings(dry_run=DRY_RUN)
        log(f"Client briefings done — {results['whatsapp_sent']} WhatsApp, "
            f"{results['emails_sent']} email, {results['total_clients']} clients total")
        return results
    except Exception as e:
        log(f"Client briefings error: {e}")
        return {}


# ─────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────

def run_intelligence_phase():
    """Phase 1 — runs at 04:00–06:30"""
    log("=== PHASE 1: INTELLIGENCE ===")
    results = {}
    for agent_fn, name in [
        (run_knowledge_agent, "knowledge"),                        # 04:00
        (run_market_intel_and_brokerage, "trade_broker"),         # 04:30
        (run_opportunity_engine, "opportunity_engine"),            # 05:00
        (run_vendor_scanner, "vendor_scanner"),                    # 05:15
        (run_product_research, "product_research"),                # 06:30
    ]:
        try:
            results[name] = agent_fn()
        except Exception as e:
            log(f"ERROR in {name}: {e}")
            traceback.print_exc()
    return results


def compile_sourcestore_ceo_report() -> str:
    """SourcedStore CEO Agent — reads ProductOpportunities + CreatorPipeline from Airtable."""
    log("Compiling SourcedStore CEO report...")

    high_tier = airtable_read(
        "ProductOpportunities",
        filter_formula="AND({Tier} = 'HIGH', {Status} = 'New')",
        max_records=10,
    )
    creators_outreached = airtable_read(
        "CreatorPipeline",
        filter_formula="NOT({OutreachStatus} = 'Closed')",
        max_records=50,
    )
    creators_posted = [r for r in creators_outreached if r["fields"].get("OutreachStatus") == "Posted"]
    dm_queue = airtable_read("ManualDMQueue", filter_formula="{Status} = 'Pending'", max_records=20)

    prompt = f"""
Generate a CEO Agent briefing block for the SourcedStore (Product Research) department.
Data:
- High-tier product opportunities found today: {len(high_tier)}
- Top product: {high_tier[0]['fields'].get('Product', 'None') if high_tier else 'None'} (score: {high_tier[0]['fields'].get('TotalScore', 0) if high_tier else 0}/100)
- Creators in pipeline: {len(creators_outreached)}
- Creators who have posted: {len(creators_posted)}
- Creators needing manual DM: {len(dm_queue)}
Format: 3 sentences max. Include top product and creator count. Flag if manual DMs needed.
Start with "SOURCESTORE:"
"""
    summary = call_model(
        task="ceo",
        system="You are the SourcedStore CEO Agent. Be specific. Use numbers.",
        prompt=prompt, max_tokens=200
    )

    airtable_write("CEOReports", {
        "Domain": "SourcedStore",
        "Business": "Product Research",
        "Date": date.today().isoformat(),
        "Summary": summary,
        "Revenue": 0,
        "LeadsFound": len(high_tier),
        "ActionsCompleted": len(creators_outreached),
        "Flags": f"{len(dm_queue)} creators need manual DM" if dm_queue else "None",
    })

    return summary


def run_ceo_phase():
    """Phase 2 — runs at 06:00"""
    log("=== PHASE 2: CEO AGENTS ===")
    reports = {}
    for ceo_fn, domain in [
        (compile_lead_gen_ceo_report, "lead_gen"),
        (compile_ecommerce_ceo_report, "ecommerce"),
        (compile_agritrade_ceo_report, "agritrade"),
        (compile_content_ceo_report, "content"),
        (compile_vendor_ceo_report, "vendor"),
        (compile_sourcestore_ceo_report, "sourcestore"),
    ]:
        try:
            reports[domain] = ceo_fn()
        except Exception as e:
            log(f"ERROR in {domain} CEO: {e}")
            reports[domain] = f"[Error generating {domain} report]"
    return reports


def run_briefing_phase():
    """Phase 3 — runs at 06:30 and delivers at 07:00"""
    log("=== PHASE 3: CHIEF OF ALL CHIEFS + DELIVERY ===")
    briefing = chief_of_all_chiefs_synthesis()
    # 1. Send Qassim's master briefing (all businesses, full picture)
    deliver_briefing(briefing)
    # 2. Send each client their own personalised briefing (their data only)
    deliver_client_briefings()
    return briefing


def main():
    parser = argparse.ArgumentParser(description="PluggedIN Orchestrator")
    parser.add_argument("--phase", choices=["intelligence", "ceo", "briefing", "all"],
                        default="all", help="Which phase to run")
    parser.add_argument("--agent", help="Run a single agent by name")
    parser.add_argument("--dry-run", action="store_true", help="Don't send or write anything")
    args = parser.parse_args()

    if DRY_RUN:
        log("=== DRY RUN MODE — no sends or writes ===")

    log(f"PluggedIN Orchestrator starting — phase: {args.phase}")

    if args.agent == "knowledge":
        run_knowledge_agent()
    elif args.agent == "opportunity":
        run_opportunity_engine()
    elif args.agent == "product_research":
        run_product_research()
    elif args.agent == "trade_broker":
        run_market_intel_and_brokerage()
    elif args.agent == "vendor":
        run_vendor_scanner()
    elif args.phase == "intelligence":
        run_intelligence_phase()
    elif args.phase == "ceo":
        run_ceo_phase()
    elif args.phase == "briefing":
        run_briefing_phase()
    elif args.phase == "all":
        run_intelligence_phase()
        run_ceo_phase()
        run_briefing_phase()

    log("Orchestrator complete.")


if __name__ == "__main__":
    main()
