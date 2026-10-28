# Figure provenance

`system-events-footprint.svg` and `system-events-footprint.png` visualize the first recorded `System Events` runaway on macOS 27.0.1 (26A434).

Two plotted endpoints come from the `Powerstats for: System Events` section of the preserved CPU-resource diagnostic:

- start: 15.48 MB at 11:12:37.749 (0.000 elapsed seconds);
- end: 187.76 GB at 11:14:29.491 (111.742 elapsed seconds);
- installed physical memory: 24 GiB, verified separately from `hw.memsize`.

A separate jetsam artifact supplies a third measurement. Its report time was 11:35:32.810, its `timeDelta` was 1,255,592 milliseconds, and their difference gives an inferred snapshot time of 11:14:37.218. At that point, PID 40483 had both `rpages` and `lifetimeMax` of 14,584,802 pages. At 16 KiB per page, this is an exact recorded accounting peak of 222.546417236328 GiB (238.957395968 GB).

The 111.742 seconds is endpoint spacing, not growth duration. The third point is 7.727 seconds after the 187.76 GB endpoint and 34.7864 GiB higher, yielding a final measured-interval mean of 4.5019 GiB/s. The instantaneous peak net-growth rate was at least that rate, but its exact value remains unmeasured. A constant-terminal-rate back-extrapolation estimates a 49.430194-second high-rate phase beginning at 11:13:47.787806; the estimate is intentionally omitted from the measured-data plot. Dashed connectors are visual guides, and intermediate values remain unmeasured. The source report uses `MB` and `GB` labels. For the log-scale calculation, the generator explicitly normalizes one reported GB to 1,024 reported MB and states that assumption on the figure.

Regenerate from the repository root:

```sh
Rscript figures/make_footprint_figure.R
```

Requirements are R with `ggplot2` and `cowplot`, plus `ragg` for the 300 dpi PNG. SVG export uses `svglite` when available and otherwise `pdftocairo` from Poppler.

The generator checks the key incident values before writing either output.
