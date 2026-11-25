# What If FC: daily run

Each scheduled run **posts the oldest `ready` episode** to YouTube Shorts, TikTok and Instagram (one
video per platform), then **builds the next episode** so it is `ready` for tomorrow. This one-day buffer means a failed
render never causes a missed post.

Read `series/BIBLE.md` and `series/log.json` first. Work from the repo root (`whatif-fc/`).

## 0. Setup (every run, fresh machine)
```bash
pip install --break-system-packages -q skia-python kokoro-onnx soundfile scipy pillow numpy
which ffmpeg
```
The voice model and font are in the repo (`models/`, `engine/fonts/`). Nothing else needs downloading.

## 1. Post the oldest ready episode
1. In `series/log.json`, find the oldest episode with `status: "ready"`. Its file is `videos/<slug>.mp4`, and the
   public URL is `https://raw.githubusercontent.com/Im0Sam/yt/main/whatif-fc/videos/<slug>.mp4`.
   Check it with `curl -sI <url>`. It must return 200.
2. Load the **Windsor.ai for Social Media** connector tools (ToolSearch `+windsor`). Post the video with
   `episodes/<slug>/script.json` → `publish`:
   - **YouTube**: as a Short. Title = `publish.title` (60 characters or fewer). Description = `publish.description`. Tags = `publish.tags`.
     Visibility public. Category Film & Animation. Not made for kids.
   - **TikTok**: caption = `publish.title` + newline + the debate question + hashtags.
   - **Instagram**: a Reel, also shared to the feed. Caption = description + hashtags.
   - After it goes live, post `publish.pinned_comment` as a comment where the connector supports comments, and pin it on YouTube if possible.
3. Record each platform's post id or URL in `log.json` → `posts`, set `status: "posted"` and `posted: <date>`.
   If a platform fails, retry once. If it still fails, record `"<platform>": "FAILED: <reason>"` and leave the
   episode `ready` only if **all** platforms failed. Otherwise mark it posted and note the failure.
4. **If the Windsor connector is missing or not authorised:** don't post anything. Send Samir a push notification saying
   the Windsor.ai connection needs reconnecting, then continue to step 2 only if fewer than 2 episodes are `ready`.
5. Never post anything except the episode videos. Never delete or edit existing posts. Don't reply to comments.

## 2. Build the next episode
1. Pick the next unbuilt episode from the active arc's `outline`. If the arc is complete, mark it `"status": "done"`,
   write a **new arc** per the bible (premise, 5–7 episode outline, any new characters added to BIBLE.md),
   and build its first episode.
2. Write the brief for yourself: the hook type, frame 1, hook text (3–6 words), the beat sheet, a planted twist and the loop line.
   Then create `episodes/<slug>/`:
   - `script.json`: copy the shape of `episodes/ep001-el-viejo/script.json`. That means `duration` (28–40 s), `hook`,
     `lines` (narration `text`, on-screen `caption` in CAPS, `hl` highlight words, `anchor` seconds, optional `speed`
     between 0.9 and 1.25), `sound` (crowd/drone envelopes and timed events on every cut and impact) and `publish`.
   - `episode.py`: `SCENES = [(start, end, fn), ...]`. These must be contiguous, start at 0 and end at `duration`.
     Reuse helpers from `engine/shots.py` and `engine/lib.py` (puppet `figure`, `profile` close-ups, `Cam` + `pitch`,
     `goal_frame`, `stands`, `floodlight`, `rain`, `ball`, `glow`). **Write new scene functions for new moments.**
     Each episode must have at least 4 shots that aren't straight reuses of ep001's shots. Put episode-specific drawing code
     in `episode.py`, and put genuinely reusable helpers in `engine/shots.py`.
3. `python3 tools/vo.py episodes/<slug>`. Check the timing printout. Any line more than 0.4 s late or past the end means you
   should shorten the text, raise `speed`, or move `anchor`s and the scene timings to match.
4. **Look before rendering.** Run `python3 tools/preview.py episodes/<slug> <6–8 key times>` and Read `build/preview.jpg`.
   Check it is readable with the sound off, nothing is clipped, text sits above the bottom 20% (the UI zone), characters stay consistent,
   and nothing breaks the guardrails. Fix and preview again until it's good.
5. `python3 tools/build.py episodes/<slug>` takes about 10 minutes, so give the command a long timeout and run it in the background if needed. It writes
   `videos/<slug>.mp4`. Then check it: extract 6 frames with ffmpeg and look at them, and confirm the duration and that audio is present.
6. Add it to `log.json` → `episodes` with `status: "ready"`.

## 3. Housekeeping and commit
- Delete `videos/*.mp4` files whose episode was posted more than 14 days ago, so the repo doesn't grow forever.
- `build/` folders are git-ignored.
- `git add -A && git commit -m "What If FC: post <slug>, build <next-slug>" && git push`. Use the push options
  that the add_repo result gives.

## 4. Report
Send one short message: what was posted (with links), what was built for tomorrow, and anything that failed.
