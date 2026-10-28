#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(cowplot)
})

args <- commandArgs(trailingOnly = FALSE)
script_arg <- grep("^--file=", args, value = TRUE)
if (length(script_arg) != 1) {
  stop("Run this file with Rscript so repository-relative paths can be resolved.")
}

script_path <- normalizePath(sub("^--file=", "", script_arg), mustWork = TRUE)
figure_dir <- dirname(script_path)
data_path <- file.path(figure_dir, "data", "first-run-measurements.csv")

observations <- read.csv(data_path, stringsAsFactors = FALSE, na.strings = "")
measurements <- subset(observations, kind == "measurement")
physical_mib <- subset(observations, kind == "reference")$normalized_mib_assuming_1024[[1]]

if (nrow(measurements) != 3 || any(!is.finite(measurements$normalized_mib_assuming_1024))) {
  stop("Expected exactly three finite footprint measurements.")
}

start_mib <- measurements$normalized_mib_assuming_1024[measurements$label == "CPU start"]
end_mib <- measurements$normalized_mib_assuming_1024[measurements$label == "CPU end"]
snapshot_mib <- measurements$normalized_mib_assuming_1024[measurements$label == "Jetsam snapshot"]
endpoint_spacing_seconds <- measurements$elapsed_seconds[measurements$label == "CPU end"]
snapshot_elapsed_seconds <- measurements$elapsed_seconds[measurements$label == "Jetsam snapshot"]
start_time <- measurements$diagnostic_time[measurements$label == "CPU start"]
end_time <- measurements$diagnostic_time[measurements$label == "CPU end"]
snapshot_time <- measurements$diagnostic_time[measurements$label == "Jetsam snapshot"]
growth_ratio <- end_mib / start_mib
physical_gib <- physical_mib / 1024
end_gib <- end_mib / 1024
snapshot_gib <- snapshot_mib / 1024
final_interval_seconds <- snapshot_elapsed_seconds - endpoint_spacing_seconds
final_interval_growth_gib <- snapshot_gib - end_gib
final_interval_rate_gib_per_second <- final_interval_growth_gib / final_interval_seconds

if (
  growth_ratio <= 12000 ||
  abs(endpoint_spacing_seconds - 111.742) > 1e-9 ||
  abs(snapshot_elapsed_seconds - 119.469) > 1e-9 ||
  abs(final_interval_seconds - 7.727) > 1e-9 ||
  abs(final_interval_rate_gib_per_second - 4.501930534) > 1e-9 ||
  !identical(start_time, "11:12:37.749") ||
  !identical(end_time, "11:14:29.491") ||
  !identical(snapshot_time, "11:14:37.218") ||
  abs(physical_gib - 24) > 1e-9 ||
  abs(end_gib - 187.76) > 1e-9 ||
  abs(snapshot_gib - 222.546417236328) > 1e-9
) {
  stop("Input values do not match the verified incident measurements.")
}

colors <- c(
  navy = "#25364D",
  blue = "#2563EB",
  red = "#C81E1E",
  purple = "#7C3AED",
  orange = "#A24A00",
  grey = "#667085",
  grid = "#D0D5DD",
  ink = "#101828",
  paper = "#FFFFFF"
)

base_theme <- theme_minimal(base_family = "Helvetica", base_size = 12) +
  theme(
    plot.background = element_rect(fill = colors[["paper"]], color = NA),
    panel.background = element_rect(fill = colors[["paper"]], color = NA),
    panel.grid.minor = element_blank(),
    panel.grid.major.x = element_blank(),
    panel.grid.major.y = element_line(color = colors[["grid"]], linewidth = 0.35),
    axis.title = element_text(color = colors[["ink"]], face = "bold"),
    axis.text = element_text(color = colors[["ink"]]),
    plot.title = element_text(color = colors[["ink"]], face = "bold", size = 14),
    plot.subtitle = element_text(color = colors[["grey"]], size = 10.5, margin = margin(b = 9)),
    plot.margin = margin(10, 14, 10, 10),
    legend.position = "none"
  )

measurements$point_color <- ifelse(
  measurements$label == "CPU start",
  colors[["blue"]],
  ifelse(measurements$label == "CPU end", colors[["red"]], colors[["purple"]])
)

p_log <- ggplot(measurements, aes(x = elapsed_seconds, y = normalized_mib_assuming_1024)) +
  geom_hline(
    yintercept = physical_mib,
    color = colors[["orange"]],
    linewidth = 0.9,
    linetype = "22"
  ) +
  geom_line(color = colors[["grey"]], linewidth = 1.1, linetype = "33") +
  geom_point(aes(fill = point_color), shape = 21, color = colors[["paper"]], stroke = 1.2, size = 6) +
  scale_fill_identity() +
  annotate(
    "text", x = 3.5, y = 23,
    label = "15.48 MB", hjust = 0, vjust = 0,
    color = colors[["blue"]], fontface = "bold", size = 4.2
  ) +
  annotate(
    "text", x = endpoint_spacing_seconds - 2.5, y = 145000,
    label = "187.76 GB", hjust = 1, vjust = 1,
    color = colors[["red"]], fontface = "bold", size = 4.2
  ) +
  annotate(
    "text", x = 98, y = 220000,
    label = "222.55 GiB\ninferred 11:14:37.218", hjust = 1, vjust = 0.5,
    color = colors[["purple"]], fontface = "bold", size = 4.2
  ) +
  annotate(
    "label", x = endpoint_spacing_seconds * 0.50, y = 920,
    label = "111.742 s endpoint spacing\ngrowth duration unmeasured",
    color = colors[["ink"]], fill = colors[["paper"]],
    linewidth = 0, fontface = "bold", size = 3.8, lineheight = 1.05
  ) +
  annotate(
    "label", x = 96, y = 5700,
    label = "+34.7864 GiB / 7.727 s\n= 4.50 GiB/s mean",
    color = colors[["purple"]], fill = colors[["paper"]],
    linewidth = 0, fontface = "bold", size = 3.8, lineheight = 1.05
  ) +
  annotate(
    "text", x = snapshot_elapsed_seconds, y = physical_mib * 1.14,
    label = "24 GiB physical RAM", hjust = 1, vjust = 0,
    color = colors[["orange"]], fontface = "bold", size = 3.6
  ) +
  scale_x_continuous(
    breaks = c(0, endpoint_spacing_seconds),
    labels = c(
      paste0("0\n", start_time),
      paste0("111.742\n", end_time)
    ),
    limits = c(-3, snapshot_elapsed_seconds + 3),
    expand = expansion(mult = c(0, 0))
  ) +
  scale_y_log10(
    breaks = c(10, 100, 1024, 10240, 102400, 307200),
    labels = c("10 MB", "100 MB", "1 GB", "10 GB", "100 GB", "300 GB"),
    limits = c(10, 307200),
    expand = expansion(mult = c(0.02, 0.02))
  ) +
  labs(
    title = "Recorded footprint measurements",
    subtitle = "The inferred 11:14:37.218 jetsam snapshot narrows the final interval to 7.727 seconds",
    x = "Elapsed seconds from first CPU endpoint and diagnostic timestamp",
    y = "System Events footprint (log scale)"
  ) +
  base_theme

comparison <- data.frame(
  label = factor(c("Physical RAM", "Jetsam\nsnapshot"), levels = c("Physical RAM", "Jetsam\nsnapshot")),
  gib = c(physical_gib, snapshot_gib),
  fill = c(colors[["navy"]], colors[["purple"]])
)

p_compare <- ggplot(comparison, aes(x = label, y = gib, fill = fill)) +
  geom_col(width = 0.62) +
  geom_text(
    aes(label = ifelse(label == "Physical RAM", "24 GiB", "222.55 GiB")),
    vjust = -0.55, color = colors[["ink"]], fontface = "bold", size = 4
  ) +
  scale_fill_identity() +
  scale_y_continuous(
    breaks = c(0, 50, 100, 150, 200, 250),
    limits = c(0, 250),
    expand = expansion(mult = c(0, 0))
  ) +
  labs(
    title = "Snapshot versus installed memory",
    subtitle = "The jetsam snapshot was 9.3x physical RAM",
    x = NULL,
    y = "Memory (GiB)"
  ) +
  base_theme +
  theme(
    axis.text.x = element_text(face = "bold"),
    panel.grid.major.x = element_blank()
  )

panels <- plot_grid(
  p_log,
  p_compare,
  nrow = 1,
  rel_widths = c(1.72, 1),
  align = "h",
  axis = "tb"
)

figure <- ggdraw() +
  draw_grob(
    grid::rectGrob(gp = grid::gpar(fill = colors[["paper"]], col = NA)),
    x = 0, y = 0, width = 1, height = 1
  ) +
  draw_label(
    "System Events: final measured-interval mean was 4.50 GiB/s",
    x = 0.035, y = 0.975, hjust = 0, vjust = 1,
    fontfamily = "Helvetica", fontface = "bold", size = 21,
    color = colors[["ink"]]
  ) +
  draw_label(
    "Observed on macOS 27.0.1 (26A434), System Events 1.3.6, Mac17,2 with 24 GiB physical memory",
    x = 0.035, y = 0.912, hjust = 0, vjust = 1,
    fontfamily = "Helvetica", size = 11.5,
    color = colors[["grey"]]
  ) +
  draw_plot(panels, x = 0.015, y = 0.09, width = 0.97, height = 0.78) +
  draw_label(
    "The CPU diagnostic recorded two endpoints 111.742 seconds apart; this spacing is not the growth duration. A separate jetsam snapshot adds a third point.\nDashed connectors are visual guides; intermediate trajectory and exact peak remain unmeasured. GB/MB normalization uses 1 GB = 1,024 MB.",
    x = 0.035, y = 0.018, hjust = 0, vjust = 0,
    fontfamily = "Helvetica", size = 9.1,
    color = colors[["grey"]]
  )

svg_path <- file.path(figure_dir, "system-events-footprint.svg")
png_path <- file.path(figure_dir, "system-events-footprint.png")

if (requireNamespace("svglite", quietly = TRUE)) {
  ggsave(
    svg_path, figure, width = 12, height = 6.75, units = "in",
    device = svglite::svglite, bg = colors[["paper"]]
  )
} else {
  pdftocairo <- Sys.which("pdftocairo")
  if (!nzchar(pdftocairo)) {
    stop("SVG export requires either the R package 'svglite' or the 'pdftocairo' command.")
  }

  local({
    intermediate_pdf <- tempfile(
      pattern = ".system-events-footprint-",
      tmpdir = figure_dir,
      fileext = ".pdf"
    )
    on.exit(unlink(intermediate_pdf), add = TRUE)
    ggsave(
      intermediate_pdf, figure, width = 12, height = 6.75, units = "in",
      device = grDevices::pdf, bg = colors[["paper"]], useDingbats = FALSE
    )
    conversion_output <- system2(
      pdftocairo,
      c("-svg", intermediate_pdf, svg_path),
      stdout = TRUE,
      stderr = TRUE
    )
    conversion_status <- attr(conversion_output, "status")
    if (!is.null(conversion_status) && conversion_status != 0) {
      stop(paste(c("pdftocairo SVG export failed:", conversion_output), collapse = "\n"))
    }
    if (!file.exists(svg_path) || file.info(svg_path)$size == 0) {
      stop("pdftocairo completed without producing a non-empty SVG file.")
    }
  })
}

if (requireNamespace("ragg", quietly = TRUE)) {
  ggsave(
    png_path, figure, width = 12, height = 6.75, units = "in", dpi = 300,
    device = ragg::agg_png, bg = colors[["paper"]]
  )
} else {
  ggsave(
    png_path, figure, width = 12, height = 6.75, units = "in", dpi = 300,
    device = "png", type = "cairo", bg = colors[["paper"]]
  )
}

cat(sprintf("Wrote %s\nWrote %s\n", basename(svg_path), basename(png_path)))
