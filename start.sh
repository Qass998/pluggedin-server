#!/bin/bash
# ─────────────────────────────────────────────
# PluggedIN — Start Everything
# Run this once. Opens the dashboard automatically.
# ─────────────────────────────────────────────

set -e
cd "$(dirname "$0")"

echo ""
echo "  ██████╗ ██╗     ██╗   ██╗ ██████╗  ██████╗ ███████╗██████╗ ██╗███╗  "
echo "  ██╔══██╗██║     ██║   ██║██╔════╝ ██╔════╝ ██╔════╝██╔══██╗██║████╗ "
echo "  ██████╔╝██║     ██║   ██║██║  ███╗██║  ███╗█████╗  ██║  ██║██║██╔██╗"
echo "  ██╔═══╝ ██║     ██║   ██║██║   ██║██║   ██║██╔══╝  ██║  ██║██║██║╚██╗"
echo "  ██║     ███████╗╚██████╔╝╚██████╔╝╚██████╔╝███████╗██████╔╝██║██║ ╚██╗"
echo "  ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═════╝ ╚═╝╚═╝  ╚═╝"
echo ""
echo "  Starting PluggedIN OS..."
echo ""

# ── Check .env ───────────────────────────────
if [ ! -f ".env" ]; then
    echo "  ❌  .env not found. Copy .env.example and fill in your keys."
    exit 1
fi

# ── Check Python deps ────────────────────────
echo "  🔧  Checking dependencies..."
pip3 install -r requirements.txt -q --break-system-packages 2>/dev/null || true
pip3 install pyngrok -q --break-system-packages 2>/dev/null || true

# ── Kill any old server on 8000 ─────────────
OLD_PID=$(lsof -ti:8000 2>/dev/null || true)
if [ -n "$OLD_PID" ]; then
    echo "  ♻️   Clearing old server on port 8000 (PID $OLD_PID)..."
    kill -9 $OLD_PID 2>/dev/null || true
    sleep 1
fi

# ── Start API server ─────────────────────────
echo "  🚀  Starting API server on http://localhost:8000..."
nohup python3 api/server.py > logs/server.log 2>&1 &
SERVER_PID=$!
echo "  ✅  Server PID: $SERVER_PID"

# ── Wait for server to be ready ──────────────
echo "  ⏳  Waiting for server..."
for i in {1..15}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "  ✅  Server is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 15 ]; then
        echo "  ⚠️   Server slow to start — check logs/server.log if dashboard doesn't load"
    fi
done

# ── Open dashboard in browser ────────────────
DASHBOARD="$(pwd)/dashboard/index.html"
echo ""
echo "  🌐  Opening dashboard..."
open "$DASHBOARD" 2>/dev/null || xdg-open "$DASHBOARD" 2>/dev/null || echo "  Open manually: file://$DASHBOARD"

echo ""
echo "  ─────────────────────────────────────────"
echo "  API:       http://localhost:8000"
echo "  Dashboard: file://$DASHBOARD"
echo "  Logs:      $(pwd)/logs/server.log"
echo "  ─────────────────────────────────────────"
echo ""
echo "  To stop: kill $SERVER_PID   (or close this terminal)"
echo ""

# ── Start ngrok tunnel ───────────────────────
echo "  🌍  Starting ngrok tunnel..."
mkdir -p logs
python3 - <<'PYEOF' > logs/ngrok.log 2>&1 &
from pyngrok import ngrok
import time, json

tunnel = ngrok.connect(8000)
url = tunnel.public_url
# Write URL to file so start.sh can read it
with open("logs/ngrok_url.txt", "w") as f:
    f.write(url)
print(f"ngrok tunnel: {url}", flush=True)

# Keep alive
try:
    while True:
        time.sleep(30)
except KeyboardInterrupt:
    ngrok.disconnect(url)
PYEOF

NGROK_PID=$!

# Wait for ngrok URL
echo "  ⏳  Waiting for ngrok..."
for i in {1..15}; do
    if [ -f "logs/ngrok_url.txt" ]; then
        NGROK_URL=$(cat logs/ngrok_url.txt)
        echo "  ✅  ngrok tunnel: $NGROK_URL"
        break
    fi
    sleep 1
done

# ── Print full summary ───────────────────────
echo ""
echo "  ─────────────────────────────────────────"
echo "  API:       http://localhost:8000"
echo "  Dashboard: file://$DASHBOARD"
echo "  Logs:      $(pwd)/logs/server.log"
if [ -n "$NGROK_URL" ]; then
echo ""
echo "  📱 TWILIO WEBHOOK URL:"
echo "  $NGROK_URL/webhook/whatsapp"
echo ""
echo "  Paste the above into Twilio → Messaging"
echo "  → Try it out → WhatsApp → Sandbox settings"
fi
echo "  ─────────────────────────────────────────"
echo ""
echo "  To stop: press Ctrl+C"
echo ""

# ── Tail the log so terminal stays useful ────
tail -f logs/server.log
