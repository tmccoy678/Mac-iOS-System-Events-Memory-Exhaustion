# Non-deployable agent threat simulation

This directory models the trust boundaries of a hypothetical prompt-injection, resource-exhaustion, and exfiltration chain. Every dangerous capability terminates at a fail-closed stub.

```text
synthetic untrusted text
  -> escaped code-point inspection
  -> content-is-data policy decision
  -> one fixed non-secret fixture
  -> blocked resource-exhaustion stub
  -> blocked network-egress stub
```

The module imports only argument parsing, hashing, JSON serialization, and sequence typing. Real data access, process execution, Apple events, network egress, credentials, persistence, and destructive action are represented by three functions that raise `CapabilityIntentionallyOmitted` when called.

Run the safe model and tests:

```sh
python3 simulation/nondeployable_chain.py --json
python3 -m unittest tests/test_threat_simulation.py -v
```

The fixed fixture is `DEMO-RECORD-NOT-PRIVATE`. Purpose: defensive architecture review of capability separation and fail-closed behavior.
