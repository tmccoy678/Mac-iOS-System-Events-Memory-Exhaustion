# Sanitized forensic timeline

All times below are local time in CDT (UTC-05:00) on 2026-10-27. The timeline combines the recorded automation session with Apple CPU-resource and jetsam diagnostics. It omits email content, account identifiers, host names, and conversation text.

| Time | Observed event | Evidence class |
| --- | --- | --- |
| 11:12:14.420 | A local automation session issued a narrow query for Outlook's frontmost state and window names through `System Events`. | Recorded command |
| 11:12:14.553 | Apple's first CPU-resource diagnostic window began for `System Events`. | Apple diagnostic |
| 11:12:28.763 | The automation session created a JXA helper that recursively called `uiElements()` to depth six. It had no global node-count, cycle, memory, or wall-clock budget. | Recorded command |
| 11:12:34.866 | The JXA helper was executed against Outlook. | Recorded command |
| 11:12:37.749 | The first measured footprint endpoint for `System Events` PID 40483 was 15.48 MB. | Apple diagnostic |
| 11:12:49.815 | The JXA caller returned, but the first-party responder remained active. | Recorded command and Apple diagnostic |
| 11:13:00.766 | The session created an AppleScript helper using `entire contents of front window`, followed by per-element property retrieval. | Recorded command |
| 11:13:04.852 | The `entire contents` helper was executed. | Recorded command |
| 11:13:52.546 | A further bulk request asked for multiple properties of every top-level UI element. | Recorded command |
| 11:14:29.491 | The second CPU-diagnostic footprint endpoint was 187.76 GB. It was recorded 111.742 seconds after the 15.48 MB endpoint; the spacing is not a measured growth duration. | Apple diagnostic |
| 11:14:30.987 | The first CPU-resource diagnostic window ended. Its heaviest stack repeatedly traversed one `System Events` offset and Foundation scripting-class property lookup. | Apple diagnostic |
| 11:14:37.218 | Inferred jetsam snapshot time for PID 40483: 14,584,802 pages at 16 KiB per page, or 222.5464 GiB. The final measured interval added 34.7864 GiB in 7.727 seconds, averaging 4.5019 GiB/s. | Apple jetsam report; timestamp inferred as report date minus `timeDelta` and cross-checked against termination logs |
| 11:15:21.673 | An Escape-key request through `System Events` caused the service to be available again as a fresh process, PID 41643. | Recorded command and later diagnostic |
| 11:20:21.832 | Apple's second CPU-resource diagnostic window began. | Apple diagnostic |
| 11:21:00.713 | The broad `entire contents` helper was retried. | Recorded command |
| 11:21:03.541 | The first CPU-diagnostic footprint endpoint for PID 41643 was 110.64 MB. | Apple diagnostic |
| 11:21:45.712 | The recursive JXA helper was retried. | Recorded command |
| 11:22:35.029 | The second CPU-diagnostic footprint endpoint for PID 41643 was 4,248.64 MB, recorded 91.488 seconds after the first endpoint. | Apple diagnostic |
| 11:22:35.587 | The second CPU-resource diagnostic window ended with the same stack family. | Apple diagnostic |
| 11:35:32.810 | The jetsam artifact containing the earlier PID 40483 snapshot was reported. Its `timeDelta` field was 1,255,592 milliseconds. | Apple jetsam report |
| 12:13:38 | A second jetsam artifact recorded PID 41643 at 16,639,984 resident pages and a lifetime maximum of 16,640,096 pages: 253.9060 and 253.9077 GiB, respectively. | Apple jetsam report |
| 12:38:18 | No `System Events` process was running. macOS reported 83% system-wide memory free and 1,877.12 MB of encrypted swap in use. The installed OS remained 27.0.1 (26A434). | Read-only live check |
| 12:54:55 | No `System Events` process was running. macOS reported 78% system-wide memory free and 1,219.19 MB of 2,048 MB encrypted swap in use. The installed OS remained 27.0.1 (26A434). | Read-only live check |

## Same-day recurrence and containment deployment

Later on 2026-10-27, a separate Codex workflow on the owner's Mac Studio issued
an `osascript` command containing `entire contents` against Outlook. The exact
requesting child process and its runaway `System Events` responder were stopped;
the canonical Codex conversation process remained alive. Private Outlook content
was excluded from the retained record.

The recurrence matched the original hazardous command shape and motivated four
deployed controls on both affected Macs:

1. a Codex pre-tool hook that blocks unbounded `System Events` command shapes;
2. an independent five-second LaunchAgent that terminates `System Events` at a
   1 GiB resident-set ceiling;
3. agent instructions requiring bounded selectors and forbidding retries of the
   same unbounded query; and
4. short Computer Use startup and tool timeouts so a missing authenticated broker
   fails promptly.

Post-deployment checks on both Macs found no active `System Events` or
`osascript` process. Each LaunchAgent reported successful interval runs with a
zero exit status. The deployable files and regression tests are preserved in
[`mitigation/`](../mitigation/README.md).

## Attribution

The direct trigger was the locally recorded automation sequence. Command provenance attributes the harmful action to agent-generated `osascript` requests. Earlier prompt provenance is unavailable, leaving prompt origin unknown.

The repeated stack family and recurrence in a fresh `System Events` process support an availability defect in Apple's handling of broad accessibility object and property requests. Apple's implementation is closed source, so the exact source-level defect remains unknown.

## Evidence limits

- The plot contains two CPU-diagnostic endpoints and one later jetsam snapshot. The 111.742 seconds is endpoint spacing, not growth duration. Intermediate trajectory and exact peak were unmeasured.
- Jetsam reports contain aggregate process histories. The simultaneous kill set is unknown.
- Process footprint and resident-page accounting quantify memory state. Source-content volume and network transfer require separate measurements.
- Confirmed impact: severe local resource exhaustion. File-loss outcome, outbound traffic, memory-safety behavior, and privilege-transition behavior remain unresolved by the preserved record.
