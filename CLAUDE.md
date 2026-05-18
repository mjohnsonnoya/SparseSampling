# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Research project for a paper on accelerating quasiparticle interference (QPI) measurements using sparse sampling with compressed sensing and drift correction. The material system is Bi2Sr2CaCu2O8+d (BSCCO), measured via scanning tunneling microscopy (STM).

The core idea: sparsely sample dI/dV maps (25% of pixels), reconstruct via Basis Pursuit Denoising (BPDN), and correct for nonlinear tip drift using simultaneously acquired full-grid topography.

## Environment

- Python 3.11 venv managed by uv: `.venv/`
- Activate: `source .venv/bin/activate`
- Run scripts: `.venv/bin/python scratch.py`
- Run notebooks: use Jupyter with the `.venv` kernel

## Key Dependencies

- **stmpy** (hoffmanstmpy): STM data I/O (`.sxm`, `.3ds`, `.spy`), FFT utilities (`stmpy.tools.fft`, `stmpy.tools.find_extrema`), drift correction (`stmpy.driftcorr`), colormaps (`stmpy.cm.blue2`, `stmpy.cm.gray_r`)
- **spgl1**: Solver for BPDN (L1 minimization for compressed sensing reconstruction)
- **numpy/scipy**: Signal processing, FFT, linear algebra
- **opencv-python**: Image processing (used in adaptive sampling)
- **matplotlib**: All plotting

## Repository Structure

- `manuscript.tex` — RevTeX4-2 paper (PRB format). Uses custom macros for Q-vectors (`\Qmag`, `\Qlat`, etc.) and paragraph numbering (`\ptitle{}`)
- `notebooks/` — Jupyter notebooks for analysis and figure generation. All `savefig()` calls save to `../figures/`.
  - `Sparse_sampling_figure_plot.ipynb` — Main figures for the paper
  - `Sparse_sampling_figure_plot_for_40_nm_map.ipynb` — 40 nm map figures
  - `Adaptive_sparse_sampling.ipynb` — Adaptive sparse sampling analysis
  - `Stmpy_102_dfc_tutorial_dev.ipynb` — Drift correction tutorial/development
  - `fft_figs.ipynb` — FFT visualization figures
- `figures/` — Figure generation scripts (`.py`) and all generated figure outputs (PNGs and PDFs). All figures for the paper should reside here. PNGs and PDFs are gitignored.
- `references/` — Reference papers and theses (all gitignored by `*.pdf`)
- `data/` — STM data files (`.sxm` topography, `.3ds` spectroscopy, `.spy` processed maps, `.h5` reconstructions), sparse sampling masks (TSP-ordered pixel positions)
- `scratch.py` — Quick experimentation script

## Data Naming Conventions

- **`LIY`** (uppercase): Raw lock-in Y (dI/dV) data as loaded from instrument files by `stmpy.io`. Unprocessed 3D cube `[n_energies, nx, ny]`.
- **`liy`** (lowercase): Processed/cropped/reconstructed working copy of the dI/dV data. Lowercase signals the data has been touched (cropped, reconstructed from sparse sampling, etc.).
- **`liy_c`**: Drift-corrected version of `liy` (produced by `stmpy.driftcorr`).
- **`d.Z`** (uppercase): Raw topography data (2D) as loaded from instrument. For `.3ds` files, extracted as `self.Z = self.Z[0]`.
- **`d.z`** (lowercase): Processed topography (e.g., `stmpy.tools.lineSubtract(d.Z, 1)`).

## Domain Context

- **QPI**: Quasiparticle interference patterns visible in Fourier transforms of dI/dV maps; reveals electronic band structure
- **Compressed sensing**: Reconstruct full image from sparse measurements when signal is sparse in some basis (here, Fourier space)
- **BPDN**: min ||x||_1 subject to ||Ax - y||_2 <= epsilon, where A = P_Omega * F^{-1}
- **Drift correction**: Uses phase maps from topography FFTs to correct for STM tip drift during long acquisitions
- FFT axes: Delta_q = 2*pi/L (depends only on scan length L), q_max = pi/Delta_x (Nyquist, depends on pixel spacing)

## Writing conventions

Marcos's background is in math and computer science; he has not taken formal quantum mechanics coursework. When a concept can be expressed with either physics-flavored or math/CS-flavored vocabulary, default to the math/CS form — both for readability and because the manuscript's contribution is signal processing and reconstruction, not physics.

Specific preferences:
- **"Fourier space"** instead of **"momentum space"** for the FT plane of STM data.
- **"Defects"** instead of **"scattering centers"** or **"impurity-bound states"** when referring to the localized real-space features the adaptive sampling targets.
- **No em dashes** (`---` in LaTeX). For parenthetical asides, use parentheses; for stronger separations, use semicolons or a fresh sentence. Em dashes only with explicit user request.

Exceptions are unavoidable cases where a physics noun names the actual object being discussed (e.g., "momentum-resolved scattering" describing the physics of QPI). In those, keep the physics term. When in doubt, ask, don't silently swap terminology in passages where the physics meaning is doing real work.

## Bibliography conventions

**`paper/refs.bib` entries are alphabetized by first-author last name** (Hoffman lab guideline). When adding a new BibTeX entry, insert it in the correct alphabetical slot rather than appending to the end. Name particles like "van", "Le", etc. are treated as part of the surname for ordering (so "van den Berg" goes under "v", "Le Ster" goes under "Le"). For multiple papers by the same first author, order by publication year (oldest first).
