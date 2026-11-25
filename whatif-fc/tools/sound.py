"""Procedural sound bed from script.json['sound'] + ducked narration -> build/sound.wav (48k stereo).
Event types: hit, thump, whoosh, whistle, splash, footsteps, heartbeat (see ep001 script.json).
Usage: python3 tools/sound.py episodes/epXXX-slug"""
import json, sys, pathlib
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
from scipy.ndimage import uniform_filter1d
from _paths import ROOT

p = pathlib.Path(sys.argv[1]); ep = p if p.is_absolute() else ROOT / p
script = json.loads((ep / 'script.json').read_text())
snd = script.get('sound', {})
SR = 48000
DUR = float(script['duration'])
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(script.get('seed', 5))


def bp(x, lo, hi, order=4):
    return sosfilt(butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)


def lp(x, hi, order=4):
    return sosfilt(butter(order, hi, 'lowpass', fs=SR, output='sos'), x)


def env(points, default=0.0):
    if not points:
        return np.full(N, default)
    ts, vs = zip(*points)
    return np.interp(t, ts, vs)


L = np.zeros(N); R = np.zeros(N)


def add(sig, start=0.0, gain=1.0, pan=0.0):
    i = int(start * SR)
    n = min(len(sig), N - i)
    if n <= 0 or i < 0:
        return
    L[i:i + n] += sig[:n] * gain * (1 - max(0, pan))
    R[i:i + n] += sig[:n] * gain * (1 + min(0, pan))


def hit(dur=1.6, f0=58, click=0.6):
    tt = np.arange(int(dur * SR)) / SR
    freq = f0 * (1 + 1.5 * np.exp(-tt * 18))
    s = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-tt * 3.2)
    return (s + lp(rng.standard_normal(len(tt)), 2500) * np.exp(-tt * 40) * click) * 0.9


def whoosh(dur=0.8, lo=300, hi=3000, rev=False):
    n = int(dur * SR); x = rng.standard_normal(n); out = np.zeros(n)
    for k in range(16):
        a, b = k * n // 16, (k + 1) * n // 16
        f = lo + (hi - lo) * (k / 16)
        out[a:b] = bp(x, max(20, f * 0.7), min(f * 1.4, 20000), 2)[a:b]
    s = out * np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return s[::-1] if rev else s


def thump(dur=0.35, f=95):
    tt = np.arange(int(dur * SR)) / SR
    return (np.sin(2 * np.pi * f * tt * (1 + np.exp(-tt * 30))) * np.exp(-tt * 14)
            + lp(rng.standard_normal(len(tt)), 900) * np.exp(-tt * 35) * 0.8)


def whistle(dur=0.7):
    tt = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * 2900 * tt + 3 * np.sin(2 * np.pi * 32 * tt)) * (1 + 0.35 * np.sin(2 * np.pi * 32 * tt))
    return s * np.minimum(1, tt * 30) * np.minimum(1, (dur - tt) * 12) * 0.18


def splash(dur=0.5):
    n = int(dur * SR)
    return bp(rng.standard_normal(n), 300, 3000) * np.exp(-np.arange(n) / SR * 8) * 0.5


# rain bed
for ch in (L, R):
    ch += bp(rng.standard_normal(N), 600, 9000) * 0.05 * snd.get('rain', 1.0)
    ch += bp(rng.standard_normal(N), 150, 600) * 0.025 * snd.get('rain', 1.0)
# crowd
crowd = bp(rng.standard_normal(N), 250, 1800) + 0.5 * bp(rng.standard_normal(N), 120, 400)
crowd /= np.abs(crowd).max()
ce = env(snd.get('crowd'), 0.1)
mod = 1 + 0.25 * np.sin(2 * np.pi * 3.1 * t) * (ce > 0.3)
add(crowd * ce * mod * 0.5, 0, 1.0, -0.1)
add(np.roll(crowd, 7000) * ce * 0.5, 0, 1.0, 0.1)
# events
for e in snd.get('events', []):
    ty, st, g, pan = e['type'], float(e['t']), float(e.get('gain', 0.5)), float(e.get('pan', 0))
    if ty == 'hit':
        add(hit(e.get('dur', 1.6), e.get('f', 55), e.get('click', 0.5)), st, g, pan)
    elif ty == 'thump':
        add(thump(e.get('dur', 0.35), e.get('f', 95)), st, g, pan)
    elif ty == 'whoosh':
        add(whoosh(e.get('dur', 0.8), e.get('lo', 300), e.get('hi', 3000), e.get('rev', False)), st, g, pan)
    elif ty == 'whistle':
        add(whistle(e.get('dur', 0.7)), st, g, pan)
    elif ty == 'splash':
        add(splash(e.get('dur', 0.5)), st, g, pan)
    elif ty == 'footsteps':
        for k in range(int(e.get('n', 10))):
            add(thump(0.12, 160) * 0.5, st + k * e.get('step', 0.14), g, 0.2 * (-1) ** k)
    elif ty == 'heartbeat':
        tb, per = st, float(e.get('period', 0.9))
        while tb < float(e['until']):
            add(thump(0.25, 55), tb, g); add(thump(0.22, 50), tb + 0.18, g * 0.73)
            tb += per; per = max(0.55, per * 0.94)
    else:
        print('unknown sound event', ty)
# drone
de = env(snd.get('drone'), 0.0)
f = env(snd.get('drone_hz'), 55.0)
ph = 2 * np.pi * np.cumsum(f) / SR
drone = lp(np.sin(ph) + 0.5 * np.sin(ph * 1.5) + 0.35 * np.sin(ph * 2.01) + 0.2 * np.sin(ph * 3), 900)
add(drone * de, 0, 0.6)
# narration + ducking
vo_path = ep / 'build' / 'vo.wav'
if vo_path.exists():
    vo, _ = sf.read(vo_path)
    vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
    pres = np.clip(uniform_filter1d((np.abs(vo) > 0.02).astype(float), int(0.25 * SR)) * 4, 0, 1)
    duck = 1 - 0.55 * uniform_filter1d(pres, int(0.15 * SR))
    L *= duck; R *= duck
    L += vo * 0.62; R += vo * 0.62
mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
mix *= 0.89 / np.abs(mix).max()
fd = int(0.01 * SR)
mix[:fd] *= np.linspace(0, 1, fd)[:, None]; mix[-fd:] *= np.linspace(1, 0, fd)[:, None]
sf.write(ep / 'build' / 'sound.wav', (mix * 32767).astype(np.int16), SR, subtype='PCM_16')
print('sound.wav ok')
