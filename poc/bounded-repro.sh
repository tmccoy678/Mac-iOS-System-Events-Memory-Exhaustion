#!/bin/sh
set -eu

repo_dir=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
trigger="$repo_dir/poc/trigger.applescript.disabled.txt"
linter="$repo_dir/tools/lint_system_events.py"

echo "DRY REVIEW ONLY: osascript invocation is disabled."
echo "Checking that the defensive linter blocks the disabled trigger..."

if python3 "$linter" "$trigger"; then
    echo "ERROR: the linter failed to block the hazardous trigger." >&2
    exit 1
fi

echo "PASS: hazardous System Events patterns were detected; trigger execution stayed disabled."
