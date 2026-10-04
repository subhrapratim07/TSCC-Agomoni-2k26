"""
Cleans text.png: removes the white/grey halo around the lettering,
smooths the edges, upscales 3x, and fills the letters with a
yellow -> orange -> red gradient. Output: text-clean.png

Usage (in the folder that has text.png):
    pip install pillow numpy
    python clean_text.py
"""
from PIL import Image, ImageFilter
import numpy as np

SRC, OUT, SCALE = "text.png", "text-clean.png", 3

im = Image.open(SRC).convert("RGBA")
im = im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS)
a = np.asarray(im).astype(float)
r, g, b, alpha = a[..., 0], a[..., 1], a[..., 2], a[..., 3] / 255.0

# "Redness": white/grey halo pixels have r ~ g ~ b, so they score ~0 and vanish.
redness = r - np.maximum(g, b)
mask = np.clip((redness - 18) / 45.0, 0, 1) * alpha

# Tighten the edge by ~1px (removes any leftover fringe), then soften.
m = Image.fromarray((mask * 255).astype("uint8"))
m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
mask = np.asarray(m).astype(float) / 255.0
mask = np.clip((mask - 0.12) / 0.76, 0, 1)  # crisp but anti-aliased

# Gradient fill: warm gold (top) -> orange (middle) -> vermilion (bottom)
h, w = mask.shape
t = np.linspace(0, 1, h)[:, None]
stops = [(0.00, (255, 214, 10)), (0.50, (255, 122, 0)), (1.00, (230, 25, 25))]
rgb = np.zeros((h, w, 3))
for c in range(3):
    rgb[..., c] = np.interp(t, [s[0] for s in stops], [s[1][c] for s in stops])

out = np.dstack([rgb, mask * 255]).astype("uint8")
img = Image.fromarray(out, "RGBA")
img = img.crop(img.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
canvas = Image.new("RGBA", (img.width + 40, img.height + 40), (0, 0, 0, 0))
canvas.paste(img, (20, 20))
canvas.save(OUT)
print(f"Saved {OUT} ({canvas.width}x{canvas.height})")