#!/usr/bin/env python3
"""Derive reproducible descriptive statistics from sanitized observations."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Sequence


ROOT = Path(__file__).parents[1]
DEFAULT_INPUT = ROOT / "evidence" / "sanitized" / "observations.json"


def _rounded(value: Decimal, places: int) -> float:
    quantum = Decimal(1).scaleb(-places)
    return float(value.quantize(quantum, rounding=ROUND_HALF_UP))


def _reported_mib(value: str) -> Decimal:
    amount_text, unit = value.split()
    amount = Decimal(amount_text.replace(",", ""))
    if unit == "MB":
        return amount
    if unit == "GB":
        return amount * Decimal(1024)
    raise ValueError(f"unsupported reported unit: {unit}")


def _elapsed_seconds(start: str, end: str) -> Decimal:
    delta = datetime.fromisoformat(end) - datetime.fromisoformat(start)
    return Decimal(str(delta.total_seconds()))


def _episode_metrics(
    report: Dict[str, Any], physical_ram_mib: Decimal
) -> Dict[str, float]:
    start_mib = _reported_mib(report["footprint_start_reported"])
    end_mib = _reported_mib(report["footprint_end_reported"])
    duration = Decimal(str(report["measured_interval_seconds"]))
    return {
        "start_mib_assuming_1024": _rounded(start_mib, 2),
        "end_mib_assuming_1024": _rounded(end_mib, 2),
        "duration_seconds": _rounded(duration, 3),
        "growth_multiple": _rounded(end_mib / start_mib, 4),
        "endpoint_derived_mean_mib_per_second": _rounded(
            (end_mib - start_mib) / duration, 4
        ),
        "endpoint_to_physical_ram_multiple": _rounded(
            end_mib / physical_ram_mib, 4
        ),
        "cpu_average_percent": float(report["cpu_average_percent"]),
    }


def derive_metrics(observations: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate descriptive metrics with explicit endpoint-only scope."""

    physical_ram_mib = Decimal(
        observations["assessed_system"]["physical_memory_bytes"]
    ) / Decimal(1024 * 1024)
    first_report = observations["first_process"]["cpu_resource_report"]
    second_report = observations["second_process"]["cpu_resource_report"]
    trigger_context = observations["recorded_trigger_context"]

    first_lag = _elapsed_seconds(
        trigger_context["first_broad_query_executed_at"],
        first_report["measured_interval_start"],
    )
    second_lag = _elapsed_seconds(
        trigger_context["second_broad_query_executed_at"],
        second_report["measured_interval_start"],
    )

    first_jetsam_gib = Decimal(
        str(observations["first_process"]["jetsam_report"]["gib_at_16384_per_page"])
    )
    second_lifetime_max_gib = Decimal(
        str(
            observations["second_process"]["jetsam_report"][
                "lifetime_max_gib_at_16384_per_page"
            ]
        )
    )
    physical_ram_gib = Decimal(
        str(observations["assessed_system"]["physical_memory_gib"])
    )

    return {
        "sample_size_episodes": 2,
        "statistical_scope": "descriptive-only",
        "rate_caveat": (
            "Rates divide the difference between two endpoints by elapsed time; "
            "intermediate trajectory was unmeasured."
        ),
        "episodes": {
            "first": _episode_metrics(first_report, physical_ram_mib),
            "second": _episode_metrics(second_report, physical_ram_mib),
        },
        "trigger_to_measurement_seconds": {
            "first": _rounded(first_lag, 3),
            "second": _rounded(second_lag, 3),
            "mean": _rounded((first_lag + second_lag) / Decimal(2), 4),
        },
        "jetsam": {
            "first_to_physical_ram_multiple": _rounded(
                first_jetsam_gib / physical_ram_gib, 4
            ),
            "second_lifetime_max_to_physical_ram_multiple": _rounded(
                second_lifetime_max_gib / physical_ram_gib, 4
            ),
        },
        "mean_cpu_average_percent": _rounded(
            (
                Decimal(str(first_report["cpu_average_percent"]))
                + Decimal(str(second_report["cpu_average_percent"]))
            )
            / Decimal(2),
            1,
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    observations = json.loads(args.input.read_text(encoding="utf-8"))
    metrics = derive_metrics(observations)
    if args.json:
        print(json.dumps(metrics, indent=2, sort_keys=True))
    else:
        first = metrics["episodes"]["first"]
        print(
            "First episode: "
            f"{first['growth_multiple']:,.4f}x in {first['duration_seconds']:.3f} s"
        )
        print(metrics["rate_caveat"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
