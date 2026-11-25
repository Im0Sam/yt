"""Episode loader + frame compositor. An episode folder holds:
  script.json  - lines (VO + captions), hook, sound cues, publish metadata
  episode.py   - defines SCENES = [(start, end, fn), ...]; fn(c, t, f) -> flash
  build/       - generated: vo.wav, vo_times.json, scene*.mp4, sound.wav, final.mp4
"""
import json, math, sys, importlib.util, pathlib
import skia
from lib import W, H, FPS, text_block, caption, post, ease_out, clamp

ENGINE = pathlib.Path(__file__).parent


class Episode:
    def __init__(self, folder):
        self.dir = pathlib.Path(folder).resolve()
        self.build = self.dir / 'build'
        self.build.mkdir(exist_ok=True)
        self.script = json.loads((self.dir / 'script.json').read_text())
        self.duration = float(self.script['duration'])
        sys.path.insert(0, str(ENGINE))
        spec = importlib.util.spec_from_file_location('episode_' + self.dir.name.replace('-', '_'),
                                                      self.dir / 'episode.py')
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.SCENES = self.mod.SCENES
        self.cues = self._cues()
        h = self.script.get('hook', {})
        self.hook = (h.get('line1', ''), h.get('line2', ''), float(h.get('until', 3.0)), float(h.get('pulse_at', -1)))

    def _cues(self):
        lines = self.script['lines']
        vt_path = self.build / 'vo_times.json'
        times = json.loads(vt_path.read_text()) if vt_path.exists() else [[l['anchor'], l['anchor'] + 1.2] for l in lines]
        cues = []
        for i, l in enumerate(lines):
            st, en = times[i]
            nxt = times[i + 1][0] - 0.03 if i + 1 < len(lines) else self.duration
            end = min(nxt, en + 0.7) if i + 1 < len(lines) else self.duration
            cues.append((max(0.0, st - 0.03), end, l['caption'], set(l.get('hl', []))))
        return cues

    def draw(self, c, t, f):
        flash = 0.0
        for a, b, fn in self.SCENES:
            if a <= t < b:
                c.clear(skia.ColorBLACK)
                flash = fn(c, t, f) or 0.0
                break
        l1, l2, until, pulse_at = self.hook
        if t < until and (l1 or l2):
            k = t - pulse_at
            pulse = 1 + 0.10 * math.exp(-k * 8) if pulse_at >= 0 and k > 0 else 1.0
            al = clamp((until - t) / 0.15)
            if l1:
                text_block(c, l1, W / 2, 215, 190, scale=pulse, rot=-2, alpha=al)
            if l2:
                text_block(c, l2, W / 2, 400, 150, fill='#ffd400', scale=pulse, rot=-2, alpha=al)
        caption(c, t, self.cues)
        post(c, f, flash=flash)


def surface():
    return skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
