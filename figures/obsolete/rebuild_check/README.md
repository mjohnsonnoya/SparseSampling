# Rebuild check: Fig. 1 and Fig. 3 as single matplotlib figures (2026-11-13)

Question answered: can the two Illustrator-assembled manuscript figures
(`paper/figure1_SS_overview.pdf`, `paper/drift_correction_results.pdf`) be rebuilt
in matplotlib with no visible difference and identical pixels?

Pipeline (run in this order; paths inside the scripts point at the scratchpad they
were developed in, change `OUT`/`S` if rerunning from here):
1. `regen_arrays.py`  (.venv)  notebook transcript: loads data, BPDN, two-pass drift
   correction, writes the single-panel PDFs exactly as the notebook did.
2. `extract_rasters.py` (needs PyMuPDF) pulls the 308x308 rasters out of those PDFs.
3. `build_fig.py fig1|fig3 out.pdf [--fix-3c]` places rasters, badges, scale bars and
   text at the coordinates in `*_geom.json` (read out of the Illustrator PDFs).
4. `compare_pdfs.py orig.pdf new.pdf` (needs PyMuPDF) byte-compares every embedded
   raster, every text span origin/size/font, and renders both pages at 300 dpi.

Results: all 10 (Fig. 1) and 6 (Fig. 3) embedded rasters byte-identical incl. alpha,
placed within 0.000 pt; all 28 and 17 text spans at 0.000 pt with the same font and
size (worst single glyph 0.56 pt); badges reproduced at their 75% opacity, bars and text opaque as in the originals.
Residual page-render differences are glyph anti-aliasing and Illustrator's CMYK
transparency group (vanish with color management off). Fonts in the rebuilt PDFs are
embedded TrueType Arial (fonttype 42).

Found along the way: Fig. 3(c) in the manuscript is the FT of the ground-truth map
(byte-identical to Fig. 1(h)), not of the reconstruction in 3(a); `rebuilt_fig3_fixed.pdf`
has the correct panel. The 308 px rasters are matplotlib's 100 dpi resampling of the
250 px data (hanning filter), so the published panels are not pixel-honest.
