# Non-deployable agent threat simulation

This directory models the boundaries of a hypothetical prompt-injection, resource-exhaustion, and exfiltration chain without implementing the chain.

```text
synthetic untrusted text
  -> escaped code-point inspection
  -> content-is-data policy decision
  -> one fixed non-secret fixture
  -> blocked resource-exhaustion stub
  -> blocked network-egress stub
```

The implementation has no filesystem collector, application API, `subprocess` call, Apple-event invocation, socket, HTTP client, credential path, destination, persistence, or destructive action. Its three dangerous capability functions raise `CapabilityIntentionallyOmitted` if called.

Run the safe model and tests:

```sh
python3 simulation/nondeployable_chain.py --json
python3 -m unittest tests/test_threat_simulation.py -v
```

The fixed fixture is `DEMO-RECORD-NOT-PRIVATE`. This is a defensive architecture example, not malware, an exploit, or evidence that prompt injection or exfiltration occurred.
