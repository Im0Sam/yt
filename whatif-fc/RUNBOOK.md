# Daily run (What If FC → Night Shift Rules)

Each scheduled run **posts one episode** to YouTube Shorts and TikTok through **Buffer**, and to Instagram Reels through
**Windsor.ai** (one video per platform), then **builds what tomorrow needs** so it is `ready` in advance. A failed render
therefore never causes a missed post.

Since 2026-11-28 the channel runs **Night Shift Rules**, an animated horror series where **viewers vote A or B in the
comments and the most votes decides the next episode** (Samir's request). Read `series/BIBLE.md` and `series/log.json`
first. Work from `whatif-fc/`.

## 0. Setup (every run, fresh machine)
```bash
pip install --break-system-packages -q skia-python kokoro-onnx soundfile scipy pillow numpy
which ffmpeg
```
The voice model and font are in the repo (`models/`, `engine/fonts/`). Nothing else needs downloading.

## 1. Count the votes (if the last posted episode has a `choice`)
Samir's rule: **count the votes on every platform, add them up, and the option with the most votes wins.**
Find the most recently posted episode in `log.json` → `episodes` that has `choice`. If it already has `vote.result`, skip.
1. Pull its comments from all three platforms with Windsor `get_data` (date range covering the post date, e.g. `last_7dT`):
   - YouTube: `connector "youtube"`, fields `comment_video_id, comment_id, comment_text, comment_author, comment_published_at`.
   - TikTok: `connector "tiktok_organic"`, fields `comment_video_id, comment_id, comment_text, comment_username, comment_parent_id`.
   - Instagram: `connector "instagram"`, fields `media_id, comment_id, comment_text, comment_username, comment_parent_id, comment_timestamp`.
2. Save the rows exactly as returned to a scratch file `{"youtube": [...], "tiktok": [...], "instagram": [...]}` and run
   `python3 tools/votes.py episodes/<slug> <that file> --write`. Do not count by hand. The script keeps only that
   episode's video ids, skips our pinned comment and replies, counts one vote per person per platform (their latest),
   reads "A"/"B" at the start of a comment or the option's words (`choice.keywords`), totals all platforms, and writes
   `vote {A, B, result, decided_by, per_platform}` to log.json. Most total votes wins; a tie goes to the option that won
   more platforms, then to `choice.tie_break`.
3. Look at the "not counted" lines it prints. If real votes were missed because people used other words, add those words
   to that episode's `choice.keywords` and run it again.
4. If a platform's comments can't be read (connector error), count the others and say so in the report.

## 2. Post
Account and channel ids are in `series/log.json` → `accounts`. Two connectors are used (find them with ToolSearch):
- **Buffer** (ToolSearch `buffer`): YouTube and TikTok uploads. Organization `accounts.buffer.organization`, channel ids in
  `accounts.buffer.channels`. Use `create_post` with `schedulingType "automatic"` and `mode "shareNow"`, then `get_post`
  to read `externalLink` (the live URL). TikTok may show `sending` for a minute or two: check again before recording.
- **Windsor.ai for Social Media** (ToolSearch `windsor`): Instagram posting and the pinned comment, plus all analytics reads.

1. **Finish partial episodes first.** For any episode with `status: "partial"`, retry only the platforms marked
   `PENDING` or `FAILED`, and never re-post a platform that already has an id.
2. **Choose today's episode.** The candidates are `status: "ready"` episodes. If some of them are branches
   (`branch_of` = the voted episode's slug, `branch` = "A" or "B"), post **the branch matching `vote.result`** and set the
   other branch to `status: "skipped"`. Otherwise post the oldest `ready` episode. Never post two episodes in one run.
3. **Check before posting, so nothing goes up twice.** Before each platform, check it doesn't already have this episode:
   Buffer `list_posts` (that channel, status sent/sending/scheduled) and Windsor `get_data` (YouTube: video, video_title,
   published_at; TikTok: video_id, video_caption, video_create_datetime; Instagram: media_id, media_caption). Samir sometimes
   posts TikTok by hand. If the episode is already there, record it and skip that platform.
4. Its video URL is `https://raw.githubusercontent.com/Im0Sam/yt/main/whatif-fc/videos/<slug>.mp4`; `curl -sI` must return
   200 with the same content-length as the local file. Metadata comes from `episodes/<slug>/script.json` → `publish`.
   - **YouTube (Buffer)**: channel `accounts.buffer.channels.youtube`, `text` = publish.description,
     `assets [{video:{url}}]`, `metadata.youtube {type "short", title: publish.title + " #Shorts" (100 characters or fewer),
     categoryId "1", madeForKids false, privacy "public", isAiGenerated false}`.
   - **TikTok (Buffer)**: channel `accounts.buffer.channels.tiktok`, `text` = a TikTok caption (description's first lines +
     the A/B question + "Fictional story, original characters." + publish.hashtags, 2200 characters or fewer),
     `assets [{video:{url}}]`, `metadata.tiktok {title: publish.title}`.
   - **Instagram (Windsor)**: `connector "instagram"`, `action "create_video_post"`, with params `video_url`, `caption`
     (description + hashtags, 2200 characters or fewer) and `share_to_feed true`. Then `create_comment` with `media_id` and
     `message` = publish.pinned_comment.
   - If Buffer fails for a platform, mark it `PENDING` (or, for TikTok only, send Samir the file with SendUserFile and a
     ready-to-paste caption, recording `tiktok: "MANUAL"`). Do not fall back to Windsor `upload_video` for YouTube: it was
     rate-limited 11 times in a row in Nov 2026.
5. Record the ids or URLs in `log.json` → `posts` with the date and `via`. Set `status` to `"posted"` once YouTube,
   TikTok and Instagram all succeeded, otherwise `"partial"`.
6. **If Buffer or Windsor is missing, disconnected or out of plan:** post nothing on the affected platforms and tell Samir
   exactly what to reconnect or renew. Buffer's free plan allows 3 channels and 10 scheduled posts; `shareNow` posts are fine.
7. Only post episode videos. Never delete or edit existing posts and never reply to comments, except the one pinned-comment
   post per episode on Instagram described above. Reading comments to count votes is fine.

## 2b. Analytics
Pull the latest stats for every episode posted in the last 14 days (fields listed in BIBLE.md → Retention rules 8) and
store them in `log.json` → `analytics.<slug>` with the date. Headline numbers for the horror lane: views, average watch,
3 s skip rate, **comments (votes) and shares per 1k views**, new followers. Apply BIBLE.md's rules to what you build next;
if new data contradicts a rule, update the rule.

## 3. Build what tomorrow needs
- **If the episode you just posted has a `choice`:** build **both branches** of the next episode: `<next>-a-<word>` for
  option A and `<next>-b-<word>` for option B, each with `branch_of: <posted slug>` and `branch: "A"/"B"` in log.json.
  Each branch opens on the consequence of its choice and has its own new rule, scare, clue and A/B choice.
  (Example: ns01 posted → build `ns02-a-...` and `ns02-b-...`; tomorrow the votes on ns01 pick one.)
- **Else, if another episode is already `ready`:** build nothing new (one is queued). You may polish it.
- **Else:** build the next episode of the active arc. If the arc is complete, mark it `"status": "done"`, write a new arc
  per the bible and build its first episode.

For each episode to build:
1. Write the brief for yourself: the rule, frame 1 (moving, loud), hook text (= the rule), recap line + badge
   ("EP n · YOU VOTED: A" when it follows a vote), beats, the jump scare, the clue, the A/B choice and the loop.
2. Create `episodes/<slug>/`:
   - `script.json`: copy the shape of `episodes/ns01-the-knock/script.json`: `duration` (30–38 s), `style`, `hook`,
     `lines` (narration `text`, on-screen `caption` in CAPS, `hl` highlight words, `anchor` seconds, optional `speed`
     0.9–1.35, and for the Visitor `voice "bm_lewis"`, `pitch -3`, `fx "whisper"`, `fill "#ff2b2b"`), `choice` (with
     `keywords` for A and B, e.g. A ["OPEN IT", "OPEN"], B ["DON'T OPEN", "DON'T"], and `tie_break`),
     `sound` (rain/buzz/drone envelopes and timed events on every cut and scare) and `publish`.
   - `episode.py`: `SCENES = [(start, end, fn), ...]`, contiguous from 0 to `duration`. Reuse `engine/horror.py` and
     `engine/lib.py`; **write new scene functions for new moments** (new rooms, Room 9, the ice machine, the parking lot,
     the stairwell...). At least 4 shots per episode that aren't straight reuses. Put reusable helpers in `engine/horror.py`.
3. `python3 tools/vo.py episodes/<slug>`. Any line more than 0.4 s late or past the end: shorten, raise `speed`, or move
   `anchor`s and scene timings.
4. **Look before rendering.** `python3 tools/preview.py episodes/<slug> <6–8 key times>` and Read `build/preview.jpg`.
   Check: readable with the sound off, nothing clipped, captions and cards above the bottom 20% (UI zone), the frame isn't
   so dark that nothing reads on a phone, the Visitor looks the same as before, nothing breaks the guardrails.
5. `python3 tools/build.py episodes/<slug>` takes about 10 minutes, so run it in the background (`nohup ... &`) and poll.
   It writes `videos/<slug>.mp4`. Then extract 6–8 frames with ffmpeg and look at them, and confirm duration and audio.
6. Add it to `log.json` → `episodes` with `status: "ready"` (plus `branch_of`/`branch` for branches) and append what
   happens on screen to the arc's `canon` once it is posted.

## 4. Housekeeping and commit
- Delete `videos/*.mp4` files whose episode was posted more than 14 days ago, and videos of `skipped` branches.
- `build/` folders are git-ignored.
- `git add -A && git commit -m "Daily run: post <slug>, build <slugs>" && git push`.

## 5. Report
Send one short message: what was posted (with links), the vote result that picked it (A n vs B n, per platform), the key analytics, what was built
for tomorrow, and anything that failed.
