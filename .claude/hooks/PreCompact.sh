#!/usr/bin/env bash
# PreCompact.sh — Saves state before context compaction.

echo "[PreCompact] Saving project state..."
echo ""

# Show git status
echo "=== Git Status ==="
git status --short 2>/dev/null || echo "Not a git repo"
echo ""

# Show pending changes summary
PENDING=$(git status --porcelain 2>/dev/null | wc -l)
if [ "$PENDING" -gt 0 ]; then
  echo "=== Changed Files ($PENDING) ==="
  git status --porcelain 2>/dev/null
  echo ""
fi

# Show current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
echo "Branch: $BRANCH"
echo ""

# Show last commit
LAST=$(git log -1 --oneline 2>/dev/null || echo "No commits")
echo "Last commit: $LAST"
echo ""

# Save uncommitted state to backup
BACKUP_FILE=".claude/precompact_backup.txt"
{
  echo "=== PreCompact Backup $(date) ==="
  echo "Branch: $BRANCH"
  echo "Last commit: $LAST"
  echo ""
  git status 2>/dev/null
} > "$BACKUP_FILE" 2>&1

echo "[PreCompact] Done. Backup saved to $BACKUP_FILE"
