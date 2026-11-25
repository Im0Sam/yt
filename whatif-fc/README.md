# What If FC

Animated football "what if" Shorts, generated in code: skia drawing, Kokoro narration and procedural sound.
A daily scheduled run follows [RUNBOOK.md](RUNBOOK.md): it posts the oldest ready episode and builds the next one.

- `series/`: the bible (cast, style, guardrails) and log.json (arcs, episodes, post links)
- `engine/`: drawing library (`lib.py`), reusable shots (`shots.py`) and the compositor (`core.py`)
- `episodes/<slug>/`: `script.json` (narration, captions, sound, publish metadata) and `episode.py` (scenes)
- `tools/`: `vo.py`, `preview.py`, `render.py`, `sound.py`, `build.py`
- `videos/`: upload copies (pruned 14 days after posting)
- `models/`: Kokoro v1.0 int8 voice model (Apache-2.0)
