# When System Events Reported a 187.76 GB Footprint: A Forensic Case Study of Agent-Generated Accessibility Enumeration on macOS

Taylor McCoy<br>
October 27, 2026

> **Disclosure status:** Private coordinated-disclosure manuscript. The active trigger, raw Apple diagnostics, and private session material are not published in this repository.

## Abstract

I investigated an extreme memory event on a Mac17,2 with an Apple M5, 24 GB of physical memory, and macOS Golden Gate 27.0.1 (26A434). A local coding agent was inspecting Microsoft Outlook through AppleScript and JavaScript for Automation when it generated broad accessibility queries, including recursive `uiElements()` traversal and `entire contents` enumeration through Apple's `System Events` process. Apple's first CPU-resource diagnostic measured the process footprint increasing from 15.48 MB to 187.76 GB in 111.742 seconds while averaging 66% CPU. Under the unit normalization used in this study, that was a 12,420.30-fold endpoint increase and an endpoint equal to 7.82 times installed physical memory. A later jetsam record accounted 222.55 GiB to the process. After `System Events` was relaunched and broad queries were repeated, a fresh process entered the same stack family; its measured footprint rose from 110.64 MB to 4,248.64 MB in 91.488 seconds, and a later jetsam record reported a 253.91 GiB lifetime maximum. Both diagnostics repeatedly sampled one `System Events` offset followed by Foundation scripting-property lookup in `NSScriptClassDescription`.

The evidence supports a local availability failure associated with broad accessibility enumeration and unbounded scripting work. It does not identify the exact closed-source defect or show data exfiltration, prompt injection, memory corruption, privilege escalation, or remote exploitation. I model a plausible prompt-injection delivery chain because an agent with shell, Automation, Accessibility, and network authority could combine otherwise separate capabilities. The accompanying model is deliberately non-deployable: it uses one fixed synthetic record, surfaces a zero-width character, and replaces real data access, `System Events` execution, and network egress with fail-closed stubs. This case demonstrates why agent controllers need content/tool separation, narrow accessibility selectors, recursion and memory budgets, retry suppression, independent process monitoring, and egress controls that remain effective during local resource exhaustion.

**Keywords:** macOS; System Events; AppleScript; accessibility; resource exhaustion; prompt injection; agent security; forensic case study; denial of service

## Introduction

At approximately 11:12 local time on October 27, 2026, a coding agent working in my logged-in session attempted to inspect Outlook's interface. The agent first used a narrow `System Events` query, then wrote a JavaScript for Automation helper that recursively called `uiElements()` to a nominal depth of six without a global node limit, cycle check, memory limit, or wall-clock budget. It next generated AppleScript using `entire contents of front window` and bulk property retrieval. Within the same interval, Apple's diagnostic system recorded `System Events` growing from megabytes to a reported 187.76 GB footprint.

The number was startling because the Mac contained 24 GB of physical memory. Process footprint can exceed physical RAM through virtual-memory accounting, compression, swap, and retained allocation. It is not a measure of how much Outlook data was read, and it is not a measure of network transmission. The central empirical question was therefore narrower: what local process entered the runaway state, which recorded actions preceded it, did the behavior recur in a fresh process, and what security boundary failed?

`System Events` is a first-party automation bridge. macOS separately controls whether one application may automate another, and accessibility-based UI scripting requires an already authorized local host (Apple Inc., n.d.-a). Foundation's documented scripting machinery includes `NSScriptSuiteRegistry`, which manages scripting terminology, and `NSScriptClassDescription`, which maps Apple-event codes to scriptable keys (Apple Inc., n.d.-b, n.d.-c). Those documented roles are relevant because the preserved stacks repeatedly traverse `-[NSScriptClassDescription keyWithAppleEventCode:]` and a private property-description lookup. They do not reveal the private implementation or establish the missing guard.

I asked five questions:

1. Which process and command sequence preceded the memory event?
2. Did a fresh `System Events` process enter the same stack family after broad queries were repeated?
3. How large was the observed change relative to its starting footprint and installed memory?
4. What can the record support about prompt injection, malware, and exfiltration?
5. Which controls would have prevented or contained the event without requiring an Apple patch?

This is a two-episode forensic case study, not a population estimate. I use descriptive statistics, preserve the distinction between measured endpoints and inferred behavior between them, and leave the source-level defect unknown.

## Methods

### Case design and system

I conducted a retrospective, single-machine forensic case study. The assessed system was a Mac17,2 with an Apple M5, 24 GiB of physical memory, macOS Golden Gate 27.0.1 (26A434), and `System Events` 1.3.6 (build 607). Microsoft Outlook was the UI target. The initiating commands ran locally through `osascript` from an automation-capable coding-agent workflow. Existing Automation and Accessibility permissions were prerequisites; the event did not create those grants.

I refer to two fresh-process episodes:

- **Episode 1:** `System Events` PID 40483, associated with the first recursive and bulk Outlook queries.
- **Episode 2:** `System Events` PID 41643, launched after the first responder was terminated and exposed to repeated broad queries.

### Evidence preservation

The primary evidence comprised two Apple CPU-resource diagnostics, two Apple jetsam records, and the local automation-session record. I preserved the four Apple artifacts outside Git because diagnostic bundles can expose host and process metadata. Their SHA-256 values, derived numerical fields, and selected stack markers are recorded in [`evidence/sanitized/observations.json`](evidence/sanitized/observations.json). The command sequence is reduced to a privacy-preserving chronology in [`docs/forensic-timeline.md`](docs/forensic-timeline.md). No message body, account identifier, credential, serial number, hardware UUID, or private email content is included.

I matched events by local timestamp, process identifier, executable, Apple-event direction, and diagnostic interval. The first broad recursive helper executed at 11:12:34.866; the first diagnostic footprint measurement began 2.883 seconds later. The repeated `entire contents` helper executed at 11:21:00.713; the second footprint interval began 2.828 seconds later. Temporal order alone does not identify the source-level defect, so I also compared the two sampled stack families and the fresh-process recurrence.

### Public-source review

I read Apple's Automation guidance, the complete accessible documentation for `NSScriptClassDescription` and `NSScriptSuiteRegistry`, Apple's Security Bounty guidelines, and every vulnerability record in Apple's macOS 27.2 security advisory. The advisory contained 263 structured vulnerability records; none was titled `System Events`, AppleScript, or Automation for this trigger (Apple Inc., 2026). I also read OWASP's prompt-injection entry and MITRE's CWE-400 entry in full (MITRE, 2026; OWASP Foundation, 2025). A source-coverage ledger is preserved in [`references/SOURCE-READING-LOG.md`](references/SOURCE-READING-LOG.md), and the APA references are in [`REFERENCES.md`](REFERENCES.md).

### Agent and command attribution

I treated the recorded shell and automation commands as the direct action layer. The local agent generated the risky query shapes while troubleshooting Outlook. I searched the available incident record for a hidden or invisible instruction that could explain those commands and found none. Prompt injection therefore remains a threat-model path rather than an observed cause.

The agent's instructions, model family, and application context are not substitutes for command provenance. The defensible attribution is that a local agent workflow authored and executed broad `osascript` requests under my session's existing permissions. The identity and intent of any hypothetical upstream attacker are unknown because no attacker-controlled instruction was identified.

### Non-deployable threat simulation

I implemented a safe model of the larger chain in [`simulation/nondeployable_chain.py`](simulation/nondeployable_chain.py). It demonstrates four boundaries: untrusted content, a policy decision, synthetic staging, and omitted dangerous capabilities. The input contains one visible marker and one U+200B zero-width space. The program renders an escaped view, treats the text as data, and stages only the fixed non-secret byte string `DEMO-RECORD-NOT-PRIVATE`.

The model cannot read real data, launch a process, invoke AppleScript, contact a destination, or transmit bytes. Calls to those three omitted capabilities raise `CapabilityIntentionallyOmitted`. Five tests verify the absent capabilities, hidden-character surfacing, fixed fixture hash, stage status, and command-line report. This supplies a concrete review target without supplying malware or a working denial-of-service chain.

### Safety constraints

I did not replay the hazardous query during this investigation. The affected Mac remains on macOS 27.0.1 at my request, and no system patch or configuration change was applied. Active validation belongs on a disposable test Mac with an independent watchdog, a second control channel, hard time and memory limits, and a plan to terminate both the caller and the specific `System Events` instance.

## Data Analysis and Statistics

I analyzed two observed episodes (`n = 2`) descriptively. I did not perform an inferential significance test or estimate an exploitation probability. The cases were not randomly sampled, the query forms differed, and the later jetsam measurements occurred outside the CPU-resource intervals.

For a diagnostic endpoint reported in GB, I normalized the reported units using the figure's explicit convention of `1 GB = 1,024 MB`. This is a declared arithmetic convention for comparing Apple's printed MB and GB labels, not a claim that the diagnostic defined those labels as IEC units. The growth multiple was:

```text
normalized endpoint / starting endpoint
```

The endpoint-derived mean change was:

```text
(normalized endpoint - starting endpoint) / measured interval seconds
```

That quantity summarizes two endpoints. It is not an instantaneous allocation rate, and the path between endpoints was not sampled. The physical-memory multiple was the reported endpoint or jetsam GiB value divided by 24 GiB. The mean trigger-to-measurement lag was calculated from the two matched command and interval-start timestamps. [`analysis/analyze_observations.py`](analysis/analyze_observations.py) reproduces every derived value from the sanitized JSON.

| Measure | Episode 1 | Episode 2 |
| --- | ---: | ---: |
| Starting footprint | 15.48 MB | 110.64 MB |
| Measured endpoint | 187.76 GB | 4,248.64 MB |
| Normalized endpoint (1 GB = 1,024 MB) | 192,266.24 MB | 4,248.64 MB |
| Measured interval | 111.742 s | 91.488 s |
| Growth multiple | 12,420.2997× | 38.4006× |
| Endpoint-derived mean change | 1,720.4879 MB/s | 45.2300 MB/s |
| Endpoint / physical memory | 7.8233× | 0.1729× |
| Average CPU in diagnostic | 66% | 67% |
| Broad-query-to-measurement lag | 2.883 s | 2.828 s |
| Later jetsam comparison | 9.2728× physical memory | 10.5795× physical memory at lifetime maximum |

The arithmetic mean of the two diagnostic CPU averages was 66.5%. The mean temporal lag was 2.8555 seconds. Both episodes showed the same three selected stack markers, but `2/2` recurrence is a case observation rather than a reliability or prevalence estimate.

![System Events footprint grew from 15.48 MB to 187.76 GB in 111.742 seconds](figures/system-events-footprint.png)

**Figure 1.** Recorded first-episode endpoints. The dashed connector is visual only; it does not represent a sampled trajectory. The right panel compares the reported endpoint with installed physical memory.

## Results

### 1. The runaway process was Apple's System Events

**Observed.** Apple's first CPU-resource diagnostic identified `System Events` PID 40483 and measured its footprint from 15.48 MB to 187.76 GB between 11:12:37.749 and 11:14:29.491. The process accumulated 90 CPU seconds in a 136-second report window, approximately 66% average CPU. The immediate `osascript` caller returned while `System Events` continued working.

**Observed.** The later jetsam record identified the same PID at 14,584,802 resident pages. At the report's 16 KiB page size, that equals 222.5464 GiB, or 9.2728 times installed physical memory.

### 2. The diagnostic stack repeatedly crossed the scripting-property path

**Observed.** The first heaviest stack contained many consecutive frames at `System Events + 10792`, followed by `-[NSScriptClassDescription keyWithAppleEventCode:]` and `_propertyDescriptionForAppleEventCode:checkSubclasses:`. Other samples passed through `NSAppleEventManager`, `NSScriptingAppleEventHandler`, repeated script-object-specifier evaluation, and descriptor construction.

**Inferred.** The stack shape is consistent with repeated or recursive expansion in the scripting bridge while it resolves accessibility objects and properties. The specific failed invariant—cycle handling, repeated class lookup, object-specifier recursion, descriptor construction, cancellation, or a combination—remains unknown.

### 3. A fresh process reproduced the same stack family

**Observed.** After the first responder was terminated, new `System Events` PID 41643 received repeated broad Outlook queries. Its diagnostic measured 110.64 MB to 4,248.64 MB in 91.488 seconds at approximately 67% CPU. The selected stack markers matched Episode 1. A later jetsam record reported 16,639,984 resident pages and a lifetime maximum of 16,640,096 pages, equal to 253.9060 and 253.9077 GiB.

**Inferred.** The recurrence shows that the first process's accumulated state was not required. It strengthens the association between the broad query family and the responder failure, while leaving general reproducibility across systems and applications unknown.

### 4. The recorded agent workflow supplied the direct trigger sequence

**Observed.** The local workflow generated recursive `uiElements()` traversal, `entire contents of front window`, bulk property retrieval, and retries. These commands preceded both measured intervals. The commands were troubleshooting attempts, not a purpose-built exploit.

**Unknown.** No preserved evidence identifies a hidden prompt, zero-width instruction, erased instruction, malicious email, or remote actor as the origin of those commands. The actor behind any hypothetical prompt injection is therefore unknown.

### 5. The event demonstrated availability impact, not 188 GB of exfiltration

**Observed.** The process footprint and jetsam accounting exceeded physical memory many times over and created severe compression and swap pressure. Terminating the runaway responder restored a healthy state. A 12:38:18 read-only check found no `System Events` process running, 83% system-wide memory free, and 1,877.12 MB of encrypted swap still in use. A second check at 12:54:55 again found no responder, 78% memory free, and 1,219.19 MB of 2,048 MB encrypted swap in use. macOS remained 27.0.1 (26A434).

**Observed.** The record contains no matching network transfer, staged archive, destination, credential use, persistence mechanism, or malware installation. The 187.76 GB value is memory accounting, not source-data volume.

**Inferred.** A separate malicious component could attempt data access and egress while using resource exhaustion as distraction or destructive cover. That chain requires capabilities the observed defect does not create.

### 6. The current public advisory does not identify this issue

Apple's macOS 27.2 advisory, dated October 26, 2026, did not identify a `System Events`, AppleScript, or Automation entry matching this trigger among its 263 vulnerability records (Apple Inc., 2026). The affected range and repair status remain unknown because I did not install or test 27.2.

## Discussion

### A local availability primitive with an agent delivery path

The narrow finding is a local availability primitive. Code already running under the logged-in user, with the required Automation and Accessibility grants, can ask a first-party responder to expand a complex accessibility hierarchy. In this case, the responder continued expensive work after the requesting process returned and reached a footprint far beyond physical memory. The behavior is conceptually consistent with uncontrolled resource consumption, but I do not assign CWE-400 as a definitive root-cause mapping because MITRE cautions against using that high-level category when a more specific implementation weakness is known (MITRE, 2026). Here, the implementation weakness is not yet known.

Agent systems make this primitive more consequential because they can connect untrusted content to tools. OWASP describes both direct and indirect prompt injection, including hidden or obfuscated instructions, and recommends constrained behavior, least privilege, separation of untrusted content, and human approval for high-impact actions (OWASP Foundation, 2025). The incident did not establish prompt injection, but it established the dangerous downstream half: an agent-generated command, an already authorized automation surface, and a first-party process that failed under an expansive request.

The safe threat chain is:

```text
untrusted content
  -> model or controller mistakes data for authority
  -> already-authorized local automation invokes a broad UI query
  -> System Events performs unbounded scripting work
  -> compression, swap, jetsam, and local availability loss
```

A larger malicious chain could add data access, staging, and outbound transport. Those capabilities should be analyzed separately:

```text
data access -> bounded staging -> independently governed egress
                               \
                                +-> separate resource-exhaustion distraction
```

The separation matters. Blocking `System Events` recursion does not control network egress, and blocking network egress does not prevent local denial of service. A secure agent runtime needs both.

### The Backspace boundary

My separate Backspace Gate work showed that a terminal recording can preserve echoed bytes for a draft that is later visually erased even when canonical line editing delivers only the committed line to the child process (McCoy & Blu, 2026). That result motivates byte-level evidence preservation and an escaped code-point view. It does not establish that Outlook, a cloud model, or the agent in this incident received erased text. Terminal display, recorder output, process input, model input, model output, and tool execution remain distinct evidence layers.

### Defensive controls

The most important client-side control is to reject broad query shapes before execution. `entire contents`, `every UI element`, recursive `uiElements()`, unrestricted property retrieval, and whole-process enumeration should require a narrower plan. Accessibility traversal should use a visited-object set plus explicit depth, node, result-size, time, and memory budgets. A first hang or abnormal slowdown should stop the workflow; a controller should not relaunch the responder and retry through another broad route.

The agent boundary needs separate authorities for content reading, shell execution, UI automation, sensitive-data access, and networking. Untrusted message and document text should remain data. Proposed commands should be logged and screened independently of the model that generated them. An out-of-process monitor should watch the new `System Events` PID and terminate the request at a conservative growth threshold. Network destination allowlists, egress logging, rate limits, and data-loss controls should remain outside the potentially exhausted process tree.

Apple's responder can provide the final containment layer. Each inbound event should have budgets for recursion, visited objects, result count, descriptor size, elapsed time, and allocation. Cycle detection should cover accessibility objects, script object specifiers, class-description traversal, and descriptor construction. Sender exit and cancellation should end outstanding work. Limit breaches should release intermediate objects, return a bounded error, and leave `System Events` responsive.

### Additional holes identified

- **Retry amplification:** a controller can relaunch `System Events` and reproduce the pressure after treating a hang as a transient failure.
- **Caller/responder lifetime mismatch:** the requesting `osascript` process can return while the first-party responder continues expensive work.
- **Permission concentration:** shell, Automation, Accessibility, sensitive-data access, and network authority in one agent process create an unnecessarily large blast radius.
- **Content opacity:** zero-width, bidirectional, and control characters can create different byte, rendered, tokenizer, and parser views.
- **Diagnostic privacy:** raw CPU, jetsam, and sysdiagnose artifacts can expose unrelated process and machine information.
- **Monitoring fragility:** an in-process monitor may fail with the workload it is meant to contain; the watchdog needs an independent control path.
- **Version uncertainty:** the current production observation is on 27.0.1, while 27.2 remains untested.
- **Target variability:** Outlook's accessibility hierarchy may not represent other applications, UI states, or data volumes.

### Disclosure and bounty readiness

Apple's Security Bounty guidelines ask for a clear, actionable report with reliable reproduction and testing on the latest publicly available software (Apple Security Research, n.d.). This repository contains strong diagnostics, recurrence, command attribution, a disabled trigger shape, and proposed regression tests. It is ready for private Apple triage. It is not yet a complete bounty-validation package because the latest public macOS release has not been tested and the packaged trigger was not replayed under a controlled lab protocol.

I would submit the evidence privately now if the goal is early vendor notice, while describing 27.2 status as unknown. A stronger bounty package would add one bounded reproduction on a disposable Mac running the latest public release, a narrow-query negative control, an independent watchdog trace, and confirmation that terminating the caller does or does not cancel responder work. I would not perform that experiment on this production Mac.

### Limitations

This study contains two episodes on one Mac, one operating-system build, one target application, and one local user session. The query sequence was not factorially controlled. The first and second measured endpoints differ substantially, and the later jetsam records are not continuous samples from the CPU-report intervals. The raw artifacts remain private and therefore are not independently reviewable from this repository alone.

Apple's relevant source is closed. Stack symbols support a mechanism hypothesis but not a source-level root cause. The 27.2 advisory review can establish only that the public advisory does not name this issue; it cannot establish whether an unlisted change repaired it. The incident record does not preserve network telemetry sufficient to exclude every unrelated transfer on the machine, although no evidence tied exfiltration to this event. Finally, the coding agent's generation of unsafe commands does not establish that untrusted content caused it to do so.

## Conclusion

A local coding-agent workflow issued broad Outlook accessibility requests through `System Events` on macOS 27.0.1. Apple's first diagnostic measured the responder growing from 15.48 MB to a reported 187.76 GB footprint in 111.742 seconds, a normalized 12,420.30-fold increase and 7.82 times installed physical memory. A fresh process later reproduced the same stack family, and the two jetsam records reached 222.55 and 253.91 GiB accounting values.

The supported outcome is severe local resource exhaustion in a first-party automation responder. The exact defect, affected-version range, prompt-injection origin, and repair status remain unknown. The memory number is not an exfiltration measurement. The broader security lesson is still concrete: an agent that combines untrusted content, powerful local automation, retry behavior, and concentrated permissions can turn an ordinary troubleshooting request into system-wide availability loss. Narrow query design, explicit budgets, independent monitoring, separated capabilities, and fail-closed egress controls would materially reduce that risk today.

## Declarations

### Data and code availability

Sanitized observations, derived statistics, the figure generator, defensive linter, disabled trigger text, and non-deployable simulation are preserved in this private repository. Raw Apple diagnostics and private session records are retained separately for vendor disclosure because they contain unnecessary host and process metadata.

### AI assistance

OpenAI Codex assisted with read-only forensic inspection, arithmetic reproduction, source review, defensive code, testing, figure production, and manuscript drafting under my direction. I retained the claim boundaries, source-selection rule, disclosure decision, and final authorship responsibility. The incident itself involved a separate local coding-agent workflow; that workflow's generated commands are part of the evidence under study.

### Safety and ethics

I did not execute the disabled trigger while preparing this repository, did not access another person's account or data, and did not include real data collection, persistence, destructive action, or network egress in the simulation. The affected production Mac was left on macOS 27.0.1 at my request and remains unsuitable for active replay.

### Competing interests

I report no financial competing interest. A potential Apple Security Bounty submission may create a future financial interest; no award, eligibility decision, CVE, or Apple confirmation exists at the time of writing.

## References

APA-formatted references and the complete-source review ledger are available in [`REFERENCES.md`](REFERENCES.md) and [`references/SOURCE-READING-LOG.md`](references/SOURCE-READING-LOG.md).
