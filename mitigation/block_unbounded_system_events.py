#!/usr/bin/python3
"""Block shell commands that request unbounded System Events traversal."""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from typing import Any, Optional


SYSTEM_EVENTS = re.compile(
    r"(?:application\s+['\"]system\s+events['\"]|"
    r"application\s*\(\s*['\"]system\s+events['\"]|"
    r"system\s+events\.app)",
    re.IGNORECASE,
)
OSASCRIPT = re.compile(r"\bosascript\b", re.IGNORECASE)
UNBOUNDED_RULES = (
    ("entire-contents", re.compile(r"\bentire\s+contents\b", re.IGNORECASE)),
    ("every-ui-element", re.compile(r"\bevery\s+ui\s+elements?\b", re.IGNORECASE)),
    (
        "every-process",
        re.compile(r"\bevery\s+(?:application\s+)?process(?:es)?\b", re.IGNORECASE),
    ),
    (
        "bulk-properties",
        re.compile(r"\b(?:properties|\{[^}\n]+\})\s+of\s+every\b", re.IGNORECASE),
    ),
    ("uielements-call", re.compile(r"(?:\.|\b)uielements\s*\(", re.IGNORECASE)),
    ("ui-elements-call", re.compile(r"(?:\.|\b)ui_elements\s*\(", re.IGNORECASE)),
)


def event_command(event: Any) -> str:
    """Return the shell command from supported Codex hook event shapes."""

    if not isinstance(event, dict):
        return ""
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    for key in ("command", "cmd"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return ""


def guarded_rule(command: str) -> Optional[str]:
    """Return the first guarded rule ID for a dangerous command."""

    normalized = unicodedata.normalize("NFKC", command)
    if OSASCRIPT.search(normalized) is None:
        return None
    if SYSTEM_EVENTS.search(normalized) is None:
        return None
    for rule_id, pattern in UNBOUNDED_RULES:
        if pattern.search(normalized):
            return rule_id
    return None


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    rule_id = guarded_rule(event_command(event))
    if rule_id is None:
        return 0

    print(
        f"Blocked unbounded System Events accessibility traversal ({rule_id}). "
        "Use native Computer Use, a purpose-built API, or a bounded selector "
        "with explicit depth, node-count, and time limits.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
