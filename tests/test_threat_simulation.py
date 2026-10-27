from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "simulation" / "nondeployable_chain.py"
SPEC = importlib.util.spec_from_file_location("nondeployable_chain", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
SIMULATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SIMULATION)


class ThreatSimulationTests(unittest.TestCase):
    def test_every_dangerous_stage_is_non_deployable(self) -> None:
        result = SIMULATION.run_simulation()

        self.assertEqual(
            [
                "synthetic-only",
                "blocked-stub",
                "synthetic-only",
                "blocked-stub",
            ],
            [stage["status"] for stage in result["stages"]],
        )

    def test_hidden_content_is_surfaced_and_treated_as_data(self) -> None:
        result = SIMULATION.run_simulation()

        self.assertEqual(["U+200B"], result["untrusted_content"]["hidden_codepoints"])
        self.assertIn("\\u200b", result["untrusted_content"]["escaped_view"])
        self.assertEqual("content-is-data", result["policy_decision"])

    def test_cli_reports_absent_real_world_capabilities(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual("NON_DEPLOYABLE_THREAT_SIMULATION", result["mode"])
        self.assertEqual(
            {
                "real_data_access": False,
                "system_events_execution": False,
                "network_egress": False,
            },
            result["capabilities_present"],
        )

    def test_only_the_fixed_nonsecret_fixture_is_staged(self) -> None:
        result = SIMULATION.run_simulation()

        self.assertEqual(
            {
                "record_count": 1,
                "byte_count": 23,
                "sha256": "3a36a1fc9874a95579abd9cd59471cb8748e3ac7d4700390d43b7303297a35aa",
            },
            result["synthetic_artifact"],
        )

    def test_omitted_capabilities_fail_closed_when_called(self) -> None:
        for capability in (
            SIMULATION.collect_real_data,
            SIMULATION.invoke_system_events_trigger,
            SIMULATION.send_over_network,
        ):
            with self.subTest(capability=capability.__name__):
                with self.assertRaisesRegex(
                    SIMULATION.CapabilityIntentionallyOmitted,
                    "intentionally omitted",
                ):
                    capability()


if __name__ == "__main__":
    unittest.main()
