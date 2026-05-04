#!/bin/bash
# Load project context on startup
# This script runs when a new OpenClaw session starts.
# It can pre-load files, set env vars, or run init commands.

# Example: load .env if exists (ignore errors)
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
