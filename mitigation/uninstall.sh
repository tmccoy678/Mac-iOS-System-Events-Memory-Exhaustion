#!/bin/sh

set -eu

readonly mitigation_home="${HOME:?HOME is required}"
readonly mitigation_uid="$(id -u)"
readonly mitigation_label="com.openai.codex.system-events-memory-guard"
readonly mitigation_hook_path="${mitigation_home}/.codex/hooks/block_unbounded_system_events.py"
readonly mitigation_guard_path="${mitigation_home}/.codex/guards/system_events_memory_guard.zsh"
readonly mitigation_plist_path="${mitigation_home}/Library/LaunchAgents/${mitigation_label}.plist"

/bin/launchctl bootout "gui/${mitigation_uid}/${mitigation_label}" 2>/dev/null || true
/bin/rm -f \
  "${mitigation_hook_path}" \
  "${mitigation_guard_path}" \
  "${mitigation_plist_path}"

printf '%s\n' \
  "Removed the System Events hook file, guard, and LaunchAgent." \
  "Remove the matching PreToolUse stanza from ${mitigation_home}/.codex/config.toml separately."
