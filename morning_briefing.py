#!/usr/bin/env python3
"""
morning_briefing.py — CEO Daily Briefing

Sends a WhatsApp digest + optional VAPI voice call to the CEO
summarising overnight WhatsApp conversations and hot leads.

Run via cron at 7am:
  0 7 * * * cd /path/to/PluggedIN && python3 morning_briefing.py

Or trigger manually:
  python3 morning_briefing.py
  python3 morning_briefing.py --voice        # also trigger VAPI voice call
  python3 morning_briefing.py --client gromatic
"""

import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()

QASSIM_PHONE = os.getenv("QASSIM_PHONE")


def run_briefing(voice: bool = False, client_id: str = None):
    from lib.whatsapp_agent import send_morning_briefing, trigger_voice_briefing

    print(f"[Briefing] Sending morning briefing...")

    # WhatsApp digest
    send_morning_briefing(
        ceo_phone=QASSIM_PHONE,
        client_id=client_id,
    )

    # Optional voice call
    if voice:
        ceo_raw = (QASSIM_PHONE or "").replace("whatsapp:", "")
        if ceo_raw:
            print(f"[Briefing] Triggering voice call to {ceo_raw}...")
            trigger_voice_briefing(
                ceo_phone_number=ceo_raw,
                client_id=client_id,
            )
        else:
            print("[Briefing] No CEO phone set — skipping voice call")

    print("[Briefing] Done ✓")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PluggedIN CEO Morning Briefing")
    parser.add_argument("--voice",   action="store_true", help="Also trigger VAPI voice call")
    parser.add_argument("--client",  type=str, default=None, help="Filter by client_id")
    args = parser.parse_args()

    run_briefing(voice=args.voice, client_id=args.client)
