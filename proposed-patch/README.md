# Proposed patch package

This directory contains the engineering recommendation for a cooperative `System Events` recovery path that preserves long-running automation and avoids abrupt process termination.

## Recommendation

Add a per-Apple-event pause–drain–resume state machine inside `System Events`, then change accessibility clients to traverse complex UI trees in checkpointed batches. A request that enters dangerous memory growth stops discovering new objects, releases retained descriptors incrementally, yields between cleanup slices, and resumes from its checkpoint after memory stabilizes.

## Package map

- [`cooperative-pause-drain-resume.md`](cooperative-pause-drain-resume.md) — complete design recommendation, pseudocode, validation plan, rollout, and acceptance criteria.
- [`diagrams/pause-drain-resume.mmd`](diagrams/pause-drain-resume.mmd) — Mermaid state-machine source.

## Evidence basis

The proposal derives from the two fresh-process incidents described in the [technical report](../report/system-events-memory-exhaustion.md), the [sanitized timeline](../docs/forensic-timeline.md), the [machine-readable observations](../evidence/sanitized/observations.json), and the [defensive agent threat model](../docs/agent-threat-model.md).

Artifact status: implementation recommendation for Apple and automation-client maintainers. Apple owns the private source integration and final constants.
