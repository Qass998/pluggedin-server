"""
core/tenant.py — PluggedIN Multi-Tenant Config Loader
======================================================
THE SPINE OF THE AGENT OS.

Every agent script starts with:
    from core.tenant import get_tenant
    tenant = get_tenant("gromatic")

The tenant object carries everything a lib/ script needs
to operate for a specific client. No hardcoded client values
anywhere else in the codebase.

Adding a new client = one row in Airtable + one block in .env.
Nothing else changes.
"""

import os
import json
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Tenant dataclass — the contract every lib/ script expects
# ---------------------------------------------------------------------------

@dataclass
class Tenant:
    # Identity
    client_id: str                        # e.g. "gromatic"
    client_name: str                      # e.g. "Gromatic"
    industry: str                         # e.g. "legal"
    plan: str                             # starter | growth | scale | enterprise

    # Airtable
    airtable_base_id: str                 # e.g. "appb2NwK5foyfJpCm"
    airtable_token: str                   # from env

    # Agency-level base (for briefings + reports — same for all tenants)
    agency_base_id: str                   # appl51bhjj9R2wtKx

    # VAPI
    vapi_api_key: str                     # from env
    vapi_assistant_id: Optional[str]      # configured per client in VAPI dashboard
    vapi_phone_number_id: Optional[str]   # one phone number per client

    # Cal.com
    calcom_api_key: str                   # from env
    calcom_event_type_id: Optional[str]   # client-specific booking link

    # WhatsApp / Green API
    whatsapp_number: Optional[str]        # client's WhatsApp number
    green_api_instance_id: Optional[str]  # Green API instance for this client
    green_api_token: Optional[str]        # Green API token for this client

    # AI Configuration
    tone: str = "professional but warm"
    language: str = "English"
    business_hours: str = "Monday to Friday, 9am to 6pm"
    faqs: list[dict] = field(default_factory=list)
    ceo_phone: Optional[str] = None       # whatsapp:+44... for alerts

    # Active modules (list of module numbers as ints, e.g. [1, 9])
    modules_active: list = field(default_factory=list)

    # Metadata
    timezone: str = "Europe/London"
    currency: str = "GBP"
    notes: str = ""


# ---------------------------------------------------------------------------
# Client registry — one block per signed client
# Loaded from env vars so secrets never live in code
# ---------------------------------------------------------------------------

def _build_registry() -> dict:
    """
    Returns a dict of client_id → Tenant.
    Add a new client by adding their env vars and a block here.
    """
    shared = {
        "airtable_token":  os.getenv("AIRTABLE_TOKEN", ""),
        "agency_base_id":  os.getenv("AIRTABLE_BASE_AGENCY", "appl51bhjj9R2wtKx"),
        "vapi_api_key":    os.getenv("VAPI_API_KEY", ""),
        "calcom_api_key":  os.getenv("CALCOM_API_KEY", ""),
    }

    registry = {}

    # ------------------------------------------------------------------
    # Gromatic — legal AI, Module 1 Presence Agent
    # ------------------------------------------------------------------
    registry["gromatic"] = Tenant(
        client_id="gromatic",
        client_name="Gromatic",
        industry="legal",
        plan="starter",
        airtable_base_id=os.getenv("AIRTABLE_BASE_GROMATIC", "appb2NwK5foyfJpCm"),
        airtable_token=shared["airtable_token"],
        agency_base_id=shared["agency_base_id"],
        vapi_api_key=shared["vapi_api_key"],
        vapi_assistant_id=os.getenv("VAPI_ASSISTANT_GROMATIC"),
        vapi_phone_number_id=os.getenv("VAPI_PHONE_GROMATIC"),
        calcom_api_key=shared["calcom_api_key"],
        calcom_event_type_id=os.getenv("CALCOM_EVENT_GROMATIC"),
        whatsapp_number=os.getenv("WHATSAPP_GROMATIC"),
        green_api_instance_id=os.getenv("GREEN_API_INSTANCE_GROMATIC"),
        green_api_token=os.getenv("GREEN_API_TOKEN_GROMATIC"),
        tone="professional, expert, and helpful",
        faqs=[
            {"question": "What services do you offer?", "answer": "We provide AI-powered legal document automation and workflow optimisation for law firms."},
            {"question": "How much does it cost?", "answer": "Our Presence Agent starts at £1,297/month and replaces an entire front-of-house department."}
        ],
        ceo_phone=os.getenv("CEO_PHONE_GROMATIC"),
        modules_active=[1],
        timezone="Europe/London",
        currency="GBP",
        notes="Damian. Legal AI. First client. Solicitors.",
    )

    # ------------------------------------------------------------------
    # Add new clients below — copy the block above, change the values
    # ------------------------------------------------------------------
    # registry["[client_id]"] = Tenant(
    #     client_id="[client_id]",
    #     client_name="[Name]",
    #     industry="[restaurant|legal|construction|logistics|healthcare]",
    #     plan="[starter|growth|scale|enterprise]",
    #     airtable_base_id=os.getenv("AIRTABLE_BASE_[CLIENT]", ""),
    #     airtable_token=shared["airtable_token"],
    #     agency_base_id=shared["agency_base_id"],
    #     vapi_api_key=shared["vapi_api_key"],
    #     vapi_assistant_id=os.getenv("VAPI_ASSISTANT_[CLIENT]"),
    #     vapi_phone_number_id=os.getenv("VAPI_PHONE_[CLIENT]"),
    #     calcom_api_key=shared["calcom_api_key"],
    #     calcom_event_type_id=os.getenv("CALCOM_EVENT_[CLIENT]"),
    #     whatsapp_number=os.getenv("WHATSAPP_[CLIENT]"),
    #     green_api_instance_id=os.getenv("GREEN_API_INSTANCE_[CLIENT]"),
    #     green_api_token=os.getenv("GREEN_API_TOKEN_[CLIENT]"),
    #     modules_active=[1, 9],
    #     timezone="Europe/London",
    #     currency="GBP",
    # )

    return registry


# Singleton — built once per process
_REGISTRY: Optional[dict] = None

def _get_registry() -> dict:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build_registry()
    return _REGISTRY


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_tenant(client_id: str) -> Tenant:
    """
    Load a tenant by client_id.

    Usage in any agent script:
        from core.tenant import get_tenant
        tenant = get_tenant("gromatic")
        airtable_base = tenant.airtable_base_id
        assistant_id  = tenant.vapi_assistant_id

    Raises ValueError if client_id is not registered.
    """
    registry = _get_registry()
    if client_id not in registry:
        registered = list(registry.keys())
        raise ValueError(
            f"Unknown client_id '{client_id}'. "
            f"Registered clients: {registered}. "
            f"Add the new client to core/tenant.py and set their env vars."
        )
    return registry[client_id]


def list_tenants() -> list[str]:
    """Return all registered client IDs."""
    return list(_get_registry().keys())


def get_all_tenants() -> list[Tenant]:
    """Return all Tenant objects — for cross-client batch operations."""
    return list(_get_registry().values())


def tenants_with_module(module_number: int) -> list[Tenant]:
    """
    Return all tenants that have a specific module active.

    Usage:
        from core.tenant import tenants_with_module
        retention_clients = tenants_with_module(9)
        for t in retention_clients:
            run_retention_os(t)
    """
    return [t for t in get_all_tenants() if module_number in t.modules_active]


def tenant_summary(tenant: Tenant) -> dict:
    """
    Return a safe (no secrets) dict summary of a tenant.
    Use for logging and briefings.
    """
    return {
        "client_id":      tenant.client_id,
        "client_name":    tenant.client_name,
        "industry":       tenant.industry,
        "plan":           tenant.plan,
        "modules_active": tenant.modules_active,
        "timezone":       tenant.timezone,
        "currency":       tenant.currency,
        "has_vapi":       bool(tenant.vapi_assistant_id),
        "has_whatsapp":   bool(tenant.whatsapp_number),
        "airtable_base":  tenant.airtable_base_id,
    }


# ---------------------------------------------------------------------------
# CLI — python core/tenant.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cid = sys.argv[1]
        try:
            t = get_tenant(cid)
            print(json.dumps(tenant_summary(t), indent=2))
        except ValueError as e:
            print(f"ERROR: {e}")
            sys.exit(1)
    else:
        print("Registered tenants:")
        for cid in list_tenants():
            t = get_tenant(cid)
            mods = ", ".join(f"M{m}" for m in t.modules_active)
            print(f"  {cid:<20} {t.plan:<12} [{mods}]  {t.industry}")
