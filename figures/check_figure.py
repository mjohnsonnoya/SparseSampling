"""Gate: audit a figure PDF against the Hoffman figure checklist.

    .venv/bin/python figures/check_figure.py figures/out/NAME.pdf [--width col|full]
    .venv/bin/python figures/check_figure.py --paper     # every figure main.tex includes

Checks what a script can check (final width, fonts, font size at print scale,
pixel honesty, red-green pairs), writes a print-size PNG to figures/out/check/, then lists
the checklist items that need eyes next to the caption. Exit status 1 on any
FAIL. Needs poppler: pdfinfo, pdffonts, pdfimages, pdftohtml, pdftoppm.
"""
import html, os, re, subprocess, sys
from collections import Counter
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN_TEX = os.path.join(os.path.dirname(HERE), 'paper', 'main.tex')
LOOK_DIR = os.path.join(HERE, 'out', 'check')
WIDTHS = {'col': 3.375, 'full': 7.0}       # inches, same as figstyle.WIDTHS
MIN_PT = 6

EYES = """\
    [ ] all axes labeled, with units; a legend covers every symbol and line
    [ ] each image (or same-scale set) has a scale bar with its number on it
    [ ] each image (or same-palette set) has a colorbar with numbers and units
    [ ] words on the graphic are concise, clear and horizontal where possible
    [ ] no chart-junk, no excess colors, nothing erasable without losing data
    [ ] caption describes every sub-part in order and explains every mark
    [ ] caption divulges all analysis steps and the origin of any error bars
    [ ] caption gives STM setup (V_sample, R_J or I), bias modulation, temperature, field
    [ ] copied figures or data are cited in the caption"""


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


# ---- what the manuscript does with each figure --------------------------------
def manuscript_includes():
    """{pdf name: ('col' | 'full', caption)} for every figure main.tex includes."""
    tex = re.sub(r'(?m)^\s*%.*$', '', open(MAIN_TEX).read())      # skip commented-out figures
    out = {}
    for m in re.finditer(r'\\includegraphics\[width=\\(\w+)\]\{([^}]+)\}', tex):
        starred = tex.rfind(r'\begin{figure*}', 0, m.start()) > tex.rfind(r'\begin{figure}', 0, m.start())
        full = m.group(1) == 'textwidth' or (starred and m.group(1) == 'linewidth')
        out[os.path.basename(m.group(2))] = ('full' if full else 'col', caption_after(tex, m.end()))
    return out


def caption_after(tex, pos):
    i = tex.find(r'\caption{', pos)
    if i < 0:
        return ''
    k = j = i + len(r'\caption{')
    depth = 1
    while depth and k < len(tex):
        depth += (tex[k] == '{') - (tex[k] == '}')
        k += 1
    return ' '.join(tex[j:k - 1].split())


# ---- reading the PDF with poppler ----------------------------------------------
def page_info(pdf):
    info = run('pdfinfo', pdf)
    w, h = map(float, re.search(r'Page size:\s+([\d.]+) x ([\d.]+)', info).groups())
    kw = re.search(r'Keywords:\s+(.*)', info)
    return w, h, kw.group(1) if kw else ''


def fonts(pdf):
    """[(name, type, embedded)] with the subset prefix removed."""
    out = []
    for row in run('pdffonts', pdf).splitlines()[2:]:
        m = re.match(r'(\S+)\s+(.*?)\s+\S+\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$', row)
        if m:
            out.append((m.group(1).split('+')[-1], m.group(2), m.group(3) == 'yes'))
    return out


def text_runs(pdf):
    """[(size in pt, string)]. pdftohtml reports integer sizes at zoom 3, so a
    size is known to within 1/3 pt: the true size lies in [size, size + 1/3)."""
    xml = run('pdftohtml', '-xml', '-i', '-stdout', '-zoom', '3', pdf)
    size = {m.group(1): int(m.group(2)) / 3 for m in re.finditer(r'<fontspec id="(\d+)" size="(\d+)"', xml)}
    runs = []
    for m in re.finditer(r'<text [^>]*font="(\d+)"[^>]*>(.*?)</text>', xml, re.S):
        s = html.unescape(re.sub(r'<[^>]+>', '', m.group(2))).strip()
        if s:
            runs.append((size[m.group(1)], s))
    return runs


def rasters(pdf):
    """[(height px, width px, ppi, interpolate flag)] for every embedded image."""
    out = []
    for row in run('pdfimages', '-list', pdf).splitlines()[2:]:
        c = row.split()
        if len(c) > 13 and c[2] == 'image':
            out.append((int(c[4]), int(c[3]), float(c[12]), c[9] == 'yes'))
    return out


# ---- red-green: which color pairs collapse for a deuteranope -------------------
DEUTAN = np.array([[0.367322, 0.860646, -0.227968],       # Machado et al. 2009, severity 1.0
                   [0.280085, 0.672501, 0.047413],
                   [-0.011820, 0.042940, 0.968881]])
TO_XYZ = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])


def linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lab(c):
    """sRGB in 0..1 -> CIELAB, so distances approximate perceived difference."""
    xyz = linear(c) @ TO_XYZ.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], 1)


def deutan(c):
    lin = np.clip(linear(c) @ DEUTAN.T, 0, 1)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)


def confusable_pairs(png, min_frac=0.002, clear=40.0, collapse=0.3):
    """Pairs of common, saturated colors that are clearly different to normal
    vision (Lab distance >= clear) but lose most of that difference under
    deuteranopia (distance falls below collapse x normal). Worst first."""
    px = np.asarray(Image.open(png).convert('RGB')).reshape(-1, 3)
    q, n = np.unique(px >> 4, axis=0, return_counts=True)            # 16 levels per channel
    keep = (n >= min_frac * len(px)) & (q.max(1).astype(int) - q.min(1) >= 4)
    c = (q[keep] * 16 + 8) / 255
    if len(c) < 2:
        return []
    def dist(x):
        return np.linalg.norm(x[:, None] - x[None], axis=2)
    d0, d1 = dist(lab(c)), dist(lab(deutan(c)))
    i, j = np.where(np.triu((d0 >= clear) & (d1 < collapse * d0), 1))
    order = np.argsort(d1[i, j] / d0[i, j])
    hexc = ['#%02x%02x%02x' % tuple(int(v * 255) for v in row) for row in c]
    return [(hexc[i[k]], hexc[j[k]]) for k in order]


# ---- the checks -----------------------------------------------------------------
def check(pdf, kind=None, caption=''):
    """Returns ([(status, check, message)], path of the print-size PNG)."""
    res = []
    w_pt, _, keywords = page_info(pdf)
    w_in = w_pt / 72
    if kind is None:                                   # not in the manuscript: nearest width
        kind = min(WIDTHS, key=lambda k: abs(WIDTHS[k] - w_in))
    scale = WIDTHS[kind] / w_in

    # 1. Built at the final width, so nothing is rescaled by LaTeX.
    ok = abs(scale - 1) <= 0.02
    res.append(('PASS' if ok else 'FAIL', 'width',
                f'{w_in:.3f} in, printed at {WIDTHS[kind]} in ({kind})'
                + ('' if ok else f': everything is rescaled to {scale:.0%}')))

    # 2. One font family, Arial, embedded as TrueType.
    fl = fonts(pdf)
    type3 = [n for n, t, _ in fl if 'Type 3' in t]
    other = sorted({n for n, _, _ in fl if 'arial' not in n.lower()})
    loose = [n for n, _, e in fl if not e]
    if not fl:
        res.append(('WARN', 'fonts', 'no live text (outlined or rasterized); cannot be checked or edited'))
    elif type3 or other or loose:
        why = [f'Type 3: {", ".join(type3)}'] * bool(type3) + [f'not Arial: {", ".join(other)}'] * bool(other) \
            + [f'not embedded: {", ".join(loose)}'] * bool(loose)
        res.append(('FAIL', 'fonts', '; '.join(why)))
    else:
        res.append(('PASS', 'fonts', 'Arial, embedded TrueType'))

    # 3. Nothing under 6 pt once printed.
    runs = text_runs(pdf)
    if type3:
        res.append(('----', 'font size', 'not measurable while fonts are Type 3 (readout is inflated); fix fonts first'))
    elif runs:
        final = [(s * scale, (s + 1 / 3) * scale, t) for s, t in runs]
        small = sorted({(round(lo, 1), t) for lo, hi, t in final if hi < MIN_PT - 0.05})
        words = [(p, t) for p, t in small if len(t) > 2]         # 1-2 characters: sub/superscripts
        edge = sorted({(round(lo, 1), t) for lo, hi, t in final if lo < MIN_PT - 0.05 <= hi})
        show = lambda items: ', '.join(f'{p:g} pt "{t[:18]}"' for p, t in items[:4]) + (' ...' if len(items) > 4 else '')
        lo_all = min(lo for lo, _, _ in final)
        if words:
            res.append(('FAIL', 'font size', f'below {MIN_PT} pt in print: {show(words)}'))
        elif small:
            res.append(('WARN', 'font size', f'sub/superscripts below {MIN_PT} pt in print: {show(small)}'))
        elif edge:
            res.append(('WARN', 'font size', f'within 1/3 pt of the {MIN_PT} pt limit: {show(edge)}'))
        else:
            res.append(('PASS', 'font size', f'smallest text {lo_all:.1f} pt in print'))

    # 4. Honest pixels: data images embedded at their native resolution.
    rs = rasters(pdf)
    big = [r for r in rs if min(r[0], r[1]) > 64]
    eg = lambda r: f'{r[0]}x{r[1]} px at {r[2] / scale:.0f} ppi in print'
    m = re.search(r'figstyle images=(\S*)', keywords)
    if any(r[3] for r in rs):
        res.append(('FAIL', 'pixels', 'an image asks the viewer to interpolate (/Interpolate true)'))
    elif m:
        want = Counter(tuple(map(int, s.split('x'))) for s in m.group(1).split(',') if s)
        have = Counter((r[0], r[1]) for r in rs)
        missing, extra = want - have, [r for r in big if (r[0], r[1]) not in want]
        if missing:
            res.append(('FAIL', 'pixels', 'data image not embedded at native size: '
                        + ', '.join(f'{h}x{w}' for h, w in missing)))
        elif extra:
            res.append(('WARN', 'pixels', f'{len(extra)} raster(s) not drawn with figstyle.image(), e.g. {eg(extra[0])}'))
        elif not want:
            res.append(('PASS', 'pixels', 'no data images'))
        else:
            res.append(('PASS', 'pixels', f'{sum(want.values())} data image(s), one PDF sample per data pixel'))
    elif big:
        res.append(('WARN', 'pixels', f'{len(big)} raster(s) of unknown origin (not built with figstyle), e.g. {eg(big[0])}'))
    else:
        res.append(('PASS', 'pixels', 'no data images'))

    # 5. Print-size render: the thing to look at, and the input to the color check.
    os.makedirs(LOOK_DIR, exist_ok=True)
    look = os.path.join(LOOK_DIR, os.path.basename(pdf)[:-4])
    run('pdftoppm', '-r', f'{300 * scale:.2f}', '-png', '-singlefile', pdf, look)
    look += '.png'
    pairs = confusable_pairs(look)
    res.append(('WARN', 'red-green', f'{len(pairs)} color pair(s) merge for red-green colorblind readers, '
                f'worst {pairs[0][0]} vs {pairs[0][1]}') if pairs else ('PASS', 'red-green', 'no confusable color pairs'))

    # 6. Caption hints for the items that are easiest to forget.
    if caption:
        has = lambda pat: 'yes' if re.search(pat, caption) else 'NO'
        setup = has(r'setpoint|Setpoint|R_J|pA|G\\Omega')
        temp = has(r'[0-9](~|\\,|\s)*K([^a-zA-Z]|$)')
        res.append(('note', 'caption', f'setup conditions: {setup}; temperature: {temp}'))
    return res, look


def report(pdf, kind, caption, eyes):
    res, look = check(pdf, kind, caption)
    print(f'\n{os.path.basename(pdf)}')
    for status, name, msg in res:
        print(f'  {status:4s}  {name:10s} {msg}')
    print(f'  look  {os.path.relpath(look)}  (print size, 300 dpi; view at 100%)')
    if eyes:
        print('  needs eyes:\n' + EYES)
        if caption:
            print('  caption: ' + caption)
    return res


def main(argv):
    includes = manuscript_includes() if os.path.exists(MAIN_TEX) else {}
    if '--paper' in argv:
        table = {name: report(os.path.join(os.path.dirname(MAIN_TEX), name), kind, cap, eyes=False)
                 for name, (kind, cap) in includes.items()}
        names = ['width', 'fonts', 'font size', 'pixels', 'red-green']
        print('\n' + ' ' * 36 + ''.join(f'{n:>11s}' for n in names))
        for name, res in table.items():
            got = {n: s for s, n, _ in res}
            print(f'{name[:35]:36s}' + ''.join(f'{got.get(n, ""):>11s}' for n in names))
        results = [r for res in table.values() for r in res]
    else:
        pdf = next(a for a in argv if a.endswith('.pdf'))
        kind, caption = includes.get(os.path.basename(pdf), (None, ''))
        if '--width' in argv:
            kind = argv[argv.index('--width') + 1]
        results = report(pdf, kind, caption, eyes=True)
    return int(any(s == 'FAIL' for s, _, _ in results))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
