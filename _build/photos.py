"""Grade stock photos to one warm, low-saturation look and export webp crops.
Run: python3 _build/photos.py  (sources: assets/photo/*-src.jpg)"""
from PIL import Image, ImageEnhance, ImageOps
from pathlib import Path
D = Path(__file__).resolve().parent.parent / 'assets' / 'photo'
INK = (31, 26, 22); PAPER = (245, 238, 226)

def grade(im):
    im = im.convert('RGB')
    im = ImageEnhance.Color(im).enhance(0.42)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    g = ImageOps.grayscale(im)
    tone = ImageOps.colorize(g, INK, PAPER, mid=(150, 128, 106))
    im = Image.blend(im, tone, 0.38)
    return im

# name: (target aspect w/h, focus x 0..1, focus y 0..1, widths)
JOBS = {
    'hero':      [(16/9, .5, .55, (2400, 1440)), (4/5, .42, .55, (1080,))],
    'loop':      [(4/5, .5, .45, (1200, 700))],
    'warehouse': [(3/2, .5, .5, (2000, 1000, 700))],
    'thread':    [(4/5, .5, .5, (1200, 700))],
    'charcoal':  [(4/5, .5, .5, (1200, 700))],
    'sacks':     [(4/5, .5, .6, (1200, 700))],
}
for name, crops in JOBS.items():
    src = Image.open(D.parent.parent / '_src' / 'photo-src' / f'{name}-src.jpg')
    src = grade(src)
    W, H = src.size
    for ar, fx, fy, widths in crops:
        if W / H > ar: cw, ch = int(H * ar), H
        else: cw, ch = W, int(W / ar)
        x = min(max(int(W * fx - cw / 2), 0), W - cw); y = min(max(int(H * fy - ch / 2), 0), H - ch)
        c = src.crop((x, y, x + cw, y + ch))
        tag = 'm' if ar < 1 and name == 'hero' else ''
        for w in widths:
            out = c.resize((w, round(w / ar)), Image.LANCZOS)
            fn = D / f'{name}{"-" + tag if tag else ""}-{w}.webp'
            out.save(fn, 'WEBP', quality=78, method=6)
            print(fn.name, out.size, fn.stat().st_size // 1024, 'KB')
