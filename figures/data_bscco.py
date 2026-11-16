"""The data behind Figs. 1 and 3: BSCCO, 40 nm field of view, 250 x 250 px, -22 mV.

One function, load(), that goes from the instrument files to the arrays the
figures draw. It is a transcript of
notebooks/Sparse_sampling_figure_plot_for_40_nm_map.ipynb (cells 3 to 14 and 24)
with the notebook's variable names kept, so a figure in the manuscript never
depends on notebook cell order. It runs in about 2 s; nothing is cached.

Inputs, in data/ (not in git):
  Grid Spectroscopy-BSCCO-2022-09-04-002.3ds    full-grid dI/dV map: the ground truth
  2022-09-05-BSCCO-SparseSamplingDOS-001.3ds    sparse dI/dV scan, 25% of the pixels
  2022-09-05_BSCCO_SparseSamplingTopo001.sxm    topography co-acquired with the sparse scan
  mask_250x250.txt                              which pixel each sparse measurement belongs to

load() returns a dict:
  tz                topography, bad pixels removed and line-subtracted, in metres    Fig. 1(a)
  to_show           sparse map in fA, NaN where nothing was measured                 Fig. 1(b)
  to_show_fft       to_show with NaN replaced by the ground-truth mean (for its FT)  Fig. 1(f)
  rec_bpdn          BPDN reconstruction in solver units (zero mean)                  Fig. 3
  rec_bpdn_display  rec_bpdn rescaled to the ground truth's mean and std, in fA      Fig. 1(c)
  gt_fA             full-grid map in fA                                              Fig. 1(d)

"fA" is the raw lock-in current signal (LIY x 1e15), not a conductance.
"""
import os
import numpy as np
import stmpy
import stmpy.tools as st
from spgl1 import spg_bpdn
from scipy.sparse.linalg import LinearOperator

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
NX = NY = 250


class PartialFourier(LinearOperator):
    """A = P_Omega F^-1: from Fourier coefficients to the measured pixels only."""

    def __init__(self, idx, n):
        self.idx, self.n = idx, n
        self.shape = (len(idx), n)
        self.dtype = np.complex128

    def _matvec(self, x):
        return (np.fft.fft(x) / np.sqrt(self.n))[self.idx]

    def _rmatvec(self, x):
        z = np.zeros(self.n, dtype=complex)
        z[self.idx] = x
        return np.fft.ifft(z) * np.sqrt(self.n)


def load():
    # cells 3 to 7: the three measurements
    full = stmpy.load(os.path.join(DATA, 'Grid Spectroscopy-BSCCO-2022-09-04-002.3ds'), biasOffset=False)
    sparse = stmpy.load(os.path.join(DATA, '2022-09-05-BSCCO-SparseSamplingDOS-001.3ds'), biasOffset=False)
    topo = stmpy.load(os.path.join(DATA, '2022-09-05_BSCCO_SparseSamplingTopo001.sxm'))
    tz = st.lineSubtract(st.nsigma_local(topo.Z), 2)

    # cells 8, 9: which pixels the sparse scan measured (the file counts from 1)
    ri = np.loadtxt(os.path.join(DATA, 'mask_250x250.txt')).astype(int) - 1

    # cell 13: the sparse measurements placed on the grid
    b = np.copy(sparse.LIY[-1, 0, :]) * 1e15
    to_show = np.full(NX * NY, np.nan)
    to_show[ri] = b
    to_show = to_show.reshape(NX, NY)

    # cell 14: the ground truth and its statistics
    gt_fA = full.LIY[-1] * 1e15
    c_gt, s_gt = np.nanmean(gt_fA), np.nanstd(gt_fA)

    # cell 24: BPDN, min ||x||_1 subject to ||A x - b||_2 <= sigma
    b_zero_dc = b - np.mean(b)
    sigma = 1e-2 * np.linalg.norm(b_zero_dc)
    x, *_ = spg_bpdn(PartialFourier(ri, NX * NY), b_zero_dc, sigma, iter_lim=1e5, verbosity=0)
    rec_bpdn = np.real(np.fft.ifft(x).reshape(NX, NY))[::-1, ::-1]
    rec_bpdn_display = (rec_bpdn - np.nanmean(rec_bpdn)) / np.nanstd(rec_bpdn) * s_gt + c_gt

    return dict(tz=tz, to_show=to_show, to_show_fft=np.where(np.isnan(to_show), c_gt, to_show),
                rec_bpdn=rec_bpdn, rec_bpdn_display=rec_bpdn_display, gt_fA=gt_fA)
