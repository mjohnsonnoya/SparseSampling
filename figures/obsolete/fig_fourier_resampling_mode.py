"""
Conceptual two-panel figure for NUDFT-style drift correction.

Panel (a): one cosine Fourier mode evaluated at drifted, off-grid coordinates.
Panel (b): reconstruction back onto the corrected uniform grid.

Usage:
    .venv/bin/python figures/fig_fourier_resampling_mode.py
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
plt.rcParams["axes.titlesize"] = 7.5
plt.rcParams["xtick.labelsize"] = 6
plt.rcParams["ytick.labelsize"] = 6
plt.rcParams["xtick.major.pad"] = 2
plt.rcParams["ytick.major.pad"] = 2
plt.rcParams["axes.labelpad"] = 2


def cosine_mode(x, period):
    return np.cos(2 * np.pi * x / period)


def logarithmic_drift(x, scale, offset):
    return scale * np.log1p(x / offset)


def label_panel(ax, letter):
    ax.text(
        0.03,
        0.95,
        f"({letter})",
        transform=ax.transAxes,
        fontsize=8,
        fontweight="bold",
        va="top",
        ha="left",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=1),
    )


L = 12.0
period = 4.0
n_grid = 9

x_dense = np.linspace(0, L, 1000)
x_grid = np.linspace(0.75, 11.25, n_grid)
u_grid = logarithmic_drift(x_grid, scale=0.34, offset=1.1)
x_drifted = x_grid - u_grid

y_dense = cosine_mode(x_dense, period)
y_drifted = cosine_mode(x_drifted, period)
y_grid = cosine_mode(x_grid, period)

purple = "#8e63ce"
green = "#69b96d"
mode_color = "#202020"
grid_color = "#d6d6d6"

fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.5), sharey=True)

# Panel (a): off-grid evaluation
ax = axes[0]
ax.plot(x_dense, y_dense, color=mode_color, lw=1.5, zorder=1)

for xg in x_grid:
    ax.axvline(xg, color=grid_color, lw=0.6, zorder=0)

ax.scatter(
    x_grid,
    np.full_like(x_grid, -1.18),
    s=24,
    marker="s",
    facecolor="white",
    edgecolor=green,
    linewidth=1.0,
    zorder=4,
)
ax.scatter(
    x_drifted,
    y_drifted,
    s=28,
    color=purple,
    edgecolor="white",
    linewidth=0.4,
    zorder=5,
)

for xg, xd, yd in zip(x_grid, x_drifted, y_drifted):
    ax.plot([xd, xd], [-1.18, yd], color=purple, lw=0.7, alpha=0.75, zorder=2)
    ax.annotate(
        "",
        xy=(xd, -1.05),
        xytext=(xg, -1.05),
        arrowprops=dict(arrowstyle="-|>", color=purple, lw=0.6, shrinkA=0, shrinkB=0),
        zorder=3,
    )

ax.text(6.0, 1.12, r"evaluate one mode at $x_n^\prime$", color=purple, ha="center")
ax.text(6.0, -1.36, r"target grid stays uniform", color=green, ha="center")
ax.text(x_grid[1] - 0.18, -1.28, r"$x_n$", color=green, ha="center")
ax.text(x_drifted[1] + 0.22, y_drifted[1] + 0.12, r"$x_n^\prime$", color=purple, ha="center")
ax.set_title(r"Drifted Sampling of One Fourier Mode")
ax.set_xlabel("position")
ax.set_ylabel(r"mode amplitude $\mathrm{Re}[e^{ikx}] = \cos(kx)$")
ax.set_xlim(0, L)
ax.set_ylim(-1.45, 1.3)
ax.set_yticks([-1, 0, 1])
ax.set_xticks([])
label_panel(ax, "a")

# Panel (b): back to the corrected uniform grid
ax = axes[1]
ax.plot(x_dense, y_dense, color=mode_color, lw=1.5, zorder=1)

for xg in x_grid:
    ax.axvline(xg, color=grid_color, lw=0.6, zorder=0)

ax.scatter(
    x_drifted,
    y_drifted,
    s=20,
    facecolor="none",
    edgecolor=purple,
    linewidth=0.9,
    alpha=0.7,
    zorder=4,
)
ax.scatter(
    x_grid,
    y_grid,
    s=28,
    color=green,
    edgecolor="white",
    linewidth=0.4,
    zorder=5,
)

for xg, yg in zip(x_grid, y_grid):
    ax.plot([xg, xg], [0, yg], color=green, lw=0.8, alpha=0.8, zorder=2)

for xd, yd, xg, yg in zip(x_drifted, y_drifted, x_grid, y_grid):
    ax.annotate(
        "",
        xy=(xg, yg),
        xytext=(xd, yd),
        arrowprops=dict(arrowstyle="->", color="0.45", lw=0.55, alpha=0.8),
        zorder=3,
    )

ax.text(6.0, 1.12, r"inverse FFT places values on $x_n$", color=green, ha="center")
ax.text(6.0, -1.28, r"purple: off-grid evaluation, green: corrected grid", color="0.35", ha="center")
ax.set_title(r"Reconstruction on the Uniform Grid")
ax.set_xlabel("position")
ax.set_xlim(0, L)
ax.set_ylim(-1.45, 1.3)
ax.set_yticks([-1, 0, 1])
ax.set_xticks([])
label_panel(ax, "b")

for ax in axes:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

fig.tight_layout(w_pad=1.2)
fig.savefig("figures/fig_fourier_resampling_mode.pdf", dpi=300, bbox_inches="tight", pad_inches=0.02)
fig.savefig("figures/fig_fourier_resampling_mode.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
print("Saved figures/fig_fourier_resampling_mode.pdf")
print("Saved figures/fig_fourier_resampling_mode.png")
