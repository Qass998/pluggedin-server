"""
api/server.py — PluggedIN OS Local API Server
==============================================
Run this once at the start of each work session.
The dashboard connects to this to trigger agents.

    pip install fastapi uvicorn python-dotenv requests
    python api/server.py

Server runs on http://localhost:8000
Dashboard connects to http://localhost:8000

Endpoints:
    GET  /                          Health check
    GET  /clients                   List all registered clients
    GET  /clients/{id}              Single client detail + status
    POST /clients/onboard           Onboard a new client (full automation)
    POST /clients/{id}/run          Run all active modules for a client
    POST /clients/{id}/run/{module} Run one specific module
    GET  /briefings                 Latest CEO briefings (all clients)
    GET  /reports                   Latest agent reports (all clients)
    GET  /revenue                   MRR summary
    GET  /health                    System health check
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional

# Add parent directory to path so we can import core/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("Missing dependencies. Run:")
    print("  pip install fastapi uvicorn python-dotenv requests pydantic")
    sys.exit(1)

from core.tenant import get_tenant, list_tenants, get_all_tenants, tenant_summary
from core.orchestrator import run_module, run_client, MODULE_NAMES
from core.onboarding import onboard_client

log = logging.getLogger("api.server")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DASHBOARD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="PluggedIN OS",
    description="Multi-tenant Agent OS API",
    version="1.0.0",
    docs_url="/api/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve dashboard at root
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_dashboard():
    path = os.path.join(DASHBOARD_DIR, "index.html")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return HTMLResponse("<h1>Dashboard not found</h1><p>Make sure dashboard/index.html exists.</p>", status_code=404)

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class OnboardRequest(BaseModel):
    client_name: str
    industry: str
    plan: str = "starter"
    modules: list[int]
    contact_email: str = ""
    contact_phone: str = ""
    website: str = ""
    location: str = "UK"

class RunModuleRequest(BaseModel):
    modules: Optional[list[int]] = None   # None = run all active modules

class CEOTaskRequest(BaseModel):
    command:   str               # Natural language command from Pasha
    client_id: str = ""          # Optional — scope task to a specific client

class MasterAskRequest(BaseModel):
    question:  str
    history:   list = []         # Last N messages for context
    client_id: str = ""

# ---------------------------------------------------------------------------
# Airtable helpers (for reading live data)
# ---------------------------------------------------------------------------

def _airtable_get(base_id: str, table: str, token: str, max_records: int = 50) -> list[dict]:
    """Fetch records from Airtable table."""
    try:
        import requests as req
        url = f"https://api.airtable.com/v0/{base_id}/{table}"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"maxRecords": max_records, "sort[0][field]": "Ran At", "sort[0][direction]": "desc"}
        resp = req.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("records", [])
    except Exception as e:
        log.warning(f"Airtable fetch failed ({table}): {e}")
    return []


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "PluggedIN OS",
        "version": "1.0.0",
        "status": "running",
        "clients": len(list_tenants()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
def health():
    token = os.getenv("AIRTABLE_TOKEN", "")
    vapi_key = os.getenv("VAPI_API_KEY", "")
    return {
        "status": "healthy",
        "airtable": "configured" if token else "missing",
        "vapi": "configured" if vapi_key else "missing",
        "clients_registered": len(list_tenants()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/clients")
def get_clients():
    """List all registered clients with summaries."""
    tenants = get_all_tenants()
    return {
        "clients": [tenant_summary(t) for t in tenants],
        "total": len(tenants),
    }


@app.get("/clients/{client_id}")
def get_client(client_id: str):
    """Get a single client's full detail."""
    try:
        tenant = get_tenant(client_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    summary = tenant_summary(tenant)
    summary["modules_available"] = {
        str(m): name for m, name in MODULE_NAMES.items()
    }
    return summary


@app.post("/clients/onboard")
async def onboard(request: OnboardRequest, background_tasks: BackgroundTasks):
    """
    Onboard a new client. Runs full setup in background.
    Returns immediately with a job ID.
    """
    job_id = f"onboard_{request.client_name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"

    def _run_onboarding():
        result = onboard_client(
            client_name=request.client_name,
            industry=request.industry,
            plan=request.plan,
            modules=request.modules,
            contact_email=request.contact_email,
            contact_phone=request.contact_phone,
            website=request.website,
            location=request.location,
        )
        log.info(f"Onboarding complete: {result.to_dict()}")

    background_tasks.add_task(_run_onboarding)
    return {
        "job_id": job_id,
        "status": "started",
        "message": f"Onboarding {request.client_name} — running in background. Check /reports shortly.",
    }


@app.post("/clients/{client_id}/run")
async def run_client_modules(client_id: str, request: RunModuleRequest, background_tasks: BackgroundTasks):
    """Run all (or specified) modules for a client."""
    try:
        tenant = get_tenant(client_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    def _run():
        results = run_client(tenant, request.modules)
        log.info(f"Run complete for {client_id}: {[r.status for r in results]}")

    background_tasks.add_task(_run)
    modules_to_run = request.modules or tenant.modules_active
    return {
        "client_id": client_id,
        "status": "started",
        "modules": modules_to_run,
        "message": f"Running {len(modules_to_run)} module(s) for {tenant.client_name}",
    }


@app.post("/clients/{client_id}/run/{module_number}")
async def run_single_module(client_id: str, module_number: int, background_tasks: BackgroundTasks):
    """Run one specific module for a client."""
    try:
        tenant = get_tenant(client_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if module_number not in MODULE_NAMES:
        raise HTTPException(status_code=400, detail=f"Module {module_number} does not exist")

    def _run():
        result = run_module(tenant, module_number)
        log.info(f"Module {module_number} complete for {client_id}: {result.status}")

    background_tasks.add_task(_run)
    return {
        "client_id": client_id,
        "module": module_number,
        "module_name": MODULE_NAMES[module_number],
        "status": "started",
    }


@app.get("/briefings")
def get_briefings(limit: int = 20):
    """Latest CEO briefings across all clients."""
    token = os.getenv("AIRTABLE_TOKEN", "")
    agency_base = os.getenv("AIRTABLE_BASE_AGENCY", "appl51bhjj9R2wtKx")
    records = _airtable_get(agency_base, "CEO%20Briefings", token, limit)
    return {
        "briefings": [r.get("fields", {}) for r in records],
        "total": len(records),
    }


@app.get("/reports")
def get_reports(limit: int = 50):
    """Latest agent reports across all clients."""
    token = os.getenv("AIRTABLE_TOKEN", "")
    agency_base = os.getenv("AIRTABLE_BASE_AGENCY", "appl51bhjj9R2wtKx")
    records = _airtable_get(agency_base, "Agent%20Reports", token, limit)
    return {
        "reports": [r.get("fields", {}) for r in records],
        "total": len(records),
    }


@app.get("/results/jobs")
def get_jobs(limit: int = 50):
    """Job applications written by M12 Job Hunter Agent."""
    token = os.getenv("AIRTABLE_TOKEN", "")
    agency_base = os.getenv("AIRTABLE_BASE_AGENCY", "appl51bhjj9R2wtKx")
    records = _airtable_get(agency_base, "Job%20Applications", token, limit)
    return {
        "records": [{"_type": "jobs", **r.get("fields", {})} for r in records],
        "total": len(records),
    }


@app.get("/results/leads")
def get_leads(limit: int = 50):
    """Leads scraped by M2 Pipeline Agent."""
    token = os.getenv("AIRTABLE_TOKEN", "")
    agency_base = os.getenv("AIRTABLE_BASE_AGENCY", "appl51bhjj9R2wtKx")
    # Try client bases too — leads may be per-client
    records = _airtable_get(agency_base, "Leads", token, limit)
    return {
        "records": [{"_type": "leads", **r.get("fields", {})} for r in records],
        "total": len(records),
    }


@app.get("/results/content")
def get_content(limit: int = 50):
    """Content drafts from M3 Marketing Agent."""
    token = os.getenv("AIRTABLE_TOKEN", "")
    agency_base = os.getenv("AIRTABLE_BASE_AGENCY", "appl51bhjj9R2wtKx")
    records = _airtable_get(agency_base, "Content", token, limit)
    return {
        "records": [{"_type": "content", **r.get("fields", {})} for r in records],
        "total": len(records),
    }


@app.get("/results/reviews")
def get_reviews(limit: int = 50):
    """Reviews and reputation data from M11 Reviews Agent."""
    token = os.getenv("AIRTABLE_TOKEN", "")
    agency_base = os.getenv("AIRTABLE_BASE_AGENCY", "appl51bhjj9R2wtKx")
    records = _airtable_get(agency_base, "Reviews", token, limit)
    return {
        "records": [{"_type": "reviews", **r.get("fields", {})} for r in records],
        "total": len(records),
    }


@app.get("/results/all")
def get_all_results(limit: int = 30):
    """Unified feed: all result types merged and sorted newest first."""
    token = os.getenv("AIRTABLE_TOKEN", "")
    agency_base = os.getenv("AIRTABLE_BASE_AGENCY", "appl51bhjj9R2wtKx")

    table_map = {
        "Job%20Applications": "jobs",
        "Leads":              "leads",
        "Content":            "content",
        "Reviews":            "reviews",
        "Agent%20Reports":    "task",
    }

    all_records = []
    for table, rtype in table_map.items():
        try:
            recs = _airtable_get(agency_base, table, token, limit)
            for r in recs:
                fields = r.get("fields", {})
                fields["_type"]  = rtype
                fields["_table"] = table
                all_records.append(fields)
        except Exception as e:
            log.warning(f"Could not fetch {table}: {e}")

    # Sort newest first by any date field
    def _date_key(r):
        for k in ("Ran At", "Created At", "Date", "createdTime"):
            if r.get(k):
                return r[k]
        return ""

    all_records.sort(key=_date_key, reverse=True)
    return {"records": all_records[:limit*3], "total": len(all_records)}


@app.get("/revenue")
def get_revenue():
    """MRR summary across all clients."""
    tenants = get_all_tenants()
    from core.onboarding import MODULE_PRICES

    total_mrr = 0
    breakdown = []
    for t in tenants:
        client_mrr = sum(MODULE_PRICES.get(m, 0) for m in t.modules_active)
        total_mrr += client_mrr
        breakdown.append({
            "client": t.client_name,
            "plan": t.plan,
            "modules": len(t.modules_active),
            "mrr": client_mrr,
        })

    return {
        "total_mrr": total_mrr,
        "clients": len(tenants),
        "breakdown": breakdown,
        "currency": "GBP",
    }


# ---------------------------------------------------------------------------
# CEO Agent — task execution + Q&A endpoints
# ---------------------------------------------------------------------------

# In-memory task store (survives the session, resets on server restart)
_task_store: dict = {}

@app.post("/ceo/task")
async def ceo_task(request: CEOTaskRequest, background_tasks: BackgroundTasks):
    """
    Pasha gives the CEO Agent a natural language command.
    CEO Agent plans which agents to run, executes them, returns a summary.

    POST /ceo/task
    { "command": "Find me 20 legal firms in Manchester and draft outreach", "client_id": "" }
    """
    from core.task_router import TaskRouter
    import uuid

    task_id = str(uuid.uuid4())[:8]
    _task_store[task_id] = {
        "id":       task_id,
        "command":  request.command,
        "status":   "running",
        "summary":  "",
        "steps":    [],
        "started":  datetime.now(timezone.utc).isoformat(),
    }

    def _run():
        progress_events = []

        def progress(agent_id, status, msg):
            progress_events.append({"agent": agent_id, "status": status, "msg": msg})
            _task_store[task_id]["progress"] = progress_events[-5:]  # keep last 5

        try:
            router = TaskRouter(progress_callback=progress)
            result = router.run(request.command, request.client_id)
            _task_store[task_id].update({
                "status":     result.status,
                "summary":    result.summary,
                "steps":      [{"agent": s.agent_name, "status": s.status,
                                "output": s.output_summary, "actions": s.actions_taken}
                               for s in result.steps],
                "run_mode":   result.run_mode,
                "finished":   result.finished_at,
            })
        except Exception as e:
            log.error(f"CEO task failed: {e}")
            _task_store[task_id].update({"status": "error", "summary": f"Task failed: {e}"})

    background_tasks.add_task(_run)
    return {"task_id": task_id, "status": "running", "message": f"CEO Agent is working on: {request.command[:60]}"}


@app.get("/ceo/task/{task_id}")
def get_task_result(task_id: str):
    """Poll for a task result by task_id."""
    if task_id not in _task_store:
        raise HTTPException(status_code=404, detail="Task not found")
    return _task_store[task_id]


@app.get("/ceo/tasks")
def list_tasks(limit: int = 20):
    """Recent CEO task history."""
    tasks = sorted(_task_store.values(), key=lambda x: x.get("started",""), reverse=True)
    return {"tasks": tasks[:limit], "total": len(_task_store)}


@app.post("/master/ask")
async def master_ask(request: MasterAskRequest):
    """
    Pasha asks the Master CEO Agent a question (non-task — Q&A mode).
    Returns an immediate answer using live client data + Claude.

    POST /master/ask
    { "question": "Who needs attention today?", "history": [], "client_id": "" }
    """
    from core.master_ceo import MasterCEO
    import anthropic as _ant

    anthropic_key = os.getenv("ANTHROPIC_API_KEY","")
    if not anthropic_key:
        return {"answer": "Anthropic API key not set. Add ANTHROPIC_API_KEY to .env and restart the server."}

    try:
        # Get live client data
        tenants = get_all_tenants()
        client_summary = "\n".join([
            f"- {t.client_name} ({t.industry}) · modules: {t.modules_active}"
            for t in tenants
        ]) or "No clients registered yet."

        history_text = "\n".join([
            f"{m['role'].upper()}: {m['content']}" for m in request.history[-6:]
        ]) if request.history else ""

        prompt = f"""You are the Master CEO Agent for PluggedIN, an AI agency run by Pasha.

REGISTERED CLIENTS:
{client_summary}

{f"RECENT CONVERSATION:{chr(10)}{history_text}{chr(10)}" if history_text else ""}

PASHA'S QUESTION: {request.question}

Answer directly and specifically. If you can calculate a number, calculate it.
If you can name a client, name them. No vague answers. Max 3 sentences unless a list is genuinely needed.
Speak as the CEO Agent — direct, informed, action-oriented."""

        client = _ant.Anthropic(api_key=anthropic_key)
        msg    = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return {"answer": msg.content[0].text.strip(), "clients": len(tenants)}

    except Exception as e:
        log.error(f"master/ask failed: {e}")
        return {"answer": f"CEO Agent error: {e}"}


@app.post("/agency/{agent_id}/run")
async def run_agency_agent(agent_id: str, background_tasks: BackgroundTasks):
    """
    Trigger an agency (in-house) agent by ID.
    IDs: product_research | redesign_engine | lead_prospector | content_machine | job_hunter
    """
    from core.task_router import TaskRouter
    import uuid

    agent_map = {
        "product_research": "Run the product research agent",
        "redesign_engine":  "Run the redesign engine",
        "lead_prospector":  "Find SME leads and draft outreach",
        "content_machine":  "Generate content for PluggedIN this week",
        "job_hunter":       "Find jobs and generate tailored CVs",
    }

    command = agent_map.get(agent_id)
    if not command:
        raise HTTPException(status_code=404, detail=f"Unknown agency agent: {agent_id}")

    task_id = str(uuid.uuid4())[:8]
    _task_store[task_id] = {"id": task_id, "command": command, "status": "running", "started": datetime.now(timezone.utc).isoformat()}

    def _run():
        try:
            router = TaskRouter()
            result = router.run(command)
            _task_store[task_id].update({"status": result.status, "summary": result.summary,
                "steps": [{"agent": s.agent_name, "status": s.status, "output": s.output_summary} for s in result.steps]})
        except Exception as e:
            _task_store[task_id].update({"status": "error", "summary": str(e)})

    background_tasks.add_task(_run)
    return {"task_id": task_id, "agent": agent_id, "status": "started"}


# ---------------------------------------------------------------------------
# Market Scout — free scraping engine endpoints
# ---------------------------------------------------------------------------

# In-memory cache so we don't re-scrape on every dashboard refresh
_scout_cache: dict = {}

@app.post("/scout/run")
async def scout_run(background_tasks: BackgroundTasks, topic: str = "all"):
    """
    Trigger the Market Scout to scrape Reddit, HN, TradeKey, EC21, Go4WorldBusiness.
    Runs in background — poll /scout/signals for results.

    ?topic=africa_china | africa_europe | ai_agency | printful | all
    """
    import uuid
    run_id = str(uuid.uuid4())[:8]
    _scout_cache[run_id] = {"status": "running", "started": datetime.now(timezone.utc).isoformat(), "topic": topic}

    def _run():
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from lib.market_scout import run_scout, TRADE_TOPICS
            topic_key = topic if topic in TRADE_TOPICS else None
            signals = run_scout(topic_key=topic_key, log_airtable=True)
            _scout_cache[run_id].update({
                "status": "done",
                "signals": signals[:50],
                "total": len(signals),
                "finished": datetime.now(timezone.utc).isoformat(),
            })
            # Also update global cache for /scout/signals
            _scout_cache["_latest"] = _scout_cache[run_id]
        except Exception as e:
            log.error(f"Scout run failed: {e}")
            _scout_cache[run_id].update({"status": "error", "error": str(e)})

    background_tasks.add_task(_run)
    return {"run_id": run_id, "status": "running", "topic": topic,
            "message": "Scout is scraping Reddit, HN, TradeKey, EC21, Go4WorldBusiness..."}


@app.get("/scout/run/{run_id}")
def scout_status(run_id: str):
    """Poll for a scout run result."""
    if run_id not in _scout_cache:
        raise HTTPException(status_code=404, detail="Scout run not found")
    return _scout_cache[run_id]


@app.get("/scout/signals")
def scout_signals(topic: str = "", source: str = "", limit: int = 30):
    """
    Return the latest cached market signals.
    Optional filters: ?topic=africa_china&source=reddit
    """
    latest = _scout_cache.get("_latest", {})
    signals = latest.get("signals", [])

    if topic:
        signals = [s for s in signals if s.get("_topic") == topic]
    if source:
        signals = [s for s in signals if s.get("source") == source]

    # Sort by relevance score
    signals = sorted(signals, key=lambda x: x.get("_score", 0), reverse=True)

    return {
        "signals": signals[:limit],
        "total": len(signals),
        "last_run": latest.get("finished", ""),
        "status": latest.get("status", "never_run"),
        "topics": list({s.get("_topic", "") for s in signals}),
    }


@app.get("/scout/topics")
def scout_topics():
    """List available scout topics."""
    try:
        from lib.market_scout import TRADE_TOPICS
        return {"topics": {k: v["label"] for k, v in TRADE_TOPICS.items()}}
    except Exception:
        return {"topics": {}}


# ---------------------------------------------------------------------------
# Results — live Airtable browser endpoints
# ---------------------------------------------------------------------------

_agency_base = os.getenv("AIRTABLE_BASE_AGENCY", "")
_at_token    = os.getenv("AIRTABLE_TOKEN", "")

@app.get("/results/jobs")
def get_jobs(limit: int = 50):
    records = _airtable_get(_agency_base, "Job%20Applications", _at_token, limit)
    return {"records": [{"_type": "jobs", **r.get("fields", {})} for r in records], "total": len(records)}

@app.get("/results/leads")
def get_leads(limit: int = 50):
    records = _airtable_get(_agency_base, "Leads", _at_token, limit)
    return {"records": [{"_type": "leads", **r.get("fields", {})} for r in records], "total": len(records)}

@app.get("/results/content")
def get_content(limit: int = 50):
    records = _airtable_get(_agency_base, "Content", _at_token, limit)
    return {"records": [{"_type": "content", **r.get("fields", {})} for r in records], "total": len(records)}

@app.get("/results/reviews")
def get_reviews(limit: int = 50):
    records = _airtable_get(_agency_base, "Reviews", _at_token, limit)
    return {"records": [{"_type": "reviews", **r.get("fields", {})} for r in records], "total": len(records)}

@app.get("/results/signals")
def get_signals(limit: int = 50):
    records = _airtable_get(_agency_base, "Market%20Signals", _at_token, limit)
    return {"records": [{"_type": "signal", **r.get("fields", {})} for r in records], "total": len(records)}

@app.get("/results/all")
def get_all_results(limit: int = 30):
    all_records = []
    table_map = {
        "Job%20Applications": "jobs",
        "Leads": "leads",
        "Content": "content",
        "Reviews": "reviews",
        "Market%20Signals": "signal",
    }
    for table, rtype in table_map.items():
        records = _airtable_get(_agency_base, table, _at_token, limit)
        for r in records:
            all_records.append({"_type": rtype, **r.get("fields", {})})

    # Sort by date field (try multiple field names)
    def get_date(r):
        for f in ("Date Found", "Ran At", "Created", "Date"):
            if r.get(f): return r[f]
        return ""
    all_records.sort(key=get_date, reverse=True)
    return {"records": all_records[:limit * 2], "total": len(all_records)}


# ---------------------------------------------------------------------------
# Business Scanner — Auto-Build from Website
# ---------------------------------------------------------------------------

class ScanRequest(BaseModel):
    url:   str
    deep:  bool = False  # Run Claude deep assessment (costs extra API call, returns richer insights)

class DescriptionScanRequest(BaseModel):
    description: str

class MultiScanRequest(BaseModel):
    url:         str  = ""
    description: str  = ""
    deep:        bool = False

@app.post("/scan/business")
async def scan_business(req: ScanRequest, background_tasks: BackgroundTasks):
    """
    Scan a prospect's website → first principles assessment → recommend agents → CEO blueprint.
    Powers the Business Scan tab and Auto-Build from Website feature.
    """
    try:
        from lib.website_scanner import scan_business as do_scan
        result = do_scan(req.url, deep=req.deep)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scan/description")
async def scan_from_description(req: DescriptionScanRequest):
    """
    Scan a business from a free-text description — no URL needed.
    Use when the prospect describes their business verbally during a meeting.
    """
    try:
        from lib.website_scanner import scan_from_description as do_scan
        result = do_scan(req.description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scan/multi")
async def scan_multi(req: MultiScanRequest):
    """
    Multi-source scan: URL + description → unified profile.
    Richer than a single source — more signals = sharper agent recommendations.
    """
    try:
        from lib.website_scanner import scan_multi as do_multi
        result = do_multi(url=req.url or None, description=req.description or None)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scan/build-team")
async def build_team(req: MultiScanRequest):
    """
    Full pipeline: scan + first principles + CEO architecture → provision agent team.
    This is the 'agent that creates agents' endpoint.
    Requires client_id and owner_phone as query params.
    """
    try:
        from lib.website_scanner import scan_multi, scan_business as do_scan, scan_from_description
        from lib.agent_creator import build_team_for_business

        # Get scan result
        if req.url and req.description:
            scan = scan_multi(url=req.url, description=req.description)
        elif req.url:
            scan = do_scan(req.url)
        else:
            scan = scan_from_description(req.description)

        if "error" in scan:
            raise HTTPException(status_code=400, detail=scan["error"])

        # Build the team blueprint (no provisioning — user confirms first)
        result = build_team_for_business(
            business_profile = scan["profile"],
            client_id        = "prospect_preview",
            owner_phone      = "",
            provision        = False,
        )
        result["scan"] = scan
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Demo Flow — one-button prospect demo & close
# ---------------------------------------------------------------------------

class DemoLaunchRequest(BaseModel):
    prospect_name:  str
    prospect_phone: str
    business_name:  str
    industry:       str
    cal_link:       str = ""
    language:       str = "English"
    auto_sequence:  bool = False

class DemoCallRequest(BaseModel):
    demo_id:        str
    phone_override: str = ""

class DemoCloseRequest(BaseModel):
    demo_id:        str
    stripe_link:    str = ""
    custom_message: str = ""


@app.post("/demo/launch")
async def demo_launch(req: DemoLaunchRequest):
    try:
        from lib.demo_flow import launch_demo, quick_demo
        fn = quick_demo if req.auto_sequence else launch_demo
        demo = fn(
            prospect_name=req.prospect_name,
            prospect_phone=req.prospect_phone,
            business_name=req.business_name,
            industry=req.industry,
            cal_link=req.cal_link,
        )
        return {"status": "ok", "demo": demo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/demo/call")
async def demo_call(req: DemoCallRequest):
    try:
        from lib.demo_flow import trigger_demo_call
        return trigger_demo_call(req.demo_id, raw_phone=req.phone_override or None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/demo/close")
async def demo_close(req: DemoCloseRequest):
    try:
        from lib.demo_flow import send_payment_link
        return send_payment_link(req.demo_id, stripe_link=req.stripe_link or None, custom_message=req.custom_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/demo/status/{demo_id}")
def demo_status(demo_id: str):
    from lib.demo_flow import get_demo
    demo = get_demo(demo_id)
    if not demo:
        raise HTTPException(status_code=404, detail="Demo not found")
    return demo


@app.get("/demo/list")
def demo_list():
    from lib.demo_flow import list_demos
    return {"demos": list_demos()}


@app.post("/demo/whatsapp")
async def demo_whatsapp(request: Request):
    """Send a manual WhatsApp to any number."""
    try:
        body    = await request.json()
        to      = body.get("to", "")
        message = body.get("message", "")
        if not to or not message:
            raise HTTPException(status_code=400, detail="to and message required")
        from lib.whatsapp_agent import send_whatsapp
        wa_to = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
        sent  = send_whatsapp(wa_to, message)
        return {"status": "sent" if sent else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Agent Team & Chat — Named agent conversations
# ---------------------------------------------------------------------------

# Demo team store — keyed by demo/client ID
_demo_teams: dict = {}

class AgentChatRequest(BaseModel):
    client_id:    str
    agent_id:     str          # e.g. "demo_gromatic_1"
    message:      str
    business_profile: dict = {}  # Optional context enrichment

class SeedDemoRequest(BaseModel):
    client_id:       str
    business_profile: dict = {}  # {business_name, industry, services, location...}
    modules:         list  = [1, 3, 7, 10]  # Which agents to seed

class TeamStatusRequest(BaseModel):
    client_id: str


@app.post("/agent/chat")
async def agent_chat(req: AgentChatRequest):
    """
    Send a message to a named agent and receive a persona-driven response.
    The agent knows their role, personality, business context, and recent activity.
    Powers the contacts UI chat panel.
    """
    try:
        from lib.agent_chat import chat_with_agent
        from lib.agent_factory import load_team

        # Load team for this client
        team = load_team(req.client_id) or _demo_teams.get(req.client_id, [])
        if not team:
            raise HTTPException(status_code=404, detail=f"No team found for client {req.client_id}")

        # Find the agent
        agent = next((a for a in team if a.get("id") == req.agent_id), None)
        if not agent:
            # Try matching by module_id embedded in agent_id
            try:
                mod_id = int(req.agent_id.split("_")[-1])
                agent = next((a for a in team if a.get("module_id") == mod_id), None)
            except (ValueError, IndexError):
                pass
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {req.agent_id} not found in team")

        result = chat_with_agent(
            message          = req.message,
            agent            = agent,
            client_id        = req.client_id,
            business_profile = req.business_profile or {},
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/history/{client_id}/{agent_id}")
async def get_chat_history(client_id: str, agent_id: str):
    """Get conversation history for a specific agent."""
    from lib.agent_chat import get_history
    history = get_history(client_id, agent_id)
    return {"client_id": client_id, "agent_id": agent_id, "messages": history}


@app.get("/team/{client_id}")
async def get_team(client_id: str):
    """Get the current named agent team for a client, with live status."""
    from lib.agent_factory import load_team
    from lib.agent_chat import get_team_status
    team = load_team(client_id) or _demo_teams.get(client_id, [])
    if not team:
        return {"client_id": client_id, "team": [], "message": "No team provisioned yet"}
    statuses = get_team_status(team, client_id)
    return {"client_id": client_id, "team": statuses}


# ---------------------------------------------------------------------------
# Website Builder — animated sites deployed to Netlify
# ---------------------------------------------------------------------------

class WebsiteBuildRequest(BaseModel):
    business_profile: dict          # Full profile from scan or manual
    deploy:           bool = True   # True = push to Netlify, False = return HTML only
    netlify_token:    str  = ""     # Optional override (falls back to NETLIFY_TOKEN env)

class PortalDeployRequest(BaseModel):
    client_id:        str
    business_profile: dict
    netlify_token:    str = ""

class SkillsRequest(BaseModel):
    module_id:  int
    agent_role: str = ""
    search_live: bool = False


@app.post("/website/build")
async def build_website(req: WebsiteBuildRequest):
    """
    Build and optionally deploy an animated website for a client.

    Input:  business_profile (from /scan/business or manual)
    Output: {status, url, html, copy, site_id}

    Design: Higgsfield motion, Huashu aesthetic, GSAP animations.
    Deploy: Netlify (requires NETLIFY_TOKEN in .env).
    """
    try:
        from lib.website_builder import build_website as do_build
        result = do_build(
            profile = req.business_profile,
            deploy  = req.deploy,
            token   = req.netlify_token or None,
        )
        # Don't return full HTML in response (can be large) — save it separately
        result_clean = {k: v for k, v in result.items() if k != "html"}
        result_clean["html_length"] = len(result.get("html", ""))
        return result_clean
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/website/preview")
async def preview_website(req: WebsiteBuildRequest):
    """
    Generate website HTML without deploying — for in-browser preview.
    Returns full HTML string.
    """
    try:
        from lib.website_builder import build_website as do_build
        result = do_build(profile=req.business_profile, deploy=False)
        return {"status": "generated", "html": result.get("html", ""), "copy": result.get("copy", {})}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/website/deploy-portal")
async def deploy_portal(req: PortalDeployRequest):
    """
    Deploy a white-label client portal to Netlify.
    The client gets their own {business-slug}-portal.netlify.app URL
    showing their named agent team and activity.
    """
    try:
        from lib.website_builder import deploy_client_portal
        from lib.agent_factory import load_team
        team = load_team(req.client_id) or []
        result = deploy_client_portal(
            business_profile = req.business_profile,
            team             = team,
            token            = req.netlify_token or None,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/skills/{module_id}")
async def get_agent_skills(module_id: int, search_live: bool = False):
    """
    Get vetted, high-star GitHub skills for a specific agent module.
    All skills are pre-vetted: MIT/Apache license, >500 stars, actively maintained.
    """
    try:
        from lib.github_skills import get_skills_for_agent
        skills = get_skills_for_agent(module_id, search_live=search_live)
        return {"module_id": module_id, "skills": skills, "count": len(skills)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/upgrade-skills")
async def upgrade_agent_skills(req: SkillsRequest):
    """
    Get recommended skill upgrades for an agent.
    Returns top vetted tools not yet assigned.
    """
    try:
        from lib.github_skills import get_skills_for_agent
        skills = get_skills_for_agent(req.module_id, req.agent_role, req.search_live)
        return {"skills": skills, "total": len(skills)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/team/seed-demo")
async def seed_demo_team(req: SeedDemoRequest):
    """
    Seed a demo agent team with realistic conversations.
    Call this before showing a client the dashboard — makes the chats feel alive.
    """
    from lib.agent_factory import generate_team, save_team
    from lib.agent_chat import seed_demo_conversations

    bp = req.business_profile or {
        "business_name": "Demo Business",
        "industry":      "Consulting",
        "location":      "London, UK",
        "services":      ["Business Consulting", "Strategy", "Advisory"],
        "tone":          "professional",
    }

    # Auto-detect region
    location = bp.get("location", "").lower()
    if any(c in location for c in ["nigeria", "ghana", "kenya", "africa", "lagos"]):
        region = "africa"
    elif any(c in location for c in ["france", "paris", "ivory"]):
        region = "francophone"
    else:
        region = "uk"

    mods = [{"module_id": m, "priority": "essential" if i < 2 else "high"}
            for i, m in enumerate(req.modules)]

    team = generate_team(bp, mods, region=region, client_id=req.client_id)
    save_team(req.client_id, team)
    _demo_teams[req.client_id] = team

    seed_demo_conversations(team, req.client_id, bp)

    from lib.agent_chat import get_team_status
    return {
        "status":    "seeded",
        "client_id": req.client_id,
        "team":      get_team_status(team, req.client_id),
    }


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"""
╔══════════════════════════════════════════╗
║       PluggedIN OS — API Server          ║
║  http://localhost:{port}                    ║
║  Docs: http://localhost:{port}/docs         ║
╚══════════════════════════════════════════╝
""")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True, app_dir=os.path.dirname(__file__))


# ---------------------------------------------------------------------------
# WHATSAPP BUSINESS REGISTRATION
# ---------------------------------------------------------------------------

class WhatsAppRegisterRequest(BaseModel):
    twilio_number: str
    config:        dict


class OnboardClientRequest(BaseModel):
    # Business identity
    business_name:   str
    owner_name:      str
    industry:        str
    location:        str = "UK"
    website_url:     str = ""
    # Operations
    services:        list = []
    business_hours:  str = "Monday to Friday, 9am to 6pm"
    tone:            str = "professional and warm"
    faqs:            list = []   # [{"question": str, "answer": str}]
    # Contact
    owner_phone:     str         # WhatsApp e.g. +447847221722
    cal_link:        str = ""
    # Twilio
    twilio_number:   str = ""    # e.g. +14155238886 (sandbox or real)
    # Options
    scan_website:    bool = True
    deploy_portal:   bool = False
    send_ceo_brief:  bool = True


@app.post("/onboard/client")
async def onboard_client_full(req: OnboardClientRequest, background_tasks: BackgroundTasks):
    """
    Unified client onboarding — one call does everything:
    1. Scans their website (if url provided)
    2. Runs first principles assessment
    3. Builds named agent team
    4. Registers WhatsApp business profile
    5. Seeds demo conversations
    6. Deploys client portal (if deploy_portal=True)
    7. Sends CEO brief to owner via WhatsApp

    Returns the full blueprint + team + next steps.
    """
    try:
        steps = []

        # ── Build base profile ──────────────────────────────
        profile = {
            "business_name":    req.business_name,
            "owner_name":       req.owner_name,
            "industry":         req.industry,
            "location":         req.location,
            "services":         req.services or [],
            "business_hours":   req.business_hours,
            "tone":             req.tone,
            "faqs":             req.faqs or [],
            "cal_link":         req.cal_link,
            "has_whatsapp":     bool(req.twilio_number),
            "has_online_booking": bool(req.cal_link),
        }

        # ── Step 1: Scan website if provided ────────────────
        if req.scan_website and req.website_url:
            try:
                from lib.website_scanner import scan_business
                scan = scan_business(req.website_url, deep=False)
                # Merge scan results into profile
                for key in ["services", "pain_signals", "tone", "has_reviews_section",
                            "has_whatsapp", "has_online_booking", "team_size_signal"]:
                    if scan.get(key) and not profile.get(key):
                        profile[key] = scan[key]
                steps.append({"step": "website_scan", "status": "done", "url": req.website_url})
            except Exception as e:
                steps.append({"step": "website_scan", "status": "skipped", "reason": str(e)})

        # ── Step 2: First principles assessment ─────────────
        from lib.first_principles import run_first_principles, run_deep_assessment
        fp = run_first_principles(profile)
        steps.append({"step": "first_principles", "status": "done",
                      "readiness_score": fp.get("readiness_score"),
                      "max_roi_play":    fp.get("max_roi_play")})

        # ── Step 3: Build named agent team ──────────────────
        from lib.agent_creator import run_ceo_architecture
        client_id = f"client_{req.business_name.lower().replace(' ','_').replace('.','')}"
        architecture = run_ceo_architecture(profile, fp, client_id)
        team = architecture["team_blueprint"]

        from lib.agent_factory import save_team
        save_team(client_id, team)
        _demo_teams[client_id] = team
        steps.append({"step": "team_built", "status": "done",
                      "agents": [a["name"] for a in team],
                      "roi":    architecture["projected_roi"]["roi_multiple"]})

        # ── Step 4: Register WhatsApp profile ───────────────
        if req.twilio_number:
            from lib.whatsapp_agent import register_client as register_wa
            wa_number = req.twilio_number if req.twilio_number.startswith("whatsapp:") \
                        else f"whatsapp:{req.twilio_number}"
            wa_config = {
                "client_id":      client_id,
                "client_name":    req.owner_name,
                "business_name":  req.business_name,
                "industry":       req.industry,
                "location":       req.location,
                "cal_link":       req.cal_link,
                "business_hours": req.business_hours,
                "ceo_phone":      f"whatsapp:{req.owner_phone}" if not req.owner_phone.startswith("whatsapp:") else req.owner_phone,
                "faqs":           req.faqs,
                "tone":           req.tone,
                "services":       req.services,
            }
            register_wa(wa_number, wa_config)

            # Persist to config file
            config_path = os.path.normpath(os.path.join(
                os.path.dirname(__file__), "..", "config", "whatsapp_clients.json"))
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            existing = []
            if os.path.exists(config_path):
                with open(config_path) as f:
                    existing = json.load(f)
            existing = [c for c in existing if c.get("twilio_number") != wa_number]
            existing.append({**wa_config, "twilio_number": wa_number})
            with open(config_path, "w") as f:
                json.dump(existing, f, indent=2)

            steps.append({"step": "whatsapp_registered", "status": "done", "number": wa_number})

        # ── Step 5: Seed demo conversations ─────────────────
        from lib.agent_chat import seed_demo_conversations
        seed_demo_conversations(team, client_id, profile)
        steps.append({"step": "demo_seeded", "status": "done"})

        # ── Step 6: Deploy portal (optional) ────────────────
        portal_url = None
        if req.deploy_portal:
            try:
                from lib.website_builder import deploy_client_portal
                netlify_token = os.getenv("NETLIFY_TOKEN", "")
                if netlify_token and netlify_token != "your-netlify-personal-access-token-here":
                    result = deploy_client_portal(profile, team, netlify_token)
                    portal_url = result.get("url")
                    steps.append({"step": "portal_deployed", "status": "done", "url": portal_url})
                else:
                    steps.append({"step": "portal_deployed", "status": "skipped", "reason": "NETLIFY_TOKEN not set"})
            except Exception as e:
                steps.append({"step": "portal_deployed", "status": "failed", "error": str(e)})

        # ── Step 7: Send CEO brief via WhatsApp ─────────────
        if req.send_ceo_brief and req.owner_phone and architecture.get("ceo_brief"):
            try:
                from lib.whatsapp_agent import send_whatsapp
                wa_to = req.owner_phone if req.owner_phone.startswith("whatsapp:") \
                        else f"whatsapp:{req.owner_phone}"
                send_whatsapp(wa_to, architecture["ceo_brief"])
                steps.append({"step": "ceo_brief_sent", "status": "done", "to": wa_to})
            except Exception as e:
                steps.append({"step": "ceo_brief_sent", "status": "failed", "error": str(e)})

        # ── Build next steps checklist ───────────────────────
        next_steps = []
        if not req.twilio_number:
            next_steps.append("Buy a Twilio number and re-run with twilio_number set")
        next_steps.append("Paste webhook URL in Twilio: POST /webhook/whatsapp")
        next_steps.append("Client sets call forwarding on their phone to VAPI number")
        if not portal_url:
            next_steps.append("Deploy client portal: set deploy_portal=true")

        from lib.agent_chat import get_team_status
        return {
            "status":        "onboarded",
            "client_id":     client_id,
            "business":      req.business_name,
            "steps":         steps,
            "team":          get_team_status(team, client_id),
            "architecture":  {
                "projected_roi":   architecture["projected_roi"],
                "ceo_brief":       architecture["ceo_brief"],
                "provisioning_order": architecture["provisioning_order"],
            },
            "first_principles": {
                "readiness_score": fp.get("readiness_score"),
                "max_roi_play":    fp.get("max_roi_play"),
                "recommended_entry_point": fp.get("recommended_entry_point"),
            },
            "portal_url":    portal_url,
            "next_steps":    next_steps,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/whatsapp/register")
async def whatsapp_register(req: WhatsAppRegisterRequest):
    """Register a business with the WhatsApp agent at runtime."""
    try:
        from lib.whatsapp_agent import register_client
        register_client(req.twilio_number, req.config)
        return {"status": "registered", "number": req.twilio_number, "business": req.config.get("business_name")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/whatsapp/clients")
async def whatsapp_list_clients():
    """List all registered WhatsApp business clients."""
    from lib.whatsapp_agent import list_registered_clients
    return {"clients": list_registered_clients()}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Twilio WhatsApp webhook — receives inbound messages, AI replies.
    Set this URL in Twilio console: https://your-domain/webhook/whatsapp
    """
    from lib.whatsapp_agent import handle_incoming_message
    try:
        form  = await request.form()
        body  = form.get("Body", "").strip()
        from_ = form.get("From", "")
        to_   = form.get("To", "")
        name  = form.get("ProfileName", "")

        if not body or not from_:
            return {"status": "ignored"}

        reply = handle_incoming_message(from_number=from_, to_number=to_, body=body, profile_name=name)
        return {"status": "handled", "reply_length": len(reply)}
    except Exception as e:
        print(f"[Webhook] WhatsApp error: {e}")
        return {"status": "error", "detail": str(e)}


def _load_whatsapp_clients_from_config():
    """Load registered businesses from config/whatsapp_clients.json on startup."""
    config_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "config", "whatsapp_clients.json"))
    if not os.path.exists(config_path):
        return
    try:
        from lib.whatsapp_agent import register_client
        with open(config_path) as f:
            clients = json.load(f)
        for client in clients:
            number = client.pop("twilio_number", None)
            if number:
                register_client(number, client)
        print(f"[Server] Loaded {len(clients)} WhatsApp client(s) from config ✓")
    except Exception as e:
        print(f"[Server] Warning — could not load WhatsApp config: {e}")


_load_whatsapp_clients_from_config()
