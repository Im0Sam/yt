"""Drawing primitives for the El Viejo Short (skia, 1080x1920)."""
import math, functools
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
import pathlib as _pl
FONT = skia.Typeface.MakeFromFile(str(_pl.Path(__file__).parent / 'fonts' / 'BebasNeue-Regular.ttf'))


# ---------------------------------------------------------------- helpers
def col(h, a=1.0):
    h = h.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.ColorSetARGB(int(max(0, min(1, a)) * 255), r, g, b)


def mix(h1, h2, t):
    a = [int(h1.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(h2.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    t = max(0, min(1, t))
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def seg(t, a, b):
    """0..1 progress of t across [a,b]."""
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)


def paint(c, a=1.0, stroke=None, cap=True, blur=0, blend=None, aa=True):
    p = skia.Paint(AntiAlias=aa)
    p.setColor(col(c, a) if isinstance(c, str) else c)
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend:
        p.setBlendMode(blend)
    return p


SCREEN = skia.BlendMode.kScreen
PLUS = skia.BlendMode.kPlus


def lin_shader(x0, y0, x1, y1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)],
                                          [col(*c) if isinstance(c, tuple) else col(c) for c in cols], pos)


def rad_shader(x, y, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(x, y), max(r, 1),
                                          [col(*c) if isinstance(c, tuple) else col(c) for c in cols], pos)


def glow(c, x, y, r, color, a=1.0, blend=SCREEN):
    p = skia.Paint(AntiAlias=True)
    p.setShader(rad_shader(x, y, r, [(color, a), (color, a * 0.35), (color, 0)], [0, 0.25, 1]))
    if blend:
        p.setBlendMode(blend)
    c.drawCircle(x, y, r, p)


def smooth_path(pts, closed=True, tension=0.5):
    """Catmull-Rom through points -> skia path."""
    p = skia.Path()
    n = len(pts)
    p.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        k = tension / 3 * 2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 2, p1[1] + (p2[1] - p0[1]) * k / 2)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 2, p2[1] - (p3[1] - p1[1]) * k / 2)
        p.cubicTo(*c1, *c2, *p2)
    if closed:
        p.close()
    return p


def rng_for(seed):
    return np.random.default_rng(seed)


# ---------------------------------------------------------------- environment
def sky(c, top='#03050b', bottom='#0d1a2b', y0=0, y1=H):
    p = skia.Paint()
    p.setShader(lin_shader(0, y0, 0, y1, [top, bottom]))
    c.drawRect(skia.Rect(0, -2000, W, H + 2000), p)


@functools.lru_cache(None)
def _crowd(seed, n):
    r = rng_for(seed)
    return r.random(n), r.random(n), r.random(n), r.random(n) * 6.28, r.random(n)


def stands(c, y_top, y_bot, t, seed=1, cheer=0.0, n=900, x0=-100, x1=W + 100, blur=0):
    """Dark stadium tier with twinkling crowd/phone lights."""
    p = skia.Paint()
    p.setShader(lin_shader(0, y_top, 0, y_bot, ['#0a0f18', '#152233', '#0b121c']))
    c.drawRect(skia.Rect(x0, y_top, x1, y_bot), p)
    # tier lines
    for k in range(1, 5):
        yy = y_top + (y_bot - y_top) * k / 5
        c.drawLine(x0, yy, x1, yy, paint('#22324a', 0.5, stroke=2))
    # roof edge
    c.drawRect(skia.Rect(x0, y_top - 14, x1, y_top), paint('#05080d'))
    xs, ys, sz, ph, kind = _crowd(seed, n)
    for i in range(n):
        x = x0 + xs[i] * (x1 - x0)
        y = y_top + 6 + ys[i] * (y_bot - y_top - 10)
        tw = 0.45 + 0.55 * math.sin(t * (2 + 3 * kind[i]) + ph[i])
        a = 0.18 + 0.25 * tw
        if kind[i] > 0.93:  # phone flashes
            a = 0.25 + cheer * 0.75 * (0.5 + 0.5 * math.sin(t * 9 + ph[i] * 3))
            colr = '#e8f3ff'
        else:
            colr = '#ffcf8f' if kind[i] < 0.5 else '#9fc4e6'
        c.drawCircle(x, y, 1.2 + sz[i] * 1.8, paint(colr, a * (1 + 0.6 * cheer), blur=blur))


def floodlight(c, x, y, t, scale=1.0, a=1.0, beams=True, beam_to=None):
    """Light bank with glow, anamorphic streak and beams."""
    s = scale
    if beams:
        bx, by = beam_to if beam_to else (x + (W / 2 - x) * 0.6, H)
        path = skia.Path()
        path.moveTo(x - 60 * s, y)
        path.lineTo(x + 60 * s, y)
        path.lineTo(bx + 520 * s, by)
        path.lineTo(bx - 520 * s, by)
        path.close()
        p = skia.Paint(AntiAlias=True)
        p.setShader(lin_shader(x, y, bx, by, [('#ffe2b0', 0.16 * a), ('#ffe2b0', 0.0)]))
        p.setBlendMode(SCREEN)
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
        c.drawPath(path, p)
    glow(c, x, y, 520 * s, '#ffcf8a', 0.55 * a)
    glow(c, x, y, 160 * s, '#fff3dc', 0.9 * a)
    # bank of lamps
    for i in range(5):
        for j in range(3):
            lx = x + (i - 2) * 26 * s
            ly = y + (j - 1) * 22 * s
            c.drawRect(skia.Rect(lx - 10 * s, ly - 8 * s, lx + 10 * s, ly + 8 * s), paint('#fffaf0', a))
    # anamorphic streak
    p = skia.Paint(AntiAlias=True)
    p.setShader(lin_shader(x - 700 * s, y, x + 700 * s, y,
                           [('#7fd8ff', 0), ('#a8e6ff', 0.5 * a), ('#7fd8ff', 0)]))
    p.setBlendMode(SCREEN)
    c.drawRect(skia.Rect(x - 700 * s, y - 3 * s, x + 700 * s, y + 3 * s), p)


@functools.lru_cache(None)
def _rain(seed, n):
    r = rng_for(seed)
    return r.random(n), r.random(n), 0.6 + r.random(n) * 0.8, r.random(n)


def rain(c, t, n=260, seed=7, speed=2600, length=60, wind=0.18, a=0.35, width=2.0,
         x0=-200, x1=W + 200, y0=-200, y1=H + 200, blur=0, color='#cfe3ff'):
    xs, ys, sp, al = _rain(seed, n)
    p = paint(color, a, stroke=width, blur=blur)
    span = y1 - y0
    for i in range(n):
        v = speed * sp[i]
        y = y0 + (ys[i] * span + v * t) % span
        x = x0 + xs[i] * (x1 - x0) + wind * (y - y0)
        L = length * sp[i]
        p.setAlphaf(a * (0.35 + 0.65 * al[i]))
        c.drawLine(x, y, x - wind * L, y - L, p)


class Cam:
    """Pinhole camera over a pitch. X lateral metres, Z forward metres, ground at 0."""

    def __init__(self, cx=W / 2, horizon=900, F=1400, h=2.0, xoff=0.0):
        self.cx, self.hz, self.F, self.h, self.xoff = cx, horizon, F, h, xoff

    def p(self, X, Z, Y=0.0):
        Z = max(Z, 0.05)
        return (self.cx + self.F * (X - self.xoff) / Z, self.hz + self.F * (self.h - Y) / Z)

    def s(self, Z, size=1.0):
        return self.F * size / max(Z, 0.05)


def pitch(c, cam, z_near=0.5, z_far=200, stripes=True, light=None):
    # base
    p = skia.Paint()
    p.setShader(lin_shader(0, cam.hz, 0, H, ['#0c2416', '#163b22', '#1b4a2a']))
    c.drawRect(skia.Rect(-500, cam.hz, W + 500, H + 500), p)
    if stripes:
        z = 1.0
        k = 0
        while z < z_far:
            z2 = z + 5.5
            y_a = cam.p(0, z)[1]
            y_b = cam.p(0, z2)[1]
            if k % 2 == 0:
                c.drawRect(skia.Rect(-500, y_b, W + 500, y_a), paint('#2c6a3a', 0.16))
            z = z2
            k += 1
    if light:
        lx, ly, lr = light
        glow(c, lx, ly, lr, '#ffd9a0', 0.22)
    # wet sheen
    p = skia.Paint()
    p.setShader(lin_shader(0, cam.hz, 0, cam.hz + 120, [('#9fc4e6', 0.10), ('#9fc4e6', 0)]))
    c.drawRect(skia.Rect(-500, cam.hz, W + 500, cam.hz + 120), p)


def pline(c, cam, pts, a=0.55, w=3.0):
    """Painted pitch line through world points (X,Z)."""
    path = skia.Path()
    first = True
    for (X, Z) in pts:
        x, y = cam.p(X, Z)
        if first:
            path.moveTo(x, y)
            first = False
        else:
            path.lineTo(x, y)
    c.drawPath(path, paint('#e9f2ea', a, stroke=w))


def goal_frame(c, cam, Zline, X0=0.0, depth=-2.0, a=1.0, w=None, net=True):
    """Goal at Zline (facing camera), posts at X0 +-3.66. depth: net extends to Zline+(-depth)."""
    L, R, Hh = X0 - 3.66, X0 + 3.66, 2.44
    Zb = Zline + abs(depth)
    if w is None:
        w = max(1.5, cam.s(Zline, 0.12))
    if net:
        np_ = paint('#dfe9f5', 0.22 * a, stroke=max(1, w * 0.25))
        for i in range(13):
            X = lerp(L, R, i / 12)
            x1, y1 = cam.p(X, Zb, 0)
            x2, y2 = cam.p(X, Zb, Hh * 0.8)
            c.drawLine(x1, y1, x2, y2, np_)
        for j in range(7):
            Y = Hh * 0.8 * j / 6
            x1, y1 = cam.p(L, Zb, Y)
            x2, y2 = cam.p(R, Zb, Y)
            c.drawLine(x1, y1, x2, y2, np_)
    pp = paint('#f4f7fb', a, stroke=w)
    tl, tr = cam.p(L, Zline, Hh), cam.p(R, Zline, Hh)
    bl, br = cam.p(L, Zline, 0), cam.p(R, Zline, 0)
    c.drawLine(*bl, *tl, pp)
    c.drawLine(*br, *tr, pp)
    c.drawLine(*tl, *tr, pp)


# ---------------------------------------------------------------- ball
def ball(c, x, y, r, rot=0.0, a=1.0, lit=(1, -1), motion=None):
    if r < 0.6:
        return
    if motion:  # (dx,dy) streak
        dx, dy = motion
        c.drawLine(x - dx, y - dy, x, y, paint('#f3f6fb', 0.25 * a, stroke=r * 1.6, blur=r * 0.3))
    p = skia.Paint(AntiAlias=True)
    lx, ly = lit
    p.setShader(rad_shader(x + lx * r * 0.35, y + ly * r * 0.35, r * 1.4,
                           [('#ffffff', a), ('#d9dee6', a), ('#5b6573', a)], [0, 0.45, 1]))
    c.drawCircle(x, y, r, p)
    if r > 5:
        c.save()
        clip = skia.Path()
        clip.addCircle(x, y, r)
        c.clipPath(clip, doAntiAlias=True)
        for k in range(4):
            ang = rot + k * 1.57
            px = x + math.cos(ang) * r * 0.62
            py = y + math.sin(ang * 0.8 + 0.5) * r * 0.55
            pent = skia.Path()
            for j in range(5):
                aa = ang + j * 1.2566
                vx = px + math.cos(aa) * r * 0.22
                vy = py + math.sin(aa) * r * 0.22
                (pent.moveTo if j == 0 else pent.lineTo)(vx, vy)
            pent.close()
            c.drawPath(pent, paint('#222831', 0.85 * a))
        c.restore()
        # specular
        c.drawCircle(x + lx * r * 0.4, y + ly * r * 0.4, r * 0.18, paint('#ffffff', 0.7 * a, blur=r * 0.08))


# ---------------------------------------------------------------- puppet
def D(a):
    r = math.radians(a)
    return math.sin(r), math.cos(r)


KITS = {
    'viejo': dict(jersey='#2e333b', sleeve='#262a31', shorts='#121417', socks='#2e333b', skin='#3a2a20',
                  glove='#0c0c0e', trim='#9aa3ad', hair='#2b2b2b', beard='#3b3936', streak='#d8d4cc'),
    'son': dict(jersey='#8fc41f', sleeve='#7cab19', shorts='#17210c', socks='#8fc41f', skin='#3a2a20',
                glove='#0c0c0e', trim='#e6ff9c', hair='#141414', beard=None, streak=None),
    'red': dict(jersey='#8e1b24', sleeve='#7a1720', shorts='#16181c', socks='#8e1b24', skin='#2f221a',
                glove=None, trim=None, hair='#151515', beard=None, streak=None),
    'navy': dict(jersey='#1d2e52', sleeve='#192845', shorts='#0e1526', socks='#1d2e52', skin='#3a2a20',
                 glove=None, trim=None, hair='#151515', beard=None, streak=None),
    'coach': dict(jersey='#14171c', sleeve='#14171c', shorts='#101216', socks='#101216', skin='#30231b',
                  glove=None, trim=None, hair='#202020', beard=None, streak=None, coat=True),
    'viejo_young': dict(jersey='#2e333b', sleeve='#262a31', shorts='#121417', socks='#2e333b', skin='#3a2a20',
                        glove='#0c0c0e', trim='#9aa3ad', hair='#1c1c1c', beard='#262422', streak='#262422'),
    'shadow': dict(jersey='#07090c', sleeve='#07090c', shorts='#07090c', socks='#07090c', skin='#07090c',
                   glove='#07090c', trim=None, hair='#07090c', beard=None, streak=None),
}

POSES = {
    'stand': dict(torso=180, head=0, uaL=-8, faL=-4, uaR=10, faR=6, thL=-5, shL=-3, thR=6, shR=4),
    'ready': dict(torso=166, head=8, uaL=40, faL=70, uaR=55, faR=85, thL=28, shL=-12, thR=40, shR=-6),
    'star': dict(torso=180, head=0, uaL=-150, faL=-160, uaR=150, faR=160, thL=-22, shL=-26, thR=22, shR=26),
    'dive': dict(torso=180, head=-6, uaL=-172, faL=-176, uaR=165, faR=172, thL=-10, shL=-18, thR=18, shR=8),
    'jump': dict(torso=184, head=-10, uaL=168, faL=176, uaR=176, faR=182, thL=-20, shL=-60, thR=30, shR=-30),
    'jumpo': dict(torso=176, head=-8, uaL=-130, faL=-150, uaR=120, faR=150, thL=-15, shL=-50, thR=25, shR=-35),
    'hold': dict(torso=176, head=6, uaL=55, faL=95, uaR=60, faR=100, thL=-6, shL=-4, thR=8, shR=4),
    'point': dict(torso=176, head=12, uaL=20, faL=40, uaR=96, faR=98, thL=-6, shL=-4, thR=10, shR=4),
}


def pose_lerp(a, b, t):
    return {k: lerp(a[k], b[k], t) for k in a}


def run_pose(ph, lean=162):
    s = math.sin(ph)
    return dict(torso=lean, head=10,
                uaL=-45 * s, faL=-45 * s + 80, uaR=45 * s, faR=45 * s + 80,
                thL=48 * s + 8, shL=48 * s + 8 - 55 * max(0, -math.cos(ph)) - 20,
                thR=-48 * s + 8, shR=-48 * s + 8 - 55 * max(0, math.cos(ph)) - 20)


def _fig_prims(pose, kit, beard, front, ball_in_hands):
    """Return list of (kind, args, colorkey, width) in local units, facing right."""
    T, UA, FA, TH, SH = 62, 30, 28, 44, 44
    hip = (0.0, 0.0)
    dt = D(pose['torso'])
    neck = (hip[0] + dt[0] * T, hip[1] + dt[1] * T)
    sh = (hip[0] + dt[0] * T * 0.9, hip[1] + dt[1] * T * 0.9)
    dh = D(pose['torso'] + pose['head'])
    head = (neck[0] + dh[0] * 14, neck[1] + dh[1] * 14)

    def limb(base, a1, l1, a2, l2):
        d1, d2 = D(a1), D(a2)
        j = (base[0] + d1[0] * l1, base[1] + d1[1] * l1)
        e = (j[0] + d2[0] * l2, j[1] + d2[1] * l2)
        return j, e

    off = 5 if front else 0
    shL = (sh[0] - off, sh[1]); shR = (sh[0] + off, sh[1])
    hipL = (hip[0] - off * 0.8, hip[1]); hipR = (hip[0] + off * 0.8, hip[1])
    eL, hL = limb(shL, pose['uaL'], UA, pose['faL'], FA)
    eR, hR = limb(shR, pose['uaR'], UA, pose['faR'], FA)
    kL, fL = limb(hipL, pose['thL'], TH, pose['shL'], SH)
    kR, fR = limb(hipR, pose['thR'], TH, pose['shR'], SH)
    pr = []
    dark = 'far'

    def leg(hp, k, f, side):
        pr.append(('line', (hp, k), 'shorts' if True else 'skin', 17, side))
        mid = (lerp(hp[0], k[0], 0.55), lerp(hp[1], k[1], 0.55))
        pr.append(('line', (mid, k), 'skin', 14, side))
        pr.append(('line', (k, f), 'socks', 12, side))
        pr.append(('circle', (f[0] + 4, f[1] + 1, 6.5), 'boot', 0, side))

    def arm(s_, e, h, side):
        pr.append(('line', (s_, e), 'sleeve', 11.5, side))
        pr.append(('line', (e, h), 'sleeve', 10, side))
        pr.append(('circle', (h[0], h[1], 7.5 if kit.get('glove') else 5.5), 'glove' if kit.get('glove') else 'skin', 0, side))

    arm(shL, eL, hL, 'far')
    leg(hipL, kL, fL, 'far')
    # torso polygon
    nx, ny = dt[1], -dt[0]  # normal
    wS, wH = (19 if not front else 21), (14 if not front else 16)
    if kit.get('coat'):
        wS, wH = wS + 3, wH + 4
    poly = [(sh[0] + nx * wS, sh[1] + ny * wS), (sh[0] - nx * wS, sh[1] - ny * wS),
            (hip[0] - nx * wH, hip[1] - ny * wH), (hip[0] + nx * wH, hip[1] + ny * wH)]
    pr.append(('poly', poly, 'jersey', 0, 'mid'))
    pr.append(('line', (hip, (hip[0] + dt[0] * 6, hip[1] + dt[1] * 6)), 'shorts', 30, 'mid'))
    leg(hipR, kR, fR, 'near')
    pr.append(('circle', (head[0], head[1], 12.5), 'skin', 0, 'mid'))
    # hair cap
    pr.append(('circle', (head[0] - dh[0] * 0 - (0 if front else 2.5), head[1] - 3.5, 10.5), 'hair', 0, 'mid'))
    pr.append(('circle', (head[0] + (0 if front else 3), head[1] + 2, 9), 'skin', 0, 'mid'))
    if beard and kit.get('beard'):
        bx = head[0] + (0 if front else 4.5)
        pr.append(('circle', (bx, head[1] + 6.5, 7.5), 'beard', 0, 'mid'))
        pr.append(('line', ((bx - 4, head[1] + 2), (bx - 3, head[1] + 9)), 'streak', 2.2, 'mid'))
    arm(shR, eR, hR, 'near')
    hands = (hL, hR)
    return pr, hands, head


def figure(c, pose, x, y, s, kit='viejo', face=1, rot=0.0, beard=None, front=False, rim=(4, -3),
           rim_col='#ffd49a', rim_a=0.95, shade=0.0, blur=0, alpha=1.0, ball_r=0):
    """Draw puppet; (x,y)=hip in screen px; s=px per unit. Returns hand positions in screen coords."""
    K = KITS[kit]
    if beard is None:
        beard = kit == 'viejo'
    prims, hands, head = _fig_prims(pose, K, beard, front, ball_r)

    def colfor(key, side):
        if key == 'boot':
            base = '#0a0a0a'
        elif key == 'streak':
            base = K['streak'] or '#cccccc'
        else:
            base = K.get(key) or K['skin']
        if side == 'far':
            base = mix(base, '#000000', 0.35)
        if shade:
            base = mix(base, '#000000', shade)
        return base

    def draw_pass(rim_pass):
        c.save()
        if rim_pass:
            c.translate(x + rim[0] * s * 0.6, y + rim[1] * s * 0.6)
        else:
            c.translate(x, y)
        c.rotate(rot)
        c.scale(face * s, s)
        for kind, args, key, wdt, side in prims:
            colr = rim_col if rim_pass else colfor(key, side)
            a = (rim_a if rim_pass else 1.0) * alpha
            if rim_pass and side == 'far':
                a *= 0.4
            p = paint(colr, a, stroke=wdt if kind == 'line' else None, blur=(blur / s if blur else 0))
            if kind == 'line':
                (a1, a2) = args
                c.drawLine(a1[0], a1[1], a2[0], a2[1], p)
            elif kind == 'circle':
                c.drawCircle(args[0], args[1], args[2], p)
            elif kind == 'poly':
                path = skia.Path()
                path.moveTo(*args[0])
                for q in args[1:]:
                    path.lineTo(*q)
                path.close()
                p.setStrokeJoin(skia.Paint.kRound_Join)
                c.drawPath(path, p)
                p2 = paint(colr, a, stroke=8)
                c.drawPath(path, p2)
        c.restore()

    if rim_a > 0:
        draw_pass(True)
    draw_pass(False)
    # transform hands to screen
    out = []
    r = math.radians(rot)
    for (hx, hy) in hands:
        lx, ly = hx * face * s, hy * s
        out.append((x + lx * math.cos(r) - ly * math.sin(r), y + lx * math.sin(r) + ly * math.cos(r)))
    return out


# ---------------------------------------------------------------- close-up profile
VIEJO_PROFILE = [(250, 1010), (262, 800), (215, 600), (225, 380), (320, 235), (470, 190), (585, 235),
                 (645, 330), (668, 430), (678, 458), (657, 488), (672, 525), (712, 575), (748, 612),
                 (712, 645), (684, 652), (700, 690), (694, 722), (712, 780), (692, 872), (612, 935),
                 (532, 962), (520, 1010)]
SON_PROFILE = [(250, 1010), (262, 800), (215, 600), (225, 380), (320, 235), (470, 190), (585, 235),
               (645, 330), (668, 430), (678, 458), (657, 488), (672, 525), (712, 575), (748, 612),
               (712, 645), (684, 652), (692, 688), (684, 716), (690, 752), (676, 808), (612, 858),
               (548, 900), (536, 1010)]


def profile(c, x, y, s, t, who='viejo', face=1, rim_col='#ffcf8f', rim_a=1.0, look_up=0.0, breath=0.0, young=False):
    """Big profile close-up. (x,y) = top-left of 1000-unit box; s scale. young=True: El Viejo before the grey/white streak."""
    pts = VIEJO_PROFILE if who == 'viejo' else SON_PROFILE
    c.save()
    c.translate(x, y)
    if face < 0:
        c.translate(1000 * s, 0)
    c.scale(face * s, s)
    c.rotate(-look_up)
    path = smooth_path(pts, closed=True, tension=0.9)
    # rim pass
    c.save()
    c.translate(9, -4)
    c.drawPath(path, paint(rim_col, rim_a))
    c.restore()
    c.save()
    c.translate(16, -6)
    c.drawPath(path, paint(rim_col, rim_a * 0.35, blur=14))
    c.restore()
    p = skia.Paint(AntiAlias=True)
    p.setShader(lin_shader(250, 0, 760, 0, ['#07080a', '#120d0b', '#2a1d16']))
    c.drawPath(path, p)
    c.save()
    c.clipPath(path, doAntiAlias=True)
    r = rng_for(3 if who == 'viejo' else 4)
    # hair
    hair_cols = (['#1c1c1c', '#2a2a2a'] if young else ['#2a2a2a', '#9a9792', '#4a4844']) if who == 'viejo' else ['#141414', '#1f1f1f']
    for i in range(420):
        hx = 220 + r.random() * 380
        hy = 180 + r.random() * 200 * (1 - (hx - 220) / 700)
        if hy > 200 + (hx - 220) * 0.25 and hx > 520:
            continue
        a = r.random() * 0.6 + 0.2
        cc = hair_cols[int(r.random() * len(hair_cols))]
        c.drawLine(hx, hy, hx - 10 - r.random() * 14, hy + 10 + r.random() * 12, paint(cc, a * 0.6, stroke=3))
    # beard
    if who == 'viejo':
        bp = smooth_path([(520, 640), (640, 650), (700, 690), (712, 780), (692, 872), (612, 935), (520, 965),
                          (470, 860), (480, 720)], closed=True)
        c.drawPath(bp, paint('#1b1714', 0.95))
        for i in range(520):
            bx = 470 + r.random() * 240
            by = 640 + r.random() * 320
            if not bp.contains(bx, by):
                continue
            streak = (not young) and bx < 590 and 690 < by < 930 and r.random() < 0.65
            cc = '#d9d5cd' if streak else ('#3a3632' if young else ('#5c5751' if r.random() < 0.35 else '#2c2723'))
            c.drawLine(bx, by, bx - 3 + r.random() * 6, by + 12 + r.random() * 10,
                       paint(cc, 0.55 if streak else 0.5, stroke=2.4))
    else:
        jaw = smooth_path([(560, 900), (620, 860), (676, 808)], closed=False)
        c.drawPath(jaw, paint('#3b2a20', 0.5, stroke=6))
    # ear
    c.drawOval(skia.Rect(380, 470, 450, 590), paint('#1a120e', 1))
    c.drawOval(skia.Rect(392, 482, 440, 580), paint('#2a1d16', 0.6, stroke=6))
    # cheek light
    glow(c, 640, 560, 150, '#ffbf80', 0.13)
    # eye
    eye = smooth_path([(598, 488), (624, 476), (648, 488), (624, 498)], closed=True)
    c.drawPath(eye, paint('#050505'))
    c.drawCircle(634, 485, 4.5, paint('#ffffff', 0.9))
    c.drawLine(592, 466, 650, 462, paint('#0a0807', 1, stroke=9))  # brow
    if who == 'viejo' and not young:
        for i in range(30):
            bx = 596 + r.random() * 54
            c.drawLine(bx, 460 + r.random() * 6, bx + 6, 452 + r.random() * 6, paint('#8d8780', 0.5, stroke=1.6))
    # rain droplets on skin edge
    for i in range(26):
        k = int(r.random() * (len(pts) - 6)) + 4
        px, py = pts[k]
        c.drawCircle(px - 6 - r.random() * 18, py + r.random() * 10, 2 + r.random() * 3.5,
                     paint('#ffe6c4', 0.55 + 0.4 * r.random()))
    c.restore()
    # collar / shoulder
    jcol = '#2e333b' if who == 'viejo' else '#8fc41f'
    sp = smooth_path([(120, 1000), (300, 935), (520, 965), (760, 1010), (900, 1150), (60, 1150)], closed=True)
    c.drawPath(sp, paint(jcol))
    c.drawPath(smooth_path([(300, 940), (420, 980), (530, 968)], closed=False),
               paint('#0b0d10' if who == 'viejo' else '#4e6e10', 1, stroke=14))
    c.restore()
    # breath vapour (screen space)
    if breath > 0:
        nose_x = x + (748 * s if face > 0 else (1000 - 748) * s)
        bx = nose_x + face * (40 + breath * 160) * s
        by = y + 660 * s + breath * 30 * s
        glow(c, bx, by, (60 + 160 * breath) * s, '#dfe9f5', 0.22 * (1 - breath))


# ---------------------------------------------------------------- text
def text_block(c, text, cx, y, size, fill='#ffffff', hl=(), hl_col='#ffd400', stroke=None, scale=1.0,
               alpha=1.0, maxw=930, rot=0.0, shadow=True):
    """Centered multi-line Bebas text with per-word highlight. Returns bottom y."""
    font = skia.Font(FONT, size)
    words = text.split(' ')
    lines, cur = [], []
    for w_ in words:
        trial = ' '.join(cur + [w_])
        if cur and font.measureText(trial) > maxw:
            lines.append(cur)
            cur = [w_]
        else:
            cur.append(w_)
    if cur:
        lines.append(cur)
    lh = size * 0.98
    stroke = size * 0.11 if stroke is None else stroke
    c.save()
    total_h = lh * len(lines)
    c.translate(cx, y + total_h / 2)
    c.rotate(rot)
    c.scale(scale, scale)
    c.translate(-cx, -(y + total_h / 2))
    space = font.measureText(' ')
    for li, ln in enumerate(lines):
        widths = [font.measureText(w_) for w_ in ln]
        tw = sum(widths) + space * (len(ln) - 1)
        x = cx - tw / 2
        yy = y + lh * (li + 1) - size * 0.12
        for w_, wd in zip(ln, widths):
            key = w_.strip('.,?!…').upper()
            fc = hl_col if key in hl else fill
            if shadow:
                c.drawString(w_, x + 6, yy + 8, font, paint('#000000', 0.55 * alpha, blur=6))
            c.drawString(w_, x, yy, font, paint('#000000', alpha, stroke=stroke))
            c.drawString(w_, x, yy, font, paint(fc, alpha))
            x += wd + space
    c.restore()
    return y + total_h


def caption(c, t, cues, y=1330, size=104):
    """cues: list of (start, end, text, highlights)."""
    for (a, b, txt, hl) in cues:
        if a <= t < b:
            k = (t - a)
            sc = 1.0 + 0.18 * (1 - ease_out(k / 0.14)) if k < 0.14 else 1.0
            al = clamp(k / 0.06) * clamp((b - t) / 0.06)
            text_block(c, txt, W / 2, y, size, hl=hl, scale=sc, alpha=al)


# ---------------------------------------------------------------- post
def _make_vignette():
    s = skia.Surface.MakeRaster(skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    c = s.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    p = skia.Paint()
    p.setShader(rad_shader(W / 2, H * 0.47, H * 0.75, [('#000000', 0), ('#000000', 0.0), ('#000000', 0.7)],
                           [0, 0.45, 1]))
    c.drawRect(skia.Rect(0, 0, W, H), p)
    return s.makeImageSnapshot()


def _make_grain(n=6):
    out = []
    r = rng_for(99)
    for i in range(n):
        g = (r.random((H // 2, W // 2)) * 255).astype(np.uint8)
        arr = np.dstack([g, g, g, np.full_like(g, 255)])
        img = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType)
        out.append(img)
    return out


_VIG = None
_GRAIN = None


def post(c, frame, flash=0.0, grain=0.07, fade=0.0):
    global _VIG, _GRAIN
    if _VIG is None:
        _VIG = _make_vignette()
        _GRAIN = _make_grain()
    c.drawImage(_VIG, 0, 0)
    p = skia.Paint()
    p.setBlendMode(skia.BlendMode.kOverlay)
    p.setAlphaf(grain)
    c.drawImageRect(_GRAIN[frame % len(_GRAIN)], skia.Rect(0, 0, W, H), skia.SamplingOptions(), p)
    if flash > 0:
        c.drawRect(skia.Rect(0, 0, W, H), paint('#fff6e6', flash))
    if fade > 0:
        c.drawRect(skia.Rect(0, 0, W, H), paint('#000000', fade))


def shake(t, amp, freq=23.0, seed=0.0):
    return (amp * math.sin(t * freq + seed) * math.cos(t * freq * 0.71 + 1.3 + seed),
            amp * math.sin(t * freq * 1.13 + 2.1 + seed))
