"""
lib/green_api_client.py — Green API WhatsApp Integration

Green API lets any WhatsApp number (personal or business) connect
via QR code scan — no WhatsApp Business approval needed.

Setup per client:
  1. Create a free instance at greenapi.com
  2. Copy idInstance + apiTokenInstance into Airtable / .env
  3. Call provision_client() — gets QR, waits for scan, sets webhook
  4. Done — WhatsApp AI is live on their existing number

Docs: https://green-api.com/en/docs/

Instance states:
  notAuthorized  — needs QR scan
  authorized     — connected, ready
  blocked        — number banned by WhatsApp
  sleepMode      — instance inactive
"""
from __future__ import annotations
import os
import time
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("green_api")

BASE_URL = "https://api.green-api.com"
TIMEOUT  = 15


# ─────────────────────────────────────────────
# CORE API CALLS
# ─────────────────────────────────────────────

def get_state(instance_id: str, token: str) -> str:
    """
    Returns: 'notAuthorized' | 'authorized' | 'blocked' | 'sleepMode' | 'error'
    """
    try:
        url = f"{BASE_URL}/waInstance{instance_id}/getStateInstance/{token}"
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json().get("stateInstance", "error")
    except Exception as e:
        log.error(f"[GreenAPI] get_state error: {e}")
        return "error"


def get_qr_code(instance_id: str, token: str) -> dict:
    """
    Returns QR code for scanning. Client must NOT already be authorized.
    Response: {"type": "qrCode", "message": "<base64 png>"} or {"type": "alreadyLogged"}
    """
    try:
        url = f"{BASE_URL}/waInstance{instance_id}/qr/{token}"
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return {
            "ok":      True,
            "type":    data.get("type", ""),
            "qr_b64":  data.get("message", ""),  # base64 PNG
        }
    except Exception as e:
        log.error(f"[GreenAPI] get_qr_code error: {e}")
        return {"ok": False, "error": str(e)}


def set_settings(instance_id: str, token: str, webhook_url: str, **extra) -> bool:
    """
    Set the webhook URL and configure the instance.
    Called once after the client scans the QR code.
    """
    try:
        url = f"{BASE_URL}/waInstance{instance_id}/setSettings/{token}"
        payload = {
            "webhookUrl":                  webhook_url,
            "webhookUrlToken":             "",
            "delaySendMessagesMilliseconds": 1000,
            "markIncomingMessagesReaded":  "yes",
            "outgoingWebhook":             "no",
            "stateWebhook":                "no",
            "incomingWebhook":             "yes",
            **extra,
        }
        r = requests.post(url, json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        saved = r.json().get("saveSettings", False)
        log.info(f"[GreenAPI] Webhook set for instance {instance_id}: {saved}")
        return bool(saved)
    except Exception as e:
        log.error(f"[GreenAPI] set_settings error: {e}")
        return False


def send_message(instance_id: str, token: str, chat_id: str, message: str) -> dict:
    """
    Send a text message to a WhatsApp chat.
    chat_id format: "447911123456@c.us" (country code, no +, @c.us suffix)
    Returns: {"idMessage": "..."} on success
    """
    try:
        url = f"{BASE_URL}/waInstance{instance_id}/sendMessage/{token}"
        payload = {"chatId": _to_chat_id(chat_id), "message": message}
        r = requests.post(url, json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        log.info(f"[GreenAPI] Message sent to {chat_id}")
        return {"ok": True, "id": data.get("idMessage", "")}
    except Exception as e:
        log.error(f"[GreenAPI] send_message error: {e}")
        return {"ok": False, "error": str(e)}


def get_account_info(instance_id: str, token: str) -> dict:
    """Returns connected phone number and profile info."""
    try:
        url = f"{BASE_URL}/waInstance{instance_id}/getWaSettings/{token}"
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return {"ok": True, **r.json()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ─────────────────────────────────────────────
# WEBHOOK PARSER
# Parses incoming Green API webhook payloads
# ─────────────────────────────────────────────

def parse_incoming_webhook(payload: dict) -> dict | None:
    """
    Parse a Green API incomingMessageReceived webhook.
    Returns normalised message dict or None if not a text message.

    Normalised format (matches Twilio handler expectations):
    {
      "from_number": "447911123456",
      "chat_id":     "447911123456@c.us",
      "sender_name": "John Smith",
      "body":        "Hello, I need help with...",
      "instance_id": "1234567890",
    }
    """
    webhook_type = payload.get("typeWebhook", "")
    if webhook_type != "incomingMessageReceived":
        return None

    msg_data   = payload.get("messageData", {})
    msg_type   = msg_data.get("typeMessage", "")
    sender     = payload.get("senderData", {})
    instance   = payload.get("instanceData", {})

    # Only handle text messages for now
    if msg_type == "textMessage":
        body = msg_data.get("textMessageData", {}).get("textMessage", "")
    elif msg_type == "extendedTextMessage":
        body = msg_data.get("extendedTextMessageData", {}).get("text", "")
    else:
        log.info(f"[GreenAPI] Ignoring non-text message type: {msg_type}")
        return None

    chat_id     = sender.get("chatId", "")
    from_number = chat_id.replace("@c.us", "").replace("@g.us", "")

    return {
        "from_number": from_number,
        "chat_id":     chat_id,
        "sender_name": sender.get("senderName", ""),
        "body":        body.strip(),
        "instance_id": str(instance.get("idInstance", "")),
    }


# ─────────────────────────────────────────────
# PROVISION FLOW
# Called during client onboarding
# ─────────────────────────────────────────────

def provision_client(
    instance_id: str,
    token: str,
    webhook_url: str,
    poll_timeout_seconds: int = 120,
) -> dict:
    """
    Full provisioning flow:
    1. Check current state
    2. If not authorized → get QR code for scanning
    3. Poll until authorized (up to poll_timeout_seconds)
    4. Set webhook URL
    5. Return account info

    Returns:
    {
      "ok": True,
      "status": "authorized" | "timeout" | "already_connected",
      "phone": "447911123456",      # if authorized
      "qr_b64": "<base64>",         # if QR was generated
    }
    """
    state = get_state(instance_id, token)
    log.info(f"[GreenAPI] Instance {instance_id} state: {state}")

    if state == "authorized":
        # Already connected — just set webhook
        set_settings(instance_id, token, webhook_url)
        info = get_account_info(instance_id, token)
        return {
            "ok":     True,
            "status": "already_connected",
            "phone":  info.get("phone", ""),
        }

    if state == "error":
        return {"ok": False, "status": "error", "error": "Could not reach Green API — check instance credentials"}

    # Get QR code
    qr = get_qr_code(instance_id, token)
    if not qr.get("ok"):
        return {"ok": False, "status": "qr_failed", "error": qr.get("error", "")}

    result = {
        "ok":     False,
        "status": "pending_scan",
        "qr_b64": qr.get("qr_b64", ""),
    }

    # Poll for authorization
    deadline = time.time() + poll_timeout_seconds
    while time.time() < deadline:
        time.sleep(5)
        state = get_state(instance_id, token)
        if state == "authorized":
            set_settings(instance_id, token, webhook_url)
            info = get_account_info(instance_id, token)
            result.update({
                "ok":     True,
                "status": "authorized",
                "phone":  info.get("phone", ""),
            })
            log.info(f"[GreenAPI] Instance {instance_id} authorized — phone: {result['phone']}")
            return result

    result["status"] = "timeout"
    log.warning(f"[GreenAPI] QR scan timed out for instance {instance_id}")
    return result


# ─────────────────────────────────────────────
# INSTANCE REGISTRY
# Maps client_id → instance credentials
# Stored in memory + optionally Airtable
# ─────────────────────────────────────────────

_instance_registry: dict[str, dict] = {}


def register_instance(client_id: str, instance_id: str, token: str, phone: str = ""):
    """Register Green API credentials for a client."""
    _instance_registry[client_id] = {
        "instance_id": instance_id,
        "token":       token,
        "phone":       phone,
        "registered":  True,
    }
    log.info(f"[GreenAPI] Instance registered for client: {client_id}")


def get_instance(client_id: str) -> dict | None:
    """Get Green API credentials for a client."""
    return _instance_registry.get(client_id)


def get_client_by_instance(instance_id: str) -> str | None:
    """Reverse lookup: instance_id → client_id (for webhook routing)."""
    for cid, cfg in _instance_registry.items():
        if str(cfg.get("instance_id")) == str(instance_id):
            return cid
    return None


def send_to_client_number(client_id: str, to_number: str, message: str) -> bool:
    """
    Send a WhatsApp message using the client's registered Green API instance.
    to_number: any format (447911123456 / +447911123456 / 447911123456@c.us)
    """
    cfg = get_instance(client_id)
    if not cfg:
        log.error(f"[GreenAPI] No instance registered for client: {client_id}")
        return False
    result = send_message(cfg["instance_id"], cfg["token"], to_number, message)
    return result.get("ok", False)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _to_chat_id(number: str) -> str:
    """Normalise any number format to Green API chat_id format."""
    cleaned = number.replace("+", "").replace(" ", "").replace("-", "")
    if "@" in cleaned:
        return cleaned
    return f"{cleaned}@c.us"
