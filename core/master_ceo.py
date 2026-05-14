"""
core/master_ceo.py — PluggedIN Master CEO Agent
=================================================
The Master CEO Agent sits above all client CEO Agents.
Every morning it:
  1. Calls report_up() on every registered client's CEO Agent
  2. Identifies which clients need attention
  3. Spots cross-client patterns (what's working, what's not)
  4. Produces a single daily brief for Pasha

Run daily at 07:30 via scheduler:
    python core/master_ceo.py

Or import and call directly:
    from core.master_ceo import MasterCEO
    brief = MasterCEO().daily_brief()
    print(brief.to_slack())
"""

import os
import json
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field

log = logging.getLogger("core.master_ceo")

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

try:
    import requests as _req
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ClientStatus:
    """One client's report as seen by the Master CEO."""
    client_id:               str
    client_name:             str
    industry:                str
    modules_active:          list
    total_activity:          int
    agents_idle:             list
    high_priority_actions:   list
    needs_attention:         bool
    one_line_status:         str


@dataclass
class MasterBriefing:
    """Pasha's daily brief from the Master CEO Agent."""
    date:                str
    total_clients:       int
    clients_needing_attention: list   # list[ClientStatus]
    clients_on_track:    list         # list[ClientStatus]
    total_mrr:           float
    agency_insights:     list         # list[str] — cross-client patterns
    pasha_priorities:    list         # list[str] — what Pasha should do today
    overnight_activity:  str          # summary of what agents did overnight
    generated_at:        str

    def to_slack(self) -> str:
        """Format as Slack/WhatsApp message for Pasha."""
        lines = [
            f"☀️ *PluggedIN Morning Brief — {self.date}*",
            f"📊 {self.total_clients} clients · £{self.total_mrr:,.0f}/mo MRR",
            "",
        ]
        if self.clients_needing_attention:
            lines.append("🔴 *Needs your attention:*")
            for c in self.clients_needing_attention:
                lines.append(f"  • {c.client_name} — {c.one_line_status}")
            lines.append("")

        if self.pasha_priorities:
            lines.append("✅ *Your priorities today:*")
            for i, p in enumerate(self.pasha_priorities, 1):
                lines.append(f"  {i}. {p}")
            lines.append("")

        if self.overnight_activity:
            lines.append(f"🤖 *Overnight:* {self.overnight_activity}")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "date":             self.date,
            "total_clients":    self.total_clients,
            "total_mrr":        self.total_mrr,
            "attention_needed": [c.client_id for c in self.clients_needing_attention],
            "pasha_priorities": self.pasha_priorities,
            "agency_insights":  self.agency_insights,
            "overnight_activity": self.overnight_activity,
            "generated_at":     self.generated_at,
        }


# ─────────────────────────────────────────────────────────────────────────────
# MASTER CEO AGENT
# ─────────────────────────────────────────────────────────────────────────────

class MasterCEO:
    """
    The PluggedIN Master CEO Agent.
    Reads all client CEO reports and produces Pasha's daily brief.
    """

    MODEL = "claude-sonnet-4-6"

    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        self._client = None
        self.agency_base  = os.getenv("AIRTABLE_BASE_AGENCY", "")
        self.token        = os.getenv("AIRTABLE_TOKEN", "")

    @property
    def anthropic_client(self):
        if self._client is None and _ANTHROPIC_AVAILABLE and self.anthropic_key:
            self._client = anthropic.Anthropic(api_key=self.anthropic_key)
        return self._client

    # ─── Collect all client reports ────────────────────────────────────────

    def _collect_all_reports(self) -> list[ClientStatus]:
        """
        Calls report_up() on every registered client's CEO Agent.
        Returns list of ClientStatus objects.
        """
        from core.tenant import get_all_tenants
        from core.ceo_agent import CEOAgent

        statuses = []
        tenants = get_all_tenants()

        if not tenants:
            log.info("No clients registered yet.")
            return []

        for tenant in tenants:
            try:
                ceo    = CEOAgent(tenant)
                report = ceo.report_up()
                statuses.append(ClientStatus(
                    client_id=report["client_id"],
                    client_name=report["client_name"],
                    industry=report["industry"],
                    modules_active=report["modules_active"],
                    total_activity=report["total_activity"],
                    agents_idle=report.get("agents_idle", []),
                    high_priority_actions=report.get("high_priority_actions", []),
                    needs_attention=report.get("needs_attention", False),
                    one_line_status=report.get("one_line_status", "—"),
                ))
                log.info(f"Report collected: {tenant.client_name} — {report['one_line_status']}")
            except Exception as e:
                log.error(f"Failed to collect report for {tenant.client_id}: {e}")
                statuses.append(ClientStatus(
                    client_id=tenant.client_id,
                    client_name=tenant.client_name,
                    industry=tenant.industry,
                    modules_active=tenant.modules_active,
                    total_activity=0,
                    agents_idle=[],
                    high_priority_actions=[],
                    needs_attention=False,
                    one_line_status="Error collecting report",
                ))

        return statuses

    # ─── Claude synthesis ──────────────────────────────────────────────────

    def _synthesise(self, statuses: list[ClientStatus]) -> tuple[list[str], list[str], str]:
        """
        Use Claude to synthesise cross-client patterns and produce
        Pasha's priorities + agency-level insights.
        Returns: (pasha_priorities, agency_insights, overnight_summary)
        """
        if not statuses:
            return (
                ["Add your first client to start generating insights"],
                [],
                "No clients registered yet."
            )

        status_text = "\n".join([
            f"- {s.client_name} ({s.industry}): {s.one_line_status}"
            + (f" ⚠️ {len(s.high_priority_actions)} high-priority actions"
               if s.needs_attention else "")
            for s in statuses
        ])

        prompt = f"""You are the Master CEO Agent for PluggedIN, an AI agency.
You manage {len(statuses)} client(s). Here is their status today:

{status_text}

Produce:
1. PASHA_PRIORITIES: 3 things Pasha should do today (specific, actionable)
2. AGENCY_INSIGHTS: 2 cross-client patterns you notice (what's working, what's a risk)
3. OVERNIGHT_SUMMARY: One sentence of what the agents did overnight

Return ONLY valid JSON:
{{
  "pasha_priorities": ["...", "...", "..."],
  "agency_insights": ["...", "..."],
  "overnight_summary": "..."
}}"""

        if not self.anthropic_client:
            return (
                [f"Review {s.client_name}" for s in statuses if s.needs_attention]
                or ["Check dashboard for updates"],
                ["Install anthropic SDK for AI synthesis: pip install anthropic"],
                f"Agents ran across {len(statuses)} client(s). Check PluggedIN OS for details."
            )

        try:
            msg = self.anthropic_client.messages.create(
                model=self.MODEL,
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = msg.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw.strip())
            return (
                data.get("pasha_priorities", []),
                data.get("agency_insights", []),
                data.get("overnight_summary", "Agents ran overnight."),
            )
        except Exception as e:
            log.error(f"Master CEO synthesis failed: {e}")
            return (
                ["Review agent logs in PluggedIN OS"],
                [],
                "Agents ran overnight — check PluggedIN OS for details."
            )

    # ─── Revenue calc ──────────────────────────────────────────────────────

    def _calc_mrr(self, statuses: list[ClientStatus]) -> float:
        """Calculate total MRR across all clients."""
        from core.tenant import get_tenant

        MODULE_PRICES = {
            1: 797, 2: 997, 3: 1197, 4: 697,
            5: 697, 6: 897, 7: 897,  8: 997,
            9: 497, 10: 297, 11: 597, 12: 397,  # M11 Reviews · M12 Job Hunter
        }

        total = 0.0
        for s in statuses:
            for m in s.modules_active:
                total += MODULE_PRICES.get(m, 0)
        return total

    # ─── Main entry point ──────────────────────────────────────────────────

    def daily_brief(self) -> MasterBriefing:
        """
        Generate Pasha's daily brief.
        Reads all client CEO reports → synthesises → returns MasterBriefing.
        """
        log.info("Master CEO Agent — generating daily brief...")

        statuses   = self._collect_all_reports()
        attention  = [s for s in statuses if s.needs_attention]
        on_track   = [s for s in statuses if not s.needs_attention]
        total_mrr  = self._calc_mrr(statuses)

        priorities, insights, overnight = self._synthesise(statuses)

        briefing = MasterBriefing(
            date=datetime.now(timezone.utc).strftime("%-d %B %Y"),
            total_clients=len(statuses),
            clients_needing_attention=attention,
            clients_on_track=on_track,
            total_mrr=total_mrr,
            agency_insights=insights,
            pasha_priorities=priorities,
            overnight_activity=overnight,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

        self._save_to_airtable(briefing)
        log.info(f"Daily brief complete — {len(statuses)} clients, £{total_mrr:,.0f} MRR, "
                 f"{len(attention)} needing attention")
        return briefing

    # ─── Persist ───────────────────────────────────────────────────────────

    def _save_to_airtable(self, briefing: MasterBriefing):
        """Save daily brief to Agency base → CEO Briefings table."""
        if not _REQUESTS_AVAILABLE or not self.token or not self.agency_base:
            return
        try:
            url = f"https://api.airtable.com/v0/{self.agency_base}/CEO%20Briefings"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type":  "application/json",
            }
            payload = {
                "fields": {
                    "Date":             briefing.date,
                    "Total Clients":    briefing.total_clients,
                    "Total MRR":        briefing.total_mrr,
                    "Priorities":       "\n".join(briefing.pasha_priorities),
                    "Insights":         "\n".join(briefing.agency_insights),
                    "Overnight":        briefing.overnight_activity,
                    "Generated At":     briefing.generated_at,
                }
            }
            _req.post(url, headers=headers, json=payload, timeout=10)
        except Exception as e:
            log.warning(f"Failed to save master brief to Airtable: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")

    from dotenv import load_dotenv
    load_dotenv()

    print("\n" + "="*55)
    print("  PluggedIN Master CEO Agent")
    print("="*55 + "\n")

    master  = MasterCEO()
    briefing = master.daily_brief()

    print(briefing.to_slack())
    print(f"\n[Generated at {briefing.generated_at}]")
