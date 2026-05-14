"""
webhook_server.py — PluggedIN Webhook Server

Receives webhooks from VAPI (calls) and Twilio (WhatsApp).
Runs as a persistent Flask server on port 5001.

Start it:
  python webhook_server.py

Or with gunicorn (recommended for production):
  gunicorn webhook_server:app --bind 0.0.0.0:5001 --workers 2

Expose it publicly via ngrok (for testing):
  ngrok http 5001
  → Copy the https URL and set WEBHOOK_BASE_URL in .env

For production:
  Deploy to a VPS or Railway.app and point WEBHOOK_BASE_URL to it.

Endpoints:
  POST /webhook/vapi      — VAPI end-of-call-report
  POST /webhook/whatsapp  — Twilio inbound WhatsApp messages
  POST /webhook/calcom    — Cal.com booking confirmations
  GET  /health            — Health check
"""

import os
import json
import hmac
import hashlib
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")  # Optional: set in .env for security


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "PluggedIN Webhook Server"}), 200


# ─────────────────────────────────────────────
# VAPI — END OF CALL REPORT
# ─────────────────────────────────────────────

@app.route("/webhook/vapi", methods=["POST"])
def vapi_webhook():
    """
    Receives VAPI end-of-call-report webhooks.
    Triggered automatically when any inbound call ends.

    VAPI sends:
    {
      "message": {
        "type": "end-of-call-report",
        "call": { ...full call object with transcript, summary, metadata... }
      }
    }
    """
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"error": "no payload"}), 400

        message = payload.get("message", payload)
        msg_type = message.get("type", "")

        print(f"\n[webhook] Received VAPI event: {msg_type}")

        if msg_type == "end-of-call-report":
            call = message.get("call", {})
            call_id  = call.get("id", "unknown")
            metadata = call.get("metadata", {})
            duration = call.get("duration", 0)
            brand    = metadata.get("brand", "unknown")

            print(f"[webhook] Call ended — ID: {call_id} | Brand: {brand} | Duration: {duration}s")

            # Process asynchronously-ish (Flask is sync but this is fast enough)
            try:
                from lib.vapi_qualifier import handle_call_completed
                result = handle_call_completed(message)
                print(f"[webhook] ✓ Call processed — action: {result.get('action')} | score: {result.get('score')}")
                return jsonify({"status": "processed", "action": result.get("action")}), 200
            except Exception as e:
                print(f"[webhook] ERROR processing call {call_id}: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({"status": "error", "message": str(e)}), 500

        elif msg_type == "status-update":
            # Informational — just acknowledge
            status = message.get("status", "")
            print(f"[webhook] VAPI status update: {status}")
            return jsonify({"status": "acknowledged"}), 200

        else:
            print(f"[webhook] Unhandled event type: {msg_type}")
            return jsonify({"status": "ignored"}), 200

    except Exception as e:
        print(f"[webhook] Unhandled error: {e}")
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# TWILIO — INBOUND WHATSAPP MESSAGES
# ─────────────────────────────────────────────

@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """
    Receives inbound WhatsApp messages from Twilio.

    Set this URL in Twilio Console:
      Phone Numbers → Your Number → Messaging → Webhook URL
      → https://yourdomain.com/webhook/whatsapp

    Twilio sends form-encoded POST with:
      From        — customer's WhatsApp number (whatsapp:+447...)
      To          — client's Twilio number (whatsapp:+14155...)
      Body        — message text
      ProfileName — customer's WhatsApp display name
    """
    try:
        from_number  = request.form.get("From", "")
        to_number    = request.form.get("To", "")
        body         = request.form.get("Body", "").strip()
        profile_name = request.form.get("ProfileName", "")

        if not from_number or not body:
            return "<Response/>", 200  # Twilio expects TwiML or empty 200

        print(f"\n[WhatsApp] Inbound: {from_number} → {to_number}: {body[:60]}")

        from lib.whatsapp_agent import handle_incoming_message
        handle_incoming_message(
            from_number=from_number,
            to_number=to_number,
            body=body,
            profile_name=profile_name,
        )

        # Return empty TwiML — we already sent the reply via Twilio API
        return "<Response/>", 200

    except Exception as e:
        print(f"[WhatsApp] Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return "<Response/>", 200  # Always 200 to Twilio to avoid retries


# ─────────────────────────────────────────────
# CAL.COM — BOOKING CONFIRMATION (optional)
# ─────────────────────────────────────────────

@app.route("/webhook/calcom", methods=["POST"])
def calcom_webhook():
    """
    Optional: Cal.com sends booking confirmations here.
    Use this to trigger follow-up actions when a meeting is confirmed.
    Set in Cal.com: Settings → Webhooks → add this URL
    """
    try:
        payload = request.get_json(force=True)
        event   = payload.get("triggerEvent", "")
        booking = payload.get("payload", {})

        print(f"[webhook] Cal.com event: {event}")

        if event == "BOOKING_CREATED":
            attendee = booking.get("attendees", [{}])[0]
            name     = attendee.get("name", "Unknown")
            email    = attendee.get("email", "")
            start    = booking.get("startTime", "")
            print(f"[webhook] ✓ Booking confirmed: {name} ({email}) at {start}")

            # Alert CEO via WhatsApp
            try:
                from lib.whatsapp_agent import _alert_ceo_booking_confirmed, DEFAULT_CLIENT_CONFIG
                _alert_ceo_booking_confirmed(DEFAULT_CLIENT_CONFIG, name, start)
            except Exception as e:
                print(f"[webhook] CEO booking alert error: {e}")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"[webhook] Cal.com webhook error: {e}")
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("WEBHOOK_PORT", 5001))
    print(f"\n🔗 PluggedIN Webhook Server starting on port {port}")
    print(f"   VAPI endpoint:      http://localhost:{port}/webhook/vapi")
    print(f"   WhatsApp endpoint:  http://localhost:{port}/webhook/whatsapp")
    print(f"   Cal.com endpoint:   http://localhost:{port}/webhook/calcom")
    print(f"   Health check:       http://localhost:{port}/health")
    print(f"\n   To expose publicly (testing): ngrok http {port}")
    print(f"   Then set in Twilio Console: Messaging → Webhook → https://YOUR_NGROK/webhook/whatsapp")
    print(f"   Set WEBHOOK_BASE_URL in .env to your public URL\n")
    app.run(host="0.0.0.0", port=port, debug=False)
