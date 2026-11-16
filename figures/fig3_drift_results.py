"""Fig. 3 (drift correction of the reconstructed BSCCO map), built to the house
standard. Writes to figures/out/ only.

STATUS 2026-11-16: this is the J16 candidate and is AHEAD of the manuscript.
The Fig. 3 now in paper/ (commit e39f2bb) came from the previous revision of
this script, which took the drift-corrected map from the notebook's "after"
branch (drift field fitted to the reconstruction itself, no crop here, no
Fourier zoom). Remove this note once the candidate is approved and pushed.

What the panels are (J16, Jenny 2026-10-24; Richard 2026-11-02):
  (b) is the reconstruction after drift correction with the field measured on the
      CO-ACQUIRED TOPOGRAPHY (notebook cells 34-41), which is what the caption
      says. Earlier versions used a field fitted to the reconstruction itself.
  Real-space crop: a drift-corrected map has no measured data to draw from along
      its border, so the remap repeats border values there (about 5 px at the top,
      3 px at the right for this field). CROP px are removed from every side with
      the lab's dfc.cropedge(force_commen=True), which also resamples the map by
      about 1% so a whole number of lattice periods fits it. (a) is the SAME
      window of the uncorrected reconstruction (a plain slice, no resampling), so
      (a) vs (b) and (c) vs (d) compare like with like.
  Fourier-space zoom: (c), (d) show q_x and q_y out to the Bragg wavevector
      2 pi / A0, which keeps the four Bragg peaks just inside the frame.
  Scale: (a), (c) use the instrument's 40 nm over 250 px. (b), (d) are calibrated
      from their own lattice: the Bragg peaks are placed at 2 pi / A0.

Other points, unchanged from the first rebuild: built at 3.375 in; data arrays
embedded unresampled; (a), (b) share color limits tied to the ground truth, as do
(c), (d); each FT is divided by its pixel count so maps of different size compare.

Data: figures/data_bscco.py (instrument files -> arrays, about 2 s).

Usage: .venv/bin/python figures/fig3_drift_results.py     -> figures/out/fig3_drift_results.pdf
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
from scipy.ndimage import maximum_filter
import stmpy
import stmpy.tools as st
import stmpy.driftcorr as dfc
import data_bscco
import figstyle as fs

D = data_bscco.load()
PX_A = 400 / 250          # Angstrom per pixel as acquired: 40 nm over 250 px (.3ds and .sxm headers)
A0 = 3.83                 # Angstrom, BSCCO lattice constant.
                          # TODO (Jenny peer review, J16): confirm this value with Richard.
CROP = 8                  # px removed from each side of the drift-corrected map
Q_VIEW = 2 * np.pi / A0   # 1/Angstrom, half-width of the Fourier panels: the Bragg wavevector, 1.64


def drift_correct_from_topography(topo, liy):
    """Lawler-Fujita drift field from the co-acquired topography, two passes,
    applied to the reconstruction (notebook cells 34-41, parameters unchanged)."""
    bp = dfc.findBraggs(topo, r=0.2, show=False)
    bp_c = dfc.generate_bp(topo, bp=bp, orient=None)
    z1, p1 = dfc.find_drift_parameter(topo, bp_c=bp_c, sigma=13, cut2=None, show=False)
    bp2 = dfc.findBraggs(z1, r=0.2, show=False)
    _, p2 = dfc.find_drift_parameter(z1, bp_c=bp2, sigma=17, show=False)
    return dfc.apply_drift_parameter(dfc.apply_drift_parameter(liy, p1), p2)


def bragg_radius(ft_mag):
    """Distance of the four lattice peaks from the center, in FT pixels."""
    n = ft_mag.shape[0]
    c = n // 2
    yy, xx = np.indices(ft_mag.shape)
    r = np.hypot(yy - c, xx - c)
    peaks = (ft_mag == maximum_filter(ft_mag, 9)) & (r > 0.34 * n) & (r < 0.49 * n)
    idx = np.argwhere(peaks)
    idx = idx[np.argsort(ft_mag[peaks])[::-1]][:4]
    radii = np.hypot(idx[:, 0] - c, idx[:, 1] - c)
    assert np.ptp(radii) < 1.5, f'the four strongest outer peaks are not one lattice: {radii}'
    return radii.mean()


def ft_window(ft_mag, px_a):
    """The central part of an FT out to Q_VIEW, and its extent in 1/Angstrom."""
    n = ft_mag.shape[0]
    c = n // 2
    dq = 2 * np.pi / (n * px_a)                   # one FT pixel: 2 pi / L
    k = int(np.floor(Q_VIEW / dq + 0.5))          # last pixel that is at least partly in view
    return ft_mag[c - k:c + k + 1, c - k:c + k + 1], (-(k + 0.5) * dq, (k + 0.5) * dq) * 2


ft = lambda a: st.fft(a, zeroDC=True) / a.size    # magnitude per pixel

# Display units: the reconstruction rescaled to the ground truth's mean and standard
# deviation, the same affine map for (a) and (b).
gt, rec = D['gt_fA'], D['rec_bpdn']
gain = np.nanstd(gt) / np.nanstd(rec)
display = lambda a: (a - np.nanmean(rec)) * gain + np.nanmean(gt)

corrected = drift_correct_from_topography(D['tz'], rec)
before = display(rec)[CROP:-CROP, CROP:-CROP]
after = display(dfc.cropedge(corrected, n=CROP, force_commen=True,
                             bp=dfc.findBraggs(corrected, r=0.2, show=False)))
ft_before, ft_after = ft(before), ft(after)

px_before = PX_A                                              # as acquired
px_after = A0 * bragg_radius(ft_after) / after.shape[0]       # from the corrected lattice
print(f'pixel size: before {px_before:.4f} A (as acquired), after {px_after:.4f} A (lattice); '
      f'Bragg radius after = {bragg_radius(ft_after):.2f} FT px of {after.shape[0]}')

# Ground truth leads each list: it is the reference the limits are tied to, which
# keeps these panels on the limits of Fig. 1.
real_lim = fs.shared_clim([gt, before, after])
ft_lim = fs.shared_clim([ft(gt), ft_before, ft_after], zero_floor=True)

# ---- layout, in inches --------------------------------------------------------
W = fs.WIDTHS['col']
S, BAR = 1.5275, 0.14                             # panel side, colorbar width
X = [0.04, 0.04 + S + 0.06]                       # column lefts
H = 0.20 + 2 * S + 0.08 + 0.04
Y = [0.04 + S + 0.08, 0.04]                       # row bottoms (top row first)
fig = fs.new_figure('col', H)
box = lambda x, y, w, h: fig.add_axes([x / W, y / H, w / W, h / H])
ax = [[box(X[c], Y[r], S, S) for c in range(2)] for r in range(2)]
cax = [box(X[1] + S + 0.06, Y[r], BAR, S) for r in range(2)]        # full panel height

for c, (rs, ftm, px, title) in enumerate([(before, ft_before, px_before, 'Reconstructed'),
                                          (after, ft_after, px_after, 'Drift corrected')]):
    side_nm = rs.shape[0] * px / 10
    im_r = fs.image(ax[0][c], rs, extent=(0, side_nm) * 2, cmap=stmpy.cm.jackyPSD,
                    vmin=real_lim[0], vmax=real_lim[1])
    window, extent = ft_window(ftm, px)
    im_q = fs.image(ax[1][c], window, extent=extent, cmap=stmpy.cm.gray_r,
                    vmin=ft_lim[0], vmax=ft_lim[1])
    ax[1][c].set_xlim(-Q_VIEW, Q_VIEW)
    ax[1][c].set_ylim(-Q_VIEW, Q_VIEW)
    ax[0][c].set_title(title, fontweight='bold', pad=3)
    fs.scalebar(ax[0][c], 10, '10 nm', color='w', size=8.6)
    # pinned a little left of the corner: a Bragg peak sits in the lower right
    fs.scalebar(ax[1][c], 0.5, '0.5 Å$^{-1}$', color=fs.INK, size=8.6, anchor=(0.80, 0.0))
    fs.panel_label(ax[0][c], 'ab'[c], note='−22 mV', on_image=True)
    fs.panel_label(ax[1][c], 'cd'[c], on_image=True)

fs.colorbar(im_r, cax[0], labels=('L', 'H'), inset=True)     # relative scales: a direction, not numbers
fs.colorbar(im_q, cax[1], labels=('0', 'H'), inset=True)

fs.save(fig, 'fig3_drift_results')
