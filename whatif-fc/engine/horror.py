"""Horror shot kit (built for arc02 'Night Shift Rules', ep101+).
Darkness + flashlight, one-point-perspective motel corridor with flickering lights, doors, CCTV look,
RGB-split glitch, peephole, the Visitor puppet and its scare face, neon sign, handwritten notes.
All functions draw at the current canvas transform; call glitch()/cctv() last, with no transform active."""
import math
import skia
from lib import *

# The Visitor: looks like the motel manager from behind (grey hair, brown cardigan), too tall and too thin.
KITS['visitor'] = dict(jersey='#4a3424', sleeve='#3e2b1e', shorts='#1c1a18', socks='#1c1a18', skin='#b9b3a6',
                       glove=None, trim=None, hair='#8d8a84', beard=None, streak=None, coat=True)
KITS['visitor_back'] = dict(KITS['visitor'], skin='#1f1b17')   # from behind: trousers, no pale skin showing
KITS['guard'] = dict(jersey='#1f2a3a', sleeve='#1a2433', shorts='#14181f', socks='#14181f', skin='#3a2a20',
                     glove=None, trim=None, hair='#141414', beard=None, streak=None)

FULL = skia.Rect(-400, -400, W + 400, H + 400)
RED = '#ff2b2b'


# ---------------------------------------------------------------- light
def darkness(c, x, y, r, dark=0.94, warm='#ffe7b8', tint=0.10):
    """Black out everything except a soft flashlight circle at (x, y)."""
    p = skia.Paint()
    p.setShader(rad_shader(x, y, r * 1.7, [('#000000', 0.0), ('#000000', 0.25 * dark), ('#000000', dark)],
                           [0, 0.5, 1]))
    c.drawRect(FULL, p)
    if tint:
        glow(c, x, y, r, warm, tint)


def dust(c, t, x, y, r, n=60, seed=1, a=0.5):
    """Dust motes drifting inside a light circle."""
    rr = rng_for(seed)
    for i in range(n):
        px = x + (rr.random() * 2 - 1) * r + 20 * math.sin(t * (0.3 + rr.random()) + i)
        py = y + (rr.random() * 2 - 1) * r + ((t * (12 + 20 * rr.random())) % (2 * r)) - r
        d = math.hypot(px - x, py - y) / r
        if d < 1:
            c.drawCircle(px, py, 1.2 + rr.random() * 2.4, paint('#fff1d6', a * (1 - d) * (0.4 + 0.6 * rr.random())))


def flicker(t, seed=0, rate=1.0, dead=0.0):
    """0..1 fluorescent flicker. dead: 0 = steady, 1 = mostly off."""
    k = int(t * 24 * rate) + seed * 97
    r = rng_for(k).random()
    on = 1.0 if r > dead * 0.85 else 0.0
    if 0.0 < dead and rng_for(k + 5).random() < 0.15:
        on *= 0.35
    return on


# ---------------------------------------------------------------- corridor
WALL = '#4b4a36'      # sickly wallpaper
CARPET = '#3a1416'    # old red carpet
CEIL = '#1d1c18'
DOORC = '#3a2618'


def corridor(c, t, cam, dolly=0.0, lamps=None, length=26.0, hw=1.6, hh=2.6, end_glow=0.6, door_nums=True,
             open_door=None):
    """One-point-perspective hallway. cam: lib.Cam (h = eye height). dolly: camera moved forward (m).
    lamps: list of (z, brightness 0..1) ceiling panels. open_door: (z, side, amount) a door ajar with light."""
    if lamps is None:
        lamps = [(z, 1.0) for z in (2, 6, 10, 14, 18, 22)]

    def light(z):
        v = 0.05
        for lz, b in lamps:
            v += b * 0.95 * math.exp(-abs(z - lz) * 0.55)
        return min(1.0, v) * math.exp(-max(0, z - dolly) * 0.03)

    c.drawRect(FULL, paint('#000000'))
    zs = []
    z = length
    while z > dolly + 0.25:
        zs.append(z)
        z -= 0.5
    zs.append(dolly + 0.25)
    # far end wall + exit sign
    ze = length - dolly
    a1, a2 = cam.p(-hw, ze, hh), cam.p(hw, ze, 0)
    c.drawRect(skia.Rect(a1[0], a1[1], a2[0], a2[1]), paint(mix('#000000', WALL, light(length) * 0.6)))
    ex, ey = cam.p(0, ze, hh - 0.25)
    sw = cam.s(ze, 0.5)
    c.drawRect(skia.Rect(ex - sw / 2, ey - sw * 0.2, ex + sw / 2, ey + sw * 0.2), paint('#ff2020', 0.9))
    glow(c, ex, ey, sw * 3, '#ff2020', 0.5 * end_glow)
    for i in range(len(zs) - 1):
        z1w, z2w = zs[i], zs[i + 1]          # far, near (world)
        z1, z2 = z1w - dolly, z2w - dolly
        lv = light((z1w + z2w) / 2)
        for X, base in ((-hw, WALL), (hw, WALL)):
            q = [cam.p(X, z1, 0), cam.p(X, z2, 0), cam.p(X, z2, hh), cam.p(X, z1, hh)]
            path = skia.Path(); path.moveTo(*q[0]); [path.lineTo(*p_) for p_ in q[1:]]; path.close()
            c.drawPath(path, paint(mix('#000000', base, lv * (0.85 if X > 0 else 0.75))))
        # floor (carpet with a diamond stripe every other band)
        q = [cam.p(-hw, z1, 0), cam.p(hw, z1, 0), cam.p(hw, z2, 0), cam.p(-hw, z2, 0)]
        path = skia.Path(); path.moveTo(*q[0]); [path.lineTo(*p_) for p_ in q[1:]]; path.close()
        band = int(z1w * 2) % 4 == 0
        c.drawPath(path, paint(mix('#000000', '#5a2a1c' if band else CARPET, lv * 0.9)))
        # ceiling
        q = [cam.p(-hw, z1, hh), cam.p(hw, z1, hh), cam.p(hw, z2, hh), cam.p(-hw, z2, hh)]
        path = skia.Path(); path.moveTo(*q[0]); [path.lineTo(*p_) for p_ in q[1:]]; path.close()
        c.drawPath(path, paint(mix('#000000', CEIL, lv)))
        # skirting
        for X in (-hw, hw):
            pa, pb = cam.p(X, z1, 0.12), cam.p(X, z2, 0.12)
            c.drawLine(*pa, *pb, paint(mix('#000000', '#2a2016', lv), 1, stroke=max(1, cam.s(z2, 0.05)), cap=False))
    # doors on both walls every 3 m (drawn far to near)
    k = 0
    for zd in [z_ for z_ in range(int(length) - 2, 0, -3)]:
        for side in (-1, 1):
            z0w, z1w = zd, zd + 0.95
            z0, z1 = z0w - dolly, z1w - dolly
            if z0 < 0.3:
                continue
            X = side * hw
            lv = light(zd + 0.5)
            q = [cam.p(X, z0, 0), cam.p(X, z1, 0), cam.p(X, z1, 2.1), cam.p(X, z0, 2.1)]
            path = skia.Path(); path.moveTo(*q[0]); [path.lineTo(*p_) for p_ in q[1:]]; path.close()
            c.drawPath(path, paint(mix('#000000', DOORC, lv)))
            c.drawPath(path, paint(mix('#000000', '#1a120c', lv), 1, stroke=max(1, cam.s(z0, 0.04))))
            if open_door and abs(open_door[0] - zd) < 0.1 and open_door[1] == side:
                amt = open_door[2]
                q2 = [cam.p(X, z0, 0), cam.p(X, z0 + 0.95 * amt, 0), cam.p(X, z0 + 0.95 * amt, 2.1), cam.p(X, z0, 2.1)]
                path = skia.Path(); path.moveTo(*q2[0]); [path.lineTo(*p_) for p_ in q2[1:]]; path.close()
                c.drawPath(path, paint('#ffd27a', 0.9))
                gx, gy = cam.p(X * 0.6, z0 + 0.5, 0)
                glow(c, gx, gy, cam.s(z0, 1.6), '#ffd27a', 0.35 * amt)
            hx, hy = cam.p(X, z0 + 0.8, 1.0)
            c.drawCircle(hx, hy, max(1, cam.s(z0, 0.035)), paint('#c9a24a', lv))
            if door_nums and cam.s(z0, 0.2) > 8:
                nx, ny = cam.p(X, z0 + 0.47, 1.65)
                num = str(2 + k) if side < 0 else str(3 + k)
                f = skia.Font(FONT, cam.s(z0 + 0.47, 0.16))
                c.save(); c.translate(nx, ny); c.scale(0.55 if True else 1, 1)
                c.drawString(num, -f.measureText(num) / 2, 0, f, paint(mix('#000000', '#c9a24a', lv)))
                c.restore()
        k += 2
    # ceiling panels
    for lz, b in lamps:
        z_ = lz - dolly
        if z_ < 0.3:
            continue
        q = [cam.p(-0.35, z_ - 0.6, hh - 0.01), cam.p(0.35, z_ - 0.6, hh - 0.01),
             cam.p(0.35, z_ + 0.6, hh - 0.01), cam.p(-0.35, z_ + 0.6, hh - 0.01)]
        path = skia.Path(); path.moveTo(*q[0]); [path.lineTo(*p_) for p_ in q[1:]]; path.close()
        c.drawPath(path, paint(mix('#2a2a24', '#f4fbe8', b)))
        if b > 0.05:
            gx, gy = cam.p(0, z_, hh - 0.1)
            glow(c, gx, gy, cam.s(z_, 1.6), '#e8f5d0', 0.45 * b)
            fx, fy = cam.p(0, z_, 0)
            glow(c, fx, fy, cam.s(z_, 1.4), '#e8f5d0', 0.12 * b)
    # depth fog
    vx, vy = cam.p(0, 40, cam.h)
    p = skia.Paint()
    p.setShader(rad_shader(vx, vy, 520, [('#05070a', 0.75), ('#05070a', 0.0)]))
    c.drawRect(FULL, p)


# ---------------------------------------------------------------- the Visitor
def visitor(c, x, y, s, t, back=True, eyes=0.0, pose=None, rim_col='#e8f5d0', rim_a=0.6, stretch=1.18, thin=0.82,
            alpha=1.0, blur=0, shade=0.0):
    """Tall, thin figure; (x, y) = feet on the floor. back=True: we see the back of its head (grey hair)."""
    pz = pose or dict(torso=180, head=0, uaL=-3, faL=-1, uaR=3, faR=1, thL=-2, shL=-1, thR=2, shR=1)
    c.save()
    c.translate(x, y)
    c.scale(thin, stretch)
    c.translate(-x, -y)
    hip_y = y - 92 * s
    figure(c, pz, x, hip_y, s, kit='visitor_back' if back else 'visitor', front=True, beard=False, rim=(3, -3), rim_col=rim_col, rim_a=rim_a,
           alpha=alpha, blur=blur, shade=shade)
    from shots import head_pos
    hx, hy = head_pos(pz, x, hip_y, s)
    if back:
        c.drawCircle(hx, hy + 0.5 * s, 12.8 * s, paint(mix('#8d8a84', '#000000', shade), alpha, blur=blur))
        c.drawCircle(hx - 3 * s, hy - 3 * s, 6 * s, paint(mix('#b5b1a9', '#000000', shade), 0.5 * alpha, blur=blur + 2))
    elif eyes > 0:
        for dx in (-4.2, 4.2):
            c.drawCircle(hx + dx * s, hy - 0.5 * s, 2.6 * s, paint('#000000', alpha))
            c.drawCircle(hx + dx * s, hy - 0.5 * s, 0.9 * s, paint('#ffffff', eyes * alpha))
            glow(c, hx + dx * s, hy - 0.5 * s, 4 * s, '#ffffff', 0.4 * eyes * alpha)
    c.restore()
    return hx, hy


def scare_face(c, cx, cy, sc, t, open_=1.0, tilt=-11):
    """The Visitor's face pressed to the lens: long, grey-pale, uneven hollow eyes with pinpoint pupils,
    a thin grin that runs too far. PG: no blood, no wounds."""
    c.save()
    c.translate(cx, cy)
    c.rotate(tilt)
    c.scale(sc, sc * 1.08)
    j = 4 * math.sin(t * 61) * math.sin(t * 17)
    c.translate(j, -j * 0.5)
    face = skia.Path()
    face.addOval(skia.Rect(-300, -470, 300, 520))
    c.drawPath(face, paint('#cfc9bb', 1, blur=4))
    p = skia.Paint(AntiAlias=True)
    p.setShader(rad_shader(-40, -80, 560, [('#000000', 0.0), ('#000000', 0.25), ('#000000', 0.9)], [0, 0.45, 1]))
    c.drawPath(face, p)
    # hair: thin grey strands hanging over the forehead
    c.drawOval(skia.Rect(-340, -560, 340, -300), paint('#77736b', 1, blur=8))
    r = rng_for(77)
    for k in range(26):
        x0 = -260 + k * 21 + r.random() * 10
        c.drawLine(x0, -380, x0 + r.random() * 30 - 15, -250 + r.random() * 120, paint('#5f5b54', 0.8, stroke=5))
    # sunken sockets (uneven), pinpoint pupils staring into the lens
    for dx, rx, ry, py in ((-120, 78, 66, -40), (125, 66, 82, -30)):
        c.drawOval(skia.Rect(dx - rx - 30, py - ry - 25, dx + rx + 30, py + ry + 35), paint('#3a3631', 0.8, blur=24))
        c.drawOval(skia.Rect(dx - rx, py - ry, dx + rx, py + ry), paint('#030303'))
        c.drawCircle(dx + 6, py + 4, 11, paint('#ffffff'))
        glow(c, dx + 6, py + 4, 40, '#ffffff', 0.3)
    # nose shadow
    c.drawPath(_tri(0, 70, 24, 150), paint('#3a3631', 0.6, blur=10))
    # the grin: a thin dark crescent running past the cheeks
    m = 18 + 90 * open_
    path = skia.Path()
    path.moveTo(-270, 250); path.quadTo(0, 250 + m * 1.6, 270, 235); path.quadTo(0, 250 + m * 0.5, -270, 250)
    c.drawPath(path, paint('#050505'))
    for k in range(9):  # faint vertical creases inside the grin
        x = -160 + k * 40
        c.drawLine(x, 262, x, 262 + m * 0.6, paint('#2a2622', 0.7, stroke=3))
    # cardigan collar
    c.drawRect(skia.Rect(-420, 470, 420, 900), paint('#3e2b1e'))
    c.restore()


def _tri(x, y, w, h):
    p = skia.Path()
    p.moveTo(x, y); p.lineTo(x + w, y + h); p.lineTo(x - w * 0.6, y + h); p.close()
    return p


# ---------------------------------------------------------------- door (from the inside, POV)
def office_door(c, t, shake_amt=0.0, handle=0.0, gap_light=0.7, feet=0.0, peephole=True, light=0.35):
    """Wooden door filling the frame. handle: 0..1 lever pressed down. feet: 0..1 shadows in the gap."""
    sx, sy = shake(t, shake_amt * 14)
    c.save()
    c.translate(sx, sy)
    c.drawRect(FULL, paint('#0b0a09'))
    x0, x1, y0, y1 = 170, 910, 160, 1700
    c.drawRect(skia.Rect(x0 - 40, y0 - 40, x1 + 40, y1), paint('#1a140f'))          # frame
    d = skia.Paint()
    d.setShader(lin_shader(x0, 0, x1, 0, [mix('#000000', '#5a3a22', light), mix('#000000', '#4a2f1b', light * 0.8)]))
    c.drawRect(skia.Rect(x0, y0, x1, y1), d)
    for (a, b, cc, dd) in ((230, 240, 850, 860), (230, 960, 850, 1620)):            # panels
        c.drawRect(skia.Rect(a, b, cc, dd), paint(mix('#000000', '#2a1a0e', light * 1.5), 1, stroke=10))
    r = rng_for(301)
    for k in range(30):                                                             # grain
        xx = x0 + r.random() * (x1 - x0)
        c.drawLine(xx, y0, xx + r.random() * 6 - 3, y1, paint('#000000', 0.12, stroke=2 + r.random() * 3))
    # gap under the door
    c.drawRect(skia.Rect(x0, y1 - 6, x1, y1 + 14), paint('#ffd9a0', gap_light))
    glow(c, 540, y1 + 40, 380, '#ffd9a0', 0.3 * gap_light)
    if feet > 0:
        for fx in (430, 640):
            c.drawRect(skia.Rect(fx - 70 * feet, y1 - 6, fx + 70 * feet, y1 + 14), paint('#000000', 0.95))
    c.drawRect(skia.Rect(-400, y1 + 14, W + 400, H + 400), paint('#0e0c0b'))
    # peephole
    if peephole:
        c.drawCircle(540, 700, 26, paint('#c9a24a', light * 2))
        c.drawCircle(540, 700, 14, paint('#050505'))
    # lever handle
    hx, hy = 820, 1000
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(hx - 34, hy - 110, hx + 34, hy + 110), 14, 14),
                paint(mix('#000000', '#9a8a6a', light * 2)))
    c.save(); c.translate(hx, hy); c.rotate(-180 + 32 * handle)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-14, -14, 200, 14), 12, 12), paint(mix('#000000', '#d8c08a', light * 2.2)))
    c.restore()
    # deadbolt + chain
    c.drawCircle(820, 820, 30, paint(mix('#000000', '#9a8a6a', light * 2)))
    c.drawLine(560, 560, 790, 600, paint(mix('#000000', '#b8b0a0', light * 2), 1, stroke=6))
    c.restore()


# ---------------------------------------------------------------- CCTV / glitch / peephole post-effects
def cctv(c, t, label='CAM 04  HALLWAY', stamp='03:00:00', rec=True):
    p = skia.Paint()
    p.setBlendMode(skia.BlendMode.kSaturation)
    p.setColor(col('#808080'))
    c.drawRect(FULL, p)
    c.drawRect(FULL, paint('#3cff9a', 0.06, blend=skia.BlendMode.kOverlay))
    for y in range(0, H, 6):
        c.drawLine(0, y, W, y, paint('#000000', 0.12, stroke=2, cap=False))
    band = (t * 380) % (H + 300) - 150
    c.drawRect(skia.Rect(0, band, W, band + 70), paint('#ffffff', 0.05))
    f = skia.Font(FONT, 64)
    c.drawString(label, 60, 1265, f, paint('#e8e8e8', 0.85))
    c.drawString(stamp, W - 60 - f.measureText(stamp), 1265, f, paint('#e8e8e8', 0.85))
    if rec and int(t * 2) % 2 == 0:
        c.drawCircle(76, 210, 16, paint(RED))
        c.drawString('REC', 104, 232, skia.Font(FONT, 64), paint('#e8e8e8', 0.85))
    for (x, y, dx, dy) in ((40, 140, 1, 1), (W - 40, 140, -1, 1), (40, 1520, 1, -1), (W - 40, 1520, -1, -1)):
        c.drawLine(x, y, x + 70 * dx, y, paint('#e8e8e8', 0.7, stroke=5))
        c.drawLine(x, y, x, y + 70 * dy, paint('#e8e8e8', 0.7, stroke=5))


_RED_M = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
_CYAN_M = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]


def glitch(c, t, amt, seed=0):
    """RGB split + displaced slices of what is already on the canvas. Call with no transform active."""
    if amt <= 0.02:
        return
    surf = c.getSurface()
    if surf is None:
        return
    img = surf.makeImageSnapshot()
    r = rng_for(int(t * 30) * 7 + seed)
    for m, dx in ((_RED_M, -18 * amt), (_CYAN_M, 18 * amt)):
        p = skia.Paint()
        p.setColorFilter(skia.ColorFilters.Matrix(m))
        p.setBlendMode(skia.BlendMode.kScreen)
        p.setAlphaf(min(1.0, 0.6 * amt))
        c.drawImage(img, dx, 0, skia.SamplingOptions(), p)
    for k in range(int(3 + 7 * amt)):
        y = r.random() * H
        h = 12 + r.random() * 110 * amt
        dx = (r.random() - 0.5) * 220 * amt
        c.save()
        c.clipRect(skia.Rect(0, y, W, y + h))
        c.drawImage(img, dx, 0)
        c.restore()


def peephole_mask(c, cx=540, cy=820, r=400):
    """Black out everything outside the round peephole lens, with a brass ring and lens vignette."""
    path = skia.Path()
    path.addRect(FULL)
    path.addCircle(cx, cy, r)
    path.setFillType(skia.PathFillType.kEvenOdd)
    c.drawPath(path, paint('#020202'))
    p = skia.Paint()
    p.setShader(rad_shader(cx, cy, r, [('#000000', 0.0), ('#000000', 0.0), ('#000000', 0.85)], [0, 0.62, 1]))
    c.drawCircle(cx, cy, r, p)
    c.drawCircle(cx, cy, r + 10, paint('#6a5a3a', 0.8, stroke=18))
    c.drawCircle(cx - r * 0.35, cy - r * 0.4, r * 0.25, paint('#ffffff', 0.05, blur=20))


# ---------------------------------------------------------------- exterior + props
def neon_text(c, s, x, y, size, colr, on=1.0, center=True):
    f = skia.Font(FONT, size)
    if center:
        x -= f.measureText(s) / 2
    if on > 0.05:
        c.drawString(s, x, y, f, paint(colr, 0.55 * on, blur=size * 0.18))
        c.drawString(s, x, y, f, paint(colr, 0.35 * on, blur=size * 0.45))
    c.drawString(s, x, y, f, paint(mix('#1a1a1a', '#ffffff', 0.15 + 0.85 * on), 1, stroke=size * 0.05))
    c.drawString(s, x, y, f, paint(mix('#2a1515', colr, on), 1))


def note(c, x, y, ang, sc, lines, a=1.0, tape=True):
    """A taped sheet of lined paper; lines = [(text, size, colour), ...] drawn top-down."""
    c.save()
    c.translate(x, y); c.rotate(ang); c.scale(sc, sc)
    c.save(); c.translate(16, 24); c.drawRect(skia.Rect(-300, -400, 300, 400), paint('#000000', 0.55 * a, blur=22))
    c.restore()
    c.drawRect(skia.Rect(-300, -400, 300, 400), paint('#e6dfcf', a))
    for k in range(14):
        yy = -300 + k * 52
        c.drawLine(-290, yy, 290, yy, paint('#7fa3c8', 0.35 * a, stroke=2))
    c.drawLine(-230, -400, -230, 400, paint('#d06060', 0.4 * a, stroke=2))
    yy = -330
    for txt, size, colr in lines:
        f = skia.Font(FONT, size)
        c.drawString(txt, -215, yy + size * 0.8, f, paint(colr, a))
        yy += size * 1.05 + 6
    if tape:
        for tx in (-260, 260):
            c.save(); c.translate(tx, -395); c.rotate(-35 if tx < 0 else 35)
            c.drawRect(skia.Rect(-70, -22, 70, 22), paint('#e8e2c0', 0.75 * a))
            c.restore()
    c.restore()
