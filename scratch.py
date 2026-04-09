import numpy as np
import matplotlib.pyplot as plt

# ── Parameters ──
L = 50.0        # scan length (nm)
d = L           # one full period across scan, so the effect is most visible
N = 25          # small N so individual samples are countable

# ── Case 1: include both endpoints (duplicate boundary) ──
x_dup = np.linspace(0, L, N)          # N points, includes x=0 AND x=L
z_dup = np.cos(2 * np.pi * x_dup / d)

# ── Case 2: exclude last endpoint (correct for FFT) ──
x_ok = np.linspace(0, L, N)[:-1]     # N-1 points, excludes x=L
z_ok = np.cos(2 * np.pi * x_ok / d)

# ── FFTs ──
fft_dup = np.abs(np.fft.fftshift(np.fft.fft(z_dup)))
fft_ok  = np.abs(np.fft.fftshift(np.fft.fft(z_ok)))

# Frequency axes (in cycles/nm)
freq_dup = np.fft.fftshift(np.fft.fftfreq(len(z_dup), d=x_dup[1] - x_dup[0]))
freq_ok  = np.fft.fftshift(np.fft.fftfreq(len(z_ok),  d=x_ok[1]  - x_ok[0]))

# ── Plotting ──
fig, axes = plt.subplots(2, 2, figsize=[10, 6])

# Top row: real-space signals with periodic tiling shown
for ax, x, z, title in [
    (axes[0, 0], x_dup, z_dup, f'With both endpoints (N={len(z_dup)})'),
    (axes[0, 1], x_ok,  z_ok,  f'Without last endpoint (N={len(z_ok)})'),
]:
    # Show one period as stems
    ax.stem(x, z, linefmt='C0-', markerfmt='C0o', basefmt='k-', label='samples')
    # Show the implicit "next period" from DFT wraparound
    ax.stem(x + L, z, linefmt='C1--', markerfmt='C1o', basefmt='k-', label='DFT periodic copy')
    # TODO(human): highlight the boundary seam between the two periods
    ax.set_xlabel('x (nm)')
    ax.set_ylabel('cos(2πx/L)')
    ax.set_title(title)
    ax.legend(fontsize=8)
    ax.set_xlim(-5, 2 * L + 5)

# Bottom row: FFT magnitudes
for ax, freq, fft_mag, title in [
    (axes[1, 0], freq_dup, fft_dup, 'FFT — with duplicate endpoint'),
    (axes[1, 1], freq_ok,  fft_ok,  'FFT — correct sampling'),
]:
    ax.stem(freq, fft_mag, linefmt='C0-', markerfmt='C0o', basefmt='k-')
    ax.set_xlabel('Frequency (1/nm)')
    ax.set_ylabel('|FFT|')
    ax.set_title(title)

plt.tight_layout()
plt.savefig('scratch_output.pdf', dpi=150)
plt.savefig('scratch_output.png', dpi=150)
plt.show()
