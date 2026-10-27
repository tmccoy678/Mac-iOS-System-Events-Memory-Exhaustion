# Proposed Patch: Cooperative Pause, Drain, and Resume for System Events

## Decision

I recommend a cooperative per-request state machine inside `System Events`, paired with checkpointed client traversal. When a request shows dangerous memory growth, the responder stops expanding the accessibility graph, drains retained work in bounded slices, preserves a resumable cursor, and continues after memory returns to a stable low-water state.

This design preserves the agent, Outlook, `System Events`, and completed traversal work. It supports large cumulative workloads because memory use is bounded per batch instead of bounded across the entire job.

## Evidence Basis

Two fresh `System Events` processes entered the same recursive scripting-property stack after broad Outlook accessibility enumeration. The first diagnostic measured growth from 15.48 MB to 187.76 GB in 111.742 seconds. The second fresh process reached the same stack family and later recorded a 253.9077 GiB jetsam lifetime maximum. In both episodes, the immediate caller could return while the responder continued expensive work.

The evidence establishes three structural conditions:

1. one Apple event can retain work far beyond the caller's useful lifetime;
2. whole-tree enumeration creates an allocation domain with no effective backpressure; and
3. fresh-process recurrence localizes the failure to request handling and target traversal.

Apple's private implementation determines the exact integration points. The preserved stack symbols identify `NSScriptClassDescription` key resolution, object-specifier evaluation, and descriptor construction as the critical path.

## Desired Invariants

- Every inbound Apple event owns a traversal context with a unique request identifier.
- Each context records visited object identities, pending work, retained descriptors, phase, and checkpoint position.
- A pause signal stops discovery of new accessibility objects within one cleanup slice.
- Draining releases retained objects and descriptors incrementally while keeping the service run loop responsive.
- Memory footprint trends downward throughout the draining phase.
- Resume continues from the exact checkpoint with each object processed once.
- Caller exit moves the request into draining and cleanup.
- New requests receive a bounded busy response while the affected context drains.
- Large jobs can continue indefinitely through completed, released, checkpointed batches.
- The emergency path freezes requester and responder state for operator-directed recovery.

## State Machine

The [Mermaid source](diagrams/pause-drain-resume.mmd) defines the proposed transitions:

```text
RUNNING
  -> PAUSE_REQUESTED
  -> DRAINING
  -> PAUSED
  -> RESUMING
  -> RUNNING
  -> COMPLETED

Any active phase
  -> EMERGENCY_FROZEN
  -> operator-directed resume or clean restart
```

### Running

The responder expands a bounded batch from an iterative work queue. Every object receives a stable identity, and the visited set prevents cyclic expansion. The context checkpoints after each completed batch.

### Pause requested

A memory-pressure signal, rapid footprint-growth signal, configured high-water boundary, caller cancellation, or caller exit sets `pauseRequested`. The traversal loop stops adding descendants and moves immediately to draining.

### Draining

The responder releases descriptors, temporary object specifiers, cached property results, and traversal objects in bounded slices. A starting cleanup slice is the first of:

- 1,000 retained objects released; or
- 50 milliseconds of cleanup work.

Each slice drains its autorelease pool and yields to the service run loop. Batch constants remain configurable and should be tuned against Apple regression workloads.

### Paused

The context retains only the compact checkpoint, visited-identity summary, pending queue, and request metadata. The service remains responsive and reports progress to the caller.

### Resuming

Resume begins after footprint remains below the configured low-water boundary for a stability interval. The responder restores the queue and cursor, validates object identities that may have changed, and continues with a fresh batch.

### Emergency frozen

The emergency ceiling freezes both requester and responder, preserves their current state, and asks the operator to resume cooperative draining or perform a clean restart. This state arrests allocation immediately. Memory release resumes when cleanup code runs again.

## Proposed Request Context

The following pseudocode describes the required ownership and lifecycle. Names are illustrative because Apple owns the source-level types and functions.

```swift
enum TraversalPhase {
    case running
    case pauseRequested(PauseReason)
    case draining
    case paused(Checkpoint)
    case resuming(Checkpoint)
    case completed
    case emergencyFrozen
}

struct TraversalContext {
    let requestID: UUID
    let senderIdentity: SenderIdentity
    var phase: TraversalPhase
    var workQueue: Deque<ObjectSpecifier>
    var visited: IdentitySet
    var retainedDescriptors: DescriptorArena
    var checkpoint: Checkpoint
    var footprintSamples: RollingWindow
    var objectsCompleted: UInt64
}
```

The request loop checks its phase before discovery and after each object:

```swift
func advance(_ context: inout TraversalContext) {
    switch context.phase {
    case .running:
        processOneObject(&context)
        sampleFootprint(&context)
        if shouldPause(context) {
            context.phase = .pauseRequested(currentReason(context))
        }

    case .pauseRequested(_):
        context.checkpoint = makeCheckpoint(context)
        context.phase = .draining

    case .draining:
        drainOneSlice(&context)
        drainAutoreleasePool()
        yieldToRunLoop()
        if reachedCompactPausedState(context) {
            context.phase = .paused(context.checkpoint)
        }

    case .resuming(let checkpoint):
        restore(checkpoint, into: &context)
        context.phase = .running

    case .paused(_), .completed, .emergencyFrozen:
        return
    }
}
```

## Resource Signals

The patch should combine several signals instead of relying on a small fixed memory allowance:

- rolling footprint growth;
- system memory-pressure state;
- administrator-configured high-water and emergency boundaries;
- retained-descriptor count;
- pending-work growth;
- caller cancellation or disappearance; and
- repeated traversal of the same object identity.

High-water values remain configurable. This design allows 32, 48, 80, or more GiB of deliberate work when the system remains stable and each completed batch drains correctly.

Low-water hysteresis prevents rapid pause/resume oscillation. A typical policy resumes after footprint stays below a percentage of the triggering high-water mark for several consecutive samples.

## Client Compatibility Layer

Automation clients can adopt the same behavior before Apple ships the responder patch:

1. replace `entire contents` with iterative breadth-first traversal;
2. request one bounded group of child objects and properties at a time;
3. persist a checkpoint after every completed group;
4. release the prior group before issuing the next Apple event;
5. pause new submissions when footprint or memory pressure rises;
6. resume from the checkpoint after the responder stabilizes; and
7. preserve a visited-object identity set across batches.

The compatibility layer gives long-running jobs effectively unlimited cumulative work while keeping live request state bounded. A single pathological Apple event remains eligible for emergency freeze until Apple adds cooperative server-side cancellation.

## Observability

Each request should expose privacy-preserving metrics:

- request identifier and caller identity;
- phase and pause reason;
- completed, queued, visited, and retained-object counts;
- current and peak process footprint;
- checkpoint generation;
- drain-slice count and duration;
- time spent paused and draining; and
- resume, completion, or operator-recovery outcome.

Message content and property values stay outside default telemetry. Command and script hashes provide provenance without copying private data.

## Validation Plan

| Test | Expected result |
| --- | --- |
| Deep acyclic hierarchy | Completes through multiple released batches. |
| Wide hierarchy with shared children | Each identity is processed once. |
| Cyclic hierarchy | Visited-object tracking terminates the cycle. |
| Rapid footprint growth | Request enters pause and draining within one cleanup slice. |
| Memory-pressure transition | New discovery stops and footprint trends downward. |
| Caller exits mid-request | Responder drains the request and remains responsive. |
| Repeated pause/resume | Cursor resumes exactly once with complete output. |
| Large legitimate workload | Continues across checkpoints without forced termination. |
| Emergency ceiling | Requester and responder freeze with state preserved. |
| Operator-directed resume | Cooperative drain completes and checkpoint remains available. |

Validation should record footprint, CPU, drain progress, service responsiveness, output completeness, duplicated identities, skipped identities, and recovery latency.

## Acceptance Criteria

- The original broad-query shape transitions into cooperative draining before system-wide jetsam pressure.
- `System Events` remains responsive throughout draining.
- Footprint declines monotonically across completed drain slices, allowing ordinary allocator variance.
- Outlook and the requesting agent remain alive.
- Completed traversal work survives pause and resume.
- Repeated identities and cycles terminate deterministically.
- Large workloads complete through bounded batches.
- Emergency freeze preserves process and checkpoint state for operator recovery.
- Regression tests cover fresh and long-lived `System Events` processes.

## Rollout

1. Add request contexts, iterative traversal, visited identities, and descriptor ownership in an Apple-internal test build.
2. Introduce pause and drain transitions behind a feature flag.
3. Validate with synthetic cyclic, deep, wide, and memory-heavy accessibility graphs.
4. Compare current and candidate builds using the same bounded test corpus.
5. Enable telemetry-only signaling to tune high-water, low-water, and drain-slice constants.
6. Enable cooperative pausing and draining for broad accessibility requests.
7. Ship the client-side batching guidance alongside the responder update.

Rollback disables the feature flag and restores the previous request path while preserving diagnostic telemetry. The client-side batching layer can remain active throughout rollout.

## Recommended Apple Submission Framing

The proposal gives Apple a concrete behavioral contract: a complex or cyclic accessibility graph should pause, drain, and resume under resource pressure while preserving the caller, responder, target application, and completed work. The supplied diagnostics and matching fresh-process stacks provide the regression basis; Apple can bind the design to the exact internal ownership points.
