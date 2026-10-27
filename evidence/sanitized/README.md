# Sanitized evidence

`observations.json` contains the numerical and stack-marker facts used by the report and figure. It is derived from four locally preserved Apple artifacts whose SHA-256 values are recorded in the file.

Raw CPU-resource and jetsam artifacts are intentionally outside this Git repository. They include machine and process metadata that is unnecessary for public review and should be provided only through Apple's private reporting channel.

The dataset contains discrete observations; continuous sampling was unavailable. `rpages` and `lifetimeMax` are multiplied by the report's 16,384-byte page size; GiB conversions use 1,073,741,824 bytes. The two recorded broad-query timestamps reproduce temporal lags. Source-level causation remains unresolved.

Run `python3 analysis/analyze_observations.py --json` from the repository root to reproduce the manuscript's descriptive statistics.
