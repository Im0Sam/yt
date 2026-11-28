"""Narration: script.json lines -> build/vo.wav (48k mono) + build/vo_times.json.
Each line starts at its 'anchor' (seconds) or right after the previous line, whichever is later.
Usage: python3 tools/vo.py episodes/epXXX-slug"""
import json, sys, numpy as np, soundfile as sf
from scipy.signal import resample_poly
from _paths import ROOT, MODELS
from kokoro_onnx import Kokoro

ep = ROOT / sys.argv[1] if not sys.argv[1].startswith('/') else __import__('pathlib').Path(sys.argv[1])
script = json.loads((ep / 'script.json').read_text())
build = ep / 'build'; build.mkdir(exist_ok=True)
k = Kokoro(str(MODELS / 'kokoro-v1.0.int8.onnx'), str(MODELS / 'voices-v1.0.bin'))
voice = script.get('voice', 'am_michael')
SR = 48000
N = int(float(script['duration']) * SR)
vo = np.zeros(N)
times, prev = [], -1.0
for i, l in enumerate(script['lines']):
    a, sr = k.create(l['text'], voice=l.get('voice', voice), speed=float(l.get('speed', 1.05)), lang='en-us')
    a = np.asarray(a, dtype=np.float64)
    idx = np.where(np.abs(a) > 0.01)[0]
    a = a[max(0, idx[0] - 200): idx[-1] + 1200]
    # optional 'pitch' in semitones (negative = deeper, also slower) for character voices
    up = SR
    if l.get('pitch'):
        up = int(round(SR * 2 ** (-float(l['pitch']) / 12)))
    a = resample_poly(a, up, sr)
    if l.get('fx') == 'whisper':  # breathy double + slight tremolo
        tt = np.arange(len(a)) / SR
        a = a * (1 + 0.25 * np.sin(2 * np.pi * 6 * tt)) + 0.35 * np.roll(a, int(0.023 * SR))
    st = max(float(l['anchor']), prev + 0.08)
    j = int(st * SR)
    n = min(len(a), N - j)
    if n > 0:
        vo[j:j + n] += a[:n]
    en = st + len(a) / SR
    times.append([round(st, 2), round(en, 2)])
    prev = en
    late = st - float(l['anchor'])
    print(f"{i:2d} {st:6.2f}-{en:6.2f}  late {late:+.2f}s  {l['text']}")
d1, d2 = int(0.037 * SR), int(0.071 * SR)
wet = np.zeros_like(vo); wet[d1:] += vo[:-d1] * 0.18; wet[d2:] += vo[:-d2] * 0.1
vo = np.tanh((vo + wet) * 1.6) / np.tanh(1.6)
vo *= 0.9 / max(1e-6, np.abs(vo).max())
sf.write(build / 'vo.wav', vo.astype(np.float32), SR)
(build / 'vo_times.json').write_text(json.dumps(times))
if prev > float(script['duration']):
    print(f"WARNING: narration ends at {prev:.2f}s, after the {script['duration']}s video")
