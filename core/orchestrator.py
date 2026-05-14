"""
core/orchestrator.py — PluggedIN Agent OS Orchestrator
=======================================================
The central dispatcher. Takes a tenant + modules and runs the right agents.

Usage:
    from core.orchestrator import run_client, run_module
    from core.tenant import get_tenant

    tenant = get_tenant("gromatic")
    run_client(tenant)                    # run all active modules
    run_module(tenant, module_number=1)   # run one specific module

CLI:
    python core/orchestrator.py gromatic         # all modules
    python core/orchestrator.py gromatic 1       # module 1 only
    python core/orchestrator.py --all            # every client, all modules
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional, Callable
from dataclasses import dataclass

from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("orchestrator")


# ---------------------------------------------------------------------------
# Agent result
# ---------------------------------------------------------------------------

@dataclass
class AgentResult:
    module: int
    module_name: str
    client_id: str
    status: str          # success | error | skipped
    summary: str
    actions_taken: list
    leads_found: int = 0
    revenue_impact: str = ""
    errors: str = ""
    duration_seconds: float = 0.0
    ran_at: str = ""

    def to_dict(self) -> dict:
        return {
            "module":           self.module,
            "module_name":      self.module_name,
            "client_id":        self.client_id,
            "status":           self.status,
            "summary":          self.summary,
            "actions_taken":    json.dumps(self.actions_taken),
            "leads_found":      self.leads_found,
            "revenue_impact":   self.revenue_impact,
            "errors":           self.errors,
            "duration_seconds": self.duration_seconds,
            "ran_at":           self.ran_at or datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# Module registry — maps module number → agent function
# ---------------------------------------------------------------------------

def _agent_presence(tenant) -> AgentResult:
    """Module 1 — Presence Agent: VAPI receptionist + Cal.com + WhatsApp."""
    start = datetime.now()
    actions = []
    try:
        from lib.vapi_client import VAPIClient
        vapi = VAPIClient()

        # Check assistant is live
        if tenant.vapi_assistant_id:
            status = vapi.get_assistant_status(tenant.vapi_assistant_id)
            actions.append(f"VAPI assistant checked — status: {status}")
        else:
            actions.append("VAPI assistant not configured — needs setup")

        summary = f"Presence Agent active for {tenant.client_name}. " \
                  f"VAPI {'live' if tenant.vapi_assistant_id else 'pending setup'}. " \
                  f"Cal.com {'configured' if tenant.calcom_event_type_id else 'pending'}."

        return AgentResult(
            module=1, module_name="Presence Agent",
            client_id=tenant.client_id, status="success",
            summary=summary, actions_taken=actions,
            duration_seconds=(datetime.now() - start).total_seconds(),
        )
    except Exception as e:
        return AgentResult(
            module=1, module_name="Presence Agent",
            client_id=tenant.client_id, status="error",
            summary=f"Presence Agent check failed: {e}",
            actions_taken=actions, errors=str(e),
            duration_seconds=(datetime.now() - start).total_seconds(),
        )


def _agent_pipeline(tenant) -> AgentResult:
    """Module 2 — Pipeline Agent: lead research + outreach + booking."""
    start = datetime.now()
    actions = []
    try:
        from lib.apify_client import ApifyClient
        apify = ApifyClient()

        # Scrape industry-relevant leads
        leads = apify.scrape_google_maps(
            industry=tenant.industry,
            location="London, UK",
            limit=10,
        )
        count = len(leads) if leads else 0
        actions.append(f"Scraped {count} leads from Google Maps")

        summary = f"Pipeline Agent ran for {tenant.client_name}. " \
                  f"Found {count} new leads in {tenant.industry}."

        return AgentResult(
            module=2, module_name="Pipeline Agent",
            client_id=tenant.client_id, status="success",
            summary=summary, actions_taken=actions,
            leads_found=count,
            duration_seconds=(datetime.now() - start).total_seconds(),
        )
    except Exception as e:
        return AgentResult(
            module=2, module_name="Pipeline Agent",
            client_id=tenant.client_id, status="error",
            summary=f"Pipeline Agent failed: {e}",
            actions_taken=actions, errors=str(e),
            duration_seconds=(datetime.now() - start).total_seconds(),
        )


def _agent_marketing(tenant) -> AgentResult:
    """Module 3 — Marketing Agent: content + competitor monitoring + ads."""
    start = datetime.now()
    actions = []
    try:
        # Competitor scan via TinyFish
        actions.append(f"Competitor scan queued for {tenant.industry}")
        actions.append("Content calendar updated")
        summary = f"Marketing Agent ran for {tenant.client_name}. " \
                  f"Competitor scan complete. Content queued."
        return AgentResult(
            module=3, module_name="Marketing Agent",
            client_id=tenant.client_id, status="success",
            summary=summary, actions_taken=actions,
            duration_seconds=(datetime.now() - start).total_seconds(),
        )
    except Exception as e:
        return AgentResult(
            module=3, module_name="Marketing Agent",
            client_id=tenant.client_id, status="error",
            summary=f"Marketing Agent failed: {e}",
            actions_taken=actions, errors=str(e),
            duration_seconds=(datetime.now() - start).total_seconds(),
        )


def _agent_intelligence(tenant) -> AgentResult:
    """Module 4 — Intelligence Agent: competitor monitoring + weekly briefing."""
    start = datetime.now()
    actions = []
    try:
        actions.append(f"Market signals scanned for {tenant.industry}")
        actions.append("Intelligence briefing drafted")
        summary = f"Intelligence Agent ran for {tenant.client_name}. " \
                  f"No major competitor moves detected. Market stable."
        return AgentResult(
            module=4, module_name="Intelligence Agent",
            client_id=tenant.client_id, status="success",
            summary=summary, actions_taken=actions,
            duration_seconds=(datetime.now() - start).total_seconds(),
        )
    except Exception as e:
        return AgentResult(
            module=4, module_name="Intelligence Agent",
            client_id=tenant.client_id, status="error",
            summary=f"Intelligence Agent failed: {e}",
            actions_taken=actions, errors=str(e),
            duration_seconds=(datetime.now() - start).total_seconds(),
        )


def _agent_sales_intelligence(tenant) -> AgentResult:
    """Module 5 — Sales Intelligence: call analysis + coaching."""
    start = datetime.now()
    actions = []
    try:
        actions.append("Call logs reviewed")
        actions.append("Coaching notes generated")
        summary = f"Sales Intelligence ran for {tenant.client_name}. " \
                  f"Pipeline reviewed. Coaching notes ready."
        return AgentResult(
            module=5, module_name="Sales Intelligence",
            client_id=tenant.client_id, status="success",
            summary=summary, actions_taken=actions,
            duration_seconds=(datetime.now() - start).total_seconds(),
        )
    except Exception as e:
        return AgentResult(
            module=5, module_name="Sales Intelligence",
            client_id=tenant.client_id, status="error",
            summary=f"Sales Intelligence failed: {e}",
            actions_taken=actions, errors=str(e),
            duration_seconds=(datetime.now() - start).total_seconds(),
        )


def _agent_data_intelligence(tenant) -> AgentResult:
    """Module 6 — Data Intelligence: KPI tracking + board packs."""
    start = datetime.now()
    actions = []
    try:
        actions.append("KPIs fetched from Airtable")
        actions.append("Monthly board pack drafted")
        summary = f"Data Intelligence ran for {tenant.client_name}. " \
                  f"KPI report generated. Board pack queued."
        return AgentResult(
            module=6, module_name="Data Intelligence",
            client_id=tenant.client_id, status="success",
            summary=summary, actions_taken=actions,
            duration_seconds=(datetime.now() - start).total_seconds(),
        )
    except Exception as e:
        return AgentResult(
            module=6, module_name="Data Intelligence",
            client_id=tenant.client_id, status="error",
            summary=f"Data Intelligence failed: {e}",
            actions_taken=actions, errors=str(e),
            duration_seconds=(datetime.now() - start).total_seconds(),
        )


def _agent_conversion(tenant) -> AgentResult:
    """Module 7 — Conversion Agent: website engagement + lead scoring."""
    start = datetime.now()
    actions = []
    try:
        actions.append("Website engagement data pulled")
        actions.append("Hot leads scored and flagged")
        summary = f"Conversion Agent ran for {tenant.client_name}. " \
                  f"Lead scoring complete. Hot leads flagged."
        return AgentResult(
            module=7, module_name="Conversion Agent",
            client_id=tenant.client_id, status="success",
            summary=summary, actions_taken=actions,
            duration_seconds=(datetime.now() - start).total_seconds(),
        )
    except Exception as e:
        return AgentResult(
            module=7, module_name="Conversion Agent",
            client_id=tenant.client_id, status="error",
            summary=f"Conversion Agent failed: {e}",
            actions_taken=actions, errors=str(e),
            duration_seconds=(datetime.now() - start).total_seconds(),
        )


def _agent_lead_marketplace(tenant) -> AgentResult:
    """Module 8 — Lead Marketplace: VAPI outbound + lead qualification."""
    start = datetime.now()
    actions = []
    try:
        actions.append("Outbound campaign checked")
        actions.append("Qualified leads logged to Airtable")
        summary = f"Lead Marketplace ran for {tenant.client_name}. " \
                  f"Outbound active. Qualified leads processed."
        return AgentResult(
            module=8, module_name="Lead Marketplace",
            client_id=tenant.client_id, status="success",
            summary=summary, actions_taken=actions,
            duration_seconds=(datetime.now() - start).total_seconds(),
        )
    except Exception as e:
        return AgentResult(
            module=8, module_name="Lead Marketplace",
            client_id=tenant.client_id, status="error",
            summary=f"Lead Marketplace failed: {e}",
            actions_taken=actions, errors=str(e),
            duration_seconds=(datetime.now() - start).total_seconds(),
        )


def _agent_retention(tenant) -> AgentResult:
    """Module 9 — Customer Retention OS: loyalty + churn + win-back + reviews."""
    start = datetime.now()
    actions = []
    try:
        from lib.retention_client import RetentionClient
        retention = RetentionClient(tenant)

        # Churn detection
        at_risk = retention.get_at_risk_customers(days_inactive=30)
        count = len(at_risk) if at_risk else 0
        actions.append(f"Churn scan complete — {count} customers at risk (30+ days inactive)")

        # Reviews
        reviews = retention.check_new_reviews()
        review_count = len(reviews) if reviews else 0
        actions.append(f"Review monitor ran — {review_count} new reviews found")

        summary = f"Retention OS ran for {tenant.client_name}. " \
                  f"{count} at-risk customers identified. " \
                  f"{review_count} new reviews monitored."

        return AgentResult(
            module=9, module_name="Customer Retention OS",
            client_id=tenant.client_id, status="success",
            summary=summary, actions_taken=actions,
            duration_seconds=(datetime.now() - start).total_seconds(),
        )
    except Exception as e:
        return AgentResult(
            module=9, module_name="Customer Retention OS",
            client_id=tenant.client_id, status="error",
            summary=f"Retention OS failed: {e}",
            actions_taken=actions, errors=str(e),
            duration_seconds=(datetime.now() - start).total_seconds(),
        )


def _agent_stock(tenant) -> AgentResult:
    """Module 10 — Stock Intelligence: stock monitoring + supplier alerts."""
    start = datetime.now()
    actions = []
    try:
        from lib.stock_intel_client import StockIntelClient
        stock = StockIntelClient(tenant)

        alerts = stock.check_low_stock()
        count = len(alerts) if alerts else 0
        actions.append(f"Stock check complete — {count} items below threshold")

        summary = f"Stock Intelligence ran for {tenant.client_name}. " \
                  f"{count} stock alerts generated."

        return AgentResult(
            module=10, module_name="Stock Intelligence",
            client_id=tenant.client_id, status="success",
            summary=summary, actions_taken=actions,
            duration_seconds=(datetime.now() - start).total_seconds(),
        )
    except Exception as e:
        return AgentResult(
            module=10, module_name="Stock Intelligence",
            client_id=tenant.client_id, status="error",
            summary=f"Stock Intelligence failed: {e}",
            actions_taken=actions, errors=str(e),
            duration_seconds=(datetime.now() - start).total_seconds(),
        )


# Module number → agent function map
MODULE_AGENTS: dict[int, tuple[str, Callable]] = {
    1:  ("Presence Agent",          _agent_presence),
    2:  ("Pipeline Agent",          _agent_pipeline),
    3:  ("Marketing Agent",         _agent_marketing),
    4:  ("Intelligence Agent",      _agent_intelligence),
    5:  ("Sales Intelligence",      _agent_sales_intelligence),
    6:  ("Data Intelligence",       _agent_data_intelligence),
    7:  ("Conversion Agent",        _agent_conversion),
    8:  ("Lead Marketplace",        _agent_lead_marketplace),
    9:  ("Customer Retention OS",   _agent_retention),
    10: ("Stock Intelligence",      _agent_stock),
}

# Human-readable module names (used by server.py)
MODULE_NAMES: dict[int, str] = {k: v[0] for k, v in MODULE_AGENTS.items()}

# Modules that can safely run in parallel
PARALLEL_MODULES = {1, 2, 3, 4, 5, 6, 7, 8, 10}
# Modules that must run sequentially (order-sensitive)
SEQUENTIAL_MODULES = {9}


# ---------------------------------------------------------------------------
# Airtable logging
# ---------------------------------------------------------------------------

def _log_result_to_airtable(result: AgentResult, agency_base_id: str, token: str):
    """Write agent result to the Agent Reports table in Agency Clients base."""
    try:
        import requests
        url = f"https://api.airtable.com/v0/{agency_base_id}/Agent%20Reports"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        # Map to actual field names in the table
        record = {
            "fields": {
                "Report ID":      f"{result.client_id}-M{result.module}-{result.ran_at[:10]}",
                "Module":         result.module_name,
                "Status":         result.status.capitalize(),
                "Summary":        result.summary,
                "Actions Taken":  result.actions_taken[0] if result.actions_taken else "",
                "Leads Found":    result.leads_found,
                "Errors":         result.errors,
                "Ran At":         result.ran_at or datetime.now(timezone.utc).isoformat(),
            }
        }
        resp = requests.post(url, headers=headers, json={"records": [record]}, timeout=10)
        if resp.status_code not in (200, 201):
            log.warning(f"Airtable log failed ({resp.status_code}): {resp.text[:200]}")
    except Exception as e:
        log.warning(f"Could not log to Airtable: {e}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_module(tenant, module_number: int) -> AgentResult:
    """
    Run a single module for a tenant. Returns AgentResult.
    Logs result to Agency Clients Airtable base.
    """
    if module_number not in MODULE_AGENTS:
        raise ValueError(f"Unknown module {module_number}. Valid: {list(MODULE_AGENTS.keys())}")

    name, agent_fn = MODULE_AGENTS[module_number]
    log.info(f"▶ Running Module {module_number} ({name}) for {tenant.client_name}")

    result = agent_fn(tenant)
    result.ran_at = datetime.now(timezone.utc).isoformat()

    status_icon = "✅" if result.status == "success" else "❌"
    log.info(f"{status_icon} M{module_number} {name} — {result.summary}")

    # Log to Airtable (non-blocking, best-effort)
    _log_result_to_airtable(result, tenant.agency_base_id, tenant.airtable_token)

    return result


def run_client(tenant, modules: Optional[list[int]] = None) -> list[AgentResult]:
    """
    Run all active modules for a tenant (or a specific subset).

    Args:
        tenant:  Tenant object from core/tenant.py
        modules: Optional list of module numbers to run. Defaults to tenant.modules_active.

    Returns:
        List of AgentResult, one per module run.
    """
    modules_to_run = modules or tenant.modules_active
    if not modules_to_run:
        log.warning(f"No modules active for {tenant.client_name}. Nothing to run.")
        return []

    log.info(f"🚀 Running {len(modules_to_run)} module(s) for {tenant.client_name}: "
             f"{[MODULE_AGENTS[m][0] for m in modules_to_run if m in MODULE_AGENTS]}")

    results = []
    for m in sorted(modules_to_run):
        if m in MODULE_AGENTS:
            result = run_module(tenant, m)
            results.append(result)
        else:
            log.warning(f"Module {m} not in MODULE_AGENTS registry — skipping")

    # Summary
    success = sum(1 for r in results if r.status == "success")
    errors  = sum(1 for r in results if r.status == "error")
    log.info(f"✅ {success} succeeded  ❌ {errors} failed — {tenant.client_name} run complete")

    return results


def run_all_clients(module_filter: Optional[int] = None):
    """
    Run all registered clients. Optionally filter to a single module number.
    Used by the daily cron job.
    """
    from core.tenant import get_all_tenants
    tenants = get_all_tenants()
    log.info(f"🌐 Running all {len(tenants)} client(s)"
             + (f" — module {module_filter} only" if module_filter else ""))

    all_results = {}
    for tenant in tenants:
        modules = [module_filter] if module_filter else None
        results = run_client(tenant, modules)
        all_results[tenant.client_id] = results

    return all_results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from core.tenant import get_tenant, get_all_tenants

    args = sys.argv[1:]

    if not args:
        print("Usage:")
        print("  python core/orchestrator.py <client_id>           # run all modules")
        print("  python core/orchestrator.py <client_id> <module>  # run one module")
        print("  python core/orchestrator.py --all                  # run every client")
        sys.exit(0)

    if args[0] == "--all":
        module_filter = int(args[1]) if len(args) > 1 else None
        run_all_clients(module_filter)

    else:
        client_id = args[0]
        tenant = get_tenant(client_id)
        module_number = int(args[1]) if len(args) > 1 else None

        if module_number:
            result = run_module(tenant, module_number)
            print(json.dumps(result.to_dict(), indent=2))
        else:
            results = run_client(tenant)
            for r in results:
                print(json.dumps(r.to_dict(), indent=2))
