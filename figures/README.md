# Figures

**The rule of this folder:** a script at the top level generates a figure the
manuscript uses. Shared tools sit beside them, work for figures not yet in the
paper is in `in_progress/`, superseded code is in `obsolete/`, and nothing
generated is kept next to code: it all goes to `out/`.

## Which code makes which figure

Figure numbers follow `paper/main.tex` as of 2026-11-16. Run every command from
the repository root.

| Fig. | PDF in `paper/` | Made by | Data | Command |
|---|---|---|---|---|
| 1 | `fig1_ss_overview.pdf` | `fig1_ss_overview.py` | `data_bscco.py` | `.venv/bin/python figures/fig1_ss_overview.py` |
| 2 | `fig2_drift_correction_standard.pdf` | `fig2_drift_correction_standard.py` | none (self-contained toy model) | `.venv/bin/python figures/fig2_drift_correction_standard.py` |
| 3 | `fig3_drift_results.pdf` | `fig3_drift_results.py` | `data_bscco.py` | `.venv/bin/python figures/fig3_drift_results.py` |
| 4 | `SNR_Illustration.pdf` | **no script yet**: `notebooks/Sparse_sampling_figure_plot_for_40_nm_map.ipynb`, then Illustrator | BSCCO full-grid map | |
| 5 | `snr_vs_sparsity.pdf` | **no script yet**: the same notebook | BSCCO sampling-fraction series | |
| 6 | `figure3_ASS.pdf` | **no script yet**: `notebooks/Adaptive_sparse_sampling.ipynb`, then Illustrator | CeBi map `2019-07-11-002 LIY local corr new.spy` | |
| 7 | `figure_ASS_pipeline_cebi_topo.pdf` | `fig_ASS_pipeline_cebi.py` | `data/CeBi_2019_raw/2019-07-15/2019-07-15_CeBi_00017.sxm` | `.venv/bin/python figures/fig_ASS_pipeline_cebi.py lowpass data/CeBi_2019_raw/2019-07-15/2019-07-15_CeBi_00017.sxm --paper` |

Checked on 2026-11-16 by rendering both and comparing pixels:

- Figs. 1, 2 and 7: the command above reproduces the PDF in `paper/` exactly.
- Fig. 3: the script is **ahead of the manuscript**. It holds the J16 candidate
  (drift field from the co-acquired topography, cropped, Fourier panels zoomed),
  which is not pushed yet. The PDF in `paper/` came from the previous revision
  of the script. The note at the top of the script says the same.
- Figs. 4 to 6 were located in their notebooks by the 2026-11-13 inventory
  (`obsolete/rebuild_check/HANDOFF.md`, Section 2); they have not been rebuilt.

`data_bscco.py` is the one data step behind Figs. 1 and 3: instrument files in,
arrays out, about 2 s, nothing cached. Its docstring lists the input files and
what each returned array is.

## Layout

```
figures/
  README.md                          this file
  figstyle.py                        house style: Arial, final width, unsampled images, scale bars, colorbars
  check_figure.py                    the gate: audits a PDF against the Hoffman checklist
  data_bscco.py                      data behind Figs. 1 and 3
  fig1_ss_overview.py                Fig. 1
  fig2_drift_correction_standard.py  Fig. 2
  fig3_drift_results.py              Fig. 3
  fig_ASS_pipeline_cebi.py           Fig. 7 (not yet on the house standard)
  in_progress/                       CeBi SNR work for a figure not yet in the paper (J27)
  obsolete/                          superseded scripts, with obsolete/README.md saying why
  out/                               everything generated (not in git); out/check/ holds the gate's renders
```

When a script stops generating a manuscript figure, move it to `obsolete/` and
add a line to `obsolete/README.md`. When a new one starts, add a row to the
table above.

## The loop for changing a figure

The figure rules are Sec. V and Appendix A of J. E. Hoffman, "How To Write a
Scientific Paper" (https://hoffman.physics.harvard.edu/Hoffman-Example-Paper.pdf,
copy in `references/`). Figures are code only: no Illustrator pass.

1. **Edit the script** for that figure (it imports `figstyle` as `fs`).
2. **Build.** Run the command from the table. Output lands in `figures/out/`.
   `fs.save` refuses a figure that is not 3.375 or 7.0 in wide or that has
   text under 6 pt.
3. **Gate.** `.venv/bin/python figures/check_figure.py figures/out/<name>.pdf`.
   No FAIL may remain; every WARN gets a decision.
4. **Look.** Open `figures/out/check/<name>.png` at 100% zoom (that is print
   size) and tick the "needs eyes" list the gate prints, against the caption.
5. **Promote.** Pull `paper/`, copy the PDF in, give the before/after report,
   commit and push after approval (see `CLAUDE.md`, "Manuscript workflow").

Audit everything the manuscript includes: `check_figure.py --paper`.

## Who enforces what

| Hoffman rule | By construction (`figstyle`) | Checked (`check_figure`) |
|---|---|---|
| Build at the final column width | `new_figure('col' or 'full')`; `save` refuses other widths | `width`, using the width `main.tex` includes the file at |
| Vector format; Arial throughout | rcParams: Arial text and math, TrueType embedding; import fails without Arial | `fonts`: Type 3, non-Arial or unembedded fonts fail |
| No font under 6 pt in the printed figure | `save` refuses | `font size`, at print scale |
| Honest pixels, no interpolation | `image()` embeds the data array itself | `pixels`: embedded raster sizes must equal the data shapes `save` records in the PDF keywords |
| Same-palette images share a colorbar | `shared_clim()` + `colorbar()` | eyes |
| Scale bar with its number on every image set | `scalebar()` in data units | eyes |
| No red-green combinations | | `red-green`: color pairs that merge under simulated deuteranopia |
| Data-ink, no chart-junk, horizontal words, axes with units, full legend | | eyes |
| Caption explains every mark, analysis step and error bar; STM setup, bias modulation, temperature, field; citations | | eyes; the gate prints the caption and notes whether setup and temperature appear |

## Two departures from the guide's Appendix A

- **`rasterized=True` is not used for data images.** The guide recommends it,
  but under matplotlib 3.10 it resamples the image to the output dpi, and with
  fewer than 3 output pixels per data pixel it smooths while doing so (measured:
  a 256-color image gains thousands of new colors). That is how the 250 px maps
  became blurred 308 px rasters. `fs.image` reaches the guide's stated goal by
  embedding the array unsampled (`interpolation='none'`, not rasterized).
  macOS Preview still smooths images on screen; Acrobat and Illustrator do not.
- **Sub/superscripts under 6 pt are a WARN, not a FAIL.** This is an
  interpretation, not Jenny's stated rule; the test is in `check_figure.py`
  (runs of one or two characters).

## Moving a notebook figure onto the standard (Figs. 4 to 6)

1. Put the data step in a function (as `data_bscco.py` does), so the figure does
   not depend on notebook cell order.
2. Build with `fs.new_figure('col' | 'full', height)`; draw images with
   `fs.image(ax, data, extent=...)` and limits from `fs.shared_clim`.
3. Save with `fs.save(fig, name)`, never `bbox_inches='tight'`.
4. Run the gate, look, then add the row to the table above.
