"""
Single-panel conceptual figure for one Fourier mode sampled at drifted coordinates.

Usage:
    .venv/bin/python figures/fig_fourier_mode_sampling_equation.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

try:
    plt.rcParams["font.family"] = "Arial"
except Exception:
    plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 7
plt.rcParams["axes.labelsize"] = 7
plt.rcParams["axes.titlesize"] = 8
plt.rcParams["xtick.labelsize"] = 6
plt.rcParams["ytick.labelsize"] = 6
plt.rcParams["xtick.major.pad"] = 2
plt.rcParams["ytick.major.pad"] = 2
plt.rcParams["axes.labelpad"] = 2


def cosine_mode(x, period):
    return np.cos(2 * np.pi * x / period)


def logarithmic_drift(x, scale, offset):
    return scale * np.log1p(x / offset)


L = 12.0
period = 4.0
n_grid = 10

x_dense = np.linspace(0, L, 1200)
x_grid = np.linspace(0.8, 11.2, n_grid)
u_grid = logarithmic_drift(x_grid, scale=0.42, offset=1.2)
x_drifted = x_grid - u_grid

y_dense = cosine_mode(x_dense, period)
y_drifted = cosine_mode(x_drifted, period)

mode_color = "#1f1f1f"
grid_color = "#cfcfcf"
uniform_color = "#0f8b8d"
drifted_color = "#c05a2b"
arrow_color = "#7a7a7a"

fig, ax = plt.subplots(figsize=(4.8, 2.6))

ax.plot(x_dense, y_dense, color=mode_color, lw=1.7, zorder=1)

for xg in x_grid:
    ax.axvline(xg, color=grid_color, lw=0.6, zorder=0)

ax.scatter(
    x_grid,
    np.full_like(x_grid, -1.18),
    s=26,
    marker="s",
    facecolor="white",
    edgecolor=uniform_color,
    linewidth=1.1,
    zorder=4,
)

ax.scatter(
    x_drifted,
    y_drifted,
    s=34,
    color=drifted_color,
    edgecolor="white",
    linewidth=0.4,
    zorder=5,
)

for xg, xd, yd in zip(x_grid, x_drifted, y_drifted):
    ax.plot([xd, xd], [-1.18, yd], color=drifted_color, lw=0.7, alpha=0.8, zorder=2)
    ax.annotate(
        "",
        xy=(xd, -1.03),
        xytext=(xg, -1.03),
        arrowprops=dict(arrowstyle="-|>", color=arrow_color, lw=0.6, shrinkA=0, shrinkB=0),
        zorder=3,
    )

ax.text(0.42, 0.88, r"$\tilde{F}(k)\; \sim\; \sum_n y_n e^{-ikx_n^\prime}$",
        transform=ax.transAxes, color=mode_color, ha="center")
ax.text(0.42, 0.79, r"sample one Fourier mode at drifted coordinates $x_n^\prime$",
        transform=ax.transAxes, color=drifted_color, ha="center")
ax.text(0.50, 0.07, r"uniform grid $x_n$", transform=ax.transAxes,
        color=uniform_color, ha="center")

ax.text(x_grid[2] - 0.05, -1.31, r"$x_n$", color=uniform_color, ha="center")
ax.text(x_drifted[2] + 0.18, y_drifted[2] + 0.11, r"$x_n^\prime$", color=drifted_color, ha="center")

ax.set_xlim(0, L)
ax.set_ylim(-1.42, 1.28)
ax.set_xticks([])
ax.set_yticks([-1, 0, 1])
ax.set_xlabel("position")
ax.set_ylabel(r"mode amplitude $\cos(kx)$")
ax.set_title("Off-Grid Sampling of One Fourier Mode")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout(pad=0.4)
fig.savefig("figures/fig_fourier_mode_sampling_equation.pdf", dpi=300, bbox_inches="tight", pad_inches=0.02)
fig.savefig("figures/fig_fourier_mode_sampling_equation.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
print("Saved figures/fig_fourier_mode_sampling_equation.pdf")
print("Saved figures/fig_fourier_mode_sampling_equation.png")
