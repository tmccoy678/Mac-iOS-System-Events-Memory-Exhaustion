# Defensive tools

`lint_system_events.py` is a dependency-free preflight guard for AppleScript, JXA, shell scripts, and text containing proposed automation. It rejects the broad query shapes associated with this incident and surfaces selected invisible or control characters.

```sh
python3 tools/lint_system_events.py path/to/proposed-script
```

Exit status is `0` when no guarded pattern is found, `2` when review is required, and `64` for usage or read errors. Scope: heuristic client-side preflight. Runtime containment and Apple-side remediation remain necessary.
