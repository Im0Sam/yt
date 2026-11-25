"""Contact sheet of frames at given times -> build/preview.jpg (look at it before rendering).
Usage: python3 tools/preview.py episodes/epXXX-slug 0.5 4 9.2 ..."""
import sys, pathlib
from PIL import Image
from _paths import ROOT
from core import Episode, surface, W, H

p = pathlib.Path(sys.argv[1]); ep = Episode(p if p.is_absolute() else ROOT / p)
times = [float(x) for x in sys.argv[2:]]
s = surface(); ims = []
for t in times:
    ep.draw(s.getCanvas(), t, int(t * 30))
    ims.append(Image.fromarray(s.makeImageSnapshot().toarray()[:, :, :3]).resize((W // 3, H // 3)))
cols = min(4, len(ims)); rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * W // 3, rows * H // 3))
for i, im in enumerate(ims):
    sheet.paste(im, ((i % cols) * W // 3, (i // cols) * H // 3))
out = ep.build / 'preview.jpg'; sheet.save(out, quality=88); print(out)
