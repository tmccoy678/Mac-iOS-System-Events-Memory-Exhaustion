from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
HUMAN_FACING_SUFFIXES = {".cff", ".json", ".md", ".mmd", ".R", ".txt"}
DISALLOWED_TOKEN_GROUPS = (
    ("evidence", "does", "not"),
    ("record", "does", "not"),
    ("finding", "does", "not"),
    ("result", "does", "not"),
    ("incident", "does", "not"),
    ("does", "not", "establish"),
    ("does", "not", "show"),
    ("does", "not", "prove"),
    ("is", "not", "evidence", "of"),
    ("no", "evidence", "of"),
    ("not", "a", "measure", "of"),
    ("not", "a", "sampled"),
    ("rather", "than"),
)


class ProseStyleTests(unittest.TestCase):
    def test_human_facing_files_avoid_defensive_contrast_scaffolding(self) -> None:
        findings: list[str] = []
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or path.suffix not in HUMAN_FACING_SUFFIXES:
                continue
            text = " ".join(path.read_text(encoding="utf-8").lower().split())
            for tokens in DISALLOWED_TOKEN_GROUPS:
                phrase = " ".join(tokens)
                if phrase in text:
                    findings.append(f"{path.relative_to(ROOT)}: {phrase}")

        self.assertEqual([], findings)


if __name__ == "__main__":
    unittest.main()
