"""
driftcorr_method_comparison.py
--------------------------------
Controlled comparison of stmpy's two drift-correction APPLICATION methods,
isolating the resampling step (which is what Jenny's (a) vs (b) question is
about) from the drift-estimation step.

Workflow:
  1) Load a real BSCCO topo and preprocess it (nsigma_local + lineSubtract,
     same recipe as Sparse_sampling_figure_plot_for_40_nm_map.ipynb cell 6).
  2) Construct a KNOWN, smooth, sub-pixel drift field (ux, uy) with a
     logarithmic-in-y profile (physical model for piezo thermal creep:
     drift accumulates roughly as log(scan_time), and scan time scales with
     the slow-axis row index).
  3) Hand the SAME (ux, uy) to driftcorr two ways:
        (b) method='lockin', interpolation='cubic'  -> bicubic spline
        (a) method='convolution'                    -> stmpy's invfft path
  4) Subtract.  Compare in real space and in Fourier space.

Sub-pixel ux/uy means no out-of-bounds zeroing, so the residual is the pure
M^H-vs-M^{-1} structural difference plus the convolution path's
mean-subtract/add-back DC handling -- the things Jenny is actually asking
about.

Plotting follows stmpy.driftcorr.quick_plot conventions:
    real space : cmap=stmpy.cm.blue2,  clims=[mean-3*std, mean+3*std]
    FT         : cmap=stmpy.cm.gray_r, clims=[0,           mean+3*std]
    signed diff: cmap=stmpy.cm.redblue, clims symmetric about 0
FFTs use stmpy.tools.fft(..., zeroDC=True).
"""
from pathlib import Path
import warnings
import numpy as np
import matplotlib.pyplot as plt

import stmpy
import stmpy.tools as st
import stmpy.driftcorr as dfc

# silence the harmless Accelerate-BLAS false-positive FPE warnings
for msg in ("divide by zero encountered in matmul",
            "overflow encountered in matmul",
            "invalid value encountered in matmul"):
    warnings.filterwarnings("ignore", message=msg)

HERE = Path(__file__).resolve().parent
TOPO = HERE.parent / "data" / "2022-09-05_BSCCO_SparseSamplingTopo001.sxm"
OUT  = HERE / "driftcorr_method_comparison.pdf"

# ------------------------------------------------------------------ load
t = stmpy.load(str(TOPO))
Z = t.Z if t.Z.ndim == 2 else t.Z[0]
z = st.lineSubtract(st.nsigma_local(Z), 2)
s2, s1 = z.shape
print(f"topo shape {z.shape}   rms={np.sqrt((z**2).mean()):.3g}")

# ------------------- construct a KNOWN smooth sub-pixel drift field
# Physically-motivated STM thermal-creep model: drift accumulates over scan
# time, and scan time scales with the slow-axis row index (here, y). Piezo
# creep relaxation has a roughly logarithmic time dependence, so we model
#     u(y) ~ log(1 + alpha * y / (s2-1))
# along the slow axis. Normalized so the max sub-pixel offset is 0.4 px,
# guaranteeing no out-of-bounds clipping. The ratio (ux : uy) = 1 : 0.5 just
# gives a non-trivial 2D shift; both grow logarithmically with y.
yy, xx = np.mgrid[0:s2, 0:s1]
alpha = 9.0
profile = np.log1p(alpha * yy / (s2 - 1))     # 0 .. log(1+alpha)
profile = profile / profile.max()              # normalized to [0, 1]
ux = 0.40 * profile                            # max 0.40 px along x
uy = 0.20 * profile                            # max 0.20 px along y
print(f"log drift profile: alpha={alpha}, |ux|_max={np.abs(ux).max():.3f} px, "
      f"|uy|_max={np.abs(uy).max():.3f} px   (sub-pixel, monotonic in y)")

# --------------- apply the SAME (ux, uy) via the two different methods
z_b = dfc.driftcorr(z, ux=ux, uy=uy, method='lockin', interpolation='cubic')
z_a = dfc.driftcorr(z, ux=ux, uy=uy, method='convolution')

diff = z_a - z_b
rel  = np.linalg.norm(diff) / np.linalg.norm(z_b)

print(f"(b) lockin+cubic   rms={np.sqrt((z_b**2).mean()):.3e}")
print(f"(a) convolution    rms={np.sqrt((z_a**2).mean()):.3e}")
print(f"diff = a - b       rms={np.sqrt((diff**2).mean()):.3e}")
print(f"relative ||a-b|| / ||b|| = {rel:.3e}")

# ------------------------------------------------------------------ plot
# Match stmpy.driftcorr.quick_plot conventions exactly so the figure reads
# the same as every other display in the project.
THRES = 3  # quick_plot default: clip at +/- thres*std (real space) or 0..mean+thres*std (FT)

def clims_rspace(img):
    c, s = float(np.mean(img)), float(np.std(img))
    return [c - THRES * s, c + THRES * s]

def clims_ft(img):
    c, s = float(np.mean(img)), float(np.std(img))
    return [0.0, c + THRES * s]

def clims_signed(img):
    v = THRES * float(np.std(img))
    return [-v, v]

# FFTs follow project convention: stmpy.tools.fft(..., zeroDC=True)
ft_b   = st.fft(z_b,   zeroDC=True)
ft_a   = st.fft(z_a,   zeroDC=True)
ft_dif = st.fft(diff,  zeroDC=True)

fig, axes = plt.subplots(2, 3, figsize=(13.2, 8.6), constrained_layout=True)

def show(ax, img, title, cmap, clims):
    im = ax.imshow(img, clim=clims, cmap=cmap, origin='lower', rasterized=True)
    ax.set_aspect(1)
    ax.set_title(title, fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)

show(axes[0, 0], z_a,   "(a) convolution",
     stmpy.cm.blue2,   clims_rspace(z_a))
show(axes[0, 1], z_b,   "(b) lockin + bicubic spline",
     stmpy.cm.blue2,   clims_rspace(z_b))
show(axes[0, 2], diff,  "(a) - (b)  (signed)",
     stmpy.cm.blue2, clims_signed(diff))
show(axes[1, 0], ft_a,  "FFT (a)",
     stmpy.cm.gray_r,  clims_ft(ft_a))
show(axes[1, 1], ft_b,  "FFT (b)",
     stmpy.cm.gray_r,  clims_ft(ft_b))
show(axes[1, 2], ft_dif, "FFT of (a) - (b)",
     stmpy.cm.gray_r,  clims_ft(ft_dif))

fig.suptitle(
    "BSCCO topo, known logarithmic drift"
    f"   |   rel ||a-b||/||b|| = {rel:.2e}", fontsize=11)
fig.savefig(OUT, dpi=140)
print(f"saved -> {OUT}")
