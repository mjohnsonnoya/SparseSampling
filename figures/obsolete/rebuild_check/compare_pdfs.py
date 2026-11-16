"""Compare a rebuilt PDF against the Illustrator original.
1. Embedded rasters: decode every image XObject in both files, match by placement
   bbox, and test byte equality of RGB and alpha.
2. Page raster: both PDFs rendered at 300 dpi by MuPDF, per-pixel difference.
Runs in the scratch venv that has PyMuPDF."""
import sys
import numpy as np
import fitz

orig, new = sys.argv[1], sys.argv[2]

def images(pdf):
    doc = fitz.open(pdf); page = doc[0]; out = []
    for info in page.get_image_info(xrefs=True):
        xref = info['xref']; pix = fitz.Pixmap(doc, xref)
        if pix.colorspace is None or pix.colorspace.n != 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        rgb = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[..., :3]
        meta = doc.extract_image(xref)
        if meta.get('smask', 0):
            sm = fitz.Pixmap(doc, meta['smask'])
            alpha = np.frombuffer(sm.samples, dtype=np.uint8).reshape(sm.h, sm.w, sm.n)[..., 0]
        else:
            alpha = np.full(rgb.shape[:2], 255, np.uint8)
        out.append((np.array(info['bbox']), rgb.copy(), alpha.copy()))
    return out, page.rect

A, ra = images(orig); B, rb = images(new)
print(f'page size  orig {tuple(round(v,3) for v in ra)}  new {tuple(round(v,3) for v in rb)}')
print(f'embedded images: orig {len(A)}  new {len(B)}')
n_same = 0
for bbox, rgb, alpha in A:
    # nearest placement in the rebuilt file
    j = int(np.argmin([np.abs(b[0] - bbox).sum() for b in B]))
    bb, rgb2, alpha2 = B[j]
    same_shape = rgb.shape == rgb2.shape
    same_rgb = same_shape and np.array_equal(rgb, rgb2)
    same_a = same_shape and np.array_equal(alpha, alpha2)
    maxd = int(np.abs(rgb.astype(int) - rgb2.astype(int)).max()) if same_shape else -1
    n_same += same_rgb and same_a
    print(f'  bbox {np.round(bbox,2).tolist()}  {rgb.shape[1]}x{rgb.shape[0]}  placement off by {np.abs(bb-bbox).max():.3f} pt  '
          f'RGB identical: {same_rgb}  alpha identical: {same_a}  max |dRGB| = {maxd}')
print(f'identical rasters: {n_same} of {len(A)}')

# text spans: match by string and nearest origin, report placement error in points
def spans(pdf):
    out = []
    for b in fitz.open(pdf)[0].get_text('dict')['blocks']:
        if b['type'] != 0: continue
        for l in b['lines']:
            for s in l['spans']:
                if s['text'].strip(): out.append((s['text'], np.array(s['origin']), s['size'], s['font']))
    return out
SA, SB = spans(orig), spans(new)
worst = 0.0; nmatch = 0
for txt, o, sz, font in SA:
    cands = [(np.linalg.norm(o - o2), o2, sz2, f2) for t2, o2, sz2, f2 in SB if t2 == txt]
    if not cands: print(f'  text {txt!r} missing in rebuilt'); continue
    dist, o2, sz2, f2 = min(cands, key=lambda c: c[0]); nmatch += 1; worst = max(worst, dist)
    if dist > 0.3 or abs(sz - sz2) > 0.01 or font.split('+')[-1] != f2.split('+')[-1]:
        print(f'  {txt!r:32s} origin off {dist:.2f} pt  size {sz:.2f}->{sz2:.2f}  font {font} -> {f2}')
print(f'text spans matched {nmatch} of {len(SA)}; worst origin offset {worst:.3f} pt; fonts: ' + ', '.join(sorted({f.split("+")[-1] for *_, f in SB})))

# page-level diff at 300 dpi
def render(pdf):
    pix = fitz.open(pdf)[0].get_pixmap(dpi=300, alpha=False)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3).astype(int)
ia, ib = render(orig), render(new)
h = min(ia.shape[0], ib.shape[0]); w = min(ia.shape[1], ib.shape[1])
ia, ib = ia[:h, :w], ib[:h, :w]
d = np.abs(ia - ib).max(axis=2)
print(f'300 dpi page diff: {w}x{h} px, pixels differing by >0: {(d>0).mean()*100:.3f}%, by >16: {(d>16).mean()*100:.3f}%, by >64: {(d>64).mean()*100:.3f}%')
# where does the residual live? inside image bboxes vs everywhere else
sc = 300 / 72
inside = np.zeros(d.shape, bool)
for bbox, _, _ in A:
    x0, y0, x1, y1 = (bbox * sc).round().astype(int)
    inside[y0:y1, x0:x1] = True
for lab, m in [('inside image areas', inside), ('outside image areas', ~inside)]:
    dd = d[m]
    print(f'  {lab:20s}: {m.mean()*100:5.1f}% of page; differing >0: {(dd>0).mean()*100:6.2f}%  >2: {(dd>2).mean()*100:6.2f}%  >16: {(dd>16).mean()*100:6.2f}%  max {dd.max()}')
doc = fitz.open(orig); x0 = A[0][0]
page = doc[0]
for info in page.get_image_info(xrefs=True)[:2]:
    print('  orig image colorspace:', doc.xref_get_key(info['xref'], 'ColorSpace'))
print('  orig page OutputIntents:', doc.xref_get_key(doc.pdf_catalog(), 'OutputIntents'))
# save a diff image: differences in red over a faded copy of the original
vis = (255 - (255 - ia) * 0.25).astype(np.uint8)
mask = d > 16
vis[mask] = [255, 0, 0]
import struct, zlib
def png(path, arr):
    h, w, _ = arr.shape
    raw = b''.join(b'\x00' + arr[i].tobytes() for i in range(h))
    def chunk(t, b): return struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t + b) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))
png(new[:-4] + '_diff.png', vis)
print('diff image', new[:-4] + '_diff.png')
