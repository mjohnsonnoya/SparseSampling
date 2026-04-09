"""
Figure Idea A: Pipeline figure for drift correction.
8 panels (2x4): Raw topo -> FFT -> Phase maps -> Drift fields -> Corrected topo -> Corrected FFT
"""
import sys
sys.path.insert(0, '/Users/marcosjohnsonnoya/Coding/SparseSampling/.venv/lib/python3.11/site-packages')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import warnings
warnings.filterwarnings('ignore')

try:
    plt.rcParams['font.family'] = 'Arial'
except:
    plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 6

import stmpy
import stmpy.tools
import stmpy.driftcorr as dfc

# ── Load data ──
print("Loading data...")
d = stmpy.load("data/Grid Spectroscopy-BSCCO-2022-09-04-002.3ds", biasOffset=False, niceUnits=False)
z = stmpy.tools.lineSubtract(d.Z, 2)
print(f"Topo shape: {z.shape}")

# ── Drift correction pipeline (step by step) ──
print("Finding Bragg peaks...")
bp = dfc.findBraggs(z, thres=0.2, show=False)

print("Computing phase maps...")
thetax, thetay, Q1, Q2 = dfc.phasemap(z, bp=bp, sigma=10, method='lockin')

print("Fixing phase slips...")
thetaxf = dfc.fixphaseslip(thetax, method='unwrap')
thetayf = dfc.fixphaseslip(thetay, method='unwrap')

print("Computing drift fields...")
ux, uy = dfc.driftmap(thetaxf, thetayf, Q1, Q2, method='lockin')

print("Applying drift correction...")
z_corr = dfc.driftcorr(z, ux=ux, uy=uy, method='lockin', interpolation='cubic')

print("Computing FFTs...")
z_fft = stmpy.tools.fft(z, zeroDC=True)
z_corr_fft = stmpy.tools.fft(z_corr, zeroDC=True)

# ── Create figure ──
print("Creating figure...")
fig, axes = plt.subplots(2, 4, figsize=(3.375, 2.2))
plt.subplots_adjust(wspace=0.35, hspace=0.4)

labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
titles = [r'$T(\mathbf{r})$', r'$|\widetilde{T}(\mathbf{q})|^2$',
          r'$\theta_x(\mathbf{r})$', r'$\theta_y(\mathbf{r})$',
          r'$u_x(\mathbf{r})$', r'$u_y(\mathbf{r})$',
          r'$T_c(\mathbf{r})$', r'$|\widetilde{T}_c(\mathbf{q})|^2$']

# Row 1
# (a) Raw topo
ax = axes[0, 0]
im = ax.imshow(z, cmap='gray', origin='lower', rasterized=True, interpolation='none')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# (b) FFT of raw topo
ax = axes[0, 1]
fft_display = np.log1p(np.abs(z_fft))
im = ax.imshow(fft_display, cmap='inferno', origin='lower', rasterized=True, interpolation='none')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# (c) Phase map theta_x
ax = axes[0, 2]
im = ax.imshow(thetaxf, cmap='RdBu_r', origin='lower', rasterized=True, interpolation='none')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# (d) Phase map theta_y
ax = axes[0, 3]
im = ax.imshow(thetayf, cmap='RdBu_r', origin='lower', rasterized=True, interpolation='none')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# Row 2
# (e) Drift field u_x
ax = axes[1, 0]
im = ax.imshow(ux, cmap='RdBu_r', origin='lower', rasterized=True, interpolation='none')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# (f) Drift field u_y
ax = axes[1, 1]
im = ax.imshow(uy, cmap='RdBu_r', origin='lower', rasterized=True, interpolation='none')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# (g) Corrected topo
ax = axes[1, 2]
im = ax.imshow(z_corr, cmap='gray', origin='lower', rasterized=True, interpolation='none')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# (h) FFT of corrected topo
ax = axes[1, 3]
fft_corr_display = np.log1p(np.abs(z_corr_fft))
im = ax.imshow(fft_corr_display, cmap='inferno', origin='lower', rasterized=True, interpolation='none')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# Add labels and titles
for idx, ax in enumerate(axes.flat):
    ax.set_title(titles[idx], fontsize=5, pad=2)
    ax.text(0.05, 0.92, f'({labels[idx]})', transform=ax.transAxes,
            fontsize=5, fontweight='bold', va='top', color='white',
            bbox=dict(boxstyle='round,pad=0.1', facecolor='black', alpha=0.5, linewidth=0))
    ax.set_xticks([])
    ax.set_yticks([])

plt.savefig("figures/fig_draft_idea_A.pdf", dpi=300, bbox_inches='tight')
print("Figure saved to figures/fig_draft_idea_A.pdf")
plt.close('all')
