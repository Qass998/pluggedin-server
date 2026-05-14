"""
core/ceo_agent.py — PluggedIN Client CEO Agent
================================================
Every client has one CEO Agent. It:
  1. Reads all module outputs from Airtable (last 7 days)
  2. Analyses the data using Claude
  3. Produces a structured weekly briefing (JSON + Remotion-ready)
  4. Decides which subagents to trigger next
  5. Answers natural-language questions from the SME owner
  6. Reports its summary upward to the Master CEO Agent

Usage:
    from core.ceo_agent import CEOAgent
    from core.tenant import get_tenant

    tenant = get_tenant("gromatic")
    ceo = CEOAgent(tenant)

    # Get weekly briefing
    briefing = ceo.weekly_briefing()

    # Answer a question from the portal
    answer = ceo.ask("Why did my leads drop this week?")

    # Decide what to run next
    actions = ceo.decide_next_actions()

    # Generate report for Master CEO
    report = ceo.report_up()
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger("core.ceo_agent")

# ─── Try to import Anthropic SDK ──────────────────────────────────────────────
try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False
    log.warning("anthropic SDK not installed — CEO Agent will run in stub mode. pip install anthropic")

# ─── Try to import requests for Airtable ──────────────────────────────────────
try:
    import requests as _req
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AgentReport:
    """What a single module agent reports up to the CEO Agent."""
    module:       int
    module_name:  str
    status:       str          # "ok" | "warning" | "error" | "idle"
    summary:      str          # 1–2 sentence plain English summary
    key_metric:   str          # e.g. "17 leads found"
    delta:        str          # e.g. "+3 vs last week"
    actions_taken: list        # list of strings
    data_snapshot: dict = field(default_factory=dict)  # raw Airtable data


@dataclass
class Insight:
    """A single AI-generated insight from the CEO Agent."""
    priority:         str   # "HIGH" | "MEDIUM" | "LOW"
    headline:         str
    body:             str
    action:           str
    estimated_impact: str   # e.g. "£2,400/month"
    module:           Optional[int] = None


@dataclass
class GrowthCheckpoint:
    """Current state of one growth milestone."""
    name:        str
    metric:      str
    current:     float
    target:      float
    deadline:    str
    status:      str   # "ON TRACK" | "BEHIND" | "ACHIEVED"
    ai_note:     str
    action_btn:  str


@dataclass
class CEOBriefing:
    """Full weekly briefing produced by the CEO Agent."""
    client_name:    str
    client_id:      str
    week_ending:    str
    headline:       str          # One-line "state of the business"
    insights:       list         # list[Insight]
    agent_reports:  list         # list[AgentReport]
    checkpoints:    list         # list[GrowthCheckpoint]
    next_actions:   list         # list[str] — what agents will do next week
    remotion_data:  dict         # structured data for Remotion video renderer
    raw_prompt:     str = ""     # the prompt sent to Claude (for debugging)
    generated_at:   str = ""


# ─────────────────────────────────────────────────────────────────────────────
# MODULE METADATA (mirrors MODULES in dashboard)
# ─────────────────────────────────────────────────────────────────────────────
MODULE_NAMES = {
    1:  "Presence Agent",
    2:  "Pipeline Agent",
    3:  "Marketing Agent",
    4:  "Intelligence Agent",
    5:  "Sales Intelligence",
    6:  "Data Intelligence",
    7:  "Conversion Agent",
    8:  "Lead Marketplace",
    9:  "Customer Retention OS",
    10: "Stock Intelligence",
    11: "Reviews & Reputation Agent",
    12: "Job Hunter Agent",
}

# Airtable table name each module primarily writes to
MODULE_TABLES = {
    1:  "Agent Logs",
    2:  "Leads",
    3:  "Agent Logs",
    4:  "Agent Logs",
    5:  "Agent Logs",
    6:  "Agent Logs",
    7:  "Leads",
    8:  "Leads",
    9:  "Contacts",
    10: "Agent Logs",
    11: "Reviews",          # M11 writes all review data to a dedicated Reviews table
    12: "Job Applications", # M12 writes each matched job + tailored CV to Job Applications table
}


# ─────────────────────────────────────────────────────────────────────────────
# AIRTABLE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _airtable_fetch(base_id: str, table: str, token: str,
                    filter_formula: str = "", max_records: int = 50) -> list:
    """Fetch records from an Airtable table."""
    if not _REQUESTS_AVAILABLE:
        return []
    if not token or not base_id:
        return []
    try:
        url = f"https://api.airtable.com/v0/{base_id}/{table.replace(' ', '%20')}"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"maxRecords": max_records}
        if filter_formula:
            params["filterByFormula"] = filter_formula
        resp = _req.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("records", [])
    except Exception as e:
        log.warning(f"Airtable fetch failed ({table}): {e}")
    return []


def _summarise_records(records: list, module: int) -> dict:
    """
    Produce a compact data snapshot from raw Airtable records.
    Returns a dict Claude can read quickly.
    """
    if not records:
        return {"count": 0, "items": []}

    fields_list = [r.get("fields", {}) for r in records[:20]]

    # Module-specific summaries
    if module in (2, 7, 8):  # lead tables
        statuses = [f.get("Status", "unknown") for f in fields_list]
        status_counts = {}
        for s in statuses:
            status_counts[s] = status_counts.get(s, 0) + 1
        return {
            "count": len(records),
            "status_breakdown": status_counts,
            "sample_names": [f.get("Name", f.get("Company", "—")) for f in fields_list[:5]],
        }

    if module == 9:  # contacts / retention
        high_risk = sum(1 for f in fields_list if f.get("ChurnRisk") == "HIGH")
        return {
            "count": len(records),
            "high_churn_risk": high_risk,
            "sample": [f.get("Name", "—") for f in fields_list[:5]],
        }

    # Generic: agent logs
    outcomes = [f.get("Outcome", f.get("Status", "—")) for f in fields_list]
    return {
        "count": len(records),
        "recent_outcomes": outcomes[:10],
        "last_ran": fields_list[0].get("Ran At", "—") if fields_list else "—",
    }


# ─────────────────────────────────────────────────────────────────────────────
# CEO AGENT
# ─────────────────────────────────────────────────────────────────────────────

class CEOAgent:
    """
    Per-client CEO Agent. Orchestrates all module agents, synthesises
    data, generates briefings, and answers owner questions.
    """

    def __init__(self, tenant):
        """
        Args:
            tenant: Tenant dataclass from core.tenant
        """
        self.tenant = tenant
        self.client_id   = tenant.client_id
        self.client_name = tenant.client_name
        self.industry    = tenant.industry
        self.modules     = tenant.modules_active
        self.base_id     = tenant.airtable_base_id
        self.token       = os.getenv("AIRTABLE_TOKEN", "")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        self._client = None  # Anthropic client, lazy-loaded

    @property
    def anthropic_client(self):
        if self._client is None and _ANTHROPIC_AVAILABLE and self.anthropic_key:
            self._client = anthropic.Anthropic(api_key=self.anthropic_key)
        return self._client

    # ─── Data collection ───────────────────────────────────────────────────

    def _collect_module_data(self) -> dict[int, dict]:
        """
        Pull last 7 days of data from Airtable for each active module.
        Returns {module_number: data_snapshot}
        """
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        data = {}

        for m in self.modules:
            table = MODULE_TABLES.get(m, "Agent Logs")
            records = _airtable_fetch(
                self.base_id, table, self.token,
                max_records=50
            )
            data[m] = _summarise_records(records, m)
            log.info(f"[{self.client_id}] M{m} data: {data[m].get('count', 0)} records")

        return data

    def _build_agent_reports(self, data: dict) -> list[AgentReport]:
        """Turn raw data snapshots into structured AgentReport objects."""
        reports = []
        for m in self.modules:
            snap = data.get(m, {})
            count = snap.get("count", 0)
            name  = MODULE_NAMES.get(m, f"Module {m}")

            # Derive a plain-English summary per module type
            if m == 1:
                summary = f"Presence Agent handled inbound enquiries. {count} interactions logged."
                metric  = f"{count} interactions"
            elif m in (2, 7, 8):
                new_leads = snap.get("status_breakdown", {}).get("new", 0)
                summary = f"Pipeline Agent found {count} leads. {new_leads} new this week."
                metric  = f"{count} leads in pipeline"
            elif m == 9:
                risk = snap.get("high_churn_risk", 0)
                summary = f"Retention OS monitoring {count} contacts. {risk} flagged as high churn risk."
                metric  = f"{risk} high-risk customers"
            elif m == 10:
                summary = f"Stock Intelligence logged {count} movements. Threshold alerts checked."
                metric  = f"{count} stock events"
            else:
                outcomes = snap.get("recent_outcomes", [])
                ok_count = sum(1 for o in outcomes if "ok" in str(o).lower() or "success" in str(o).lower())
                summary = f"{name} ran {count} cycles. {ok_count} completed successfully."
                metric  = f"{count} runs"

            status = "ok" if count > 0 else "idle"

            reports.append(AgentReport(
                module=m,
                module_name=name,
                status=status,
                summary=summary,
                key_metric=metric,
                delta="—",  # TODO: compare vs prior week
                actions_taken=[],
                data_snapshot=snap,
            ))

        return reports

    # ─── Claude analysis ───────────────────────────────────────────────────

    def _claude(self, prompt: str, max_tokens: int = 1200) -> str:
        """Call Claude claude-sonnet-4-6 with a prompt. Returns text."""
        if not self.anthropic_client:
            return json.dumps(_stub_insights(self.industry))

        try:
            msg = self.anthropic_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except Exception as e:
            log.error(f"Claude API error: {e}")
            return json.dumps(_stub_insights(self.industry))

    def _build_analysis_prompt(self, agent_reports: list[AgentReport]) -> str:
        """Build the master advisory prompt for this client."""
        reports_text = "\n".join([
            f"- M{r.module} {r.module_name}: {r.summary} ({r.key_metric})"
            for r in agent_reports
        ])

        return f"""You are the AI CEO Advisor for {self.client_name}, a {self.industry} business.

ACTIVE MODULES THIS WEEK:
{reports_text}

Your job: produce exactly 3 business insights ranked by financial impact (highest first).

Rules:
- Be specific and quantified. Never vague.
- Every insight must trace to revenue gained or cost saved.
- If an agent can solve the problem, say so and name the module.
- Reference actual data points from the reports above.

Return ONLY valid JSON — an array of 3 objects:
[
  {{
    "priority": "HIGH",
    "headline": "...",
    "body": "2-3 sentences with specific data.",
    "action": "One specific action the owner can take today.",
    "estimated_impact": "£X/month or X% improvement",
    "module": 1
  }}
]"""

    def _parse_insights(self, raw: str) -> list[Insight]:
        """Parse Claude's JSON response into Insight objects."""
        try:
            # Strip markdown code fences if present
            clean = raw.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            data = json.loads(clean.strip())
            return [
                Insight(
                    priority=i.get("priority", "MEDIUM"),
                    headline=i.get("headline", ""),
                    body=i.get("body", ""),
                    action=i.get("action", ""),
                    estimated_impact=i.get("estimated_impact", ""),
                    module=i.get("module"),
                )
                for i in data
            ]
        except Exception as e:
            log.warning(f"Failed to parse insights JSON: {e}\nRaw: {raw[:200]}")
            return _default_insights(self.industry)

    # ─── Growth checkpoints ────────────────────────────────────────────────

    def _build_checkpoints(self, agent_reports: list[AgentReport]) -> list[GrowthCheckpoint]:
        """
        Generate or update growth checkpoints based on current data.
        In production: load from Airtable and update. Here: derive from data.
        """
        checkpoints = []

        # Pull lead count from pipeline agents if active
        lead_count = 0
        for r in agent_reports:
            if r.module in (2, 7, 8):
                lead_count = int(r.key_metric.split()[0]) if r.key_metric else 0
                break

        # Checkpoint 1 — Lead volume (if pipeline module active)
        if any(m in self.modules for m in [2, 7, 8]):
            target = 20
            status = "ON TRACK" if lead_count >= target * 0.7 else "BEHIND"
            checkpoints.append(GrowthCheckpoint(
                name="Hit 20 Qualified Leads/Month",
                metric="leads_qualified_this_month",
                current=float(lead_count),
                target=float(target),
                deadline="2025-09-01",
                status=status,
                ai_note=f"Currently at {lead_count}/{target}. "
                        + ("On track — keep pipeline agent running daily."
                           if status == "ON TRACK"
                           else "Expand scrape to 3 more postcodes to close the gap."),
                action_btn="Expand pipeline coverage →",
            ))

        # Checkpoint 2 — Response coverage (if M1 active)
        if 1 in self.modules:
            checkpoints.append(GrowthCheckpoint(
                name="100% Enquiry Coverage",
                metric="unanswered_calls_pct",
                current=5.0,
                target=0.0,
                deadline="2025-08-01",
                status="ON TRACK",
                ai_note="Presence Agent is active. Enable weekend hours to reach 100% coverage.",
                action_btn="Enable weekend coverage →",
            ))

        # Checkpoint 3 — Retention (if M9 active)
        if 9 in self.modules:
            churn_risk = 0
            for r in agent_reports:
                if r.module == 9:
                    churn_risk = r.data_snapshot.get("high_churn_risk", 0)
            checkpoints.append(GrowthCheckpoint(
                name="Churn Risk Below 5%",
                metric="high_churn_risk_count",
                current=float(churn_risk),
                target=0.0,
                deadline="2025-08-15",
                status="ON TRACK" if churn_risk == 0 else "BEHIND",
                ai_note=f"{churn_risk} customers flagged as high churn risk. "
                        + "Win-back campaign ready to send — approve to activate.",
                action_btn="Launch win-back campaign →",
            ))

        # Always have at least one checkpoint
        if not checkpoints:
            checkpoints.append(GrowthCheckpoint(
                name="Full Agent Coverage Active",
                metric="modules_setup_pct",
                current=len(self.modules) * 20.0,
                target=100.0,
                deadline="2025-08-01",
                status="ON TRACK",
                ai_note="Complete remaining module setup steps to unlock full agent capability.",
                action_btn="View setup checklist →",
            ))

        return checkpoints[:3]  # Always return max 3

    # ─── Public API ────────────────────────────────────────────────────────

    def weekly_briefing(self) -> CEOBriefing:
        """
        Generate the full weekly briefing for this client.
        Called by: scheduler (Friday 07:45), portal on demand, Master CEO.
        """
        log.info(f"[{self.client_id}] Generating weekly briefing...")

        # 1. Collect data
        raw_data = self._collect_module_data()

        # 2. Build agent reports
        agent_reports = self._build_agent_reports(raw_data)

        # 3. Run Claude analysis
        prompt = self._build_analysis_prompt(agent_reports)
        raw_response = self._claude(prompt)
        insights = self._parse_insights(raw_response)

        # 4. Build growth checkpoints
        checkpoints = self._build_checkpoints(agent_reports)

        # 5. Determine next actions
        next_actions = _derive_next_actions(self.modules, insights)

        # 6. Build Remotion data payload
        remotion_data = _build_remotion_payload(
            client_name=self.client_name,
            industry=self.industry,
            agent_reports=agent_reports,
            insights=insights,
            checkpoints=checkpoints,
            next_actions=next_actions,
        )

        briefing = CEOBriefing(
            client_name=self.client_name,
            client_id=self.client_id,
            week_ending=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            headline=_derive_headline(agent_reports, insights),
            insights=insights,
            agent_reports=agent_reports,
            checkpoints=checkpoints,
            next_actions=next_actions,
            remotion_data=remotion_data,
            raw_prompt=prompt,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

        # 7. Persist to Airtable
        _save_briefing(briefing, self.base_id, self.token)

        log.info(f"[{self.client_id}] Briefing complete — {len(insights)} insights, "
                 f"{len(agent_reports)} agent reports")
        return briefing

    def ask(self, question: str) -> str:
        """
        Answer a natural-language question from the SME owner.
        Called from the portal's "Ask your advisor" chat input.

        Example:
            ceo.ask("Why did my leads drop this week?")
            ceo.ask("What should I focus on tomorrow?")
            ceo.ask("How close am I to hitting £10k/month?")
        """
        raw_data = self._collect_module_data()
        agent_reports = self._build_agent_reports(raw_data)

        reports_text = "\n".join([
            f"- M{r.module} {r.module_name}: {r.summary}"
            for r in agent_reports
        ])

        prompt = f"""You are the AI CEO Advisor for {self.client_name}, a {self.industry} business.

Current agent data (last 7 days):
{reports_text}

The business owner asks: "{question}"

Answer in 2–4 sentences. Be specific, use the data above, and end with one clear action they can take.
Do not use bullet points. Write as a trusted advisor, not a chatbot."""

        return self._claude(prompt, max_tokens=400)

    def decide_next_actions(self) -> list[dict]:
        """
        Decide which subagents to run next based on current data.
        Returns a list of action dicts with module + reason + priority.
        Called by: orchestrator scheduler, Master CEO Agent.
        """
        raw_data = self._collect_module_data()
        actions = []

        for m in self.modules:
            snap = raw_data.get(m, {})
            count = snap.get("count", 0)
            name  = MODULE_NAMES.get(m, f"Module {m}")

            # Simple priority rules — extend with ML scoring later
            if count == 0:
                priority = "HIGH"
                reason   = f"{name} has no data — needs to run immediately"
            elif m in (2, 7, 8) and count < 10:
                priority = "HIGH"
                reason   = f"Lead pipeline thin ({count} leads) — run scrape now"
            elif m == 9 and snap.get("high_churn_risk", 0) > 0:
                priority = "HIGH"
                reason   = f"{snap['high_churn_risk']} high-risk customers need win-back"
            else:
                priority = "NORMAL"
                reason   = f"Scheduled run for {name}"

            actions.append({
                "module":   m,
                "name":     name,
                "priority": priority,
                "reason":   reason,
                "run_now":  priority == "HIGH",
            })

        # Sort: HIGH first
        actions.sort(key=lambda x: 0 if x["priority"] == "HIGH" else 1)
        return actions

    def report_up(self) -> dict:
        """
        Generate a compact summary report for the Master CEO Agent.
        Called daily by master_ceo.py to aggregate across all clients.
        """
        raw_data  = self._collect_module_data()
        reports   = self._build_agent_reports(raw_data)
        actions   = self.decide_next_actions()
        high_prio = [a for a in actions if a["priority"] == "HIGH"]

        total_activity = sum(r.data_snapshot.get("count", 0) for r in reports)

        return {
            "client_id":       self.client_id,
            "client_name":     self.client_name,
            "industry":        self.industry,
            "modules_active":  self.modules,
            "total_activity":  total_activity,
            "agents_idle":     [r.module_name for r in reports if r.status == "idle"],
            "high_priority_actions": high_prio,
            "needs_attention": len(high_prio) > 0,
            "one_line_status": _one_line_status(reports, high_prio),
            "generated_at":    datetime.now(timezone.utc).isoformat(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _derive_headline(reports: list[AgentReport], insights: list[Insight]) -> str:
    """One-line state-of-the-business headline."""
    if not insights:
        return "Agents running — data collecting."
    top = insights[0]
    return top.headline if top.headline else "Agents active — see insights below."


def _derive_next_actions(modules: list[int], insights: list[Insight]) -> list[str]:
    """Derive next week's agent actions from insights."""
    actions = []
    for ins in insights:
        if ins.action:
            actions.append(ins.action)
    # Always add a default for each active module
    for m in modules[:3]:
        actions.append(f"M{m} {MODULE_NAMES.get(m, 'Agent')} — scheduled run")
    return list(dict.fromkeys(actions))[:5]  # deduplicate, max 5


def _one_line_status(reports: list[AgentReport], high_prio: list) -> str:
    active = sum(1 for r in reports if r.status == "ok")
    total  = len(reports)
    if high_prio:
        return f"{active}/{total} agents active — {len(high_prio)} HIGH priority action(s) needed"
    return f"{active}/{total} agents active — on track"


def _build_remotion_payload(client_name, industry, agent_reports,
                             insights, checkpoints, next_actions) -> dict:
    """
    Structured data payload for Remotion video renderer.
    Passed to remotion/generate.js as JSON.
    """
    top_kpis = []
    for r in agent_reports[:3]:
        top_kpis.append({
            "label": r.module_name,
            "value": r.key_metric,
            "delta": r.delta,
            "status": r.status,
        })

    top_insight = None
    if insights:
        i = insights[0]
        top_insight = {
            "priority":        i.priority,
            "headline":        i.headline,
            "body":            i.body,
            "estimated_impact": i.estimated_impact,
        }

    top_checkpoint = None
    if checkpoints:
        c = checkpoints[0]
        pct = int((c.current / c.target * 100)) if c.target > 0 else 100
        top_checkpoint = {
            "name":    c.name,
            "pct":     min(pct, 100),
            "status":  c.status,
            "ai_note": c.ai_note,
        }

    return {
        "client_name":     client_name,
        "industry":        industry,
        "kpis":            top_kpis,
        "top_insight":     top_insight,
        "checkpoint":      top_checkpoint,
        "next_actions":    next_actions[:3],
        "week_ending":     datetime.now(timezone.utc).strftime("%-d %B %Y"),
    }


def _save_briefing(briefing: CEOBriefing, base_id: str, token: str):
    """Persist briefing summary to Airtable CEO Briefings table."""
    if not _REQUESTS_AVAILABLE or not token or not base_id:
        log.info("Skipping Airtable save (no token/base or requests unavailable)")
        return
    try:
        url = f"https://api.airtable.com/v0/{base_id}/CEO%20Briefings"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json",
        }
        payload = {
            "fields": {
                "Client":       briefing.client_name,
                "Week Ending":  briefing.week_ending,
                "Headline":     briefing.headline,
                "Insights":     json.dumps([
                    {"priority": i.priority, "headline": i.headline, "impact": i.estimated_impact}
                    for i in briefing.insights
                ]),
                "Next Actions": "\n".join(briefing.next_actions),
                "Generated At": briefing.generated_at,
            }
        }
        _req.post(url, headers=headers, json=payload, timeout=10)
        log.info(f"Briefing saved to Airtable for {briefing.client_name}")
    except Exception as e:
        log.warning(f"Failed to save briefing to Airtable: {e}")


def _default_insights(industry: str) -> list[Insight]:
    """Fallback insights if Claude is unavailable."""
    return [
        Insight(
            priority="HIGH",
            headline="Enable full agent coverage to unlock data-driven insights",
            body=f"Your {industry} business has agents configured but needs more data to generate specific financial insights. Complete the remaining setup steps.",
            action="Complete module setup checklist",
            estimated_impact="Unlocks full advisory capability",
        ),
    ]


def _stub_insights(industry: str) -> list:
    """JSON stub when Anthropic SDK not available."""
    return [
        {
            "priority": "HIGH",
            "headline": "Anthropic SDK not installed — running in stub mode",
            "body": "Install the anthropic package to enable AI insights: pip install anthropic",
            "action": "pip install anthropic",
            "estimated_impact": "Unlocks full AI advisory",
            "module": None,
        }
    ]


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from dotenv import load_dotenv
    load_dotenv()

    from core.tenant import get_tenant, list_tenants

    if len(sys.argv) > 1:
        client_id = sys.argv[1]
        question  = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    else:
        tenants = list_tenants()
        if not tenants:
            print("No clients registered. Add one first.")
            sys.exit(1)
        client_id = tenants[0]
        question  = None

    print(f"\n{'='*55}")
    print(f"  CEO Agent — {client_id}")
    print(f"{'='*55}\n")

    tenant = get_tenant(client_id)
    ceo    = CEOAgent(tenant)

    if question:
        print(f"Question: {question}\n")
        answer = ceo.ask(question)
        print(f"Advisor: {answer}\n")
    else:
        briefing = ceo.weekly_briefing()
        print(f"Client:     {briefing.client_name}")
        print(f"Week:       {briefing.week_ending}")
        print(f"Headline:   {briefing.headline}\n")
        print("INSIGHTS:")
        for i, ins in enumerate(briefing.insights, 1):
            print(f"  {i}. [{ins.priority}] {ins.headline}")
            print(f"     Impact: {ins.estimated_impact}")
            print(f"     Action: {ins.action}\n")
        print("AGENT REPORTS:")
        for r in briefing.agent_reports:
            print(f"  M{r.module} {r.module_name}: {r.key_metric} ({r.status})")
        print("\nNEXT ACTIONS:")
        for a in briefing.next_actions:
            print(f"  • {a}")
