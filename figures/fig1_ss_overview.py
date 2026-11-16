"""Fig. 1 (sparse QPI reconstruction benchmark on BSCCO), built to the house
standard. Same eight panels as the Illustrator-assembled
paper/figure1_SS_overview.pdf, which it replaced; writes to figures/out/ only.

Differences from the Illustrator figure, all deliberate:
  - scale bars sit in the lower right corner of each panel (J6, Jenny 2026-10-24);
  - built at 7.0 in, so nothing is rescaled in print (the old file shrank to 74%);
  - the 250 px data arrays are embedded as they are, no resampling;
  - the topography (a) and its FT (e) are on their own limits, so they get their
    own colorbars on the left; (b)-(d) share one pair of limits and so do (f)-(h),
    tied to the ground truth;
  - only the topography colorbar carries numbers (pm). The dI/dV and Fourier
    colorbars are marked L/H and 0/H inside the bar: those scales are relative;
  - each FT is divided by its pixel count, the same normalization Fig. 3 needs to
    compare maps of 250 and 241 px;
  - scale bars are round numbers (10 nm, 1 per Angstrom).

Data: figures/data_bscco.py (instrument files -> arrays, about 2 s).

Usage: .venv/bin/python figures/fig1_ss_overview.py     -> figures/out/fig1_ss_overview.pdf
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import stmpy
import stmpy.tools as st
import data_bscco
import figstyle as fs

D = data_bscco.load()
N = 250
FOV_NM = 40.0
ft = lambda a: st.fft(a, zeroDC=True) / a.size          # magnitude per pixel

topo = D['tz'] * 1e12                                    # m -> pm
gt = D['gt_fA']
maps = [topo, D['to_show'], D['rec_bpdn_display'], gt]   # (a)-(d); NaN = unmeasured
fts = [ft(topo), ft(D['to_show_fft']), ft(D['rec_bpdn_display']), ft(gt)]              # (e)-(h)

# Ground truth leads each list: the limits are tied to it (see fs.shared_clim).
real_lim = fs.shared_clim([gt, maps[1], maps[2]])
ft_lim = fs.shared_clim([fts[3], fts[1], fts[2]], zero_floor=True)
lims = [fs.shared_clim([topo]), real_lim, real_lim, real_lim]
ft_lims = [fs.shared_clim([fts[0]], zero_floor=True), ft_lim, ft_lim, ft_lim]

dq = 2 * np.pi / (FOV_NM * 10)                           # 1/Angstrom per FT pixel
Q_EXTENT = (-(N // 2 + 0.5) * dq, (N // 2 - 0.5) * dq) * 2

# ---- layout, in inches --------------------------------------------------------
W = fs.WIDTHS['full']
S, GAP, BAR = 1.5475, 0.05, 0.14                         # panel side, gap between panels, colorbar width
X = [0.44 + c * (S + GAP) for c in range(4)]
H = 0.34 + 2 * S + 0.07 + 0.04
Y = [0.04 + S + 0.07, 0.04]                              # row bottoms, top row first
fig = fs.new_figure('full', H)
box = lambda x, y, w, h: fig.add_axes([x / W, y / H, w / W, h / H])
ax = [[box(X[c], Y[r], S, S) for c in range(4)] for r in range(2)]
cax_left = [box(X[0] - 0.06 - BAR, Y[r], BAR, S) for r in range(2)]  # full panel height
cax_right = [box(X[3] + S + 0.06, Y[r], BAR, S) for r in range(2)]

titles = ['Topography', 'Sparsely Measured Map', 'Reconstructed Map', 'Full-Grid Map\n(Ground Truth)']
cmaps = [stmpy.cm.blue2] + [stmpy.cm.jackyPSD] * 3
ims = [[None] * 4, [None] * 4]
for c in range(4):
    ims[0][c] = fs.image(ax[0][c], maps[c], extent=(0, FOV_NM) * 2, cmap=cmaps[c],
                         vmin=lims[c][0], vmax=lims[c][1])
    ims[1][c] = fs.image(ax[1][c], fts[c], extent=Q_EXTENT, cmap=stmpy.cm.gray_r,
                         vmin=ft_lims[c][0], vmax=ft_lims[c][1])
    ax[0][c].set_title(titles[c], fontweight='bold', pad=3, linespacing=1.0)
    sparse = c == 1                                      # mostly blank: the bar needs a backing
    fs.scalebar(ax[0][c], 10, '10 nm', color=fs.INK if sparse else 'w', size=8.6, box=sparse)
    fs.scalebar(ax[1][c], 1, '1 Å$^{-1}$', color=fs.INK, size=8.6)
    fs.panel_label(ax[0][c], 'abcd'[c], note='' if c == 0 else '−22 mV', on_image=True)
    fs.panel_label(ax[1][c], 'efgh'[c], on_image=True)

# Topography is a height, so its bar carries numbers. The dI/dV maps (a raw
# lock-in signal) and every Fourier magnitude are relative, so theirs carry only
# a direction: L and H inside the bar, as in the original figure, with 0 at the
# foot of the Fourier bars because that zero is real.
fs.colorbar(ims[0][0], cax_left[0], 'pm', fmt='%.0f', side='left')
fs.colorbar(ims[1][0], cax_left[1], labels=('0', 'H'), inset=True)
fs.colorbar(ims[0][3], cax_right[0], labels=('L', 'H'), inset=True)
fs.colorbar(ims[1][3], cax_right[1], labels=('0', 'H'), inset=True)

fs.save(fig, 'fig1_ss_overview')
