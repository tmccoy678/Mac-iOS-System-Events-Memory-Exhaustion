#!/usr/bin/env python3
"""Reject hazardous broad System Events queries before execution."""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path


RULES = (
    (
        "entire-contents",
        re.compile(r"\bentire\s+contents\b", re.IGNORECASE),
        "whole-tree `entire contents` enumeration",
    ),
    (
        "every-ui-element",
        re.compile(r"\bevery\s+ui\s+elements?\b", re.IGNORECASE),
        "bulk `every UI element` enumeration",
    ),
    (
        "every-process",
        re.compile(r"\bevery\s+(?:application\s+)?process\b", re.IGNORECASE),
        "bulk process enumeration through System Events",
    ),
    (
        "bulk-properties",
        re.compile(r"\b(?:properties|\{[^}\n]+\})\s+of\s+every\b", re.IGNORECASE),
        "bulk property retrieval",
    ),
    (
        "uielements-call",
        re.compile(r"(?:\.|\b)uiElements\s*\(", re.IGNORECASE),
        "JXA accessibility-child expansion requiring explicit budgets",
    ),
)

INVISIBLE_CODEPOINTS = {
    0x00AD,
    0x034F,
    0x061C,
    0x180E,
    0x200B,
    0x200C,
    0x200D,
    0x200E,
    0x200F,
    0x2060,
    0x2061,
    0x2062,
    0x2063,
    0x2064,
    0x2066,
    0x2067,
    0x2068,
    0x2069,
    0xFEFF,
}


def inspect(text: str) -> list[tuple[int, str, str]]:
    findings: list[tuple[int, str, str]] = []
    system_events_context = bool(
        re.search(r"System\s+Events|Application\s*\(\s*['\"]System Events", text, re.IGNORECASE)
    )

    if system_events_context:
        for rule_id, pattern, message in RULES:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append((line, rule_id, message))

    for index, char in enumerate(text):
        codepoint = ord(char)
        category = unicodedata.category(char)
        unexpected_control = category == "Cc" and char not in "\n\r\t"
        bidi_control = 0x202A <= codepoint <= 0x202E
        if codepoint in INVISIBLE_CODEPOINTS or bidi_control or unexpected_control:
            line = text.count("\n", 0, index) + 1
            name = unicodedata.name(char, "UNNAMED CONTROL")
            findings.append(
                (line, "hidden-control", f"U+{codepoint:04X} {name} requires review")
            )

    return sorted(set(findings))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {Path(argv[0]).name} FILE", file=sys.stderr)
        return 64

    path = Path(argv[1])
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 64

    findings = inspect(text)
    if not findings:
        print(f"PASS: no guarded pattern found in {path}")
        return 0

    print(f"BLOCK: {len(findings)} guarded pattern(s) found in {path}")
    for line, rule_id, message in findings:
        print(f"  line {line}: {rule_id}: {message}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
