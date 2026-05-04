#!/usr/bin/env bash
# SessionStart.sh — Loads project context on session start.

PROJECT_NAME="AI-pelaporan-sampah"
DB_FILE="pelaporan.db"
DB_PATH="./data/${DB_FILE}"
API_PORT=8000

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  🗑️  $PROJECT_NAME — Session Started      ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Check database exists
if [ -f "$DB_PATH" ]; then
  DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
  echo "  📊 Database: $DB_FILE ($DB_SIZE)"
else
  echo "  ⚠️  Database not found at $DB_PATH"
fi

# Check backend
if [ -f "backend/main.py" ]; then
  echo "  ✅ Backend:  http://localhost:$API_PORT"
fi

# Check bot
if [ -f "bot/main.py" ]; then
  echo "  ✅ Bot:      polling mode (or webhook if PROD=1)"
fi

# Check reports directory
if [ -d "data/reports" ]; then
  REPORT_COUNT=$(find data/reports -type f 2>/dev/null | wc -l)
  echo "  📁 Reports:  $REPORT_COUNT image(s) stored"
fi

# Pending git changes
PENDING=$(git status --porcelain 2>/dev/null | wc -l)
if [ "$PENDING" -gt 0 ]; then
  echo ""
  echo "  📝 Pending changes: $PENDING file(s)"
  git status --short 2>/dev/null | head -5
fi

# Current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
echo ""
echo "  🌿 Branch: $BRANCH"
echo ""
echo "  Commands:"
echo "    bash deploy.sh       — deploy to Vercel"
echo "    bash start-tunnel.sh — start cloudflare tunnel for webhooks"
echo "    ruff check .         — lint Python"
echo ""
