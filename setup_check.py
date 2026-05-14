"""
setup_check.py — PluggedIN Pre-Launch Validator
Run this at any time to see exactly what's ready and what's missing.

Usage:
  python setup_check.py           # full check
  python setup_check.py --quick  # env vars only (no live API calls)

Green ✓ = ready
Yellow ⚠ = optional / can skip for now
Red ✗   = blocking — must fix before agents run
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

QUICK = "--quick" in sys.argv

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

passed = 0
failed = 0
warned = 0


def ok(label):
    global passed
    passed += 1
    print(f"  {GREEN}✓{RESET} {label}")


def fail(label, hint=""):
    global failed
    failed += 1
    hint_text = f"\n      → {hint}" if hint else ""
    print(f"  {RED}✗{RESET} {label}{hint_text}")


def warn(label, hint=""):
    global warned
    warned += 1
    hint_text = f"\n      → {hint}" if hint else ""
    print(f"  {YELLOW}⚠{RESET} {label}{hint_text}")


def section(title):
    print(f"\n{BOLD}{title}{RESET}")
    print("─" * 50)


def check_env(key, label, required=True, hint=""):
    val = os.getenv(key, "")
    if val and val.strip() and not val.startswith("#"):
        ok(f"{label} ({key})")
        return val
    elif required:
        fail(f"{label} ({key})", hint)
        return ""
    else:
        warn(f"{label} — optional ({key})", hint)
        return ""


def test_url(url, headers=None, label="", timeout=10):
    try:
        r = requests.get(url, headers=headers or {}, timeout=timeout)
        if r.status_code in (200, 204):
            ok(label)
            return True
        elif r.status_code == 401:
            fail(label, "Invalid API key — check .env")
        elif r.status_code == 403:
            fail(label, "Forbidden — check API key scopes/permissions")
        else:
            fail(label, f"HTTP {r.status_code}")
    except requests.exceptions.ConnectionError:
        fail(label, "Connection failed — check internet / API endpoint")
    except Exception as e:
        fail(label, str(e)[:80])
    return False


# ─────────────────────────────────────────────
# 1. CORE AI (nothing works without this)
# ─────────────────────────────────────────────
section("1. CORE AI  ← agents can't run without at least one of these")

anthropic_key = check_env(
    "ANTHROPIC_API_KEY", "Anthropic API key", required=False,
    hint="console.anthropic.com/settings/keys"
)
openrouter_key = check_env(
    "OPENROUTER_API_KEY", "OpenRouter API key", required=False,
    hint="openrouter.ai/keys — needed if no Anthropic key"
)

if not anthropic_key and not openrouter_key:
    fail("No AI key set — agents cannot run at all",
         "Fill either ANTHROPIC_API_KEY or OPENROUTER_API_KEY in .env")
elif openrouter_key and not anthropic_key:
    warn("Only OpenRouter set — agents will use OpenRouter routing (fine)")

if not QUICK and (anthropic_key or openrouter_key):
    key = openrouter_key or anthropic_key
    base = "https://openrouter.ai/api/v1" if openrouter_key else "https://api.anthropic.com/v1"
    test_url(
        f"{base}/models",
        headers={"Authorization": f"Bearer {key}"},
        label="AI API connection live"
    )


# ─────────────────────────────────────────────
# 2. AIRTABLE (the message bus — everything logs here)
# ─────────────────────────────────────────────
section("2. AIRTABLE  ← all agents log here; required to run")

airtable_token = check_env(
    "AIRTABLE_TOKEN", "Airtable API token", required=True,
    hint="airtable.com/create/tokens → scopes: data.records:read/write, schema.bases:read"
)
airtable_base = check_env(
    "AIRTABLE_BASE_PLUGGEDIN", "Airtable base ID (PluggedIN)", required=True,
    hint="Open your Airtable base → URL shows: airtable.com/[BASE_ID]/..."
)

if not QUICK and airtable_token and airtable_base:
    # Check required tables exist
    required_tables = [
        "KnowledgeLog", "Opportunities", "Leads", "CEOReports",
        "DemandSignals", "BrokerageDeals", "EcomSourcingBriefs",
        "VendorLeads", "VendorOutreach",
        "ProductOpportunities", "GTMBriefs",
        "CreatorPipeline", "ManualDMQueue",
        "CreativeAssets", "PostingCalendar", "ContentMachines",
        "Clients", "ClientBriefings",
    ]
    try:
        r = requests.get(
            f"https://api.airtable.com/v0/meta/bases/{airtable_base}/tables",
            headers={"Authorization": f"Bearer {airtable_token}"},
            timeout=15,
        )
        if r.ok:
            existing = {t["name"] for t in r.json().get("tables", [])}
            missing_tables = [t for t in required_tables if t not in existing]
            if not missing_tables:
                ok(f"All {len(required_tables)} required Airtable tables exist")
            else:
                for t in missing_tables:
                    fail(f"Missing Airtable table: {t}",
                         "Create it — see docs/setup-checklist.md for field definitions")
        else:
            fail("Could not read Airtable tables", f"HTTP {r.status_code} — check token scopes")
    except Exception as e:
        fail("Airtable table check failed", str(e)[:80])


# ─────────────────────────────────────────────
# 3. SCRAPING (trade broker + product intel need this)
# ─────────────────────────────────────────────
section("3. SCRAPING  ← trade broker + product intel")

apify = check_env(
    "APIFY_TOKEN", "Apify token", required=True,
    hint="console.apify.com/settings/integrations"
)
tinyfish = check_env(
    "TINYFISH_API_KEY", "TinyFish API key", required=False,
    hint="tinyfish.io/dashboard — used for trade board scraping"
)

if not QUICK and apify:
    test_url(
        "https://api.apify.com/v2/user/me",
        headers={"Authorization": f"Bearer {apify}"},
        label="Apify API connection live"
    )


# ─────────────────────────────────────────────
# 4. WHATSAPP BRIEFING (daily 07:00 briefing to your phone)
# ─────────────────────────────────────────────
section("4. WHATSAPP BRIEFING  ← daily briefing to your phone")

check_env(
    "TWILIO_ACCOUNT_SID", "Twilio Account SID", required=True,
    hint="console.twilio.com → Account Info"
)
check_env(
    "TWILIO_AUTH_TOKEN", "Twilio Auth Token", required=True,
    hint="console.twilio.com → Account Info"
)
check_env(
    "TWILIO_WHATSAPP_FROM", "Twilio WhatsApp sender", required=True,
    hint="Default: whatsapp:+14155238886 (sandbox) — already in .env"
)
check_env(
    "QASSIM_PHONE", "Your phone number for briefings", required=True,
    hint="Format: +447XXXXXXXXX — your WhatsApp number"
)


# ─────────────────────────────────────────────
# 5. EMAIL OUTREACH (vendor + creator outreach emails)
# ─────────────────────────────────────────────
section("5. EMAIL OUTREACH  ← sends vendor + creator emails")

check_env(
    "GMAIL_USER", "Gmail address", required=True,
    hint="The Gmail account that sends outreach emails"
)
check_env(
    "GMAIL_APP_PASSWORD", "Gmail App Password", required=True,
    hint="myaccount.google.com → Security → 2FA on → App Passwords → Mail"
)


# ─────────────────────────────────────────────
# 6. CREATOMATE (static + video ad rendering)
# ─────────────────────────────────────────────
section("6. CREATOMATE  ← renders image + video ads automatically")

creatomate = check_env(
    "CREATOMATE_API_KEY", "Creatomate API key", required=False,
    hint="creatomate.com/dashboard → API — free tier: 10 renders/month"
)

template_keys = [
    ("CREATOMATE_TMPL_STATIC_1X1", "Template: Static 1x1 image"),
    ("CREATOMATE_TMPL_STATIC_9X16", "Template: Static 9x16 image"),
    ("CREATOMATE_TMPL_STATIC_4X5", "Template: Static 4x5 image"),
    ("CREATOMATE_TMPL_VIDEO_SHOWCASE", "Template: Product showcase video"),
    ("CREATOMATE_TMPL_VIDEO_UGC", "Template: UGC frame video"),
]
for key, label in template_keys:
    check_env(key, label, required=False,
              hint="Create template in Creatomate dashboard → copy Template ID")

if not QUICK and creatomate:
    test_url(
        "https://api.creatomate.com/v1/templates",
        headers={"Authorization": f"Bearer {creatomate}"},
        label="Creatomate API connection live"
    )


# ─────────────────────────────────────────────
# 7. ELEVENLABS (AI voiceover)
# ─────────────────────────────────────────────
section("7. ELEVENLABS  ← AI voiceover for ads (optional but recommended)")

elevenlabs = check_env(
    "ELEVENLABS_API_KEY", "ElevenLabs API key", required=False,
    hint="elevenlabs.io → Profile → API Key — free tier: 10k chars/month"
)

if not QUICK and elevenlabs:
    test_url(
        "https://api.elevenlabs.io/v1/user",
        headers={"xi-api-key": elevenlabs},
        label="ElevenLabs API connection live"
    )


# ─────────────────────────────────────────────
# 8. GOOGLE DRIVE (saves creatives to your Drive)
# ─────────────────────────────────────────────
section("8. GOOGLE DRIVE  ← saves all creative assets to your Drive")

sa_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
if sa_path and os.path.exists(sa_path):
    ok(f"Service account JSON found ({sa_path})")
else:
    warn("Google Drive service account JSON not found",
         "console.cloud.google.com → Drive API → Service Account → download JSON → save to secrets/")

check_env(
    "GDRIVE_ROOT_FOLDER_ID", "Google Drive root folder ID", required=False,
    hint="Open your 'PluggedIN Creative' Drive folder → copy ID from URL"
)


# ─────────────────────────────────────────────
# 9. SOCIAL POSTING (organic content machine)
# ─────────────────────────────────────────────
section("9. SOCIAL POSTING  ← posts content to TikTok, Instagram, Pinterest")

buffer = check_env(
    "BUFFER_ACCESS_TOKEN", "Buffer access token (easiest)", required=False,
    hint="buffer.com → Connect your socials → buffer.com/developers for token"
)
check_env("BUFFER_PROFILE_TIKTOK",    "Buffer: TikTok profile ID",    required=False)
check_env("BUFFER_PROFILE_INSTAGRAM", "Buffer: Instagram profile ID", required=False)
check_env("BUFFER_PROFILE_PINTEREST", "Buffer: Pinterest profile ID", required=False)

if not buffer:
    warn("No social posting configured",
         "Set up Buffer first (easiest) — direct APIs can be added later")


# ─────────────────────────────────────────────
# 10. CRON JOBS (automation schedule)
# ─────────────────────────────────────────────
section("10. CRON JOBS  ← schedules agents to run automatically")

import subprocess
try:
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    crontab_content = result.stdout
    if "orchestrator.py" in crontab_content:
        ok("Cron jobs installed (orchestrator.py found in crontab)")
    else:
        fail("Cron jobs not installed",
             "Run: python setup_check.py --install-cron  OR  bash install_cron.sh")
except Exception:
    warn("Could not check crontab", "Run 'crontab -l' manually to verify")


# ─────────────────────────────────────────────
# 11. OPTIONAL / LATER
# ─────────────────────────────────────────────
section("11. OPTIONAL  ← not needed for Day 1")

check_env("VAPI_API_KEY", "VAPI voice agents", required=False,
          hint="dashboard.vapi.ai — for phone qualifier + receptionist agents")
check_env("CALCOM_API_KEY", "Cal.com booking", required=False,
          hint="cal.com/settings/developer/api-keys")
check_env("VIBE_PROSPECTING_KEY", "Vibe prospecting (B2B leads)", required=False)
check_env("TIKTOK_ACCESS_TOKEN", "TikTok direct API", required=False,
          hint="Use Buffer first — direct API needs developer app approval")
check_env("INSTAGRAM_ACCESS_TOKEN", "Instagram direct API", required=False,
          hint="Use Buffer first")
check_env("PINTEREST_ACCESS_TOKEN", "Pinterest direct API", required=False,
          hint="Use Buffer first")


# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
total = passed + failed + warned
print(f"\n{'═'*50}")
print(f"{BOLD}SETUP SUMMARY{RESET}")
print(f"{'═'*50}")
print(f"  {GREEN}✓ Ready:    {passed}{RESET}")
print(f"  {RED}✗ Blocking: {failed}{RESET}")
print(f"  {YELLOW}⚠ Optional: {warned}{RESET}")

if failed == 0:
    print(f"\n{GREEN}{BOLD}✓ ALL REQUIRED CHECKS PASSED — you're ready to launch!{RESET}")
    print(f"\nRun a dry-run to confirm everything works end-to-end:")
    print(f"  python orchestrator.py --dry-run")
    print(f"\nThen go live:")
    print(f"  bash install_cron.sh")
else:
    print(f"\n{RED}{BOLD}✗ {failed} blocking issue(s) — fix these before launching{RESET}")
    print(f"\nQuickest path to first agent running:")
    print(f"  1. Fill ANTHROPIC_API_KEY or complete OPENROUTER_API_KEY")
    print(f"  2. Create Airtable base + tables (docs/setup-checklist.md)")
    print(f"  3. Fill AIRTABLE_TOKEN + AIRTABLE_BASE_PLUGGEDIN")
    print(f"  4. Run: python orchestrator.py --dry-run")

print()
