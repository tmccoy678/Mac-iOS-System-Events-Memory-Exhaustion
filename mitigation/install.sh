#!/bin/sh

set -eu

readonly mitigation_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
readonly mitigation_home="${HOME:?HOME is required}"
readonly mitigation_uid="$(id -u)"
readonly mitigation_label="com.openai.codex.system-events-memory-guard"
readonly mitigation_hook_dir="${mitigation_home}/.codex/hooks"
readonly mitigation_guard_dir="${mitigation_home}/.codex/guards"
readonly mitigation_launchagent_dir="${mitigation_home}/Library/LaunchAgents"
readonly mitigation_hook_path="${mitigation_hook_dir}/block_unbounded_system_events.py"
readonly mitigation_guard_path="${mitigation_guard_dir}/system_events_memory_guard.zsh"
readonly mitigation_plist_path="${mitigation_launchagent_dir}/${mitigation_label}.plist"

mkdir -p \
  "${mitigation_hook_dir}" \
  "${mitigation_guard_dir}" \
  "${mitigation_launchagent_dir}"

/usr/bin/install -m 0755 \
  "${mitigation_dir}/block_unbounded_system_events.py" \
  "${mitigation_hook_path}"
/usr/bin/install -m 0755 \
  "${mitigation_dir}/system_events_memory_guard.zsh" \
  "${mitigation_guard_path}"

/usr/bin/sed \
  "s#__GUARD_PATH__#${mitigation_guard_path}#g" \
  "${mitigation_dir}/${mitigation_label}.plist.template" \
  > "${mitigation_plist_path}"
/bin/chmod 0644 "${mitigation_plist_path}"
/usr/bin/plutil -lint "${mitigation_plist_path}"

/bin/launchctl bootout "gui/${mitigation_uid}/${mitigation_label}" 2>/dev/null || true
/bin/launchctl bootstrap "gui/${mitigation_uid}" "${mitigation_plist_path}"
/bin/launchctl enable "gui/${mitigation_uid}/${mitigation_label}"

printf '%s\n' \
  "Installed ${mitigation_hook_path}" \
  "Installed ${mitigation_guard_path}" \
  "Loaded ${mitigation_plist_path}" \
  "" \
  "Merge this hook into ${mitigation_home}/.codex/config.toml:" \
  "" \
  "[features]" \
  "hooks = true" \
  "" \
  "[[hooks.PreToolUse]]" \
  'matcher = "Bash"' \
  "" \
  "[[hooks.PreToolUse.hooks]]" \
  'type = "command"' \
  "command = \"/usr/bin/python3 ${mitigation_hook_path}\"" \
  "timeout = 5" \
  'statusMessage = "Checking macOS automation safety"'
