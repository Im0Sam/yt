"""Hand-drawn character designs for Night Shift Rules (replace the stick-puppet look).

Every character is built from smooth bezier shapes in a 1000-unit box (feet at y=0, top of head near y=-1000,
x=0 the centre line), then scaled to the requested pixel height. Each draw does: rim-light silhouette pass, base
colours, form shading (gradients), texture (knit ribs, hair strands, fabric folds), then face details.

  visitor(c, x, y, h, t, view='back'|'front'|'side', light=1.0, arm=0.0, head_turn=0.0, rim='#e8f5d0', ...)
  hale(c, x, y, h, t, view='front'|'back', light=1.0, ...)
  pov_hand(c, x, y, sc, t, ang, flashlight=True)        # your hand holding the flashlight, from the bottom of frame
"""
import math
import skia
from lib import *


def P(pts, closed=True):
    """Path through points; a point (x, y, 'q', cx, cy) means quadratic curve to (x, y) with control (cx, cy)."""
    p = skia.Path()
    p.moveTo(pts[0][0], pts[0][1])
    for q in pts[1:]:
        if len(q) == 5:
            p.quadTo(q[3], q[4], q[0], q[1])
        else:
            p.lineTo(q[0], q[1])
    if closed:
        p.close()
    return p


def _shade(col_, light):
    return mix('#000000', col_, max(0.0, min(1.0, light)))


def _limb(x0, y0, x1, y1, x2, y2, w0, w1, w2):
    """Tapered limb outline through shoulder/elbow/wrist with widths w0, w1, w2."""
    def nrm(ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        l = math.hypot(dx, dy) or 1
        return -dy / l, dx / l
    n0 = nrm(x0, y0, x1, y1)
    n2 = nrm(x1, y1, x2, y2)
    n1 = ((n0[0] + n2[0]) / 2, (n0[1] + n2[1]) / 2)
    L = [(x0 + n0[0] * w0, y0 + n0[1] * w0), (x1 + n1[0] * w1, y1 + n1[1] * w1), (x2 + n2[0] * w2, y2 + n2[1] * w2)]
    R = [(x2 - n2[0] * w2, y2 - n2[1] * w2), (x1 - n1[0] * w1, y1 - n1[1] * w1), (x0 - n0[0] * w0, y0 - n0[1] * w0)]
    p = skia.Path()
    p.moveTo(*L[0]); p.quadTo(L[1][0], L[1][1], L[2][0], L[2][1])
    p.quadTo(x2 + (x2 - x1) * 0.08, y2 + (y2 - y1) * 0.08, R[0][0], R[0][1])
    p.quadTo(R[1][0], R[1][1], R[2][0], R[2][1])
    p.close()
    return p


def _fingers(c, wx, wy, ang, length, width, colr, n=4, spread=10, curl=0.0):
    """Long thin fingers from a wrist at (wx, wy) pointing at angle ang (degrees, 90 = down)."""
    for k in range(n):
        a = math.radians(ang + (k - (n - 1) / 2) * spread)
        l = length * (0.82 + 0.18 * math.sin(k * 1.7 + 1))
        mx = wx + math.cos(a) * l * 0.55
        my = wy + math.sin(a) * l * 0.55
        a2 = a + curl
        ex = mx + math.cos(a2) * l * 0.5
        ey = my + math.sin(a2) * l * 0.5
        c.drawPath(P([(wx, wy), (ex, ey, 'q', mx, my)], closed=False), paint(colr, 1, stroke=width))
        c.drawCircle(mx, my, width * 0.62, paint(colr))   # knuckle


# ====================================================================== the Visitor
V = dict(cardigan='#4b3423', rib='#3a2819', trousers='#1e1b18', skin='#bbb4a6', hair='#8e8b85', scalp='#a59f94',
         shoe='#0d0c0b', shirt='#5c5a52', button='#c9b48a')


def visitor(c, x, y, h, t, view='back', light=1.0, arm=0.0, head_turn=0.0, rim='#e8f5d0', rim_a=0.7, alpha=1.0,
            blur=0.0, sway=1.0, grin=0.6):
    """The Visitor: Hale's clothes and hair on something too tall and too thin.
    (x, y) = between its feet on the floor, h = height in px. arm: 0..1 raises its right arm to knock (back view).
    head_turn: 0 = facing its view, 1 = head turned 180° (the back view shows its face over its shoulder)."""
    s = h / 1000.0
    L = lambda col_: _shade(col_, light)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if alpha < 1:
        c.saveLayerAlpha(skia.Rect(-600, -1100, 600, 100), int(255 * alpha))
    bl = blur / s if blur else 0
    sw = sway * (4 * math.sin(t * 0.9) + 1.5 * math.sin(t * 2.3))   # barely moving, never still
    c.rotate(sw * 0.15)

    # ---- geometry
    hip_y, sh_y, neck_y = -470, -800, -845
    head_c = (0, -930)
    # arms: shoulder -> elbow -> wrist; right arm can lift to knock
    la = [(-80, sh_y + 14), (-100, -600), (-96, -380)]
    ra_down = [(80, sh_y + 14), (100, -600), (96, -380)]
    ra_up = [(80, sh_y + 14), (150, -690), (128, -900)]
    ra = [(lerp(a[0], b[0], arm), lerp(a[1], b[1], arm)) for a, b in zip(ra_down, ra_up)]

    def silhouette():
        """All body shapes in one path (for the rim-light pass)."""
        p = skia.Path()
        p.addPath(_body_path(hip_y, sh_y, neck_y))
        p.addPath(_limb(*la[0], *la[1], *la[2], 24, 20, 15))
        p.addPath(_limb(*ra[0], *ra[1], *ra[2], 24, 20, 15))
        p.addPath(_legs_path(hip_y))
        p.addOval(skia.Rect(head_c[0] - 50, head_c[1] - 68, head_c[0] + 50, head_c[1] + 64))
        return p

    # ---- rim pass (backlit edge), then a soft halo
    if rim_a > 0:
        sil = silhouette()
        c.save(); c.translate(7, -6); c.drawPath(sil, paint(rim, rim_a * 0.9, blur=bl + 2)); c.restore()
        c.save(); c.translate(-5, -4); c.drawPath(sil, paint(rim, rim_a * 0.35, blur=bl + 6)); c.restore()

    # ---- shoes + legs
    for sx_ in (-1, 1):
        c.drawOval(skia.Rect(sx_ * 42 - 40, -24, sx_ * 42 + 44, 4), paint(L(V['shoe']), 1, blur=bl))
    c.drawPath(_legs_path(hip_y), paint(L(V['trousers']), 1, blur=bl))
    c.drawLine(0, hip_y + 10, 0, -40, paint('#000000', 0.5, stroke=6, blur=bl))       # gap between legs
    for sx_ in (-1, 1):  # trouser crease highlight
        c.drawLine(sx_ * 36, hip_y + 40, sx_ * 42, -60, paint(L('#3a3630'), 0.5, stroke=4, blur=bl))

    # ---- cardigan body
    body = _body_path(hip_y, sh_y, neck_y)
    c.drawPath(body, paint(L(V['cardigan']), 1, blur=bl))
    g = skia.Paint(AntiAlias=True)
    g.setShader(lin_shader(-120, 0, 120, 0, [('#000000', 0.45), ('#000000', 0.0), ('#000000', 0.5)]))
    c.drawPath(body, g)
    c.save(); c.clipPath(body, doAntiAlias=True)
    for k in range(-5, 6):                       # fine knit ribs (vertical) + hem band
        xx = k * 15
        c.drawLine(xx, sh_y + 30, xx * 1.12, -405, paint(L(V['rib']), 0.35, stroke=3, blur=bl))
    c.drawRect(skia.Rect(-140, -436, 140, -400), paint(L(V['rib']), 0.9, blur=bl))
    for sx_ in (-1, 1):                          # drape creases from the shoulder blades
        c.drawPath(P([(sx_ * 60, sh_y + 40), (sx_ * 30, -520, 'q', sx_ * 70, -660)], closed=False),
                   paint('#000000', 0.22, stroke=7, blur=4))
    if view == 'front':
        c.drawRect(skia.Rect(-22, sh_y + 20, 22, -420), paint(L(V['shirt']), 1, blur=bl))   # open front
        c.drawLine(-24, sh_y + 20, -30, -410, paint(L(V['rib']), 1, stroke=10))
        c.drawLine(24, sh_y + 20, 30, -410, paint(L(V['rib']), 1, stroke=10))
        for k in range(5):
            c.drawCircle(-34, -720 + k * 70, 7, paint(L(V['button'])))
    else:
        c.drawLine(0, sh_y + 30, 0, -420, paint('#000000', 0.25, stroke=8))           # back seam
    c.restore()
    # hunch: a darker curve across the upper back
    c.drawPath(P([(-100, sh_y + 30), (100, sh_y + 30, 'q', 0, sh_y - 10)], closed=False),
               paint('#000000', 0.25, stroke=14, blur=6))

    # ---- neck + head
    c.drawPath(P([(-17, neck_y + 40), (-15, neck_y - 40), (15, neck_y - 40), (17, neck_y + 40)]),
               paint(L(mix(V['skin'], '#000000', 0.25)), 1, blur=bl))
    c.save()
    c.translate(head_c[0], head_c[1] + 40)
    tw = 6 * math.sin(t * 7.3) * math.sin(t * 1.3) ** 8          # rare small twitch
    c.rotate(-4 + tw + (14 if view == 'back' else 0) * head_turn)
    c.translate(-head_c[0], -(head_c[1] + 40))
    face_front = (view == 'front') != (head_turn > 0.5)
    _head(c, head_c, L, bl, face_front, t, grin)
    c.restore()

    # ---- arms over the body edges (no gaps at the shoulders)
    _draw_arm(c, la, L, bl, view, t, side=-1)
    _draw_arm(c, ra, L, bl, view, t, side=1, knocking=arm > 0.5)

    if alpha < 1:
        c.restore()
    c.restore()


def _body_path(hip_y, sh_y, neck_y):
    return P([(-26, neck_y + 8), (-92, sh_y + 22, 'q', -70, sh_y - 2), (-80, -620, 'q', -92, -720),
              (-92, -400, 'q', -70, -520), (92, -400), (80, -620, 'q', 70, -520), (92, sh_y + 22, 'q', 92, -720),
              (26, neck_y + 8, 'q', 70, sh_y - 2)])


def _legs_path(hip_y):
    p = skia.Path()
    p.addPath(P([(-66, hip_y + 40), (-6, hip_y + 40), (-26, -22, 'q', -14, -240), (-58, -22), (-66, hip_y + 40, 'q', -56, -240)]))
    p.addPath(P([(66, hip_y + 40), (6, hip_y + 40), (26, -22, 'q', 14, -240), (58, -22), (66, hip_y + 40, 'q', 56, -240)]))
    return p


def _draw_arm(c, pts, L, bl, view, t, side, knocking=False):
    (x0, y0), (x1, y1), (x2, y2) = pts
    arm_p = _limb(x0, y0, x1, y1, x2, y2, 24, 20, 15)
    c.drawPath(arm_p, paint(L(mix(V['cardigan'], '#000000', 0.12)), 1, blur=bl))
    c.drawPath(arm_p, paint('#000000', 0.35, stroke=4, blur=bl + 1))      # outline separates arm from body
    # cuff
    dx, dy = x2 - x1, y2 - y1
    l = math.hypot(dx, dy) or 1
    cx_, cy_ = x2 - dx / l * 16, y2 - dy / l * 16
    c.drawLine(cx_ - dy / l * 17, cy_ + dx / l * 17, cx_ + dy / l * 17, cy_ - dx / l * 17,
               paint(L(V['rib']), 1, stroke=18, cap=False))
    ang = math.degrees(math.atan2(dy, dx))
    twitch = 6 * math.sin(t * 3.1 + side) * (0.5 + 0.5 * math.sin(t * 0.7))
    if knocking:
        c.drawCircle(x2, y2 - 4, 22, paint(L(V['skin']), 1, blur=bl))             # a bony fist
        for k in range(4):
            c.drawCircle(x2 - 14 + k * 9, y2 - 22, 7, paint(L(mix(V['skin'], '#000000', 0.15))))
    else:
        c.drawPath(P([(x2 - 14, y2), (x2 + 14, y2), (x2 + 12, y2 + 34), (x2 - 12, y2 + 34)]),
                   paint(L(V['skin']), 1, blur=bl))
        _fingers(c, x2, y2 + 30, ang + twitch, 120, 8.5, L(V['skin']), n=4, spread=7, curl=0.25 * side)


def _head(c, hc, L, bl, face_front, t, grin):
    hx, hy = hc
    skull = skia.Rect(hx - 50, hy - 68, hx + 50, hy + 64)
    c.drawOval(skull, paint(L(V['skin']), 1, blur=bl))
    shade = skia.Paint(AntiAlias=True)
    shade.setShader(rad_shader(hx - 14, hy - 24, 90, [('#000000', 0.0), ('#000000', 0.55)]))
    c.drawOval(skull, shade)
    r = rng_for(9)
    if not face_front:
        # back of the head: thin grey hair over a pale crown, strands to the collar
        c.drawOval(skia.Rect(hx - 52, hy - 70, hx + 52, hy + 52), paint(L(V['hair']), 1, blur=bl))
        c.drawOval(skia.Rect(hx - 26, hy - 66, hx + 22, hy - 26), paint(L(V['scalp']), 0.85, blur=bl + 3))
        for k in range(34):
            x0 = hx - 46 + k * 2.8
            c.drawPath(P([(x0, hy - 50 + r.random() * 30), (x0 + r.random() * 8 - 4, hy + 62 + r.random() * 18,
                                                            'q', x0 + r.random() * 10 - 5, hy + 10)], closed=False),
                       paint(L(mix(V['hair'], '#ffffff', 0.15 * r.random())), 0.8, stroke=1.6))
        c.drawOval(skia.Rect(hx - 60, hy - 10, hx - 44, hy + 22), paint(L(V['skin']), 1))      # ears
        c.drawOval(skia.Rect(hx + 44, hy - 10, hx + 60, hy + 22), paint(L(V['skin']), 1))
        return
    # face: thin hair combed over, hollow uneven eyes, pinpoint pupils, a long thin grin
    c.drawPath(P([(hx - 52, hy - 30), (hx + 52, hy - 34, 'q', hx, hy - 96), (hx + 40, hy - 50, 'q', hx + 10, hy - 70),
                  (hx - 40, hy - 46, 'q', hx - 10, hy - 66)]), paint(L(V['hair']), 1, blur=bl))
    for k in range(14):
        x0 = hx - 40 + k * 6
        c.drawLine(x0, hy - 56, x0 + 3, hy - 28 + r.random() * 12, paint(L(V['hair']), 0.8, stroke=1.6))
    for dx, rx, ry in ((-19, 13, 11), (20, 11, 14)):
        c.drawOval(skia.Rect(hx + dx - rx - 6, hy - 8 - ry - 4, hx + dx + rx + 6, hy - 8 + ry + 8),
                   paint('#2a2622', 0.7, blur=5))
        c.drawOval(skia.Rect(hx + dx - rx, hy - 8 - ry, hx + dx + rx, hy - 8 + ry), paint('#030303'))
        c.drawCircle(hx + dx + 1.5, hy - 7, 2.2, paint('#ffffff'))
        glow(c, hx + dx + 1.5, hy - 7, 9, '#ffffff', 0.35)
    c.drawPath(P([(hx, hy + 2), (hx + 5, hy + 22), (hx - 4, hy + 22)]), paint('#2a2622', 0.6, blur=2))   # nose
    m = 4 + 14 * grin
    c.drawPath(P([(hx - 38, hy + 34), (hx + 38, hy + 31, 'q', hx, hy + 34 + m * 1.6),
                  (hx - 38, hy + 34, 'q', hx, hy + 34 + m * 0.45)]), paint('#050505'))
    for k in range(6):  # creases at the mouth corners and under the eyes
        c.drawLine(hx - 44 + k * 1.5, hy + 22 + k * 3, hx - 40, hy + 40, paint('#000000', 0.15, stroke=1.4))
        c.drawLine(hx + 44 - k * 1.5, hy + 20 + k * 3, hx + 40, hy + 38, paint('#000000', 0.15, stroke=1.4))


# ====================================================================== Mr. Hale (the real manager)
H_ = dict(cardigan='#5a3f29', rib='#463020', trousers='#3a3a40', skin='#d2b49a', hair='#c8c5bf', shirt='#d8d2c0',
          glasses='#2a2a2a', shoe='#1a1410')


def hale(c, x, y, h, t, view='front', light=1.0, rim='#ffd49a', rim_a=0.6, key=True):
    """Mr. Hale: short, a little stooped, round glasses, kind tired face, the same brown cardigan, keys on his belt.
    Normal human proportions (the Visitor's are wrong)."""
    s = h / 1000.0
    L = lambda col_: _shade(col_, light)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.rotate(2 + 1.5 * math.sin(t * 1.1))
    # rim
    body = P([(-60, -790), (-150, -740, 'q', -120, -790), (-165, -380, 'q', -175, -560), (165, -380),
              (150, -740, 'q', 175, -560), (60, -790, 'q', 120, -790)])
    arms = [_limb(sx_ * 135, -730, sx_ * 172, -560, sx_ * 158, -410, 38, 33, 27) for sx_ in (-1, 1)]
    if rim_a > 0:
        sil = skia.Path(); sil.addPath(body); [sil.addPath(a_) for a_ in arms]
        sil.addOval(skia.Rect(-80, -965, 80, -780))
        c.save(); c.translate(8, -6); c.drawPath(sil, paint(rim, rim_a, blur=3)); c.restore()
    # legs + shoes
    for sx_ in (-1, 1):
        c.drawPath(P([(sx_ * 20, -420), (sx_ * 120, -420), (sx_ * 105, -30), (sx_ * 35, -30)]), paint(L(H_['trousers'])))
        c.drawOval(skia.Rect(sx_ * 70 - 60, -40, sx_ * 70 + 60, 4), paint(L(H_['shoe'])))
    # body (wider, softer)
    c.drawPath(body, paint(L(H_['cardigan'])))
    g = skia.Paint(AntiAlias=True)
    g.setShader(lin_shader(-160, 0, 160, 0, [('#000000', 0.35), ('#000000', 0.0), ('#000000', 0.4)]))
    c.drawPath(body, g)
    if view == 'front':
        c.drawPath(P([(-50, -790), (50, -790), (24, -390), (-24, -390)]), paint(L(H_['shirt'])))
        for k in range(5):
            c.drawCircle(-48, -700 + k * 70, 8, paint(L('#c9b48a')))
        if key:  # the key ring on his belt: the point of the P.S.
            c.drawCircle(110, -420, 22, paint(L('#c9a24a'), 1, stroke=5))
            for k in range(3):
                c.drawLine(110, -400, 100 + k * 12, -340, paint(L('#d8c08a'), 1, stroke=7))
    # arms
    for sx_, a_ in zip((-1, 1), arms):
        c.drawPath(a_, paint(L(mix(H_['cardigan'], '#000000', 0.1))))
        c.drawPath(a_, paint('#000000', 0.3, stroke=4))
        c.drawLine(sx_ * 158 - 26, -418, sx_ * 158 + 26, -418, paint(L(H_['rib']), 1, stroke=16, cap=False))
        hand = P([(sx_ * 158 - 24, -404), (sx_ * 158 + 24, -404), (sx_ * 158 + 20, -330, 'q', sx_ * 158 + 30, -360),
                  (sx_ * 158 - 20, -330, 'q', sx_ * 158, -312), (sx_ * 158 - 24, -404, 'q', sx_ * 158 - 30, -360)])
        c.drawPath(hand, paint(L(H_['skin'])))
        c.drawPath(hand, paint('#000000', 0.25, stroke=3))
    # head
    hx, hy = 0, -870
    c.drawRect(skia.Rect(-28, -800, 28, -770), paint(L(mix(H_['skin'], '#000000', 0.2))))
    c.drawOval(skia.Rect(hx - 80, hy - 95, hx + 80, hy + 90), paint(L(H_['skin'])))
    sh = skia.Paint(AntiAlias=True)
    sh.setShader(rad_shader(hx - 20, hy - 30, 140, [('#000000', 0.0), ('#000000', 0.45)]))
    c.drawOval(skia.Rect(hx - 80, hy - 95, hx + 80, hy + 90), sh)
    if view == 'front':
        c.drawPath(P([(hx - 82, hy - 10), (hx - 60, hy - 90, 'q', hx - 90, hy - 70), (hx + 60, hy - 90, 'q', hx, hy - 120),
                      (hx + 82, hy - 10, 'q', hx + 90, hy - 70), (hx + 66, hy - 40), (hx - 66, hy - 40, 'q', hx, hy - 70)]),
               paint(L(H_['hair'])))
        for dx in (-32, 32):
            c.drawCircle(hx + dx, hy, 24, paint(L(H_['glasses']), 1, stroke=5))
            c.drawCircle(hx + dx, hy + 2, 6, paint('#1a1a1a'))
            c.drawCircle(hx + dx - 8, hy - 8, 6, paint('#ffffff', 0.4))
        c.drawLine(hx - 8, hy, hx + 8, hy, paint(L(H_['glasses']), 1, stroke=4))
        c.drawPath(P([(hx, hy + 6), (hx + 10, hy + 36), (hx - 6, hy + 38)]), paint('#000000', 0.18, blur=2))
        c.drawPath(P([(hx - 26, hy + 56), (hx + 26, hy + 56, 'q', hx, hy + 66)], closed=False), paint('#5a3a30', 1, stroke=5))
        for dx in (-30, 30):  # bushy grey eyebrows + smile lines: a kind, tired face
            c.drawLine(hx + dx - 18, hy - 34, hx + dx + 18, hy - 36, paint(L(H_['hair']), 1, stroke=9))
            c.drawPath(P([(hx + dx * 1.6, hy + 30), (hx + dx * 1.4, hy + 62, 'q', hx + dx * 1.8, hy + 48)], closed=False),
                       paint('#000000', 0.18, stroke=3))
    else:
        c.drawOval(skia.Rect(hx - 82, hy - 96, hx + 82, hy + 70), paint(L(H_['hair'])))
    c.restore()


# ====================================================================== your hand + flashlight (POV)
def pov_hand(c, x, y, sc, t, ang=-20, on=1.0, skin='#3a2a20', sleeve='#1f2a3a'):
    """Your right hand holding a black flashlight, entering from the bottom of the frame. (x, y) = lens of the light."""
    c.save()
    c.translate(x, y)
    c.rotate(ang + 1.5 * math.sin(t * 2.1))
    c.scale(sc, sc)
    shake_ = 2 * math.sin(t * 13) * math.sin(t * 3.3)
    c.translate(shake_, 0)
    # sleeve + forearm toward the bottom
    c.drawPath(P([(-70, 330), (80, 330), (130, 900), (-150, 900)]), paint(sleeve))
    c.drawLine(-60, 340, 70, 340, paint(mix(sleeve, '#ffffff', 0.12), 1, stroke=18))
    # flashlight body
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-34, -20, 34, 300), 18, 18), paint('#111214'))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-46, -60, 46, 10), 12, 12), paint('#1b1c20'))
    c.drawLine(-20, 20, -20, 280, paint('#ffffff', 0.08, stroke=6))
    for k in range(6):
        c.drawLine(-34, 120 + k * 16, 34, 120 + k * 16, paint('#000000', 0.6, stroke=4))
    if on > 0:
        c.drawOval(skia.Rect(-40, -66, 40, -50), paint('#fff4d8', on))
        glow(c, 0, -60, 90, '#fff4d8', 0.5 * on)
    # fist wrapped around it
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-70, 140, 70, 330), 50, 50), paint(skin))
    for k in range(4):
        yy = 150 + k * 44
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-80, yy, 10, yy + 40), 20, 20), paint(mix(skin, '#000000', 0.12)))
        c.drawLine(-70, yy + 6, 0, yy + 6, paint('#ffcf8f', 0.25, stroke=3))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(20, 100, 66, 220), 22, 22), paint(mix(skin, '#ffffff', 0.05)))  # thumb
    c.restore()
