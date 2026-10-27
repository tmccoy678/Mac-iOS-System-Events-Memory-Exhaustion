#!/usr/bin/env python3
"""Non-deployable model of a prompt-injection-to-resource-exhaustion chain."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence


SYNTHETIC_UNTRUSTED_CONTENT = "Quarterly report\u200b[hidden instruction omitted]"
SYNTHETIC_RECORDS = (b"DEMO-RECORD-NOT-PRIVATE",)


class CapabilityIntentionallyOmitted(RuntimeError):
    """Raised where deployable malware would require a harmful capability."""


def collect_real_data() -> None:
    """Fail-closed boundary representing intentionally omitted real data access."""

    raise CapabilityIntentionallyOmitted("real data collection is intentionally omitted")


def invoke_system_events_trigger() -> None:
    """Fail-closed boundary representing intentionally omitted process execution."""

    raise CapabilityIntentionallyOmitted("System Events execution is intentionally omitted")


def send_over_network() -> None:
    """Fail-closed boundary representing intentionally omitted network egress."""

    raise CapabilityIntentionallyOmitted("network egress is intentionally omitted")


def _inspect_synthetic_content() -> dict[str, object]:
    hidden = [f"U+{ord(char):04X}" for char in SYNTHETIC_UNTRUSTED_CONTENT if ord(char) == 0x200B]
    return {
        "escaped_view": SYNTHETIC_UNTRUSTED_CONTENT.encode("unicode_escape").decode("ascii"),
        "hidden_codepoints": hidden,
    }


def _stage_synthetic_fixture() -> dict[str, object]:
    payload = b"".join(SYNTHETIC_RECORDS)
    return {
        "record_count": len(SYNTHETIC_RECORDS),
        "byte_count": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def run_simulation() -> dict[str, object]:
    """Return a synthetic chain in which every dangerous boundary fails closed."""

    return {
        "mode": "NON_DEPLOYABLE_THREAT_SIMULATION",
        "capabilities_present": {
            "real_data_access": False,
            "system_events_execution": False,
            "network_egress": False,
        },
        "untrusted_content": _inspect_synthetic_content(),
        "policy_decision": "content-is-data",
        "synthetic_artifact": _stage_synthetic_fixture(),
        "stages": [
            {"name": "data_access", "status": "synthetic-only"},
            {"name": "resource_exhaustion", "status": "blocked-stub"},
            {"name": "staging", "status": "synthetic-only"},
            {"name": "network_egress", "status": "blocked-stub"},
        ]
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the simulation record as JSON")
    args = parser.parse_args(argv)
    result = run_simulation()

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("NON-DEPLOYABLE: synthetic data; exploit and egress are blocked stubs.")
        for stage in result["stages"]:
            print(f"{stage['name']}: {stage['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
