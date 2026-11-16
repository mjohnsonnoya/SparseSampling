# Handoff: rebuilding the manuscript figures in matplotlib

Written 2026-11-13 after proving that Fig. 1 (`paper/figure1_SS_overview.pdf`) and
Fig. 3 (`paper/drift_correction_results.pdf`), both assembled by hand in Illustrator,
can be rebuilt as single matplotlib figures with byte-identical image pixels and
text at the same coordinates. This document collects everything learned on the way,
for the planned reorganization of how figures are generated and how reviewer
feedback turns into figure updates.

Read alongside `README.md` in this folder (what each script does) and
`reports/Agent friendly vector figure tools.md` (why code-first beats a GUI editor
for agent-driven figure work). Jenny's own figure rules are in
`references/Hoffman-Example-Paper.pdf`, Section V and Appendix A.

---

## 1. What was proven, in numbers

| Check | Fig. 1 | Fig. 3 |
|---|---|---|
| Embedded rasters byte-identical to the Illustrator file (RGB and alpha) | 10 of 10 | 6 of 6 |
| Raster placement error | 0.000 pt | 0.000 pt |
| Text spans at identical origin, font and size | 28 of 28 | 17 of 17 |
| Worst single glyph offset (the Å in "0.78 Å⁻¹") | 0.56 pt | 0.56 pt |
| Page pixels differing by more than 64 levels, poppler 150 dpi | 0.14% | 0.28% |
| Page pixels differing by more than 16 levels, poppler 150 dpi | 0.30% | 0.56% |
| Fonts in rebuilt PDF | CID TrueType Arial, embedded, subset | same |

What remains different and why:

- Glyph edges. Two PDF writers rasterize the same Arial outlines with slightly
  different anti-aliasing. Ink centroids agree to 0.01 to 0.04 pt.
- Illustrator's page carries a transparency group in DeviceCMYK (the document was in
  CMYK mode). Color-managed renderers push the panel colors through CMYK and back,
  shifting them by a few levels. With MuPDF color management off, panel interiors
  agree to within 2 levels in more than 99% of pixels.
- Illustrator's "black" is CMYK 0/0/0/1, which viewers show as (35,31,32), hex
  231f20. The rebuild uses that RGB value directly.
- The Å glyph and the tail of one title ("Reconstructed Map", right column of Fig. 3)
  sit 0.48 to 0.56 pt off because Illustrator applied its own kerning or tracking.
  Sub-point, invisible at print size.

Full regeneration from the raw `.3ds` and `.sxm` files (loading, BPDN, two drift
passes, 12 panel PDFs) takes about 2 seconds. There is no reason to cache panels.

---

## 2. Inventory of the figures `paper/main.tex` includes

| File | Made with | Fonts (pdffonts) | Source |
|---|---|---|---|
| `figure1_SS_overview.pdf` | Illustrator 30.2, assembled from matplotlib panel PDFs | TrueType Arial, embedded | notebook `Sparse_sampling_figure_plot_for_40_nm_map.ipynb`, cells 20, 21, 22, 26, 27 |
| `fig2_drift_correction_condensed.pdf` | matplotlib script | Type 3 Arial + Type 3 DejaVu Sans | `figures/fig2_drift_correction_condensed.py` |
| `drift_correction_results.pdf` | Illustrator | TrueType Arial, embedded | same notebook, cells 26 and 59 |
| `SNR_Illustration.pdf` | passed through an editor | TrueType Arial, embedded | notebook cell 18 |
| `snr_vs_sparsity.pdf` | matplotlib (notebook cell 17) | Type 3 DejaVu Sans only, no Arial | notebook cell 17 |
| `figure3_ASS.pdf` | passed through an editor | TrueType Arial, embedded | `Adaptive_sparse_sampling.ipynb` cells 15 to 33 |
| `figure_ASS_pipeline_cebi_topo.pdf` | matplotlib script | Type 3 Arial | `figures/fig_ASS_pipeline_cebi.py` |

Three PDFs carry Type 3 fonts because no script sets `pdf.fonttype = 42` and
matplotlib 3.10.8 (the version in `.venv`) defaults to 3. Publisher checks can reject
Type 3. One line in a shared style block fixes it (Section 6).

---

## 3. How the Illustrator figures are built (the geometry to preserve)

All numbers are PDF points, origin top-left, read with PyMuPDF and stored in
`figure1_SS_overview_geom.json` and `drift_correction_results_geom.json` (images,
text spans, drawings, with per-path opacity added).

Fig. 1, page 676.659 × 337.071 pt:

- Four columns of 160 pt cells starting at x = 0, 160, 320, 480; two rows starting
  at y = 14.81 and 174.81. Each image is 150.24 pt square, inset 4.88 pt inside its
  cell. The sparse map (b) is 149.27 pt because Illustrator trimmed its transparent
  1 px border (306 px instead of 308).
- Column titles: Arial Bold 12 pt, baseline y = 10.29, color 231f20.
- Badges: 75% opaque rectangles drawn as form objects, 20.75 pt tall. Orange
  (0.9703, 0.5792, 0.1146), 60 pt wide, behind "(b) -22 mV" style labels. Gray
  (0.6553, 0.6636, 0.6735), 22.95 pt wide, behind bare letters. Labels are white
  Arial Bold 12 pt with baseline 15 pt below the badge top.
- Scale bars: 30 pt × 1.87 pt rectangles. White on real-space panels, 231f20 on FT
  panels. 30 pt on a 150.24 pt panel of 40 nm is 8.0 nm, so the bar is honest.
  Labels "8 nm" and "0.78 Å" in Arial 14 pt, the "-1" superscript in Arial 8.16 pt
  raised 4.66 pt. In panel (b) the white label and bar carry a 1 pt dark outline.
- Colorbars: 19 × 154 px rasters placed at x = 649.31, 17.69 pt wide, 143.38 and
  144.49 pt tall, with "H" and "L" in Arial 12 pt.
- White background rectangles under every cell and colorbar. Invisible on a white
  page; drop them.

Fig. 3, page 359.688 × 350.789 pt: same cell size and badge rules, two columns at
x = 36.66 and 196.66, rows at y = 29.21 and 189.21, colorbars at x = 9.31. Two-line
title on the right column with baselines at y = 10.29 and 24.69.

Everything in both figures is opaque except the badges. An earlier pass of this work
reported some labels at 75%; that was a bug in a content-stream parser that ignored
the PDF q/Q state stack. Verified correct afterwards.

---

## 4. Where the 308 px rasters came from (and why they are not pixel-honest)

The notebook makes each panel with `stmpy.driftcorr.quick_plot(..., rasterized=True)`
and saves with `plt.savefig(path, bbox_inches='tight')`. The chain:

1. `quick_plot` creates a 4 × 4 in figure. Default subplot margins leave a 3.1 × 3.08
   in axes; `set_aspect(1)` on square data shrinks it to 3.08 × 3.08 in.
2. `rasterized=True` sends the image through the mixed-mode renderer at the figure
   dpi (100), so the 250 × 250 data becomes a 308 × 308 raster.
3. matplotlib 3.10 defaults `image.interpolation = 'auto'` and
   `image.interpolation_stage = 'auto'`: for upsampling by less than 3× it applies a
   Hanning filter in RGBA space. Result: zero repeated rows, 13,387 distinct colors in
   a 256-color colormap, data blurred by about one pixel. This is the "dishonest
   interpolation" Jenny's guide warns about, happening before Illustrator ever saw it.
4. The sparse map has NaN at unmeasured pixels. NaN maps to the colormap's "bad"
   color, transparent, so the raster is RGBA with an alpha mask (93,116 pixels below
   255), and its outer transparent ring makes it 306 px.
5. Colorbars come from a 0.25 × 2 in figure with `ColorbarBase`; the gradient is a
   pcolormesh that matplotlib rasterizes automatically when the colormap has more than
   50 entries, giving 19 × 154 px.
6. Illustrator re-encoded grayscale rasters as Indexed color (lossless) and scaled
   each panel to 150.24 pt, which is why `pdfimages -list` shows 148 ppi.

For the real rebuild: embed the data arrays at native resolution with
`imshow(arr, cmap=..., vmin=..., vmax=..., interpolation='none')` and no
`rasterized=True`. The PDF then carries the 250 × 250 (or 241 × 241) array itself,
every data pixel is one PDF image sample, and the viewer does the scaling. Note that
macOS Preview smooths images on screen; Acrobat and Illustrator show them crisp.
Jenny's Appendix A says the same.

---

## 5. matplotlib mechanics that made byte identity possible

- Unsampled embedding. `imshow(rgba, interpolation='none')` on an artist that is not
  rasterized makes the PDF backend write the array as-is (the `_check_unsampled_image`
  path). Any other interpolation value resamples at save time.
- Storage orientation. matplotlib stores image samples bottom-up with a negative
  `d` in the PDF image matrix; Illustrator stores top-down. Same picture, different
  bytes. `imshow(arr[::-1], origin='lower', interpolation='none')` yields top-down
  storage. Only matters for byte comparisons.
- Placing things in points. Build the figure at the page size in inches
  (`figsize=(W/72, H/72)`), place image axes with `fig.add_axes([x0/W, 1-y1/H,
  w/W, h/H])`, and draw text and patches with `transform=fig.dpi_scale_trans` at
  `(x/72, (H-y)/72)`. Text with `va='baseline'` lands on the PDF text origin exactly
  (0.000 pt in every span).
- Path effects convert text to outlines. `withStroke` makes the glyphs paths, so the
  label stops being text. For an outlined label, draw a `color='none'` copy with a
  `Stroke` effect underneath and the plain text on top.
- Figure-level patches. `fig.add_artist(Rectangle(...))` with zorder above the axes
  draws on top of images; anything added later with a lower zorder is hidden, which is
  how the colorbars disappeared behind white rectangles once.
- Fonts. `font.family = 'Arial'` plus `pdf.fonttype = 42` embeds ArialMT from
  `/System/Library/Fonts/Supplemental` as subsetted CID TrueType with a ToUnicode map
  (searchable, copyable). The default fonttype 3 gives Type 3 glyph programs with no
  Unicode. Math text uses DejaVu Sans unless `mathtext.fontset = 'custom'` points at
  Arial, which is where the stray DejaVu rows in `pdffonts` come from.
- Opacity. `facecolor=(r, g, b, 0.75)` on a patch writes an ExtGState with `ca 0.75`,
  matching Illustrator's badges.
- Useful for the redesign, verified in the research notes: `Figure.subfigures` for
  nested panel groups, `ax.inset_axes` + `ax.indicate_inset_zoom` for zoom insets,
  `mpl_toolkits.axes_grid1.anchored_artists.AnchoredSizeBar` for scale bars whose
  label embeds with the same Arial subset, `ConnectionPatch` for cross-panel arrows
  in data or axes coordinates. Constrained layout ignores figure-level artists, so
  add panel letters and arrows in figure coordinates or fix the gridspec geometry
  explicitly (the sparse-sampling-figures skill has the same advice).

---

## 6. Recommended shared style block

Put this in one module every figure script imports, so no figure can drift:

```python
import matplotlib as mpl
mpl.rcParams.update({
    'font.family': 'Arial',
    'pdf.fonttype': 42, 'ps.fonttype': 42,
    'mathtext.fontset': 'custom',
    'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic', 'mathtext.bf': 'Arial:bold',
    'font.size': 8, 'axes.linewidth': 0.5,
    'image.interpolation': 'none',          # honest pixels by default
    'savefig.dpi': 300,                     # only affects anything still rasterized
})
```

Jenny's checklist items that a script or a gate can enforce mechanically: Arial
everywhere; no text below 6 pt at final size; figure built at 3.375 in (one column)
or 7.0 in (two columns) from the start; a numbered scale bar on every image; a
labelled colorbar per palette; no red-green pairs; `rasterized=True` only where a
vector element would otherwise explode, never for data images.

---

## 7. PDF forensics toolkit (how to read an existing figure exactly)

Poppler, already installed: `pdfimages -list f.pdf` (raster sizes, ppi, color
model), `pdffonts f.pdf` (Type 3 vs TrueType, embedded, Unicode), `pdfinfo` (page
size, producer), `pdftoppm -r 300 -png` (independent renderer for diffs).

PyMuPDF (`import fitz`; currently only in a scratch venv, see Section 9):

- `page.get_image_info(xrefs=True)` gives each image's bbox and 6-number transform.
  Negative `d` means bottom-up storage.
- `page.get_text('dict')` gives spans with font, size, color and baseline origin;
  `'rawdict'` gives per-character origins (use it to measure kerning differences).
- `page.get_drawings()` gives rectangles and paths with fill and stroke colors, but it
  flattens form XObjects and reports their opacity as 1.0. Opacity has to be read from
  the content stream (`page.read_contents()`) by tracking `gs` and the `q`/`Q` stack.
- `fitz.Pixmap(doc, xref)` decodes a raster; the soft mask is a separate xref in
  `doc.extract_image(xref)['smask']`.
- `doc.xref_get_key(page.xref, 'Group')`, `'Resources/ExtGState/GS0'`,
  `'Resources/ColorSpace/CS0'` expose transparency groups, opacity states and color
  spaces. This is how the CMYK page group was found.
- `fitz.TOOLS.set_icc(False)` turns off color management; rendering both PDFs with and
  without it separates color-profile differences from content differences.

Pitfalls: `pdftocairo -svg` and `inkscape --pdf-poppler` convert all text to outlines,
never use them to open a figure for text edits; `pdfimages -png` writes palette PNGs
for Indexed images (convert to RGB before comparing); Illustrator's `.ai` files open
as PDF only if saved with PDF compatibility.

---

## 8. The verification harness, and how to reuse it as a regression test

`compare_pdfs.py orig.pdf new.pdf` reports, in order: page size; for every embedded
raster, byte equality of RGB and alpha and placement error in points; for every text
span, nearest match by string with origin offset, size and font; a 300 dpi render
diff with the fraction of pixels above 0, 16 and 64 levels, split into image areas
and the rest; and a `*_diff.png` with differences above 16 levels painted red over
a faded copy of the original.

This is exactly the tool for the feedback loop: after changing a figure script, run
the harness against the previous PDF. Rasters that should not have changed must
report identical; the red overlay shows precisely what moved. Thresholds that held
here: rasters identical, text at 0.000 pt, under 0.3% of pixels above 64 levels.

---

## 9. Environment facts

- `.venv/bin/python` runs fine on this Mac (matplotlib 3.10.8, numpy 2.2.6, stmpy,
  spgl1). The sparse-sampling-figures skill's note that it cannot launch applies only
  to the cloud sandbox.
- PyMuPDF, pikepdf and svgutils are not in `.venv`. The harness ran from a scratch
  venv under the session scratchpad, which is ephemeral. Add PyMuPDF to the project
  (`uv add --dev pymupdf`) before relying on `extract_rasters.py` or `compare_pdfs.py`.
- Not installed: Inkscape, any TeX engine, draw.io, Ghostscript, rsvg-convert.
  Poppler and Node are.
- All four scripts resolve paths from their own directory, so the folder works from
  `figures/rebuild_check/`. `regen_arrays.py` has the repo root hardcoded.
- zsh does not word-split `$var` in `for` loops; use explicit commands or `${=var}`.

---

## 10. Analysis provenance confirmed while regenerating

- Fig. 1 panels: (a) `t.z = lineSubtract(nsigma_local(t.Z), 2)` from
  `2022-09-05_BSCCO_SparseSamplingTopo001.sxm`, colormap `blue2`, auto limits at ±5σ;
  (b) sparse map with NaN at unmeasured pixels; (c) `rec_bpdn_display`, the BPDN
  reconstruction rescaled to the ground-truth mean and std; (d) `gt_fA`, full grid at
  −22 mV; (e) to (h) FTs with `zeroDC=True`. Real-space limits are the ground truth's
  mean ± 5σ; FT limits are 0 to the ground-truth FT's mean + 5σ, shared across the row.
- BPDN (notebook cell 24) is deterministic and converges in about 1 s with spgl1
  status 1 ("root found"), so reconstructions never need caching.
- Fig. 3(b) comes from the notebook's "after" branch: drift field fit on the
  reconstruction itself (`find_drift_parameter(rec_bpdn, sigma=10, cut2=[9,0,9,0])`,
  then a second pass at sigma 13), output 241 × 241. The topography-derived branch
  (cells 34 to 44) was never saved to a figure. This is the J16 item in the response doc.
- Fig. 3(a) uses the ground-truth color limits; 3(b) and 3(d) use automatic limits
  from their own data (cell 59 passes no `clims`). The shared colorbar in Fig. 3 is
  therefore only qualitatively shared.

---

## 11. Defects found in the current manuscript figures

1. Fig. 3(c) is the FT of the ground-truth map (its raster is byte-identical to
   Fig. 1(h)), not the FT of the reconstruction in 3(a). `rebuilt_fig3_fixed.pdf`
   has the right panel; the caption's before/after comparison is wrong until then.
2. Every data panel is blurred by one-pixel Hanning resampling (Section 4).
3. Three included PDFs carry Type 3 fonts (Section 2); one has no Arial at all.
4. Fig. 3 real-space panels do not share color limits (Section 10).
5. Illustrator documents were in CMYK mode. New figures should stay RGB.
6. The 75% badge opacity is a design choice worth a conscious yes or no; code makes
   it uniform either way.

---

## 12. Suggested shape for the reorganization

- One script per manuscript figure in `figures/`, each writing its PDF straight to
  `paper/` (the path `main.tex` includes) and a print-size PNG to `figures/` for
  review.
- A shared `figures/style.py` (Section 6) and `figures/panels.py` with the helpers
  these two figures need: place an axes by points, badge, scale bar with label,
  colorbar with H/L, panel letter, FT-row scale bar in Å⁻¹.
- A `figures/pipeline.py` that is the notebook's cells 3 to 14, 24 and 52 to 57 as
  functions (`load_40nm()`, `reconstruct_bpdn()`, `drift_correct_after()`,
  `drift_correct_from_topo()`), so figure scripts import data and never copy code.
  `regen_arrays.py` in this folder is already that transcript.
- A `figures/check_figure.py` gate run after every build: `pdffonts` shows only
  embedded TrueType Arial, page width is 3.375 or 7.0 in, no text under 6 pt, a PNG
  at print size for a human or model to look at.
- `compare_pdfs.py` as the regression diff between the previous and the new PDF of
  the same figure, attached to the response-doc entry for the comment that caused
  the change.
- Feedback loop: each reviewer comment maps to one script edit plus one harness run
  plus one PNG look. The response doc's "Change:" line then cites the script, the
  commit and the diff image instead of describing a manual Illustrator step.
- Keep the notebooks for exploration only. Nothing the manuscript includes should
  depend on notebook cell order again.

Decisions for Marcos before building this: keep or drop the badge opacity; whether
Fig. 3(b) moves to the topography-derived drift field (J16); whether Fig. 1 becomes
the four-panel version Jenny sketched on 4 Nov (then Sections 3 and 4 are reference,
not a target); where the single source of truth for figure PDFs lives.
