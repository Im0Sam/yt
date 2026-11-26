# What If FC: daily run

Each scheduled run **posts the oldest `ready` episode** to YouTube Shorts and TikTok through **Buffer**, and to Instagram
Reels through **Windsor.ai** (one video per platform), then **builds the next episode** so it is `ready` for tomorrow.
This one-day buffer means a failed render never causes a missed post.

Read `series/BIBLE.md` and `series/log.json` first. Work from the repo root (`whatif-fc/`).

## 0. Setup (every run, fresh machine)
```bash
pip install --break-system-packages -q skia-python kokoro-onnx soundfile scipy pillow numpy
which ffmpeg
```
The voice model and font are in the repo (`models/`, `engine/fonts/`). Nothing else needs downloading.

## 1. Post
Account and channel ids are in `series/log.json` → `accounts`. Two connectors are used (find them with ToolSearch):
- **Buffer** (ToolSearch `buffer`): YouTube and TikTok uploads. Organization `accounts.buffer.organization`, channel ids in
  `accounts.buffer.channels`. Use `create_post` with `schedulingType "automatic"` and `mode "shareNow"`, then `get_post`
  to read `externalLink` (the live URL).
- **Windsor.ai for Social Media** (ToolSearch `windsor`): Instagram posting and the pinned comment, plus all analytics reads.

1. **Finish partial episodes first.** For any episode with `status: "partial"`, retry only the platforms marked
   `PENDING` or `FAILED`, and never re-post a platform that already has an id.
2. **Check before posting, so nothing goes up twice.** Before each platform, check it doesn't already have this episode:
   Buffer `list_posts` (that channel, status sent/sending/scheduled) and Windsor `get_data` (YouTube: video, video_title,
   published_at; TikTok: video_id, video_caption, video_create_datetime; Instagram: media_id, media_caption). Samir sometimes
   posts TikTok by hand. If the episode is already there, record it and skip that platform.
3. Then post the oldest `status: "ready"` episode. Its video URL is
   `https://raw.githubusercontent.com/Im0Sam/yt/main/whatif-fc/videos/<slug>.mp4`, and `curl -sI` must return 200 with the
   same content-length as the local file. Metadata comes from `episodes/<slug>/script.json` → `publish`.
   - **YouTube (Buffer)**: channel `accounts.buffer.channels.youtube`, `text` = publish.description,
     `assets [{video:{url}}]`, `metadata.youtube {type "short", title: publish.title + " #Shorts" (100 characters or fewer),
     categoryId "1", madeForKids false, privacy "public", isAiGenerated false}`.
   - **TikTok (Buffer)**: channel `accounts.buffer.channels.tiktok`, `text` = a TikTok caption (description's first lines +
     the debate question + "Fictional story, original characters." + publish.hashtags, 2200 characters or fewer),
     `assets [{video:{url}}]`, `metadata.tiktok {title: publish.title}`.
   - **Instagram (Windsor)**: `connector "instagram"`, `action "create_video_post"`, with params `video_url`, `caption`
     (description + hashtags, 2200 characters or fewer) and `share_to_feed true`. Then `create_comment` with `media_id` and
     `message` = publish.pinned_comment.
   - If Buffer fails for a platform, mark it `PENDING` (or, for TikTok only, send Samir the file with SendUserFile and a
     ready-to-paste caption, recording `tiktok: "MANUAL"`). Do not fall back to Windsor `upload_video` for YouTube: it was
     rate-limited 11 times in a row in Nov 2026.
4. Record the ids or URLs in `log.json` → `posts` with the date and `via`. Set `status` to `"posted"` once YouTube,
   TikTok and Instagram all succeeded, otherwise `"partial"`.
5. **If Buffer or Windsor is missing, disconnected or out of plan:** post nothing on the affected platforms and tell Samir
   exactly what to reconnect or renew. Buffer's free plan allows 3 channels and 10 scheduled posts; `shareNow` posts are fine.
6. Only post episode videos. Never delete or edit existing posts and never reply to comments, except the one pinned-comment
   post per episode on Instagram described above.

## 1b. Analytics
Pull the latest stats for every posted episode (fields listed in BIBLE.md → Retention rules) and store them in
`log.json` → `analytics.<slug>` with the date. Apply BIBLE.md's retention rules to the episode you build next; if new
data contradicts a rule, update the rule.

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
