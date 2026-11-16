"""Pull the embedded raster (RGB + alpha) out of each single-panel PDF that
regen_arrays.py wrote, and save them as one npz for the figure builder.
Runs in the scratch venv that has PyMuPDF."""
import os, sys, glob
import numpy as np
import fitz

OUT = os.path.dirname(os.path.abspath(__file__))
PAN = os.path.join(OUT, 'panels')

def rasters_of(pdf):
    doc = fitz.open(pdf); page = doc[0]
    out = []
    for info in page.get_image_info(xrefs=True):
        xref = info['xref']
        pix = fitz.Pixmap(doc, xref)
        if pix.n - pix.alpha >= 3:
            pix = fitz.Pixmap(fitz.csRGB, pix) if pix.colorspace and pix.colorspace.n != 3 else pix
        rgb = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[..., :3]
        if pix.n == 1 or (pix.n - pix.alpha) == 1:
            rgb = np.repeat(rgb[..., :1], 3, axis=2)
        meta = doc.extract_image(xref)
        if meta.get('smask', 0):
            sm = fitz.Pixmap(doc, meta['smask'])
            alpha = np.frombuffer(sm.samples, dtype=np.uint8).reshape(sm.h, sm.w, sm.n)[..., 0]
        else:
            alpha = np.full(rgb.shape[:2], 255, np.uint8)
        out.append(np.dstack([rgb, alpha]))
    return out

store = {}
for pdf in sorted(glob.glob(os.path.join(PAN, '*.pdf'))):
    name = os.path.basename(pdf)[:-4]
    ims = rasters_of(pdf)
    assert len(ims) == 1, (name, len(ims))
    store[name] = ims[0]
    print(f'{name:18s} {ims[0].shape}  alpha<255 pixels: {(ims[0][...,3] < 255).sum()}')
np.savez(os.path.join(OUT, 'panel_rasters.npz'), **store)
print('saved', os.path.join(OUT, 'panel_rasters.npz'))
