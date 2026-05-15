"""
lib/pipeline_agent.py — Pipeline Agent (M2) Orchestrator

Ties together the four OpenOutreach patterns:
  1. pipeline_state    — lead lifecycle (QUALIFIED→READY→PENDING→CONNECTED→COMPLETED/FAILED)
  2. icp_gate          — confidence scoring and gating
  3. conversation_memory — fact-based memory per lead
  4. followup_engine   — structured follow-up decisions

Usage:
  from lib.pipeline_agent import run_pipeline_cycle
  run_pipeline_cycle(client_id="gromatic")
"""
from __future__ import annotations
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()


def run_pipeline_cycle(client_id: str, send_fn=None):
    """
    Full pipeline cycle for one client:
    1. Score and gate any new UNSCORED leads
    2. Run follow-up decisions for PENDING / CONNECTED leads
    3. Reconcile stale tasks

    send_fn(lead_id, message) — callable that sends the message via Gmail MCP / LinkedIn.
    If None, decisions are logged but not executed.
    """
    from lib.pipeline_state import get_leads_by_stage, reconcile_pipeline, is_active
    from lib.icp_gate        import gate_lead
    from lib.followup_engine import make_followup_decision, execute_decision
    from lib.conversation_memory import get_facts

    print(f"[PipelineAgent] Starting cycle for {client_id}")

    # ── Step 1: Gate unscored leads ──────────────────────────
    new_leads = get_leads_by_stage(client_id, ["QUALIFIED"])
    unscored  = [l for l in new_leads if not l.get("ICP Score")]
    for lead in unscored:
        lead_id = lead.get("_id")
        if lead_id:
            gate_lead(lead_id, lead, use_ai=False)

    # ── Step 2: Follow-up decisions ──────────────────────────
    active_leads = get_leads_by_stage(client_id, ["PENDING", "CONNECTED"])
    business_name = _get_business_name(client_id)

    for lead in active_leads:
        lead_id = lead.get("_id")
        if not lead_id or not is_active(lead):
            continue

        # Check if it's time to follow up
        if not _is_due(lead):
            continue

        facts    = get_facts(lead_id)
        messages = _get_messages(lead_id)
        decision = make_followup_decision(lead, business_name, messages, facts)

        print(f"[PipelineAgent] {lead.get('Name','?')} → {decision['action']} ({decision.get('reasoning','')})")

        if send_fn:
            execute_decision(lead_id, decision, send_fn)
        else:
            _log_decision(lead_id, decision)

    # ── Step 3: Reconcile ─────────────────────────────────────
    reconcile_pipeline(client_id)

    print(f"[PipelineAgent] Cycle complete for {client_id}")


def process_inbound_reply(lead_id: str, message: str, client_id: str):
    """
    Call when a prospect replies (LinkedIn DM, email, WhatsApp).
    Updates conversation facts and advances stage to CONNECTED.
    """
    from lib.pipeline_state      import mark_connected, get_lead
    from lib.conversation_memory import extract_and_update_facts

    lead = get_lead(lead_id)

    # Advance to CONNECTED if still PENDING
    if lead.get("Stage") == "PENDING":
        mark_connected(lead_id)

    # Extract and store facts from their message
    updated_facts = extract_and_update_facts(lead_id, [message])
    print(f"[PipelineAgent] {lead_id} replied — {len(updated_facts)} facts on record")
    return updated_facts


def onboard_lead(lead_data: dict, client_id: str) -> dict:
    """
    Entry point for a new lead.
    Scores, gates, and stages the lead. Returns the gate decision.

    lead_data: dict from Apify/Vibe/Apollo with at minimum {Name or Company, industry, ...}
    """
    from lib.pipeline_state import get_leads_by_stage
    from lib.airtable_client import AirtableClient
    from lib.icp_gate import gate_lead

    # Write to Airtable first to get a record ID
    try:
        at = AirtableClient(
            os.getenv("AIRTABLE_TOKEN",""),
            os.getenv("AIRTABLE_BASE_PLUGGEDIN","")
        )
        record = at.create_record("Leads", {
            **lead_data,
            "Client":  client_id,
            "Stage":   "QUALIFIED",
            "Added At": datetime.now(timezone.utc).isoformat(),
        })
        lead_id = record.get("id")
    except Exception as e:
        print(f"[PipelineAgent] onboard_lead create error: {e}")
        return {"gate": "error", "error": str(e)}

    return gate_lead(lead_id, lead_data, use_ai=False)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _get_business_name(client_id: str) -> str:
    try:
        from core.tenant import get_tenant
        t = get_tenant(client_id)
        return t.get("business_name", client_id) if t else client_id
    except Exception:
        return client_id


def _is_due(lead: dict) -> bool:
    """Check if Next Action At has passed (or is not set)."""
    next_at = lead.get("Next Action At")
    if not next_at:
        return True
    try:
        due = datetime.fromisoformat(next_at.replace("Z", "+00:00"))
        return datetime.now(timezone.utc) >= due
    except Exception:
        return True


def _get_messages(lead_id: str) -> list[dict]:
    """Fetch last 6 messages for a lead from Airtable."""
    try:
        from lib.airtable_client import AirtableClient
        at = AirtableClient(
            os.getenv("AIRTABLE_TOKEN",""),
            os.getenv("AIRTABLE_BASE_PLUGGEDIN","")
        )
        records = at.list_records(
            "Messages",
            filter_formula=f"{{Lead ID}}='{lead_id}'",
            sort=[{"field": "Sent At", "direction": "desc"}],
            max_records=6,
        ) or []
        msgs = [r.get("fields", {}) for r in records]
        return list(reversed(msgs))
    except Exception:
        return []


def _log_decision(lead_id: str, decision: dict):
    """Log a decision to Airtable without executing it (dry-run mode)."""
    try:
        from lib.airtable_client import AirtableClient
        at = AirtableClient(
            os.getenv("AIRTABLE_TOKEN",""),
            os.getenv("AIRTABLE_BASE_PLUGGEDIN","")
        )
        at.create_record("Agent Reports", {
            "Lead ID":    lead_id,
            "Action":     decision.get("action"),
            "Message":    decision.get("message") or "",
            "Reasoning":  decision.get("reasoning") or "",
            "Outcome":    decision.get("outcome") or "",
            "Ran At":     datetime.now(timezone.utc).isoformat(),
            "Module":     "Pipeline Agent (M2)",
            "Status":     "dry-run",
        })
    except Exception as e:
        print(f"[PipelineAgent] log_decision error: {e}")
