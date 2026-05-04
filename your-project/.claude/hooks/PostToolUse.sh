#!/bin/bash
# Auto-commit after edits
# This script runs after any tool usage that modifies files.
# It stages all changes and creates a commit.

git add -A
if git diff-index --quiet HEAD --; then
  echo "No changes to commit."
else
  git commit -m "Auto-commit: tool usage changes"
fi
