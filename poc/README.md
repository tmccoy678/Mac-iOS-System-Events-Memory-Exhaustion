# Review-only reproduction material

This directory is for coordinated disclosure. It does not contain malware, persistence, exfiltration logic, or a production-safe active reproducer.

- `trigger.applescript.disabled.txt` records the minimal hazardous query shape as inert text.
- `bounded-repro.sh` performs a dry review only: it verifies that the defensive linter rejects the trigger. It never invokes `osascript`.

Run the safe review from the repository root:

```sh
sh poc/bounded-repro.sh
```

Do not rename or execute the disabled trigger on a production Mac. An active vendor reproduction should be performed once on a disposable test system with an independent watchdog, a second control channel, strict resource limits, and a plan to terminate both the caller and the newly launched `System Events` process.
