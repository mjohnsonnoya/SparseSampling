# Obsolete figure code

Nothing here generates a figure in the manuscript. It is kept so that an older
version of a figure can be explained or compared. The scripts were written for
the old folder layout: their paths are not maintained and most will not run
from here without editing.

| Item | What it was | Replaced by | When |
|---|---|---|---|
| `fig2_drift_correction_condensed.py` | Fig. 2 (3x4 layout), the manuscript figure from 2026-09-12 | `../fig2_drift_correction_standard.py` | 2026-11-15 |
| `fig2_drift_correction_4x4.py` | Fig. 2 in its 4x4 layout | the condensed script above | 2026-09-12 |
| `fig2_nudft_resampling_panel.py`, `fig2_inverse_fft_panel.py` | stand-alone drafts of the two resampling panels (August 2026) | merged into the 4x4 figure; now panels (e), (f) of Fig. 2 | 2026-09 |
| `fig_drift_correction_1d.py` | the first 1D drift correction figure (April 2026) | the 4x4 figure | 2026-08 |
| `fig_fourier_mode_sampling_equation.py`, `fig_fourier_resampling_mode.py` | April 2026 drafts for the resampling idea | set aside; never in the manuscript | 2026-08 |
| `driftcorr_method_comparison.py` | comparison of drift correction resampling methods (May 2026); a research check, never a manuscript figure | nothing | moved here 2026-11-16 |
| `fig2_caption_4x4.tex`, `fig2_caption_condensed.tex` | Fig. 2 caption drafts, staged before they were applied | the caption in `paper/main.tex` | 2026-09 |
| `rebuild_check/` | the 2026-11-13 exercise that rebuilt the Illustrator Figs. 1 and 3 byte for byte; `HANDOFF.md` documents what was learned | `../fig1_ss_overview.py`, `../fig3_drift_results.py`; its `regen_arrays.py` became `../data_bscco.py` | 2026-11-16 |
| `ASS_pipeline_panels/` | Illustrator file and panels for the first pipeline figure, built on BSCCO (not in git) | `../fig_ASS_pipeline_cebi.py` | 2026-09 |
| `outputs/` | old renders of the scripts above (not in git) | | |

Still useful from here: `rebuild_check/compare_pdfs.py old.pdf new.pdf` compares
two versions of a figure raster by raster and text span by text span (needs
PyMuPDF, which is not in `.venv`).
