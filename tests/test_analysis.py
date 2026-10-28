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
        self.assertEqual(111.742, first["endpoint_spacing_seconds"])

    def test_first_episode_final_measured_interval(self) -> None:
        bounded = self.metrics["first_episode_final_measured_interval"]

        self.assertEqual(7.727, bounded["seconds"])
        self.assertEqual(34.7864, bounded["growth_gib"])
        self.assertEqual(4.5019, bounded["mean_gib_per_second"])
        self.assertEqual(
            4.5019, bounded["peak_net_growth_lower_bound_gib_per_second"]
        )
        self.assertEqual(
            "unmeasured", bounded["instantaneous_peak_net_growth_rate_status"]
        )

    def test_recorded_peak_and_modeled_duration_are_distinguished(self) -> None:
        peak = self.metrics["first_episode_recorded_footprint_peak"]
        model = self.metrics["first_episode_constant_terminal_rate_model"]

        self.assertEqual(14584802, peak["pages"])
        self.assertEqual(238957395968, peak["bytes"])
        self.assertEqual(222.546417236328, peak["gib"])
        self.assertEqual(238.957395968, peak["decimal_gb"])
        self.assertTrue(peak["rpages_equals_lifetime_max"])
        self.assertEqual(49.430194, model["duration_seconds"])
        self.assertEqual(
            "2026-10-27T11:13:47.787806-05:00", model["inferred_onset"]
        )
        self.assertEqual("modeled, not directly observed", model["status"])

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
        self.assertIn("unmeasured", self.metrics["rate_caveat"])
        self.assertIn("not growth duration", self.metrics["rate_caveat"])
        self.assertIn("instantaneous", self.metrics["rate_caveat"])


if __name__ == "__main__":
    unittest.main()
