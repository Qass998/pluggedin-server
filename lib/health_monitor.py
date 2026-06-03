"""
lib/health_monitor.py — System Health Monitor
===============================================
Pings all PluggedIN client portals every 15 minutes.
If anything is down, sends WhatsApp alert to Qassim (operator).

Alert rules:
  - State-change only — won't spam the same alert twice
  - First failure → immediate alert
  - Recovery → "back up" alert
  - Every 6 hours while still down → reminder alert

Usage (in api/server.py scheduler):
    from lib.health_monitor import run_health_checks
    _scheduler.add_job(run_health_checks, CronTrigger(minute="*/15"), ...)
"""

import os
import json
import time
import logging
import requests
from datetime import datetime, timezone
from typing import Optional

log = logging.getLogger("health.monitor")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

META_API_URL = "https://graph.facebook.com/v22.0"
OPERATOR_PHONE = os.getenv("PLUGGEDIN_OPERATOR_PHONE", "")  # Qassim's WhatsApp

# ---- in-memory state (persists across checks within same process) ----------
_last_state: dict[str, str] = {}       # portal_id → "healthy"|"down"
_last_alerted: dict[str, float] = {}    # portal_id → last_alert_timestamp
RE_ALERT_SECONDS = 6 * 3600             # re-alert every 6 hours if still down


# ---------------------------------------------------------------------------
# Portal registry — add new client portals here
# ---------------------------------------------------------------------------

PORTALS = [
    {
        "id": "segguinee",
        "name": "SEGGUINÉE",
        "url": "https://segguinee.vercel.app",
        "health_url": "https://segguinee.vercel.app/api/health",
        "whatsapp_phone_id": os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
        "whatsapp_token": os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
        "director_phone": os.getenv("SEGGUINEE_DIRECTOR_PHONE", ""),
    },
    # Add more portals here as we deploy them
]


# ---------------------------------------------------------------------------
# Core checks
# ---------------------------------------------------------------------------

def _check_http(url: str, timeout: int = 15) -> dict:
    """Ping a URL — returns {ok, status_code, latency_ms, error}."""
    start = time.time()
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
        return {
            "ok": resp.status_code < 500,
            "status_code": resp.status_code,
            "latency_ms": round((time.time() - start) * 1000),
        }
    except requests.RequestException as e:
        return {
            "ok": False,
            "status_code": None,
            "latency_ms": round((time.time() - start) * 1000),
            "error": str(e)[:200],
        }


def _check_health_endpoint(health_url: str) -> dict:
    """Call the /api/health endpoint — returns parsed JSON or error."""
    start = time.time()
    try:
        resp = requests.get(health_url, timeout=15)
        data = resp.json()
        return {
            "ok": resp.status_code == 200,
            "status_code": resp.status_code,
            "latency_ms": round((time.time() - start) * 1000),
            "overall": data.get("overall", "unknown"),
            "services": data.get("services", {}),
        }
    except Exception as e:
        return {
            "ok": False,
            "status_code": None,
            "latency_ms": round((time.time() - start) * 1000),
            "overall": "down",
            "error": str(e)[:200],
        }


def _check_meta_api(phone_id: str, token: str) -> dict:
    """Verify Meta WhatsApp API credentials are still valid."""
    if not phone_id or not token:
        return {"ok": False, "error": "Meta credentials not configured"}
    try:
        url = f"{META_API_URL}/{phone_id}"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers, timeout=15)
        data = resp.json()
        return {
            "ok": resp.status_code == 200,
            "status_code": resp.status_code,
            "number": data.get("display_phone_number", "unknown"),
            "quality": data.get("quality_rating", "unknown"),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


# ---------------------------------------------------------------------------
# WhatsApp alerting
# ---------------------------------------------------------------------------

def _send_operator_alert(phone_id: str, token: str, body: str) -> bool:
    """Send WhatsApp alert to Qassim (operator)."""
    if not OPERATOR_PHONE:
        log.warning("[Health] Cannot send alert — PLUGGEDIN_OPERATOR_PHONE not set")
        return False

    if not phone_id or not token:
        log.warning("[Health] Cannot send alert — Meta credentials not configured")
        return False

    url = f"{META_API_URL}/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": OPERATOR_PHONE,
        "type": "text",
        "text": {"preview_url": False, "body": body[:4096]},
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        data = resp.json()
        ok = resp.status_code == 200 and "messages" in data
        if ok:
            log.info(f"[Health] Alert sent to operator — {body[:80]}...")
        else:
            log.error(f"[Health] Alert failed — {data.get('error', {}).get('message', 'unknown')}")
        return ok
    except Exception as e:
        log.error(f"[Health] Alert error: {e}")
        return False


def _should_alert(portal_id: str, new_state: str) -> bool:
    """
    Decide whether to send an alert.
    Rules:
      - State change (healthy→down or down→healthy) → always alert
      - Still down but last alert > 6 hours → re-alert
      - Still healthy → don't alert
    """
    global _last_state, _last_alerted
    old_state = _last_state.get(portal_id, "healthy")
    now = time.time()

    # State change — always alert
    if new_state != old_state:
        return True

    # Still down, re-alert every 6 hours
    if new_state == "down":
        last = _last_alerted.get(portal_id, 0)
        if (now - last) >= RE_ALERT_SECONDS:
            return True

    return False


# ---------------------------------------------------------------------------
# Main check — called by scheduler every 15 min
# ---------------------------------------------------------------------------

def run_health_checks():
    """
    Check all registered portals. Send alerts on state changes.
    Called by APScheduler every 15 minutes.
    """
    global _last_state, _last_alerted
    log.info(f"[Health] Running checks on {len(PORTALS)} portal(s)...")
    now = time.time()

    for portal in PORTALS:
        pid = portal["id"]
        name = portal["name"]
        issues: list[str] = []

        # 1. Ping portal homepage
        http = _check_http(portal["url"])
        if not http["ok"]:
            issues.append(f"Portal down: HTTP {http.get('status_code', 'N/A')} — {http.get('error', 'unknown')}")

        # 2. Health endpoint (includes Supabase check)
        health = _check_health_endpoint(portal["health_url"])
        if not health["ok"]:
            issues.append(f"Health check failed: {health.get('overall', 'unknown')} — {health.get('error', '')}")
        elif health.get("overall") == "degraded":
            svc = health.get("services", {})
            for svc_name, svc_data in svc.items():
                if isinstance(svc_data, dict) and svc_data.get("status") != "healthy":
                    issues.append(f"Service {svc_name} degraded: {svc_data.get('error', 'unknown')[:100]}")

        # 3. Meta API check
        meta = _check_meta_api(portal["whatsapp_phone_id"], portal["whatsapp_token"])
        if not meta["ok"]:
            issues.append(f"Meta API: {meta.get('error', 'unknown')[:100]}")

        # Determine state
        new_state = "down" if issues else "healthy"

        # Log
        status_line = f"{name}: HTTP {http.get('status_code','?')} ({http['latency_ms']}ms) | Health {health.get('status_code','?')} ({health['latency_ms']}ms) | Meta {'OK' if meta['ok'] else 'FAIL'}"
        if new_state == "healthy":
            log.info(f"[Health] ✓ {status_line}")
        else:
            log.error(f"[Health] ✗ {status_line}")
            for issue in issues:
                log.error(f"[Health]   → {issue}")

        # Alert if needed
        if _should_alert(pid, new_state):
            phone_id = portal["whatsapp_phone_id"]
            token = portal["whatsapp_token"]

            if new_state == "down":
                alert = (
                    f"🚨 *ALERT — {name} Portal Down*\n\n"
                    + "\n".join(f"• {i}" for i in issues)
                    + f"\n\n_Health Monitor • {datetime.now(timezone.utc).strftime('%H:%M UTC')}_"
                )
            else:
                # Recovery
                alert = (
                    f"✅ *RECOVERED — {name} Portal Back Online*\n\n"
                    f"All checks passing.\n\n"
                    f"_Health Monitor • {datetime.now(timezone.utc).strftime('%H:%M UTC')}_"
                )

            _send_operator_alert(phone_id, token, alert)
            _last_alerted[pid] = now

        # Update state
        _last_state[pid] = new_state

    log.info(f"[Health] Checks complete — {len(PORTALS)} portal(s) checked")


# ---------------------------------------------------------------------------
# Manual trigger — for testing
# ---------------------------------------------------------------------------

def run_single_check(portal_id: str) -> dict:
    """Run a single portal check and return the result. For manual testing."""
    for portal in PORTALS:
        if portal["id"] == portal_id:
            http = _check_http(portal["url"])
            health = _check_health_endpoint(portal["health_url"])
            meta = _check_meta_api(portal.get("whatsapp_phone_id", ""),
                                   portal.get("whatsapp_token", ""))
            return {
                "portal": portal["name"],
                "http": http,
                "health": health,
                "meta": meta,
                "overall": "healthy" if (http["ok"] and health["ok"] and meta["ok"]) else "degraded",
            }
    return {"error": f"Portal '{portal_id}' not registered"}
