# Deployed client-side containment

This package contains the defense-in-depth repair deployed after the 2026-10-27
recurrence. It is a client-side containment layer for affected Macs. Apple's
closed-source `System Events` implementation still requires an Apple-side fix.

## Layers

1. `block_unbounded_system_events.py` is a Codex `PreToolUse` hook. It rejects
   shell commands that invoke `osascript`, target `System Events`, and contain a
   known whole-tree or bulk-enumeration shape.
2. `system_events_memory_guard.zsh` is an independent watchdog. It checks the
   full executable path every five seconds and stops a `System Events` process
   whose resident set reaches 1 GiB. It also stops a live `osascript` requester
   when that requester's command line still contains the same dangerous shape.
3. The LaunchAgent template keeps the watchdog outside the requesting agent's
   process tree, so it remains available when the requester stalls.
4. `automation-safety-policy.md` supplies the matching instruction text for
   automation-capable agents.

The hook prevents the recorded command shape. The watchdog bounds the impact
when a request bypasses static inspection, arrives through another client, or
continues inside `System Events` after its caller exits.

## Install the watchdog and hook file

Run from the repository root:

```sh
./mitigation/install.sh
```

The installer is user-scoped and requires no `sudo`. It installs:

- `~/.codex/hooks/block_unbounded_system_events.py`
- `~/.codex/guards/system_events_memory_guard.zsh`
- `~/Library/LaunchAgents/com.openai.codex.system-events-memory-guard.plist`

It validates and bootstraps the LaunchAgent, then prints the exact Codex hook
configuration for the current home directory. Merge that stanza into
`~/.codex/config.toml`; keep any existing `[features]` table and merge
`hooks = true` into it instead of creating a duplicate TOML table.

The installed hook stanza has this shape:

```toml
[features]
hooks = true

[[hooks.PreToolUse]]
matcher = "Bash"

[[hooks.PreToolUse.hooks]]
type = "command"
command = "/usr/bin/python3 /Users/REPLACE_ME/.codex/hooks/block_unbounded_system_events.py"
timeout = 5
statusMessage = "Checking macOS automation safety"
```

Restart the Codex process after editing its configuration. A long-running
process retains the configuration and plugin environment with which it started.

## Validate

Check the installed LaunchAgent:

```sh
launchctl print "gui/$(id -u)/com.openai.codex.system-events-memory-guard"
```

Expected steady-state fields include `state = spawn scheduled` and
`last exit code = 0`. The job normally exits immediately and is relaunched by
`StartInterval`; it is not expected to remain resident.

Test the hook without starting `System Events`:

```sh
printf '%s\n' '{"tool_input":{"command":"osascript -e '\''tell application \"System Events\" to get name of front window'\''"}}' \
  | /usr/bin/python3 mitigation/block_unbounded_system_events.py

printf '%s\n' '{"tool_input":{"command":"osascript -e '\''tell application \"System Events\" to get entire contents of front window'\''"}}' \
  | /usr/bin/python3 mitigation/block_unbounded_system_events.py
```

The bounded example exits `0`. The whole-tree example exits `2` and prints a
blocking message. These tests inspect text only; they never invoke `osascript`.

Run the repository regression suite:

```sh
python3 -m unittest discover -s tests -v
```

## Operating limits

- The 1 GiB resident-set boundary is intentionally conservative for the
  recorded failure, which grew from megabytes to hundreds of gigabytes.
- Process matching uses the complete executable path. A truncated process name
  such as `System Events` is insufficient.
- The watchdog terminates only over-limit `System Events` instances and live
  requesters whose command lines retain a guarded pattern. It never uses a
  blanket `pkill osascript` operation.
- A compiled script file can hide its source from command-line inspection. Run
  `tools/lint_system_events.py` on source files before execution.
- Native Computer Use and narrowly targeted AppleScript/JXA remain available.
- Full filesystem access, macOS Accessibility permission, and Computer Use
  broker authentication are separate controls. Broad permissions cannot make
  an unbounded accessibility traversal safe.

## Companion recovery settings

The two repaired Macs also use short Computer Use startup/tool timeouts so a
missing authenticated broker fails quickly, and Codex terminal alternate-screen
mode is disabled to preserve terminal scrollback and reduce input-focus churn.
Those settings are operational preferences, not prerequisites for this memory
containment package.

The MacBook's built-in keyboard was excluded from Karabiner processing after an
independent intermittent-input investigation. Existing auxiliary-device
mappings were preserved. That keyboard change addresses the spacebar symptom
and is intentionally outside this installer.

## Remove

```sh
./mitigation/uninstall.sh
```

The uninstaller removes only the three paths listed above and unloads the named
LaunchAgent. Remove the hook stanza from Codex configuration separately so an
installer never rewrites an unrelated user configuration file.
