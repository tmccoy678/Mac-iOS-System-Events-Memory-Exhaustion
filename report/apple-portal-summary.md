# System Events resource exhaustion from broad accessibility enumeration

## Product and build

- macOS 27.0.1 (26A434)
- Mac17,2, Apple M5, 24 GB physical memory
- `System Events` 1.3.6 (build 607)
- Target application: Microsoft Outlook

## Observed behavior

A local automation client with existing Automation and Accessibility authorization issued broad accessibility queries through `System Events`. A fresh `System Events` process remained active after the immediate caller returned and entered a deeply repeated scripting-class property-lookup stack.

During the first run, Apple's CPU-resource diagnostic measured the process footprint growing from 15.48 MB to 187.76 GB between 11:12:37.749 and 11:14:29.491, a 111.742-second interval, at approximately 66% CPU. A later jetsam record accounted 14,584,802 resident pages at 16 KiB per page, or 222.5464 GiB.

A new `System Events` process reached the same stack family after the broad queries were repeated. Its CPU diagnostic measured 110.64 MB to 4,248.64 MB in 91.488 seconds, and a later jetsam record reported a 253.9077 GiB lifetime maximum.

## Expected behavior

A broad or cyclic accessibility hierarchy should complete within a resource budget or return a bounded error. Cancellation or caller exit should stop outstanding work. `System Events` should remain responsive and should not drive system-wide compression, swap, and jetsam pressure.

## Minimal reproduction shape

1. On a disposable test Mac, grant a terminal automation host permission to control `System Events` and inspect Outlook through Accessibility.
2. Open an Outlook window with its normal complex UI hierarchy.
3. Start an independent watchdog for the newly launched `System Events` PID.
4. Issue `entire contents of front window` and retrieve several properties from each returned element, as preserved in `poc/trigger.applescript.disabled.txt`.
5. Observe `System Events` CPU, resident memory, and stack samples. Stop immediately on abnormal growth.
6. Relaunch `System Events` and repeat once to confirm fresh-process recurrence.

The packaged trigger is disabled and was not replayed during report preparation. The incident itself produced two recorded runs. Raw diagnostics and a sanitized command timeline are available.

## Security impact and prerequisites

The demonstrated impact is local denial of service through uncontrolled resource consumption in a first-party responder. Local code execution and existing Automation and Accessibility authorization are required. An automation-capable agent that mistakes untrusted document or message text for instructions is a plausible delivery path, but prompt injection was not observed in this incident.

The 187.76 GB value is process footprint, not a measure of Outlook data read or transmitted. There is no evidence here of exfiltration, memory corruption, privilege escalation, or remote code execution.

A separate malicious component with data access and outbound transport could use the resource-exhaustion effect to impair monitoring or disrupt response while attempting exfiltration. That is a plausible chained-risk scenario, not an observed event or a capability conferred by the memory-exhaustion defect itself.

## Root-cause evidence

Both runs repeatedly sampled `System Events + 10792`, followed by Foundation's `-[NSScriptClassDescription keyWithAppleEventCode:]` and `_propertyDescriptionForAppleEventCode:checkSubclasses:`. Other samples traverse Cocoa scripting object-specifier and descriptor construction. This supports an unbounded recursion or repeated-expansion failure in the responder's scripting bridge, but Apple's closed source prevents a source-level conclusion.

## Version status

macOS 27.2 was released on 2026-10-26 but has not been installed or tested on the affected production Mac. Its public security advisory does not name `System Events`, AppleScript, or Automation for this trigger. The affected range and fixed release are unknown.
