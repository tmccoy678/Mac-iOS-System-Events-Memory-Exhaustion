# macOS System Events memory exhaustion

Private coordinated-disclosure case study and Apple-ready report for an availability defect observed in Apple's `System Events` scripting bridge on macOS 27.0.1 (26A434).

> **Private disclosure status:** Do not make this repository public or publish the proof of concept before Apple has had a reasonable opportunity to investigate and coordinate remediation.

![System Events footprint grew from 15.48 MB to 187.76 GB in 111.7 seconds](figures/system-events-footprint.png)

## Start here

- [`CASE_STUDY.md`](CASE_STUDY.md) — full first-person manuscript with abstract, introduction, methods, data analysis and statistics, results, discussion, conclusion, declarations, and APA citations.
- [`report/system-events-memory-exhaustion.md`](report/system-events-memory-exhaustion.md) — concise vendor-facing vulnerability report.
- [`report/apple-portal-summary.md`](report/apple-portal-summary.md) — short submission text for Apple's portal.
- [`proposed-patch/cooperative-pause-drain-resume.md`](proposed-patch/cooperative-pause-drain-resume.md) — cooperative recovery patch recommendation for Apple and automation clients.
- [`mitigation/README.md`](mitigation/README.md) — deployed client-side blocker, memory watchdog, LaunchAgent, installer, and operating notes.
- [`REFERENCES.md`](REFERENCES.md) — APA-formatted references; the source-reading ledger records the complete-reading rule used for citation.

## What happened

A local automation process with macOS Automation and Accessibility permission inspected Microsoft Outlook through `System Events`. After recursive and unbounded accessibility-tree enumeration, the first-party `System Events` process entered a recursive scripting-metadata path and exhausted memory.

The first Apple CPU-resource diagnostic measured `System Events` growing from **15.48 MB to 187.76 GB in 111.742 seconds** while averaging 66% CPU. The Mac had 24 GB of physical memory. A later jetsam record accounted approximately 222.55 GiB to that process. After `System Events` was relaunched and broad accessibility queries were repeated, the second instance later accounted approximately 253.91 GiB.

Normalizing the first endpoint with the documented analysis convention of 1 GB = 1,024 MB gives a **12,420.2997-fold increase** and an endpoint **7.8233 times installed physical memory**. The dataset contains two endpoint measurements; the intermediate trajectory was unmeasured.

The observed impact is local availability loss with extreme memory and swap pressure. The exact source defect, affected-release range, and repair status remain unknown.

## Repository map

- `report/` — Apple-ready technical disclosure report.
- `CASE_STUDY.md` — full case-study manuscript in Taylor's established first-person, evidence-led style.
- `REFERENCES.md` and `references/` — APA references and complete-source reading ledger.
- `docs/forensic-timeline.md` — sanitized event and attribution timeline.
- `docs/agent-threat-model.md` — bounded analysis of agent prompt-injection and denial-of-service risk.
- `evidence/sanitized/observations.json` — machine-readable values derived from Apple diagnostics.
- `analysis/` — reproducible descriptive-statistics script.
- `figures/` — source data, reproducible generator, SVG, and PNG.
- `poc/` — disabled trigger text and a non-executing review harness. **Do not execute the trigger on a production Mac.**
- `proposed-patch/` — cooperative pause–drain–resume patch recommendation, state machine, pseudocode, and validation plan.
- `mitigation/` — deployable Codex hook and independent `System Events` memory containment used on the affected Macs.
- `simulation/` — non-deployable model with fixed synthetic data and fail-closed stubs for every dangerous capability.
- `tools/lint_system_events.py` — heuristic guard against the unbounded automation patterns involved here.
- `tests/` — regression tests for the linter, analysis, and safe simulation.

Raw `.diag` and `.ips` files are intentionally excluded from Git. They remain preserved separately for a private Apple submission because they can contain host-specific process inventories and identifiers.

## Immediate mitigation

Do not use `entire contents`, `every UI element`, `every application process`, or recursive `uiElements()` traversal through `System Events` on a complex application. Use targeted accessibility selectors with explicit depth, node-count, memory, and time limits. If automation hangs, terminate both the requesting process and the newly launched `System Events` instance before retrying through a narrower route.

Run the local heuristic guard before accepting AppleScript or JXA automation:

```sh
python3 tools/lint_system_events.py path/to/script.applescript
```

Install the deployed runtime containment package on an affected Mac:

```sh
./mitigation/install.sh
```

## Validation status

- Runtime failure: observed twice on macOS 27.0.1 (26A434).
- Attribution: matched to local Terminal-launched `osascript` commands and a recorded coding-agent workflow.
- Statistics: reproduced directly from sanitized evidence by `analysis/analyze_observations.py`; `n = 2`, descriptive only.
- Safe threat simulation: capability is limited to fixed synthetic content and fail-closed stubs; five tests verify every boundary.
- Runtime containment: deployed and verified on the owner's Mac Studio and 2026 MacBook Pro; the pre-tool hook blocks the recorded query shape and the five-second LaunchAgent enforces a 1 GiB responder ceiling.
- Prose style: a repository-wide regression test rejects defensive claim-versus-limitation contrast templates.
- Current machine state: healthy after process termination; no active runaway remained.
- macOS 27.2 status: untested at the owner's request. Apple's public 27.2 security notes contain zero matching `System Events`, AppleScript, or Automation entry.
- Vendor source: unavailable because the relevant Apple implementation is closed source. The report is runtime-evidence-based and keeps source-dependent conclusions conditional.

## Disclosure handling

See [SECURITY.md](SECURITY.md). Preserve the private repository and raw evidence until Apple assigns a case identifier and provides disclosure guidance.
