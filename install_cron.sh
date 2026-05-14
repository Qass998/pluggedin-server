#!/bin/bash
# install_cron.sh — PluggedIN Cron Job Installer
# Run once to schedule all agents automatically.
# Usage: bash install_cron.sh

PLUGGEDIN_DIR="$HOME/Documents/AI-Agency/PluggedIN"
PYTHON=$(which python3 || which python)
LOG_DIR="$HOME/pluggedin-logs"

mkdir -p "$LOG_DIR"

echo "Installing PluggedIN cron jobs..."
echo "Directory: $PLUGGEDIN_DIR"
echo "Python:    $PYTHON"
echo "Logs:      $LOG_DIR"
echo ""

# Remove any existing PluggedIN cron jobs
crontab -l 2>/dev/null | grep -v "orchestrator.py" | grep -v "# PluggedIN" > /tmp/crontab_clean

# Add new schedule
cat >> /tmp/crontab_clean << EOF

# PluggedIN — Automated Agent Schedule
# ─────────────────────────────────────────────
# 04:00 — Intelligence phase: knowledge, trade broker, vendor scanner, product research
0 4 * * * cd $PLUGGEDIN_DIR && $PYTHON orchestrator.py --phase intelligence >> $LOG_DIR/intelligence.log 2>&1

# 06:30 — CEO reports compiled from intelligence outputs
30 6 * * * cd $PLUGGEDIN_DIR && $PYTHON orchestrator.py --phase ceo >> $LOG_DIR/ceo.log 2>&1

# 07:00 — Chief synthesis + WhatsApp briefing delivered to Qassim
0 7 * * * cd $PLUGGEDIN_DIR && $PYTHON orchestrator.py --phase briefing >> $LOG_DIR/briefing.log 2>&1

# 09:00 — Morning social posts (TikTok, Instagram, Pinterest)
0 9 * * * cd $PLUGGEDIN_DIR && $PYTHON -c "from lib.content_machine import execute_todays_posts; execute_todays_posts('SourcedStore')" >> $LOG_DIR/posting.log 2>&1

# 18:00 — Evening social posts
0 18 * * * cd $PLUGGEDIN_DIR && $PYTHON -c "from lib.content_machine import execute_todays_posts; execute_todays_posts('SourcedStore')" >> $LOG_DIR/posting_evening.log 2>&1

# Weekly: Sunday 08:00 — log rotation (keep last 30 days)
0 8 * * 0 find $LOG_DIR -name "*.log" -mtime +30 -delete
EOF

# Install
crontab /tmp/crontab_clean
rm /tmp/crontab_clean

echo ""
echo "✓ Cron jobs installed. Current schedule:"
echo ""
crontab -l | grep -A1 "PluggedIN"
echo ""
echo "To verify: crontab -l"
echo "To remove: crontab -l | grep -v 'orchestrator.py' | grep -v '# PluggedIN' | crontab -"
echo "Logs at:   $LOG_DIR/"
