"""CeBi adaptive-vs-uniform SNR-vs-sparsity sweep (A1(ii)).

Reproducible, version-controlled replacement for the orphan
`data/cebi_snr_vs_sparsity.npz` (which had no generating code and degenerate
contents). Produces the CeBi ASS-vs-uniform gain the manuscript's second [TBD]
needs -- once the finalized CeBi SNR metric is ported here (Pass 2).

CeBi data: data/2019-07-11-002 LIY local corr new.spy  (data[1] in
Adaptive_sparse_sampling.ipynb). GT map = LIY[mid energy] / mean, 256x256.

Reconstruction recipe mirrors the 40 nm notebook's reconstruct_from_indices:
A = P_Omega F^{-1}, BPDN via spgl1, sigma = 1e-2 * ||b||_2 / sqrt(k).

Run: .venv/bin/python figures/cebi_ass_vs_uniform_snr.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.sparse.linalg import LinearOperator
from spgl1 import spg_bpdn
import stmpy

st = stmpy.tools

CEBI = "data/2019-07-11-002 LIY local corr new.spy"
# Hardcoded CeBi Bragg-peak pixel coords (from Adaptive_sparse_sampling.ipynb cell 46,
# the 256x256 FT of this exact map). Used only to build the adaptive mask.
CEBI_BRAGG = np.array([[66, 170], [169, 178], [80, 70], [182, 80]])


def load_cebi_gt():
    """CeBi ground-truth full-grid map (normalized) + its FT."""
    d = stmpy.load(CEBI, biasOffset=False)
    idx = len(d.en) // 2
    z = d.LIY[idx] / np.mean(d.LIY[idx])
    return z, st.fft(z, zeroDC=True)


def _partial_fourier_op(idx, n):
    """A = P_Omega F^{-1} as a spgl1-compatible complex LinearOperator.

    matvec : Fourier coeffs (len n) -> sampled real-space values (len k)
    rmatvec: sampled values (len k) -> zero-filled, FFT'd (len n)
    Mirrors the notebook's 1-D fft on the flattened length-n vector.
    """
    k = len(idx)

    def mv(x):
        return np.real(np.fft.ifft(x))[idx]

    def rmv(y):
        full = np.zeros(n, dtype=complex)
        full[idx] = y
        return np.fft.fft(full)

    return LinearOperator((k, n), matvec=mv, rmatvec=rmv, dtype=complex)


def reconstruct(gt_flat, idx, nx, ny):
    """Noiseless CS reconstruction from spatial samples at idx (BPDN)."""
    b = gt_flat[idx]
    b0 = b - np.mean(b)
    op = _partial_fourier_op(idx, len(gt_flat))
    sigma = 1e-2 * np.linalg.norm(b0) / np.sqrt(len(idx))
    x, *_ = spg_bpdn(op, b0, sigma, iter_lim=int(1e5), verbosity=0)
    rec = np.real(np.fft.ifft(x).reshape(nx, ny))
    return rec + np.mean(b)


def uniform_indices(n, k, rng):
    return np.sort(rng.choice(n, size=k, replace=False))


def adaptive_indices(z_gt, k, nx, ny, rng):
    """5%-uniform + feature-driven Gaussian-density draw, faithfully ported
    from Adaptive_sparse_sampling.ipynb cells 46-54 (Bragg-notch -> defect
    find -> intensity-weighted Gaussians -> rejection sample)."""
    # Bragg-notch in Fourier space -> real-space lattice-suppressed map
    ft = np.fft.fftshift(np.fft.fft2(z_gt))
    yy, xx = np.mgrid[0:ny, 0:nx]
    notch = np.ones((ny, nx))
    for bx, by in CEBI_BRAGG:
        notch *= 1 - np.exp(-(((xx - bx) ** 2 + (yy - by) ** 2) / (2 * 5.0 ** 2)))
    z_masked = np.real(np.fft.ifft2(np.fft.ifftshift(ft * notch)))
    # Defect peaks -> intensity-weighted Gaussian probability mask
    coords = st.find_extrema(z_masked, n=(19, 0))
    g = np.array([z_masked[int(a), int(b)] for a, b in coords])
    inten = (g - z_masked.min()) / (z_masked.max() - z_masked.min())
    r = 25 * inten
    grid = np.arange(nx)
    mask = sum(
        st.gauss2d(grid, grid,
                   p=[coords[i, 1], coords[i, 0], r[i], r[i], inten[i], inten[i]])
        for i in range(len(coords))
    )
    mask /= mask.max()
    k_unif = round(0.5 * k)                       # half uniform baseline
    idx = list(uniform_indices(nx * ny, k_unif, rng))
    while len(idx) < k:                           # rejection-sample the rest
        px, py = rng.integers(0, nx), rng.integers(0, ny)
        if rng.random() < mask[px, py]:
            idx.append(px * ny + py)
    return np.sort(np.array(idx))


def cebi_snr(ft_2d):
    """SNR of a CeBi QPI Fourier-transform map.

    CeBi's QPI signal is NOT a diagonal streak (unlike BSCCO, where a 1-D
    51.5-deg linecut works). It is a 2-D outer superellipse / diamond; the
    noise floor is the surrounding whitespace. A linecut would slice two thin
    chords and miss most of the signal, so this needs a 2-D region estimator.

    TODO (Pass 2 port): the metric is now FINALIZED and validated in
    figures/cebi_snr_contour_playground.py (perpendicular-profile windowed-max
    along a superellipse contour; geometry frozen as GEOM_LOCKED). Pass 2
    ports `superellipse_perimeter` + the geometry-parameterized `cebi_snr`
    here and applies the SINGLE locked geometry identically to GT / uniform /
    adaptive (never re-fit per reconstruction). Not a human-input task.
    """
    raise NotImplementedError("cebi_snr: Pass 2 port from "
                              "cebi_snr_contour_playground.py (see plan)")


def sweep(sparsities=(0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50),
          n_trials=3, seed0=0):
    z_gt, gt_ft = load_cebi_gt()
    nx, ny = z_gt.shape
    flat = z_gt.flatten()
    N = nx * ny
    gt_snr = cebi_snr(gt_ft)
    out = {"uniform": {}, "adaptive": {}, "gt_snr": gt_snr}
    for sp in sparsities:
        k = int(round(sp * N))
        u_t, a_t = [], []
        for t in range(n_trials):
            rng = np.random.default_rng(seed0 + 1000 * int(sp * 100) + t)
            ru = uniform_indices(N, k, rng)
            ra = adaptive_indices(z_gt, k, nx, ny, rng)
            u_t.append(cebi_snr(st.fft(reconstruct(flat, ru, nx, ny), zeroDC=True)))
            a_t.append(cebi_snr(st.fft(reconstruct(flat, ra, nx, ny), zeroDC=True)))
        out["uniform"][sp] = u_t
        out["adaptive"][sp] = a_t
        print(f"  {sp:.0%}: uniform {np.mean(u_t):.3f}  adaptive {np.mean(a_t):.3f}")
    return out


if __name__ == "__main__":
    res = sweep()
    np.savez("data/cebi_ass_vs_uniform_snr.npz", **{
        "gt_snr": res["gt_snr"],
        "sparsities": np.array(sorted(res["uniform"])),
        "uniform": res["uniform"], "adaptive": res["adaptive"],
    })
    s25 = 0.25
    g = np.mean(res["adaptive"][s25]) - np.mean(res["uniform"][s25])
    print(f"\nCeBi ASS-vs-uniform gain @ 25% : {g:+.3f} SNR "
          f"(uniform {np.mean(res['uniform'][s25]):.3f} -> "
          f"adaptive {np.mean(res['adaptive'][s25]):.3f})")
    print("Saved data/cebi_ass_vs_uniform_snr.npz")
