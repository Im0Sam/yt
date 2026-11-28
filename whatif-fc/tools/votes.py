"""Count the A/B votes for an episode across YouTube, TikTok and Instagram. The most votes in total wins.

Usage:
  python3 tools/votes.py episodes/<slug> comments.json [--write]

comments.json is the raw comment rows pulled with Windsor get_data, saved as
  {"youtube":   [{comment_video_id, comment_id, comment_text, comment_author}, ...],
   "tiktok":    [{comment_video_id, comment_id, comment_text, comment_username, comment_parent_id}, ...],
   "instagram": [{media_id, comment_id, comment_text, comment_username, comment_parent_id}, ...]}
Rows for other videos are ignored: only the episode's own ids from series/log.json -> posts are counted.

Rules (also in RUNBOOK.md step 1):
- A vote is a top-level comment that starts with A or B as its own word ("A", "a!!", "B 100%", "option A", "(B)"),
  or that names exactly one option's words (script.json choice.keywords, e.g. "open it" / "don't open").
  Comments naming both options, or neither, don't count. Our own pinned comment never counts.
- One vote per person per platform: if someone votes twice, their latest comment counts.
- Winner = most votes summed over all three platforms. Tie: the option that won on more platforms; still tied: the
  option in choice.tie_break (default "A"), and the log says it was a tie.
--write stores the result in series/log.json on that episode as `vote`."""
import json, re, sys, pathlib, datetime
from _paths import ROOT

ep_dir = pathlib.Path(sys.argv[1])
ep_dir = ep_dir if ep_dir.is_absolute() else ROOT / ep_dir
slug = ep_dir.name
rows = json.loads(pathlib.Path(sys.argv[2]).read_text())
script = json.loads((ep_dir / 'script.json').read_text())
choice = script['choice']
log_path = ROOT / 'series' / 'log.json'
log = json.loads(log_path.read_text())
ep = next(e for e in log['episodes'] if e['slug'] == slug)
posts = ep.get('posts', {})

ids = {
    'youtube': posts.get('youtube', {}).get('video_id'),
    'tiktok': posts.get('tiktok', {}).get('video_id'),
    'instagram': posts.get('instagram', {}).get('media_id'),
}
own = {posts.get('instagram', {}).get('pinned_comment_id')} - {None}


def norm(s):
    s = (s or '').upper()
    s = s.replace('’', "'")
    return re.sub(r"[^A-Z0-9' ]+", ' ', s).strip()


def default_keywords(label):
    return [norm(label)]


kw = {k: [norm(x) for x in choice.get('keywords', {}).get(k, default_keywords(choice[k]))] for k in ('A', 'B')}


def parse(text):
    t = norm(text)
    if not t:
        return None
    m = re.match(r"^(?:OPTION |VOTE |I VOTE |I CHOOSE |MY VOTE )?([AB])(?:\b|$)", t)
    if m:
        return m.group(1)
    # longest keyword first so "DON'T OPEN" beats "OPEN"
    hits = set()
    pairs = sorted(((w, k) for k in kw for w in kw[k]), key=lambda p: -len(p[0]))
    rest = ' ' + t + ' '
    for w, k in pairs:
        if w and (' ' + w + ' ') in rest:
            hits.add(k)
            rest = rest.replace(' ' + w + ' ', ' # ')
    return hits.pop() if len(hits) == 1 else None


VID = {'youtube': 'comment_video_id', 'tiktok': 'comment_video_id', 'instagram': 'media_id'}
WHO = {'youtube': 'comment_author', 'tiktok': 'comment_username', 'instagram': 'comment_username'}
TS = {'youtube': 'comment_published_at', 'tiktok': 'comment_create_time', 'instagram': 'comment_timestamp'}

per = {}
ignored = []
for plat in ('youtube', 'tiktok', 'instagram'):
    tally = {'A': 0, 'B': 0}
    voters = {}
    plat_rows = [r for r in rows.get(plat, []) if ids[plat] and str(r.get(VID[plat])) == str(ids[plat])]
    plat_rows.sort(key=lambda r: str(r.get(TS[plat]) or ''))
    for r in plat_rows:
        if r.get('comment_id') in own or r.get('comment_parent_id'):
            continue
        v = parse(r.get('comment_text'))
        if v is None:
            ignored.append((plat, r.get('comment_text')))
            continue
        who = r.get(WHO[plat]) or r.get('comment_id')
        voters[who] = v
    for v in voters.values():
        tally[v] += 1
    per[plat] = dict(tally, comments_read=len(plat_rows), counted=bool(ids[plat]))

total = {k: sum(per[p][k] for p in per) for k in ('A', 'B')}
platforms_won = {k: sum(1 for p in per if per[p][k] > per[p]['AB'.replace(k, '')]) for k in ('A', 'B')}
if total['A'] != total['B']:
    result, how = ('A' if total['A'] > total['B'] else 'B'), 'most votes'
elif platforms_won['A'] != platforms_won['B']:
    result, how = ('A' if platforms_won['A'] > platforms_won['B'] else 'B'), 'tie on votes, won more platforms'
else:
    result, how = choice.get('tie_break', 'A'), 'full tie, tie_break'

out = {'A': total['A'], 'B': total['B'], 'result': result, 'decided_by': how, 'per_platform': per,
       'counted': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
       'options': {'A': choice['A'], 'B': choice['B']}}
print(json.dumps(out, indent=1, ensure_ascii=False))
if ignored:
    print('not counted (no clear A/B):', *[f'  [{p}] {t!r}' for p, t in ignored[:30]], sep='\n')
if '--write' in sys.argv:
    ep['vote'] = out
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False))
    print('written to log.json')
