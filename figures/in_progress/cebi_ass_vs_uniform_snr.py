"""CeBi adaptive-vs-uniform QPI signal recovery vs sampling fraction (Pass 2).

Puts a number on the Fig. ASS claim (paper/figure3_ASS.pdf; abstract and
Fig. ASS caption): at the same sampling fraction, the 5% uniform + 5%
feature-guided mask preserves the defect-centred QPI signal better than a
10% uniform mask. Also produces the CeBi uniform/adaptive curves for the
SNR-vs-sparsity figure (Fig. 5 caption's "can be added when ... available").

METRIC (decided with Marcos 2026-10-11)
  Ridge band and noise band from cebi_snr_contour_playground (GEOM_LOCKED,
  one locked contour traced on the full-grid FT, applied identically to
  every map; Jenny's 2026-04-06 sketch: a line along the ridge and a
  parallel line just outside it).
    signal(map) = mean FT intensity within +/- 2 px of the locked contour
    noise(map)  = mean FT intensity 3.7 to 5 px outside the contour
  Headline quantity = signal recovery = signal(rec) / signal(full grid),
  i.e. the reconstruction SNR with the FULL-GRID noise floor as the common
  denominator: SNR_rec / SNR_GT = [signal(rec)/noise(GT)] / [signal(GT)/noise(GT)].
  Why not the reconstruction's own noise band: basis pursuit leaves ~17% of
  the Fourier coefficients nonzero, so a reconstruction's background measures
  the solver's sparsity, not noise. Dividing by it gave 304% of the full-grid
  ratio for the adaptive mask (sanity run 2026-10-11) and props up the BSCCO
  25% number as well (48% signal recovery / 69% background = 69% ratio).
  The own-map ratio is still computed and reported as a secondary column.

RECIPE mirrors notebooks/Adaptive_sparse_sampling.ipynb cells 15-33, the
cells that produced figure3_ASS.pdf (provenance re-verified 2026-10-11: the
embedded panel (a) raster matches d.liy[2], NOT d.LIY[2]; the saved point
counts 2668 + 2724 = 5392 only fit N = 231^2):
  GT map    d.liy[2] / mean   (231x231 top-left crop of LIY, -300 mV)
  operator  partialFourier (cell 3): y = FFT(x)[idx] / sqrt(n); the solver's
            x comes back point-reflected and scaled by 1/sqrt(n); cells 19/33
            flip it and rescale by the mean for display, as reconstruct() does.
  BPDN      spg_bpdn(A, b, sigma=1e-2, iter_lim=1e5) on the RAW samples (no
            mean removal). ||b|| ~ sqrt(k) >> sigma, so this is effectively
            basis pursuit: an exact interpolation of the sampled pixels.
  uniform   k = round(f*N) pixels drawn without replacement (cell 15)
  adaptive  (cell 22) round(0.05*N) uniform  +  (cells 25-27) a Gaussian
            draw centred at (110, 106) with covariance 750*I, rounded to
            pixels and de-duplicated. The notebook REQUESTS round(0.06*N)
            points and keeps the ~0.05*N unique ones (cell 28 output).
            Pixel index = (x0-1)*nx + (y0-1)  (convert_ri, d=2).

Run:  .venv/bin/python figures/in_progress/cebi_ass_vs_uniform_snr.py --sanity
          10% uniform vs 5%+5% adaptive, one trial, overlay figure
      .venv/bin/python figures/in_progress/cebi_ass_vs_uniform_snr.py
          full sweep (needs adaptive_indices; see TODO(human))
Out:  figures/out/cebi_ass_vs_uniform_sanity.png
      data/cebi_ass_vs_uniform_snr.npz, figures/out/cebi_ass_vs_uniform_snr.png
"""
import os
import sys
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.sparse.linalg import LinearOperator
from spgl1 import spg_bpdn
import stmpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cebi_snr_contour_playground as pg  # noqa: E402  (bands + GEOM_LOCKED)

st = stmpy.tools
CEBI = pg.CEBI
LAYER = 2                      # -300 mV = len(d.en)//2, the Fig. ASS layer
SIGMA = 1e-2                   # notebook cells 18/32, absolute
ITER_LIM = int(1e5)
GAUSS_CENTER = (110, 106)      # cell 26, (x0, y0) in convert_ri's convention
GAUSS_VAR = 750.0              # cell 26, isotropic covariance
FIG_UNIFORM_FRAC = 0.05        # cell 22
FIG_GAUSS_REQUEST_FRAC = 0.06  # cell 26 (requested; ~0.05 survive de-dup)

SWEEP_FRACS = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50)
N_TRIALS = 3


def load_cebi_gt():
    """Fig. ASS ground truth: d.liy[2] / mean (231x231) and its FT."""
    d = stmpy.load(CEBI, biasOffset=False)
    z = d.liy[LAYER] / np.mean(d.liy[LAYER])
    return z, st.fft(z, zeroDC=True)


class PartialFourier(LinearOperator):
    """Notebook cell 3: y = FFT(x)[idx]/sqrt(n); adjoint zero-fills, ifft*sqrt(n)."""

    def __init__(self, idx, n):
        self.idx, self.n = idx, n
        self.shape = (len(idx), n)
        self.dtype = np.complex128

    def _matvec(self, x):
        return (np.fft.fft(x) / np.sqrt(self.n))[self.idx]

    def _rmatvec(self, y):
        z = np.zeros(self.n, dtype=complex)
        z[self.idx] = y
        return np.fft.ifft(z) * np.sqrt(self.n)


def reconstruct(z_gt, idx):
    """BPDN reconstruction from the pixels at flat indices idx (cells 16-19)."""
    nx, ny = z_gt.shape
    b = z_gt.flat[idx]
    x, *_ = spg_bpdn(PartialFourier(idx, nx * ny), b, sigma=SIGMA,
                     iter_lim=ITER_LIM, verbosity=0)
    rec = np.real(np.fft.ifft(x).reshape(nx, ny))[::-1, ::-1]
    return rec * np.mean(z_gt) / np.mean(rec)      # cell 19 scaling (undoes 1/sqrt(n))


def uniform_indices(N, k, rng):
    return np.sort(rng.choice(N, size=k, replace=False))


def gaussian_indices(n_request, nx, ny, rng, center=GAUSS_CENTER, var=GAUSS_VAR):
    """Cells 25-27: draw n_request points from N(center, var*I), round to
    pixels, keep the unique ones, map with (x0-1)*nx + (y0-1), drop any
    that fall outside the frame. Returns sorted unique flat indices."""
    # explicit isotropic draw; numpy's multivariate_normal raises spurious
    # matmul overflow warnings under Accelerate on macOS
    xy = np.asarray(center, float) + np.sqrt(var) * rng.standard_normal((n_request, 2))
    xy = np.unique(np.round(xy).astype(int), axis=0)
    ok = (xy[:, 0] >= 1) & (xy[:, 0] <= nx) & (xy[:, 1] >= 1) & (xy[:, 1] <= ny)
    flat = (xy[ok, 0] - 1) * nx + (xy[ok, 1] - 1)
    return np.sort(flat)


def adaptive_indices_fig(nx, ny, rng):
    """The Fig. ASS mask exactly: 5% uniform + Gaussian (6% requested)."""
    N = nx * ny
    u = uniform_indices(N, round(FIG_UNIFORM_FRAC * N), rng)
    g = gaussian_indices(round(FIG_GAUSS_REQUEST_FRAC * N), nx, ny, rng)
    return np.unique(np.concatenate([u, g]))       # union of distinct pixels


def adaptive_indices(frac, nx, ny, rng):
    """Adaptive mask for an ARBITRARY total sampling fraction `frac`.

    Must reproduce adaptive_indices_fig at frac = 0.10 (5% uniform + the
    Gaussian draw that leaves ~5% unique pixels) and return sorted unique
    flat indices whose count is as close to round(frac * N) as the
    de-duplication allows.

    TODO(human): decide how the 5% + 5% split generalizes with frac.
    Building blocks: uniform_indices(N, k, rng) and
    gaussian_indices(n_request, nx, ny, rng) (de-duplicated, so the unique
    count is below n_request; the figure asked for 6% to get 5%). The
    Gaussian has sigma ~ 27 px, so its 2-sigma disk holds only ~9000 of the
    53361 pixels; past ~15% adaptive it saturates and extra requests return
    ever fewer new pixels. Return np.unique(np.concatenate([u, g])).
    """
    raise NotImplementedError("TODO(human): split rule for arbitrary frac")


# ── scoring ──────────────────────────────────────────────────────────────
def bands(ft_2d):
    """Locked-geometry ridge-band signal and outer-band noise of one map,
    plus the map's own ratio (secondary) and the May max statistic."""
    own_ratio, _, _, sig, noi = pg.cebi_snr(ft_2d, pg.GEOM_LOCKED, return_debug=True)
    return dict(signal=sig.mean(), noise=noi.mean(), own_ratio=own_ratio,
                own_ratio_max=pg.cebi_snr(ft_2d, pg.GEOM_LOCKED, signal_stat="max"))


def recovery(b, gt):
    """Headline: signal(rec)/signal(GT) = SNR with the full-grid noise floor."""
    return b["signal"] / gt["signal"]


def draw_bands(ax, shape):
    """Locked contour (cyan), ridge band edges (orange), noise band (red)."""
    g = dict(pg.GEOM_LOCKED)
    H, W = shape
    cx = (W - 1) / 2 if g["cx"] is None else g["cx"]
    cy = (H - 1) / 2 if g["cy"] is None else g["cy"]
    pts, nrm = pg.superellipse_perimeter(400, g["a"], g["b"], g["p"], g["theta"], cx, cy)
    s = np.linspace(-g["cut_inner"], g["cut_outer"], g["n_profile"])
    n_edge = max(1, int(round(g["noise_edge_frac"] * g["n_profile"])))
    for off, col, lw in [(0.0, "cyan", 0.9),
                         (-g["signal_halfwidth"], "orange", 0.6),
                         (g["signal_halfwidth"], "orange", 0.6),
                         (s[-n_edge], "red", 0.6), (g["cut_outer"], "red", 0.6)]:
        q = pts + off * nrm
        ax.plot(np.r_[q[:, 0], q[0, 0]], np.r_[q[:, 1], q[0, 1]], "-", color=col, lw=lw, alpha=0.9)


def sanity(seed=0, out="figures/out/cebi_ass_vs_uniform_sanity.png"):
    z, ft = load_cebi_gt()
    nx, ny = z.shape
    N = nx * ny
    rng = np.random.default_rng(seed)
    masks = {"10% uniform": uniform_indices(N, round(0.10 * N), rng),
             "5% uniform + 5% adaptive": adaptive_indices_fig(nx, ny, rng)}
    panels = [("full grid", ft)]
    for name, idx in masks.items():
        t0 = time.time()
        rec = reconstruct(z, idx)
        print(f"{name}: k = {len(idx)} ({len(idx) / N:.1%}), BPDN {time.time() - t0:.0f} s")
        panels.append((name, st.fft(rec, zeroDC=True)))
    res = {name: bands(f) for name, f in panels}
    gt = res["full grid"]
    print(f"\n{'map':26s} {'signal':>7s} {'RECOVERY':>9s} {'noise':>7s} {'bkg/GT':>7s} "
          f"{'own ratio':>10s} {'own/GT':>7s}")
    for name, r in res.items():
        print(f"{name:26s} {r['signal']:7.3f} {recovery(r, gt):9.0%} {r['noise']:7.4f} "
              f"{r['noise'] / gt['noise']:7.0%} {r['own_ratio']:10.3f} "
              f"{r['own_ratio'] / gt['own_ratio']:7.0%}")
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.8))
    c0 = (nx - 1) / 2
    for ax, (name, f) in zip(axs, panels):
        c, sd = np.mean(f), np.std(f)
        ax.imshow(f, origin="lower", cmap=stmpy.cm.gray_r, clim=[0, c + 3 * sd])
        draw_bands(ax, f.shape)
        ax.set_xlim(c0 - 60, c0 + 60); ax.set_ylim(c0 - 60, c0 + 60)
        ax.set_title(f"{name}\nsignal recovery {recovery(res[name], gt):.0%}   "
                     f"background {res[name]['noise'] / gt['noise']:.0%} of full grid", fontsize=9.5)
        ax.set_xticks([]); ax.set_yticks([])
    fig.text(0.5, 0.01, "cyan: locked contour    orange: ridge band (signal)    red: outer band (background)",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out, dpi=130)
    print(f"overlay -> {out}")
    return res


def sweep(fracs=SWEEP_FRACS, n_trials=N_TRIALS, seed0=0):
    z, ft = load_cebi_gt()
    nx, ny = z.shape
    N = nx * ny
    gt = bands(ft)
    out = {"gt": gt, "fracs": list(fracs)}
    for key in ("uniform", "adaptive"):
        out[key] = {"signal": [], "noise": [], "own_ratio": [], "k": []}
    for f in fracs:
        trial = {key: {q: [] for q in ("signal", "noise", "own_ratio", "k")} for key in ("uniform", "adaptive")}
        for t in range(n_trials):
            rng = np.random.default_rng(seed0 + 1000 * int(round(f * 100)) + t)
            for key, idx in (("uniform", uniform_indices(N, round(f * N), rng)),
                             ("adaptive", adaptive_indices(f, nx, ny, rng))):
                b = bands(st.fft(reconstruct(z, idx), zeroDC=True))
                for q in ("signal", "noise", "own_ratio"):
                    trial[key][q].append(b[q])
                trial[key]["k"].append(len(idx))
        for key in ("uniform", "adaptive"):
            for q in ("signal", "noise", "own_ratio", "k"):
                out[key][q].append(trial[key][q])
        ru = np.array(trial["uniform"]["signal"]) / gt["signal"]
        ra = np.array(trial["adaptive"]["signal"]) / gt["signal"]
        print(f"  {f:.0%}: recovery uniform {ru.mean():.0%} +/- {ru.std():.0%}   "
              f"adaptive {ra.mean():.0%} +/- {ra.std():.0%}   "
              f"(k = {np.mean(trial['uniform']['k']):.0f} / {np.mean(trial['adaptive']['k']):.0f})")
    for key in ("uniform", "adaptive"):
        for q in ("signal", "noise", "own_ratio", "k"):
            out[key][q] = np.array(out[key][q])          # [n_frac, n_trials]
    return out


def plot_sweep(res, out="figures/out/cebi_ass_vs_uniform_snr.png"):
    fr = 100 * np.array(res["fracs"])
    gt = res["gt"]
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.6))
    for key, col in [("uniform", "C0"), ("adaptive", "C3")]:
        for ax, q, ref in ((axs[0], "signal", gt["signal"]), (axs[1], "noise", gt["noise"])):
            v = res[key][q] / ref
            ax.errorbar(fr, v.mean(1), v.std(1), marker="o", ms=4, color=col, capsize=2, label=key)
    for ax, lab in ((axs[0], "QPI signal recovery (ridge band / full grid)"),
                    (axs[1], "background (outer band / full grid)")):
        ax.axhline(1.0, color="k", lw=0.8, ls="--", label="full grid")
        ax.set_xlabel("Sampling fraction (%)"); ax.set_ylabel(lab); ax.set_ylim(bottom=0)
    axs[0].legend(frameon=False)
    fig.tight_layout(); fig.savefig(out, dpi=150)
    print(f"plot -> {out}")


if __name__ == "__main__":
    if "--sanity" in sys.argv:
        sanity()
    else:
        res = sweep()
        np.savez("data/cebi_ass_vs_uniform_snr.npz",
                 fracs=np.array(res["fracs"]),
                 gt_signal=res["gt"]["signal"], gt_noise=res["gt"]["noise"],
                 gt_own_ratio=res["gt"]["own_ratio"],
                 **{f"{key}_{q}": res[key][q] for key in ("uniform", "adaptive")
                    for q in ("signal", "noise", "own_ratio", "k")})
        plot_sweep(res)
        i10 = res["fracs"].index(0.10)
        ru = res["uniform"]["signal"][i10].mean() / res["gt"]["signal"]
        ra = res["adaptive"]["signal"][i10].mean() / res["gt"]["signal"]
        print(f"\nCeBi QPI signal recovery @ 10%: uniform {ru:.0%} -> adaptive {ra:.0%} of full grid;"
              f"  saved data/cebi_ass_vs_uniform_snr.npz")
