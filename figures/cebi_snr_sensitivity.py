"""CeBi SNR sensitivity analysis (Pass 1).

Defends the HAND-TUNED CeBi SNR geometry (GEOM_LOCKED) by showing how little
the ground-truth SNR moves when the geometry is perturbed. This converts a
subjective-looking ROI choice into an objective, reproducible claim:
"GT SNR = X, +/-Y% over +/-20% ROI perturbation" -- the disclosed defense
against a 'you cherry-picked the half-axes' reviewer challenge.

It only REPORTS SNR vs geometry; it never SELECTS geometry by SNR
(GEOM_LOCKED is fixed, not optimized) -- so it is non-circular by construction.

Scope limit: this measures sensitivity of the *GT SNR*. The claim that appears
in the paper is the ASS-vs-uniform *gain*, whose ROI sensitivity can only be
measured inside the sweep -- that is Pass 2. Do not over-read this as fully
retiring the cherry-picking concern; it shows the metric is not fragile.

Run: .venv/bin/python figures/cebi_snr_sensitivity.py
Out: figures/cebi_snr_sensitivity.csv
     figures/cebi_snr_sensitivity_tornado.png
     figures/cebi_snr_sensitivity_contours.png
"""
import os
import sys
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cebi_snr_contour_playground as pg  # noqa: E402  (sibling module)

PCT_PARAMS = ["a", "b", "p", "signal_halfwidth"]   # perturbed by fraction
PCT_GRID = [-0.20, -0.10, 0.0, 0.10, 0.20]
THETA_ABS = [-4.0, -2.0, 0.0, 2.0, 4.0]            # deg (0 has no %)
N_ENSEMBLE = 200
JITTER = 0.20                                       # +/-20% joint
THETA_JITTER = 4.0                                  # +/- deg joint
SEED = 0


def _perturb(base, **over):
    g = dict(base)
    g.update(over)
    return g


def one_at_a_time(ft, base, snr0):
    """Vary each param alone; rows: (param, perturb, value, snr, frac_dev)."""
    rows = []
    for prm in PCT_PARAMS:
        for f in PCT_GRID:
            val = base[prm] * (1.0 + f)
            snr = pg.cebi_snr(ft, _perturb(base, **{prm: val}))
            rows.append((prm, f, val, snr, (snr - snr0) / snr0))
    for dt in THETA_ABS:
        snr = pg.cebi_snr(ft, _perturb(base, theta=base["theta"] + dt))
        rows.append(("theta(+deg)", dt, base["theta"] + dt, snr,
                     (snr - snr0) / snr0))
    return rows


def joint_ensemble(ft, base, snr0):
    """N draws, every param jittered +/-JITTER simultaneously (fixed seed)."""
    rng = np.random.default_rng(SEED)
    out = np.empty(N_ENSEMBLE)
    for i in range(N_ENSEMBLE):
        g = dict(base)
        for prm in PCT_PARAMS:
            g[prm] = base[prm] * (1.0 + rng.uniform(-JITTER, JITTER))
        g["theta"] = base["theta"] + rng.uniform(-THETA_JITTER, THETA_JITTER)
        out[i] = pg.cebi_snr(ft, g)
    return out


def write_csv(rows, path):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["param", "perturb", "value", "snr", "frac_dev_from_snr0"])
        for r in rows:
            w.writerow([r[0], f"{r[1]:.4f}", f"{r[2]:.4f}",
                        f"{r[3]:.6f}", f"{r[4]:+.4f}"])


def tornado_png(rows, snr0, path):
    """Max |frac dev| per param over its sweep -> horizontal bar chart."""
    params, mags = [], []
    for prm in PCT_PARAMS + ["theta(+deg)"]:
        devs = [abs(r[4]) for r in rows if r[0] == prm]
        params.append(prm)
        mags.append(max(devs) * 100 if devs else 0.0)
    order = np.argsort(mags)
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.barh([params[i] for i in order], [mags[i] for i in order],
            color="steelblue")
    ax.set_xlabel("max |GT SNR deviation| over the sweep (% of SNR0)")
    ax.set_title(f"CeBi GT SNR sensitivity (SNR0 = {snr0:.3f})")
    ax.grid(True, axis="x", alpha=0.3)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def contour_envelope_png(ft, base, path):
    """Locked superellipse + its +/-20% a,b,p envelope drawn on the GT FT,
    so the perturbation stays visibly on the diamond (not on Bragg/center)."""
    H, W = ft.shape
    cx = (W - 1) / 2 if base["cx"] is None else base["cx"]
    cy = (H - 1) / 2 if base["cy"] is None else base["cy"]
    c, sd = np.mean(ft), np.std(ft)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(ft, origin="lower", cmap=pg.stmpy.cm.gray_r,
              clim=[0, c + 3 * sd])
    variants = [("locked", base["a"], base["b"], base["p"], "cyan", 1.6)]
    for f, col in [(-JITTER, "orange"), (JITTER, "lime")]:
        variants.append((f"a,b,p {f:+.0%}", base["a"] * (1 + f),
                         base["b"] * (1 + f), base["p"] * (1 + f), col, 1.0))
    for lbl, a, b, p, col, lw in variants:
        pts, _ = pg.superellipse_perimeter(240, a, b, p, base["theta"], cx, cy)
        ax.plot(np.r_[pts[:, 0], pts[0, 0]], np.r_[pts[:, 1], pts[0, 1]],
                "-", color=col, lw=lw, label=lbl)
    ax.set_xticks(np.arange(0, W + 1, 16))
    ax.set_yticks(np.arange(0, H + 1, 16))
    ax.grid(True, alpha=0.3, lw=0.4)
    ax.set_title("locked superellipse + /-20% envelope on CeBi GT FT")
    ax.legend(loc="upper right")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def robustness_verdict(snr0, ensemble, oat_rows):
    """TODO(human): the scientific call this whole study exists to make.

    Inputs:
      snr0      : baseline GT SNR at the locked geometry (~4.08)
      ensemble  : np.ndarray of GT SNRs, N draws with EVERY geom param
                  jittered +/-20% simultaneously
      oat_rows  : the one-at-a-time rows (param, perturb, value, snr, frac_dev)

    Return (is_robust: bool, verdict: str).

    This is YOURS because the threshold is a scientific judgment about your
    own paper that you must defend to a referee: what fractional GT-SNR
    spread is small enough to claim the conclusion does not depend on the
    exact ROI? A common bar is the 5-95th-percentile ensemble spread staying
    within ~10-15% of snr0 -- but you choose and own the number. Keep it
    ~3-8 lines; the returned string is the sentence that would go in the
    methods / reviewer response and must quote the ACTUAL measured spread
    (compute it from `ensemble` and `snr0`), not a placeholder.
    """
    raise NotImplementedError("robustness_verdict: see TODO(human)")


def main():
    ft = pg.load_cebi_ft()
    base = pg.GEOM_LOCKED
    snr0 = pg.cebi_snr(ft, base)
    print(f"SNR0 (locked geometry) = {snr0:.4f}")

    oat = one_at_a_time(ft, base, snr0)
    ens = joint_ensemble(ft, base, snr0)

    # artifacts are written BEFORE the verdict so they exist regardless
    write_csv(oat, "figures/cebi_snr_sensitivity.csv")
    tornado_png(oat, snr0, "figures/cebi_snr_sensitivity_tornado.png")
    contour_envelope_png(ft, base, "figures/cebi_snr_sensitivity_contours.png")

    lo, hi = np.percentile(ens, [5, 95])
    print(f"one-at-a-time: {len(oat)} evaluations -> "
          "figures/cebi_snr_sensitivity.csv")
    print(f"joint ensemble N={N_ENSEMBLE} (+/-{JITTER:.0%} all params): "
          f"mean {ens.mean():.4f}  std {ens.std():.4f}  "
          f"5-95% [{lo:.4f}, {hi:.4f}]  "
          f"spread {(hi - lo) / snr0 * 100:.1f}% of SNR0")
    print("artifacts: cebi_snr_sensitivity_{tornado,contours}.png")

    is_robust, verdict = robustness_verdict(snr0, ens, oat)
    print(f"\nVERDICT (robust={is_robust}): {verdict}")


if __name__ == "__main__":
    main()
