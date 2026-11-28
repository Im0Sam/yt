# Series bible

**Current lane (from 2026-11-29): animated horror, "Night Shift Rules".** Samir switched the channel from football to
horror on 2026-11-28: scary, haunted, jump scares, and **every episode ends on a choice the viewers vote on in the
comments (A or B); the most votes decides the next episode.** No football in this lane.
El Viejo (football, arc01) ended with ep004 "The Offer"; its notes are archived at the bottom.

**Format:** YouTube Shorts / TikTok / Instagram Reels, 9:16 1080×1920, 30 fps, 30–38 s, narrated, captions burned in.
**Look (horror):** stylised 2D drawn in code (skia + `engine/horror.py`): near-black frames lit by a flashlight circle
(`darkness`, `dust`), flickering fluorescent corridors (`corridor`, `flicker`), CCTV footage (`cctv`), RGB-split glitch on
every scare (`glitch`), peephole lens (`peephole_mask`), the Visitor (`visitor`, `scare_face`), neon (`neon_text`),
handwritten notes (`note`). Bebas Neue captions: white with one **red** highlight word (`style.hl_col "#ff2b2b"`); lines
spoken by the Visitor are captioned in red with quotes (`fill`). Series badge top-left for the first ~3 s
(`style.badge "NIGHT SHIFT RULES · EP n"`).
**Voices:** narrator Kokoro `am_michael`, second person ("you"), short sentences. The Visitor: `bm_lewis`, `pitch -3`
to `-4`, `fx "whisper"`. Sound: `buzz` hum bed, `knock`, `creak`, `static`, `riser`, `sting` on every jump scare,
low dissonant `drone_hz` (~41–46 Hz). No crowd (`crowd [[0, 0]]`).

## Night Shift Rules: world and cast
- **You (POV, never shown clearly):** the new night-shift clerk at the Wren Motel. Seen only as a flashlight beam, hands,
  or a small silhouette in the office window (`kit='guard'`: navy shirt).
- **The Wren Motel:** a fictional roadside motel, 12 rooms, red neon "WREN MOTEL" sign with a flickering green
  "VACANCY", one long carpeted hallway (red carpet, sickly olive wallpaper, red EXIT sign at the far end), the front office
  with a heavy wooden door, peephole, lever handle, chain.
- **Mr. Hale:** the manager: short, a little stooped, round glasses, bushy grey eyebrows, kind tired face, the same brown
  cardigan, white shirt, grey trousers, **a key ring on his belt**. Normal human proportions (the Visitor's are wrong). He wrote the rules note. Rarely seen; maybe never truly.
- **Character art lives in `engine/characters.py`** (hand-drawn bezier designs, not the old stick puppets):
  `visitor(c, x, y, h, t, view='back'|'front', arm, head_turn, light, rim_a)` with h ≈ `cam.s(Z, 2.25)`;
  `hale(c, x, y, h, t, view)` with h ≈ `cam.s(Z, 1.7)`; `pov_hand(...)` for your flashlight hand. Always use these for
  full-body shots; `horror.scare_face` for face close-ups. Check `/tmp` character sheets against these before rendering.
- **The Visitor:** wears Hale's shape: grey hair, brown cardigan, but too tall and too thin (`visitor(..., stretch 1.18,
  thin 0.82)`). From behind it looks like Hale. Its face (`scare_face`): long and grey-pale, uneven hollow eyes with
  pinpoint pupils, a thin grin that runs past the cheeks. It imitates voices.
- **The Rules note** (`RULES` in ns01's episode.py): 1. Never open the office door after 3 a.m. 2. Room 9 is empty; if its
  light is on, don't look. 3. If someone says your name, don't answer. Signed "- HALE". **P.S. I always have my key.**
  Later episodes can reveal more rules (a torn-off bottom half of the note, rules scratched into a wall, etc).
- New characters get a one-line visual description here.

## Episode formula (horror + vote)
1. **0–0.5 s:** a moving, loud first frame: an impact, a knock, a light bursting, a glitch, with `sting` or `knock`.
2. **Hook text = the rule** ("RULE 2:" / "DON'T LOOK.") and the first VO line says the same rule.
3. **1–3 s:** a hard cut to a second reveal (the rule being broken, or the thing behind the door).
4. **Recap in one line for new viewers** inside the first 6 s ("Last night, you chose not to open the door.") plus the
   badge "EP n · YOU VOTED: B". This rewards voters and tells cold viewers what's going on.
5. 3–5 escalating beats, cut every ≤2 s until 8 s. At least 4 brand-new shots per episode.
6. **One jump scare** around 60–70% of the runtime (face, figure in the frame, light bursting) with `sting` + glitch +
   white flash, and a fake-out calm moment just before it.
7. **A planted clue** (a rule, a door number, a sound) that helps viewers choose. Pinned comment points at it.
8. **The vote card** for the last ~8 s: the question in white, two option cards "A | ..." (red) and "B | ..." (dark),
   "COMMENT A OR B · YOU DECIDE EP n+1". VO: "Comment A or B. The most votes decides episode n+1." Then a rewatch prompt
   tied to the clue, and a loop into frame 1. **Both options must be genuinely tempting**, and neither is "obviously right".
9. `script.json` → `choice {question, A, B}` must be filled; publish `pinned_comment` repeats the A/B options.
10. Description: hook sentence, "Night Shift Rules, Episode n. YOU decide what happens next.", the guardrail line,
   the A/B question, hashtags `#horror #scary #shorts` (+ `#creepy #nightshift #scarystories` in TikTok/IG captions).

## Branching (how votes become episodes)
Each run: count the votes on the last posted episode on **all three platforms** (YouTube + TikTok + Instagram, summed;
most votes wins; `tools/votes.py`), post the matching pre-built branch, then build **both** branches
of the next episode (`<slug>-a`, `<slug>-b`, e.g. `ns02-a-opened`, `ns02-b-stayed`). Each branch follows its choice
honestly: if viewers open the door, something really happens because they opened it. Choosing "safe" should never be
boring; it brings a different danger. Branches that lose are marked `skipped` in `log.json` (their videos are deleted
in housekeeping). Keep a running `canon` list in the arc entry of `log.json` (what has actually happened on screen).

## Retention rules (learned from the football arc, still apply)
ep001 on TikTok: 752 views, 7.4 s average watch of 31 s, 11% full watches; 74% gone by 5 s. **Almost all the loss is in the
first 5 seconds; viewers who reach 8 s stay.**
1. **Frame 1 moves** with an impact within 0.5 s and a hit sound. Never a static or abstract opener.
2. **Hook text and the first narration line say the same thing.**
3. **No slow bridge.** Cut at least every 2 s until 8 s; the 1–4 s stretch needs a second reveal or hard cut.
4. **End with a rewatch prompt tied to the planted detail.**
5. **Binary question** (A or B) in description, pinned comment and on screen. Open questions got 0 comments.
6. Measured gains from these rules on the football arc: IG skip rate 49% → 27%, IG avg watch 8.6 s → 19.5 s, TikTok
   full watches 11.5% → 19.7% → 23.6%, TikTok avg watch 7.5 s → 10.8 s → 16.7 s (ep001 → ep003).
7. **What did NOT improve (2026-11-28 analysis):** reach. TikTok views fell 757 → 701 → 614 even as retention rose;
   shares, saves and profile visits were ~0 on every post; ~1 new follower in total. Serialized "Part N" football
   stories didn't give cold viewers a reason to comment, share or follow. Horror + voting targets exactly these signals:
   votes = comments, "send this to the friend who'd open it" = shares, "your vote decides" = follows.
8. Re-check every run (Windsor `get_data`: instagram `media_views`, `media_reel_skip_rate`, `media_reel_avg_watch_time`,
   `media_comments_count`, `media_shares`, `media_saved`; tiktok_organic `video_views_count`,
   `video_average_time_watched`, `video_full_watched_rate`, `video_comments`, `video_shares`, `video_new_followers`,
   `video_view_retention_*`; YouTube views/likes/comments from Buffer `get_post includeMetrics`) and record them in
   `log.json` → `analytics`. Track **comments (votes) and shares per 1k views** as the headline numbers for this lane.

## Guardrails (hard rules)
- Original characters and places only. No real people, real hotels/brands/chains, real crimes, real missing persons,
  or famous horror IP (no Slender-type, SCP, Backrooms or movie-monster lookalikes).
- Stories are fiction. Never claim "this really happened" or "true story".
- **Scary, not graphic (PG-13):** jump scares, dread, creepy faces and figures are fine. No blood, gore, wounds, bodies,
  violence shown on screen, self-harm or suicide themes, harm to children or animals, sexual content, slurs, or politics.
  The threat is implied (a hand on the handle, a shadow, a face at the lens).
- Every description includes the line "Fictional story. Animated, original characters."
- Music: only the generated sound bed. No copyrighted tracks.

## Arc structure
An arc is 5–7 voted episodes. Each episode stands alone (one rule, one scare, one choice) and moves the arc forward.
The finale's vote decides the ending. When an arc ends, the next run writes a **new arc** (new place, new rules list,
can keep the Visitor) and adds it to `series/log.json` with a premise, rules and a loose 5–7 episode plan (the votes
will bend it) before building episode 1.

---
## Archive: El Viejo (arc01, football, ep001–ep004)
El Viejo: 41-year-old keeper, charcoal #1 kit, salt-and-pepper beard with a white streak, "TEO" written on his wrist tape.
Teo: his son, early 20s, lime kit. The Director (ep004): long dark coat, short grey hair. Football guardrails: no real
players, clubs, crests, competitions or trophies. Arc ended early at ep004 by Samir's choice (2026-11-28).
