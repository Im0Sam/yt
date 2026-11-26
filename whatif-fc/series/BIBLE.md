# What If FC — series bible

**Lane:** animated football "what if" cinematics. Fictional matches, original characters, and emotional twists.
**Format:** YouTube Shorts / TikTok / Instagram Reels, 9:16 1080×1920, 30 fps, 28–40 s, narrated, captions burned in.
**Look:** stylised 2D animation drawn in code (skia): rainy night stadiums, warm floodlights with teal streaks,
silhouette figures with warm rim light, film grain and vignette. Bebas Neue captions are white with one yellow
highlight word. The hook text sits at the top for the first ~3 s.
**Voice:** Kokoro `am_michael`, a calm trailer narrator. Sentences are short. Hard facts come first and the emotion lands last.

## Recurring cast
- **El Viejo**: a 41-year-old goalkeeper who refuses to retire. He has weathered olive skin and a salt-and-pepper beard with a
  white streak on the left side. He wears a plain charcoal keeper kit with #1 and no logos, plus black gloves, and has white tape on his right hand with "TEO" written on it.
  He is quiet and stubborn and says little.
- **Teo**: El Viejo's son, early 20s. He is the opposing team's keeper and wears a lime kit. He has the same nose and eyes as his dad and no beard.
- **Teams (fictional, no names needed):** El Viejo's side wears navy outfield kits and the opponents wear crimson.
- New arcs may add new original characters. Each one gets a one-line visual description added here.

## Episode formula (every episode)
1. Hook in 0–2 s, usually **payoff first**: show the ending image before explaining it.
2. Promise at 2–5 s ("Ten minutes earlier…").
3. Three to five escalation beats, each a new shot.
4. A twist that is **planted earlier** with a one-second shot or a hidden detail.
5. A loop line whose last image or sentence flows back into frame 1.
6. A debate question in the description and a pinned comment that points at a hidden detail.

## Retention rules (learned from ep001 analytics)
ep001 on TikTok: 752 views, 7.4 s average watch of 31 s, 11% full watches. Retention was 66% at 1 s, 44% at 3 s,
26% at 5 s and 18% at 8 s, then almost flat (9% at the end). On Instagram, 50% of viewers skipped in the first 3 s.
**Almost all the loss is in the first 5 seconds; viewers who reach 8 s stay.** So:
1. **Frame 1 moves.** Open on an impact or action that lands within 0.5 s (net bulge, catch, collision) with a hit
   sound. Don't open on a static or abstract image.
2. **Hook text and the first narration line say the same thing** (or the VO directly answers the text). Two different
   messages in the first 2 s split attention.
3. **No slow "Ten minutes earlier…" bridge.** The 2–6 s promise must keep moving: a whip-in, fast cut or new information.
   Cut at least every 2 s until 8 s.
4. **End with a rewatch prompt tied to the planted detail** ("Watch again. Look at his tape."), which drives replays.
5. **Debate question is binary** (YES or NO, A or B) in both the description and the pinned comment. ep001's open question
   got 0 comments.
6. Re-check these numbers each run (Windsor `get_data`: instagram `media_reel_skip_rate`, `media_reel_avg_watch_time`;
   tiktok_organic `video_view_retention_*`, `video_full_watched_rate`) and record them in `log.json` → `analytics`.

## Guardrails (hard rules)
- No real players, coaches, clubs, crests, sponsor logos, league or FIFA/World Cup branding, or real trophies.
  Say "the final", not "the World Cup final".
- Never recreate a famous real goal or match moment.
- Stories are fiction. Don't claim "this really happened", and don't put real-world statistics in the narration.
- Keep it PG: no injuries shown graphically, no violence, nothing sexual, no slurs, no politics.
- Every description includes the line "Fictional story. Animated, original characters."
- Music: only the generated sound bed. No copyrighted tracks.

## Arc structure
An arc is 5–7 episodes about one character or relationship. Each episode stands alone and also moves the arc forward.
When an arc's planned episodes are all posted, the next run writes a **new arc** (new premise, can reuse
or retire characters) and adds it to `series/log.json` with its full episode outline before building episode 1.
