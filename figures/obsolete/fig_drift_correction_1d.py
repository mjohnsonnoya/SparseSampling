"""
Composite figure: 1D Drift Correction Tutorial (all steps in one figure).
Based on: Hamidian et al., New J. Phys. 14, 053017 (2012)

Generates a multi-panel figure summarizing the Lawler-Fujita drift correction
algorithm in 1D, from perfect lattice through correction.

Layout (3 rows x 4 columns = 12 panels):
  Row 1: Setup + diagnostic FFT
    (a) Perfect lattice, (b) Drift field u(r), (c) Distorted signal,
    (d) FFT comparison (peak broadening)
  Row 2: Lock-in demodulation pipeline
    (e) cos lock-in product, (f) sin lock-in product,
    (g) LPF cos -> X(r), (h) LPF sin -> Y(r)
  Row 3: Phase extraction, drift recovery, and correction
    (i) Extracted theta(r), (j) Recovered u(r),
    (k) Corrected signal, (l) FFT corrected (peak sharpened)

Usage:
    .venv/bin/python figures/fig_drift_correction_1d.py
"""
import sys
sys.path.insert(0, '/Users/marcosjohnsonnoya/Coding/SparseSampling/.venv/lib/python3.11/site-packages')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import string
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
# Signal generation (identical to Drift_Correction_1D_Tutorial)
# ═══════════════════════════════════════════════════════════════
L = 14.0
N = 1000
d = 2.0
k = 2 * np.pi / d

x = np.linspace(0, L, N, endpoint=False)
dx = x[1] - x[0]
A_perfect = np.cos(k * x)

# Drift field: logarithmic (piezo relaxation model)
theta_fn = lambda r: np.log(r + 1)
u_fn = lambda r: theta_fn(r) / k
A_distorted = np.cos(k * x + theta_fn(x))

# Lock-in demodulation
ref_cos = np.cos(k * x)
ref_sin = np.sin(k * x)
prod_cos = A_distorted * ref_cos
prod_sin = A_distorted * ref_sin

# Low-pass filter
sigma_pixels = 80
X_r = gaussian_filter1d(prod_cos, sigma=sigma_pixels)
Y_r = gaussian_filter1d(prod_sin, sigma=sigma_pixels)

# Phase extraction
theta_extracted = np.unwrap(np.arctan2(-Y_r, X_r))
u_extracted = theta_extracted / k

# Correction
r_tilde = x + u_extracted
A_corrected = np.interp(x, r_tilde, A_distorted)

# FFTs
freqs = np.fft.fftshift(np.fft.fftfreq(N, d=dx))
fft_perfect = np.abs(np.fft.fftshift(np.fft.fft(A_perfect)))
fft_distorted = np.abs(np.fft.fftshift(np.fft.fft(A_distorted)))
fft_corrected = np.abs(np.fft.fftshift(np.fft.fft(A_corrected)))

# Atom positions
atoms_perfect = np.arange(0, 11, d)
atoms_distorted = atoms_perfect - u_fn(atoms_perfect)

# ═══════════════════════════════════════════════════════════════
# Figure layout: 3 rows × 4 columns
# ═══════════════════════════════════════════════════════════════
fig, axes = plt.subplots(3, 4, figsize=(6.67, 5))
xlim_signal = (-0.5, 11)
xlim_fft = (-2, 2)

def label_panel(ax, letter, x=0.03, y=0.95):
    ax.text(x, y, f'({letter})', transform=ax.transAxes,
            fontsize=8, fontweight='bold', va='top', ha='left',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))


# ── Row 1: Setup + diagnostic FFT ────────────────────────────

# (a) Perfect lattice
ax = axes[0, 0]
ax.plot(x, A_perfect, 'C0', lw=0.8)
ax.plot(atoms_perfect, atoms_perfect * 0, 'C0.', ms=5)
ax.set_xlim(*xlim_signal)
ax.set_ylim(-2, 2)
ax.set_ylabel('Height')
ax.set_title("Perfect lattice")
label_panel(ax, 'a')

# (b) Drift field u(r)
ax = axes[0, 1]
ax.plot(x, u_fn(x), 'k', lw=1.2)
ax.set_xlim(*xlim_signal)
ax.set_ylabel('$u(r)$ (nm)')
ax.set_title("Drift field")
label_panel(ax, 'b')

# (c) Distorted signal overlaid
ax = axes[0, 2]
ax.plot(x, A_perfect, 'C0', alpha=0.3, lw=0.6, label='Perfect lattice')
ax.plot(x, A_distorted, 'r', lw=0.6, label='Distorted (measured)')
ax.plot(atoms_perfect, atoms_perfect * 0, 'C0.', ms=4)
ax.plot(atoms_distorted, atoms_distorted * 0, 'ro', ms=3, mew=0.5)
for i, a in enumerate(atoms_perfect):
    drift = u_fn(a)
    if drift > 0.05:
        ax.annotate('', xy=[a - drift, 0.9], xytext=[a, 0.9],
                    arrowprops=dict(arrowstyle='-|>', color='r', lw=0.6))
ax.set_xlim(*xlim_signal)
ax.set_ylim(-2, 2)
ax.legend(fontsize=5, loc='lower right')
ax.set_title("Distorted measurement")
label_panel(ax, 'c')

# (d) FFT: perfect vs distorted
ax = axes[0, 3]
ax.plot(freqs, fft_perfect, 'C0', lw=0.8, alpha=0.5, label='Perfect')
ax.plot(freqs, fft_distorted, 'r', lw=0.8, label='Distorted')
ax.set_xlim(*xlim_fft)
ax.set_ylabel('|FFT|')
ax.legend(fontsize=5)
ax.set_title("FFT: peak broadening")
label_panel(ax, 'd')


# ── Row 2: Lock-in demodulation pipeline ─────────────────────

# (e) cos lock-in product (raw)
ax = axes[1, 0]
ax.plot(x, prod_cos, 'C0', lw=0.5, alpha=0.6, label=r'$A(r) \cdot \cos(kr)$')
ax.plot(x, 0.5 * np.cos(theta_fn(x)), 'k--', lw=1, alpha=0.7,
        label=r'$\frac{1}{2}\cos(\theta)$ (slow)')
ax.set_xlim(*xlim_signal)
ax.set_ylabel('Amplitude')
ax.legend(fontsize=4, loc='lower left')
ax.set_title(r"$A \cdot \cos(kr)$")
label_panel(ax, 'e')

# (f) sin lock-in product (raw)
ax = axes[1, 1]
ax.plot(x, prod_sin, 'C1', lw=0.5, alpha=0.6, label=r'$A(r) \cdot \sin(kr)$')
ax.plot(x, -0.5 * np.sin(theta_fn(x)), 'k--', lw=1, alpha=0.7,
        label=r'$-\frac{1}{2}\sin(\theta)$ (slow)')
ax.set_xlim(*xlim_signal)
ax.legend(fontsize=4, loc='lower left')
ax.set_title(r"$A \cdot \sin(kr)$")
label_panel(ax, 'f')

# (g) Filtered cos → X(r)
ax = axes[1, 2]
ax.plot(x, prod_cos, 'C0', alpha=0.2, lw=0.4, label='Raw product')
ax.plot(x, X_r, 'C0', lw=1.2, label=r'$X(r)$ = LPF[$A \cdot \cos$]')
ax.plot(x, 0.5 * np.cos(theta_fn(x)), 'k--', lw=0.8, alpha=0.5,
        label=r'True $\frac{1}{2}\cos(\theta)$')
ax.set_xlim(*xlim_signal)
ax.legend(fontsize=4)
ax.set_title("LPF → $X(r)$")
label_panel(ax, 'g')

# (h) Filtered sin → Y(r)
ax = axes[1, 3]
ax.plot(x, prod_sin, 'C1', alpha=0.2, lw=0.4, label='Raw product')
ax.plot(x, Y_r, 'C1', lw=1.2, label=r'$Y(r)$ = LPF[$A \cdot \sin$]')
ax.plot(x, -0.5 * np.sin(theta_fn(x)), 'k--', lw=0.8, alpha=0.5,
        label=r'True $-\frac{1}{2}\sin(\theta)$')
ax.set_xlim(*xlim_signal)
ax.legend(fontsize=4)
ax.set_title("LPF → $Y(r)$")
label_panel(ax, 'h')


# ── Row 3: Phase extraction → drift → correction ─────────────

# (i) Extracted phase θ(r)
ax = axes[2, 0]
ax.plot(x, theta_fn(x), 'k', lw=1.5, alpha=0.4, label=r'True $\theta(r) = \ln(r+1)$')
ax.plot(x, theta_extracted, 'r--', lw=1.2, label=r'Extracted $\theta(r)$')
ax.set_xlim(*xlim_signal)
ax.set_ylabel(r'$\theta(r)$ (rad)')
ax.set_xlabel('Position (nm)')
ax.legend(fontsize=5)
ax.set_title(r"Phase: $\theta = \arctan(-Y/X)$")
label_panel(ax, 'i')

# (j) Recovered drift field
ax = axes[2, 1]
ax.plot(x, u_fn(x), 'k', lw=1.5, alpha=0.4, label='True $u(r)$')
ax.plot(x, u_extracted, 'r--', lw=1.2, label='Recovered $u(r)$')
ax.set_xlim(*xlim_signal)
ax.set_ylabel('$u(r)$ (nm)')
ax.set_xlabel('Position (nm)')
ax.legend(fontsize=5)
ax.set_title("Drift: $u = \\theta / k$")
label_panel(ax, 'j')

# (k) Corrected signal A
ax = axes[2, 2]
ax.plot(x, A_corrected, 'C2', lw=0.8, label='Corrected')
ax.plot(x, A_perfect, 'C0', alpha=0.3, lw=0.6, ls='--', label='Perfect (reference)')
ax.set_xlim(*xlim_signal)
ax.set_ylim(-2, 2)
ax.set_xlabel('Position (nm)')
ax.legend(fontsize=5)
ax.set_title("Corrected signal A")
label_panel(ax, 'k')

# (l) FFT of corrected A
ax = axes[2, 3]
ax.plot(freqs, fft_perfect, 'C0', alpha=0.3, lw=0.8, label='Perfect')
ax.plot(freqs, fft_corrected, 'C2', lw=0.8, label='Corrected')
ax.set_xlim(*xlim_fft)
ax.set_ylabel('|FFT|')
ax.legend(fontsize=5)
ax.set_title("FFT: peak sharpened")
label_panel(ax, 'l')


# ── Final layout ──────────────────────────────────────────────
plt.tight_layout(h_pad=0.3, w_pad=0.3)

# Align ylabels within each column
for col in range(4):
    fig.align_ylabels(axes[:, col])

# Save
outpath = 'figures/fig_drift_correction_1d.pdf'
fig.savefig(outpath, dpi=300, bbox_inches='tight', pad_inches=0.05)
print(f"Saved to {outpath}")

# Also save PNG for quick viewing
outpath_png = 'figures/fig_drift_correction_1d.png'
fig.savefig(outpath_png, dpi=200, bbox_inches='tight', pad_inches=0.05)
print(f"Saved to {outpath_png}")
