# Observed effects and current state

## Observed during the incident

- Two separate `System Events` processes entered the same high-CPU recursive stack family after broad Outlook accessibility queries.
- The first CPU diagnostic recorded footprint endpoints of 15.48 MB and 187.76 GB, 111.742 seconds apart. That spacing is not the growth duration.
- A separate jetsam snapshot placed the first process at 222.5464 GiB 7.727 seconds after the second CPU endpoint. The final measured interval added 34.7864 GiB at a 4.5019 GiB/s mean, establishing a 4.5019 GiB/s lower bound on peak net growth; the exact peak remains unmeasured.
- Later jetsam accounting recorded a 253.9077 GiB lifetime maximum for the second process.
- The jetsam artifacts record widespread `low-swap` pressure. Their aggregate histories leave the simultaneous kill set unknown.
- The system experienced severe compression, swap, and transient disk-space pressure. User-file integrity status: no loss or corruption was reported; a comprehensive audit remains pending.

## State after recovery

At 12:38:18 CDT:

- no `System Events` process was running;
- system-wide memory free was 83%;
- encrypted swap use was 1,877.12 MB of 3,072 MB; and
- macOS remained 27.0.1 (26A434).

At 12:54:55 CDT, a second read-only check again found no `System Events` process. macOS still reported 27.0.1 (26A434), system-wide memory was 78% free, and encrypted swap use had fallen to 1,219.19 MB of 2,048 MB.

System state was preserved throughout the investigation: macOS, security patches, and permissions remained unchanged, and active reproduction stayed disabled.

## Unresolved or unassigned fields

- Prompt origin: unknown; earlier prompt provenance is unavailable.
- Network activity: incident-window telemetry was unavailable.
- Source-level defect and affected-release range: unknown pending Apple analysis.
- CVE, fixed release, and bounty decision: unassigned.
