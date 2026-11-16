"""Regenerate every array and every single-panel PDF behind Fig. 1 and Fig. 3,
following notebooks/Sparse_sampling_figure_plot_for_40_nm_map.ipynb cell by cell
(cells 3-14, 24, 52-57, 59, 27). Nothing here is new analysis; it is a transcript
of the notebook with show=False and files written to the scratchpad.
"""
import os, sys, time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
import stmpy, stmpy.tools as st, stmpy.driftcorr as dfc
from spgl1 import spg_bpdn
from scipy.sparse.linalg import LinearOperator

ROOT = '/Users/marcosjohnsonnoya/Coding/SparseSampling'
OUT = os.path.dirname(os.path.abspath(__file__))
PAN = os.path.join(OUT, 'panels'); os.makedirs(PAN, exist_ok=True)
t0 = time.time()
def log(*a): print(f'[{time.time()-t0:7.1f}s]', *a, flush=True)

# cells 3, 5, 6, 7
d1_true = stmpy.load(f'{ROOT}/data/Grid Spectroscopy-BSCCO-2022-09-04-002.3ds', biasOffset=False)
d = stmpy.load(f'{ROOT}/data/2022-09-05-BSCCO-SparseSamplingDOS-001.3ds', biasOffset=False)
t = stmpy.load(f'{ROOT}/data/2022-09-05_BSCCO_SparseSamplingTopo001.sxm')
t.z = st.lineSubtract(st.nsigma_local(t.Z), 2)
log('loaded', d1_true.LIY.shape, d.LIY.shape, t.Z.shape)

# cells 8, 9
ri_temp = np.loadtxt(f'{ROOT}/data/mask_250x250.txt')
ri = np.array([int(k) - 1 for k in ri_temp])
nx = ny = 250
class partialFourier(LinearOperator):
    def __init__(self, idx, n):
        self.idx = idx; self.n = n; self.shape = (len(idx), n); self.dtype = np.complex128
    def _matvec(self, x):
        z = np.fft.fft(x) / np.sqrt(self.n); return z[self.idx]
    def _rmatvec(self, x):
        z = np.zeros(self.n, dtype=complex); z[self.idx] = x; return np.fft.ifft(z) * np.sqrt(self.n)
n = nx * ny
opA = partialFourier(idx=ri, n=n)

# cell 13
b = np.copy(d.LIY[-1, 0, :]) * 1e15
result = np.full(nx * ny, np.nan); result[ri] = b
to_show = result.reshape((nx, ny))
for i in range(len(ri)):
    index = ri[i]; j = index // nx; k = index % ny
    to_show[j, k] = b[i]

# cell 14
gt_fA = d1_true.LIY[-1] * 1e15
c_gt = np.nanmean(gt_fA); s_gt = np.nanstd(gt_fA)
real_space_clims = [c_gt - 5 * s_gt, c_gt + 5 * s_gt]
gt_ft = st.fft(gt_fA, zeroDC=True)
c_ft = np.mean(gt_ft); s_ft = np.std(gt_ft)
ft_clims = [0, c_ft + 5 * s_ft]
log('clims', real_space_clims, ft_clims)

# cell 24
b_zeroDC = b - np.mean(b)
sigma = 1e-2 * np.linalg.norm(b_zeroDC)
x, resid, grad, info = spg_bpdn(opA, b_zeroDC, sigma, iter_lim=1e5, verbosity=0)
rec_bpdn = np.real(np.fft.ifft(x).reshape(nx, ny))[::-1, ::-1]
rec_bpdn_display = (rec_bpdn - np.nanmean(rec_bpdn)) / np.nanstd(rec_bpdn) * s_gt + c_gt
ft_bpdn = st.fft(rec_bpdn_display, zeroDC=True)
log('bpdn done, iters', info.get('iter'), 'stat', info.get('stat'))

# cells 52-57 (the "after" branch that produced the saved Fig. 3(b))
bpdn_after = dfc.findBraggs(rec_bpdn, r=0.5, min_dist=20, show=False)
bpc1_after = dfc.generate_bp(rec_bpdn, bp=bpdn_after, orient=None)
z1_after, p1_after = dfc.find_drift_parameter(rec_bpdn, bp_c=bpc1_after, sigma=10, cut2=[9, 0, 9, 0], show=False)
bp2_after = dfc.findBraggs(z1_after, r=0.2, show=False)
z2_after, p2_after = dfc.find_drift_parameter(z1_after, bp_c=bp2_after, sigma=13, show=False)
liy_temp = dfc.apply_drift_parameter(rec_bpdn, p1_after)
rec_bpdn_after = dfc.apply_drift_parameter(liy_temp, p2_after)
ft_bpdn_after = st.fft(rec_bpdn_after, zeroDC=True)
log('drift done', rec_bpdn_after.shape, 'bp after', bpdn_after, bp2_after)

to_show_fft = np.where(np.isnan(to_show), c_gt, to_show)
np.savez(os.path.join(OUT, 'arrays.npz'), tz=t.z, to_show=to_show, to_show_fft=to_show_fft, gt_fA=gt_fA,
         rec_bpdn=rec_bpdn, rec_bpdn_display=rec_bpdn_display, ft_bpdn=ft_bpdn, gt_ft=gt_ft,
         rec_bpdn_after=rec_bpdn_after, ft_bpdn_after=ft_bpdn_after,
         real_space_clims=real_space_clims, ft_clims=ft_clims, ri=ri)

# Single-panel PDFs exactly as the notebook wrote them (quick_plot + plt.savefig(bbox_inches='tight')).
def panel(name, A, **kw):
    dfc.quick_plot(A, thres=5, rasterized=True, **kw)
    plt.savefig(os.path.join(PAN, name + '.pdf'), bbox_inches='tight')
    plt.close('all')
panel('a_topo', t.z[::-1], cmap=stmpy.cm.blue2)                                                      # cell 21
panel('e_topo_ft', st.fft(t.z, zeroDC=True)[::-1], rspace=False, cmap=stmpy.cm.gray_r)                # cell 21
panel('b_sparse', to_show[::-1], cmap=stmpy.cm.jackyPSD, clims=real_space_clims)                      # cell 20
panel('f_sparse_ft', st.fft(to_show_fft, zeroDC=True)[::-1], rspace=False, cmap=stmpy.cm.gray_r, clims=ft_clims)
panel('d_gt', gt_fA[::-1], cmap=stmpy.cm.jackyPSD, clims=real_space_clims)                            # cell 22
panel('h_gt_ft', st.fft(gt_fA, zeroDC=True)[::-1], rspace=False, cmap=stmpy.cm.gray_r, clims=ft_clims)
panel('c_rec', rec_bpdn_display[::-1], cmap=stmpy.cm.jackyPSD, clims=real_space_clims)               # cell 26
panel('g_rec_ft', ft_bpdn[::-1], rspace=False, cmap=stmpy.cm.gray_r, clims=ft_clims)
panel('f3b_rec_after', rec_bpdn_after[::-1], cmap=stmpy.cm.jackyPSD)                                  # cell 59 (auto clims)
panel('f3d_rec_after_ft', ft_bpdn_after[::-1], rspace=False, cmap=stmpy.cm.gray_r)                    # cell 59 (auto clims)

# cell 27 colorbars
for name, cmap, clims in [('cb_real', stmpy.cm.jackyPSD, real_space_clims), ('cb_ft', stmpy.cm.gray_r, ft_clims)]:
    fig, ax = plt.subplots(figsize=[0.25, 2])
    norm = mpl.colors.Normalize(vmin=clims[0], vmax=clims[1])
    cb = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation='vertical')
    cb.set_ticks([clims[0], clims[1]]); cb.set_ticks([])
    cb.ax.tick_params(labelsize=10, length=0); cb.outline.set_visible(False)
    plt.savefig(os.path.join(PAN, name + '.pdf'), bbox_inches='tight'); plt.close('all')
log('panels written to', PAN)
