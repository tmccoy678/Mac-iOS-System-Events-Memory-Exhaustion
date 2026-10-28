# Reproducible descriptive analysis

`analyze_observations.py` reads the sanitized evidence file and reproduces the manuscript's endpoint normalizations, growth multiples, CPU-endpoint spacing, final measured-interval rate, physical-memory comparisons, CPU summary, and command-to-measurement lags.

```sh
python3 analysis/analyze_observations.py --json
python3 -m unittest tests/test_analysis.py -v
```

The analysis has two observed episodes and uses descriptive statistics. The 111.742 seconds in Episode 1 is spacing between CPU-diagnostic endpoints, not growth duration. A separate jetsam snapshot adds a third point 7.727 seconds after the second CPU endpoint: 34.7864 GiB of net growth at a 4.5019 GiB/s interval mean. That mean is a lower bound on peak net growth; intermediate allocation behavior and the exact peak were unmeasured.
