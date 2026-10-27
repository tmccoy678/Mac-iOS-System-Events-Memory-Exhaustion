from __future__ import annotations

import importlib.util
import plistlib
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
HOOK_PATH = ROOT / "mitigation" / "block_unbounded_system_events.py"
GUARD_PATH = ROOT / "mitigation" / "system_events_memory_guard.zsh"
PLIST_TEMPLATE = (
    ROOT
    / "mitigation"
    / "com.openai.codex.system-events-memory-guard.plist.template"
)

SPEC = importlib.util.spec_from_file_location("block_unbounded_system_events", HOOK_PATH)
assert SPEC is not None and SPEC.loader is not None
HOOK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOOK)


class RuntimeHookTests(unittest.TestCase):
    def test_bounded_system_events_query_passes(self) -> None:
        command = '''osascript -e 'tell application "System Events" to get name of front window' '''
        self.assertIsNone(HOOK.guarded_rule(command))

    def test_entire_contents_is_blocked(self) -> None:
        command = '''osascript -e 'tell application "System Events" to get entire contents of front window' '''
        self.assertEqual("entire-contents", HOOK.guarded_rule(command))

    def test_recursive_jxa_is_blocked(self) -> None:
        command = "osascript -l JavaScript -e \"Application('System Events').uiElements()\""
        self.assertEqual("uielements-call", HOOK.guarded_rule(command))

    def test_unrelated_text_is_outside_hook_scope(self) -> None:
        command = "printf 'System Events entire contents'"
        self.assertIsNone(HOOK.guarded_rule(command))

    def test_cmd_event_shape_is_supported(self) -> None:
        event = {"tool_input": {"cmd": "printf safe"}}
        self.assertEqual("printf safe", HOOK.event_command(event))


class RuntimeGuardTests(unittest.TestCase):
    def test_snapshot_match_uses_full_path_and_threshold(self) -> None:
        snapshot = "\n".join(
            (
                "101 1048576 /System/Library/CoreServices/System Events.app/Contents/MacOS/System Events",
                "102 1048575 /System/Library/CoreServices/System Events.app/Contents/MacOS/System Events",
                "103 2097152 System Events",
                "104 2097152 /tmp/System Events.app/Contents/MacOS/System Events helper",
            )
        )
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
            handle.write(snapshot)
            handle.flush()
            completed = subprocess.run(
                ["/bin/zsh", str(GUARD_PATH), "--match-snapshot", handle.name],
                check=True,
                capture_output=True,
                text=True,
            )
        self.assertEqual("101:1048576", completed.stdout.strip())

    def test_launchagent_template_is_valid_after_substitution(self) -> None:
        rendered = PLIST_TEMPLATE.read_text(encoding="utf-8").replace(
            "__GUARD_PATH__", "/Users/example/.codex/guards/system_events_memory_guard.zsh"
        )
        parsed = plistlib.loads(rendered.encode("utf-8"))
        self.assertEqual(
            "com.openai.codex.system-events-memory-guard", parsed["Label"]
        )
        self.assertEqual(5, parsed["StartInterval"])


if __name__ == "__main__":
    unittest.main()
