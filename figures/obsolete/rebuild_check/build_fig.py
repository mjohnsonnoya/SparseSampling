"""Rebuild figure1_SS_overview.pdf and drift_correction_results.pdf as ONE
matplotlib figure each, placing every raster, badge, scale bar and text span at
the coordinates read out of the Illustrator PDFs (…_geom.json).

Rasters are the 308x308 arrays matplotlib itself produced for the notebook
panels, embedded with interpolation='none' so the PDF carries them unchanged.
Text is Arial (TrueType, pdf.fonttype 42), so it stays text in the PDF.

Usage: build_fig.py fig1|fig3 out.pdf [--fix-3c]
  --fix-3c   put the FT of the reconstruction (Fig. 1(g)) in Fig. 3(c) instead
             of the ground-truth FT that the Illustrator file contains.
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe

OUT = os.path.dirname(os.path.abspath(__file__))
which, out_pdf = sys.argv[1], sys.argv[2]
fix3c = '--fix-3c' in sys.argv

plt.rcParams.update({'font.family': 'Arial', 'pdf.fonttype': 42, 'ps.fonttype': 42})
R = np.load(os.path.join(OUT, 'panel_rasters.npz'))

if which == 'fig1':
    geom = json.load(open(os.path.join(OUT, 'figure1_SS_overview_geom.json')))
    xref2panel = {196: 'f_sparse_ft', 197: 'b_sparse', 198: 'c_rec', 199: 'd_gt', 200: 'h_gt_ft',
                  201: 'g_rec_ft', 202: 'e_topo_ft', 203: 'a_topo', 204: 'cb_real', 205: 'cb_ft'}
else:
    geom = json.load(open(os.path.join(OUT, 'drift_correction_results_geom.json')))
    xref2panel = {21: 'c_rec', 22: 'g_rec_ft' if fix3c else 'h_gt_ft', 23: 'f3b_rec_after',
                  24: 'f3d_rec_after_ft', 25: 'cb_real', 26: 'cb_ft'}

W, H = geom['page'][2], geom['page'][3]            # points
fig = plt.figure(figsize=(W / 72, H / 72), dpi=100)
fig.patch.set_facecolor('white')

def rect_axes(bbox):
    """PDF bbox (x0,y0,x1,y1, y down, points) -> matplotlib axes in figure fractions."""
    x0, y0, x1, y1 = bbox
    return fig.add_axes([x0 / W, 1 - y1 / H, (x1 - x0) / W, (y1 - y0) / H])

pt = fig.dpi_scale_trans                             # draw in inches
def P(x, y):                                         # PDF point -> inches, y flipped
    return x / 72, (H - y) / 72

# --- rasters ---------------------------------------------------------------
for im in geom['images']:
    name = xref2panel[im['xref']]
    a = R[name]
    bbox = im['bbox']
    # Illustrator trimmed the fully transparent 1 px border of the sparse map (308 -> 306).
    if a.shape[0] != im['h'] or a.shape[1] != im['w']:
        alpha = a[..., 3]
        rows = np.where(alpha.max(axis=1) > 0)[0]; cols = np.where(alpha.max(axis=0) > 0)[0]
        a = a[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]
        assert a.shape[:2] == (im['h'], im['w']), (name, a.shape, im['h'], im['w'])
    ax = rect_axes(bbox)
    # origin='lower' with a pre-flipped array shows the same picture but makes the
    # PDF backend store the samples top-down, the way Illustrator stored them.
    ax.imshow(a[::-1], origin='lower', interpolation='none', aspect='auto')
    ax.set_axis_off()

# --- vector drawings: badges, scale bars (skip the white panel-background rects) ---
for d in geom['drawings']:
    x0, y0, x1, y1 = d['rect']
    fill = d['fill']; stroke = d['color']
    if fill == [1.0, 1.0, 1.0] and stroke is None and max(x1 - x0, y1 - y0) > 100:
        continue                                             # white background cells (invisible on the page)
    if fill is None and stroke is not None and (x1 - x0) < 12:  # outlined glyph paths of panel (b) label
        continue
    xi, yi = P(x0, y1)
    # Illustrator draws the badges (orange / gray) as 75% opaque form objects in both files;
    # every other fill, stroke and text span is opaque (verified in the content streams).
    is_badge = fill is not None and fill[0] < 0.99 and (y1 - y0) > 10
    alpha = 0.75 if is_badge else 1.0
    fig.add_artist(Rectangle((xi, yi), (x1 - x0) / 72, (y1 - y0) / 72, transform=pt,
                             facecolor=(*fill, alpha) if fill else 'none',
                             edgecolor=(*stroke, d.get('stroke_opacity') or 1.0) if stroke else 'none',
                             linewidth=d['width'] or 0, zorder=5))

# --- text --------------------------------------------------------------------
def rgb(c):
    return ((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255
outlined = {'8 nm': None}
for s in geom['text']:
    txt = s['text']
    if not txt.strip():
        continue
    weight = 'bold' if 'Bold' in s['font'] else 'normal'
    xi, yi = P(*s['origin'])
    # panel (b) of Fig. 1 carries a 1 pt dark outline around its white "8 nm": draw the
    # outline as a stroked path underneath, then the plain text on top so it stays text.
    if which == 'fig1' and txt == '8 nm' and 270 < s['origin'][0] < 290:
        fig.text(xi, yi, txt, transform=pt, fontsize=s['size'], weight=weight, color='none',
                 ha='left', va='baseline', zorder=9,
                 path_effects=[pe.Stroke(linewidth=1.0, foreground=(0.1367, 0.1220, 0.1253))])
    fig.text(xi, yi, txt, transform=pt, fontsize=s['size'], weight=weight, color=rgb(s['color']),
             ha='left', va='baseline', zorder=10)

fig.savefig(out_pdf, dpi=100)
fig.savefig(out_pdf[:-4] + '.png', dpi=150)
print('wrote', out_pdf, 'page', W, H)
