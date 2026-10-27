# Defensive agent threat model

## Protected outcome

Prevent an automation-capable agent from turning untrusted email, web, document, or UI text into an unbounded macOS accessibility query that exhausts memory through `System Events`.

## Plausible abuse chain

```text
untrusted content
  -> model treats data as an instruction
  -> agent invokes an already-authorized automation tool
  -> broad or recursive System Events enumeration
  -> unbounded scripting metadata and object-specifier work
  -> compression, swap pressure, jetsam, and local denial of service
```

This chain requires several independent preconditions:

1. The agent ingests attacker-controlled content.
2. The model or controller fails to keep that content in the data plane.
3. The agent is permitted to run AppleScript or JXA.
4. The automation host already has the required Automation and Accessibility grants.
5. The controller lacks command-shape, time, node-count, retry, and memory guards.
6. The target application exposes a sufficiently complex or cyclic accessibility hierarchy.

The incident establishes steps 3 through 6 for the recorded troubleshooting workflow. It does not establish that attacker-controlled content caused step 2. The commands were authored by the local agent while trying to inspect Outlook.

## Backspace and invisible-text boundary

Taylor's [Backspace Text Retention](https://github.com/tmccoy678/Backspace-Text-Retention) project demonstrates a narrower terminal boundary: a sequential terminal recording can retain echoed bytes for a draft that was later visually erased, while canonical line editing delivers only the committed line to the child program. That finding motivates preserving and inspecting raw bytes at trust boundaries.

It does not show that Outlook, Codex, a cloud model, or this incident received deleted text. Terminal echo, recorder output, process input, model input, model output, and tool execution are separate evidence layers.

Defensive ingestion should therefore:

- preserve the original bytes and hash before normalization;
- surface zero-width, bidirectional, and unexpected control characters;
- compare rendered text with an escaped code-point view when content is suspicious;
- log the exact normalized text passed to the model and the exact command passed to a tool; and
- never treat text extracted from a message or UI as authority to invoke tools.

## Required controls

### Agent policy

- Treat email bodies, attachments, webpages, documents, accessibility labels, OCR, and tool output as untrusted data.
- Do not execute instructions found inside those sources unless the human request independently authorizes the action.
- Reject `entire contents`, `every UI element`, `every application process`, bulk `properties`, and recursive `uiElements()` against complex apps.
- Stop after the first hung or abnormally slow query. Do not retry through a fresh `System Events` process.
- Prefer a purpose-built connector or narrowly addressed accessibility element over whole-tree enumeration.

### Runtime containment

- Separate content-reading from shell and UI-automation capabilities.
- Require explicit depth, node-count, result-size, elapsed-time, and memory budgets.
- Track visited accessibility objects and terminate cycles.
- Tie responder work to the caller's lifetime and cancel outstanding work when the caller exits.
- Monitor the newly created `System Events` PID from an independent watchdog and fail closed on abnormal growth.
- Apply outbound-network policy independently; memory containment is not an exfiltration control.

### Review and detection

- Run `tools/lint_system_events.py` over proposed AppleScript and JXA before execution.
- Preserve command provenance, exit status, child PID, target process, and timestamps.
- Alert on rapid `System Events` CPU or resident-memory growth and repeated relaunches.
- Review Automation and Accessibility grants periodically and remove grants an agent no longer needs.

## Exfiltration boundary

The 187.76 GB figure is process footprint. It may include allocated objects, descriptors, compressed memory, and swap accounting, and can be much larger than the data that caused it. Exfiltration would additionally require data selection, serialization, an outbound channel, and evidence of transmission. None of those was established here.

A purpose-built malicious agent workflow could combine separate capabilities: authorized or stolen access to sensitive data, a staging mechanism, outbound transport, and this resource-exhaustion primitive. In that chain, the runaway could impair monitoring, force unrelated processes to terminate, disrupt incident response, or provide destructive cover while another component attempts exfiltration. The availability primitive still does not grant data access, create an outbound channel, or make the 187.76 GB footprint an exfiltration-volume measure.

Defenses must therefore cover both halves of the chain: out-of-band resource monitoring and process containment for the denial-of-service path, plus least-privilege data access, destination allowlists, egress logging, rate limits, and data-loss controls for the exfiltration path.

The supported incident conclusion remains local availability impact. This repository contains no malware implementation or exfiltration procedure.

## Reviewable non-deployable model

[`simulation/nondeployable_chain.py`](../simulation/nondeployable_chain.py) makes the hypothetical stages concrete without implementing harmful capabilities. It uses one fixed non-secret fixture, exposes a U+200B zero-width character in an escaped view, and records a `content-is-data` policy decision. Real data access, `System Events` invocation, and network egress are separate functions that only raise `CapabilityIntentionallyOmitted`.

This structure lets a reviewer verify the intended security boundaries and tests without receiving a working exploit, malware sample, collector, or exfiltration path. See [`simulation/README.md`](../simulation/README.md).

## Additional holes to close

- **Retry amplification:** a controller can relaunch the responder and reproduce the pressure after a failed attempt.
- **Caller/responder lifetime mismatch:** the requesting `osascript` process can exit while `System Events` continues expensive work.
- **Permission concentration:** one agent process holding shell, Automation, Accessibility, and network access creates a broad blast radius.
- **Unicode and control-character opacity:** visually equivalent content can differ at the byte, code-point, tokenizer, and parser layers.
- **Diagnostic privacy:** raw `.diag`, `.ips`, sysdiagnose, and session records can contain identifiers and unrelated process data.
- **Version uncertainty:** macOS 27.2 has not been tested for this trigger; its public advisory does not name this issue.
- **Unrelated remote-access surface:** remote-support and VPN software should be reviewed as ordinary attack-surface hygiene, but it was not the trigger found here.
