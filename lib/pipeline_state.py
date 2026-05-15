"""
lib/pipeline_state.py — Lead Lifecycle State Machine

Stages: QUALIFIED → READY → PENDING → CONNECTED → COMPLETED / FAILED
Outcomes: converted | not_interested | wrong_fit | no_budget |
          has_solution | bad_timing | unresponsive | unknown

All state writes go to Airtable Leads table via airtable_client.
"""
from __future__ import annotations
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

STAGES   = ["QUALIFIED", "READY", "PENDING", "CONNECTED", "COMPLETED", "FAILED"]
TERMINAL = {"COMPLETED", "FAILED"}
OUTCOMES = {
    "converted", "not_interested", "wrong_fit",
    "no_budget", "has_solution", "bad_timing",
    "unresponsive", "unknown",
}

# Stages that allow automatic advancement
AUTO_ADVANCE_SCORE_THRESHOLD = 80
MANUAL_REVIEW_SCORE_THRESHOLD = 60
MAX_ATTEMPTS = 3


def _at():
    """Current UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────
# AIRTABLE HELPERS
# ─────────────────────────────────────────────

def _get_airtable():
    from lib.airtable_client import AirtableClient
    token = os.getenv("AIRTABLE_TOKEN", "")
    base  = os.getenv("AIRTABLE_BASE_PLUGGEDIN", "")
    return AirtableClient(token, base)


def get_lead(lead_id: str) -> dict:
    try:
        at = _get_airtable()
        return at.get_record("Leads", lead_id) or {}
    except Exception as e:
        print(f"[PipelineState] get_lead error: {e}")
        return {}


def get_leads_by_stage(client_id: str, stages: list[str]) -> list[dict]:
    try:
        at     = _get_airtable()
        filter_str = "OR(" + ",".join([f"{{Stage}}='{s}'" for s in stages]) + ")"
        records = at.list_records("Leads", filter_formula=filter_str) or []
        return [r.get("fields", {}) | {"_id": r["id"]} for r in records]
    except Exception as e:
        print(f"[PipelineState] get_leads_by_stage error: {e}")
        return []


def _update_lead(lead_id: str, fields: dict):
    try:
        at = _get_airtable()
        at.update_record("Leads", lead_id, fields)
    except Exception as e:
        print(f"[PipelineState] _update_lead error: {e}")


# ─────────────────────────────────────────────
# STATE TRANSITIONS
# ─────────────────────────────────────────────

def advance_stage(lead_id: str, to_stage: str, reason: str = "") -> dict:
    """
    Move a lead to the next stage. Validates transition is legal.
    Returns updated fields dict.
    """
    if to_stage not in STAGES:
        raise ValueError(f"Unknown stage: {to_stage}")

    fields = {"Stage": to_stage, "Last Updated": _at()}
    if reason:
        fields["Stage Note"] = reason

    _update_lead(lead_id, fields)
    print(f"[PipelineState] {lead_id} → {to_stage}" + (f" ({reason})" if reason else ""))
    return fields


def qualify_lead(lead_id: str, icp_score: int, auto_advance: bool = True) -> str:
    """
    Gate a lead based on ICP score. Returns the resulting stage.
    Score < 60  → discarded (do not call this function — caller should skip)
    Score 60-79 → QUALIFIED (needs manual review)
    Score ≥ 80  → QUALIFIED then immediately READY if auto_advance=True
    """
    if icp_score < MANUAL_REVIEW_SCORE_THRESHOLD:
        _update_lead(lead_id, {"Stage": "FAILED", "Outcome": "wrong_fit",
                               "ICP Score": icp_score, "Disqualified": True})
        return "FAILED"

    _update_lead(lead_id, {"Stage": "QUALIFIED", "ICP Score": icp_score})

    if auto_advance and icp_score >= AUTO_ADVANCE_SCORE_THRESHOLD:
        advance_stage(lead_id, "READY", "auto-advanced: high ICP score")
        return "READY"

    return "QUALIFIED"


def mark_contacted(lead_id: str, attempt_number: int):
    """Call after each outreach attempt."""
    _update_lead(lead_id, {
        "Stage":          "PENDING",
        "Attempts":       attempt_number,
        "Last Contacted": _at(),
    })


def mark_connected(lead_id: str):
    """Call when the lead responds."""
    _update_lead(lead_id, {
        "Stage":        "CONNECTED",
        "Connected At": _at(),
    })


def close_lead(lead_id: str, outcome: str, note: str = ""):
    """
    Terminal state. outcome must be one of OUTCOMES.
    Sets Disqualified=True if outcome is wrong_fit or unresponsive.
    """
    if outcome not in OUTCOMES:
        outcome = "unknown"

    fields = {
        "Stage":        "COMPLETED" if outcome == "converted" else "FAILED",
        "Outcome":      outcome,
        "Closed At":    _at(),
    }
    if note:
        fields["Stage Note"] = note
    if outcome in {"wrong_fit", "unresponsive"}:
        fields["Disqualified"] = True

    _update_lead(lead_id, fields)
    print(f"[PipelineState] {lead_id} closed — {outcome}")


def disqualify_lead(lead_id: str, reason: str = ""):
    """Permanent exclusion. Lead will never re-enter the pipeline."""
    _update_lead(lead_id, {
        "Stage":        "FAILED",
        "Outcome":      "wrong_fit",
        "Disqualified": True,
        "Stage Note":   reason,
    })


def is_active(lead: dict) -> bool:
    return lead.get("Stage") not in TERMINAL and not lead.get("Disqualified")


def needs_followup(lead: dict) -> bool:
    return lead.get("Stage") in {"PENDING", "CONNECTED"} and not lead.get("Disqualified")


# ─────────────────────────────────────────────
# RECONCILIATION
# ─────────────────────────────────────────────

_last_reconcile: str | None = None

def reconcile_pipeline(client_id: str, force: bool = False):
    """
    Walk all active leads. Recreate missing follow-up tasks.
    Auto-called on server start and when task queue goes idle.
    Throttled: runs at most once per 30 minutes.
    """
    global _last_reconcile
    from datetime import timedelta

    now = datetime.now(timezone.utc)
    if not force and _last_reconcile:
        last = datetime.fromisoformat(_last_reconcile)
        if (now - last).total_seconds() < 1800:
            return

    _last_reconcile = now.isoformat()

    active = get_leads_by_stage(client_id, ["READY", "PENDING", "CONNECTED"])
    recovered = 0
    for lead in active:
        lead_id = lead.get("_id")
        if not lead_id:
            continue
        attempts = lead.get("Attempts", 0)
        if attempts >= MAX_ATTEMPTS and lead.get("Stage") == "PENDING":
            close_lead(lead_id, "unresponsive", f"max attempts ({MAX_ATTEMPTS}) reached")
            recovered += 1

    if recovered:
        print(f"[PipelineState] Reconciled {recovered} stale leads for {client_id}")
