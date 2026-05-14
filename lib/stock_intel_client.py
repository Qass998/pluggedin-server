"""
lib/stock_intel_client.py — Stock Intelligence Wrapper
PluggedIN Module 10. Real-time stock monitoring, supplier alerts,
auto-ordering thresholds, supplier portal network.
Never call external stock APIs directly. Use this.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE_PLUGGEDIN")


# ─────────────────────────────────────────────
# STOCK MONITORING
# ─────────────────────────────────────────────

def get_stock_levels(
    business_base_id: str,
    category: str = None,
) -> list[dict]:
    """
    Retrieve current stock levels for a business.
    Returns items with level, threshold, and status.
    category: optional filter e.g. "food", "beverages", "cleaning"
    """
    url = f"https://api.airtable.com/v0/{business_base_id}/Stock"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    params = {"maxRecords": 500}
    if category:
        params["filterByFormula"] = f"{{Category}} = '{category}'"

    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    records = r.json().get("records", [])

    results = []
    for rec in records:
        f = rec["fields"]
        current = f.get("CurrentStock", 0)
        threshold = f.get("ReorderThreshold", 0)
        status = (
            "critical" if current <= threshold * 0.5
            else "low" if current <= threshold
            else "ok"
        )
        results.append({
            "record_id": rec["id"],
            "item": f.get("ItemName", ""),
            "category": f.get("Category", ""),
            "current_stock": current,
            "unit": f.get("Unit", ""),
            "reorder_threshold": threshold,
            "days_remaining": f.get("DaysRemaining"),
            "supplier": f.get("Supplier", ""),
            "supplier_contact": f.get("SupplierContact", ""),
            "status": status,
        })

    return results


def get_low_stock_items(
    business_base_id: str,
    include_critical: bool = True,
) -> list[dict]:
    """
    Return only items at or below reorder threshold.
    Sorted by urgency (critical first).
    """
    all_stock = get_stock_levels(business_base_id)
    low = [item for item in all_stock if item["status"] in ("low", "critical")]
    if not include_critical:
        low = [item for item in low if item["status"] == "low"]
    return sorted(low, key=lambda x: 0 if x["status"] == "critical" else 1)


def update_stock_level(
    business_base_id: str,
    record_id: str,
    new_level: float,
    updated_by: str = "agent",
) -> dict:
    """
    Update stock level after delivery or count.
    Logs the update with timestamp.
    """
    url = f"https://api.airtable.com/v0/{business_base_id}/Stock/{record_id}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "fields": {
            "CurrentStock": new_level,
            "LastUpdated": datetime.utcnow().isoformat(),
            "UpdatedBy": updated_by,
        }
    }
    r = requests.patch(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


def log_stock_movement(
    business_base_id: str,
    item_name: str,
    movement_type: str,
    quantity: float,
    reference: str = "",
) -> dict:
    """
    Log stock in/out movements for audit trail.
    movement_type: "delivery", "usage", "adjustment", "waste"
    """
    url = f"https://api.airtable.com/v0/{business_base_id}/StockMovements"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "fields": {
            "Item": item_name,
            "Type": movement_type,
            "Quantity": quantity,
            "Reference": reference,
            "Timestamp": datetime.utcnow().isoformat(),
        }
    }
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


# ─────────────────────────────────────────────
# SUPPLIER ALERTS
# ─────────────────────────────────────────────

def alert_supplier(
    supplier_email: str,
    supplier_name: str,
    business_name: str,
    items_needed: list[dict],
    urgency: str = "normal",
) -> dict:
    """
    Send an automatic reorder alert to a supplier via email.
    items_needed: list of {"item": str, "quantity": float, "unit": str}
    urgency: "normal", "urgent", "critical"
    Uses Gmail MCP in practice — this drafts the content.
    Returns email content dict ready to send.
    """
    subject_prefix = {
        "normal": "Reorder Request",
        "urgent": "URGENT: Reorder Required",
        "critical": "CRITICAL: Immediate Reorder Needed",
    }.get(urgency, "Reorder Request")

    items_text = "\n".join(
        [f"- {item['item']}: {item['quantity']} {item['unit']}" for item in items_needed]
    )

    body = (
        f"Dear {supplier_name},\n\n"
        f"This is an automated stock alert from {business_name}.\n\n"
        f"The following items have reached reorder threshold and require replenishment:\n\n"
        f"{items_text}\n\n"
        f"Please confirm availability and expected delivery date at your earliest convenience.\n\n"
        f"This order has been automatically generated by our stock intelligence system.\n\n"
        f"Thank you,\n{business_name} Operations"
    )

    return {
        "to": supplier_email,
        "subject": f"{subject_prefix} — {business_name}",
        "body": body,
        "urgency": urgency,
        "items_count": len(items_needed),
    }


def auto_reorder_check(
    business_base_id: str,
    business_name: str,
    dry_run: bool = False,
) -> dict:
    """
    Run automatic reorder check. Find low items, group by supplier,
    draft supplier alerts. If dry_run=False, logs to Airtable.
    Returns summary of actions taken.
    """
    low_items = get_low_stock_items(business_base_id)
    if not low_items:
        return {"status": "ok", "message": "All stock levels healthy", "alerts_sent": 0}

    # Group by supplier
    by_supplier = {}
    for item in low_items:
        supplier = item.get("supplier", "Unknown")
        if supplier not in by_supplier:
            by_supplier[supplier] = {
                "email": item.get("supplier_contact", ""),
                "items": [],
            }
        by_supplier[supplier]["items"].append({
            "item": item["item"],
            "quantity": item["reorder_threshold"] * 2,  # Order 2x threshold
            "unit": item["unit"],
        })

    alerts = []
    for supplier_name, data in by_supplier.items():
        urgency = "critical" if any(
            i["status"] == "critical" for i in low_items
            if i["supplier"] == supplier_name
        ) else "normal"

        alert = alert_supplier(
            supplier_email=data["email"],
            supplier_name=supplier_name,
            business_name=business_name,
            items_needed=data["items"],
            urgency=urgency,
        )
        alerts.append(alert)

        if not dry_run:
            log_stock_movement(
                business_base_id,
                item_name=", ".join([i["item"] for i in data["items"]]),
                movement_type="reorder_initiated",
                quantity=0,
                reference=f"Auto-reorder to {supplier_name}",
            )

    return {
        "status": "reorder_initiated",
        "low_items": len(low_items),
        "suppliers_alerted": len(alerts),
        "alerts": alerts,
        "dry_run": dry_run,
    }


# ─────────────────────────────────────────────
# SUPPLIER PORTAL (network effect)
# ─────────────────────────────────────────────

def register_supplier(
    supplier_name: str,
    supplier_email: str,
    supplier_phone: str,
    categories: list[str],
    regions_served: list[str],
    lead_time_days: int,
    minimum_order: float = 0,
    notes: str = "",
) -> dict:
    """
    Add a supplier to the PluggedIN supplier network.
    Once registered, they serve ALL PluggedIN clients.
    This is the network effect — one supplier, many clients.
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/Suppliers"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "fields": {
            "Name": supplier_name,
            "Email": supplier_email,
            "Phone": supplier_phone,
            "Categories": ", ".join(categories),
            "RegionsServed": ", ".join(regions_served),
            "LeadTimeDays": lead_time_days,
            "MinimumOrder": minimum_order,
            "Notes": notes,
            "RegisteredAt": datetime.utcnow().isoformat(),
            "Status": "Active",
            "ClientsServed": 0,
        }
    }
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()


def find_supplier(
    category: str,
    region: str = None,
) -> list[dict]:
    """
    Find matching suppliers for a given product category.
    Used when onboarding a new client with no supplier relationships.
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/Suppliers"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    formula = f"FIND('{category}', {{Categories}}) > 0"
    if region:
        formula = f"AND({formula}, FIND('{region}', {{RegionsServed}}) > 0)"

    params = {
        "filterByFormula": formula,
        "maxRecords": 20,
    }
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    records = r.json().get("records", [])

    return [
        {
            "record_id": rec["id"],
            "name": rec["fields"].get("Name", ""),
            "email": rec["fields"].get("Email", ""),
            "lead_time_days": rec["fields"].get("LeadTimeDays", ""),
            "minimum_order": rec["fields"].get("MinimumOrder", 0),
            "categories": rec["fields"].get("Categories", ""),
        }
        for rec in records
    ]


def get_supplier_dashboard() -> list[dict]:
    """
    Show all active suppliers and which clients they serve.
    Used for PluggedIN Live supplier portal view.
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE}/Suppliers"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    params = {
        "filterByFormula": "{Status} = 'Active'",
        "sort[0][field]": "ClientsServed",
        "sort[0][direction]": "desc",
    }
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    records = r.json().get("records", [])

    return [
        {
            "name": rec["fields"].get("Name", ""),
            "categories": rec["fields"].get("Categories", ""),
            "regions": rec["fields"].get("RegionsServed", ""),
            "clients_served": rec["fields"].get("ClientsServed", 0),
            "lead_time_days": rec["fields"].get("LeadTimeDays", ""),
        }
        for rec in records
    ]


# ─────────────────────────────────────────────
# ANALYTICS AND REPORTING
# ─────────────────────────────────────────────

def stock_summary(
    business_base_id: str,
    business_name: str,
) -> dict:
    """
    Generate stock health summary for weekly CEO briefing.
    Returns: total items, ok/low/critical counts, reorder value.
    """
    all_items = get_stock_levels(business_base_id)
    ok = sum(1 for i in all_items if i["status"] == "ok")
    low = sum(1 for i in all_items if i["status"] == "low")
    critical = sum(1 for i in all_items if i["status"] == "critical")

    summary = {
        "business": business_name,
        "total_items_tracked": len(all_items),
        "ok": ok,
        "low": low,
        "critical": critical,
        "generated_at": datetime.utcnow().isoformat(),
    }

    if critical > 0:
        summary["alert"] = f"{critical} item(s) CRITICAL — reorder immediately"
    elif low > 0:
        summary["alert"] = f"{low} item(s) below threshold — reorder this week"
    else:
        summary["alert"] = "All stock healthy"

    return summary
