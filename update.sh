#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

python3 update_calendars.py

if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "Update calendars $(date +%Y-%m-%d)"
    git push
else
    echo "No changes to push"
fi