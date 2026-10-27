# Figure provenance

`system-events-footprint.svg` and `system-events-footprint.png` visualize the first recorded `System Events` runaway on macOS 27.0.1 (26A434).

The plotted endpoints come from the `Powerstats for: System Events` section of the preserved CPU-resource diagnostic:

- start: 15.48 MB at 11:12:37.749 (0.000 elapsed seconds);
- end: 187.76 GB at 11:14:29.491 (111.742 elapsed seconds);
- installed physical memory: 24 GB, verified separately from `hw.memsize`.

Only the two endpoints were recorded. The dashed connector helps the eye compare them; it is not an interpolation or measured time series. The source report uses `MB` and `GB` labels. For the log-scale calculation, the generator explicitly normalizes one reported GB to 1,024 reported MB and states that assumption on the figure. The growth callout is deliberately rounded to `>12,000x`.

Regenerate from the repository root:

```sh
Rscript figures/make_footprint_figure.R
```

Requirements are R with `ggplot2` and `cowplot`, plus `ragg` for the 300 dpi PNG. SVG export uses `svglite` when available and otherwise `pdftocairo` from Poppler.

The generator checks the key incident values before writing either output.
