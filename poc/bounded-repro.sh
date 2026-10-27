#!/bin/sh
set -eu

repo_dir=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
trigger="$repo_dir/poc/trigger.applescript.disabled.txt"
linter="$repo_dir/tools/lint_system_events.py"

echo "DRY REVIEW ONLY: osascript will not be invoked."
echo "Checking that the defensive linter blocks the disabled trigger..."

if python3 "$linter" "$trigger"; then
    echo "ERROR: the hazardous trigger was not blocked." >&2
    exit 1
fi

echo "PASS: hazardous System Events patterns were detected; no trigger ran."
