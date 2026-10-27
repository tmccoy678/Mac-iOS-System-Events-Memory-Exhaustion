# Reproducible descriptive analysis

`analyze_observations.py` reads the sanitized evidence file and reproduces the manuscript's endpoint normalizations, growth multiples, endpoint-derived mean changes, physical-memory comparisons, CPU summary, and command-to-measurement lags.

```sh
python3 analysis/analyze_observations.py --json
python3 -m unittest tests/test_analysis.py -v
```

The analysis has two observed episodes and uses descriptive statistics. The endpoint-derived mean divides net endpoint change by elapsed time; intermediate allocation behavior was unmeasured.
