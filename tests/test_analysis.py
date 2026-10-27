from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "analysis" / "analyze_observations.py"
OBSERVATIONS_PATH = ROOT / "evidence" / "sanitized" / "observations.json"
SPEC = importlib.util.spec_from_file_location("analyze_observations", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
ANALYSIS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYSIS)


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.observations = json.loads(OBSERVATIONS_PATH.read_text(encoding="utf-8"))
        cls.metrics = ANALYSIS.derive_metrics(cls.observations)

    def test_first_episode_endpoint_statistics(self) -> None:
        first = self.metrics["episodes"]["first"]

        self.assertEqual(192266.24, first["end_mib_assuming_1024"])
        self.assertEqual(12420.2997, first["growth_multiple"])
        self.assertEqual(1720.4879, first["endpoint_derived_mean_mib_per_second"])
        self.assertEqual(7.8233, first["endpoint_to_physical_ram_multiple"])

    def test_second_episode_and_jetsam_statistics(self) -> None:
        second = self.metrics["episodes"]["second"]

        self.assertEqual(38.4006, second["growth_multiple"])
        self.assertEqual(45.23, second["endpoint_derived_mean_mib_per_second"])
        self.assertEqual(9.2728, self.metrics["jetsam"]["first_to_physical_ram_multiple"])
        self.assertEqual(10.5795, self.metrics["jetsam"]["second_lifetime_max_to_physical_ram_multiple"])

    def test_temporal_association_and_scope_are_explicit(self) -> None:
        self.assertEqual(
            {"first": 2.883, "second": 2.828, "mean": 2.8555},
            self.metrics["trigger_to_measurement_seconds"],
        )
        self.assertEqual(2, self.metrics["sample_size_episodes"])
        self.assertEqual("descriptive-only", self.metrics["statistical_scope"])
        self.assertIn("not sampled", self.metrics["rate_caveat"])


if __name__ == "__main__":
    unittest.main()
