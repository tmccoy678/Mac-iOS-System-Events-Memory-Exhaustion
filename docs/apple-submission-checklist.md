# Apple submission checklist

Apple's current [Security Bounty guidelines](https://security.apple.com/bounty/guidelines) prioritize concise, human-validated, actionable reports with reliable reproduction steps. They also say not to disclose an issue publicly before Apple publishes a fix, and recommend attaching the proof of concept rather than relying on a hosted link.

## Before submission

- [ ] Keep this repository private and do not publish the figure or PoC.
- [ ] Have Taylor personally review the concise portal summary and confirm every factual statement.
- [ ] Reproduce once on a disposable test Mac with independent monitoring; do not replay on the production Mac.
- [ ] Test the latest public macOS release. As of 2026-10-27, Apple lists macOS 27.2 as released on 2026-10-26. This repository has not tested it.
- [ ] Begin with a narrow-query negative control, then perform at most one bounded broad-query attempt.
- [ ] Capture the exact OS build, System Events version, target-app version, privacy grants, timestamps, process IDs, and command hashes.
- [ ] Capture a sysdiagnose or the Apple-requested diagnostic profile at the reproduction timestamp.
- [ ] Record whether the responder stops when the requesting process exits.
- [ ] Redact account identifiers, message bodies, serial numbers, hardware UUIDs, and unrelated process information.
- [ ] Recheck the archive for credentials and private data.

## Suggested package

1. `report/apple-portal-summary.md`
2. `report/system-events-memory-exhaustion.md`
3. the disabled trigger and review-only harness from `poc/`
4. `evidence/sanitized/observations.json`
5. the two CPU-resource diagnostics and two jetsam reports in a separately encrypted attachment
6. a short screen recording only if a safe disposable-system reproduction is completed

Apple recommends a password-protected attachment for exploit material. Share the password through the report's private communication channel, not in a public repository.

## Submission framing

- Component: macOS `System Events` / Cocoa scripting bridge.
- Impact: local denial of service through uncontrolled resource consumption.
- Preconditions: local execution plus existing Automation and Accessibility authorization.
- Security relevance: an authorized or prompt-injected automation agent can trigger system-wide availability loss through a first-party responder.
- Unknowns: earliest affected build, behavior on 27.2, exact source defect, reliability across target apps, and bounty eligibility.

Submit through [Apple Security Research](https://security.apple.com/bounty/). Do not call the unrelated Mail resource-exhaustion entry in macOS 27.2 the fix for this issue; Apple's [27.2 security advisory](https://support.apple.com/en-us/149521) does not name `System Events`, AppleScript, or Automation for this trigger.
