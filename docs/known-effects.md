# Observed effects and current state

## Observed during the incident

- Two separate `System Events` processes entered the same high-CPU recursive stack family after broad Outlook accessibility queries.
- The first measured footprint grew from 15.48 MB to 187.76 GB in 111.742 seconds.
- Later jetsam accounting reached 222.5464 GiB for the first process and a 253.9077 GiB lifetime maximum for the second.
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
