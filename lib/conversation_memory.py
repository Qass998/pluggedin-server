"""
lib/conversation_memory.py — Fact-Based Lead Conversation Memory

mem0-style incremental fact extraction per lead.
Facts are extracted only from INBOUND messages (lead's words).
Stored as JSON in Airtable Lead record → Chat Summary field.

Pattern from: github.com/eracle/OpenOutreach
Adapted for: PluggedIN stack (Airtable + Anthropic)
"""
from __future__ import annotations
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

_FACT_EXTRACT_PROMPT = """You are extracting facts about a sales prospect from their messages.

Existing facts:
{existing_facts}

New inbound messages from the prospect:
{new_messages}

Extract facts ONLY from the prospect's words — never from the seller's messages.
Facts to capture: company size, role/seniority, pain points, budget signals, timeline, objections, interest level, decision process.

Return JSON with three arrays:
{{
  "add":    ["new fact 1", "new fact 2"],
  "update": [["old fact text", "corrected fact text"]],
  "delete": ["fact text to remove (contradicted or no longer relevant)"]
}}

Rules:
- Be specific and quote numbers/details when mentioned
- Mark budget signals as "Budget signal: ..."
- Mark objections as "Objection: ..."
- If no changes, return {{"add":[],"update":[],"delete":[]}}
Return ONLY valid JSON."""


# ─────────────────────────────────────────────
# AIRTABLE HELPERS
# ─────────────────────────────────────────────

def _load_facts(lead_id: str) -> list[str]:
    try:
        from lib.airtable_client import AirtableClient
        at     = AirtableClient(os.getenv("AIRTABLE_TOKEN",""), os.getenv("AIRTABLE_BASE_PLUGGEDIN",""))
        record = at.get_record("Leads", lead_id)
        raw    = (record or {}).get("fields", {}).get("Chat Summary", "[]")
        return json.loads(raw) if raw else []
    except Exception:
        return []


def _save_facts(lead_id: str, facts: list[str]):
    try:
        from lib.airtable_client import AirtableClient
        at = AirtableClient(os.getenv("AIRTABLE_TOKEN",""), os.getenv("AIRTABLE_BASE_PLUGGEDIN",""))
        at.update_record("Leads", lead_id, {"Chat Summary": json.dumps(facts)})
    except Exception as e:
        print(f"[ConvMemory] save_facts error: {e}")


# ─────────────────────────────────────────────
# FACT EXTRACTION
# ─────────────────────────────────────────────

def extract_and_update_facts(lead_id: str, new_inbound_messages: list[str]) -> list[str]:
    """
    Extract facts from new inbound messages and merge with existing facts.
    Only call with INBOUND messages — never pass seller messages.
    Returns updated fact list.
    """
    if not new_inbound_messages:
        return _load_facts(lead_id)

    existing = _load_facts(lead_id)

    if not ANTHROPIC_API_KEY:
        # Fallback: just append messages as raw facts
        updated = existing + [f"Said: {m[:120]}" for m in new_inbound_messages[:3]]
        _save_facts(lead_id, updated)
        return updated

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        prompt = _FACT_EXTRACT_PROMPT.format(
            existing_facts=json.dumps(existing, indent=2) if existing else "[]",
            new_messages="\n".join([f"- {m}" for m in new_inbound_messages]),
        )

        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        ops = json.loads(resp.content[0].text.strip().replace("```json","").replace("```",""))

        updated = list(existing)

        # Apply ADD
        for fact in ops.get("add", []):
            if fact and fact not in updated:
                updated.append(fact)

        # Apply UPDATE
        for pair in ops.get("update", []):
            if len(pair) == 2:
                old, new = pair
                try:
                    idx = updated.index(old)
                    updated[idx] = new
                except ValueError:
                    updated.append(new)

        # Apply DELETE
        for fact in ops.get("delete", []):
            if fact in updated:
                updated.remove(fact)

        _save_facts(lead_id, updated)
        return updated

    except Exception as e:
        print(f"[ConvMemory] extract_facts error: {e}")
        return existing


def get_facts(lead_id: str) -> list[str]:
    return _load_facts(lead_id)


def clear_facts(lead_id: str):
    _save_facts(lead_id, [])


def format_facts_for_prompt(facts: list[str]) -> str:
    """Returns a concise bullet-point string for use in Claude prompts."""
    if not facts:
        return "No facts collected yet."
    return "\n".join([f"• {f}" for f in facts])
