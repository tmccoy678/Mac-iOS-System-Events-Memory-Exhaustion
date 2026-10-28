# Sanitized evidence

`observations.json` contains the numerical and stack-marker facts used by the report and figure. It is derived from four locally preserved Apple artifacts whose SHA-256 values are recorded in the file.

Raw CPU-resource and jetsam artifacts are intentionally outside this Git repository. They include machine and process metadata that is unnecessary for public review and should be provided only through Apple's private reporting channel.

The dataset contains discrete observations; continuous sampling was unavailable. `rpages` and `lifetimeMax` are multiplied by the report's 16,384-byte page size; GiB conversions use 1,073,741,824 bytes and decimal-GB conversions use 1,000,000,000 bytes. For the first process, both page counts equal 14,584,802, supporting an exact recorded accounting peak of 222.546417236328 GiB (238.957395968 GB). This does not measure the instantaneous peak net-growth rate.

The analysis derives a 49.430194-second high-rate-phase estimate by extrapolating the final measured-interval mean backward from the jetsam snapshot to the 15.48 MB baseline. The value is a constant-rate model, not a recorded duration. The two recorded broad-query timestamps reproduce temporal lags. Source-level causation remains unresolved.

Run `python3 analysis/analyze_observations.py --json` from the repository root to reproduce the manuscript's descriptive statistics.
