#!/bin/zsh

set -u

readonly system_events_limit_kib=1048576

select_runaway_system_events() {
  /usr/bin/awk -v limit="${system_events_limit_kib}" \
    '$2 >= limit && $0 ~ /^[[:space:]]*[0-9]+[[:space:]]+[0-9]+[[:space:]]+\/System\/Library\/CoreServices\/System Events\.app\/Contents\/MacOS\/System Events( |$)/ { print $1 ":" $2 }'
}

select_unbounded_requesters() {
  /usr/bin/awk '
    {
      line = tolower($0)
      dangerous = \
        line ~ /entire[[:space:]]+contents/ || \
        line ~ /every[[:space:]]+ui[[:space:]]+elements?/ || \
        line ~ /every[[:space:]]+application[[:space:]]+process/ || \
        line ~ /\.uielements[[:space:]]*\(/ || \
        line ~ /\.ui_elements[[:space:]]*\(/
      if (line ~ /osascript/ && line ~ /system[[:space:]]+events/ && dangerous) {
        print $1
      }
    }'
}

if [[ "${1:-}" == "--match-snapshot" ]]; then
  if [[ "$#" -ne 2 || ! -r "$2" ]]; then
    print -u2 "usage: $0 --match-snapshot PS_SNAPSHOT"
    exit 64
  fi
  select_runaway_system_events < "$2"
  exit 0
fi

readonly process_snapshot="$(/bin/ps -axo pid=,rss=,command=)"
readonly runaway_system_events="$(print -r -- "${process_snapshot}" | select_runaway_system_events)"

[[ -z "${runaway_system_events}" ]] && exit 0

# Stop only requesters whose still-visible command line contains a guarded
# traversal shape. The responder kill below remains sufficient when the caller
# has already exited or invoked an opaque script file.
readonly unbounded_requesters="$(print -r -- "${process_snapshot}" | select_unbounded_requesters)"
if [[ -n "${unbounded_requesters}" ]]; then
  while IFS= read -r requester_pid; do
    [[ -z "${requester_pid}" ]] && continue
    /usr/bin/logger -t codex-system-events-guard \
      "Stopping unbounded osascript requester pid=${requester_pid}"
    /bin/kill -TERM "${requester_pid}" 2>/dev/null || true
  done <<< "${unbounded_requesters}"
fi

while IFS=: read -r system_events_pid system_events_rss_kib; do
  [[ -z "${system_events_pid}" ]] && continue
  /usr/bin/logger -t codex-system-events-guard \
    "Stopping runaway System Events pid=${system_events_pid} rss_kib=${system_events_rss_kib}"
  /bin/kill -TERM "${system_events_pid}" 2>/dev/null || true
done <<< "${runaway_system_events}"

/bin/sleep 1

while IFS=: read -r system_events_pid _; do
  [[ -z "${system_events_pid}" ]] && continue
  /bin/kill -0 "${system_events_pid}" 2>/dev/null || continue
  /bin/kill -KILL "${system_events_pid}" 2>/dev/null || true
done <<< "${runaway_system_events}"
