"""Render every scene of an episode to build/sceneN.mp4 (2 workers), then concat to build/video.mp4.
Usage: python3 tools/render.py episodes/epXXX-slug [scene_index ...]"""
import sys, os, subprocess, pathlib
from multiprocessing import Pool
from _paths import ROOT


def ep_path(a):
    p = pathlib.Path(a)
    return p if p.is_absolute() else ROOT / p


def render_scene(args):
    ep_dir, i = args
    from core import Episode, surface, W, H, FPS
    ep = Episode(ep_dir)
    a, b, fn = ep.SCENES[i]
    f0, f1 = round(a * FPS), round(b * FPS)
    tmp = ep.build / f'scene{i}.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                          '-pix_fmt', 'yuv420p', str(tmp)], stdin=subprocess.PIPE)
    s = surface()
    for f in range(f0, f1):
        c = s.getCanvas()
        ep.draw(c, f / FPS, f)
        p.stdin.write(s.makeImageSnapshot().toarray().tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError(f'scene {i} failed')
    os.rename(tmp, ep.build / f'scene{i}.mp4')
    return i, f1 - f0


if __name__ == '__main__':
    ep_dir = ep_path(sys.argv[1])
    from core import Episode
    ep = Episode(ep_dir)
    idx = [int(x) for x in sys.argv[2:]] or list(range(len(ep.SCENES)))
    # contiguity check
    for (a, b, _), (c, d, _) in zip(ep.SCENES, ep.SCENES[1:]):
        assert abs(b - c) < 1e-6, f'scene gap/overlap at {b} vs {c}'
    assert abs(ep.SCENES[-1][1] - ep.duration) < 1e-6, 'last scene must end at script duration'
    with Pool(2) as pool:
        for i, n in pool.imap_unordered(render_scene, [(str(ep_dir), i) for i in idx]):
            print('scene', i, n, 'frames', flush=True)
    lst = ep.build / 'list.txt'
    lst.write_text(''.join(f"file 'scene{i}.mp4'\n" for i in range(len(ep.SCENES))))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy',
                    str(ep.build / 'video.mp4')], check=True)
    print('video.mp4 ok')
