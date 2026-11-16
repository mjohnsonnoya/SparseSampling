"""
Fig. 2 (condensed): Lawler-Fujita drift correction in 1D, 3x4 layout.

Manuscript figure since 2026-09-12; supersedes fig2_drift_correction_4x4.py
(kept for reference). Built after two rounds of cold reads (four independent
readers) flagged the same redundancy in the 4x4:

  (a) ideal lattice   is contained in (c) measured-vs-ideal
  (e,f) raw products  are contained in (g,h) as the faint background trace
  (i) theta(r)        is (j) u(r) rescaled by 1/k
  (d) and (n)         are two halves of one before/after FFT comparison

Applied cuts: drop (a), (e), (f), (i); merge (d)+(n). One further cut the
readers did NOT ask for, made so the remaining panels tile a 3x4 grid with
no empty cell: the standalone true-drift panel (b) is dropped, since the
same grey curve, with its formula, is the reference in the recovered-u
panel. Restore it by giving (b) the first cell and pushing X, Y, u right,
which then needs a 9th cell (a 4-row layout or an empty cell).

Layout (3 rows x 4 columns):

  Row 1  (a) measured vs ideal  (b) LPF -> X(r)  (c) LPF -> Y(r)  (d) recovered u(r)
  Row 2  (e) Fourier weights at r_n vs r~_n [spans 2]  (f) back on uniform grid [spans 2]
  Row 3  (g) corrected signal [spans 2]  (h) |FFT| ideal / distorted / corrected [spans 2]

Letter map from the 4x4: c->a, g->b, h->c, j->d, k->e, l->f, m->g, d+n->h.

Signal generation, colours, marker styles and the sample positions of the
resampling panels are copied unchanged from fig2_drift_correction_4x4.py so
the only variable between the two renders is the panel set. Two small
adaptations that the merges force: the raw lock-in products (formerly their
own panels) are drawn a little darker in (b), (c) since those traces now
carry that information alone, and formulas that lived in dropped titles
move into the legends of the panels that absorbed them.

Usage:
    .venv/bin/python figures/fig2_drift_correction_condensed.py
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import ConnectionPatch
from scipy.ndimage import gaussian_filter1d
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
# Figure layout: same row height and column width as the 4x4
# (fixed margins, see the 4x4 script for why not constrained layout)
# ═══════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(6.67, 5.4))
gs = fig.add_gridspec(
    3, 4,
    left=0.072, right=0.995, bottom=0.068, top=0.94,
    hspace=0.42, wspace=0.34,
)

xlim_signal = (-0.5, 11)
xlim_fft = (-4 * np.pi, 4 * np.pi)
XLABEL_POS = r'Position $r$ (nm)'
XLABEL_FREQ = r'Frequency $q$ (nm$^{-1}$)'


def label_panel(ax, letter, x=0.03, y=0.95):
    ax.text(x, y, f'({letter})', transform=ax.transAxes,
            fontsize=8, fontweight='bold', va='top', ha='left',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))


def stacked_pair(subspec, curve_color=mode_color):
    inner = subspec.subgridspec(2, 1, hspace=0.38)
    ax_top = fig.add_subplot(inner[0])
    ax_bot = fig.add_subplot(inner[1], sharex=ax_top)
    ax_top.tick_params(labelbottom=False)
    for ax in (ax_top, ax_bot):
        ax.plot(x_dense, mode_dense, color=curve_color, lw=0.8, zorder=1)
        ax.set_xlim(*xlim_signal)
        ax.set_ylim(-1.3, 1.3)
        ax.set_yticks([-1, 0, 1])
    return ax_top, ax_bot


# ── Row 1: measure, demodulate, recover the drift ────────────

# (a) Measured vs ideal  [4x4 (c); absorbs (a): formula moves into legend]
ax_a = fig.add_subplot(gs[0, 0])
ax_a.plot(x, A_perfect, color=ref_color, alpha=0.5, lw=0.6)
ax_a.plot(x, A_distorted, color=uncorr_color, lw=0.6)
ax_a.plot(atoms_perfect, np.cos(k * atoms_perfect), 'o', color=ref_color,
          alpha=0.6, ms=3, mec='white', mew=0.4, zorder=4)
ax_a.plot(atoms_distorted, np.interp(atoms_distorted, x, A_distorted), 'o',
          color=uncorr_color, ms=3, mec='white', mew=0.4, zorder=5)
ax_a.set_xlim(*xlim_signal)
ax_a.set_xlabel(XLABEL_POS)
ax_a.set_ylim(-2, 2)
ax_a.set_ylabel('Height')
ax_a.legend([Line2D([], [], color=ref_color, alpha=0.6, lw=0.6, marker='o', ms=3, mec='white', mew=0.4),
             Line2D([], [], color=uncorr_color, lw=0.6, marker='o', ms=3, mec='white', mew=0.4)],
            [r'Ideal lattice $\cos(kr)$', 'Distorted (measured)'],
            fontsize=5, loc='lower right', handlelength=1.6)
ax_a.set_title(r"Measured $A(r)=\cos[k(r+u(r))]$")
label_panel(ax_a, 'a')

# (b) Filtered cos -> X(r)  [4x4 (g); absorbs (e): product named in legend]
ax_b = fig.add_subplot(gs[0, 1])
ax_b.plot(x, prod_cos, color=uncorr_color, alpha=0.35, lw=0.4, label=r'$A(r)\cos(kr)$')
ax_b.plot(x, X_r, color=uncorr_color, lw=1.2, label=r'$X(r)$ = LPF[$A\cos(kr)$]')
ax_b.plot(x, 0.5 * np.cos(theta_fn(x)), 'k--', lw=0.8, alpha=0.5,
          label=r'True $\frac{1}{2}\cos(\theta)$')
ax_b.set_xlim(*xlim_signal)
ax_b.set_xlabel(XLABEL_POS)
ax_b.set_ylabel('Amplitude')
ax_b.legend(fontsize=4)
ax_b.set_title("LPF → $X(r)$")
label_panel(ax_b, 'b')

# (c) Filtered sin -> Y(r)  [4x4 (h); absorbs (f)]
ax_c = fig.add_subplot(gs[0, 2])
ax_c.plot(x, prod_sin, color=uncorr_color, alpha=0.35, lw=0.4, label=r'$A(r)\sin(kr)$')
ax_c.plot(x, Y_r, color=uncorr_color, lw=1.2, label=r'$Y(r)$ = LPF[$A\sin(kr)$]')
ax_c.plot(x, -0.5 * np.sin(theta_fn(x)), 'k--', lw=0.8, alpha=0.5,
          label=r'True $-\frac{1}{2}\sin(\theta)$')
ax_c.set_xlim(*xlim_signal)
ax_c.set_xlabel(XLABEL_POS)
ax_c.legend(fontsize=4)
ax_c.set_title("LPF → $Y(r)$")
label_panel(ax_c, 'c')

# (d) Recovered drift  [4x4 (j); absorbs (i) via the title, and (b) via the
#     legend, which now carries the formula of the true field]
ax_d = fig.add_subplot(gs[0, 3])
ax_d.plot(x, u_fn(x), color=ref_color, lw=1.5, label=r'True $u(r)=\ln(r+1)/k$')
ax_d.plot(x, u_extracted, color=uncorr_color, ls='--', lw=1.2, label='Recovered $u(r)$')
ax_d.set_xlim(*xlim_signal)
ax_d.set_xlabel(XLABEL_POS)
ax_d.set_ylabel('$u(r)$ (nm)')
ax_d.legend(fontsize=5)
ax_d.set_title(r"Drift $u = \arctan(-Y/X)\,/\,k$")
label_panel(ax_d, 'd')


# ── Row 2: the correction step in Fourier terms ──────────────

# (e) Fourier weights at grid vs corrected positions  [4x4 (k), unchanged]
ax_e_top, ax_e_bot = stacked_pair(gs[1, 0:2])
for ax, xs, ys, c in ((ax_e_top, x_n, y_kernel_grid, uncorr_color),
                      (ax_e_bot, x_corr, y_kernel_corr, corr_color)):
    ax.axhline(0, color='0.75', lw=0.5, zorder=1)
    ax.vlines(xs, 0, ys, color=c, lw=0.9, zorder=4)
    ax.plot(xs, ys, 'o', ms=3, color=c, mec='white', mew=0.3, zorder=5)
ax_e_top.set_ylabel(r'Weight $\cos(qr)$')
ax_e_top.yaxis.set_label_coords(-0.06, -0.19)
ax_e_bot.set_xlabel(XLABEL_POS)
ax_e_top.set_title(r"Fourier weights at grid $r_n$ vs corrected $\tilde{r}_n = r_n + u(r_n)$")
label_panel(ax_e_top, 'e')

h_grid = Line2D([], [], marker='o', ls='none', ms=3, color=uncorr_color,
                mec='white', mew=0.3)
h_corr = Line2D([], [], marker='o', ls='none', ms=3, color=corr_color,
                mec='white', mew=0.3)
h_link = Line2D([], [], color=link_color, lw=0.55)
ax_e_top.legend([h_grid, h_corr, h_link],
                [r'Grid $r_n$', r'Corrected $\tilde{r}_n$', 'Same sample'],
                fontsize=5, loc='upper right', framealpha=0.85,
                borderpad=0.3, handletextpad=0.4, handlelength=1.2,
                labelspacing=0.25)

for xg, yg, xc, yc in zip(x_n, y_kernel_grid, x_corr, y_kernel_corr):
    fig.add_artist(ConnectionPatch(
        xyA=(xg, yg), coordsA=ax_e_top.transData,
        xyB=(xc, yc), coordsB=ax_e_bot.transData,
        color=link_color, lw=0.55, alpha=0.85, zorder=2,
    ))

# (f) Back on the uniform grid  [4x4 (l), unchanged]
ax_f_top, ax_f_bot = stacked_pair(gs[1, 2:4], curve_color=ref_color)
ax_f_top.plot(x_corr, y_reg, 'o', ms=3, color=corr_color,
              mec='white', mew=0.3, zorder=5)
ax_f_bot.plot(x_n, y_out, 'D', ms=3, mfc='white', mec=corr_color,
              mew=0.8, zorder=5)
ax_f_top.set_ylabel('Height')
ax_f_bot.set_ylabel('Height')
ax_f_bot.set_xlabel(XLABEL_POS)
ax_f_top.set_title("Back on the uniform grid")
label_panel(ax_f_top, 'f')

h_reg = Line2D([], [], marker='o', ls='none', ms=3, color=corr_color,
               mec='white', mew=0.3)
h_out = Line2D([], [], marker='D', ls='none', ms=3, mfc='white',
               mec=corr_color, mew=0.8)
h_ideal = Line2D([], [], color=ref_color, lw=0.8)
ax_f_top.legend([h_reg, h_ideal], [r'Measured $y_n$ at $\tilde{r}_n$', 'Ideal lattice'],
                fontsize=5, loc='upper right', framealpha=0.85,
                borderpad=0.3, handletextpad=0.4, handlelength=1.2)
ax_f_bot.legend([h_out], [r'Recomputed $\tilde{y}_n$ at grid $r_n$'],
                fontsize=5, loc='lower right', framealpha=0.85,
                borderpad=0.3, handletextpad=0.4, handlelength=1.2)

_x_arrow = 0.50
fig.add_artist(ConnectionPatch(
    xyA=(_x_arrow, -0.03), coordsA='axes fraction', axesA=ax_f_top,
    xyB=(_x_arrow, 1.03), coordsB='axes fraction', axesB=ax_f_bot,
    arrowstyle='-|>', color='0.15', lw=1.1,
    shrinkA=0, shrinkB=0, mutation_scale=7, zorder=6,
))
ax_f_top.text(_x_arrow + 0.015, -0.23,
              r'$\tilde{x}_q=\Sigma_n\, y_n e^{-iq\tilde{r}_n}$, then $\tilde{y}=F^{-1}\tilde{x}$',
              transform=ax_f_top.transAxes, fontsize=5, color='0.15',
              ha='left', va='center', zorder=6)


# ── Row 3: result, real space and Fourier space ──────────────

# (g) Corrected signal  [4x4 (m), now double width]. The measured signal is
#     drawn faintly behind it so this panel is a before/after in real space,
#     parallel to the merged FFT panel (h) beside it.
ax_g = fig.add_subplot(gs[2, 0:2])
ax_g.plot(x, A_perfect, color=ref_color, alpha=0.6, lw=0.6, ls='--',
          label='Ideal (reference)')
ax_g.plot(x, A_distorted, color=uncorr_color, alpha=0.35, lw=0.6,
          label='Distorted (measured)')
ax_g.plot(x, A_corrected, color=corr_color, lw=0.8, label='Corrected')
ax_g.set_xlim(*xlim_signal)
ax_g.set_ylim(-2, 2)
ax_g.set_ylabel('Height')
ax_g.set_xlabel(XLABEL_POS)
ax_g.legend(fontsize=5, loc='upper right', ncol=3, columnspacing=1.0, handlelength=1.4)
ax_g.set_title("Corrected signal A")
label_panel(ax_g, 'g')

# (h) One FFT panel: before, after, reference  [4x4 (d) + (n) merged]
ax_h = fig.add_subplot(gs[2, 2:4])
ax_h.plot(freqs, fft_perfect, color=ref_color, alpha=0.6, lw=0.8, label='Ideal')
ax_h.plot(freqs, fft_distorted, color=uncorr_color, lw=0.8, label='Distorted')
ax_h.plot(freqs, fft_corrected, color=corr_color, lw=0.8, label='Corrected')
ax_h.set_xlim(*xlim_fft)
ax_h.set_ylabel('|FFT|')
ax_h.set_xlabel(XLABEL_FREQ)
ax_h.legend(fontsize=5)
ax_h.set_title("FFT: peak broadened by drift, sharpened by correction")
label_panel(ax_h, 'h')


# ── Save ──────────────────────────────────────────────────────
outpath = 'figures/fig2_drift_correction_condensed.pdf'
fig.savefig(outpath, dpi=300)
fig.savefig('figures/fig2_drift_correction_condensed.png', dpi=200)
print(f"Saved {outpath} and .png")
