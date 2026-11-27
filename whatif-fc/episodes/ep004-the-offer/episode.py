"""ep004 — The Offer. Next season: Teo's club offers El Viejo the goalkeeper-coach job, on one condition: retire.
He slides the contract back... after tearing off one corner (the plant: 'TRAINING 7:00').
Next morning at 7 a.m. he turns up at Teo's training anyway, with a bag of balls.
Scene functions take GLOBAL time t. Return value = white flash amount (0..1)."""
import math
import skia
from lib import *
from shots import zoom, bokeh, back_view, chain_fence

# The Director: Teo's club's sporting director (new, original). Long dark coat, short grey hair, no badge.
KITS['director'] = dict(jersey='#15181d', sleeve='#15181d', shorts='#101216', socks='#101216', skin='#3b2b22',
                        glove=None, trim=None, hair='#a9a9a6', beard=None, streak=None, coat=True)

PAPER = '#e9e3d6'
VSLEEVE = '#262a31'      # El Viejo's charcoal sleeve
VSKIN = '#3a2a20'
DSLEEVE = '#15181d'      # the Director's coat sleeve
DSKIN = '#3b2b22'
SKIN_LIT = '#ffcf8f'

# paper coords: 600 x 800 sheet centred on the origin. The bottom-right corner tears off along this zigzag.
TEAR = [(300, 200), (276, 226), (286, 250), (250, 272), (258, 298), (218, 316), (228, 342), (186, 356), (192, 380),
        (150, 392), (120, 400)]


def _poly(pts):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    return p


def _text(c, s, x, y, size, colr='#1a1a1a', a=1.0, center=False):
    f = skia.Font(FONT, size)
    if center:
        x -= f.measureText(s) / 2
    c.drawString(s, x, y, f, paint(colr, a))


def scrap_local(c, a=1.0, shadow=True):
    """The torn corner, in paper coords: 'TRAINING 7:00'."""
    pts = TEAR + [(300, 400)]
    if shadow:  # a loose scrap (torn off); attached to the sheet it is just the printed text
        c.drawPath(_poly(pts), paint('#000000', 0.35 * a, blur=10))
        c.drawPath(_poly(pts), paint(PAPER, a))
    _text(c, 'TRAINING', 224, 352, 22, '#3a3a3a', a)
    _text(c, '7:00', 222, 392, 40, '#111111', a)


def contract(c, cx, cy, ang, sc=1.0, torn=False, scrap=None, blur=0.0, a=1.0):
    """Offer sheet. torn: corner missing. scrap=(dx, dy, rot, alpha) draws the torn corner displaced."""
    c.save()
    c.translate(cx, cy)
    c.rotate(ang)
    c.scale(sc, sc)
    if torn:
        body = [(-300, -400), (300, -400)] + TEAR + [(-300, 400)]
    else:
        body = [(-300, -400), (300, -400), (300, 400), (-300, 400)]
    path = _poly(body)
    c.save(); c.translate(14, 22); c.drawPath(path, paint('#000000', 0.55 * a, blur=22)); c.restore()
    c.save(); c.translate(-4, -5); c.drawPath(path, paint(SKIN_LIT, 0.55 * a, blur=3)); c.restore()
    c.drawPath(path, paint(PAPER, a, blur=blur))
    # lamp falloff across the sheet
    p = skia.Paint(AntiAlias=True)
    p.setShader(lin_shader(-300, -400, 300, 400, [('#000000', 0.0), ('#000000', 0.22 * a)]))
    c.drawPath(path, p)
    ink = '#1a1a1a'
    _text(c, 'OFFER', 0, -300, 96, ink, a, center=True)
    c.drawLine(-240, -270, 240, -270, paint(ink, 0.6 * a, stroke=3))
    _text(c, 'ROLE:', -240, -180, 40, '#555555', a)
    _text(c, 'GOALKEEPER COACH', -130, -180, 48, ink, a)
    _text(c, 'START:', -240, -100, 40, '#555555', a)
    _text(c, 'MONDAY', -130, -100, 48, ink, a)
    _text(c, 'CONDITION:', -240, -20, 40, '#555555', a)
    _text(c, 'PLAYER RETIRES', -240, 40, 58, '#7a1018', a)
    for k in range(3):
        c.drawLine(-240, 100 + k * 34, 200 - k * 60, 100 + k * 34, paint('#8a8a8a', 0.5 * a, stroke=6))
    _text(c, 'X', -240, 250, 54, ink, a)
    c.drawLine(-200, 255, 140, 255, paint(ink, 0.8 * a, stroke=3))
    _text(c, 'SIGNATURE', -200, 290, 26, '#666666', a)
    if not torn:
        scrap_local(c, a, shadow=False)
    elif scrap is not None:
        dx, dy, rot, sa = scrap
        c.save()
        c.translate(240 + dx, 330 + dy); c.rotate(rot); c.translate(-240, -330)
        scrap_local(c, a * sa)
        c.restore()
    c.restore()


def pen(c, x, y, ang, sc=1.0, blur=0.0):
    c.save()
    c.translate(x, y); c.rotate(ang); c.scale(sc, sc)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-130 + 14, -14 + 18, 130 + 14, 14 + 18), 14, 14),
                paint('#000000', 0.5, blur=10))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-130, -14, 130, 14), 14, 14), paint('#0d0d10', 1, blur=blur))
    c.drawLine(-120, -8, 110, -8, paint(SKIN_LIT, 0.5, stroke=3, blur=blur))
    c.drawRect(skia.Rect(-110, -20, -30, -12), paint('#c9a24a', 1, blur=blur))      # gold clip
    tip = _poly([(130, -10), (165, 0), (130, 10)])
    c.drawPath(tip, paint('#b8b8b8', 1, blur=blur))
    c.restore()


def desk(c, t, rain_shadow=True):
    c.drawRect(skia.Rect(-200, -200, W + 200, H + 200), paint('#150f0c'))
    r = rng_for(401)
    for i in range(46):
        y = -100 + i * 48 + r.random() * 20
        c.drawLine(-100, y, W + 100, y + r.random() * 40 - 20, paint('#201713', 0.9, stroke=3 + r.random() * 4))
    glow(c, 820, 420, 900, '#ffbf70', 0.26)
    if rain_shadow:  # streaks from the rainy window drifting across the desk
        for k in range(16):
            rr = rng_for(410 + k)
            x = rr.random() * W
            y = ((t * (160 + 80 * rr.random()) + rr.random() * 2400) % 2400) - 300
            c.drawLine(x, y, x + 6, y + 120 + 80 * rr.random(), paint('#000000', 0.16, stroke=10, blur=8))


def arm_top(c, x0, y0, x1, y1, sleeve, skin=VSKIN, w=150, tape=None, fingers=1.0, blur=0.0, rim=SKIN_LIT):
    """Forearm seen from above, from (x0,y0) (off screen) to the hand at (x1,y1).
    fingers: 1 = fist/knuckles, 0 = open flat palm (fingers extended)."""
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    L = math.hypot(x1 - x0, y1 - y0)
    c.save()
    c.translate(x1, y1)
    c.rotate(ang)
    # forearm toward -x
    c.drawLine(-L, -10, -40, -10, paint(rim, 0.8, stroke=w * 0.95, blur=blur))
    c.drawLine(-L, 0, -40, 0, paint(skin, 1, stroke=w * 0.9, blur=blur))
    c.drawLine(-L - 200, 0, -L * 0.42, 0, paint(sleeve, 1, stroke=w * 1.3, blur=blur, cap=False))
    c.drawLine(-L * 0.42 - 6, 0, -L * 0.42, 0, paint(mix(sleeve, '#ffffff', 0.15), 1, stroke=w * 1.3, blur=blur, cap=False))
    if tape:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-210, -w * 0.5, -70, w * 0.5), 14, 14), paint('#ece8df', 1, blur=blur))
        for k in range(3):
            c.drawLine(-200 + k * 46, -w * 0.45, -200 + k * 46, w * 0.45, paint('#b9b3a8', 0.7, stroke=4, blur=blur))
        c.save(); c.translate(-140, 0); c.rotate(90)
        f = skia.Font(FONT, w * 0.62)
        tw = f.measureText(tape)
        c.drawString(tape, -tw / 2, w * 0.22, f, paint('#111111', 0.9, blur=blur * 0.5))
        c.restore()
    # palm
    palm = skia.RRect.MakeRectXY(skia.Rect(-70, -w * 0.58, 70, w * 0.58), 44, 44)
    c.save(); c.translate(6, -8); c.drawRRect(palm, paint(rim, 0.75, blur=blur)); c.restore()
    c.drawRRect(palm, paint(skin, 1, blur=blur))
    # fingers
    fl = lerp(120, 34, fingers)
    for k in range(4):
        fy = -w * 0.45 + k * w * 0.3
        rect = skia.Rect(50, fy - 15, 50 + fl - abs(k - 1.5) * 10, fy + 15)
        c.drawRRect(skia.RRect.MakeRectXY(rect, 15, 15), paint(mix(skin, '#000000', 0.12), 1, blur=blur))
        c.drawLine(58, fy - 11, 40 + fl - abs(k - 1.5) * 10, fy - 11, paint(rim, 0.35, stroke=4, blur=blur))
    # thumb
    th = skia.RRect.MakeRectXY(skia.Rect(-20, -w * 0.62 - 30, 70, -w * 0.62 + 4), 18, 18)
    c.drawRRect(th, paint(skin, 1, blur=blur))
    c.restore()


# =============================================================== S1 0-1.6 the slam
def s1(c, t, f):
    lt = t
    T_HIT = 0.35
    amp = 18 * math.exp(-(lt - T_HIT) * 7) if lt > T_HIT else 0
    sx, sy = shake(lt, amp)
    c.save()
    c.translate(sx, sy)
    zoom(c, 1.0 + 0.06 * ease(seg(lt, T_HIT, 1.6)), 540, 960)
    desk(c, t)
    contract(c, 540, 960, -3, 0.88)
    u = ease_in(seg(lt, 0.0, T_HIT))
    sc = lerp(1.9, 1.0, u)            # hand comes down from near the camera
    hx, hy = lerp(820, 680, u), lerp(300, 1060, u)
    pen(c, hx - 30 * sc, hy + 40 * sc, -28, sc, blur=6 * (1 - u) if lt < T_HIT else 0)
    lift = ease(seg(lt, 0.8, 1.5))     # hand lifts off, leaving the pen
    arm_top(c, 1400, -300, hx + 60 * lift, hy - 120 * lift, DSLEEVE, DSKIN, w=140 * sc, fingers=0.9,
            blur=8 * (1 - u) if lt < T_HIT else 0)
    c.restore()
    rain(c, t, n=24, seed=402, a=0.12, width=5, length=140, blur=6, speed=3000)
    return 0.3 * math.exp(-(lt - T_HIT) * 10) if lt > T_HIT else 0.0


# =============================================================== S1b 1.6-2.8 he pushes it back
def s1b(c, t, f):
    lt = t - 1.6
    u = ease_out(seg(lt, 0.05, 0.6))
    c.save()
    zoom(c, 1.0, 540, 900)
    desk(c, t)
    cy = lerp(1000, 760, u)
    ang = lerp(-3, 7, u)
    contract(c, 540, cy, ang, 0.88, blur=6 * math.sin(math.pi * u))
    pen(c, 620 + 40 * u, cy + 130, -28 + 10 * u, 0.9)
    # El Viejo's hand on the bottom edge of the sheet, TEO tape on the wrist
    arm_top(c, 380, 2300, 520, cy + 420, VSLEEVE, VSKIN, w=170, tape='TEO', fingers=0.6)
    c.restore()
    rain(c, t, n=24, seed=403, a=0.12, width=5, length=140, blur=6, speed=3000)
    return 0.25 * math.exp(-lt * 12)


# =============================================================== the office (side view), shared by S2 and S7b
WIN = (60, 300, 1020, 1060)


def office_window(c, t, inner_zoom=1.0, teo_dive=None):
    """The big window behind the desk: floodlit training pitch, Teo tiny in goal."""
    x0, y0, x1, y1 = WIN
    c.save()
    c.clipRect(skia.Rect(x0, y0, x1, y1))
    zoom(c, inner_zoom, 540, 760)
    sky(c, '#02040a', '#0d1828', y0, 820)
    floodlight(c, 200, 420, t, 0.75, beam_to=(420, 1000))
    floodlight(c, 880, 400, t, 0.75, beam_to=(700, 1000))
    cam = Cam(horizon=820, F=900, h=6.0)
    pitch(c, cam, light=(540, 930, 300))
    pline(c, cam, [(-30, 30), (30, 30)])
    pline(c, cam, [(-9.16, 30), (-9.16, 24.5), (9.16, 24.5), (9.16, 30)])
    goal_frame(c, cam, 30, depth=2.0)
    kx, ky = cam.p(0.0, 29.6)
    s = cam.s(29.6, 1.9) / 190
    pz = dict(POSES['ready'])
    pz['uaL'] += 8 * math.sin(t * 5); pz['uaR'] -= 8 * math.sin(t * 5)
    figure(c, pz, kx + 4 * math.sin(t * 2), ky - 80 * s, s, kit='son', front=True, rim_a=0.7)
    rain(c, t, n=160, seed=421, a=0.2)
    c.restore()
    # glass: droplets + frame
    r = rng_for(422)
    for k in range(70):
        dx = x0 + r.random() * (x1 - x0)
        dy = y0 + ((r.random() * (y1 - y0) + t * 40 * r.random()) % (y1 - y0))
        rr = 3 + r.random() * 7
        c.drawCircle(dx, dy, rr, paint('#cfe3f5', 0.18))
        c.drawCircle(dx - rr * 0.3, dy - rr * 0.3, rr * 0.35, paint('#ffffff', 0.25))
    c.drawRect(skia.Rect(x0, y0, x1, y1), paint('#0b0908', 1, stroke=26))
    c.drawLine((x0 + x1) / 2, y0, (x0 + x1) / 2, y1, paint('#0b0908', 1, stroke=16))


SIT = dict(torso=178, head=4, uaL=60, faL=95, uaR=70, faR=100, thL=86, shL=6, thR=90, shR=8)
STAND = dict(POSES['stand'])


def office(c, t, viejo=None, director=True, paper_x=None, door=0.0):
    """Side view across the desk. viejo = (x, pose, face) or None."""
    c.drawRect(skia.Rect(-200, -200, W + 200, H + 200), paint('#0a0908'))
    office_window(c, t)
    glow(c, 540, 700, 560, '#9fc4e6', 0.10)
    # door on the far left: a wedge of corridor light when it opens
    if door > 0:
        c.drawRect(skia.Rect(-40, 520, -40 + 150 * door, 1300), paint('#ffcf8a', 0.75))
        glow(c, 30, 1000, 300, '#ffcf8a', 0.25 * door)
    # lamp on the desk
    glow(c, 820, 1080, 380, '#ffbf70', 0.32)
    c.drawLine(820, 1180, 840, 1060, paint('#1a1512', 1, stroke=10))
    c.drawPath(_poly([(780, 1070), (900, 1070), (870, 1010), (810, 1010)]), paint('#2a211b'))
    if director:
        figure(c, SIT, 800, 1170, 2.9, kit='director', face=-1, rim=(-4, -3), rim_col='#ffbf70', rim_a=0.75)
    if viejo:
        vx, vpose, vface = viejo
        figure(c, vpose, vx, 1170, 2.9, kit='viejo',
               face=vface, rim=(4, -3), rim_col='#ffbf70', rim_a=0.8)
    # desk (front panel hides the legs)
    c.drawRect(skia.Rect(-100, 1180, W + 100, 1205), paint('#2a1f19'))
    c.drawLine(-100, 1180, W + 100, 1180, paint('#ffbf70', 0.35, stroke=3))
    c.drawRect(skia.Rect(-100, 1205, W + 100, H + 100), paint('#110c0a'))
    g = skia.Paint()
    g.setShader(lin_shader(0, 1205, 0, 1700, [('#ffbf70', 0.08), ('#000000', 0.0)]))
    c.drawRect(skia.Rect(-100, 1205, W + 100, 1700), g)
    if paper_x is not None:  # the contract lying flat on the desk, seen edge-on
        c.drawLine(paper_x - 70, 1176, paper_x + 70, 1176, paint(PAPER, 1, stroke=6))


# =============================================================== S2 2.8-4.85 whip-in: the office
def s2(c, t, f):
    lt = t - 2.8
    c.save()
    zoom(c, 1.0 + 0.45 * (1 - ease_out(lt / 0.45)) + 0.05 * lt / 2.0, 540, 900)
    office(c, t, viejo=(280, SIT, 1), paper_x=560)
    c.restore()
    rain(c, t, n=20, seed=431, a=0.1, width=5, length=140, blur=6, speed=3000)
    return 0.3 * math.exp(-lt * 10)


# =============================================================== S3 4.85-6.4 through the glass: his son
def s3(c, t, f):
    lt = t - 4.85
    c.save()
    zoom(c, 1.0 + 0.04 * lt, 540, 900)
    sky(c, '#02040a', '#0d1828', 0, 950)
    floodlight(c, 170, 300, t, 1.0, beam_to=(380, 1400))
    floodlight(c, 930, 280, t, 1.0, beam_to=(720, 1400))
    cam = Cam(horizon=950, F=1700, h=1.4)
    c.drawRect(skia.Rect(-200, 820, W + 200, 950), paint('#05080c'))
    chain_fence(c, -200, W + 200, 840, 950, a=0.22, cell=28)
    pitch(c, cam, light=(540, 1250, 420))
    pline(c, cam, [(-30, 13), (30, 13)])
    goal_frame(c, cam, 13, depth=2.0)
    T_S = 0.75
    d = ease_out(seg(lt, 0.35, 0.8))
    fall = ease_in(seg(lt, 0.85, 1.3))
    X = lerp(0.0, 2.2, d)
    Y = lerp(0.95, 1.6, d) - 1.1 * fall
    kx, ky = cam.p(X, 12.4, Y)
    s = cam.s(12.4, 1.9) / 190
    pz = pose_lerp(POSES['ready'], POSES['dive'], ease_out(seg(lt, 0.3, 0.6)))
    hands = figure(c, pz, kx, ky, s, kit='son', front=True, rot=lerp(0, -70, d) - 15 * fall, rim=(3, -3), rim_a=0.9)
    hxx = (hands[0][0] + hands[1][0]) / 2; hyy = (hands[0][1] + hands[1][1]) / 2
    if lt < T_S:
        u = seg(lt, 0.0, T_S)
        bx, by = cam.p(lerp(-1.0, 2.0, u), lerp(3.0, 12.4, u), lerp(0.4, 1.9, u))
        ball(c, lerp(bx, hxx, u ** 4), lerp(by, hyy, u ** 4), cam.s(lerp(3.0, 12.4, u), 0.11), rot=lt * 12)
    else:
        ball(c, hxx, hyy, cam.s(12.4, 0.11), rot=0.4)
    rain(c, t, n=220, seed=441, a=0.22)
    c.restore()
    # his reflection in the glass
    c.saveLayerAlpha(None, 70)
    profile(c, -260, 500, 1.15, t, 'viejo', face=1, rim_col='#9fc4e6', rim_a=0.8, look_up=-4)
    c.restore()
    r = rng_for(442)
    for k in range(90):  # droplets on the glass
        dx = r.random() * W
        dy = (r.random() * H + t * 60 * r.random() * (k % 3 == 0)) % H
        rr = 4 + r.random() * 10
        c.drawCircle(dx, dy, rr, paint('#cfe3f5', 0.15))
        c.drawCircle(dx - rr * 0.3, dy - rr * 0.3, rr * 0.35, paint('#ffffff', 0.22))
    return 0.25 * math.exp(-lt * 12)


# =============================================================== S4 6.4-8.4 hang up the gloves
def glove_shape(c, x, y, ang, sc=1.0, a=1.0, mirror=1):
    c.save()
    c.translate(x, y); c.rotate(ang); c.scale(sc * mirror, sc)
    rim = '#ffbf70'
    palm = skia.RRect.MakeRectXY(skia.Rect(-70, -40, 70, 150), 40, 40)
    c.save(); c.translate(-6, -6)
    c.drawRRect(palm, paint(rim, 0.6 * a))
    c.restore()
    c.drawRRect(palm, paint('#0c0c0e', a))
    for k in range(4):  # fingers hanging down
        fx = -55 + k * 37
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(fx, 120, fx + 32, 270 - abs(k - 1.5) * 22), 16, 16),
                    paint('#0c0c0e', a))
        c.drawLine(fx + 8, 135, fx + 8, 250 - abs(k - 1.5) * 22, paint(rim, 0.3 * a, stroke=3))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, 20, 110, 150), 22, 22), paint('#0c0c0e', a))  # thumb
    c.drawRect(skia.Rect(-72, -40, 72, 10), paint('#2e333b', a))   # charcoal cuff
    c.drawLine(-72, 10, 72, 10, paint('#9aa3ad', 0.8 * a, stroke=5))
    c.restore()


def s4(c, t, f):
    lt = t - 6.4
    T_D = 0.45
    c.save()
    zoom(c, 1.05 + 0.05 * lt / 2.0, 540, 800)
    c.drawRect(skia.Rect(-200, -200, W + 200, H + 200), paint('#14110f'))
    # wall texture + window light + rain shadows
    glow(c, 760, 600, 700, '#9fc4e6', 0.12)
    glow(c, 300, 1100, 600, '#ffbf70', 0.16)
    for k in range(18):
        rr = rng_for(450 + k)
        x = rr.random() * W
        y = ((t * (120 + 60 * rr.random()) + rr.random() * 2400) % 2400) - 300
        c.drawLine(x, y, x + 6, y + 140, paint('#000000', 0.2, stroke=12, blur=9))
    # a lime scarf on the next hook (Teo's club)
    c.drawCircle(250, 520, 16, paint('#b08b45'))
    c.drawLine(250, 520, 250, 470, paint('#b08b45', 1, stroke=10))
    for k in range(2):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(205 + k * 50, 520, 245 + k * 50, 1000 - k * 60), 18, 18),
                    paint('#7cab19' if k == 0 else '#8fc41f'))
        for j in range(4):
            yy = 600 + j * 90
            c.drawLine(205 + k * 50, yy, 245 + k * 50, yy, paint('#17210c', 0.5, stroke=10))
    # the hook
    hx, hy = 640, 540
    c.drawCircle(hx, hy, 18, paint('#b08b45'))
    c.drawLine(hx, hy, hx, hy - 60, paint('#b08b45', 1, stroke=12))
    c.drawLine(hx - 30, hy - 120, hx + 30, hy - 120, paint('#3a3029', 1, stroke=24))
    # gloves drop onto the hook, then swing
    if lt < T_D:
        u = ease_in(seg(lt, 0.0, T_D))
        gy = lerp(-400, hy + 10, u)
        sw = 0
    else:
        k = lt - T_D
        gy = hy + 10 + 14 * math.exp(-k * 8) * math.sin(k * 30)
        sw = 16 * math.exp(-k * 2.2) * math.sin(k * 6.5)
    c.save(); c.translate(hx, hy); c.rotate(sw); c.translate(-hx, -hy)
    glove_shape(c, hx - 55, gy + 40, 8, 1.15)
    glove_shape(c, hx + 55, gy + 50, -8, 1.15, mirror=-1)
    c.restore()
    c.drawCircle(hx, hy, 10, paint('#e8c47a'))
    c.restore()
    return 0.2 * math.exp(-(lt - T_D) * 12) if lt > T_D else 0.0


# =============================================================== front-on goal (stadium night or training dawn)
def goal_front(c, x0=90, x1=990, top=640, ground=1460, a=1.0):
    pp = paint('#f4f7fb', a, stroke=26)
    c.drawLine(x0, ground, x0, top, pp)
    c.drawLine(x1, ground, x1, top, pp)
    c.drawLine(x0, top, x1, top, pp)
    np_ = paint('#dfe9f5', 0.16 * a, stroke=2.5)
    for i in range(1, 14):
        x = lerp(x0 + 60, x1 - 60, i / 14)
        c.drawLine(x, top + 60, x, ground - 80, np_)
    for j in range(1, 9):
        y = lerp(top + 60, ground - 80, j / 9)
        c.drawLine(x0 + 60, y, x1 - 60, y, np_)
    c.drawLine(x0, top, x0 + 60, top + 60, np_)
    c.drawLine(x1, top, x1 - 60, top + 60, np_)


def stadium_bg(c, t, cheer=0.0):
    sky(c, '#02040a', '#0e1d30', 0, 1000)
    stands(c, 380, 990, t, seed=461, n=1300, blur=2.5, cheer=cheer)
    floodlight(c, 140, 300, t, 1.0, beam_to=(380, 1400))
    floodlight(c, 950, 280, t, 1.0, beam_to=(720, 1400))
    g = skia.Paint()
    g.setShader(lin_shader(0, 990, 0, H, ['#0d2615', '#1b4a2a']))
    c.drawRect(skia.Rect(-200, 990, W + 200, H + 200), g)
    glow(c, 540, 1350, 520, '#ffd9a0', 0.12)


def dawn_sky(c, y0=0, y1=1000):
    p = skia.Paint()
    p.setShader(lin_shader(0, y0, 0, y1, ['#070b18', '#1d2340', '#4a3550', '#a86a58'], [0, 0.45, 0.8, 1]))
    c.drawRect(skia.Rect(-300, y0, W + 300, y1), p)


def training_bg(c, t):
    dawn_sky(c, 0, 1000)
    glow(c, 760, 990, 420, '#ffb070', 0.35)
    r = rng_for(471)
    path = skia.Path()
    path.moveTo(-50, 1000)
    for i in range(24):
        path.lineTo(-50 + i * 52, 900 - r.random() * 90)
    path.lineTo(W + 50, 1000)
    path.close()
    c.drawPath(path, paint('#06070c'))
    floodlight(c, 130, 380, t, 0.75, beam_to=(380, 1400), a=0.7)
    chain_fence(c, -20, W + 20, 870, 1000, a=0.25)
    g = skia.Paint()
    g.setShader(lin_shader(0, 990, 0, H, ['#13281c', '#1e4a2c']))
    c.drawRect(skia.Rect(-200, 990, W + 200, H + 200), g)
    glow(c, 540, 1350, 520, '#ffcf9a', 0.12)


DIVE_R = dict(torso=180, head=-6, uaL=-172, faL=-176, uaR=-160, faR=-170, thL=-10, shL=-18, thR=18, shR=8)
READY_F = dict(torso=172, head=6, uaL=40, faL=60, uaR=50, faR=70, thL=24, shL=-10, thR=30, shR=-6)
KS = 3.35   # adult keeper in a full-size goal, front-on


def keeper_front(c, t, lt, kit, bg, t_imp, catch=True, late=0.0, zm=1.0, slow=1.0):
    """Front-on keeper dives right. catch: ball into gloves at t_imp; else ball beats him into the top corner."""
    amp = 16 * math.exp(-(lt - t_imp) * 6) if lt > t_imp else 0
    sx, sy = shake(lt, amp)
    c.save()
    c.translate(sx, sy)
    zoom(c, zm, 540, 1100)
    bg(c, t)
    goal_front(c)
    c.drawOval(skia.Rect(360, 1440, 720, 1490), paint('#000000', 0.35, blur=10))
    dl = (lt - late) * slow
    d = ease_out(seg(dl, 0.0, 0.5))
    fall = ease_in(seg(dl, 0.6, 1.1))
    x = lerp(540, 760, d) + 40 * fall
    y = lerp(1460 - 80 * KS, 1000, d) + (1330 - 1000) * fall
    rot = lerp(0, -62, d) - 18 * fall
    pz = pose_lerp(READY_F, DIVE_R, ease_out(seg(dl, 0.0, 0.3)))
    hands = figure(c, pz, x, y, KS, kit=kit, front=True, rot=rot, rim=(-3, -3), rim_a=0.9)
    hx = (hands[0][0] + hands[1][0]) / 2
    hy = (hands[0][1] + hands[1][1]) / 2 - 8
    if catch:
        if lt < t_imp:
            u = ease_in(seg(lt, t_imp - 0.4, t_imp))
            ball(c, lerp(470, hx, u), lerp(1900, hy, u), lerp(190, 34, u ** 0.7), rot=lt * 14,
                 motion=(lerp(-40, -120, u), lerp(160, 260, u)))
        else:
            ball(c, hx, hy, 34, rot=0.6)
            for k in range(14):
                rr = rng_for(int(k * 7 + 5))
                ang = rr.random() * 6.28
                dist = (lt - t_imp) * (300 + 500 * rr.random())
                c.drawCircle(hx + math.cos(ang) * dist, hy + math.sin(ang) * dist + 200 * (lt - t_imp) ** 2,
                             3 + rr.random() * 5, paint('#dfe9f5', 0.5 * math.exp(-(lt - t_imp) * 3)))
    else:
        tx, ty = 905, 730   # top corner, just past his fingertips
        if lt < t_imp:
            u = ease_in(seg(lt, t_imp - 0.9, t_imp))
            ball(c, lerp(430, tx, u), lerp(1900, ty, u), lerp(190, 30, u ** 0.7), rot=lt * 10,
                 motion=(lerp(-60, -140, u), lerp(160, 240, u)))
        else:
            k = lt - t_imp
            ball(c, tx + 10 * ease_out(k / 0.3), ty - 6 * ease_out(k / 0.3), 28 * (1 - 0.1 * ease_out(k / 0.3)), rot=0.4)
            bul = math.exp(-k * 3) * (0.6 + 0.4 * math.cos(k * 14))
            for j in range(4):
                c.drawCircle(tx, ty, 50 + j * 35 * (1 + bul), paint('#dfe9f5', 0.18 * bul, stroke=3))
    c.restore()
    rain(c, t, n=36, seed=472, a=0.35, width=6, length=150, blur=6, speed=3600)
    if catch:
        return 0.4 * math.exp(-(lt - t_imp) * 9) if lt > t_imp else 0.0
    return 0.15 * math.exp(-(lt - t_imp) * 9) if lt > t_imp else 0.0


# =============================================================== S5 8.4-11.2 a step slower
def s5(c, t, f):
    lt = t - 8.4
    T_IMP = 1.45                     # global 9.85
    fl = keeper_front(c, t, lt, 'viejo', lambda c_, t_: stadium_bg(c_, t_, cheer=0.9 * seg(lt, T_IMP, T_IMP + 0.3)),
                      T_IMP, catch=False, late=0.75, slow=0.8, zm=1.0 + 0.05 * lt / 2.8)
    rain(c, t, n=200, seed=473, a=0.22)
    return fl


# =============================================================== S6 11.2-13.4 he stares at the pen
def s6(c, t, f):
    lt = t - 11.2
    c.drawRect(skia.Rect(0, 0, W, H), paint('#0a0807'))
    bokeh(c, t, 481, y0=100, y1=1300, a=0.35, drift=-lt * 30)
    glow(c, 860, 500, 600, '#ffbf70', 0.24)
    s = 1.25 + 0.05 * lt
    profile(c, 600 - 640 * s, 930 - 470 * s, s, t, 'viejo', face=1, rim_col='#ffcf8f', look_up=-14 + 3 * ease(lt / 2))
    # the pen in the foreground, out of focus, glinting
    pen(c, 760, 1200, -18, 2.4, blur=9)
    glow(c, 640, 1155, 80, '#ffe2b0', 0.4 + 0.3 * math.sin(t * 3))
    rain(c, t, n=30, seed=482, a=0.12, width=5, length=140, blur=6, speed=3000)
    return 0.2 * math.exp(-lt * 12)


# =============================================================== S7 13.4-14.6 PLANT: he tears off one corner
def s7(c, t, f):
    lt = t - 13.4
    T_R = 0.55                       # rip (global 13.95)
    c.save()
    zoom(c, 1.0 + 0.04 * lt, 540, 900)
    desk(c, t)
    SC = 2.2
    cx, cy = 520 - 240 * SC, 840 - 330 * SC
    rip = seg(lt, T_R, T_R + 0.12)
    away = ease_in(seg(lt, T_R + 0.12, 1.15))
    dx, dy = 40 * rip + 760 * away, 10 * rip + 500 * away
    if lt < T_R:
        contract(c, cx, cy, 0, SC, torn=False)
    else:
        contract(c, cx, cy, 0, SC, torn=True, scrap=(dx / SC, dy / SC, 10 * rip + 30 * away, 1.0))
    # his hand comes in from the right and pinches the very tip of the corner
    tipx, tipy = 520 + 60 * SC, 840 + 70 * SC
    reach = ease_out(seg(lt, 0.0, 0.35))
    arm_top(c, 1900, 1100, lerp(1250, tipx + 95, reach) + dx, lerp(1060, tipy + 10, reach) + dy, VSLEEVE, VSKIN,
            w=170, tape='TEO', fingers=0.8)
    c.restore()
    return 0.15 * math.exp(-(lt - T_R) * 12) if lt > T_R else 0.0


# =============================================================== S7b 14.6-18.6 slid back, stands, leaves
def walk_pose(ph):
    sw = math.sin(ph)
    return dict(torso=178, head=2, uaL=-16 * sw, faL=-8 * sw - 6, uaR=16 * sw, faR=8 * sw + 6,
                thL=18 * sw, shL=14 * sw - 6, thR=-18 * sw, shR=-14 * sw - 6)


def s7b(c, t, f):
    lt = t - 14.6
    slide = ease_out(seg(lt, 0.0, 0.7))
    paper_x = lerp(380, 640, slide)
    up = ease(seg(lt, 1.0, 1.9))
    walk = seg(lt, 2.0, 4.0)
    door = ease(seg(lt, 1.6, 2.3))
    if lt < 1.0:
        vx, pose, face = 280, SIT, 1
    elif lt < 2.0:
        vx, pose, face = 280 - 20 * up, pose_lerp(SIT, STAND, up), 1
    else:
        vx, pose, face = 260 - 330 * walk, walk_pose((lt - 2.0) * 7), -1
    c.save()
    zoom(c, 1.04 + 0.04 * lt / 4.0, 540, 1000)
    c.drawRect(skia.Rect(-200, -200, W + 200, H + 200), paint('#0a0908'))
    # draw the office, but place Viejo ourselves (he stands up out of the chair)
    office(c, t, viejo=None, paper_x=paper_x, door=door)
    hip_y = lerp(1170, 1180 - 4, up)
    if lt >= 2.0:
        hip_y = 1176 - 3 * abs(math.sin((lt - 2.0) * 7))
    c.save()
    c.clipRect(skia.Rect(-200, -200, W + 200, 1180))   # the desk hides his legs
    figure(c, pose, vx, hip_y, 2.9, kit='viejo', face=face, rim=(4, -3), rim_col='#ffbf70', rim_a=0.8)
    c.restore()
    c.restore()
    rain(c, t, n=20, seed=491, a=0.1, width=5, length=140, blur=6, speed=3000)
    return 0.2 * math.exp(-lt * 12)


# =============================================================== S8 18.6-23.2 dawn training, 7 a.m.
def pitch_clock(c, x, y, txt, a=1.0):
    c.drawLine(x + 130, y + 150, x + 130, 1000, paint('#0c0d10', a, stroke=14))
    c.drawRect(skia.Rect(x, y, x + 260, y + 150), paint('#050608', a))
    c.drawRect(skia.Rect(x, y, x + 260, y + 150), paint('#2a2f38', a, stroke=6))
    f = skia.Font(FONT, 120)
    tw = f.measureText(txt)
    glow(c, x + 130, y + 75, 120, '#ffb347', 0.3 * a)
    c.drawString(txt, x + 130 - tw / 2, y + 120, f, paint('#ffb347', a))


def ball_bag(c, x, y, s=1.0):
    c.drawOval(skia.Rect(x - 70 * s, y - 8 * s, x + 70 * s, y + 14 * s), paint('#000000', 0.4, blur=6))
    for k, (dx, dy) in enumerate(((-30, -20), (10, -26), (40, -14), (-8, -52), (24, -56))):
        ball(c, x + dx * s, y + dy * s, 22 * s, rot=k)
    c.drawLine(x - 55 * s, y - 70 * s, x + 60 * s, y + 4 * s, paint('#cfd8e0', 0.25, stroke=2))
    c.drawLine(x + 55 * s, y - 70 * s, x - 60 * s, y + 4 * s, paint('#cfd8e0', 0.25, stroke=2))


def s8a(c, t, lt):
    cam = Cam(horizon=1000, F=1600, h=1.6)
    c.save()
    zoom(c, 1.02 + 0.05 * lt / 2.0, 540, 1000)
    training_bg(c, t)
    pitch(c, cam, light=(540, 1200, 400))
    pline(c, cam, [(-30, 14), (30, 14)])
    pline(c, cam, [(-9.16, 14), (-9.16, 8.5), (9.16, 8.5), (9.16, 14)])
    pitch_clock(c, 60, 420, '06:59' if lt < 0.7 else '07:00')
    goal_frame(c, cam, 14, depth=2.0)
    kx, ky = cam.p(0, 13.5)
    s = cam.s(13.5, 1.9) / 190
    pz = dict(READY_F)
    pz['uaL'] += 8 * math.sin(t * 4); pz['uaR'] -= 8 * math.sin(t * 4)
    figure(c, pz, kx + 5 * math.sin(t * 2), ky - 80 * s, s, kit='son', front=True, rim=(3, -3), rim_col='#ffcf9a',
           rim_a=0.85)
    bx, by = cam.p(0.8, 3.0)
    ball_bag(c, bx, by, 1.6)
    rain(c, t, n=200, seed=501, a=0.2)
    c.restore()
    rain(c, t, n=30, seed=502, a=0.3, width=6, length=150, blur=6, speed=3600)
    return 0.25 * math.exp(-lt * 10) + (0.12 * math.exp(-(lt - 0.7) * 10) if lt > 0.7 else 0)


def s8b(c, t, lt):
    """Behind Teo, in goal: the empty pitch, one bag of balls, the rain."""
    cam = Cam(horizon=980, F=1500, h=1.7)
    c.save()
    zoom(c, 1.0 + 0.06 * lt / 2.6, 540, 1000)
    training_bg(c, t)
    pitch(c, cam, light=(540, 1150, 380))
    pline(c, cam, [(-9.16, 1.0), (-9.16, 5.5), (9.16, 5.5), (9.16, 1.0)])
    pline(c, cam, [(-20.16, 1.0), (-20.16, 16.5), (20.16, 16.5), (20.16, 1.0)])
    bx, by = cam.p(0.3, 11.0)
    ball_bag(c, bx, by, 0.9)
    rain(c, t, n=220, seed=511, a=0.22)
    c.restore()
    pz = dict(READY_F)
    back_view(c, pz, 330 + 6 * math.sin(t * 2.5), 1930, 4.6, rim=(4, -3), rim_col='#ffcf9a', rim_a=0.7, shade=0.1)
    rain(c, t, n=36, seed=512, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.2 * math.exp(-lt * 12)


def s8(c, t, f):
    lt = t - 18.6
    return s8a(c, t, lt) if lt < 2.0 else s8b(c, t, lt - 2.0)


# =============================================================== S9 23.2-25.0 someone starts shooting
def s9(c, t, f):
    lt = t - 23.2
    fl = keeper_front(c, t, lt, 'son', training_bg, 0.35, catch=True, late=-0.05, zm=1.04)
    rain(c, t, n=200, seed=521, a=0.2)
    return fl + 0.25 * math.exp(-lt * 14)


# =============================================================== S10 25.0-27.4 the reveal
def s10a(c, t, lt):
    """Reveal: El Viejo in profile at dawn, rain on his face, the white streak in his beard."""
    dawn_sky(c, 0, H)
    bokeh(c, t, 571, y0=200, y1=1300, a=0.35, drift=lt * 40)
    glow(c, 900, 1000, 600, '#ffb070', 0.3)
    s = 1.3 + 0.06 * lt
    profile(c, 700 - 640 * s, 900 - 470 * s, s, t, 'viejo', face=1, rim_col='#ffcf9a', look_up=-2)
    rain(c, t, n=180, seed=572, a=0.25)
    rain(c, t, n=40, seed=573, a=0.35, width=6, length=150, blur=5, speed=3600)
    return 0.3 * math.exp(-lt * 12)


def s10(c, t, f):
    lt = t - 25.0
    if lt < 1.0:
        return s10a(c, t, lt)
    T_K = 1.35                      # strike (global 26.35)
    cam = Cam(horizon=960, F=2500, h=1.2)
    c.save()
    zoom(c, 1.0 + 0.12 * ease(seg(lt, 0, 1.2)), 540, 900)
    training_bg(c, t)
    pitch(c, cam, light=(540, 1250, 420))
    pline(c, cam, [(-9.16, 1.0), (-9.16, 5.5), (9.16, 5.5), (9.16, 1.0)])
    Z = 9.0
    vx, vy = cam.p(0.1, Z)
    s = cam.s(Z, 1.9) / 190
    glow(c, vx, vy - 300, 380, '#ffcf9a', 0.25)
    if lt < T_K - 0.5:   # walking up, holding a ball
        ph = lt * 6
        pz = walk_pose(ph)
        pz.update(uaR=40, faR=90)
        hip = vy - 92 * s - 4 * abs(math.sin(ph))
        hands = figure(c, pz, vx, hip, s, kit='viejo', front=True, rim=(4, -3), rim_col='#ffcf9a', rim_a=0.9)
        ball(c, hands[1][0], hands[1][1] - 10, cam.s(Z, 0.11) * 1.1, rot=0.3)
    else:
        k = seg(lt, T_K - 0.5, T_K)
        pre = dict(torso=172, head=8, uaL=-40, faL=-20, uaR=50, faR=60, thL=-10, shL=-8, thR=-30, shR=-60)
        kick = dict(torso=190, head=-6, uaL=-90, faL=-70, uaR=100, faR=130, thL=-4, shL=-4, thR=95, shR=110)
        pz = pose_lerp(pre, kick, ease_in(k))
        figure(c, pz, vx, vy - 92 * s, s, kit='viejo', front=True, rim=(4, -3), rim_col='#ffcf9a', rim_a=0.9)
        if lt < T_K:
            bx, by = cam.p(0.35, Z - 0.3, 0.11)
            ball(c, bx, by, cam.s(Z, 0.11), rot=0.2)
        else:
            u = seg(lt, T_K, T_K + 0.3)
            Zb = lerp(Z - 0.3, 0.6, u)
            bx, by = cam.p(lerp(0.35, -0.3, u), Zb, lerp(0.11, 1.2, u))
            ball(c, bx, by, cam.s(Zb, 0.11), rot=lt * 14, motion=(0, -40 * u))
    bbx, bby = cam.p(-1.0, Z + 0.6)
    ball_bag(c, bbx, bby, 1.3)
    rain(c, t, n=200, seed=531, a=0.2)
    c.restore()
    # Teo, foreground, back to camera
    back_view(c, dict(READY_F), 880 + 5 * math.sin(t * 3), 1960, 4.4, rim=(-3, -3), rim_col='#ffcf9a', rim_a=0.7,
              shade=0.15)
    rain(c, t, n=36, seed=532, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.25 * math.exp(-(lt - 1.0) * 12) + (0.35 * math.exp(-(lt - T_K - 0.3) * 10) if lt > T_K + 0.3 else 0)


# =============================================================== S11 27.4-30.0 father shoots, son saves, sunrise
def goal_side(c, x, ground, h=470, depth=180):
    pp = paint('#e9eef4', 1, stroke=14)
    c.drawLine(x, ground, x, ground - h, pp)
    c.drawLine(x, ground - h, x + depth, ground - h * 0.85, paint('#e9eef4', 0.7, stroke=8))
    c.drawLine(x + depth, ground - h * 0.85, x + depth * 1.1, ground, paint('#e9eef4', 0.7, stroke=8))
    np_ = paint('#dfe9f5', 0.18, stroke=2)
    for k in range(1, 8):
        u = k / 8
        c.drawLine(x + depth * u, ground - h + h * 0.15 * u, x + depth * 1.1 * u, ground, np_)
        y = ground - h + h * u
        c.drawLine(x, y, x + depth * lerp(1.0, 1.1, u), lerp(ground - h * 0.85, ground, u), np_)


def s11(c, t, f):
    lt = t - 27.4
    T_K, T_S = 0.75, 1.2            # kick global 28.15, save global 28.6
    GROUND = 1240
    c.save()
    zoom(c, 1.0 + 0.04 * lt / 2.6, 540, 1000)
    dawn_sky(c, 0, GROUND)
    glow(c, 560, GROUND - 20, 520, '#ffb070', 0.45 + 0.1 * ease(lt / 2.6))
    c.drawCircle(560, GROUND - 100 - 40 * ease(lt / 2.6), 90, paint('#ffd9a0', 0.6, blur=10))
    r = rng_for(541)
    path = skia.Path()
    path.moveTo(-50, GROUND)
    for i in range(24):
        path.lineTo(-50 + i * 52, GROUND - 60 - r.random() * 60)
    path.lineTo(W + 50, GROUND)
    path.close()
    c.drawPath(path, paint('#06070c'))
    g = skia.Paint()
    g.setShader(lin_shader(0, GROUND, 0, H, ['#0f1f16', '#183a24']))
    c.drawRect(skia.Rect(-200, GROUND, W + 200, H + 200), g)
    c.drawRect(skia.Rect(-200, GROUND, W + 200, GROUND + 60), paint('#ffb070', 0.12, blur=10))  # wet shine
    goal_side(c, 880, GROUND)
    S = 2.6
    # El Viejo, left, kicks toward the goal (side view, facing right) -- silhouette against the sunrise
    pre = dict(torso=172, head=6, uaL=-40, faL=-20, uaR=40, faR=60, thL=-6, shL=-6, thR=-40, shR=-80)
    kick = dict(torso=190, head=-6, uaL=-80, faL=-60, uaR=90, faR=120, thL=-4, shL=-4, thR=95, shR=105)
    pz = pose_lerp(pre, kick, ease_in(seg(lt, T_K - 0.35, T_K))) if lt < T_K + 0.4 else \
        pose_lerp(kick, dict(POSES['stand']), ease(seg(lt, T_K + 0.4, T_K + 1.0)))
    figure(c, pz, 250, GROUND - 88 * S, S, kit='viejo', face=1, rim=(4, -3), rim_col='#ffcf9a', rim_a=0.9, shade=0.45)
    # Teo, in the goal mouth (facing left), dives up to his right
    d = ease_out(seg(lt, T_S - 0.3, T_S + 0.1))
    fall = ease_in(seg(lt, T_S + 0.3, T_S + 0.8))
    tpz = pose_lerp(READY_F, dict(torso=180, head=-6, uaL=-170, faL=-175, uaR=-165, faR=-172, thL=-10, shL=-20,
                                  thR=20, shR=10), d)
    tx = 840
    ty = GROUND - 80 * S - 120 * d + 140 * fall
    hands = figure(c, tpz, tx, ty, S, kit='son', face=-1, rot=lerp(0, 25, d), rim=(-4, -3), rim_col='#ffcf9a',
                   rim_a=0.9, shade=0.4)
    hx = (hands[0][0] + hands[1][0]) / 2; hy = (hands[0][1] + hands[1][1]) / 2
    if T_K <= lt < T_S:
        u = seg(lt, T_K, T_S)
        bx = lerp(300, hx, u)
        by = lerp(GROUND - 10, hy, u) - 140 * math.sin(math.pi * u)
        ball(c, bx, by, 16, rot=lt * 14, motion=(-40, 0))
    elif lt >= T_S:
        ball(c, hx, hy, 16, rot=0.4)
    elif lt < T_K:
        ball(c, 300, GROUND - 10, 16, rot=0.2)
    rain(c, t, n=180, seed=542, a=0.18)
    c.restore()
    rain(c, t, n=30, seed=543, a=0.3, width=6, length=150, blur=6, speed=3600)
    return 0.25 * math.exp(-lt * 12) + (0.3 * math.exp(-(lt - T_S) * 9) if lt > T_S else 0)


# =============================================================== S12 30.0-33.5 what he tore off / loop
def s12(c, t, f):
    lt = t - 30.0
    if lt > 2.9:  # loop: back to the desk, the contract waiting for the slam that opens the video
        k = lt - 2.9
        c.save()
        desk(c, t)
        contract(c, 540, 960, -3, 0.88)
        c.restore()
        return 0.3 * math.exp(-k * 10)
    c.drawRect(skia.Rect(0, 0, W, H), paint('#0b0a10'))
    dawn_sky(c, 0, 1100)
    bokeh(c, t, 551, y0=200, y1=1300, a=0.35, drift=lt * 25)
    glow(c, 700, 500, 600, '#ffb070', 0.25)
    op = ease(seg(lt, 0.2, 1.1))
    c.save()
    zoom(c, 1.0 + 0.06 * lt / 2.9, 540, 950)
    # palm up, from the bottom; fingers open to show the scrap
    arm_top(c, 420, 2500, 560, 900, VSLEEVE, VSKIN, w=340, fingers=1 - op, rim='#ffcf9a')
    # the scrap on his palm
    c.save()
    c.translate(565, 900); c.rotate(-14 + 4 * op); c.scale(2.2, 2.2); c.translate(-230, -330)
    scrap_local(c, op)
    c.restore()
    # rain drops landing on the paper
    for k in range(6):
        rr = rng_for(560 + k)
        tk = (lt * 1.5 + rr.random()) % 1.0
        dx, dy = 470 + rr.random() * 180, 920 + rr.random() * 140
        c.drawCircle(dx, dy, 4 + 30 * tk, paint('#dfe9f5', 0.35 * (1 - tk) * op, stroke=2))
    c.restore()
    rain(c, t, n=160, seed=561, a=0.2)
    rain(c, t, n=30, seed=562, a=0.3, width=6, length=150, blur=6, speed=3600)
    return 0.25 * math.exp(-lt * 12)


SCENES = [(0.0, 1.6, s1), (1.6, 2.8, s1b), (2.8, 4.85, s2), (4.85, 6.4, s3), (6.4, 8.4, s4), (8.4, 11.2, s5),
          (11.2, 13.4, s6), (13.4, 14.6, s7), (14.6, 18.6, s7b), (18.6, 23.2, s8), (23.2, 25.0, s9),
          (25.0, 27.4, s10), (27.4, 30.0, s11), (30.0, 33.5, s12)]
