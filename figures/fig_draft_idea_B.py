"""
Figure Idea B: Temporal/Spatial lock-in analogy figure.
10 panels (2x5): Top row = temporal lock-in (1D), Bottom row = spatial lock-in (2D)
"""
import sys
sys.path.insert(0, '/Users/marcosjohnsonnoya/Coding/SparseSampling/.venv/lib/python3.11/site-packages')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d, gaussian_filter
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
from stmpy.driftcorr import sortBraggs

# ═══════════════════════════════════════════
# ROW 1: Temporal lock-in (simulated)
# ═══════════════════════════════════════════
print("Generating temporal lock-in simulation...")
num = 2000
t = np.linspace(0, 40, num)
omega_0 = 5.0
# Slowly varying phase -- linear drift of pi/2 over the window
phi_true = 0.5 * np.pi * (t / t[-1])
V_signal = 10.5 * np.cos(omega_0 * t + phi_true)
V_ref = np.cos(omega_0 * t)
V_ref_sin = np.sin(omega_0 * t)

# Product
V_product = V_signal * V_ref

# Low-pass filter both channels
sigma_lpf_t = 50  # in samples
V_X = gaussian_filter1d(V_signal * V_ref, sigma=sigma_lpf_t)
V_Y = gaussian_filter1d(V_signal * V_ref_sin, sigma=sigma_lpf_t)

# Extracted phase
phi_extracted = np.arctan2(V_Y, V_X)

# ═══════════════════════════════════════════
# ROW 2: Spatial lock-in (real BSCCO data)
# ═══════════════════════════════════════════
print("Loading real data...")
d = stmpy.load("data/Grid Spectroscopy-BSCCO-2022-09-04-002.3ds", biasOffset=False, niceUnits=False)
z = stmpy.tools.lineSubtract(d.Z, 2)

print("Finding Bragg peaks...")
bp = dfc.findBraggs(z, thres=0.2, show=False)
bp_sorted = sortBraggs(bp, s=np.shape(z))
s2, s1 = z.shape
t1 = np.arange(s1, dtype='float')
t2 = np.arange(s2, dtype='float')
x, y = np.meshgrid(t1, t2)
Q1 = 2*np.pi*np.array([(bp_sorted[0][0]-int((s1-1)/2))/s1,
                        (bp_sorted[0][1]-int((s2-1)/2))/s2])

print("Computing spatial lock-in intermediates...")
# Reference cosine
ref_cos = np.cos(Q1[0]*x + Q1[1]*y)

# Product
product_spatial = z * ref_cos

# Lock-in: cos and sin channels
product_cos = z * np.cos(Q1[0]*x + Q1[1]*y)
product_sin = z * np.sin(Q1[0]*x + Q1[1]*y)

# Low-pass filter (Gaussian)
sigma_spatial = 10  # pixels
filtered_cos = gaussian_filter(product_cos, sigma=sigma_spatial)
filtered_sin = gaussian_filter(product_sin, sigma=sigma_spatial)

# Phase map
theta_x = np.arctan2(filtered_sin, filtered_cos)

# ═══════════════════════════════════════════
# CREATE FIGURE
# ═══════════════════════════════════════════
print("Creating figure...")
fig, axes = plt.subplots(2, 5, figsize=(3.375, 1.8),
                         gridspec_kw={'height_ratios': [1, 1.2]})
plt.subplots_adjust(wspace=0.3, hspace=0.5)

labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
col_titles = ['Signal', 'Reference', 'Product', 'Low-pass filter', 'Phase']

# ── Row 1: Temporal ──
# Trim time range for display
t_show = slice(0, 800)

ax = axes[0, 0]
ax.plot(t[t_show], V_signal[t_show], 'b-', linewidth=0.3)
ax.set_ylabel('Temporal', fontsize=5, fontweight='bold')
ax.set_xlim(t[t_show][0], t[t_show][-1])

ax = axes[0, 1]
ax.plot(t[t_show], V_ref[t_show], color='C1', linewidth=0.3)
ax.set_xlim(t[t_show][0], t[t_show][-1])

ax = axes[0, 2]
ax.plot(t[t_show], V_product[t_show], color='gray', linewidth=0.2, alpha=0.7)
ax.plot(t[t_show], V_X[t_show], 'b-', linewidth=0.5)
ax.set_xlim(t[t_show][0], t[t_show][-1])

ax = axes[0, 3]
ax.plot(t[t_show], V_X[t_show], 'b-', linewidth=0.5, label='X')
ax.plot(t[t_show], V_Y[t_show], 'r-', linewidth=0.5, label='Y')
ax.set_xlim(t[t_show][0], t[t_show][-1])

ax = axes[0, 4]
ax.plot(t, phi_extracted, 'b-', linewidth=0.5, label='Extracted')
ax.plot(t, phi_true, 'k--', linewidth=0.5, label='True')
ax.legend(fontsize=3, loc='lower right')

# Clean up temporal row
for ax in axes[0]:
    ax.tick_params(labelsize=4, length=1, width=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for sp in ax.spines.values():
        sp.set_linewidth(0.3)

# ── Row 2: Spatial ──
ax = axes[1, 0]
im = ax.imshow(z, cmap='gray', origin='lower', rasterized=True, interpolation='none')
ax.set_ylabel('Spatial', fontsize=5, fontweight='bold')

ax = axes[1, 1]
im = ax.imshow(ref_cos, cmap='gray', origin='lower', rasterized=True, interpolation='none')

ax = axes[1, 2]
im = ax.imshow(product_spatial, cmap='gray', origin='lower', rasterized=True, interpolation='none')

ax = axes[1, 3]
im = ax.imshow(filtered_cos, cmap='RdBu_r', origin='lower', rasterized=True, interpolation='none')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

ax = axes[1, 4]
im = ax.imshow(theta_x, cmap='RdBu_r', origin='lower', rasterized=True, interpolation='none')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# Clean up spatial row
for ax in axes[1]:
    ax.set_xticks([])
    ax.set_yticks([])

# Add column titles and panel labels
for j, title in enumerate(col_titles):
    axes[0, j].set_title(title, fontsize=5, pad=2)

for idx, ax in enumerate(axes.flat):
    ax.text(0.05, 0.92, f'({labels[idx]})', transform=ax.transAxes,
            fontsize=4, fontweight='bold', va='top',
            color='white' if idx >= 5 else 'black',
            bbox=dict(boxstyle='round,pad=0.1',
                      facecolor='black' if idx >= 5 else 'white',
                      alpha=0.5, linewidth=0))

plt.savefig("figures/fig_draft_idea_B.pdf", dpi=300, bbox_inches='tight')
print("Figure saved to figures/fig_draft_idea_B.pdf")
plt.close('all')
