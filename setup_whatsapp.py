#!/usr/bin/env python3
"""
setup_whatsapp.py — WhatsApp Business Onboarding

Run this once per business to configure the WhatsApp agent.
It walks you through the business profile, registers it with the agent,
then starts ngrok and gives you the webhook URL to paste into Twilio.

Usage:
    python3 setup_whatsapp.py
"""

import os
import sys
import json
import time
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

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
  {DIM}WhatsApp Business Setup{RESET}
""")


def collect_business_profile():
    header("STEP 1 — Business Profile")
    print(f"  {DIM}Tell me about the business the WhatsApp agent will represent.{RESET}\n")

    profile = {}
    profile["business_name"]    = ask("Business name", "PluggedIN")
    profile["industry"]         = ask("Industry (e.g. Legal, Recruitment, Clinic, Restaurant)", "AI Agency")
    profile["location"]         = ask("Location (city/country)", "London, UK")
    profile["business_hours"]   = ask("Business hours", "Monday to Friday, 9am to 6pm")
    profile["tone"]             = ask("Tone (professional / friendly / luxury)", "professional and warm")
    profile["language"]         = ask("Primary language", "English")
    profile["cal_link"]         = ask("Cal.com / Calendly booking link (leave blank if none)", "")
    profile["ceo_phone"]        = ask("Your WhatsApp number for hot lead alerts (e.g. +447847221722)", os.getenv("QASSIM_PHONE","").replace("whatsapp:",""))

    header("STEP 2 — Services")
    print(f"  {DIM}What services does this business offer?{RESET}\n")
    profile["services"] = ask_list("Services")
    if not profile["services"]:
        profile["services"] = ["General enquiries"]

    header("STEP 3 — FAQs")
    print(f"  {DIM}Add common questions the AI should know answers to.{RESET}\n")
    faqs = []
    print(f"  {CYAN}→{RESET} Add FAQs (blank question to skip):")
    for i in range(1, 8):
        q = input(f"    Q{i}: ").strip()
        if not q: break
        a = input(f"    A{i}: ").strip()
        if a: faqs.append({"question": q, "answer": a})
    profile["faqs"] = faqs

    header("STEP 4 — Twilio Number")
    print(f"  {DIM}Which Twilio WhatsApp number will this business use?{RESET}")
    print(f"  {DIM}For sandbox testing use: +14155238886{RESET}\n")
    raw = ask("Twilio WhatsApp number (e.g. +14155238886)", "+14155238886")
    profile["twilio_number"] = raw if raw.startswith("whatsapp:") else f"whatsapp:{raw}"

    return profile


def register_with_agent(profile):
    """Register the business with the in-memory WhatsApp agent."""
    header("Registering Business")

    # Build config for register_client()
    config = {
        "client_id":      f"client_{profile['business_name'].lower().replace(' ','_')}",
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

    # Save config file so server picks it up on startup
    config_path = os.path.join(os.path.dirname(__file__), "config", "whatsapp_clients.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    existing = []
    if os.path.exists(config_path):
        with open(config_path) as f:
            existing = json.load(f)

    # Replace if same number
    existing = [c for c in existing if c.get("twilio_number") != profile["twilio_number"]]
    existing.append({**config, "twilio_number": profile["twilio_number"]})

    with open(config_path, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"  {GREEN}✅ Business registered: {profile['business_name']}{RESET}")
    print(f"  {DIM}Config saved to config/whatsapp_clients.json{RESET}")
    return config


def check_server():
    """Check if the API server is already running."""
    try:
        r = requests.get("http://localhost:8000/health", timeout=2)
        return r.status_code == 200
    except:
        return False


def start_server():
    """Start the FastAPI server in the background."""
    header("Starting API Server")
    if check_server():
        print(f"  {GREEN}✅ Server already running on port 8000{RESET}")
        return

    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)

    proc = subprocess.Popen(
        [sys.executable, "api/server.py"],
        stdout=open(f"{log_dir}/server.log", "w"),
        stderr=subprocess.STDOUT,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

    print(f"  {DIM}Server starting (PID {proc.pid})...{RESET}")
    for i in range(15):
        time.sleep(1)
        if check_server():
            print(f"  {GREEN}✅ Server live on http://localhost:8000{RESET}")
            return
        print(f"  {DIM}  waiting... ({i+1}s){RESET}", end="\r")

    print(f"  {YELLOW}⚠️  Server slow to start — check logs/server.log{RESET}")


def register_via_api(config, twilio_number):
    """Push registration to the running server."""
    try:
        r = requests.post(
            "http://localhost:8000/whatsapp/register",
            json={"twilio_number": twilio_number, "config": config},
            timeout=5,
        )
        if r.status_code == 200:
            print(f"  {GREEN}✅ Registered with live server{RESET}")
        else:
            print(f"  {YELLOW}⚠️  Server registration returned {r.status_code} — config file will be used on next restart{RESET}")
    except Exception as e:
        print(f"  {YELLOW}⚠️  Could not reach server ({e}) — config file saved, restart server to apply{RESET}")


def start_ngrok():
    """Start ngrok tunnel and return the public URL."""
    header("Starting ngrok Tunnel")

    # Check if ngrok is installed
    try:
        subprocess.run(["ngrok", "version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"  {RED}❌ ngrok not found.{RESET}")
        print(f"  Install it: {CYAN}brew install ngrok{RESET}")
        print(f"  Then re-run this script.\n")
        return None

    # Kill existing ngrok
    subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
    time.sleep(1)

    # Start ngrok
    proc = subprocess.Popen(
        ["ngrok", "http", "8000", "--log=stdout"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"  {DIM}ngrok starting...{RESET}")
    time.sleep(3)

    # Get URL from ngrok API
    for attempt in range(10):
        try:
            r = requests.get("http://localhost:4040/api/tunnels", timeout=3)
            tunnels = r.json().get("tunnels", [])
            for t in tunnels:
                if t.get("proto") == "https":
                    url = t["public_url"]
                    print(f"  {GREEN}✅ ngrok tunnel: {url}{RESET}")
                    return url
        except:
            pass
        time.sleep(1)

    print(f"  {YELLOW}⚠️  Could not auto-detect ngrok URL — check http://localhost:4040{RESET}")
    return None


def print_twilio_instructions(public_url, profile):
    header("📱 CONFIGURE TWILIO")

    webhook = f"{public_url}/webhook/whatsapp"
    number  = profile["twilio_number"].replace("whatsapp:","")

    print(f"""
  {BOLD}Your webhook URL:{RESET}
  {CYAN}{BOLD}  {webhook}{RESET}

  {BOLD}Steps to configure Twilio:{RESET}

  1. Go to {CYAN}console.twilio.com{RESET}
  2. Messaging → Settings → WhatsApp Sandbox (or your number)
  3. Set {BOLD}"When a message comes in"{RESET} to:
     {CYAN}{webhook}{RESET}
  4. Set method to {BOLD}HTTP POST{RESET}
  5. Click Save

  {BOLD}To test:{RESET}
  WhatsApp {CYAN}{number}{RESET} from your phone.
  The agent will respond as {CYAN}{profile['business_name']}{RESET}.

  {DIM}Sandbox: your friend must first send{RESET}
  {DIM}"join <your-keyword>" to +14155238886{RESET}
""")


def print_summary(profile):
    header("✅ SETUP COMPLETE")
    print(f"""
  {BOLD}Business:{RESET}     {profile['business_name']}
  {BOLD}Industry:{RESET}     {profile['industry']}
  {BOLD}Hours:{RESET}        {profile['business_hours']}
  {BOLD}Services:{RESET}     {', '.join(profile['services'][:3])}{'...' if len(profile['services']) > 3 else ''}
  {BOLD}FAQs loaded:{RESET}  {len(profile['faqs'])}
  {BOLD}Booking link:{RESET} {profile['cal_link'] or 'Not set'}
  {BOLD}CEO alerts:{RESET}   {profile['ceo_phone']}
  {BOLD}Number:{RESET}       {profile['twilio_number']}

  {DIM}The agent knows all of this. When a customer messages,
  it will answer in character — warm, knowledgeable, on-brand.{RESET}
""")


def main():
    print_banner()

    # Collect business info
    profile = collect_business_profile()

    # Register
    config = register_with_agent(profile)

    # Start server
    start_server()

    # Register with live server
    register_via_api(config, profile["twilio_number"])

    # Start ngrok
    public_url = start_ngrok()

    if public_url:
        print_twilio_instructions(public_url, profile)
    else:
        print(f"\n  {YELLOW}Start ngrok manually:{RESET}")
        print(f"  {CYAN}ngrok http 8000{RESET}")
        print(f"  Then use the https URL + /webhook/whatsapp in Twilio\n")

    print_summary(profile)

    print(f"  {DIM}Press Ctrl+C to stop when done testing.{RESET}\n")

    # Keep alive
    try:
        while True:
            time.sleep(30)
            if check_server():
                print(f"  {DIM}[{time.strftime('%H:%M')}] Server healthy ✓{RESET}", end="\r")
    except KeyboardInterrupt:
        print(f"\n\n  {YELLOW}Shutting down. Run again to resume.{RESET}\n")


if __name__ == "__main__":
    main()
