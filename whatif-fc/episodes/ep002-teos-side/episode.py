"""ep002 — Teo's side. Same final, seen from the son's end of the pitch.
Scene functions take GLOBAL time t. Return value = white flash amount (0..1)."""
import math
import skia
from lib import *
from shots import zoom, bokeh

TEO_HAIR = KITS['son']['hair']

KNEEL = dict(torso=166, head=30, uaL=10, faL=4, uaR=-4, faR=-8, thL=8, shL=-90, thR=-4, shR=-94)
STAND_SIDE = dict(torso=178, head=14, uaL=-6, faL=-4, uaR=8, faR=4, thL=-5, shL=-3, thR=6, shR=4)


def head_pos(pose, x, y, s, face=1, rot=0.0):
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


def stripes(c, cam, off, z_far=160, a=0.16):
    """Mowing stripes that scroll as the camera travels forward by `off` metres."""
    z = 1.0 - (off % 11.0)
    k = 0
    while z < z_far:
        z2 = z + 5.5
        if k % 2 == 0 and z2 > 0.6:
            ya = cam.p(0, max(z, 0.6))[1]
            yb = cam.p(0, z2)[1]
            c.drawRect(skia.Rect(-500, yb, W + 500, ya), paint('#2c6a3a', a))
        z = z2
        k += 1


def bug(c, t, score='1 - 1', clock=None):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, 150, 360, 230), 14, 14), paint('#0b0f16', 0.85))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, 150, 360, 230), 14, 14), paint('#ffffff', 0.15, stroke=3))
    f1 = skia.Font(FONT, 64)
    c.drawString(score, 88, 212, f1, paint('#ffffff'))
    c.drawRect(skia.Rect(212, 162, 216, 218), paint('#ffffff', 0.3))
    c.drawString(clock, 232, 212, f1, paint('#ffd400', 1.0 if (t * 2) % 2 < 1.4 else 0.5))


# =============================================================== kneel (hook 0-3 and loop 28.6-31.5)
def kneel_shot(c, t, zm, drop):
    """Teo on his knees in front of his own goal, ball resting in the net. drop: 0 standing -> 1 kneeling."""
    cam = Cam(horizon=1000, F=1500, h=0.6)
    c.save()
    zoom(c, zm, 520, 1000)
    sky(c, '#02040a', '#0e1d30', 0, 1000)
    floodlight(c, 160, 420, t, 1.0, beam_to=(400, 1300))
    floodlight(c, 930, 380, t, 1.05, beam_to=(700, 1300))
    stands(c, 600, 995, t, seed=111, n=900, cheer=0.1)
    pitch(c, cam, light=(500, 1160, 520))
    pline(c, cam, [(-30, 10), (30, 10)])
    pline(c, cam, [(-9.16, 10), (-9.16, 4.5), (9.16, 4.5), (9.16, 10)])
    goal_frame(c, cam, 10, depth=2.0)
    bx, by = cam.p(2.3, 11.4, 0.11)
    ball(c, bx, by, cam.s(11.4, 0.11), rot=0.8, lit=(-1, -1))
    gx, gy = cam.p(-0.35, 5.0)
    s = cam.s(5.0, 1.9) / 190
    glow(c, gx, gy - 40, 230, '#ffd49a', 0.22)
    c.drawOval(skia.Rect(gx - 110, gy - 10, gx + 90, gy + 12), paint('#000000', 0.4, blur=8))
    d = ease(drop)
    pz = pose_lerp(STAND_SIDE, KNEEL, d)
    breathe = 1.5 * math.sin(t * 3.0) * d
    pz['torso'] += breathe
    hip_y = gy - lerp(95, 51, d) * s
    figure(c, pz, gx, hip_y, s, kit='son', face=1, rim=(-3, -3), rim_a=0.85)
    rain(c, t, n=230, seed=121, a=0.24)
    c.restore()
    rain(c, t, n=36, seed=122, a=0.35, width=6, length=150, blur=6, speed=3600)


def s1(c, t, f):
    # Hook: open ON the impact (ball slams the net at 0.35 s), then cut to him on his knees.
    # ep001 lost 56% of TikTok viewers by 3 s on a static opener, so frame 1 now moves.
    if t < 1.4:
        return s7a(c, t, t + (T_NET - 0.35))
    kneel_shot(c, t, 1.0 + 0.07 * ease((t - 1.4) / 1.6), 1.0)
    return 0.25 * math.exp(-(t - 1.4) * 12)


# =============================================================== S2 3.0-5.8 reverse telephoto: the other end
def s2(c, t, f):
    lt = t - 3.0
    cam = Cam(horizon=980, F=3600, h=1.4)
    vx, vy = cam.p(0, 74.3)
    c.save()
    zoom(c, 1 + 0.45 * ease_out(lt / 0.5) + 0.2 * ease(lt / 2.8), vx, vy - 60)  # whip-in on Dad
    sky(c, '#02040a', '#0d1828', 0, 980)
    stands(c, 560, 975, t, seed=131, n=1000, blur=1.5, cheer=0.4)
    floodlight(c, 830, 360, t, 1.15, beam_to=(600, 1200))
    pitch(c, cam)
    pline(c, cam, [(-30, 75), (30, 75)])
    pline(c, cam, [(-9.16, 75), (-9.16, 69.5), (9.16, 69.5), (9.16, 75)])
    pline(c, cam, [(-20.16, 75), (-20.16, 58.5), (20.16, 58.5), (20.16, 75)])
    goal_frame(c, cam, 75, depth=2.0)
    s = cam.s(74.3, 1.9) / 190
    glow(c, vx, vy - 50, 110, '#ffd49a', 0.3)
    figure(c, dict(POSES['stand'], uaL=-24, uaR=24, faL=-14, faR=14), vx, vy - 88 * s, s, kit='viejo',
           front=True, rim=(3, -2), rim_a=0.8)
    c.restore()
    # foreground Teo, back to camera, out of focus
    sway = 6 * math.sin(lt * 1.7)
    pz = dict(POSES['stand'], uaL=-20, uaR=26, faL=-10, faR=18)
    back_view(c, pz, 250 + sway, 1500, 5.4, blur=5, shade=0.25, rim=(4, -3), rim_a=0.6)
    rain(c, t, n=200, seed=132, a=0.24)
    rain(c, t, n=40, seed=133, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.0


# =============================================================== S3 5.8-9.7 99th minute / coach / tape plant
def s3a(c, t, lt):
    cam = Cam(horizon=900, F=2600, h=1.3)
    gx, gy = cam.p(0, 13.4)
    c.save()
    zoom(c, 1 + 0.08 * lt / 1.7, gx, gy - 200)
    sky(c, '#02040a', '#0d1828', 0, 900)
    floodlight(c, 140, 260, t, 1.0, beam_to=(300, 1300))
    floodlight(c, 960, 230, t, 1.0, beam_to=(780, 1300))
    stands(c, 430, 895, t, seed=141, n=1000, blur=2)
    pitch(c, cam)
    pline(c, cam, [(-30, 14), (30, 14)])
    goal_frame(c, cam, 14, depth=2.0)
    s = cam.s(13.4, 1.9) / 190
    bounce = abs(math.sin(lt * 7)) * 6
    pz = dict(torso=180, head=0, uaL=-55, faL=-35, uaR=55, faR=35, thL=-20, shL=-4, thR=20, shR=4)
    look = ease(seg(lt, 0.7, 1.0))
    pz['head'] = -16 * look
    pz['uaL'] -= 30 * look
    glow(c, gx, gy - 90, 200, '#ffd49a', 0.22)
    figure(c, pz, gx, gy - 86 * s - bounce, s, kit='son', front=True, rim=(3, -3))
    rain(c, t, n=220, seed=142, a=0.25)
    c.restore()
    bug(c, t, '1 - 1', '99:%02d' % int(lt))
    return 0.0


def s3b(c, t, lt):
    sx, sy = shake(lt, 6)
    c.save()
    c.translate(sx, sy)
    sky(c, '#03050a', '#0d1726')
    bokeh(c, t, 143, y0=200, y1=1500, a=0.45, drift=-lt * 80)
    floodlight(c, 900, 280, t, 0.9, beams=False)
    w = math.sin(lt * 11)
    pz = dict(torso=180, head=-8, uaL=-150 + 18 * w, faL=-168 + 10 * w, uaR=150 - 18 * w, faR=168 - 10 * w,
              thL=-6, shL=-4, thR=8, shR=4)
    figure(c, pz, 540, 1250, 5.6, kit='coach', front=True, rim=(4, -3), rim_a=0.9)
    rain(c, t, n=200, seed=144, a=0.26)
    rain(c, t, n=40, seed=145, a=0.35, width=6, length=150, blur=6, speed=3600)
    c.restore()
    return 0.3 * math.exp(-lt * 10)


def s3c(c, t, lt):
    """The plant: Teo yanks his glove strap tight. On his wrist tape, in marker: 1 (his dad's number)."""
    sky(c, '#05070c', '#0b1420')
    bokeh(c, t, 146, y0=100, y1=1500)
    floodlight(c, 120, 240, t, 0.7, beams=False)
    tug = ease_out(seg(lt, 0.0, 0.25)) - 0.15 * ease(seg(lt, 0.35, 0.6))
    c.save()
    c.translate(120 * (1 - tug), 160 * (1 - tug))
    ang = 34
    # forearm + lime sleeve
    c.drawLine(1180 - 10, 1980 - 12, 560 - 10, 1150 - 12, paint('#ffcf8f', 0.9, stroke=250))
    c.drawLine(1180, 1980, 560, 1150, paint('#2a1d16', 1, stroke=240))
    c.drawLine(1260, 2100, 930, 1680, paint('#8fc41f', 1, stroke=290))
    c.drawLine(1080, 1880, 960, 1720, paint('#e6ff9c', 0.5, stroke=10))
    # glove
    c.save()
    c.translate(450, 960)
    c.rotate(ang)
    g = skia.RRect.MakeRectXY(skia.Rect(-180, -150, 180, 150), 100, 100)
    c.save(); c.translate(-10, -8); c.drawRRect(g, paint('#ffcf8f', 0.8)); c.restore()
    c.drawRRect(g, paint('#0c0c0e'))
    for k in range(4):
        fy = -110 + k * 70
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-250, fy, -120, fy + 60), 30, 30), paint('#141417'))
    # strap being pulled
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(120 - 40 * tug, -150, 200 - 40 * tug, 150), 20, 20),
                paint('#8fc41f', 1))
    c.restore()
    # wrist tape with "1"
    c.save()
    c.translate(640, 1230)
    c.rotate(ang)
    for off in (-70, 20):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(off, -135, off + 100, 135), 18, 18), paint('#ece8df'))
        c.drawLine(off + 8, -125, off + 8, 125, paint('#b9b3a8', 0.8, stroke=5))
    c.rotate(-ang)
    fnt = skia.Font(FONT, 170)
    c.drawString("1", -10, 62, fnt, paint('#111111', 0.92))
    c.restore()
    c.restore()
    rain(c, t, n=50, seed=147, a=0.35, width=6, length=150, blur=5, speed=3600)
    return 0.0


def s3(c, t, f):
    lt = t - 5.8
    if lt < 1.7:
        return s3a(c, t, lt)
    if lt < 2.9:
        return s3b(c, t, lt - 1.7)
    return s3c(c, t, lt - 2.9)


# =============================================================== S4 9.7-14.6 the run up / the corner
def s4a(c, t, lt):
    sky(c, '#02040a', '#0d1828', 0, 900)
    c.save()
    c.translate(-((lt * 2200) % 1200), 0)
    for k in range(3):
        c.save(); c.translate(k * 1200, 0)
        stands(c, 500, 1110, t, seed=151, n=500, blur=6, x0=0, x1=1200, cheer=0.5)
        c.restore()
    c.restore()
    floodlight(c, 1300 - ((lt * 500) % 1700), 250, t, 0.8, beams=False)
    g = skia.Paint()
    g.setShader(lin_shader(0, 1110, 0, H, ['#0f2a18', '#1d4a2a']))
    c.drawRect(skia.Rect(0, 1110, W, H), g)
    for k in range(8):
        x = W - ((k * 300 + lt * 3200) % 2400 - 600)
        c.drawRect(skia.Rect(x - 150, 1110, x, H), paint('#2c6a3a', 0.14))
    # halfway line sweeping past
    hx = 1500 - lt * 1500
    if -100 < hx < W + 100:
        c.drawLine(hx, 1110, hx - 260, H, paint('#e9f2ea', 0.5, stroke=10))
    # players waiting in the box ahead (background, slide in)
    for i, (dx, kit) in enumerate(((0, 'navy'), (130, 'red'), (250, 'navy'), (380, 'red'))):
        px = 1500 + dx - lt * 520
        if -100 < px < W + 100:
            figure(c, POSES['ready'], px, 1040, 1.5, kit=kit, face=-1, rim_a=0.5, shade=0.3, blur=2, beard=False)
    ph = lt * 13
    pz = run_pose(ph)
    pz['head'] = 4
    bob = 18 * abs(math.sin(ph))
    s = 2.8
    figure(c, pz, 470, 1420 - 92 * s - bob, s, kit='son', face=1, rim=(4, -3), beard=False)
    r = rng_for(int(lt * 12) + 500)
    for i in range(10):
        c.drawCircle(300 + r.random() * 200, 1430 + r.random() * 20 - r.random() * 60, 2 + r.random() * 4,
                     paint('#dfe9f5', 0.4))
    rain(c, t, n=200, seed=152, a=0.25, wind=-0.35)
    rain(c, t, n=36, seed=153, a=0.35, width=6, length=150, blur=6, speed=3600, wind=-0.35)
    return 0.0


T_C = 1.3  # local catch time in s4b (global 13.3)


def s4b(c, t, lt):
    amp = 12 * math.exp(-(lt - T_C) * 5) if lt > T_C else 0
    sx, sy = shake(lt, amp)
    c.save()
    c.translate(sx, sy)
    zoom(c, 1 + 0.07 * lt / 2.6, 540, 700)
    p = skia.Paint()
    p.setShader(lin_shader(0, 0, 0, H, ['#02040a', '#0b1626', '#14243a']))
    c.drawRect(skia.Rect(-200, -200, W + 200, H + 200), p)
    floodlight(c, 170, 300, t, 1.0, beams=True, beam_to=(500, 1500))
    floodlight(c, 930, 220, t, 1.1, beams=True, beam_to=(600, 1500))
    stands(c, 1420, 2000, t, seed=161, n=600, blur=5, cheer=0.6)
    rise_t = ease_out(seg(lt, 0.2, 1.15)) * (1 - ease_in(seg(lt, 1.55, 2.2)))
    rise_v = ease_out(seg(lt, 0.3, T_C)) * (1 - 0.35 * ease(seg(lt, 1.9, 2.6)))
    # Teo: lime, one arm stretched, a fraction too late
    tp = pose_lerp(dict(torso=180, head=0, uaL=-50, faL=-30, uaR=60, faR=40, thL=-12, shL=-4, thR=14, shR=4),
                   dict(torso=186, head=-16, uaL=-70, faL=-50, uaR=168, faR=176, thL=-14, shL=-60, thR=26, shR=-28),
                   rise_t)
    figure(c, tp, 330, 1380 - 190 * rise_t, 4.4, kit='son', front=True, rim=(3, -3), rim_a=0.9)
    # El Viejo: higher, both gloves
    vp = pose_lerp(dict(torso=180, head=0, uaL=-55, faL=-35, uaR=55, faR=35, thL=-20, shL=-4, thR=20, shR=4),
                   dict(torso=180, head=-14, uaL=-172, faL=172, uaR=172, faR=-172, thL=-10, shL=-40, thR=14, shR=-20),
                   rise_v)
    hands = figure(c, vp, 680, 1330 - 300 * rise_v, 4.8, kit='viejo', front=True, rim=(-3, -3), rim_a=0.9)
    hx, hy = (hands[0][0] + hands[1][0]) / 2, (hands[0][1] + hands[1][1]) / 2 - 10
    if lt < T_C:
        u = seg(lt, 0.0, T_C)
        bx = lerp(1250, hx, u)
        by = lerp(-120, hy, u) - 260 * math.sin(math.pi * u) * (1 - u)
        ball(c, bx, by, lerp(30, 42, u), rot=lt * 10, motion=(60, -30))
    else:
        ball(c, hx, hy, 42, rot=0.4)
    rain(c, t, n=220, seed=162, a=0.26)
    c.restore()
    rain(c, t, n=40, seed=163, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.4 * math.exp(-(lt - T_C) * 8) if lt > T_C else 0.0


def s4(c, t, f):
    lt = t - 9.7
    fl = s4a(c, t, lt) if lt < 2.3 else s4b(c, t, lt - 2.3)
    bug(c, t, '1 - 1', '99:%02d' % (4 + int(lt)))
    return fl


# =============================================================== S5 14.6-20.6 the kick / the chase
T_KICK5 = 0.2


def s5a(c, t, lt):
    cam = Cam(horizon=880, F=1500, h=1.7)
    amp = 10 * math.exp(-(lt - T_KICK5) * 6) if lt > T_KICK5 else 0
    sx, sy = shake(lt, amp)
    c.save()
    c.translate(sx, sy)
    sky(c, '#02040a', '#0d1828', 0, 880)
    floodlight(c, 150, 300, t, 1.0, beam_to=(350, 1300))
    floodlight(c, 940, 260, t, 1.0, beam_to=(760, 1300))
    stands(c, 480, 875, t, seed=171, n=900, blur=2, cheer=0.3)
    pitch(c, cam)
    pline(c, cam, [(-30, 30), (30, 30)])
    pline(c, cam, [(-20.16, 30), (-20.16, 13.5), (20.16, 13.5), (20.16, 30)])
    goal_frame(c, cam, 30, depth=2.0)
    vx, vy = cam.p(0.6, 13)
    s = cam.s(13, 1.9) / 190
    hold = POSES['hold']
    kick = dict(torso=200, head=-10, uaL=-100, faL=-80, uaR=110, faR=140, thL=-4, shL=-4, thR=112, shR=128)
    pz = pose_lerp(hold, kick, ease_out(seg(lt, T_KICK5 - 0.12, T_KICK5 + 0.15)))
    glow(c, vx, vy - 60, 120, '#ffd49a', 0.3)
    figure(c, pz, vx, vy - 90 * s, s, kit='viejo', face=-1, rim=(3, -3))
    # ball from El Viejo's boot, straight over the camera
    if T_KICK5 <= lt < 1.3:
        u = seg(lt, T_KICK5, 1.3)
        Z = lerp(12.6, 0.6, u)
        Y = 0.4 + 9 * math.sin(math.pi * 0.5 * u) ** 0.8
        X = lerp(0.4, 0.2, u)
        if Z > 1.0:
            bx, by = cam.p(X, Z, Y)
            r = cam.s(Z, 0.11)
            glow(c, bx, by, 40 + 3 * r, '#ffffff', 0.35)
            ball(c, bx, by, r, rot=lt * 14, motion=(0, r * 3))
    rain(c, t, n=220, seed=172, a=0.25)
    c.restore()
    # Teo in the foreground, back to us; turns to chase
    turn = ease(seg(lt, 0.7, 1.6))
    pz = dict(POSES['stand'], uaL=-30 - 20 * turn, uaR=30 + 20 * turn, faL=-20, faR=20)
    back_view(c, pz, 400 + 160 * turn, 1640, 5.0, rim=(4, -3), rim_a=0.75, shade=0.15)
    rain(c, t, n=40, seed=173, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.35 * math.exp(-(lt - T_KICK5) * 9) if lt > T_KICK5 else 0.0


def s5b(c, t, lt):
    """Chase cam: following Teo as he sprints back toward his own empty goal; the ball drops in from above."""
    cam = Cam(horizon=900, F=1500, h=1.8)
    travel = 12 * lt
    Zg = 75 - travel
    sky(c, '#02040a', '#0d1828', 0, 900)
    floodlight(c, 170, 330, t, 0.95, beam_to=(380, 1300))
    floodlight(c, 920, 300, t, 0.95, beam_to=(720, 1300))
    stands(c, 520, 896, t, seed=181, n=1000, blur=2, cheer=0.05)
    p = skia.Paint()
    p.setShader(lin_shader(0, cam.hz, 0, H, ['#0c2416', '#163b22', '#1b4a2a']))
    c.drawRect(skia.Rect(-500, cam.hz, W + 500, H + 500), p)
    stripes(c, cam, travel)
    pline(c, cam, [(-34, max(Zg, 1)), (34, max(Zg, 1))])
    pline(c, cam, [(-20.16, Zg), (-20.16, Zg - 16.5), (20.16, Zg - 16.5), (20.16, Zg)])
    pline(c, cam, [(-9.16, Zg), (-9.16, Zg - 5.5), (9.16, Zg - 5.5), (9.16, Zg)])
    pline(c, cam, [(-34, 1), (-34, Zg)])
    pline(c, cam, [(34, 1), (34, Zg)])
    goal_frame(c, cam, Zg, depth=2.0)
    gx, gy = cam.p(0, Zg)
    glow(c, gx, gy - 30, 150, '#ffe2b0', 0.25 + 0.1 * math.sin(t * 5))
    # the ball, coming down from above
    Zb = 10 + 3.0 * lt
    Yb = 16 - 2.4 * lt
    bx, by = cam.p(0.6, Zb, Yb)
    r = cam.s(Zb, 0.11)
    if by > -50:
        glow(c, bx, by, 60, '#ffffff', 0.25)
        ball(c, bx, by, max(r, 7), rot=lt * 8, motion=(0, -40))
    # Teo, from behind, sprinting
    ph = lt * 14
    sw = math.sin(ph)
    pz = dict(torso=180, head=0, uaL=-25 + 40 * sw, faL=-10 + 50 * sw, uaR=25 + 40 * sw, faR=10 + 50 * sw,
              thL=-8 + 10 * sw, shL=-6 + 8 * sw, thR=8 + 10 * sw, shR=6 + 8 * sw)
    tx, ty = cam.p(-0.95, 5.5)
    s = cam.s(5.5, 1.9) / 190
    bob = 14 * abs(math.sin(ph))
    c.drawOval(skia.Rect(tx - 70, ty - 8, tx + 70, ty + 10), paint('#000000', 0.35, blur=8))
    back_view(c, pz, tx, ty - 92 * s - bob, s, rim=(3, -3), rim_a=0.85)
    r_ = rng_for(int(lt * 14) + 900)
    for i in range(12):
        c.drawCircle(tx - 80 + r_.random() * 160, ty - r_.random() * 40, 2 + r_.random() * 4, paint('#dfe9f5', 0.35))
    rain(c, t, n=230, seed=182, a=0.26)
    rain(c, t, n=40, seed=183, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.0


def s5(c, t, f):
    lt = t - 14.6
    fl = s5a(c, t, lt) if lt < 1.8 else s5b(c, t, lt - 1.8)
    if lt >= 1.8:
        bug(c, t, '1 - 1', '99:%02d' % (9 + int(lt)))
    return fl


# =============================================================== S6 20.6-26.0 the slowdown / his face
def run_phase(lt):
    """Stride phase: full sprint, then easing off after ~2 s (integral of a falling rate)."""
    a, b, r0, r1 = 2.0, 3.0, 14.0, 5.0
    if lt < a:
        return r0 * lt
    if lt < b:
        u = lt - a
        return r0 * a + r0 * u + (r1 - r0) * u * u / (2 * (b - a))
    return r0 * a + (r0 + r1) / 2 * (b - a) + r1 * (lt - b)


def s6a(c, t, lt):
    rate = 14 if lt < 2.0 else lerp(14, 5, seg(lt, 2.0, 3.0))
    speed = rate / 14
    ph = run_phase(lt)
    scroll = (ph / 14) * 3000
    sky(c, '#03050a', '#0d1828', 0, 1000)
    c.save()
    c.translate((scroll * 0.4) % 1200 - 1200, 0)
    for k in range(3):
        c.save(); c.translate(k * 1200, 0)
        stands(c, 380, 1000, t, seed=191, n=500, blur=9, x0=0, x1=1200)
        c.restore()
    c.restore()
    g = skia.Paint()
    g.setShader(lin_shader(0, 1000, 0, H, ['#0f2a18', '#1d4a2a']))
    c.drawRect(skia.Rect(0, 1000, W, H), g)
    for k in range(6):
        x = (k * 420 + scroll) % 2520 - 600
        c.drawRect(skia.Rect(x, 1000, x + 210, H), paint('#2c6a3a', 0.14))
    glow(c, 540, 1220, 520, '#ffd9a0', 0.15)
    pz = run_pose(ph, lean=lerp(170, 162, speed))
    pz['head'] = 4
    s = 10.5
    bob = 16 * abs(math.sin(ph)) * speed
    figure(c, pz, 560, 1222 - 95 * s - bob, s, kit='son', face=-1, rim=(-4, -3), beard=False)
    # spray off the boots, fading as he slows
    r = rng_for(int(ph * 1.5) + 1300)
    for i in range(int(6 + 18 * speed)):
        c.drawCircle(380 + r.random() * 420, 1230 - r.random() * 140 * speed, 3 + r.random() * 8,
                     paint('#dfe9f5', 0.35 * speed + 0.1))
    rain(c, t, n=200, seed=192, a=0.25, wind=-0.4 * speed)
    rain(c, t, n=36, seed=193, a=0.35, width=6, length=150, blur=6, speed=3600, wind=-0.4 * speed)
    return 0.0


def s6b(c, t, lt):
    sky(c, '#03050a', '#0c1522')
    bokeh(c, t, 194, y0=150, y1=1300, a=0.4, drift=lt * 60)
    floodlight(c, 960, 280, t, 0.9, beams=False)
    s = 1.34 + 0.06 * lt
    profile(c, 540 - (1000 - 640) * s, 900 - 470 * s, s, t, 'son', face=-1, rim_col='#ffd9a0', look_up=-8,
            breath=seg(lt, 0.3, 1.3))
    rain(c, t, n=180, seed=195, a=0.25)
    rain(c, t, n=40, seed=196, a=0.35, width=6, length=150, blur=5, speed=3600)
    return 0.0


def s6(c, t, f):
    lt = t - 20.6
    return s6a(c, t, lt) if lt < 3.6 else s6b(c, t, lt - 3.6)


# =============================================================== S7 26.0-31.5 from inside the net / loop
T_NET = 1.2  # local (global 27.2)


def s7a(c, t, lt):
    cam = Cam(horizon=900, F=1500, h=1.0)
    amp = 0.0
    if lt >= T_NET:
        k = lt - T_NET
        amp = 0.45 * math.exp(-k * 3.0) * math.cos(k * 13) + 0.12
    sx, sy = shake(lt, 14 * math.exp(-(lt - T_NET) * 6) if lt > T_NET else 0)
    c.save()
    c.translate(sx, sy)
    sky(c, '#02040a', '#0d1828', 0, 900)
    floodlight(c, 180, 330, t, 1.0, beam_to=(380, 1300))
    floodlight(c, 900, 290, t, 1.0, beam_to=(720, 1300))
    stands(c, 470, 896, t, seed=201, n=1000, blur=2, cheer=ease(seg(lt, T_NET, T_NET + 0.5)) * 0.8)
    pitch(c, cam)
    pline(c, cam, [(-30, 1.6), (30, 1.6)], w=6)
    pline(c, cam, [(-9.16, 1.6), (-9.16, 7.1), (9.16, 7.1), (9.16, 1.6)])
    pline(c, cam, [(-20.16, 1.6), (-20.16, 18.1), (20.16, 18.1), (20.16, 1.6)])
    # Teo, stopped at the edge of the six-yard box
    tx, ty = cam.p(-0.9, 8.5)
    s = cam.s(8.5, 1.9) / 190
    up = ease(seg(lt, T_NET + 0.3, T_NET + 1.0))
    pz = dict(torso=180, head=-4 * up, uaL=-8 - 132 * up, faL=-4 + 104 * up, uaR=10 + 130 * up, faR=6 - 100 * up,
              thL=-5, shL=-3, thR=6, shR=4)
    glow(c, tx, ty - 80, 160, '#ffd49a', 0.22)
    figure(c, pz, tx, ty - 95 * s, s, kit='son', front=True, rim=(3, -3), rim_a=0.85)
    # ball bouncing in toward the camera
    if lt < T_NET:
        u = seg(lt, 0.0, T_NET)
        Z = lerp(14, 1.9, u)
        Y = 0.11 + 1.1 * abs(math.sin(math.pi * 1.5 * u)) * (1 - u)
        X = lerp(0.7, 0.15, u)
        bx, by = cam.p(X, Z, Y)
        r = cam.s(Z, 0.11)
    else:
        k = lt - T_NET
        push = 1 + 0.1 * math.exp(-k * 5) * math.cos(k * 16)
        bx, by = cam.p(0.15, 1.9, 0.11)
        r = cam.s(1.9, 0.11) * push
        by += 30 * ease(k / 1.2)
    ball(c, bx, by, r, rot=lt * 9, lit=(-1, -1))
    rain(c, t, n=220, seed=202, a=0.24)
    # net in the foreground (square mesh), bulging where the ball hits
    cxp, cyp = bx, by
    sig = 300.0
    cell = 96
    pn = paint('#eef3f8', 0.5, stroke=4.5, blur=1.2)
    pd = paint('#000000', 0.4, stroke=8, blur=3)

    def vert(x, y):
        dx, dy = x - cxp, y - cyp
        gg = math.exp(-(dx * dx + dy * dy) / (2 * sig * sig))
        return x + dx * amp * gg, y + dy * amp * gg + 30 * amp * gg

    for i in range(-2, 14):
        for vertical in (True, False):
            path = skia.Path()
            for j in range(0, 26):
                x, y = (i * cell, j * cell - 100) if vertical else (j * cell - 200, i * cell * 1.6 - 100)
                x, y = vert(x, y)
                (path.moveTo if j == 0 else path.lineTo)(x, y)
            c.drawPath(path, pd)
            c.drawPath(path, pn)
    c.restore()
    rain(c, t, n=36, seed=203, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.35 * math.exp(-(lt - T_NET) * 7) if lt > T_NET else 0.0


def s7(c, t, f):
    lt = t - 26.0
    if lt < 2.6:
        fl = s7a(c, t, lt)
        if lt >= T_NET:
            bug(c, t, '1 - 2', '99:%02d' % 21)
        return fl
    k = lt - 2.6
    kneel_shot(c, t, lerp(0.97, 1.0, ease(k / 2.9)), seg(k, 0.25, 1.0))
    return 0.0


SCENES = [(0.0, 3.0, s1), (3.0, 5.8, s2), (5.8, 9.7, s3), (9.7, 14.6, s4), (14.6, 20.6, s5),
          (20.6, 26.0, s6), (26.0, 31.5, s7)]
