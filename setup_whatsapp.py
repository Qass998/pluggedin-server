#!/usr/bin/env python3
"""
setup_whatsapp.py — WhatsApp Business Onboarding (Render Edition)

Run this once per client to configure their WhatsApp agent.
The server runs permanently on Render — no local server or ngrok needed.

Usage:
    python3 setup_whatsapp.py
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

RENDER_URL = os.getenv("RENDER_URL", "").rstrip("/")

CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def c(text, colour): return f"{colour}{text}{RESET}"
def header(text):    print(f"\n{BOLD}{CYAN}{'─'*50}{RESET}\n{BOLD}  {text}{RESET}\n{DIM}{'─'*50}{RESET}")
def ask(prompt, default=""):
    suffix = f" [{default}]" if default else ""
    val = input(f"  {CYAN}→{RESET} {prompt}{suffix}: ").strip()
    return val if val else default
def ask_list(prompt):
    print(f"  {CYAN}→{RESET} {prompt} (one per line, blank to finish):")
    items = []
    while True:
        val = input("    • ").strip()
        if not val: break
        items.append(val)
    return items


def print_banner():
    print(f"""
{CYAN}{BOLD}
  ██████╗ ██╗     ██╗   ██╗ ██████╗  ██████╗ ███████╗██████╗ ██╗███╗
  ██╔══██╗██║     ██║   ██║██╔════╝ ██╔════╝ ██╔════╝██╔══██╗██║████╗
  ██████╔╝██║     ██║   ██║██║  ███╗██║  ███╗█████╗  ██║  ██║██║██╔██╗
  ██╔═══╝ ██║     ██║   ██║██║   ██║██║   ██║██╔══╝  ██║  ██║██║██║╚██╗
  ██║     ███████╗╚██████╔╝╚██████╔╝╚██████╔╝███████╗██████╔╝██║██║ ╚██╗
  ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═════╝ ╚═╝╚═╝  ╚═╝
{RESET}
  {DIM}WhatsApp Business Setup — Render Edition{RESET}
""")


def get_render_url() -> str:
    """Get or confirm the Render deployment URL."""
    global RENDER_URL
    header("STEP 0 — Render URL")

    if RENDER_URL:
        print(f"  {GREEN}Using RENDER_URL from .env: {RENDER_URL}{RESET}")
        return RENDER_URL

    print(f"  {DIM}Your Render service URL looks like:{RESET}")
    print(f"  {CYAN}https://pluggedin-api.onrender.com{RESET}\n")
    url = ask("Paste your Render service URL").rstrip("/")
    if not url:
        print(f"  {RED}❌ No URL provided. Add RENDER_URL to .env and re-run.{RESET}")
        raise SystemExit(1)

    RENDER_URL = url
    return url


def collect_business_profile() -> dict:
    header("STEP 1 — Business Profile")
    print(f"  {DIM}Tell me about the business this WhatsApp agent will represent.{RESET}\n")

    profile = {}
    profile["business_name"]    = ask("Business name")
    profile["industry"]         = ask("Industry (e.g. Legal, Recruitment, Clinic, Restaurant)")
    profile["location"]         = ask("Location (city/country)", "UK")
    profile["business_hours"]   = ask("Business hours", "Monday to Friday, 9am to 6pm")
    profile["tone"]             = ask("Tone (professional / friendly / luxury)", "professional and warm")
    profile["language"]         = ask("Primary language", "English")
    profile["cal_link"]         = ask("Booking link — Cal.com or Calendly (leave blank if none)", "")
    profile["ceo_phone"]        = ask(
        "Client's WhatsApp number for hot lead alerts (e.g. +447847221722)",
        os.getenv("QASSIM_PHONE", "").replace("whatsapp:", "")
    )

    header("STEP 2 — Services")
    print(f"  {DIM}What services does this business offer?{RESET}\n")
    profile["services"] = ask_list("Services")
    if not profile["services"]:
        profile["services"] = ["General enquiries"]

    header("STEP 3 — FAQs")
    print(f"  {DIM}Add common questions the AI should know how to answer.{RESET}\n")
    faqs = []
    print(f"  {CYAN}→{RESET} Add FAQs (blank question to skip):")
    for i in range(1, 8):
        q = input(f"    Q{i}: ").strip()
        if not q: break
        a = input(f"    A{i}: ").strip()
        if a: faqs.append({"question": q, "answer": a})
    profile["faqs"] = faqs

    header("STEP 4 — Twilio WhatsApp Number")
    print(f"  {DIM}Which Twilio WhatsApp number will this client use?{RESET}")
    print(f"  {DIM}Sandbox testing: +14155238886  |  Production: buy a number in Twilio{RESET}\n")
    raw = ask("Twilio WhatsApp number (e.g. +14155238886)", "+14155238886")
    profile["twilio_number"] = raw if raw.startswith("whatsapp:") else f"whatsapp:{raw}"

    return profile


def save_config(profile: dict, config: dict):
    """Save client config locally as a backup record."""
    config_path = os.path.join(os.path.dirname(__file__), "config", "whatsapp_clients.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    existing = []
    if os.path.exists(config_path):
        with open(config_path) as f:
            existing = json.load(f)

    existing = [c for c in existing if c.get("twilio_number") != profile["twilio_number"]]
    existing.append({**config, "twilio_number": profile["twilio_number"]})

    with open(config_path, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"  {GREEN}✅ Config saved locally → config/whatsapp_clients.json{RESET}")


def register_on_render(render_url: str, profile: dict, config: dict):
    """Register this client with the live Render server."""
    header("Registering with Render Server")

    try:
        r = requests.post(
            f"{render_url}/whatsapp/register",
            json={"twilio_number": profile["twilio_number"], "config": config},
            timeout=15,
        )
        if r.status_code == 200:
            print(f"  {GREEN}✅ Client registered on live server ✓{RESET}")
        else:
            print(f"  {YELLOW}⚠️  Server returned {r.status_code} — config saved locally, will load on next deploy{RESET}")
    except Exception as e:
        print(f"  {YELLOW}⚠️  Could not reach Render server ({e}){RESET}")
        print(f"  {DIM}Config saved locally — will load automatically on next server restart/deploy.{RESET}")


def print_twilio_instructions(render_url: str, profile: dict):
    header("📱 CONFIGURE TWILIO")

    webhook = f"{render_url}/webhook/whatsapp"
    number  = profile["twilio_number"].replace("whatsapp:", "")

    print(f"""
  {BOLD}Webhook URL to paste into Twilio:{RESET}
  {CYAN}{BOLD}  {webhook}{RESET}

  {BOLD}Steps:{RESET}

  1. Go to {CYAN}console.twilio.com{RESET}
  2. Messaging → Settings → WhatsApp Sandbox (or your number settings)
  3. Set {BOLD}"When a message comes in"{RESET} to:
     {CYAN}{webhook}{RESET}
  4. Method: {BOLD}HTTP POST{RESET}
  5. Save

  {BOLD}To test:{RESET}
  WhatsApp {CYAN}{number}{RESET} from any phone.
  The agent responds as {CYAN}{profile['business_name']}{RESET}.

  {DIM}Sandbox only: the tester must first send{RESET}
  {DIM}"join <your-keyword>" to +14155238886{RESET}
  {DIM}Production: buy a dedicated number in Twilio (~$5/month){RESET}
""")


def print_summary(profile: dict, render_url: str):
    header("✅ SETUP COMPLETE")
    webhook = f"{render_url}/webhook/whatsapp"
    print(f"""
  {BOLD}Business:{RESET}     {profile['business_name']}
  {BOLD}Industry:{RESET}     {profile['industry']}
  {BOLD}Hours:{RESET}        {profile['business_hours']}
  {BOLD}Services:{RESET}     {', '.join(profile['services'][:3])}{'...' if len(profile['services']) > 3 else ''}
  {BOLD}FAQs loaded:{RESET}  {len(profile['faqs'])}
  {BOLD}Booking link:{RESET} {profile['cal_link'] or 'Not set'}
  {BOLD}Alerts to:{RESET}    {profile['ceo_phone']}
  {BOLD}Number:{RESET}       {profile['twilio_number']}
  {BOLD}Webhook:{RESET}      {webhook}

  {DIM}The agent is live on Render. When a customer messages,
  Claude Haiku responds in character — warm, knowledgeable, on-brand.
  Hot leads fire a WhatsApp alert to the client immediately.{RESET}
""")


def main():
    print_banner()

    render_url = get_render_url()
    profile    = collect_business_profile()

    config = {
        "client_id":      f"client_{profile['business_name'].lower().replace(' ', '_')}",
        "client_name":    profile["business_name"],
        "business_name":  profile["business_name"],
        "industry":       profile["industry"],
        "location":       profile["location"],
        "cal_link":       profile["cal_link"],
        "business_hours": profile["business_hours"],
        "ceo_phone":      f"whatsapp:{profile['ceo_phone']}" if not profile["ceo_phone"].startswith("whatsapp:") else profile["ceo_phone"],
        "faqs":           profile["faqs"],
        "tone":           profile["tone"],
        "language":       profile["language"],
        "services":       profile["services"],
    }

    save_config(profile, config)
    register_on_render(render_url, profile, config)
    print_twilio_instructions(render_url, profile)
    print_summary(profile, render_url)


if __name__ == "__main__":
    main()
