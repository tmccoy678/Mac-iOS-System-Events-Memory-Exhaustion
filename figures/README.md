# Figure provenance

`system-events-footprint.svg` and `system-events-footprint.png` visualize the first recorded `System Events` runaway on macOS 27.0.1 (26A434).

Two plotted endpoints come from the `Powerstats for: System Events` section of the preserved CPU-resource diagnostic:

- start: 15.48 MB at 11:12:37.749 (0.000 elapsed seconds);
- end: 187.76 GB at 11:14:29.491 (111.742 elapsed seconds);
- installed physical memory: 24 GiB, verified separately from `hw.memsize`.

A separate jetsam artifact supplies a third measurement. Its report time was 11:35:32.810, its `timeDelta` was 1,255,592 milliseconds, and their difference gives an inferred snapshot time of 11:14:37.218. At that point, PID 40483 had 14,584,802 pages at 16 KiB per page, or 222.546417236328 GiB.

The 111.742 seconds is endpoint spacing, not growth duration. The third point is 7.727 seconds after the 187.76 GB endpoint and 34.7864 GiB higher, yielding a final measured-interval mean of 4.5019 GiB/s. Peak net growth was at least that rate; its exact value remains unmeasured. Dashed connectors are visual guides, and intermediate values remain unmeasured. The source report uses `MB` and `GB` labels. For the log-scale calculation, the generator explicitly normalizes one reported GB to 1,024 reported MB and states that assumption on the figure.

Regenerate from the repository root:

```sh
Rscript figures/make_footprint_figure.R
```

Requirements are R with `ggplot2` and `cowplot`, plus `ragg` for the 300 dpi PNG. SVG export uses `svglite` when available and otherwise `pdftocairo` from Poppler.

The generator checks the key incident values before writing either output.
