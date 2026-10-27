# Observed effects and current state

## Observed during the incident

- Two separate `System Events` processes entered the same high-CPU recursive stack family after broad Outlook accessibility queries.
- The first measured footprint grew from 15.48 MB to 187.76 GB in 111.742 seconds.
- Later jetsam accounting reached 222.5464 GiB for the first process and a 253.9077 GiB lifetime maximum for the second.
- The jetsam artifacts record widespread `low-swap` pressure. Because these are aggregate histories, they do not identify a reliable list of applications killed at the same moment.
- The system experienced severe compression, swap, and transient disk-space pressure. The available evidence does not identify lost or corrupted user files.

## State after recovery

At 12:38:18 CDT:

- no `System Events` process was running;
- system-wide memory free was 83%;
- encrypted swap use was 1,877.12 MB of 3,072 MB; and
- macOS remained 27.0.1 (26A434).

At 12:54:55 CDT, a second read-only check again found no `System Events` process. macOS still reported 27.0.1 (26A434), system-wide memory was 78% free, and encrypted swap use had fallen to 1,219.19 MB of 2,048 MB.

No operating-system update, security patch, permission change, or active reproducer was applied during this investigation.

## Findings not supported by the evidence

- malware installation or persistence;
- a malicious Outlook message or hidden prompt;
- 187.76 GB of Outlook data read or transmitted;
- network exfiltration;
- privilege escalation or code execution;
- a public CVE or confirmed fixed release; or
- bounty eligibility.
