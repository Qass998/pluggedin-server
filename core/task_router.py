"""
core/task_router.py — PluggedIN CEO Agent Task Router
=======================================================
Pasha gives a natural language command.
The Task Router:
  1. Reads the command with Claude → decides which M1–M12 agents to activate
  2. Builds a task plan (agents, params, run order: parallel or sequential)
  3. Executes the plan — calls the right agent functions
  4. Collects results → asks Claude to summarise for Pasha
  5. Returns a structured TaskResult ready for the dashboard

This is what powers the CEO Agent chat panel.

Usage:
    from core.task_router import TaskRouter

    router = TaskRouter()
    result = router.run("Find me 20 legal firms in Manchester and draft outreach")
    print(result.summary)
    for step in result.steps:
        print(step["agent"], step["status"], step["output_summary"])
"""

import os
import json
import logging
import time
import threading
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Callable, Optional

from dotenv import load_dotenv
load_dotenv()

log = logging.getLogger("core.task_router")

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# AGENT REGISTRY
# Maps module number → human name + executor function name + description
# Executor functions live in core/orchestrator.py (client agents)
# and lib/* (agency/internal agents)
# ─────────────────────────────────────────────────────────────────────────────

AGENT_REGISTRY = {
    1:  {
        "name":        "Presence Agent",
        "description": "Manages VAPI voice receptionist, call handling, booking. Use when: answer calls, check call logs, configure VAPI, booking setup.",
        "scope":       "client",
        "executor":    "_agent_presence",
    },
    2:  {
        "name":        "Pipeline Agent",
        "description": "Scrapes leads from Google Maps, LinkedIn, directories. Qualifies against ICP. Drafts outreach. Use when: find leads, prospect, build pipeline.",
        "scope":       "client",
        "executor":    "_agent_pipeline",
    },
    3:  {
        "name":        "Marketing Agent",
        "description": "Competitor monitoring, content calendar, social posts, Creatomate ads. Use when: create content, monitor competitors, run campaigns.",
        "scope":       "client",
        "executor":    "_agent_marketing",
    },
    4:  {
        "name":        "Intelligence Agent",
        "description": "Deep competitor tracking, market positioning, weekly intelligence report. Use when: competitor analysis, market research, positioning.",
        "scope":       "client",
        "executor":    "_agent_intelligence",
    },
    5:  {
        "name":        "Sales Intelligence",
        "description": "Analyses call transcripts, flags objections, generates coaching notes. Use when: analyse calls, improve conversion, sales coaching.",
        "scope":       "client",
        "executor":    "_agent_sales",
    },
    6:  {
        "name":        "Data Intelligence",
        "description": "Financial reporting, board packs, cashflow forecasts, KPI dashboards. Use when: generate reports, financial analysis, board pack.",
        "scope":       "client",
        "executor":    "_agent_data",
    },
    7:  {
        "name":        "Conversion Agent",
        "description": "Website visitor scoring, hot lead alerts, conversion optimisation. Use when: improve website conversion, score visitors, flag hot leads.",
        "scope":       "client",
        "executor":    "_agent_conversion",
    },
    8:  {
        "name":        "Lead Marketplace",
        "description": "Outbound VAPI campaigns to purchased lead lists. Qualifies by conversation. Books into calendar. Use when: run outbound, dial lists, qualify leads.",
        "scope":       "client",
        "executor":    "_agent_marketplace",
    },
    9:  {
        "name":        "Customer Retention OS",
        "description": "Churn risk scoring, win-back WhatsApp campaigns, review monitoring, NPS. Use when: reduce churn, win-back customers, monitor reviews.",
        "scope":       "client",
        "executor":    "_agent_retention",
    },
    10: {
        "name":        "Stock Intelligence",
        "description": "Monitors stock levels, generates supplier orders, demand forecasting. Use when: check stock, order supplies, manage inventory.",
        "scope":       "client",
        "executor":    "_agent_stock",
    },
    11: {
        "name":        "Reviews & Reputation Agent",
        "description": "Generates review requests, drafts responses, dispute handling, competitor review benchmarking. Use when: get more reviews, respond to reviews, improve rating.",
        "scope":       "client",
        "executor":    "_agent_reviews",
    },
    12: {
        "name":        "Job Hunter Agent",
        "description": "Scrapes Indeed, Reed, LinkedIn Jobs. Scores listings. Generates tailored CV + cover letter. Use when: find jobs, write CV, apply for roles.",
        "scope":       "agency",
        "executor":    "_agent_job_hunter",
    },
}

# Agency (internal) agents — no client context needed
AGENCY_AGENTS = {
    "product_research": {
        "name":        "Digital Products Research",
        "description": "Scans Gumroad, AppSumo, Product Hunt for trending digital product opportunities. Use when: find products to build/sell, market research.",
        "executor":    "_agency_product_research",
    },
    "redesign_engine": {
        "name":        "Website Redesign Engine",
        "description": "Audits prospect websites, generates redesign briefs, creates pitch decks. Use when: audit a website, generate redesign proposal.",
        "executor":    "_agency_redesign",
    },
    "lead_prospector": {
        "name":        "SME Lead Prospector",
        "description": "Finds SMEs who are earning but have no systems. Qualifies and drafts cold outreach. Use when: find PluggedIN prospects, generate leads for the agency.",
        "executor":    "_agency_prospector",
    },
    "content_machine": {
        "name":        "Content Machine",
        "description": "Generates LinkedIn posts, cold email sequences, case studies for PluggedIN's own brand. Use when: create content, write emails, generate posts.",
        "executor":    "_agency_content",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TaskStep:
    agent_id:      str          # "M2" or "product_research"
    agent_name:    str
    status:        str          # queued | running | done | error
    params:        dict = field(default_factory=dict)
    output_summary: str = ""
    actions_taken:  list = field(default_factory=list)
    duration_s:    float = 0.0
    error:         str = ""


@dataclass
class TaskResult:
    command:    str
    plan:       list            # list of dicts from Claude's planning step
    steps:      list            # list[TaskStep]
    summary:    str             # Claude's plain-English summary for Pasha
    status:     str             # done | partial | error
    run_mode:   str             # parallel | sequential
    started_at: str = ""
    finished_at:str = ""
    client_id:  str = ""        # set if command was for a specific client

    def to_dict(self) -> dict:
        return {
            "command":     self.command,
            "summary":     self.summary,
            "status":      self.status,
            "run_mode":    self.run_mode,
            "started_at":  self.started_at,
            "finished_at": self.finished_at,
            "client_id":   self.client_id,
            "steps": [
                {
                    "agent_id":      s.agent_id,
                    "agent_name":    s.agent_name,
                    "status":        s.status,
                    "output_summary":s.output_summary,
                    "actions_taken": s.actions_taken,
                    "duration_s":    s.duration_s,
                    "error":         s.error,
                }
                for s in self.steps
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# TASK ROUTER
# ─────────────────────────────────────────────────────────────────────────────

class TaskRouter:
    """
    The CEO Agent's execution engine.
    Reads a natural language command, picks the right agents, runs them,
    and returns a plain-English result for Pasha.
    """

    MODEL = "claude-sonnet-4-6"

    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        progress_callback: optional function called with (step_id, status, message)
        so the dashboard can show live progress.
        """
        self.anthropic_key       = os.getenv("ANTHROPIC_API_KEY", "")
        self.airtable_token      = os.getenv("AIRTABLE_TOKEN", "")
        self.airtable_base       = os.getenv("AIRTABLE_BASE_PLUGGEDIN", "")
        self._claude             = None
        self.progress_callback   = progress_callback or (lambda *a: None)

    @property
    def claude(self):
        if self._claude is None and _ANTHROPIC_AVAILABLE and self.anthropic_key:
            self._claude = anthropic.Anthropic(api_key=self.anthropic_key)
        return self._claude

    # ─── Main entry point ─────────────────────────────────────────────────

    def run(self, command: str, client_id: str = "") -> TaskResult:
        """
        Full pipeline:
          1. Plan — Claude decides which agents + params + order
          2. Execute — run selected agents
          3. Summarise — Claude writes Pasha's result in plain English
        """
        started = datetime.now(timezone.utc).isoformat()
        log.info(f"Task Router — command: '{command[:80]}'")
        self.progress_callback("plan", "running", "Reading your command...")

        # Step 1: Plan
        plan = self._plan(command, client_id)
        log.info(f"Plan: {len(plan['agents'])} agent(s), mode={plan['run_mode']}")
        self.progress_callback("plan", "done", f"Plan ready — {len(plan['agents'])} agent(s) selected")

        # Step 2: Execute
        steps = self._execute(plan, client_id, command)

        # Step 3: Summarise
        self.progress_callback("summary", "running", "Summarising results...")
        summary = self._summarise(command, steps)
        self.progress_callback("summary", "done", "Done")

        finished = datetime.now(timezone.utc).isoformat()
        overall  = "done" if all(s.status in ("done","skipped") for s in steps) else \
                   "partial" if any(s.status == "done" for s in steps) else "error"

        result = TaskResult(
            command=command,
            plan=plan["agents"],
            steps=steps,
            summary=summary,
            status=overall,
            run_mode=plan.get("run_mode", "sequential"),
            started_at=started,
            finished_at=finished,
            client_id=client_id,
        )
        self._save_to_airtable(result)
        return result

    # ─── Step 1: Plan ─────────────────────────────────────────────────────

    def _plan(self, command: str, client_id: str) -> dict:
        """
        Ask Claude to read the command and decide:
        - Which agents to activate (M1–M12 and/or agency agents)
        - What params to pass each agent
        - Whether to run in parallel or sequentially
        - Whether a client_id is needed
        """
        if not self.claude:
            return self._stub_plan(command)

        registry_text = "\n".join([
            f"M{k}: {v['name']} — {v['description']}"
            for k, v in AGENT_REGISTRY.items()
        ])
        agency_text = "\n".join([
            f"{k}: {v['name']} — {v['description']}"
            for k, v in AGENCY_AGENTS.items()
        ])

        prompt = f"""You are the CEO Agent for PluggedIN, an AI agency OS.

Pasha has given you a command. Your job is to decide which agents to activate to complete it.

AVAILABLE CLIENT AGENTS (need a client_id to run):
{registry_text}

AVAILABLE AGENCY AGENTS (run for PluggedIN itself, no client needed):
{agency_text}

COMMAND FROM PASHA: "{command}"
CURRENT CLIENT ID (if relevant): "{client_id or 'none'}"

Decide:
1. Which agents to activate (can be one or many)
2. What params each needs (keywords, location, client_id, etc.)
3. Whether to run them in parallel (independent tasks) or sequentially (one feeds the next)
4. A one-line explanation of what you're doing

Rules:
- Only activate agents that are actually needed for the command
- If the command is about a specific client, set needs_client=true
- If agents can run independently, use parallel
- If agent B needs agent A's output, use sequential
- For job hunting, always use M12
- For finding PluggedIN leads/prospects, use lead_prospector
- For writing content for PluggedIN, use content_machine
- For client-specific tasks (a named client), use client agents with their client_id

Return ONLY valid JSON:
{{
  "explanation": "One sentence — what you're going to do",
  "run_mode": "parallel" | "sequential",
  "needs_client": true | false,
  "agents": [
    {{
      "id": "M2" | "product_research" | etc,
      "name": "Agent name",
      "reason": "Why this agent",
      "params": {{
        "keywords": "...",
        "location": "...",
        "client_id": "..."
      }}
    }}
  ]
}}"""

        try:
            msg = self.claude.messages.create(
                model=self.MODEL,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = msg.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            plan = json.loads(raw.strip())
            log.info(f"Plan: {plan.get('explanation','')}")
            return plan
        except Exception as e:
            log.error(f"Planning failed: {e}")
            return self._stub_plan(command)

    def _stub_plan(self, command: str) -> dict:
        """Fallback plan when Claude is unavailable."""
        cmd = command.lower()
        if any(w in cmd for w in ["job", "cv", "apply", "role"]):
            agents = [{"id": "M12", "name": "Job Hunter Agent", "reason": "Job hunting command", "params": {"keywords": command}}]
        elif any(w in cmd for w in ["lead", "prospect", "find business"]):
            agents = [{"id": "lead_prospector", "name": "SME Lead Prospector", "reason": "Lead gen command", "params": {}}]
        elif any(w in cmd for w in ["content", "post", "linkedin", "email"]):
            agents = [{"id": "content_machine", "name": "Content Machine", "reason": "Content command", "params": {}}]
        elif any(w in cmd for w in ["product", "build", "opportunity"]):
            agents = [{"id": "product_research", "name": "Product Research", "reason": "Product command", "params": {}}]
        else:
            agents = [{"id": "M2", "name": "Pipeline Agent", "reason": "Default: lead gen", "params": {}}]
        return {"explanation": f"Running best-match agent for: {command[:60]}", "run_mode": "sequential", "needs_client": False, "agents": agents}

    # ─── Step 2: Execute ──────────────────────────────────────────────────

    def _execute(self, plan: dict, client_id: str, command: str) -> list:
        """Run the planned agents, return list of TaskStep results."""
        agents   = plan.get("agents", [])
        run_mode = plan.get("run_mode", "sequential")
        steps    = [TaskStep(
            agent_id=a["id"], agent_name=a["name"],
            status="queued", params=a.get("params", {})
        ) for a in agents]

        if run_mode == "parallel":
            threads = []
            for i, step in enumerate(steps):
                t = threading.Thread(target=self._run_one, args=(step, client_id, command))
                threads.append(t)
                t.start()
            for t in threads:
                t.join()
        else:
            for step in steps:
                self._run_one(step, client_id, command)

        return steps

    def _run_one(self, step: TaskStep, client_id: str, command: str):
        """Execute a single agent step."""
        step.status = "running"
        self.progress_callback(step.agent_id, "running", f"Running {step.agent_name}...")
        t_start = time.time()

        try:
            agent_id = step.agent_id
            params   = step.params

            # ── Client agents (M1–M11) ──────────────────────────────────
            if agent_id.startswith("M") and agent_id[1:].isdigit():
                module_num = int(agent_id[1:])
                result     = self._run_client_agent(module_num, client_id, params, command)
                step.output_summary = result.get("summary", "Completed")
                step.actions_taken  = result.get("actions", [])
                step.status         = "done" if result.get("ok") else "error"
                step.error          = result.get("error", "")

            # ── Agency agents ────────────────────────────────────────────
            elif agent_id == "M12" or agent_id == "12":
                result = self._run_job_hunter(params, command)
                step.output_summary = result.get("summary", "")
                step.actions_taken  = result.get("actions", [])
                step.status         = "done" if result.get("ok") else "error"

            elif agent_id == "product_research":
                result = self._run_product_research(params)
                step.output_summary = result.get("summary", "")
                step.actions_taken  = result.get("actions", [])
                step.status         = "done"

            elif agent_id == "redesign_engine":
                result = self._run_redesign(params, command)
                step.output_summary = result.get("summary", "")
                step.actions_taken  = result.get("actions", [])
                step.status         = "done"

            elif agent_id == "lead_prospector":
                result = self._run_prospector(params, command)
                step.output_summary = result.get("summary", "")
                step.actions_taken  = result.get("actions", [])
                step.status         = "done"

            elif agent_id == "content_machine":
                result = self._run_content(params, command)
                step.output_summary = result.get("summary", "")
                step.actions_taken  = result.get("actions", [])
                step.status         = "done"

            else:
                step.status         = "error"
                step.error          = f"Unknown agent: {agent_id}"
                step.output_summary = f"No executor found for {agent_id}"

        except Exception as e:
            step.status = "error"
            step.error  = str(e)
            step.output_summary = f"Error running {step.agent_name}: {e}"
            log.error(f"Agent {step.agent_id} failed: {e}")

        step.duration_s = round(time.time() - t_start, 2)
        self.progress_callback(step.agent_id, step.status, step.output_summary)

    # ─── Client agent executors ───────────────────────────────────────────

    def _run_client_agent(self, module_num: int, client_id: str, params: dict, command: str) -> dict:
        """Run a client-facing module agent via the orchestrator."""
        try:
            from core.orchestrator import run_module
            from core.tenant import get_tenant

            # Determine client: use provided client_id or extract from params
            cid = client_id or params.get("client_id", "")
            if not cid:
                # No specific client — run across all registered tenants
                from core.tenant import get_all_tenants
                tenants = get_all_tenants()
                if not tenants:
                    return {"ok": True, "summary": f"M{module_num} ready — no clients registered yet. Add a client first.", "actions": []}
                # Run for first tenant as default
                tenant = tenants[0]
            else:
                tenant = get_tenant(cid)

            result = run_module(tenant, module_num)
            return {
                "ok":      result.status == "success",
                "summary": result.summary,
                "actions": result.actions_taken,
                "error":   result.errors,
            }
        except Exception as e:
            return {"ok": False, "summary": f"M{module_num} could not run: {e}", "actions": [], "error": str(e)}

    # ─── Agency agent executors ───────────────────────────────────────────

    def _run_job_hunter(self, params: dict, command: str) -> dict:
        """Run M12 Job Hunter Agent."""
        try:
            from lib.job_hunter import JobHunter
            # Extract keywords from params or command
            keywords = params.get("keywords", "") or self._extract_keywords(command, "AI consultant")
            location = params.get("location", "UK")
            hunter   = JobHunter()
            results  = hunter.run(
                keywords=keywords, location=location,
                max_jobs=params.get("max_jobs", 20),
                top_n=params.get("top_n", 3),
            )
            top = results.get("top_matches", [])
            actions = [
                f"Scraped {results.get('total_found', 0)} listings",
                f"Generated {len(top)} tailored CV(s)",
            ]
            if top:
                actions.append(f"Top match: {top[0]['title']} @ {top[0]['company']} ({top[0]['match_score']}/100)")
                actions.append(f"Saved to Airtable Job Applications table")
            return {
                "ok":      True,
                "summary": f"Found {results.get('total_found',0)} listings. Generated {len(top)} tailored CV(s). Top match: {top[0]['title'] if top else 'none'} at {top[0]['company'] if top else '—'}.",
                "actions": actions,
                "data":    results,
            }
        except Exception as e:
            log.error(f"Job Hunter failed: {e}")
            return {"ok": False, "summary": f"Job Hunter error: {e}", "actions": [], "error": str(e)}

    def _run_product_research(self, params: dict) -> dict:
        try:
            from lib.product_intelligence import ProductIntelligence
            agent   = ProductIntelligence()
            results = agent.run()
            return {
                "ok":      True,
                "summary": f"Product research complete. {len(results.get('opportunities',[]))} opportunities found.",
                "actions": [f"Scanned {len(results.get('sources',[]))} marketplaces"] + [o.get("name","") for o in results.get("opportunities",[])[:3]],
            }
        except Exception as e:
            return {"ok": False, "summary": f"Product research error: {e}", "actions": []}

    def _run_redesign(self, params: dict, command: str) -> dict:
        try:
            from lib.creative_studio import CreativeStudio
            url   = params.get("url", "") or self._extract_url(command)
            studio = CreativeStudio()
            result = studio.audit_website(url) if url else studio.batch_audit()
            return {
                "ok":      True,
                "summary": result.get("summary", "Redesign audit complete"),
                "actions": result.get("actions", ["Website audited", "Brief generated"]),
            }
        except Exception as e:
            return {"ok": False, "summary": f"Redesign engine error: {e}", "actions": []}

    def _run_prospector(self, params: dict, command: str) -> dict:
        try:
            from lib.creator_outreach import CreatorOutreach
            industry  = params.get("industry", "") or self._extract_industry(command)
            location  = params.get("location", "UK")
            outreach  = CreatorOutreach()
            results   = outreach.prospect(industry=industry, location=location)
            count     = len(results.get("prospects", []))
            return {
                "ok":      True,
                "summary": f"Found {count} qualified SME prospects. {results.get('outreach_drafted',0)} outreach emails drafted.",
                "actions": [f"Scraped {results.get('sources_checked',0)} directories", f"{count} prospects qualified", f"{results.get('outreach_drafted',0)} emails ready to send"],
            }
        except Exception as e:
            return {"ok": False, "summary": f"Prospector error: {e}", "actions": []}

    def _run_content(self, params: dict, command: str) -> dict:
        try:
            from lib.content_machine import ContentMachine
            machine = ContentMachine()
            results = machine.run(context=command)
            return {
                "ok":      True,
                "summary": f"Content created: {results.get('pieces_created',0)} pieces ready.",
                "actions": results.get("pieces", [])[:5],
            }
        except Exception as e:
            return {"ok": False, "summary": f"Content Machine error: {e}", "actions": []}

    # ─── Step 3: Summarise ────────────────────────────────────────────────

    def _summarise(self, command: str, steps: list) -> str:
        """Ask Claude to write a clean, specific summary of what was done."""
        if not steps:
            return "No agents ran — check your command or API connection."

        steps_text = "\n".join([
            f"- {s.agent_name}: {s.status.upper()} — {s.output_summary}"
            + (f"\n  Actions: {', '.join(s.actions_taken[:3])}" if s.actions_taken else "")
            for s in steps
        ])

        if not self.claude:
            # Plain fallback summary
            done  = [s for s in steps if s.status == "done"]
            error = [s for s in steps if s.status == "error"]
            parts = [f"{s.agent_name} completed: {s.output_summary}" for s in done]
            if error:
                parts.append(f"⚠️ {len(error)} agent(s) had errors.")
            return " ".join(parts) or "Task complete."

        prompt = f"""Pasha gave the CEO Agent this command: "{command}"

The following agents ran:
{steps_text}

Write a short, specific, direct summary for Pasha. Maximum 4 sentences.
- Lead with what was actually done and the key result
- Include specific numbers where available
- If CVs were generated, say so and mention the top match
- If leads were found, state how many
- If there were errors, mention them briefly at the end
- No fluff, no "I have completed", no passive voice
- Write as the CEO Agent speaking to Pasha"""

        try:
            msg = self.claude.messages.create(
                model=self.MODEL,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            log.error(f"Summarise failed: {e}")
            done = [s for s in steps if s.status == "done"]
            return f"{len(done)}/{len(steps)} agents completed. " + " | ".join(s.output_summary for s in done[:2])

    # ─── Helpers ──────────────────────────────────────────────────────────

    def _extract_keywords(self, text: str, default: str = "") -> str:
        for phrase in ["for ", "as ", "about ", "keywords: "]:
            if phrase in text.lower():
                after = text.lower().split(phrase, 1)[1].split(" in ")[0].strip()
                if after:
                    return after
        return default

    def _extract_url(self, text: str) -> str:
        import re
        match = re.search(r'https?://\S+', text)
        return match.group(0) if match else ""

    def _extract_industry(self, text: str) -> str:
        industries = ["legal", "restaurant", "construction", "logistics", "healthcare",
                      "trades", "retail", "hospitality", "dental", "property"]
        for ind in industries:
            if ind in text.lower():
                return ind
        return "SME"

    # ─── Persist ──────────────────────────────────────────────────────────

    def _save_to_airtable(self, result: TaskResult):
        """Log the task run to Airtable → CEO Tasks table."""
        try:
            import requests as _req
            if not self.airtable_token or not self.airtable_base:
                return
            url     = f"https://api.airtable.com/v0/{self.airtable_base}/CEO%20Tasks"
            headers = {"Authorization": f"Bearer {self.airtable_token}", "Content-Type": "application/json"}
            payload = {
                "fields": {
                    "Command":     result.command[:500],
                    "Summary":     result.summary,
                    "Status":      result.status,
                    "Agents Used": ", ".join(s.agent_name for s in result.steps),
                    "Run Mode":    result.run_mode,
                    "Started At":  result.started_at,
                    "Client ID":   result.client_id,
                }
            }
            _req.post(url, headers=headers, json=payload, timeout=10)
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# CLI — quick test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    command = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Find me AI consultant jobs in London"

    def progress(agent_id, status, msg):
        icons = {"running": "⟳", "done": "✓", "error": "✗", "plan": "◆", "summary": "◆"}
        print(f"  {icons.get(status,'·')} [{agent_id}] {msg}")

    print(f"\n{'═'*60}")
    print(f"  CEO Agent Task Router")
    print(f"{'═'*60}")
    print(f"  Command: {command}")
    print(f"{'─'*60}\n")

    router = TaskRouter(progress_callback=progress)
    result = router.run(command)

    print(f"\n{'─'*60}")
    print(f"  RESULT ({result.status.upper()})")
    print(f"{'─'*60}")
    print(f"\n{result.summary}\n")

    for step in result.steps:
        icon = "✓" if step.status == "done" else "✗"
        print(f"  {icon} {step.agent_name} ({step.duration_s}s)")
        for action in step.actions_taken[:3]:
            print(f"      · {action}")
