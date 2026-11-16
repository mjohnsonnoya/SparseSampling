"""
Fig. 2 addition, panel 2 of 2: back on the uniform grid.

Row-4 companion to fig2_nudft_resampling_panel.py (panel 1). Panel 1 ended
with the Fourier kernel evaluated at the corrected off-grid positions x~_n;
this panel shows the return trip:

  top:    the measured values y_n registered at their corrected positions
          x~_n (green circles). In this single-mode toy y_n = cos(k x~_n),
          so the registered samples trace the ideal lattice cosine.
  bottom: the corrected map evaluated back ON the uniform grid x_n by an
          ordinary inverse FFT of the corrected coefficients F~(q) (open
          diamonds). These are newly computed values, each a sum over ALL
          samples, not a moved copy of any single measurement, so no
          per-sample connectors are drawn (deliberate contrast to panel 1:
          the inverse transform is global, not pointwise).

Same slot geometry as panel 1: 3.29 x 1.64 in canvas (half the parent PDF's
rendered 6.58 in width), no tight crop, fonts match siblings at 100%.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
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

# Draft caption fragment for the Fig. 2 assembly (conceptual level, matching
# panel 1's caption; dots here are DATA values, unlike panel 1's kernel dots).
CAPTION = r"""
The corrected coefficients $\tilde{F}(q)$ occupy the same uniform frequency
grid as an ordinary FFT, so a standard inverse FFT evaluates the corrected
map back on the uniform grid. Green circles: the measured values $y_n$
registered at their corrected positions $\tilde{x}_n$ (in this single-mode
illustration they trace the ideal lattice cosine). Open diamonds: the
recomputed on-grid values; each is a sum over all samples rather than a
moved copy of any single measurement, so no sample-to-sample connectors are
drawn. Only a subset of positions is drawn for clarity.
"""

# Same lattice as fig_drift_correction_1d.py and panel 1
L = 14.0
d = 2.0
k = 2 * np.pi / d

# Keep in sync with sample_positions() in fig2_nudft_resampling_panel.py
x_n = np.arange(0.5, 8.1, 1.25)
u = np.log(x_n + 1) / k
x_corr = x_n + u

y_reg = np.cos(k * x_corr)   # measured values registered at x~_n (on-curve)
y_out = np.cos(k * x_n)      # recomputed values on the uniform grid (ideal)

x_dense = np.linspace(0, 11, 1200)
signal = np.cos(k * x_dense)

corr_color = 'C2'       # matches "corrected" in Fig. 2 and panel 1
mode_color = '0.15'

fig, (ax_top, ax_bot) = plt.subplots(
    2, 1, figsize=(3.29, 1.64), sharex=True,
    gridspec_kw=dict(hspace=0.38),
)
fig.subplots_adjust(left=0.115, right=0.99, top=0.985, bottom=0.185)

for ax in (ax_top, ax_bot):
    ax.plot(x_dense, signal, color=mode_color, lw=0.8, zorder=1)
    ax.set_xlim(0, 11)
    ax.set_ylim(-1.3, 1.3)
    ax.set_yticks([-1, 0, 1])
    # full spine box kept: matches the sibling panels in Fig. 2

# Both axes show signal amplitude (the toy is unitless), echoing panel (a)
fig.supylabel('Height', fontsize=7, x=0.02)

ax_top.plot(x_corr, y_reg, 'o', ms=3, color=corr_color,
            mec='white', mew=0.3, zorder=5)
ax_bot.plot(x_n, y_out, 'D', ms=3, mfc='white', mec=corr_color,
            mew=0.8, zorder=5)
ax_bot.set_xlabel(r'Position $x$ (nm)')

h_reg = Line2D([], [], marker='o', ls='none', ms=3, color=corr_color,
               mec='white', mew=0.3)
h_out = Line2D([], [], marker='D', ls='none', ms=3, mfc='white',
               mec=corr_color, mew=0.8)
ax_top.legend([h_reg], [r'Measured $y_n$ at $\tilde{x}_n$'],
              fontsize=5, loc='upper right', framealpha=0.85,
              borderpad=0.3, handletextpad=0.4, handlelength=1.2)
ax_bot.legend([h_out], [r'Recomputed at grid $x_n$'],
              fontsize=5, loc='lower right', framealpha=0.85,
              borderpad=0.3, handletextpad=0.4, handlelength=1.2)


def operation_annotation(fig, ax_top, ax_bot):
    """Depict the global operation carrying the top frame into the bottom
    frame (the inverse FFT of F~(q)) in the gap between the two axes.

    Unlike panel 1's per-sample connectors, this must read as ONE operation
    applied to everything at once: a single bold arrow (heavier and darker
    than panel 1's thin light-gray connectors) with a two-word, legend-weight
    tag. Placed on the right rail, grouped with the legends, so the data
    region stays clean.
    """
    top_edge = ax_top.get_position().y0
    bot_edge = ax_bot.get_position().y1
    x_arrow = 0.80
    arrow = FancyArrowPatch((x_arrow, top_edge - 0.005),
                            (x_arrow, bot_edge + 0.005),
                            transform=fig.transFigure,
                            arrowstyle='-|>', color='0.15', lw=1.1,
                            shrinkA=0, shrinkB=0, mutation_scale=7)
    fig.add_artist(arrow)
    fig.text(0.815, (top_edge + bot_edge) / 2, 'inverse FFT',
             fontsize=5, color='0.15', ha='left', va='center')


operation_annotation(fig, ax_top, ax_bot)

# No tight crop: the canvas IS the slot size
fig.savefig('figures/fig2_inverse_fft_panel.pdf', dpi=300)
fig.savefig('figures/fig2_inverse_fft_panel.png', dpi=200)
print('Saved figures/fig2_inverse_fft_panel.{pdf,png}')
