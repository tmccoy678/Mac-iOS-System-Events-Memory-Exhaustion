from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "tools" / "lint_system_events.py"
SPEC = importlib.util.spec_from_file_location("lint_system_events", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
LINTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LINTER)


class LintSystemEventsTests(unittest.TestCase):
    def test_targeted_query_passes(self) -> None:
        text = '''tell application "System Events"
tell process "Microsoft Outlook" to get name of front window
end tell'''
        self.assertEqual([], LINTER.inspect(text))

    def test_entire_contents_is_blocked(self) -> None:
        text = '''tell application "System Events"
tell process "Microsoft Outlook" to get entire contents of front window
end tell'''
        ids = {finding[1] for finding in LINTER.inspect(text)}
        self.assertIn("entire-contents", ids)

    def test_recursive_jxa_shape_is_blocked(self) -> None:
        text = "const se = Application('System Events'); element.uiElements();"
        ids = {finding[1] for finding in LINTER.inspect(text)}
        self.assertIn("uielements-call", ids)

    def test_zero_width_character_is_visible_to_review(self) -> None:
        findings = LINTER.inspect("safe\u200btext")
        self.assertEqual("hidden-control", findings[0][1])


if __name__ == "__main__":
    unittest.main()
