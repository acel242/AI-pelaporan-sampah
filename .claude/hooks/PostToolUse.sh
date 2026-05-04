#!/usr/bin/env bash
# PostToolUse.sh — Auto-commits changes after file edits
# Triggers after any write, edit, or exec tool modifies files.
# Uses NM-XXX ticket format from branch name (e.g., NM-123-description).

set -e

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

# Extract ticket number from branch name (e.g., NM-123-feature-xyz → NM-123)
if [[ "$BRANCH" =~ ^NM-[0-9]+ ]]; then
  TICKET="${BASH_REMATCH[0]}"
else
  TICKET="NM-000"
fi

# Find staged changes
STAGED=$(git diff --cached --name-only 2>/dev/null | wc -l)
UNSTAGED=$(git status --porcelain 2>/dev/null | grep -v "^??" | wc -l)

# Only commit if there are meaningful changes
if [ "$STAGED" -gt 0 ] || [ "$UNSTAGED" -gt 0 ]; then
  git add -A

  # Build commit message
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
  COMMIT_MSG="${TICKET} — auto-save at ${TIMESTAMP}"

  git commit -m "$COMMIT_MSG" --no-verify 2>/dev/null && echo "[PostToolUse] Committed: $COMMIT_MSG"
fi
