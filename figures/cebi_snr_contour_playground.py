"""CeBi SNR via PERPENDICULAR PROFILES along a superellipse contour.

Marcos's method (2026-05-15):
  - A superellipse roughly traces the CeBi QPI signal ridge (the diamond).
    It does NOT need to be exact -- it just has to be near the ridge.
  - Walk along that contour. At many points around it, shoot a line
    PERPENDICULAR (normal) to the contour, crossing the ridge.
  - On each perpendicular cut: max  -> a SIGNAL sample (snaps to the true
    ridge even if the superellipse guess is off); outermost end -> a NOISE
    sample (dark whitespace far outside the diamond).
  - SNR = mean(signal maxima) / mean(outer-edge noise).

The inner "filled" blob is excluded simply by not letting cuts reach
inward that far (CUT_INNER), so no separate inner mask is needed.

Run:    .venv/bin/python figures/cebi_snr_contour_playground.py
Output: figures/cebi_snr_contour_overlay.png   (contour + cuts + picks)
        + printed SNR on this ground-truth map (sanity: should be >> 1).

Reproducibility:
  Needs the CeBi dataset `data/2019-07-11-002 LIY local corr new.spy`
  (NOT in the repo -- ask Marcos/Richard). Deps: hoffmanstmpy, spgl1,
  scipy, numpy, matplotlib.
  Run: .venv/bin/python figures/cebi_snr_contour_playground.py

Geometry is frozen in GEOM_LOCKED, chosen on the GROUND-TRUTH FT to trace
the visible diamond ridge -- NOT tuned to maximize SNR. GT CeBi SNR ~ 4.08.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import map_coordinates
import stmpy

st = stmpy.tools

CEBI = "data/2019-07-11-002 LIY local corr new.spy"

# Superellipse that roughly traces the signal ridge (cyan in the overlay).
CX, CY = None, None      # None -> auto: geometric center of the loaded FT
A,  B  = 25.0, 25.0      # half-axes (pixels)
P      = 1.0             # exponent: 1=diamond, 2=ellipse, >2=box
THETA  = 0.0             # rotation (degrees, CCW)

N_SAMPLES = 36          # how many perpendicular cuts around the perimeter
CUT_INNER = 5.0         # how far each cut reaches INWARD from the contour (px)
CUT_OUTER = 5.0         # how far each cut reaches OUTWARD (px) -> noise end
N_PROFILE = 70           # samples along each perpendicular cut
SIGNAL_HALFWIDTH = 2.0   # search the ridge max ONLY within +/- this many px of
                         # the contour (orange band) -> can't grab a bright
                         # off-ridge feature farther out along the normal
NOISE_EDGE_FRAC = 0.15   # fraction at the OUTWARD end averaged as that cut's noise

SHOW_CUTS_EVERY = 2      # draw every Nth cut in the overlay (visual only)
OVERLAY_ALPHA   = 0.9
GEOM_LOCKED = dict(
    cx=None, cy=None, a=25.0, b=25.0, p=1.0, theta=0.0,
    n_samples=36, cut_inner=5.0, cut_outer=5.0, n_profile=70,
    signal_halfwidth=2.0, noise_edge_frac=0.15,
)


def load_cebi_ft():
    """CeBi ground-truth FT: d.liy[mid energy] / mean, st.fft(zeroDC=True)."""
    d = stmpy.load(CEBI, biasOffset=False)
    z = d.liy[len(d.en) // 2]
    z = z / np.mean(z)
    return st.fft(z, zeroDC=True)


def superellipse_perimeter(n, a, b, p, theta_deg, cx, cy):
    """n points around the (rotated, translated) superellipse, plus the
    outward unit normal at each (computed numerically -> robust for any p,
    including concave p<1)."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ct, sstt = np.cos(t), np.sin(t)
    x0 = a * np.sign(ct) * np.abs(ct) ** (2.0 / p)
    y0 = b * np.sign(sstt) * np.abs(sstt) ** (2.0 / p)
    th = np.deg2rad(theta_deg)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    pts = (R @ np.vstack([x0, y0])).T + np.array([cx, cy])
    # numerical outward normal: rotate the tangent (central difference) by 90 deg
    tang = np.roll(pts, -1, axis=0) - np.roll(pts, 1, axis=0)
    nrm = np.stack([tang[:, 1], -tang[:, 0]], axis=1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
    outward = pts - np.array([cx, cy])
    flip = np.sum(nrm * outward, axis=1) < 0
    nrm[flip] *= -1
    return pts, nrm


def cebi_snr(ft_2d, geom=None, return_debug=False):
    """SNR = mean(perpendicular-cut maxima) / mean(outer-edge noise).

    geom : optional dict overriding any of cx,cy,a,b,p,theta,n_samples,
    cut_inner,cut_outer,n_profile,signal_halfwidth,noise_edge_frac. When
    None, the module-level EDIT-block globals are used, so a manual run is
    byte-identical to before this refactor.
    """
    g = dict(cx=CX, cy=CY, a=A, b=B, p=P, theta=THETA,
             n_samples=N_SAMPLES, cut_inner=CUT_INNER, cut_outer=CUT_OUTER,
             n_profile=N_PROFILE, signal_halfwidth=SIGNAL_HALFWIDTH,
             noise_edge_frac=NOISE_EDGE_FRAC)
    if geom:
        g.update(geom)
    H, W = ft_2d.shape
    cx = (W - 1) / 2 if g["cx"] is None else g["cx"]
    cy = (H - 1) / 2 if g["cy"] is None else g["cy"]
    pts, nrm = superellipse_perimeter(g["n_samples"], g["a"], g["b"],
                                      g["p"], g["theta"], cx, cy)
    s = np.linspace(-g["cut_inner"], g["cut_outer"], g["n_profile"])
    win = np.abs(s) <= g["signal_halfwidth"]           # ridge-search band
    if not win.any():                                  # guard: keep >=1 sample
        win[np.argmin(np.abs(s))] = True
    n_edge = max(1, int(round(g["noise_edge_frac"] * g["n_profile"])))

    sig, noi, dbg = [], [], []
    for (px, py), (nx, ny) in zip(pts, nrm):
        xs = px + s * nx
        ys = py + s * ny
        prof = map_coordinates(ft_2d, [ys, xs], order=1, mode="nearest")
        # windowed max: search the ridge ONLY within +/- signal_halfwidth
        imax = int(np.argmax(np.where(win, prof, -np.inf)))
        sig.append(prof[imax])
        noi.append(prof[-n_edge:].mean())
        dbg.append((xs, ys, imax, win))
    sig, noi = np.array(sig), np.array(noi)
    snr = sig.mean() / noi.mean()
    if return_debug:
        return snr, pts, dbg, sig, noi
    return snr


def draw_overlay(ft_2d, pts, dbg, snr, path):
    c, sd = np.mean(ft_2d), np.std(ft_2d)
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.imshow(ft_2d, origin="lower", cmap=stmpy.cm.gray_r, clim=[0, c + 3 * sd])
    ax.plot(np.r_[pts[:, 0], pts[0, 0]], np.r_[pts[:, 1], pts[0, 1]],
            "-", color="cyan", lw=1.0, alpha=OVERLAY_ALPHA, label="superellipse")
    for k, (xs, ys, imax, win) in enumerate(dbg):
        if k % SHOW_CUTS_EVERY:
            continue
        ax.plot(xs, ys, "-", color="yellow", lw=0.5, alpha=0.5)        # full cut
        ax.plot(xs[win], ys[win], "-", color="orange", lw=1.4, alpha=0.9)  # search band
        ax.plot(xs[imax], ys[imax], ".", color="lime", ms=6)          # signal max
        ax.plot(xs[-1], ys[-1], ".", color="red", ms=5)               # noise end
    ax.plot([], [], "-", color="orange", label="ridge-search band")
    ax.plot([], [], ".", color="lime", label="signal (windowed max)")
    ax.plot([], [], ".", color="red", label="noise (outer end)")
    ax.set_xticks(np.arange(0, ft_2d.shape[1] + 1, 16))
    ax.set_yticks(np.arange(0, ft_2d.shape[0] + 1, 16))
    ax.grid(True, alpha=0.3, lw=0.4)
    ax.set_title(f"perpendicular-profile SNR = {snr:.3f}   "
                 f"(A,B={A},{B} P={P} THETA={THETA})")
    ax.legend(loc="upper right")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    ft = load_cebi_ft()
    snr, pts, dbg, sig, noi = cebi_snr(ft, return_debug=True)
    out = "figures/cebi_snr_contour_overlay.png"
    draw_overlay(ft, pts, dbg, snr, out)
    print(f"cuts used        = {len(sig)} / {N_SAMPLES}")
    print(f"signal (cut max) : mean {sig.mean():.4g}  min {sig.min():.4g}  "
          f"max {sig.max():.4g}")
    print(f"noise (outer end): mean {noi.mean():.4g}")
    print(f"GT CeBi SNR      = {snr:.4f}   (sanity: should be >> 1)")
    print(f"overlay -> {out}")
