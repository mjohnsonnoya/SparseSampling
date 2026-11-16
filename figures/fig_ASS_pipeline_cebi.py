"""
Appendix Fig. (ASS pipeline) rebuilt on CeBi. PRELIMINARY, 2026-09-12.

The manuscript's paper/figure_ASS_pipeline.pdf was generated from the BSCCO
dI/dV map (Adaptive_sparse_sampling.ipynb cells 38-55, d = data[0]), i.e.
the material the main text says has no topographically separable defects.
This script runs the identical pipeline on the CeBi map used by the
main-text ASS figure (2019-07-11-002, dI/dV layer 2 at -300 mV), so the
two figures agree. It is still dI/dV standing in for topography: the CeBi
.spy carries no height channel and no CeBi topography exists in data/.

Pipeline and parameters copied from the notebook:
  invFT_filter(width=5, lattice=True)  -> lattice-only map
  find_extrema(n=(19, 0))              -> 19 strongest lattice maxima
  gauss2d radius 25*intensity          -> probability mask
  5% uniform + 5% rejection-sampled from the mask
The only CeBi-specific input is the Bragg-peak list, found automatically as
the four strongest |FT| maxima away from the centre (radius ~50 px, square).

Two detection modes (argv[1], default 'lattice'):
  lattice  : the notebook pipeline verbatim (Bragg-pass filter, 19 strongest
             lattice maxima). On CeBi the 19 values differ by <4%, so the
             ranking barely discriminates; the defect wins by luck.
  lowpass  : band-pass instead of Bragg-pass: Gaussian smooth (LP_SIGMA px)
             minus a large-scale Gaussian background (BG_SIGMA px), which
             removes both the lattice and slow tilt/terrace variation. Defects
             are then the connected components where |deviation| exceeds
             Z_THRESH robust sigma (MAD); each component gives one site at its
             intensity-weighted centre. Site weight saturates at 3*Z_THRESH so
             one giant protrusion cannot starve the smaller defects of mask
             radius. This is the "feature region" reading of the caption's
             "selected Bragg or feature regions". (2026-09-13: replaced the
             fixed-count find_extrema step, which returned image corners and
             lattice texture on real topography.)

Usage:
    .venv/bin/python figures/fig_ASS_pipeline_cebi.py [lattice|lowpass] [path.sxm] [--paper]

--paper renders at true single-column width (3.375 in, Arial, 6.5 pt titles)
and writes figures/out/figure_ASS_pipeline_cebi_topo.pdf, the file the manuscript
includes (copied to paper/). Without it, a large preview is written.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter, gaussian_filter, label, center_of_mass
import os
import stmpy
import stmpy.tools as st
import warnings
warnings.filterwarnings('ignore')

try:
    plt.rcParams['font.family'] = 'Arial'
except Exception:
    pass

MODE = sys.argv[1] if len(sys.argv) > 1 else 'lattice'
assert MODE in ('lattice', 'lowpass'), MODE
# Optional argv[2]: path to a Nanonis .sxm topography (2026-09-13). When given,
# the pipeline runs on REAL topography (line-subtracted Z) instead of the dI/dV
# stand-in, which is what the manuscript protocol actually describes.
PAPER = '--paper' in sys.argv
_args = [a for a in sys.argv[2:] if not a.startswith('--')]
SXM = _args[0] if _args else None
LP_SIGMA = 2.0      # px, small-scale Gaussian smoothing (lowpass mode)
BG_SIGMA = 15.0     # px, large-scale background removed (lowpass mode)
Z_THRESH = 5.0      # robust z-score threshold for a pixel to count as defect
MIN_PX = 4          # smallest component kept (drops single-pixel noise)
MAX_ASPECT = 3.0    # components longer than this along the fast-scan axis are streaks
MERGE_NM = 2.0      # sites closer than this (nm) merge into one (defect core + ring)
np.random.seed(0)

# ── data ──────────────────────────────────────────────────────
if SXM is None:
    d = stmpy.load('data/2019-07-11-002 LIY local corr new.spy', biasOffset=False)
    LAYER = 2                               # -300 mV, same layer as figure3_ASS
    z_test = d.LIY[LAYER] / np.mean(d.LIY[LAYER])
    L_NM = 25.0                             # Drive doc "CeBi - Data summary 2020": 25 nm map
    TAG = ''
else:
    d = stmpy.load(SXM)
    z = st.lineSubtract(d.Z, 1)
    z_test = (z - z.min()) / (z.max() - z.min()) + 0.5     # positive, O(1), like the dI/dV stand-in
    L_NM = float(np.ravel(d.header['scan_range'])[0]) * 1e9
    TAG = '_' + os.path.basename(SXM).replace('.sxm', '')
nx, ny = z_test.shape
MERGE_PX = MERGE_NM * nx / L_NM

# ── (b) FT and Bragg peaks ────────────────────────────────────
z_ft = st.fft(z_test, zeroDC=True)
c0 = nx // 2
rr = np.hypot(*np.meshgrid(np.arange(nx) - c0, np.arange(ny) - c0))
mf = maximum_filter(z_ft, size=7)
yy, xx = np.nonzero((z_ft == mf) & (rr > 12))
order = np.argsort(z_ft[yy, xx])[::-1][:4]
masks = np.array([[xx[o], yy[o]] for o in order])      # (x, y) as in the notebook
print("Bragg peaks (x, y):", masks.tolist())


# ── notebook helpers (verbatim) ───────────────────────────────
def invFT_filter(A, bp, width=2, lattice=False):
    g = 0
    x = np.arange(np.shape(A)[-1])
    for i in range(len(bp)):
        x0, y0 = bp[i]
        g = g + st.gauss2d(x, x, p=[x0, y0, width, width, 1, 0])
    mask = g if lattice else 1 - g
    A_ft_masked = st.fft(A, output='complex') * mask
    return np.real(st.ifft(A_ft_masked))


def generate_random_coordinates(num_points, nx, mask):
    out = []
    while len(out) < num_points:
        x, y = np.random.randint(0, nx, size=2)
        if np.random.rand() < mask[x, y]:
            out.append([x, y])
    return np.array(out)


# ── (c) filtered map, (d) extrema, (e) probability mask ──────
if MODE == 'lattice':
    z_masked = invFT_filter(z_test, bp=masks, width=5, lattice=True)
    coords = st.find_extrema(z_masked, n=(19, 0))
    g_intensity = np.array([z_masked[int(x), int(y)] for x, y in coords])
    intensity = (g_intensity - z_masked.min()) / (z_masked.max() - z_masked.min())
else:
    z_masked = gaussian_filter(z_test, LP_SIGMA) - gaussian_filter(z_test, BG_SIGMA)
    # per-row median removal: kills tip-change streaks (wide along the fast-scan
    # axis, a few rows tall) while leaving compact defects untouched
    z_masked = z_masked - np.median(z_masked, axis=1, keepdims=True)
    sig = 1.4826 * np.median(np.abs(z_masked - np.median(z_masked)))   # robust sigma (MAD)
    zmap = (z_masked - np.median(z_masked)) / sig
    lab, ncomp = label(np.abs(zmap) > Z_THRESH)
    edge = 2 * LP_SIGMA
    sites, zpk = [], []
    for i in range(1, ncomp + 1):
        m = lab == i
        if m.sum() < MIN_PX:
            continue
        cy, cx = center_of_mass(np.abs(zmap), lab, i)
        if not (edge < cy < nx - edge and edge < cx < ny - edge):
            continue                                   # filter-edge artefacts
        rr_, cc_ = np.nonzero(m)
        if (np.ptp(cc_) + 1) > MAX_ASPECT * (np.ptp(rr_) + 1):
            continue                                   # tip-change streak along the scan line
        sites.append([cy, cx])
        zpk.append(zmap[m][np.argmax(np.abs(zmap[m]))])
    # merge sites closer than MERGE_PX, keeping the strongest (defect core + ring)
    order_ = np.argsort(-np.abs(zpk))
    kept = []
    for i in order_:
        if all(np.hypot(sites[i][0] - sites[j][0], sites[i][1] - sites[j][1]) > MERGE_PX for j in kept):
            kept.append(i)
    coords = np.array([sites[i] for i in kept])
    zpk = np.array([zpk[i] for i in kept])
    print(f"lowpass: {len(coords)} defects from {ncomp} components above {Z_THRESH} sigma; peak z:",
          np.round(zpk, 1).tolist())
    intensity = np.minimum(np.abs(zpk), 3 * Z_THRESH) / (3 * Z_THRESH)   # saturating weight
r = 25 * intensity
xg = np.arange(nx)
mask = 0
for i in range(len(coords)):
    mask += st.gauss2d(xg, xg, p=[coords[i, 1], coords[i, 0], r[i], r[i], intensity[i], intensity[i]])
mask /= np.max(mask)

# ── (f) combined 5% + 5% mask ─────────────────────────────────
k = round(nx * ny * 0.05)
ri_uniform = np.random.choice(nx * ny, k, replace=False)
uni = np.column_stack(np.unravel_index(ri_uniform, (nx, ny)))   # (row, col)
ada = generate_random_coordinates(k, nx=nx, mask=mask)          # (row, col)

# ── assemble 2x3 ──────────────────────────────────────────────
if PAPER:
    FS = dict(fig=(3.375, 2.42), title=6.5, letter=6, legend=4, circ_ms=3.5, circ_mew=0.8,
              circ_lw=(1.0, 0.7), x_ms=3.5, x_mew=0.9, pt=0.18, top=0.915, hspace=0.20, wspace=0.05)
else:
    FS = dict(fig=(9, 6.2), title=11, letter=11, legend=7, circ_ms=8, circ_mew=2,
              circ_lw=(2, 1.2), x_ms=7, x_mew=1.6, pt=1.2, top=0.93, hspace=0.16, wspace=0.06)
fig, axs = plt.subplots(2, 3, figsize=FS['fig'])
fig.subplots_adjust(left=0.005, right=0.995, bottom=0.005, top=FS['top'], wspace=FS['wspace'], hspace=FS['hspace'])
if PAPER:
    titles = ['Topography' if SXM else 'dI/dV map', 'FT',
              'Bragg-filtered' if MODE == 'lattice' else 'Band-pass filtered',
              'Defect locations', 'Probability mask', 'Combined mask']
else:
    titles = ['Full-grid topography' if SXM else 'Full-grid map', 'FT',
              'Inverse FT of Bragg peaks only' if MODE == 'lattice' else 'Inverse FT of band-passed region',
              'Impurity locations', 'ASS probability mask', 'Combined sampling mask']
(ax_a, ax_b, ax_c), (ax_d, ax_e, ax_f) = axs

ax_a.imshow(z_test, origin='lower', rasterized=True)

c, s = np.mean(z_ft), np.std(z_ft)
ax_b.imshow(z_ft, origin='lower', cmap=stmpy.cm.gray_r, clim=[0, c + 3 * s], rasterized=True)
if MODE == 'lattice':
    for bx, by in masks:
        ax_b.plot(bx, by, 'ro', markersize=FS['circ_ms'], markerfacecolor='none', markeredgewidth=FS['circ_mew'])
else:
    # band-pass: keeps |q| between ~2 sigma_q of the two Gaussians, sigma_q = N / (2 pi sigma)
    from matplotlib.patches import Circle
    ax_b.add_patch(Circle((c0, c0), 2 * nx / (2 * np.pi * LP_SIGMA), fill=False, ec='r', lw=FS['circ_lw'][0]))
    ax_b.add_patch(Circle((c0, c0), 2 * nx / (2 * np.pi * BG_SIGMA), fill=False, ec='r', lw=FS['circ_lw'][1], ls='--'))

ax_c.imshow(z_masked, origin='lower', rasterized=True)

ax_d.imshow(z_masked, origin='lower', rasterized=True)
ax_d.plot(coords[:, 1], coords[:, 0], 'rx', ms=FS['x_ms'], mew=FS['x_mew'])

ax_e.imshow(mask, origin='lower', rasterized=True)

ax_f.imshow(z_test, origin='lower', rasterized=True)
_lab = ('Uniform 5%', 'Adaptive 5%') if PAPER else (f'Uniform 5% ({k} pts)', f'Adaptive 5% ({k} pts)')
ax_f.scatter(uni[:, 1], uni[:, 0], s=FS['pt'], c='C0', alpha=0.45, rasterized=True, label=_lab[0])
ax_f.scatter(ada[:, 1], ada[:, 0], s=FS['pt'], c='r', alpha=0.45, rasterized=True, label=_lab[1])
ax_f.legend(loc='upper right', fontsize=FS['legend'], markerscale=5 if not PAPER else 8,
            framealpha=0.85, borderpad=0.3, handletextpad=0.3, labelspacing=0.2)

for ax, t, L in zip(axs.flat, titles, 'abcdef'):
    ax.set_title(t, fontsize=FS['title'], fontweight='bold', pad=2 if PAPER else 6)
    ax.set_xlim(0, ny); ax.set_ylim(0, nx); ax.axis('off')
    ax.text(0.03, 0.97, f'({L})', transform=ax.transAxes, fontsize=FS['letter'], fontweight='bold',
            va='top', ha='left', color='white',
            bbox=dict(facecolor='0.4', edgecolor='none', alpha=0.8, pad=1.2 if PAPER else 2))

suffix = ('' if MODE == 'lattice' else '_lowpass') + TAG
if PAPER:
    fig.savefig('figures/out/figure_ASS_pipeline_cebi_topo.pdf', dpi=300)
    fig.savefig('figures/out/figure_ASS_pipeline_cebi_topo.png', dpi=300)
    suffix = ' (paper) -> figures/out/figure_ASS_pipeline_cebi_topo'
else:
    fig.savefig(f'figures/out/fig_ASS_pipeline_cebi{suffix}.pdf', dpi=300)
    fig.savefig(f'figures/out/fig_ASS_pipeline_cebi{suffix}.png', dpi=150)
print("extrema (row, col):", coords.astype(int).tolist())
print(f"Saved figures/out/fig_ASS_pipeline_cebi{suffix}.pdf and .png")
