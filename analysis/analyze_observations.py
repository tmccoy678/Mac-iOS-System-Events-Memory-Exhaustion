#!/usr/bin/env python3
"""Derive reproducible descriptive statistics from sanitized observations."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
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
    endpoint_spacing = Decimal(str(report["endpoint_spacing_seconds"]))
    return {
        "start_mib_assuming_1024": _rounded(start_mib, 2),
        "end_mib_assuming_1024": _rounded(end_mib, 2),
        "endpoint_spacing_seconds": _rounded(endpoint_spacing, 3),
        "growth_multiple": _rounded(end_mib / start_mib, 4),
        "endpoint_derived_mean_mib_per_second": _rounded(
            (end_mib - start_mib) / endpoint_spacing, 4
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
    first_jetsam = observations["first_process"]["jetsam_report"]
    first_jetsam_time = observations["first_process"]["jetsam_report"][
        "inferred_snapshot_time"
    ]
    first_start_gib = _reported_mib(first_report["footprint_start_reported"]) / Decimal(
        1024
    )
    first_endpoint_gib = _reported_mib(first_report["footprint_end_reported"]) / Decimal(
        1024
    )
    final_interval_seconds = _elapsed_seconds(
        first_report["measured_interval_end"], first_jetsam_time
    )
    final_interval_growth_gib = first_jetsam_gib - first_endpoint_gib
    final_interval_mean_gib_per_second = (
        final_interval_growth_gib / final_interval_seconds
    )
    modeled_high_rate_duration_seconds = (
        (first_jetsam_gib - first_start_gib)
        / final_interval_mean_gib_per_second
    )
    modeled_high_rate_onset = datetime.fromisoformat(first_jetsam_time) - timedelta(
        seconds=float(modeled_high_rate_duration_seconds)
    )
    first_peak_bytes = Decimal(str(first_jetsam["bytes_at_16384_per_page"]))
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
            "The 111.742 seconds is spacing between CPU-diagnostic endpoints, "
            "not growth duration. A separate jetsam snapshot supports a tighter "
            "final measured interval. The recorded footprint peak is exact within "
            "the jetsam accounting, but intermediate trajectory and the instantaneous "
            "peak net-growth rate remain unmeasured."
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
        "first_episode_final_measured_interval": {
            "seconds": _rounded(final_interval_seconds, 3),
            "growth_gib": _rounded(final_interval_growth_gib, 4),
            "mean_gib_per_second": _rounded(
                final_interval_mean_gib_per_second, 4
            ),
            "peak_net_growth_lower_bound_gib_per_second": _rounded(
                final_interval_mean_gib_per_second, 4
            ),
            "instantaneous_peak_net_growth_rate_status": "unmeasured",
        },
        "first_episode_recorded_footprint_peak": {
            "pages": int(first_jetsam["rpages"]),
            "page_size_bytes": int(observations["assessed_system"]["page_size_bytes"]),
            "bytes": int(first_peak_bytes),
            "gib": _rounded(first_jetsam_gib, 12),
            "decimal_gb": _rounded(first_peak_bytes / Decimal(1_000_000_000), 9),
            "rpages_equals_lifetime_max": bool(
                first_jetsam["rpages_equals_lifetime_max"]
            ),
            "status": "recorded in the jetsam artifact",
        },
        "first_episode_constant_terminal_rate_model": {
            "status": "modeled, not directly observed",
            "assumption": (
                "the final measured-interval mean of 4.501930534 GiB/s is "
                "extrapolated backward from the jetsam snapshot to the 15.48 MB baseline"
            ),
            "duration_seconds": _rounded(modeled_high_rate_duration_seconds, 6),
            "inferred_onset": modeled_high_rate_onset.isoformat(timespec="microseconds"),
            "interpretation": (
                "a model-supported estimate of the high-rate phase; nonlinear "
                "allocation could produce a different duration"
            ),
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
            f"{first['growth_multiple']:,.4f}x across endpoints spaced "
            f"{first['endpoint_spacing_seconds']:.3f} s apart"
        )
        bounded = metrics["first_episode_final_measured_interval"]
        print(
            "Final measured interval: "
            f"+{bounded['growth_gib']:.4f} GiB in {bounded['seconds']:.3f} s "
            f"= {bounded['mean_gib_per_second']:.4f} GiB/s; "
            "instantaneous peak rate unmeasured"
        )
        model = metrics["first_episode_constant_terminal_rate_model"]
        print(
            "Constant-terminal-rate model: "
            f"{model['duration_seconds']:.6f} s, inferred onset "
            f"{model['inferred_onset']} (modeled, not directly observed)"
        )
        print(metrics["rate_caveat"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
