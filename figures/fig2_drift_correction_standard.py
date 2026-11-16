"""
Fig. 2 (Lawler-Fujita drift correction in a 1D toy model), on the house
standard. The manuscript's Fig. 2 since 2026-11-15. It is the condensed 3x4
figure (obsolete/fig2_drift_correction_condensed.py) rebuilt on figstyle.
Self-contained: no data files. Writes to figures/out/ only.

Nothing about the science changes. The signal-generation block, colours,
marker styles and sample positions are copied verbatim from the condensed
script. What changes is presentation, each item tied to a Hoffman rule:

  width      7.0 in (was 6.67 in, which LaTeX enlarged to 105%)
  fonts      Arial for text and math, embedded TrueType (was Type 3, with the
             math in DejaVu Sans)
  font size  legends 6 pt (were 4 and 5 pt); the formula in (f) 7 pt (was
             5 pt with a 2.5 pt nested subscript), written with exp() so
             nothing sits in an exponent
  data-ink   legend boxes removed, and every legend sits in a band reserved
             for it instead of on top of a curve; frames and ticks 0.5 pt
  scales     (b) and (c) share one y range, so X(r) and Y(r) compare by eye

Content changes since the condensed script:
  J13 (Jenny, 2026-10-24)  the legends in (b), (c) write the slow phase as
                           k u; the symbol theta no longer appears on the figure.
  J12, J14                 panel (a): the ideal lattice is a continuous line
                           with no dots; the measurement is drawn as dots at
                           sample points (every 18th of the 1000); the dashed
                           line is the continuous A(r) they sample, with its
                           own legend entry. No atoms are drawn.

Usage:
    .venv/bin/python figures/fig2_drift_correction_standard.py
    .venv/bin/python figures/check_figure.py figures/out/fig2_drift_correction_standard.pdf --width full
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib.lines import Line2D
from matplotlib.patches import ConnectionPatch
from scipy.ndimage import gaussian_filter1d
import figstyle as fs

# ═══════════════════════════════════════════════════════════════
# Signal generation (verbatim from fig2_drift_correction_4x4.py)
# ═══════════════════════════════════════════════════════════════
L = 14.0
N = 1000
d = 2.0
k = 2 * np.pi / d

x = np.linspace(0, L, N, endpoint=False)
dx = x[1] - x[0]
A_perfect = np.cos(k * x)

theta_fn = lambda r: np.log(r + 1)
u_fn = lambda r: theta_fn(r) / k
A_distorted = np.cos(k * x + theta_fn(x))

ref_cos = np.cos(k * x)
ref_sin = np.sin(k * x)
prod_cos = A_distorted * ref_cos
prod_sin = A_distorted * ref_sin

sigma_pixels = 80
X_r = gaussian_filter1d(prod_cos, sigma=sigma_pixels)
Y_r = gaussian_filter1d(prod_sin, sigma=sigma_pixels)

theta_extracted = np.unwrap(np.arctan2(-Y_r, X_r))
u_extracted = theta_extracted / k

r_tilde = x + u_extracted
A_corrected = np.interp(x, r_tilde, A_distorted)

freqs = 2 * np.pi * np.fft.fftshift(np.fft.fftfreq(N, d=dx))
fft_perfect = np.abs(np.fft.fftshift(np.fft.fft(A_perfect)))
fft_distorted = np.abs(np.fft.fftshift(np.fft.fft(A_distorted)))
fft_corrected = np.abs(np.fft.fftshift(np.fft.fft(A_corrected)))

atoms_perfect = np.arange(0, 11, d)
atoms_distorted = np.interp(atoms_perfect, x + u_fn(x), x)

# Sample positions for the resampling panels (locked, see 4x4 script)
x_n = np.arange(0.5, 8.1, 1.25)
x_corr = x_n + u_fn(x_n)

x_dense = np.linspace(0, 11, 1200)
mode_dense = np.cos(k * x_dense)

y_kernel_grid = np.cos(k * x_n)
y_kernel_corr = np.cos(k * x_corr)
y_reg = np.cos(k * x_corr)
y_out = np.cos(k * x_n)

uncorr_color = '#D55E00'   # Okabe-Ito vermillion: "distorted / measured"
corr_color = '#0072B2'     # Okabe-Ito blue:       "corrected"
ref_color = '0.45'         # neutral grey:         "perfect / ideal reference"
mode_color = '0.15'
link_color = '0.55'

# ═══════════════════════════════════════════════════════════════
# Figure layout: the condensed figure's grid, at the full text width
# (fixed margins, see the 4x4 script for why not constrained layout)
# ═══════════════════════════════════════════════════════════════
fig = fs.new_figure('full', 5.7)
gs = fig.add_gridspec(
    3, 4,
    left=0.066, right=0.995, bottom=0.064, top=0.945,
    hspace=0.42, wspace=0.34,
)

xlim_signal = (-0.5, 11)
xlim_fft = (-4 * np.pi, 4 * np.pi)
XLABEL_POS = r'Position $r$ (nm)'
XLABEL_FREQ = r'Frequency $q$ (nm$^{-1}$)'

# Legend bands: each axis keeps headroom (or footroom) that only its legend
# uses, so no legend covers a curve and none needs a box. In a stacked pair
# the bands are mirrored, leaving the gap between the two axes to the
# connectors and the arrow.
BAND_ABOVE = (-1.3, 2.1)
BAND_BELOW = (-2.1, 1.3)
LEGEND = dict(handletextpad=0.4, handlelength=1.4, borderaxespad=0.25,
              labelspacing=0.25, columnspacing=1.0)


def stacked_pair(subspec, curve_color=mode_color):
    inner = subspec.subgridspec(2, 1, hspace=0.46)
    ax_top = fig.add_subplot(inner[0])
    ax_bot = fig.add_subplot(inner[1], sharex=ax_top)
    ax_top.tick_params(labelbottom=False)
    for ax, ylim in ((ax_top, BAND_ABOVE), (ax_bot, BAND_BELOW)):
        ax.plot(x_dense, mode_dense, color=curve_color, lw=0.8, zorder=1)
        ax.set_xlim(*xlim_signal)
        ax.set_ylim(*ylim)
        ax.set_yticks([-1, 0, 1])
    return ax_top, ax_bot


# ── Row 1: measure, demodulate, recover the drift ────────────

# (a) Measured vs ideal. J12/J14 (Jenny): the ideal lattice is a continuous
# line (it exists whether or not it is measured); the measurement is a set of
# dots. The dashed line is the continuous A(r) the dots sample; it has its own
# legend entry because cold readers could not otherwise tell which orange mark
# was A(r). Every 18th of the 1000 samples is drawn (0.25 nm apart, 8 per
# lattice period). No atoms are drawn: Jenny offered them only as an option,
# and the peaks of the ideal line already mark them.
SHOW_EVERY = 18
ax_a = fig.add_subplot(gs[0, 0])
dot = dict(marker='o', ms=2.4, color=uncorr_color, mec='white', mew=0.25)
ax_a.plot(x_dense, mode_dense, color=ref_color, alpha=0.6, lw=0.8)
ax_a.plot(x_dense, np.cos(k * x_dense + theta_fn(x_dense)), color=uncorr_color,
          lw=0.5, ls='--', alpha=0.7)
ax_a.plot(x[::SHOW_EVERY], A_distorted[::SHOW_EVERY], ls='none', zorder=5, **dot)
ax_a.set_xlim(*xlim_signal)
ax_a.set_xlabel(XLABEL_POS)
ax_a.set_ylim(-1.3, 2.6)
ax_a.set_yticks([-1, 0, 1])
ax_a.set_ylabel('Height')
ax_a.legend([Line2D([], [], color=ref_color, alpha=0.6, lw=0.8),
             Line2D([], [], color=uncorr_color, lw=0.5, ls='--', alpha=0.7),
             Line2D([], [], ls='none', **dot)],
            [r'Ideal lattice $\cos(kr)$', r'$A(r)$', 'Measured samples'],
            loc='upper right', **LEGEND)
ax_a.set_title(r"Measured $A(r)=\cos[k(r+u(r))]$")
fs.panel_label(ax_a, 'a')

# (b) Filtered cos -> X(r).  (b) and (c) share one y range.
YLIM_XY = (-1.1, 1.75)
ax_b = fig.add_subplot(gs[0, 1])
ax_b.plot(x, prod_cos, color=uncorr_color, alpha=0.35, lw=0.4, label=r'$A(r)\cos(kr)$')
ax_b.plot(x, X_r, color=uncorr_color, lw=1.2, label=r'$X(r)$ = LPF[$A\cos(kr)$]')
ax_b.plot(x, 0.5 * np.cos(theta_fn(x)), 'k--', lw=0.8, alpha=0.5,
          label=r'True ½$\cos(ku)$')
ax_b.set_xlim(*xlim_signal)
ax_b.set_xlabel(XLABEL_POS)
ax_b.set_ylabel('Amplitude')
ax_b.legend(loc='upper right', **LEGEND)
ax_b.set_title("LPF → $X(r)$")
fs.panel_label(ax_b, 'b')

# (c) Filtered sin -> Y(r)
ax_c = fig.add_subplot(gs[0, 2])
ax_c.plot(x, prod_sin, color=uncorr_color, alpha=0.35, lw=0.4, label=r'$A(r)\sin(kr)$')
ax_c.plot(x, Y_r, color=uncorr_color, lw=1.2, label=r'$Y(r)$ = LPF[$A\sin(kr)$]')
ax_c.plot(x, -0.5 * np.sin(theta_fn(x)), 'k--', lw=0.8, alpha=0.5,
          label=r'True −½$\sin(ku)$')
ax_c.set_xlim(*xlim_signal)
ax_c.set_xlabel(XLABEL_POS)
ax_c.legend(loc='upper right', **LEGEND)
ax_c.set_title("LPF → $Y(r)$")
fs.panel_label(ax_c, 'c')
for ax in (ax_b, ax_c):
    ax.set_ylim(*YLIM_XY)
    ax.set_yticks([-1, -0.5, 0, 0.5, 1])

# (d) Recovered drift
ax_d = fig.add_subplot(gs[0, 3])
ax_d.plot(x, u_fn(x), color=ref_color, lw=1.5, label=r'True $u(r)=\ln(r+1)/k$')
ax_d.plot(x, u_extracted, color=uncorr_color, ls='--', lw=1.2, label='Recovered $u(r)$')
ax_d.set_xlim(*xlim_signal)
ax_d.set_xlabel(XLABEL_POS)
ax_d.set_ylabel('$u(r)$ (nm)')
ax_d.legend(loc='lower right', **LEGEND)
ax_d.set_title(r"Drift $u = \arctan(-Y/X)\,/\,k$")
fs.panel_label(ax_d, 'd')
for ax in (ax_a, ax_b, ax_c, ax_d):
    ax.set_xticks([0, 5, 10])


# ── Row 2: the correction step in Fourier terms ──────────────

# (e) Fourier weights at grid vs corrected positions
ax_e_top, ax_e_bot = stacked_pair(gs[1, 0:2])
for ax, xs, ys, c in ((ax_e_top, x_n, y_kernel_grid, uncorr_color),
                      (ax_e_bot, x_corr, y_kernel_corr, corr_color)):
    ax.axhline(0, color='0.75', lw=0.5, zorder=1)
    ax.vlines(xs, 0, ys, color=c, lw=0.9, zorder=4)
    ax.plot(xs, ys, 'o', ms=3, color=c, mec='white', mew=0.3, zorder=5)
ax_e_top.set_ylabel(r'Weight $\cos(qr)$')
ax_e_top.yaxis.set_label_coords(-0.06, -0.23)
ax_e_bot.set_xlabel(XLABEL_POS)
ax_e_top.set_title(r"Fourier weights at grid $r_n$ vs corrected $\tilde{r}_n = r_n + u(r_n)$")
fs.panel_label(ax_e_top, 'e')

h_grid = Line2D([], [], marker='o', ls='none', ms=3, color=uncorr_color,
                mec='white', mew=0.3)
h_corr = Line2D([], [], marker='o', ls='none', ms=3, color=corr_color,
                mec='white', mew=0.3)
h_link = Line2D([], [], color=link_color, lw=0.55)
ax_e_top.legend([h_grid, h_link], [r'Grid $r_n$', 'Same sample'],
                loc='upper right', ncol=2, **LEGEND)
ax_e_bot.legend([h_corr], [r'Corrected $\tilde{r}_n$'], loc='lower right', **LEGEND)

for xg, yg, xc, yc in zip(x_n, y_kernel_grid, x_corr, y_kernel_corr):
    fig.add_artist(ConnectionPatch(
        xyA=(xg, yg), coordsA=ax_e_top.transData,
        xyB=(xc, yc), coordsB=ax_e_bot.transData,
        color=link_color, lw=0.55, alpha=0.85, zorder=2,
    ))

# (f) Back on the uniform grid
ax_f_top, ax_f_bot = stacked_pair(gs[1, 2:4], curve_color=ref_color)
ax_f_top.plot(x_corr, y_reg, 'o', ms=3, color=corr_color,
              mec='white', mew=0.3, zorder=5)
ax_f_bot.plot(x_n, y_out, 'D', ms=3, mfc='white', mec=corr_color,
              mew=0.8, zorder=5)
ax_f_top.set_ylabel('Height')
ax_f_bot.set_ylabel('Height')
ax_f_bot.set_xlabel(XLABEL_POS)
ax_f_top.set_title("Back on the uniform grid")
fs.panel_label(ax_f_top, 'f')

h_reg = Line2D([], [], marker='o', ls='none', ms=3, color=corr_color,
               mec='white', mew=0.3)
h_out = Line2D([], [], marker='D', ls='none', ms=3, mfc='white',
               mec=corr_color, mew=0.8)
h_ideal = Line2D([], [], color=ref_color, lw=0.8)
ax_f_top.legend([h_reg, h_ideal], [r'Measured $y_n$ at $\tilde{r}_n$', 'Ideal lattice'],
                loc='upper right', ncol=2, **LEGEND)
ax_f_bot.legend([h_out], [r'Recomputed $\tilde{y}_n$ at grid $r_n$'],
                loc='lower right', **LEGEND)

# The arrow and its formula live in the gap between the two axes; the formula
# reads across the arrow, left to right.
_x_arrow = 0.50
fig.add_artist(ConnectionPatch(
    xyA=(_x_arrow, -0.03), coordsA='axes fraction', axesA=ax_f_top,
    xyB=(_x_arrow, 1.03), coordsB='axes fraction', axesB=ax_f_bot,
    arrowstyle='-|>', color='0.15', lw=1.1,
    shrinkA=0, shrinkB=0, mutation_scale=7, zorder=6,
))
for dx_txt, ha, s in ((-0.02, 'right', r'$\tilde{x}_q=\Sigma_n\, y_n \exp(-iq\tilde{r}_n)$'),
                      (+0.02, 'left', r'then $\tilde{y}=F^{-1}\tilde{x}$')):
    ax_f_top.text(_x_arrow + dx_txt, -0.23, s, transform=ax_f_top.transAxes,
                  fontsize=7, color='0.15', ha=ha, va='center', zorder=6)


# ── Row 3: result, real space and Fourier space ──────────────

# (g) Corrected signal, with the measured signal faint behind it
ax_g = fig.add_subplot(gs[2, 0:2])
ax_g.plot(x, A_perfect, color=ref_color, alpha=0.6, lw=0.6, ls='--',
          label='Ideal (reference)')
ax_g.plot(x, A_distorted, color=uncorr_color, alpha=0.35, lw=0.6,
          label='Distorted (measured)')
ax_g.plot(x, A_corrected, color=corr_color, lw=0.8, label='Corrected')
ax_g.set_xlim(*xlim_signal)
ax_g.set_ylim(-1.3, 1.9)
ax_g.set_yticks([-1, 0, 1])
ax_g.set_ylabel('Height')
ax_g.set_xlabel(XLABEL_POS)
ax_g.legend(loc='upper right', ncol=3, **LEGEND)
ax_g.set_title("Corrected signal A")
fs.panel_label(ax_g, 'g')

# (h) One FFT panel: before, after, reference
ax_h = fig.add_subplot(gs[2, 2:4])
ax_h.plot(freqs, fft_perfect, color=ref_color, alpha=0.6, lw=0.8, label='Ideal')
ax_h.plot(freqs, fft_distorted, color=uncorr_color, lw=0.8, label='Distorted')
ax_h.plot(freqs, fft_corrected, color=corr_color, lw=0.8, label='Corrected')
ax_h.set_xlim(*xlim_fft)
ax_h.set_ylabel('|FFT|')
ax_h.set_xlabel(XLABEL_FREQ)
ax_h.legend(loc='upper right', **LEGEND)
ax_h.set_title("FFT: peak broadened by drift, sharpened by correction")
fs.panel_label(ax_h, 'h')


fs.save(fig, 'fig2_drift_correction_standard')
