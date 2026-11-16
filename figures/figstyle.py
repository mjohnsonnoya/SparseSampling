"""House style for manuscript figures: the Hoffman-lab figure standard as code.

Rules come from J. E. Hoffman, "How To Write a Scientific Paper", Sec. V and
Appendix A (https://hoffman.physics.harvard.edu/Hoffman-Example-Paper.pdf, copy
in references/). Importing this module applies the style, so a figure script
cannot drift from its siblings:

    import figstyle as fs
    fig = fs.new_figure('col', height=3.1)        # built at final print width
    im = fs.image(ax, data, extent=(0, 40, 0, 40), cmap=..., vmin=..., vmax=...)
    fs.scalebar(ax, 10, '10 nm')
    fs.save(fig, 'fig3_drift_results')            # -> figures/out/<name>.pdf + .png

Then run the gate:  .venv/bin/python figures/check_figure.py figures/out/<name>.pdf
See figures/README.md for the whole loop and for which script makes which figure.
"""
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.text import Text

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')     # everything generated goes here, never beside the code

# APS column widths in inches (8.6 cm and 17.8 cm). "Start by deciding how wide
# your final figure will be ... and build your figure within it."
WIDTHS = {'col': 3.375, 'full': 7.0}
MIN_PT = 6                      # "All figure fonts should be at least size 6"
INK = '#231f20'                 # the near-black the existing figures use

RC = {
    # Fonts: Arial everywhere, including math, embedded as TrueType (type 42).
    # matplotlib's default type 3 is what publisher checks reject.
    'font.family': 'Arial',
    'pdf.fonttype': 42, 'ps.fonttype': 42,
    'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial',
    'mathtext.it': 'Arial:italic', 'mathtext.bf': 'Arial:bold',
    # Sizes locked across the manuscript (see the sparse-sampling-figures skill).
    'font.size': 7, 'axes.labelsize': 7, 'axes.titlesize': 8,
    'xtick.labelsize': 6, 'ytick.labelsize': 6, 'legend.fontsize': 6,
    'xtick.major.pad': 2, 'ytick.major.pad': 2, 'axes.labelpad': 2,
    # Less non-data ink.
    'axes.linewidth': 0.5, 'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
    'legend.frameon': False,
    # Honest pixels: never resample a data image.
    'image.interpolation': 'none',
    'savefig.dpi': 300,
}


def apply():
    """Apply the house rcParams. Fails loudly when Arial is missing, because a
    silent fallback is how a figure ends up in DejaVu Sans."""
    font_manager.findfont('Arial', fallback_to_default=False)
    mpl.rcParams.update(RC)


def new_figure(width, height, **kw):
    """A figure at its final printed width. width: 'col' (3.375 in) or 'full' (7 in)."""
    return plt.figure(figsize=(WIDTHS[width], height), **kw)


def image(ax, data, frame=False, **kw):
    """Draw a data image with one PDF sample per data pixel.

    interpolation='none' on a non-rasterized artist makes the PDF backend embed
    the array itself, so the viewer scales it and nothing is blurred. Do not
    pass rasterized=True: that routes the image through a renderer that
    resamples it to the figure dpi (how the old 250 px maps became blurred
    308 px rasters). Pass extent= in physical units so scale bars are honest.
    """
    if kw.pop('rasterized', False):
        raise ValueError('rasterized=True resamples data images; leave it out')
    kw['interpolation'] = 'none'
    kw.setdefault('origin', 'lower')
    im = ax.imshow(data, **kw)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(frame)
    # Remembered for save(), which writes the shapes into the PDF so the gate
    # can confirm the embedded rasters are the data arrays, pixel for pixel.
    fig = ax.figure
    fig._figstyle_images = getattr(fig, '_figstyle_images', []) + [np.shape(data)[:2]]
    return im


def shared_clim(arrays, zero_floor=False):
    """One (vmin, vmax) for a set of panels that share a colorbar.

    arrays      list of 2-D arrays; arrays[0] is the reference panel (for
                example the ground truth). NaN marks an unmeasured pixel.
    zero_floor  True for magnitudes (Fourier transforms): the lower limit is 0.

    Panels drawn with one colorbar must use one pair of limits, so every figure
    script gets its limits here instead of computing them inline.

    Policy: the reference panel's mean +/- 5 sigma (0 to mean + 5 sigma for
    magnitudes). This is the rule the notebooks used, so the published look
    carries over. Limits are rounded to two significant figures so the colorbar
    reads cleanly. The other arrays are listed so the call site names every
    panel on the colorbar, and so a pooled policy is a change to this function
    only.
    """
    ref = np.asarray(arrays[0], dtype=float)
    c, s = np.nanmean(ref), np.nanstd(ref)
    lo, hi = (0.0, c + 5 * s) if zero_floor else (c - 5 * s, c + 5 * s)
    return float(f'{lo:.2g}'), float(f'{hi:.2g}')


def scalebar(ax, length, label, color='w', loc='lower right', size=7, box=False, anchor=None):
    """A scale bar of `length` data units with its number written on it
    ("an accurate length scalebar, with numerical label"), in a corner of the
    image. box=True puts a translucent white patch behind it, for images with
    no quiet corner (a sparse map, for example). anchor=(x, y), in axes
    fractions, moves the corner the bar is pinned to, to step around a feature
    that sits in the corner (a Bragg peak, for example)."""
    from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
    y0, y1 = ax.get_ylim()
    where = {} if anchor is None else dict(bbox_to_anchor=anchor, bbox_transform=ax.transAxes)
    bar = AnchoredSizeBar(ax.transData, length, label, loc, pad=0.3 if box else 0.5,
                          borderpad=0.3 if box else 0.2, sep=2, color=color,
                          frameon=box, label_top=True,
                          size_vertical=abs(y1 - y0) * 0.012,
                          fontproperties=font_manager.FontProperties(size=size), **where)
    if box:
        bar.patch.set(facecolor='w', edgecolor='none', alpha=0.85)
    ax.add_artist(bar)
    return bar


def colorbar(im, cax, unit=None, ticks=None, fmt='%g', labels=None, side='right', inset=False):
    """A colorbar marked at its two limits.

    With a unit: numbers at the limits and the unit on top, horizontal
    ("labeled with numerical values and units if possible"). Use this when the
    number means something to the reader (a height in pm).

    With labels=('Low', 'High') or ('0', 'High'): words instead of numbers, for
    quantities whose absolute scale carries no meaning, such as a Fourier
    magnitude (its value depends on the normalization convention) or a raw
    lock-in signal. What the reader needs there is which panels share the bar.

    side='left' puts the labels on the left, for a bar left of its panels.
    inset=True writes the two labels inside the bar at its ends (the lab's
    usual "L" and "H"), in white or ink, whichever contrasts with that end of
    the colormap. The bar then needs no label margin; make it about 0.14 in wide.
    """
    cb = cax.figure.colorbar(im, cax=cax)
    if inset:
        cb.set_ticks([])
        cb.outline.set_linewidth(0.5)
        for y, text, va, (r, g, b, _) in ((0.02, labels[0], 'bottom', im.cmap(0.0)),
                                          (0.98, labels[1], 'top', im.cmap(1.0))):
            dark = 0.299 * r + 0.587 * g + 0.114 * b < 0.5
            cax.text(0.5, y, text, transform=cax.transAxes, ha='center', va=va,
                     fontsize=mpl.rcParams['font.size'], color='w' if dark else INK)
        return cb
    cb.ax.yaxis.set_ticks_position(side)
    cb.set_ticks(list(im.get_clim()) if ticks is None else ticks)
    if labels is None:
        cb.ax.yaxis.set_major_formatter(lambda v, _: (fmt % v).replace('-', '−'))   # true minus sign
    else:
        cb.set_ticklabels(labels)
    cb.ax.tick_params(length=2, pad=1.5)
    cb.outline.set_linewidth(0.5)
    if ticks is None:
        # Keep the two end labels inside the bar's height, so a bar can span
        # its whole row without its labels running into the next row's.
        ends = cb.ax.get_yticklabels()
        ends[0].set_verticalalignment('bottom')
        ends[-1].set_verticalalignment('top')
    if unit:
        cax.set_title(unit, fontsize=mpl.rcParams['ytick.labelsize'], pad=3)
    return cb


def panel_label(ax, letter, note='', on_image=False, x=0.03, y=0.97):
    """Bold "(a)" in the top-left corner; `note` follows it, e.g. "(a) -22 mV".
    on_image=True draws white text on a gray badge, readable over any colormap."""
    text = f'({letter})' + (f' {note}' if note else '')
    style = (dict(color='w', bbox=dict(facecolor='0.4', edgecolor='none', alpha=0.8, pad=1.5))
             if on_image else
             dict(color=INK, bbox=dict(facecolor='w', edgecolor='none', alpha=0.7, pad=1)))
    return ax.text(x, y, text, transform=ax.transAxes, fontsize=8, fontweight='bold',
                   va='top', ha='left', **style)


def save(fig, name):
    """Write figures/out/<name>.pdf and a 300 dpi PNG after two checks that are
    exact here and only approximate from the PDF: final width and font size.

    No bbox_inches='tight': it would change the page width the figure was
    built at. Output stays in figures/out/; copying into paper/ is a separate,
    reviewed step.
    """
    w = fig.get_figwidth()
    if not any(abs(w - v) < 1e-6 for v in WIDTHS.values()):
        raise ValueError(f'figure is {w:.3f} in wide; use new_figure("col") or new_figure("full")')
    fig.canvas.draw()
    small = sorted({(t.get_fontsize(), t.get_text()) for t in fig.findobj(Text)
                    if t.get_visible() and t.get_text().strip() and t.get_fontsize() < MIN_PT})
    if small:
        raise ValueError(f'text below {MIN_PT} pt: ' + ', '.join(f'{s:g} pt {t!r}' for s, t in small))
    shapes = ','.join(f'{h}x{w}' for h, w in getattr(fig, '_figstyle_images', []))
    os.makedirs(OUT, exist_ok=True)
    pdf = os.path.join(OUT, name + '.pdf')
    fig.savefig(pdf, metadata={'Keywords': f'figstyle images={shapes}'})
    fig.savefig(pdf[:-4] + '.png')
    print(f'saved {pdf} (+ .png), {w:g} in wide, {len(shapes.split(",")) if shapes else 0} data image(s)')
    return pdf


apply()
