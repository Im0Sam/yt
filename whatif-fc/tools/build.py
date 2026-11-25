"""Full build: narration -> render -> sound -> mux.
Outputs build/final.mp4 (high quality) and videos/<slug>.mp4 (compressed for upload, < ~20 MB).
Usage: python3 tools/build.py episodes/epXXX-slug [--skip-render]"""
import sys, subprocess, pathlib, json
from _paths import ROOT

p = pathlib.Path(sys.argv[1]); ep = p if p.is_absolute() else ROOT / p
T = str(ROOT / 'tools')
run = lambda *a: subprocess.run([sys.executable, *a], check=True)
run(f'{T}/vo.py', str(ep))
if '--skip-render' not in sys.argv:
    run(f'{T}/render.py', str(ep))
run(f'{T}/sound.py', str(ep))
b = ep / 'build'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(b / 'video.mp4'), '-i', str(b / 'sound.wav'),
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                '-movflags', '+faststart', str(b / 'final.mp4')], check=True)
out = ROOT / 'videos' / f'{ep.name}.mp4'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(b / 'final.mp4'), '-c:v', 'libx264', '-preset',
                'veryfast', '-crf', '24', '-maxrate', '5M', '-bufsize', '10M', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                '-b:a', '160k', '-movflags', '+faststart', str(out)], check=True)
print('final:', b / 'final.mp4')
print('upload copy:', out, round(out.stat().st_size / 1e6, 1), 'MB')
