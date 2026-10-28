# Reproducible descriptive analysis

`analyze_observations.py` reads the sanitized evidence file and reproduces the manuscript's endpoint normalizations, growth multiples, CPU-endpoint spacing, final measured-interval rate, recorded jetsam peak, constant-terminal-rate duration model, physical-memory comparisons, CPU summary, and command-to-measurement lags.

```sh
python3 analysis/analyze_observations.py --json
python3 -m unittest tests/test_analysis.py -v
```

The analysis has two observed episodes and uses descriptive statistics. The 111.742 seconds in Episode 1 is spacing between CPU-diagnostic endpoints, not growth duration. A separate jetsam snapshot adds a third point 7.727 seconds after the second CPU endpoint: 34.7864 GiB of net growth at a 4.501930534 GiB/s interval mean. That mean is a lower bound on the instantaneous peak net-growth rate.

The first jetsam record reports both `rpages` and `lifetimeMax` as 14,584,802 pages. At 16,384 bytes per page, the exact recorded accounting peak is 238,957,395,968 bytes, 222.546417236328 GiB, or 238.957395968 decimal GB. The instantaneous peak rate and intermediate trajectory remain unmeasured.

For a close duration estimate, the script applies one explicit model:

```text
(222.546417236328 GiB - 15.48 / 1,024 GiB) / 4.501930534 GiB/s
= 49.430194 seconds
```

Subtracting that modeled duration from the inferred 11:14:37.218 snapshot time yields a modeled onset of 11:13:47.787806. This extrapolates the terminal measured-interval mean backward at a constant rate; it is not a direct observation or a confidence interval, and nonlinear allocation could produce a different duration.
