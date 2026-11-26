"""Reusable shot library (built for ep001 'El Viejo').
Each sN(c, t, f) draws one scene at GLOBAL time t using ep001 timings; the helpers
(zoom, bokeh, taped_hand, physio_hand, keeper4, score_bug, s5a/s5b/s6a/s6b/s6c...) can be
reused or copied into new episodes. Return value = white flash amount (0..1)."""
import math, functools
import skia
from lib import *

def zoom(c, s, cx, cy):
    c.translate(cx, cy)
    c.scale(s, s)
    c.translate(-cx, -cy)


def bokeh(c, t, seed, n=26, y0=300, y1=1400, drift=0.0, a=0.35):
    r = rng_for(seed)
    for i in range(n):
        x = (r.random() * (W + 400) - 200 + drift * (0.6 + r.random())) % (W + 400) - 200
        y = y0 + r.random() * (y1 - y0)
        rr = 30 + r.random() * 90
        colr = '#ffcf8a' if r.random() < 0.6 else '#9fc4e6'
        glow(c, x, y, rr, colr, a * (0.4 + 0.6 * r.random()) * (0.8 + 0.2 * math.sin(t * 2 + i)))


# =============================================================== S1 0.0-3.0 net bulge (payoff first)
def s1(c, t, f):
    lt = t
    ti = 0.62
    sx, sy = shake(lt, 16 * math.exp(-max(0, lt - ti) * 5) * (lt > ti))
    c.save()
    c.translate(sx, sy)
    cam = Cam(horizon=1250, F=1500, h=0.5)
    sky(c, '#02040a', '#0e1d30', 0, 1250)
    cheer = ease(seg(lt, 1.1, 1.6))
    floodlight(c, 150, 600, lt, 1.0, beam_to=(420, 1400))
    floodlight(c, 940, 540, lt, 1.1, beam_to=(700, 1400))
    stands(c, 1010, 1242, lt, seed=11, cheer=cheer)
    pitch(c, cam, light=(540, 1300, 500))
    for X in (-20.16, 20.16):
        pline(c, cam, [(X, 2.5), (X, 19)])
    pline(c, cam, [(-20.16, 19), (20.16, 19)])
    pline(c, cam, [(-9.16, 2.5), (-9.16, 8), (9.16, 8), (9.16, 2.5)])
    pline(c, cam, [(-34, 55), (34, 55)], a=0.4)
    goal_frame(c, cam, 107.5, net=False)
    fx, fy = cam.p(0, 107)
    s = cam.s(107, 1.9) / 190
    glow(c, fx, fy - 15, 60, '#ffd49a', 0.35)
    figure(c, POSES['stand'], fx, fy - 88 * s, s, kit='viejo', front=True, rim_a=0)
    rain(c, lt, n=220, seed=3, a=0.22, length=40, width=1.6)
    # ball (beyond the net, flying toward camera)
    if lt < ti:
        u = ease_in(lt / ti) * 0.85 + (lt / ti) * 0.15
        bx, by = lerp(660, 540, u), lerp(250, 880, u)
        br = lerp(24, 118, u ** 1.6)
        ball(c, bx, by, br, rot=lt * 9, motion=(lerp(60, 160, u) * 0.4, -lerp(60, 160, u)))
    else:
        k = lt - ti
        push = 1 + 0.12 * math.exp(-k * 5) * math.cos(k * 16)
        bx, by = 540, 880 + 60 * ease(k / 1.6)
        ball(c, bx, by, 122 * push, rot=ti * 9 + k * 1.5)
    # net (foreground) with bulge
    amp = 0.0
    if lt >= ti:
        k = lt - ti
        amp = 0.42 * math.exp(-k * 3.2) * math.cos(k * 13) + 0.16
    cxp, cyp = 540, 880 + (60 * ease((lt - ti) / 1.6) if lt > ti else 0)
    sig = 260.0
    cell = 92
    e1 = (cell * 0.7071, cell * 0.7071)
    e2 = (-cell * 0.7071, cell * 0.7071)
    N = 26
    p = paint('#eef3f8', 0.55, stroke=4.5, blur=1.2)
    pdark = paint('#000000', 0.45, stroke=8, blur=3)

    def vert(u, v):
        x = 540 + u * e1[0] + v * e2[0]
        y = 900 + u * e1[1] + v * e2[1] - 150
        dx, dy = x - cxp, y - cyp
        g = math.exp(-(dx * dx + dy * dy) / (2 * sig * sig))
        return x + dx * amp * g, y + dy * amp * g + 30 * amp * g

    for fixed in range(-N, N + 1):
        for along_u in (True, False):
            path = skia.Path()
            for i, w_ in enumerate(range(-N, N + 1)):
                x, y = vert(w_, fixed) if along_u else vert(fixed, w_)
                (path.moveTo if i == 0 else path.lineTo)(x, y)
            c.drawPath(path, pdark)
            c.drawPath(path, p)
    # crossbar top (out of focus)
    c.drawRect(skia.Rect(-50, 40, W + 50, 112), paint('#e8edf3', 0.95, blur=6))
    c.drawRect(skia.Rect(-50, 100, W + 50, 116), paint('#000000', 0.35, blur=6))
    c.restore()
    flash = 0.35 * math.exp(-(lt - ti) * 7) if lt > ti else 0
    return flash


# =============================================================== S2 3.0-5.8 coach + sub board
def s2(c, t, f):
    lt = t - 3.0
    c.save()
    zoom(c, 1 + 0.06 * lt / 2.8, 600, 1000)
    sky(c, '#02040a', '#0d1828', 0, 700)
    floodlight(c, 900, 330, t, 0.9, beam_to=(700, 1400))
    stands(c, 560, 1180, t, seed=21, n=700, blur=3.5)
    cam = Cam(horizon=1180, F=1500, h=1.6)
    pitch(c, cam, stripes=True)
    pline(c, cam, [(-60, 3.0), (60, 3.0)], a=0.7, w=6)
    # 4th official's board
    bx0, by0 = 150, 620
    c.drawLine(-60, 1080, 240, 860, paint('#14171c', 1, stroke=46))
    c.drawRect(skia.Rect(bx0, by0, bx0 + 330, by0 + 230), paint('#050608'))
    c.drawRect(skia.Rect(bx0, by0, bx0 + 330, by0 + 230), paint('#2a2f38', 1, stroke=6))
    blink = 0.75 + 0.25 * math.sin(t * 14)
    font = skia.Font(FONT, 200)
    glow(c, bx0 + 120, by0 + 115, 140, '#ff2d2d', 0.35 * blink)
    c.drawString("1", bx0 + 88, by0 + 200, font, paint('#ff3b3b', blink))
    tri = skia.Path()
    tri.moveTo(bx0 + 220, by0 + 80); tri.lineTo(bx0 + 300, by0 + 80); tri.lineTo(bx0 + 260, by0 + 150); tri.close()
    c.drawPath(tri, paint('#ff3b3b', blink))
    # coach
    pz = dict(POSES['point'])
    pz['uaR'] = 98 + 12 * math.sin(lt * 10)
    pz['faR'] = 100 + 16 * math.sin(lt * 10 + 0.4)
    pz['head'] = 4 + 10 * math.sin(lt * 5)
    figure(c, pz, 760, 1060, 3.7, kit='coach', face=-1, rim=(5, -3), rim_a=0.85)
    rain(c, t, n=200, seed=5, a=0.28)
    rain(c, t, n=40, seed=6, a=0.35, width=5, length=120, blur=4, speed=3600)
    c.restore()
    return 0.0


# =============================================================== S3 5.8-11.6 hand, profile, son plant
def taped_hand(c, lt):
    pull = ease_in(seg(lt, 0.78, 1.0)) if lt < 1.0 else 1.0
    pull = ease(seg(lt, 0.78, 1.05))
    dx, dy = -300 * pull, 520 * pull
    blur = 10 * math.sin(math.pi * clamp(seg(lt, 0.78, 1.05)))
    c.save()
    c.translate(dx, dy)
    ang = -38
    # forearm
    p = paint('#ffcf8f', 0.9, stroke=250, blur=blur)
    c.drawLine(-120 + 10, 2000 - 12, 500 + 10, 1180 - 12, p)
    c.drawLine(-120, 2000, 500, 1180, paint('#2a1d16', 1, stroke=240, blur=blur))
    # sleeve
    c.drawLine(-160, 2100, 150, 1690, paint('#2e333b', 1, stroke=290, blur=blur))
    # fist
    c.save()
    c.translate(610, 1030)
    c.rotate(ang)
    fist = skia.RRect.MakeRectXY(skia.Rect(-170, -130, 170, 130), 90, 90)
    c.save(); c.translate(10, -8); c.drawRRect(fist, paint('#ffcf8f', 0.9, blur=blur)); c.restore()
    c.drawRRect(fist, paint('#2a1d16', 1, blur=blur))
    for k in range(4):
        fy = -95 + k * 62
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, fy, 200, fy + 56), 28, 28), paint('#33241b', 1, blur=blur))
        c.drawLine(80, fy + 6, 190, fy + 6, paint('#ffcf8f', 0.35, stroke=4, blur=blur))
    # knuckle tape
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(40, -110, 120, 130), 30, 30), paint('#e9e5dc', 0.95, blur=blur))
    c.restore()
    # wrist tape bands with TEO
    c.save()
    c.translate(450, 1250)
    c.rotate(ang)
    for k, off in enumerate((-60, 30)):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(off, -135, off + 95, 135), 18, 18), paint('#ece8df', 1, blur=blur))
        c.drawLine(off + 8, -125, off + 8, 125, paint('#b9b3a8', 0.8, stroke=5, blur=blur))
    c.rotate(90)
    fnt = skia.Font(FONT, 92)
    c.drawString("TEO", -62, 50 - 60 + 30, fnt, paint('#111111', 0.92, blur=blur * 0.5))
    c.restore()
    c.restore()


def physio_hand(c, lt):
    reach = ease_out(seg(lt, 0.15, 0.7)) - 0.25 * ease(seg(lt, 1.0, 1.6))
    x = lerp(1450, 930, reach)
    y = lerp(1250, 1180, reach)
    c.drawLine(x + 500, y - 130, x, y, paint('#0f1b2e', 1, stroke=170))
    c.save()
    c.translate(x, y)
    c.rotate(-168)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-20, -75, 150, 75), 60, 60), paint('#3b7fd9'))
    for k in range(4):
        fy = -62 + k * 34
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(120, fy, 230 - abs(k - 1.5) * 18, fy + 28), 14, 14), paint('#4a8fe6'))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-20, -75, 150, 75), 60, 60), paint('#9cc6ff', 0.4, stroke=5))
    c.restore()


def s3(c, t, f):
    lt = t - 5.8
    flash = 0.0
    if lt < 1.8:  # hand
        sky(c, '#05070c', '#0b1420')
        bokeh(c, t, 31, y0=100, y1=1500)
        floodlight(c, 980, 200, t, 0.7, beams=False)
        physio_hand(c, lt)
        taped_hand(c, lt)
        rain(c, t, n=50, seed=8, a=0.35, width=6, length=150, blur=5, speed=3600)
    elif lt < 3.8 or lt >= 4.9:  # profile
        k = lt - 1.8 if lt < 3.8 else lt - 4.9
        tight = lt >= 4.9
        sky(c, '#03050a', '#0c1522')
        bokeh(c, t, 33, y0=150, y1=1300, a=0.4)
        floodlight(c, 1000, 330, t, 0.9, beams=False)
        if not tight:
            s = 1.22 + 0.06 * k / 2.0
            profile(c, 540 - 640 * s, 900 - 470 * s, s, t, 'viejo', breath=seg(k, 0.9, 1.9))
        else:
            s = 1.85 + 0.08 * k
            profile(c, 560 - 630 * s, 780 - 480 * s, s, t, 'viejo')
        rain(c, t, n=180, seed=9, a=0.25)
        rain(c, t, n=40, seed=10, a=0.35, width=6, length=150, blur=5, speed=3600)
        if lt < 1.9:
            flash = 0.0
    else:  # son plant, telephoto
        k = lt - 3.8
        c.save()
        cam = Cam(horizon=1060, F=3400, h=1.5)
        zm = 1 + 0.5 * ease(k / 1.1)
        fx, fy = cam.p(0, 60)
        zoom(c, zm, 540, fy - 60)
        sky(c, '#02040a', '#0d1828', 0, 1060)
        stands(c, 640, 1052, t, seed=41, n=800, blur=2.5)
        floodlight(c, 760, 420, t, 1.2, beams=True, beam_to=(560, 1200))
        pitch(c, cam)
        goal_frame(c, cam, 61.5)
        s = cam.s(60, 1.9) / 190
        glow(c, fx, fy - 70, 160, '#ffd49a', 0.25)
        pz = dict(POSES['stand']); pz['uaL'] = -22; pz['uaR'] = 22; pz['faL'] = -14; pz['faR'] = 14
        figure(c, pz, fx, fy - 88 * s, s, kit='son', front=True, rim=(3, -2), rim_a=0.8)
        c.restore()
        rain(c, t, n=220, seed=12, a=0.25)
        rain(c, t, n=40, seed=13, a=0.35, width=6, length=150, blur=6, speed=3600)
    return flash


# =============================================================== S4 11.6-17.4 penalty save
CAM4 = Cam(horizon=980, F=1700, h=1.3)
T_KICK, T_HIT, T_LAND = 1.8, 3.25, 3.85


def s4_warp(lt):
    if lt < T_KICK:
        return lt
    if lt < T_LAND:
        return T_KICK + (lt - T_KICK) * 0.3
    return T_KICK + (T_LAND - T_KICK) * 0.3 + (lt - T_LAND)


FRONT_READY = dict(torso=180, head=0, uaL=-55, faL=-35, uaR=55, faR=35, thL=-20, shL=-4, thR=20, shR=4)


def keeper4(lt):
    """Return (pose, x, y, rot)."""
    s = CAM4.s(15, 1.9) / 190
    gx, gy = CAM4.p(0, 14.6)
    stand_hip = (gx, gy - 84 * s)
    if lt < 2.0:
        sway = 10 * math.sin(lt * 4)
        return FRONT_READY, stand_hip[0] + sway, stand_hip[1], 0.0
    if lt < T_HIT:
        u = ease_out(seg(lt, 2.0, T_HIT))
        pz = pose_lerp(FRONT_READY, POSES['dive'], u)
        x = lerp(stand_hip[0], 322, u)
        y = lerp(stand_hip[1], 945, u) - 60 * math.sin(math.pi * u) * 0.6
        return pz, x, y, -82 * u
    u = ease_in(seg(lt, T_HIT, T_LAND))
    pz = POSES['dive']
    return pz, lerp(322, 345, u), lerp(945, 1080, u), lerp(-82, -93, u)


@functools.lru_cache(None)
def hit_point():
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(10, 10, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    pz, x, y, rot = keeper4(T_HIT)
    s = CAM4.s(15, 1.9) / 190
    hands = figure(surf.getCanvas(), pz, x, y, s, front=True, rot=rot)
    return min(hands, key=lambda h: h[0])  # screen-left hand


def s4(c, t, f):
    lt = t - 11.6
    rt = s4_warp(lt)
    s = CAM4.s(15, 1.9) / 190
    amp = 14 * math.exp(-(lt - T_HIT) * 5) if lt > T_HIT else 0
    amp += 10 * math.exp(-(lt - T_LAND) * 6) if lt > T_LAND else 0
    sx, sy = shake(lt, amp)
    c.save()
    c.translate(sx, sy)
    zoom(c, 1.0 + 0.16 * ease(seg(lt, 0, 5.8)), 470, 1000)
    sky(c, '#02040a', '#0d1828', 0, 980)
    cheer = ease(seg(lt, 3.4, 3.9))
    floodlight(c, 110, 300, t, 1.0, beam_to=(300, 1300))
    floodlight(c, 980, 250, t, 1.05, beam_to=(780, 1300))
    stands(c, 560, 975, rt, seed=51, n=1000, cheer=cheer)
    cam = CAM4
    pitch(c, cam)
    pline(c, cam, [(-30, 15), (30, 15)])
    pline(c, cam, [(-9.16, 15), (-9.16, 9.5), (9.16, 9.5), (9.16, 15)])
    pline(c, cam, [(-20.16, 15), (-20.16, -1)])
    pline(c, cam, [(20.16, 15), (20.16, -1)])
    sp = cam.p(0, 4)
    c.drawOval(skia.Rect(sp[0] - 22, sp[1] - 6, sp[0] + 22, sp[1] + 6), paint('#e9f2ea', 0.7))
    goal_frame(c, cam, 15, depth=2.0)
    # keeper
    pz, kx, ky, rot = keeper4(lt)
    figure(c, pz, kx, ky, s, kit='viejo', front=True, rot=rot, rim=(3, -3))
    # ball
    hx, hy = hit_point()
    if lt < T_KICK:
        ball(c, sp[0], sp[1] - cam.s(4, 0.11), cam.s(4, 0.11), rot=0)
    elif lt < T_HIT:
        u = seg(lt, T_KICK, T_HIT)
        Z = lerp(4, 14.3, u)
        tx = (hx - cam.cx) * 14.3 / cam.F
        ty = cam.h - (hy - cam.hz) * 14.3 / cam.F
        X = lerp(0, tx, u)
        Y = lerp(0.11, ty, u) + 0.5 * math.sin(math.pi * u)
        bx, by = cam.p(X, Z, Y)
        r = cam.s(Z, 0.11)
        ball(c, bx, by, r, rot=lt * 6, motion=(-(tx * cam.F / Z) * 0.02, 30))
    else:
        u = seg(lt, T_HIT, T_HIT + 0.9)
        bx = lerp(hx, -120, ease_out(u))
        by = lerp(hy, 640, ease_out(u)) + 120 * u * u
        ball(c, bx, by, cam.s(14.3, 0.11) * (1 - 0.2 * u), rot=lt * 14)
    # mud / water burst on landing
    if lt > T_LAND - 0.05:
        k = (lt - (T_LAND - 0.05)) * 0.45 if lt < T_LAND + 0.6 else 0.27 + (lt - T_LAND - 0.6)
        r_ = rng_for(77)
        ox, oy = 360, 1118
        for i in range(120):
            vx = (r_.random() - 0.35) * 900
            vy = -r_.random() * 900 - 200
            px = ox + vx * k
            py = oy + vy * k + 1600 * k * k
            if py > oy + 30:
                continue
            mud = r_.random() < 0.55
            rr = 2 + r_.random() * 7
            c.drawCircle(px, py, rr, paint('#2a1f16' if mud else '#dfe9f5', 0.9 if mud else 0.6))
    # taker (foreground, out of focus)
    if lt < T_KICK + 0.6:
        run = seg(lt, 0.2, T_KICK)
        out = ease_in(seg(lt, T_KICK, T_KICK + 0.6))
        tx = lerp(1000, 760, run) + 300 * out
        ty = lerp(1720, 1600, run) + 500 * out
        ph = lt * 11
        pz2 = dict(torso=180, head=0, uaL=-30 - 20 * math.sin(ph), faL=-20, uaR=30 + 20 * math.sin(ph), faR=20,
                   thL=-8 + 12 * math.sin(ph), shL=-6, thR=8 - 12 * math.sin(ph), shR=6)
        figure(c, pz2, tx, ty, 4.6, kit='red', front=True, rim=(3, -3), rim_a=0.7, shade=0.55, blur=7)
    rain(c, rt, n=230, seed=14, a=0.26)
    rain(c, rt, n=36, seed=15, a=0.35, width=6, length=150, blur=6, speed=3600)
    c.restore()
    flash = 0.4 * math.exp(-(lt - T_HIT) * 8) if lt > T_HIT else 0.0
    return flash


# =============================================================== S5 17.4-23.2 corner catch + POV
T_CATCH = 2.4  # local


def score_bug(c, t):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, 150, 360, 230), 14, 14), paint('#0b0f16', 0.85))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, 150, 360, 230), 14, 14), paint('#ffffff', 0.15, stroke=3))
    f1 = skia.Font(FONT, 64)
    c.drawString("1 - 1", 88, 212, f1, paint('#ffffff'))
    c.drawRect(skia.Rect(212, 162, 216, 218), paint('#ffffff', 0.3))
    sec = int((t - 17.4) * 1.0) % 60
    blink = 1.0 if (t * 2) % 2 < 1.4 else 0.5
    c.drawString("99:%02d" % sec, 232, 212, f1, paint('#ffd400', blink))


PLAYERS = [  # X, Z, kit, jump offset, pose
    (-5.5, 16.5, 'red', 0.05, 'jumpo'), (-3.4, 17.6, 'navy', 0.12, 'jumpo'), (-1.8, 15.6, 'red', 0.0, 'jump'),
    (2.6, 16.2, 'navy', 0.08, 'jumpo'), (4.2, 17.2, 'red', 0.18, 'jump'), (6.3, 15.4, 'navy', 0.02, 'jumpo'),
    (-7.6, 14.8, 'navy', 0.22, 'stand'), (8.4, 14.6, 'red', 0.3, 'stand'), (1.6, 18.6, 'son', 0.1, 'jumpo'),
    (-0.2, 13.6, 'red', 0.15, 'jump'),
]


def s5a(c, t, lt):
    cam = Cam(horizon=760, F=1500, h=4.0)
    vx, vz = -0.4, 19.6
    gx, gy = cam.p(vx, vz)
    sv = cam.s(vz, 1.9) / 190
    amp = 14 * math.exp(-(lt - T_CATCH) * 5) if lt > T_CATCH else 0
    sx, sy = shake(lt, amp)
    c.save()
    c.translate(sx, sy)
    zm = 1 + 0.4 * ease(seg(lt, 0, 3.0))
    zoom(c, zm, gx, gy - 140)
    sky(c, '#02040a', '#0d1828', 0, 760)
    stands(c, 420, 755, t, seed=61, n=900, cheer=0.3)
    floodlight(c, 900, 230, t, 1.0, beam_to=(600, 1300))
    pitch(c, cam)
    pline(c, cam, [(-30, 22), (30, 22)])
    pline(c, cam, [(-9.16, 22), (-9.16, 16.5), (9.16, 16.5), (9.16, 22)])
    pline(c, cam, [(-20.16, 22), (-20.16, 5.5), (20.16, 5.5), (20.16, 22)])
    goal_frame(c, cam, 22, depth=2.0)
    # draw far-to-near
    items = list(PLAYERS) + [(vx, vz, 'viejo', 0, 'viejo')]
    items.sort(key=lambda it: -it[1])
    catch_hands = None
    for (X, Z, kit, off, pname) in items:
        px, py = cam.p(X, Z)
        s = cam.s(Z, 1.9) / 190
        if kit == 'viejo':
            j = seg(lt, 1.85, T_CATCH)
            fall = seg(lt, T_CATCH + 0.35, T_CATCH + 0.75)
            h = 70 * math.sin(math.pi * 0.5 * j) * (1 - ease(fall))
            if lt < 1.85:
                pz = dict(POSES['ready']); pz['torso'] = 180
                pz = pose_lerp(FRONT_READY, FRONT_READY, 0)
            else:
                pz = pose_lerp(FRONT_READY, dict(torso=180, head=-14, uaL=-172, faL=172, uaR=172, faR=-172,
                                                 thL=-10, shL=-40, thR=14, shR=-20), ease(j))
            hands = figure(c, pz, px, py - 86 * s - h * s * 1.4, s, kit='viejo', front=True, rim=(3, -3))
            catch_hands = hands
        else:
            jt = seg(lt, 1.7 + off, 2.2 + off) - seg(lt, 2.55 + off, 3.0 + off)
            h = 40 * math.sin(math.pi * 0.5 * clamp(jt)) if pname != 'stand' else 0
            base = FRONT_READY
            pz = pose_lerp(base, POSES[pname if pname != 'stand' else 'ready'], clamp(jt)) if pname != 'stand' else POSES['ready']
            figure(c, pz, px, py - 86 * s - h * s * 1.2, s, kit=kit, front=pname != 'stand',
                   face=-1 if X > 0 else 1, rim=(3, -3), rim_a=0.75, beard=False)
    # ball arc from right corner
    (h1, h2) = catch_hands
    bxh, byh = (h1[0] + h2[0]) / 2, (h1[1] + h2[1]) / 2 - 4
    if lt < T_CATCH:
        u = seg(lt, 0.6, T_CATCH)
        bx = lerp(1300, bxh, u)
        by = lerp(260, byh, u) - 420 * math.sin(math.pi * u) * (1 - u)
        if u > 0:
            ball(c, bx, by, lerp(16, 9, u), rot=lt * 10, motion=(-40, -20))
    else:
        ball(c, bxh, byh, 9, rot=0)
    rain(c, t, n=200, seed=16, a=0.24)
    c.restore()
    return 0.35 * math.exp(-(lt - T_CATCH) * 8) if lt > T_CATCH else 0.0


def s5b(c, t, lt):
    cam = Cam(horizon=800, F=1500, h=2.6)
    gx, gy = cam.p(0, 88)
    c.save()
    zm = 1 + 0.7 * ease(seg(lt, 0.2, 2.8))
    zoom(c, zm, gx, gy - 20)
    sky(c, '#02040a', '#0d1828', 0, 800)
    stands(c, 560, 796, t, seed=71, n=1000, cheer=0.2)
    floodlight(c, 120, 330, t, 0.9, beam_to=(300, 1200))
    floodlight(c, 960, 300, t, 0.9, beam_to=(760, 1200))
    pitch(c, cam)
    pline(c, cam, [(-34, 1), (-34, 88)])
    pline(c, cam, [(34, 1), (34, 88)])
    pline(c, cam, [(-34, 88), (34, 88)])
    pline(c, cam, [(-34, 36), (34, 36)])
    circ = [(9.15 * math.cos(a / 40 * 6.283), 36 + 9.15 * math.sin(a / 40 * 6.283)) for a in range(41)]
    pline(c, cam, circ)
    pline(c, cam, [(-20.16, 88), (-20.16, 71.5), (20.16, 71.5), (20.16, 88)])
    pline(c, cam, [(-9.16, 88), (-9.16, 82.5), (9.16, 82.5), (9.16, 88)])
    glow(c, gx, gy - 12, 90, '#ffe2b0', 0.35 + 0.15 * math.sin(t * 4))
    goal_frame(c, cam, 88, depth=2.0)
    rain(c, t, n=160, seed=17, a=0.2)
    c.restore()
    # POV gloves + ball
    bob = 8 * math.sin(lt * 3.2)
    bx, by = 540, 1790 + bob
    ball(c, bx, by - 10, 175, rot=0.3, lit=(0.8, -1))
    for side in (-1, 1):
        gx_ = bx + side * 205
        gp = skia.RRect.MakeRectXY(skia.Rect(gx_ - 120, by - 170, gx_ + 120, by + 230), 110, 110)
        c.save(); c.translate(side * 8 + 6, -8); c.drawRRect(gp, paint('#ffcf8f', 0.6)); c.restore()
        c.drawRRect(gp, paint('#0d0d0f'))
        c.drawLine(gx_ - 90, by + 120, gx_ + 90, by + 120, paint('#9aa3ad', 0.8, stroke=14))
        for k in range(1, 4):
            fx_ = gx_ - 120 + k * 60
            c.drawLine(fx_, by - 150, fx_, by - 40, paint('#2a2d33', 1, stroke=5))
    rain(c, t, n=40, seed=18, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.0


def s5(c, t, f):
    lt = t - 17.4
    fl = s5a(c, t, lt) if lt < 3.0 else s5b(c, t, lt - 3.0)
    score_bug(c, t)
    return fl


# =============================================================== S6 23.2-28.2 kick, son run, son face
T_DROP, T_K = 0.25, 0.62


def s6a(c, t, lt):
    tilt = 1500 * ease(seg(lt, 0.8, 1.8)) ** 1.3
    c.save()
    c.translate(0, tilt)
    sky(c, '#02040a', '#0d1828', -1700, 760)
    floodlight(c, 120, 300, t, 1.0, beams=False)
    floodlight(c, 1000, 220, t, 1.0, beams=False)
    stands(c, 480, 1100, t, seed=81, n=900, blur=3)
    g = skia.Paint()
    g.setShader(lin_shader(0, 1100, 0, H, ['#0f2a18', '#1d4a2a']))
    c.drawRect(skia.Rect(0, 1100, W, H + 200), g)
    glow(c, 450, 1480, 500, '#ffd9a0', 0.2)
    # keeper side view facing right
    s = 2.5
    hipx, hipy = 380, 1480 - 88 * s
    if lt < T_DROP:
        pz = POSES['hold']
    elif lt < T_K:
        u = seg(lt, T_DROP, T_K)
        pz = pose_lerp(POSES['hold'], dict(torso=186, head=14, uaL=-60, faL=-40, uaR=70, faR=50,
                                           thL=-4, shL=-4, thR=-50, shR=-80), ease(u))
    else:
        u = ease_out(seg(lt, T_K, T_K + 0.35))
        pz = pose_lerp(dict(torso=186, head=14, uaL=-60, faL=-40, uaR=70, faR=50, thL=-4, shL=-4, thR=-50, shR=-80),
                       dict(torso=200, head=-10, uaL=-100, faL=-80, uaR=110, faR=140, thL=-4, shL=-4, thR=112, shR=128), u)
    hands = figure(c, pz, hipx, hipy, s, kit='viejo', rim=(-4, -3))
    # ball
    if lt < T_DROP:
        bx, by = hands[1][0] + 10, hands[1][1] + 6
        ball(c, bx, by, 27, rot=0, lit=(-1, -1))
    elif lt < T_K:
        u = seg(lt, T_DROP, T_K)
        bx = lerp(hands[1][0] + 10, hipx + 95, u)
        by = lerp(hands[1][1], hipy + 150, u * u)
        ball(c, bx, by, 27, rot=0, lit=(-1, -1))
    c.restore()
    if lt >= T_K:  # in flight, screen-space so it outruns the tilt
        k = lt - T_K
        bx = hipx + 95 + 700 * k ** 0.8
        by = (hipy + 150 + tilt) - 1900 * k + 300 * k * k
        by = max(by, lerp(hipy + 150, 380, ease(k / 1.2)))
        r = 27 * (1 / (1 + 1.1 * k))
        ball(c, bx, by, r, rot=k * 20, lit=(-1, -1), motion=(-140 * r / 27, 260 * r / 27))
    rain(c, t, n=230, seed=19, a=0.25)
    rain(c, t, n=36, seed=20, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.45 * math.exp(-(lt - T_K) * 9) if lt > T_K else 0.0


def s6b(c, t, lt):
    sky(c, '#02040a', '#0d1828', 0, 900)
    c.save()
    c.translate((lt * 2400) % 1200 - 1200, 0)
    for k in range(3):
        c.save(); c.translate(k * 1200, 0)
        stands(c, 520, 1120, t, seed=91, n=500, blur=6, x0=0, x1=1200)
        c.restore()
    c.restore()
    floodlight(c, 300 + ((lt * 600) % 1600), 260, t, 0.8, beams=False)
    g = skia.Paint()
    g.setShader(lin_shader(0, 1120, 0, H, ['#0f2a18', '#1d4a2a']))
    c.drawRect(skia.Rect(0, 1120, W, H), g)
    for k in range(8):
        x = (k * 300 + lt * 3400) % 2400 - 600
        c.drawRect(skia.Rect(x, 1120, x + 150, H), paint('#2c6a3a', 0.14))
    ph = lt * 13
    pz = run_pose(ph)
    pz['head'] = -18
    bob = 18 * abs(math.sin(ph))
    s = 2.7
    figure(c, pz, 560, 1420 - 92 * s - bob, s, kit='son', face=-1, rim=(-4, -3), beard=False)
    # spray from boots
    r = rng_for(int(lt * 12))
    for i in range(10):
        c.drawCircle(600 + r.random() * 200, 1430 + r.random() * 20 - r.random() * 60, 2 + r.random() * 4,
                     paint('#dfe9f5', 0.4))
    rain(c, t, n=200, seed=22, a=0.25, wind=0.45)
    rain(c, t, n=36, seed=23, a=0.35, width=6, length=150, blur=6, speed=3600, wind=0.45)
    return 0.0


def s6c(c, t, lt):
    sky(c, '#03050a', '#0c1522')
    bokeh(c, t, 37, y0=150, y1=1300, a=0.4, drift=lt * 300)
    floodlight(c, 120, 300, t, 0.9, beams=False)
    s = 1.3 + 0.08 * lt
    profile(c, 540 - (1000 - 640) * s, 930 - 470 * s, s, t, 'son', face=-1, rim_col='#ffd9a0', look_up=-5,
            breath=seg(lt, 0.5, 1.5))
    rain(c, t, n=180, seed=24, a=0.25)
    rain(c, t, n=40, seed=25, a=0.35, width=6, length=150, blur=5, speed=3600)
    return 0.5 * math.exp(-lt * 7)


def s6(c, t, f):
    lt = t - 23.2
    if lt < 1.8:
        return s6a(c, t, lt)
    if lt < 3.4:
        return s6b(c, t, lt - 1.8)
    return s6c(c, t, lt - 3.4)


# =============================================================== S7 28.2-31.0 into the night
def s7(c, t, f):
    lt = t - 28.2
    tilt = 1100 * ease(seg(lt, 0, 2.2))
    sky(c, '#010205', '#0b1626', -1200, H)
    c.save()
    c.translate(0, tilt)
    stands(c, 1560, 2100, t, seed=101, n=600, blur=3)
    floodlight(c, 180, 1500, t, 1.0, beams=False, a=1 - 0.6 * seg(lt, 1, 2.6))
    floodlight(c, 900, 1440, t, 1.0, beams=False, a=1 - 0.6 * seg(lt, 1, 2.6))
    c.restore()
    u = seg(lt, 0, 2.2)
    bx = lerp(600, 540, u)
    by = lerp(1150, 330, ease_out(u))
    r = lerp(18, 2, ease(u))
    ball(c, bx, by, r, rot=lt * 12, a=1 - seg(lt, 1.6, 2.2), lit=(0, 1), motion=(10, -60 * (1 - u)))
    rain(c, t, n=260, seed=26, a=0.28)
    rain(c, t, n=40, seed=27, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.0




# =============================================================== helpers promoted from ep002 (back views)
def head_pos(pose, x, y, s, face=1, rot=0.0):
    """Screen position of a puppet's head centre."""
    dt = D(pose['torso'])
    nx, ny = dt[0] * 62, dt[1] * 62
    dh = D(pose['torso'] + pose['head'])
    hx, hy = nx + dh[0] * 14, ny + dh[1] * 14
    lx, ly = hx * face * s, hy * s
    r = math.radians(rot)
    return x + lx * math.cos(r) - ly * math.sin(r), y + lx * math.sin(r) + ly * math.cos(r)


def back_view(c, pose, x, y, s, kit='son', **kw):
    """Puppet seen from behind: draw the figure, then cover the face with hair."""
    hands = figure(c, pose, x, y, s, kit=kit, front=True, beard=False, **kw)
    hx, hy = head_pos(pose, x, y, s, rot=kw.get('rot', 0.0))
    c.drawCircle(hx, hy + 0.5 * s, 12.8 * s, paint(KITS[kit]['hair'], kw.get('alpha', 1.0), blur=kw.get('blur', 0)))
    return hands


def umbrella(c, x, y, r, a=1.0, rim='#ffd49a', tilt=0.0):
    """Dark umbrella canopy centred at (x, y) (top of the handle), radius r, rim-lit on top."""
    c.save()
    c.translate(x, y)
    c.rotate(tilt)
    path = skia.Path()
    path.moveTo(-r, 0)
    path.cubicTo(-r, -r * 0.9, r, -r * 0.9, r, 0)
    for k in range(4, 0, -1):
        xa, xb = -r + 2 * r * k / 4, -r + 2 * r * (k - 1) / 4
        path.quadTo((xa + xb) / 2, -r * 0.14, xb, 0)
    path.close()
    c.save(); c.translate(0, -5); c.drawPath(path, paint(rim, 0.55 * a)); c.restore()
    c.drawPath(path, paint('#07090d', a))
    c.drawLine(0, 0, 0, r * 0.95, paint('#07090d', a, stroke=max(2, r * 0.05)))
    c.restore()


def chain_fence(c, x0, x1, y0, y1, cell=46, a=0.4, blur=0, col='#9fb2c6'):
    """Chain-link fence (diamond mesh) with posts, screen space."""
    c.save()
    c.clipRect(skia.Rect(x0, y0, x1, y1))
    p = paint(col, a, stroke=2.4, blur=blur)
    h = y1 - y0
    xx = x0 - h
    while xx < x1 + h:
        c.drawLine(xx, y0, xx + h, y1, p)
        c.drawLine(xx + h, y0, xx, y1, p)
        xx += cell
    c.restore()
    pp = paint('#1a222c', 1, stroke=12, blur=blur)
    for k in range(int((x1 - x0) / 360) + 2):
        px = x0 + 60 + k * 360
        c.drawLine(px, y0 - 10, px, y1, pp)
    c.drawLine(x0, y0, x1, y0, paint('#2a3542', 1, stroke=8, blur=blur))
