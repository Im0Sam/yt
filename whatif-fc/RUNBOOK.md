# What If FC: daily run

Each scheduled run **posts the oldest `ready` episode** to YouTube Shorts and Instagram through Windsor.ai, and sends
the video to Samir to post on TikTok himself (one video per platform), then **builds the next episode** so it is `ready` for tomorrow. This one-day buffer means a failed
render never causes a missed post.

Read `series/BIBLE.md` and `series/log.json` first. Work from the repo root (`whatif-fc/`).

## 0. Setup (every run, fresh machine)
```bash
pip install --break-system-packages -q skia-python kokoro-onnx soundfile scipy pillow numpy
which ffmpeg
```
The voice model and font are in the repo (`models/`, `engine/fonts/`). Nothing else needs downloading.

## 1. Post
Account ids are in `series/log.json` → `accounts`. All posting goes through the **Windsor.ai for Social Media**
connector (ToolSearch `windsor`). Call `execute_action` with the connector, action and account given below.

1. **Finish partial episodes first.** For any episode with `status: "partial"`, retry only the platforms marked
   `PENDING` or `FAILED`, and never re-post a platform that already has an id.
2. Then post the oldest `status: "ready"` episode. Its video URL is
   `https://raw.githubusercontent.com/Im0Sam/yt/main/whatif-fc/videos/<slug>.mp4`, and `curl -sI` must return 200.
   Metadata comes from `episodes/<slug>/script.json` → `publish`.
   - **YouTube**: `connector "youtube"`, `action "upload_video"`, with params `video_url`, `title` (publish.title + " #Shorts", 100 characters or fewer),
     `description` (publish.description), `tags`, `category_id "1"`, `made_for_kids false`, `privacy_status "public"`.
     If you get "rate-limited", wait 75 s with Bash `sleep 75` and retry once. If it still fails, mark it `PENDING` and the next run retries.
     Before any retry, check the channel's video list with `get_data` (fields video, video_title, published_at), so you never upload twice.
   - **Instagram**: `connector "instagram"`, `action "create_video_post"`, with params `video_url`, `caption` (description +
     hashtags, 2200 characters or fewer) and `share_to_feed true`. Then `create_comment` with `media_id` and `message` = publish.pinned_comment.
   - **TikTok**: Windsor can't upload to TikTok. Don't try another route. Send Samir the video with SendUserFile
     (`videos/<slug>.mp4`) plus a ready-to-paste TikTok caption, so he can post it from his phone. Record `tiktok: "MANUAL"`.
3. Record the ids or URLs in `log.json` → `posts` with the date. Set `status` to `"posted"` once YouTube and Instagram both
   succeeded, otherwise `"partial"`.
4. **If Windsor is missing, unauthorised or out of trial/plan:** post nothing and tell Samir exactly what to reconnect or
   renew. Then continue to step 2 only if fewer than 2 episodes are `ready`.
5. Only post episode videos. Never delete or edit existing posts and never reply to comments, except the one pinned-comment
   post per episode described above.

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
