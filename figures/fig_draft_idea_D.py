"""
Figure Idea D: Hybrid analogy + real data figure.
9 panels (3x3): Row 1 = temporal (1D), Row 2 = spatial sim, Row 3 = real STM data
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

# ═══════════════════════════════════════════
# ROW 1: Temporal lock-in (simulated)
# ═══════════════════════════════════════════
print("Generating temporal lock-in simulation...")
num = 2000
t = np.linspace(0, 40, num)
omega_0 = 5.0
phi_true = 0.5 * np.pi * (t / t[-1])
V_signal = 10.5 * np.cos(omega_0 * t + phi_true)
V_ref = np.cos(omega_0 * t)

sigma_lpf_t = 50
V_X = gaussian_filter1d(V_signal * V_ref, sigma=sigma_lpf_t)
V_Y = gaussian_filter1d(V_signal * np.sin(omega_0 * t), sigma=sigma_lpf_t)
phi_extracted = np.arctan2(V_Y, V_X)

# ═══════════════════════════════════════════
# ROW 2: Spatial lock-in (simulated lattice with drift)
# ═══════════════════════════════════════════
print("Generating simulated lattice with drift...")
N = 128
a0_pix = 10
x_grid = np.arange(N, dtype=float)
y_grid = np.arange(N, dtype=float)
X, Y = np.meshgrid(x_grid, y_grid)

Qx_sim = np.array([2*np.pi/a0_pix, 0.0])
Qy_sim = np.array([0.0, 2*np.pi/a0_pix])

# Smooth drift field (exaggerated for visibility)
ux_true = 2.0 * X / N + 0.3 * np.sin(2*np.pi*Y / (N/2))
uy_true = 1.5 * Y / N

# Drifted lattice
T_sim = (np.cos(Qx_sim[0]*(X + ux_true) + Qx_sim[1]*(Y + uy_true)) +
         np.cos(Qy_sim[0]*(X + ux_true) + Qy_sim[1]*(Y + uy_true)))
T_sim += 0.1 * np.random.randn(N, N)

# Reference cosine (Q_x direction only)
ref_cos_sim = np.cos(Qx_sim[0]*X + Qx_sim[1]*Y)

# Spatial lock-in
sigma_sim = 5 * a0_pix / (2*np.pi)
filt_cos_sim = gaussian_filter(T_sim * np.cos(Qx_sim[0]*X + Qx_sim[1]*Y), sigma=sigma_sim)
filt_sin_sim = gaussian_filter(T_sim * np.sin(Qx_sim[0]*X + Qx_sim[1]*Y), sigma=sigma_sim)
theta_x_sim = np.arctan2(filt_sin_sim, filt_cos_sim)

# ═══════════════════════════════════════════
# ROW 3: Real STM data
# ═══════════════════════════════════════════
print("Loading real data...")
d = stmpy.load("data/Grid Spectroscopy-BSCCO-2022-09-04-002.3ds", biasOffset=False, niceUnits=False)
z = stmpy.tools.lineSubtract(d.Z, 2)

print("Running drift correction pipeline...")
bp = dfc.findBraggs(z, thres=0.2, show=False)
thetax, thetay, Q1, Q2 = dfc.phasemap(z, bp=bp, sigma=10, method='lockin')
thetaxf = dfc.fixphaseslip(thetax, method='unwrap')
thetayf = dfc.fixphaseslip(thetay, method='unwrap')
ux, uy = dfc.driftmap(thetaxf, thetayf, Q1, Q2, method='lockin')
z_corr = dfc.driftcorr(z, ux=ux, uy=uy, method='lockin', interpolation='cubic')

z_fft = stmpy.tools.fft(z, zeroDC=True)
z_corr_fft = stmpy.tools.fft(z_corr, zeroDC=True)

# ═══════════════════════════════════════════
# CREATE FIGURE: 3 rows x 3 columns
# ═══════════════════════════════════════════
print("Creating figure...")
fig, axes = plt.subplots(3, 3, figsize=(3.375, 4.0),
                         gridspec_kw={'height_ratios': [0.8, 1.0, 1.0]})
plt.subplots_adjust(wspace=0.35, hspace=0.55)

labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
col_titles = ['Signal / Input', 'Reference', 'Extracted / Result']
row_labels = ['Temporal\n(1D)', 'Spatial\n(simulated)', 'Real\nSTM data']

# ── Row 1: Temporal ──
t_show = slice(0, 800)

ax = axes[0, 0]
ax.plot(t[t_show], V_signal[t_show], 'b-', linewidth=0.3)

ax = axes[0, 1]
ax.plot(t[t_show], V_ref[t_show], color='C1', linewidth=0.3)

ax = axes[0, 2]
ax.plot(t, phi_extracted, 'b-', linewidth=0.5, label='Extracted')
ax.plot(t, phi_true, 'k--', linewidth=0.5, label='True')
ax.legend(fontsize=3, loc='lower right')

for ax in axes[0]:
    ax.tick_params(labelsize=4, length=1, width=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for sp in ax.spines.values():
        sp.set_linewidth(0.3)

# ── Row 2: Simulated spatial ──
ax = axes[1, 0]
ax.imshow(T_sim, cmap='gray', origin='lower', rasterized=True, interpolation='none')

ax = axes[1, 1]
ax.imshow(ref_cos_sim, cmap='gray', origin='lower', rasterized=True, interpolation='none')

ax = axes[1, 2]
im = ax.imshow(theta_x_sim, cmap='RdBu_r', origin='lower', rasterized=True, interpolation='none')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

for ax in axes[1]:
    ax.set_xticks([])
    ax.set_yticks([])

# ── Row 3: Real data ──
# (g) Raw topo with FFT inset
ax = axes[2, 0]
ax.imshow(z, cmap='gray', origin='lower', rasterized=True, interpolation='none')
# FFT inset
inset_g = ax.inset_axes([0.58, 0.58, 0.38, 0.38])
fft_disp = np.log1p(np.abs(z_fft))
inset_g.imshow(fft_disp, cmap='inferno', origin='lower', rasterized=True, interpolation='none')
inset_g.set_xticks([])
inset_g.set_yticks([])
inset_g.patch.set_edgecolor('white')
inset_g.patch.set_linewidth(0.5)

# (h) Drift field u_x
ax = axes[2, 1]
im = ax.imshow(ux, cmap='RdBu_r', origin='lower', rasterized=True, interpolation='none')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# (i) Corrected topo with FFT inset
ax = axes[2, 2]
ax.imshow(z_corr, cmap='gray', origin='lower', rasterized=True, interpolation='none')
# FFT inset
inset_i = ax.inset_axes([0.58, 0.58, 0.38, 0.38])
fft_corr_disp = np.log1p(np.abs(z_corr_fft))
inset_i.imshow(fft_corr_disp, cmap='inferno', origin='lower', rasterized=True, interpolation='none')
inset_i.set_xticks([])
inset_i.set_yticks([])
inset_i.patch.set_edgecolor('white')
inset_i.patch.set_linewidth(0.5)

for ax in axes[2]:
    ax.set_xticks([])
    ax.set_yticks([])

# ── Labels and titles ──
for j, title in enumerate(col_titles):
    axes[0, j].set_title(title, fontsize=5, pad=2)

for i, label in enumerate(row_labels):
    axes[i, 0].set_ylabel(label, fontsize=5, fontweight='bold', labelpad=8)

for idx, ax in enumerate(axes.flat):
    is_image = idx >= 3  # rows 2 and 3 are images
    ax.text(0.05, 0.92, f'({labels[idx]})', transform=ax.transAxes,
            fontsize=5, fontweight='bold', va='top',
            color='white' if is_image else 'black',
            bbox=dict(boxstyle='round,pad=0.1',
                      facecolor='black' if is_image else 'white',
                      alpha=0.5, linewidth=0))

# Horizontal separator between analogy (rows 0-1) and real data (row 2)
# Draw a thin line across the figure
line_y = 0.345  # approximate y position between row 2 and row 3
fig.add_artist(plt.Line2D([0.05, 0.95], [line_y, line_y],
               transform=fig.transFigure, color='gray',
               linewidth=0.5, linestyle='--'))

plt.savefig("figures/fig_draft_idea_D.pdf", dpi=300, bbox_inches='tight')
print("Figure saved to figures/fig_draft_idea_D.pdf")
plt.close('all')
