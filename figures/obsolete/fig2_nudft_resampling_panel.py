"""
Fig. 2 addition: off-grid resampling panel (Jenny's sketch, June 2026 meeting).

One panel, two stacked copies of a single Fourier mode:
  top:    kernel evaluated at the nominal uniform grid positions x_n
          (what a standard FFT assumes)
  bottom: kernel evaluated at the drift-corrected off-grid positions
          x~_n = x_n + u(x_n) (where the measured values actually live)
Connector lines pair sample n on the top curve with sample n on the bottom
curve: same measured value y_n, same frequency q, different kernel position.
The sums F(q) = sum_n y_n e^{-iq x_n} vs F~(q) = sum_n y_n e^{-iq x~_n} and
their interpretation belong to the figure caption, not the panel.

Signal parameters mirror figures/fig_drift_correction_1d.py (L=14, d=2,
k=2*pi/d, logarithmic drift) so the panel sits natively inside Fig. 2.

Usage:
    .venv/bin/python figures/fig2_nudft_resampling_panel.py
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import ConnectionPatch
import warnings
warnings.filterwarnings('ignore')

try:
    plt.rcParams['font.family'] = 'Arial'
except Exception:
    plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 7
plt.rcParams['axes.labelsize'] = 7
plt.rcParams['axes.titlesize'] = 8
plt.rcParams['xtick.labelsize'] = 6
plt.rcParams['ytick.labelsize'] = 6
plt.rcParams['xtick.major.pad'] = 2
plt.rcParams['ytick.major.pad'] = 2
plt.rcParams['axes.labelpad'] = 2

# Draft caption fragment for the Fig. 2 assembly (conceptual level per the
# 2026-08 decision: no claim about which resampling operator the pipeline
# uses). The dots are evaluations of the mode, NOT the measured data; the
# caption must say so explicitly (independent-review catch, 2026-08-09).
CAPTION = r"""
A single Fourier mode $\cos(qx)$. The dots mark the mode's value at each
sample's assigned position: a standard FFT pairs the measurement $y_n$ with
the grid position $x_n$ (red), while drift correction pairs the same $y_n$
with the corrected position $\tilde{x}_n = x_n + u(x_n)$ (green); gray lines
connect the two assignments of the same sample. The same measured value $y_n$
therefore multiplies the red mode value in the uncorrected sum
$F(q)=\sum_n y_n\,e^{-iq x_n}$ and the green mode value in the corrected sum
$\tilde{F}(q)=\sum_n y_n\,e^{-iq \tilde{x}_n}$, at the same frequencies $q$.
Only a subset of the full-grid sample positions is drawn for clarity.
"""

# Same lattice as fig_drift_correction_1d.py
L = 14.0
d = 2.0
k = 2 * np.pi / d


def sample_positions():
    """Return (x_n, x_corr): the nominal uniform grid positions and the
    drift-corrected off-grid positions of the samples shown in the panel.

    Fig. 2 convention: corrected position x~_n = x_n + u(x_n), with panel (b)'s
    drift field u(r) = ln(r + 1) / k (the consistent route: no exaggeration).

    Spacing must avoid multiples of the period d, else every sample sits at the
    same phase of the mode; 1.25 nm advances the phase by 5*pi/4 per sample.
    The range is capped at 8.0 so max(x_corr) ~ 8.7 leaves the right end of
    both axes free for the legends (no marker may hide under a legend).
    """
    x_n = np.arange(0.5, 8.1, 1.25)
    u = np.log(x_n + 1) / k
    x_corr = x_n + u
    return x_n, x_corr


x_n, x_corr = sample_positions()

x_dense = np.linspace(0, 11, 1200)
mode = np.cos(k * x_dense)
y_grid = np.cos(k * x_n)        # kernel evaluated at nominal grid positions
y_corr = np.cos(k * x_corr)     # kernel evaluated at corrected positions

uncorr_color = 'r'      # matches "distorted / measured" in Fig. 2
corr_color = 'C2'       # matches "corrected" in Fig. 2
mode_color = '0.15'
link_color = '0.55'

# Sized for its Fig. 2 slot: the parent PDF renders at 6.58 in wide (tight
# crop of its 6.67 canvas), so a 2-of-4-column slot is 3.29 in. Fixed canvas,
# no tight crop on save: place at 100% and the fonts match the siblings.
fig, (ax_top, ax_bot) = plt.subplots(
    2, 1, figsize=(3.29, 1.64), sharex=True,
    gridspec_kw=dict(hspace=0.38),
)
fig.subplots_adjust(left=0.115, right=0.99, top=0.985, bottom=0.185)

for ax in (ax_top, ax_bot):
    ax.plot(x_dense, mode, color=mode_color, lw=0.8, zorder=1)
    ax.set_xlim(0, 11)
    ax.set_ylim(-1.3, 1.3)
    ax.set_yticks([-1, 0, 1])
    # full spine box kept: matches the sibling panels in Fig. 2

# Both curves show the same unitless kernel, so label it once for the figure
fig.supylabel(r'$\cos(qx)$', fontsize=7, x=0.02)

ax_top.plot(x_n, y_grid, 'o', ms=3, color=uncorr_color,
            mec='white', mew=0.3, zorder=5)
ax_bot.plot(x_corr, y_corr, 'o', ms=3, color=corr_color,
            mec='white', mew=0.3, zorder=5)
# Name the axis variable so the ylabel cos(qx) and the marked points x_n,
# x~_n all visibly refer to the same coordinate
ax_bot.set_xlabel(r'Position $x$ (nm)')

# One compact legend, top right; labels kept short so the box never reaches
# the last marker (red dot at x = 8.0). Sums live in CAPTION above.
h_grid = Line2D([], [], marker='o', ls='none', ms=3, color=uncorr_color,
                mec='white', mew=0.3)
h_corr = Line2D([], [], marker='o', ls='none', ms=3, color=corr_color,
                mec='white', mew=0.3)
h_link = Line2D([], [], color=link_color, lw=0.55)
ax_top.legend([h_grid, h_corr, h_link],
              [r'Grid $x_n$', r'Corrected $\tilde{x}_n$', 'Same sample'],
              fontsize=5, loc='upper right', framealpha=0.85,
              borderpad=0.3, handletextpad=0.4, handlelength=1.2,
              labelspacing=0.25)

# Connector lines: same sample, reassigned coordinate
for xg, yg, xc, yc in zip(x_n, y_grid, x_corr, y_corr):
    con = ConnectionPatch(
        xyA=(xg, yg), coordsA=ax_top.transData,
        xyB=(xc, yc), coordsB=ax_bot.transData,
        color=link_color, lw=0.55, alpha=0.85, zorder=2,
    )
    fig.add_artist(con)

# No tight crop: the canvas IS the slot size
fig.savefig('figures/fig2_nudft_resampling_panel.pdf', dpi=300)
fig.savefig('figures/fig2_nudft_resampling_panel.png', dpi=200)
print('Saved figures/fig2_nudft_resampling_panel.{pdf,png}')
