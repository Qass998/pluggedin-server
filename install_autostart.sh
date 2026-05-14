#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  PluggedIN OS — Auto-start Installer
#  Registers the API server as a Mac background service.
#  After running this, the server starts automatically on login
#  and restarts if it ever crashes. No Terminal needed.
#
#  Run once:   bash install_autostart.sh
#  To remove:  bash install_autostart.sh --uninstall
# ─────────────────────────────────────────────────────────────

set -e

PLIST_NAME="com.pluggedin.os"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$PLIST_DIR/$PLIST_NAME.plist"
PLUGGEDIN_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON=$(which python3)
LOG_DIR="$HOME/Library/Logs/PluggedIN"

GRN="\033[32m"; YLW="\033[33m"; RED="\033[31m"; BLD="\033[1m"; RST="\033[0m"

echo ""
echo -e "${BLD}PluggedIN OS — Auto-start Installer${RST}"
echo "─────────────────────────────────────"

# ── Uninstall mode ──────────────────────────────────────────
if [[ "$1" == "--uninstall" ]]; then
  echo -e "${YLW}Removing auto-start...${RST}"
  launchctl unload "$PLIST_FILE" 2>/dev/null || true
  rm -f "$PLIST_FILE"
  echo -e "${GRN}✓ Removed. Server will no longer auto-start.${RST}"
  exit 0
fi

# ── Checks ───────────────────────────────────────────────────
if [ ! -f "$PLUGGEDIN_DIR/api/server.py" ]; then
  echo -e "${RED}✗ api/server.py not found in $PLUGGEDIN_DIR${RST}"
  exit 1
fi

mkdir -p "$PLIST_DIR"
mkdir -p "$LOG_DIR"

# ── Write LaunchAgent plist ──────────────────────────────────
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$PLUGGEDIN_DIR/api/server.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$PLUGGEDIN_DIR</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>
        <string>$PLUGGEDIN_DIR</string>
    </dict>

    <!-- Start on login -->
    <key>RunAtLoad</key>
    <true/>

    <!-- Restart if it crashes -->
    <key>KeepAlive</key>
    <true/>

    <!-- Wait 3s before restarting after a crash -->
    <key>ThrottleInterval</key>
    <integer>3</integer>

    <!-- Log output -->
    <key>StandardOutPath</key>
    <string>$LOG_DIR/server.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/server-error.log</string>
</dict>
</plist>
EOF

echo -e "${GRN}✓ LaunchAgent written${RST}"

# ── Load it now (no reboot needed) ──────────────────────────
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

echo -e "${GRN}✓ Service registered and started${RST}"
echo ""

# ── Wait and verify ──────────────────────────────────────────
echo -n "  Waiting for server..."
for i in $(seq 1 12); do
  sleep 0.5
  if curl -s --max-time 1 http://localhost:8000/health > /dev/null 2>&1; then
    echo -e " ${GRN}online!${RST}"
    break
  fi
  echo -n "."
done

echo ""
echo -e "${BLD}Done.${RST} PluggedIN OS will now:"
echo "  ✓ Start automatically every time your Mac logs in"
echo "  ✓ Restart automatically if it ever crashes"
echo "  ✓ Run silently in the background — no Terminal needed"
echo ""
echo -e "  Dashboard: ${BLD}http://localhost:8000${RST}"
echo -e "  Logs:      ${BLD}$LOG_DIR/server.log${RST}"
echo ""
echo -e "  To remove:  ${YLW}bash install_autostart.sh --uninstall${RST}"
echo ""
