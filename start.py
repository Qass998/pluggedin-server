"""
start.py — PluggedIN OS Launcher
=================================
Double-click this file, or run:

    python3 start.py

What it does:
  1. Checks your .env is loaded
  2. Starts the FastAPI server (api/server.py) on port 8000
  3. Opens the dashboard automatically in your browser
  4. Shows a live log so you can see agents running

Press Ctrl+C to stop everything.
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
import signal
from pathlib import Path

ROOT    = Path(__file__).parent.resolve()
PORT    = int(os.getenv("PORT", 8000))
URL     = f"http://localhost:{PORT}"
SERVER  = ROOT / "api" / "server.py"
ENV     = ROOT / ".env"

# ── Colours (safe on Mac Terminal) ──────────────────────────────────────────
GRN  = "\033[32m"
YLW  = "\033[33m"
RED  = "\033[31m"
CYN  = "\033[36m"
BLD  = "\033[1m"
RST  = "\033[0m"

def banner():
    print(f"""
{CYN}{BLD}╔══════════════════════════════════════════════╗
║           PluggedIN OS — Launching           ║
║  Dashboard → {URL:<29} ║
╚══════════════════════════════════════════════╝{RST}
""")

def check_env():
    if not ENV.exists():
        print(f"{RED}✗ .env file not found at {ENV}{RST}")
        print(f"  Copy .env.example → .env and add your API keys.\n")
        return False

    content = ENV.read_text()
    missing = []
    required = ["ANTHROPIC_API_KEY", "AIRTABLE_TOKEN", "AIRTABLE_BASE_AGENCY"]
    for key in required:
        val = ""
        for line in content.splitlines():
            if line.startswith(key + "="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
        if not val or val.startswith("your_"):
            missing.append(key)

    if missing:
        print(f"{YLW}⚠  Missing .env keys: {', '.join(missing)}{RST}")
        print(f"  Agents will run in stub mode until these are set.\n")
    else:
        print(f"{GRN}✓ .env loaded — API keys present{RST}")
    return True

def check_deps():
    """Check FastAPI + uvicorn are installed."""
    try:
        import fastapi, uvicorn
        print(f"{GRN}✓ FastAPI + uvicorn ready{RST}")
        return True
    except ImportError:
        print(f"{YLW}⚠  Installing missing packages...{RST}")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "fastapi", "uvicorn", "python-dotenv", "requests", "pydantic",
            "--break-system-packages", "-q"
        ])
        print(f"{GRN}✓ Packages installed{RST}")
        return True

def open_browser_when_ready():
    """Wait for server to respond then open the browser."""
    import urllib.request
    for _ in range(30):
        time.sleep(0.5)
        try:
            urllib.request.urlopen(URL, timeout=1)
            print(f"\n{GRN}✓ Server ready — opening dashboard{RST}")
            webbrowser.open(URL)
            return
        except Exception:
            pass
    print(f"{YLW}  Server taking a while — open manually: {URL}{RST}")

def main():
    banner()
    check_env()
    check_deps()

    if not SERVER.exists():
        print(f"{RED}✗ api/server.py not found at {SERVER}{RST}")
        sys.exit(1)

    print(f"\n{BLD}Starting API server...{RST}")
    print(f"  {CYN}Logs below — agents will print here as they run{RST}\n")
    print("─" * 50)

    # Open browser in background
    threading.Thread(target=open_browser_when_ready, daemon=True).start()

    # Start the FastAPI server (this blocks — Ctrl+C stops it)
    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        cwd=str(ROOT),
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )

    def _stop(sig, frame):
        print(f"\n\n{YLW}  Stopping PluggedIN OS...{RST}")
        proc.terminate()
        proc.wait()
        print(f"{GRN}  Stopped. Goodbye.{RST}\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    proc.wait()  # Block here until server exits

if __name__ == "__main__":
    main()
