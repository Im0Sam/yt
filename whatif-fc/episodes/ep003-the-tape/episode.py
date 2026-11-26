"""ep003 — The Tape. Flashback, fourteen years earlier: Teo's first match, the night his dad wasn't there.
Why 'TEO' is on El Viejo's tape, and why Teo wears a '1' (the detail planted in ep002).
Scene functions take GLOBAL time t. Return value = white flash amount (0..1)."""
import math
import skia
from lib import *
from shots import zoom, bokeh, back_view, umbrella, chain_fence

KID_S = 2.3          # puppet scale for 8-year-old Teo in the front-on goal shots
T_IMP = 0.35         # local impact time in kid_save


# =============================================================== shared: the community pitch, front-on goal
def community_bg(c, t, cheer=0.0):
    sky(c, '#02040a', '#0d1828', 0, 1150)
    # tree line + houses beyond the fence
    r = rng_for(301)
    path = skia.Path()
    path.moveTo(-50, 1000)
    for i in range(24):
        path.lineTo(-50 + i * 52, 860 - r.random() * 120)
    path.lineTo(W + 50, 1000)
    path.close()
    c.drawPath(path, paint('#05080c'))
    for i in range(6):  # lit windows
        wx, wy = 80 + r.random() * 900, 900 + r.random() * 60
        c.drawRect(skia.Rect(wx, wy, wx + 26, wy + 20), paint('#ffcf8a', 0.35))
    floodlight(c, 120, 420, t, 0.8, beam_to=(400, 1400))
    chain_fence(c, -20, W + 20, 880, 1120, a=0.28)
    g = skia.Paint()
    g.setShader(lin_shader(0, 1110, 0, H, ['#0d2615', '#1a4527']))
    c.drawRect(skia.Rect(-200, 1110, W + 200, H + 200), g)
    glow(c, 540, 1350, 520, '#ffd9a0', 0.12)


def goal_front(c, x0=90, x1=990, top=640, ground=1460):
    pp = paint('#f4f7fb', 1, stroke=26)
    c.drawLine(x0, ground, x0, top, pp)
    c.drawLine(x1, ground, x1, top, pp)
    c.drawLine(x0, top, x1, top, pp)
    np_ = paint('#dfe9f5', 0.16, stroke=2.5)
    for i in range(1, 14):
        x = lerp(x0 + 60, x1 - 60, i / 14)
        c.drawLine(x, top + 60, x, ground - 80, np_)
    for j in range(1, 9):
        y = lerp(top + 60, ground - 80, j / 9)
        c.drawLine(x0 + 60, y, x1 - 60, y, np_)
    c.drawLine(x0, top, x0 + 60, top + 60, np_)
    c.drawLine(x1, top, x1 - 60, top + 60, np_)


READY_K = dict(torso=172, head=6, uaL=40, faL=60, uaR=50, faR=70, thL=24, shL=-10, thR=30, shR=-6)
DIVE_K = dict(torso=180, head=-6, uaL=-172, faL=-176, uaR=-160, faR=-170, thL=-10, shL=-18, thR=18, shR=8)


def kid_save(c, t, lt, mirror=False, zm=1.0):
    """Front-on: 8-year-old Teo dives and catches a penalty. Ball hits his gloves at lt = T_IMP.
    lt < 0: he waits in his crouch (used for the loop ending)."""
    amp = 16 * math.exp(-(lt - T_IMP) * 6) if lt > T_IMP else 0
    sx, sy = shake(lt, amp)
    c.save()
    c.translate(sx, sy)
    zoom(c, zm, 540, 1150)
    if mirror:
        c.translate(W, 0)
        c.scale(-1, 1)
    community_bg(c, t)
    goal_front(c)
    c.drawOval(skia.Rect(380, 1440, 720, 1490), paint('#000000', 0.35, blur=10))
    if lt < 0:
        sway = math.sin(t * 4.0) * 10
        pz = dict(READY_K)
        pz['uaL'] += 6 * math.sin(t * 4); pz['uaR'] -= 6 * math.sin(t * 4)
        figure(c, pz, 540 + sway, 1460 - 80 * KID_S, KID_S, kit='son', front=True, rim=(-3, -3), rim_a=0.85)
        hands = None
    else:
        d = ease_out(seg(lt, 0.0, 0.42))
        fall = ease_in(seg(lt, 0.5, 1.0))
        x = lerp(540, 790, d) + 40 * fall
        y = lerp(1460 - 80 * KID_S, 1080, d) + (1350 - 1080) * fall
        rot = lerp(0, -62, d) - 18 * fall
        pz = pose_lerp(READY_K, DIVE_K, ease_out(seg(lt, 0.0, 0.3)))
        hands = figure(c, pz, x, y, KID_S, kit='son', front=True, rot=rot, rim=(-3, -3), rim_a=0.9)
        if lt > T_IMP:
            for k in range(14):  # spray off the gloves
                rr = rng_for(int(k * 7 + 3))
                ang = rr.random() * 6.28
                dist = (lt - T_IMP) * (300 + 500 * rr.random())
                hx = (hands[0][0] + hands[1][0]) / 2
                hy = (hands[0][1] + hands[1][1]) / 2
                c.drawCircle(hx + math.cos(ang) * dist, hy + math.sin(ang) * dist + 200 * (lt - T_IMP) ** 2,
                             3 + rr.random() * 5, paint('#dfe9f5', 0.5 * math.exp(-(lt - T_IMP) * 3)))
    rain(c, t, n=220, seed=311, a=0.24)
    # ball: flies from the camera (big, bottom) into his gloves
    if hands is not None:
        hx = (hands[0][0] + hands[1][0]) / 2
        hy = (hands[0][1] + hands[1][1]) / 2 - 8
        if lt < T_IMP:
            u = ease_in(seg(lt, -0.05, T_IMP))
            bx, by = lerp(470, hx, u), lerp(1900, hy, u)
            ball(c, bx, by, lerp(190, 30, u ** 0.7), rot=lt * 14, motion=(lerp(-40, -120, u), lerp(160, 260, u)))
        else:
            ball(c, hx, hy, 30, rot=0.6)
    c.restore()
    rain(c, t, n=36, seed=312, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.4 * math.exp(-(lt - T_IMP) * 9) if lt > T_IMP else 0.0


# =============================================================== the parents at the fence (one gap)
PARENTS = [(60, 2.5, -4), (210, 2.35, 6), (370, 2.55, -2), (740, 2.4, 3), (900, 2.6, -5), (1050, 2.4, 2)]


def fence_scene(c, t, zm=1.0, blur=0.0, kid=None):
    """Parents with umbrellas behind the fence; an empty, lit spot in the middle (x ~ 560).
    kid = (x, y, s) draws young Teo from behind in the foreground."""
    c.save()
    zoom(c, zm, 560, 1050)
    sky(c, '#02040a', '#0c1626', 0, 900)
    floodlight(c, 930, 330, t, 0.9, beam_to=(600, 1300))
    c.drawRect(skia.Rect(-200, 860, W + 200, 1250), paint('#060a10'))
    # puddle of light where his dad always stood
    glow(c, 560, 1180, 230, '#ffd49a', 0.35)
    c.drawOval(skia.Rect(440, 1165, 690, 1205), paint('#ffe2b0', 0.18, blur=6))
    for i, (px, s, tilt) in enumerate(PARENTS):
        sway = 3 * math.sin(t * 1.3 + i)
        pz = dict(POSES['stand'], uaR=-150, faR=-175, head=sway * 0.5)
        hands = figure(c, pz, px, 1190 - 92 * s, s, kit='shadow', front=True, rim=(3, -3), rim_a=0.55,
                       blur=blur, rim_col='#ffc98a')
        umbrella(c, hands[1][0] - 10, hands[1][1] - 120, 110 + 8 * (i % 2), tilt=tilt + sway, rim='#ffc98a')
    chain_fence(c, -40, W + 40, 820, 1250, a=0.42, blur=blur * 0.5)
    g = skia.Paint()
    g.setShader(lin_shader(0, 1250, 0, H, ['#0d2615', '#1a4527']))
    c.drawRect(skia.Rect(-200, 1250, W + 200, H + 300), g)
    rain(c, t, n=200, seed=321, a=0.22, blur=blur * 0.3)
    c.restore()
    if kid:
        kx, ky, ks = kid
        pz = dict(POSES['stand'], uaL=-14, faL=-6, uaR=16, faR=10, head=8)
        back_view(c, pz, kx, ky, ks, rim=(4, -3), rim_a=0.7, shade=0.2)
    rain(c, t, n=36, seed=322, a=0.35, width=6, length=150, blur=6, speed=3600)


# =============================================================== S1 0-2.8 hook: the save, then the gap
def s1(c, t, f):
    if t < 1.5:
        return kid_save(c, t, t)
    lt = t - 1.5
    fence_scene(c, t, zm=1.0 + 0.25 * ease(lt / 1.3))
    return 0.25 * math.exp(-lt * 12)


# =============================================================== S2 2.8-5.2 whip-in: tiny keeper, giant goal
def s2(c, t, f):
    lt = t - 2.8
    cam = Cam(horizon=1000, F=1700, h=1.2)
    gx, gy = cam.p(0, 11.0)
    c.save()
    zoom(c, 1 + 0.55 * ease_out(lt / 0.45) + 0.12 * ease(lt / 2.4), gx, gy - 140)
    sky(c, '#02040a', '#0d1828', 0, 1000)
    floodlight(c, 180, 380, t, 0.85, beam_to=(420, 1300))
    c.drawRect(skia.Rect(-300, 820, W + 300, 1000), paint('#05080c'))
    chain_fence(c, -300, W + 300, 860, 1000, a=0.25, cell=30)
    pitch(c, cam, light=(540, 1150, 400))
    pline(c, cam, [(-30, 11.0), (30, 11.0)])
    pline(c, cam, [(-9.16, 11.0), (-9.16, 5.5), (9.16, 5.5), (9.16, 11.0)])
    goal_frame(c, cam, 11.0, depth=2.0)
    kx, ky = cam.p(0, 10.4)
    s = cam.s(10.4, 1.3) / 190   # 1.3 m tall: a kid in a full-size goal
    glow(c, kx, ky - 60, 120, '#ffd49a', 0.3)
    pz = dict(READY_K)
    pz['uaL'] += 8 * math.sin(t * 5); pz['uaR'] -= 8 * math.sin(t * 5)
    figure(c, pz, kx + 6 * math.sin(t * 2.5), ky - 80 * s, s, kit='son', front=True, rim=(3, -3), rim_a=0.85)
    rain(c, t, n=220, seed=331, a=0.24)
    c.restore()
    rain(c, t, n=36, seed=332, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.3 * math.exp(-lt * 10)


# =============================================================== S3 5.2-9.4 across town: his dad's final
def s3a(c, t, lt):
    cam = Cam(horizon=900, F=1500, h=1.5)
    c.save()
    zoom(c, 1.05 + 0.08 * lt / 2.1, 540, 900)
    sky(c, '#02040a', '#0e1d30', 0, 900)
    stands(c, 280, 895, t, seed=341, n=1500, blur=1.5, cheer=0.9)
    floodlight(c, 150, 230, t, 1.1, beam_to=(380, 1400))
    floodlight(c, 940, 200, t, 1.15, beam_to=(720, 1400))
    pitch(c, cam, light=(540, 1250, 520))
    # tunnel mouth glow
    glow(c, 540, 1000, 260, '#ffe2b0', 0.25)
    # El Viejo, 27, walking out toward camera
    ph = lt * 5.2
    sw = math.sin(ph)
    pz = dict(torso=180, head=-2, uaL=-12 * sw, faL=-6 * sw - 10, uaR=12 * sw, faR=6 * sw + 10,
              thL=10 * sw, shL=10 * sw - 4, thR=-10 * sw, shR=-10 * sw + 4)
    s = lerp(2.7, 3.3, lt / 2.1)
    bob = 5 * abs(sw)
    figure(c, pz, 540, 1480 - 92 * s - bob, s, kit='viejo_young', front=True, rim=(4, -3), rim_a=0.95)
    rain(c, t, n=240, seed=342, a=0.25)
    c.restore()
    rain(c, t, n=40, seed=343, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.3 * math.exp(-lt * 10)


def s3b(c, t, lt):
    sky(c, '#03050a', '#0c1522')
    bokeh(c, t, 344, y0=150, y1=1300, a=0.45, drift=-lt * 50)
    floodlight(c, 160, 260, t, 0.8, beams=False)
    s = 1.30 + 0.05 * lt
    profile(c, 560 - 640 * s, 960 - 470 * s, s, t, 'viejo', face=1, rim_col='#ffd9a0', look_up=-10 + 6 * ease(lt / 2),
            young=True)
    rain(c, t, n=180, seed=345, a=0.25)
    rain(c, t, n=40, seed=346, a=0.35, width=6, length=150, blur=5, speed=3600)
    return 0.2 * math.exp(-lt * 10)


def s3(c, t, f):
    lt = t - 5.2
    return s3a(c, t, lt) if lt < 2.1 else s3b(c, t, lt - 2.1)


# =============================================================== S4 9.4-14.2 the penalty
T_KICK = 1.95


def s4a(c, t, lt):
    """Behind young Teo: a crimson striker runs up to the spot."""
    cam = Cam(horizon=930, F=1500, h=1.1)
    c.save()
    zoom(c, 1 + 0.06 * lt / 2.1, 540, 1100)
    sky(c, '#02040a', '#0d1828', 0, 930)
    floodlight(c, 880, 380, t, 0.9, beam_to=(620, 1300))
    c.drawRect(skia.Rect(-200, 760, W + 200, 930), paint('#05080c'))
    chain_fence(c, -200, W + 200, 800, 930, a=0.22, cell=26)
    for i, (px, s_) in enumerate(((160, 1.1), (300, 1.0), (760, 1.1), (900, 1.05))):  # parents far away
        figure(c, POSES['stand'], px, 905 - 92 * s_, s_, kit='shadow', front=True, rim_a=0.4, rim_col='#ffc98a')
    pitch(c, cam, light=(540, 1180, 420))
    pline(c, cam, [(-9.16, 1.0), (-9.16, 5.5), (9.16, 5.5), (9.16, 1.0)])
    spot = cam.p(0, 11.0)
    c.drawCircle(spot[0], spot[1], 5, paint('#e9f2ea', 0.6))
    # striker
    run = ease_in(seg(lt, 0.2, T_KICK))
    Z = lerp(16.5, 11.6, run)
    sx_, sy_ = cam.p(-0.5 + 0.3 * run, Z)
    s = cam.s(Z, 1.35) / 190
    if lt < T_KICK:
        pz = run_pose(lt * 11, lean=168) if lt > 0.2 else dict(POSES['stand'])
    else:
        pz = dict(torso=196, head=-8, uaL=-100, faL=-80, uaR=110, faR=140, thL=-4, shL=-4, thR=100, shR=120)
    figure(c, pz, sx_, sy_ - 92 * s, s, kit='red', face=-1, rim=(3, -3), rim_a=0.8, beard=False)
    if lt < T_KICK:
        bx, by = cam.p(0, 11.0, 0.11)
        ball(c, bx, by, cam.s(11.0, 0.11), rot=0.3)
    else:
        u = seg(lt, T_KICK, T_KICK + 0.25)
        bx, by = cam.p(lerp(0, 1.8, u), lerp(11.0, 1.5, u), lerp(0.11, 1.0, u))
        ball(c, bx, by, cam.s(lerp(11.0, 1.5, u), 0.11), rot=lt * 12, motion=(-20, -30))
    rain(c, t, n=220, seed=351, a=0.24)
    c.restore()
    # young Teo from behind, foreground, crouched
    pz = dict(READY_K)
    back_view(c, pz, 300 + 8 * math.sin(t * 3), 1770, 4.6, rim=(4, -3), rim_a=0.7, shade=0.1)
    rain(c, t, n=36, seed=352, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.0


def s4(c, t, f):
    lt = t - 9.4
    if lt < 2.1:
        return s4a(c, t, lt)
    return kid_save(c, t, (lt - 2.1) * 0.75, mirror=True, zm=1.12)  # slightly slowed; impact at global 11.97


# =============================================================== S5 14.2-17.6 he looks at the fence
def s5(c, t, f):
    lt = t - 14.2
    blur = 10 * (1 - ease(seg(lt, 0.3, 1.4)))
    fence_scene(c, t, zm=1.0 + 0.1 * ease(lt / 3.4), blur=blur, kid=(230 - 20 * ease(lt / 3.4), 1780, 4.6))
    return 0.2 * math.exp(-lt * 10)


# =============================================================== S6 17.6-23.6 home at midnight / the tape
def s6a(c, t, lt):
    """Dark living room. Door opens: dad's silhouette with a kit bag. Teo asleep on the sofa in his gloves,
    a marker in his hand (the plant)."""
    c.save()
    zoom(c, 1 + 0.06 * lt / 2.8, 540, 1100)
    c.drawRect(skia.Rect(-100, -100, W + 100, H + 100), paint('#07080c'))
    # window with rain
    win = skia.Rect(90, 420, 470, 900)
    c.drawRect(win, paint('#0c1726'))
    c.save(); c.clipRect(win)
    glow(c, 380, 520, 200, '#9fc4e6', 0.18)
    rain(c, t, n=120, seed=361, a=0.3, length=30)
    c.restore()
    c.drawRect(win, paint('#15110e', 1, stroke=18))
    c.drawLine(280, 420, 280, 900, paint('#15110e', 1, stroke=10))
    # door at right: light wedge opening
    op = ease(seg(lt, 0.15, 0.9))
    dx0, dx1, dy0, dy1 = 760, 1000, 560, 1380
    c.drawRect(skia.Rect(dx0, dy0, dx1, dy1), paint('#050506'))
    c.drawRect(skia.Rect(dx0, dy0, dx0 + (dx1 - dx0) * op, dy1), paint('#ffcf8a', 0.85))
    wedge = skia.Path()
    wedge.moveTo(dx0, dy1); wedge.lineTo(dx0 + (dx1 - dx0) * op, dy1)
    wedge.lineTo(dx0 - 520 * op, H + 50); wedge.lineTo(dx0 - 900 * op, H + 50); wedge.close()
    p = skia.Paint(AntiAlias=True)
    p.setShader(lin_shader(dx0, dy1, dx0 - 600, H, [('#ffcf8a', 0.35), ('#ffcf8a', 0.0)]))
    c.drawPath(wedge, p)
    if op > 0.3:  # dad in the doorway with his kit bag
        fa = ease(seg(op, 0.3, 0.8))
        pz = dict(POSES['stand'], uaR=14, faR=8, uaL=-6, faL=-4)
        hands = figure(c, pz, dx0 + 110, dy1 - 92 * 4.0, 4.0, kit='shadow', front=True, rim_a=0.0, alpha=fa)
        hx, hy = hands[1]
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(hx - 20, hy, hx + 90, hy + 70), 20, 20), paint('#050506', fa))
    # lamp
    glow(c, 640, 760, 260, '#ffbf70', 0.22)
    # sofa
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(40, 1080, 760, 1420), 60, 60), paint('#2a1f22'))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(40, 960, 760, 1180), 60, 60), paint('#33262a'))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(20, 1000, 140, 1420), 50, 50), paint('#3a2c30'))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(660, 1000, 780, 1420), 50, 50), paint('#3a2c30'))
    # Teo asleep, lying along the sofa, head on the left armrest
    breathe = 1.2 * math.sin(t * 2.2)
    pz = dict(torso=180, head=-10, uaL=150, faL=60, uaR=120 + breathe, faR=40, thL=10, shL=60, thR=20, shR=70)
    hands = figure(c, pz, 470, 1070, 2.8, kit='son', front=False, rot=-90, rim=(3, -3), rim_a=0.55,
                   rim_col='#ffbf70')
    hx, hy = hands[1]
    c.drawCircle(hx, hy, 28, paint('#0c0c0e'))                      # oversized glove
    c.drawCircle(hx, hy, 28, paint('#ffbf70', 0.4, stroke=3))
    # the marker in his glove (plant): black body, white band, cap off
    c.save(); c.translate(hx + 6, hy - 6); c.rotate(-35); c.scale(2.0, 2.0)
    glow(c, 0, -20, 50, '#ffbf70', 0.25)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-8, -60, 8, 30), 6, 6), paint('#101012'))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-8, -60, 8, 30), 6, 6), paint('#ffbf70', 0.6, stroke=2))
    c.drawRect(skia.Rect(-8, -40, 8, -28), paint('#f2f2f2', 0.9))
    c.drawRect(skia.Rect(-3, -72, 3, -60), paint('#101012'))
    c.restore()
    c.restore()
    return 0.0


def wrist(c, cx, cy, ang, sleeve, text, reveal=1.0, scale=1.0, skin='#2a1d16', blur=0.0, rim='#ffcf8f',
          font_size=110, tape='#ece8df', marker=None):
    """Close-up forearm + wrist tape seen from above. text drawn along the tape, revealed left->right."""
    c.save()
    c.translate(cx, cy)
    c.rotate(ang)
    c.scale(scale, scale)
    # forearm runs from the wrist (0,0) down-right off screen
    c.drawLine(10, -12, 900, -12, paint(rim, 0.85, stroke=230, blur=blur))
    c.drawLine(0, 0, 900, 0, paint(skin, 1, stroke=220, blur=blur))
    c.drawLine(560, 0, 1100, 0, paint(sleeve, 1, stroke=270, blur=blur))
    # hand / fist end
    fist = skia.RRect.MakeRectXY(skia.Rect(-330, -125, -40, 125), 90, 90)
    c.save(); c.translate(6, -10); c.drawRRect(fist, paint(rim, 0.8, blur=blur)); c.restore()
    c.drawRRect(fist, paint(skin, 1, blur=blur))
    # tape bands
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-30, -122, 300, 122), 18, 18), paint(tape, 1, blur=blur))
    for k in range(4):
        x = -10 + k * 82
        c.drawLine(x, -112, x, 112, paint('#b9b3a8', 0.7, stroke=4, blur=blur))
    fnt = skia.Font(FONT, font_size)
    w = fnt.measureText(text)
    x0 = 135 - w / 2
    c.save()
    c.clipRect(skia.Rect(x0 - 5, -200, x0 - 5 + (w + 10) * reveal, 200))
    c.drawString(text, x0, font_size * 0.36, fnt, paint('#111111', 0.92, blur=blur * 0.5))
    c.restore()
    if marker is not None:
        mx = x0 + w * reveal
        my = font_size * 0.1 + 18 * math.sin(marker * 40)
        c.save(); c.translate(mx, my - 20); c.rotate(-60)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-22, -330, 22, 0), 14, 14), paint('#101012'))
        c.drawRect(skia.Rect(-22, -250, 22, -215), paint('#f2f2f2', 0.9))
        c.drawRect(skia.Rect(-7, 0, 7, 22), paint('#101012'))
        c.restore()
    c.restore()


def s6b(c, t, lt):
    """Dad's wrist: he writes T-E-O on his own tape."""
    c.drawRect(skia.Rect(0, 0, W, H), paint('#0a0807'))
    bokeh(c, t, 362, y0=100, y1=1500, a=0.3, drift=lt * 30)
    glow(c, 820, 420, 600, '#ffbf70', 0.22)
    rev = ease(seg(lt, 0.3, 2.3))
    c.save()
    zoom(c, 1.0 + 0.05 * lt / 3.2, 540, 1000)
    wrist(c, 380, 1000, 28, '#262a31', 'TEO', reveal=rev, font_size=150, marker=lt if rev < 1 else None)
    c.restore()
    return 0.0


def s6(c, t, f):
    lt = t - 17.6
    return s6a(c, t, lt) if lt < 2.8 else s6b(c, t, lt - 2.8)


# =============================================================== S7 23.6-28.4 what he never knew
def s7a(c, t, lt):
    """The marker slips out of the sleeping boy's glove and rolls on the floor."""
    c.drawRect(skia.Rect(0, 0, W, H), paint('#08070a'))
    glow(c, 300, 600, 500, '#ffbf70', 0.16)
    # sofa edge + floorboards
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-100, 200, 1180, 900), 80, 80), paint('#2a1f22'))
    for k in range(9):
        y = 980 + k * 120
        c.drawLine(-50, y, W + 50, y + 30, paint('#1a1512', 1, stroke=4))
    c.drawRect(skia.Rect(-50, 900, W + 50, H + 50), paint('#130f0d', 0.6))
    # glove hanging over the sofa edge
    gx, gy = 620, 860
    c.drawCircle(gx, gy, 120, paint('#0c0c0e'))
    c.drawCircle(gx, gy, 120, paint('#ffbf70', 0.35, stroke=6))
    c.drawLine(gx - 60, gy - 120, gx - 220, gy - 400, paint('#7cab19', 1, stroke=150))
    # marker falls
    u = ease_in(seg(lt, 0.4, 0.95))
    bounce = 0.0
    if lt > 0.95:
        k = lt - 0.95
        bounce = 60 * abs(math.sin(k * 9)) * math.exp(-k * 5)
    mx = gx + 40 + 220 * ease_out(seg(lt, 0.95, 2.0))
    my = lerp(gy + 40, 1420, u) - bounce
    rot = lerp(-35, 80, u) + 200 * ease_out(seg(lt, 0.95, 2.0))
    c.drawOval(skia.Rect(mx - 120, 1430, mx + 120, 1460), paint('#000000', 0.4 * u, blur=8))
    glow(c, mx, my, 220, '#ffbf70', 0.2)
    c.save(); c.translate(mx, my); c.rotate(rot); c.scale(1.5, 1.5)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-26, -170, 26, 120), 18, 18), paint('#101012'))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-26, -170, 26, 120), 18, 18), paint('#ffbf70', 0.7, stroke=4))
    c.drawRect(skia.Rect(-26, -110, 26, -70), paint('#f2f2f2', 0.9))
    c.drawRect(skia.Rect(-9, 120, 9, 150), paint('#101012'))
    c.restore()
    return 0.0


def s7b(c, t, lt):
    """The boy's wrist. The glove slides off: a crooked '1' on his tape (his dad's number)."""
    T_R = 1.1  # reveal (global 27.0)
    c.drawRect(skia.Rect(0, 0, W, H), paint('#0a0807'))
    bokeh(c, t, 371, y0=100, y1=1500, a=0.28, drift=-lt * 25)
    glow(c, 300, 500, 600, '#ffbf70', 0.2)
    c.save()
    zoom(c, 1.0 + 0.08 * ease(seg(lt, T_R, 2.5)), 520, 1000)
    wrist(c, 420, 1000, -24, '#7cab19', '1', scale=0.8, font_size=230)
    # glove covering the hand + tape, sliding away
    off = ease_in(seg(lt, T_R - 0.35, T_R))
    c.save(); c.translate(420, 1000); c.rotate(-24); c.scale(0.8, 0.8)
    c.translate(-700 * off, -120 * off)
    g = skia.RRect.MakeRectXY(skia.Rect(-420, -190, 330, 190), 140, 140)
    c.drawRRect(g, paint('#0c0c0e'))
    c.drawRRect(g, paint('#ffbf70', 0.35, stroke=8))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(200, -190, 330, 190), 40, 40), paint('#7cab19'))
    c.restore()
    c.restore()
    return 0.35 * math.exp(-(lt - T_R) * 7) if lt > T_R else 0.0


def s7(c, t, f):
    lt = t - 23.6
    return s7a(c, t, lt) if lt < 2.3 else s7b(c, t, lt - 2.3)


# =============================================================== S8 28.4-33.0 fourteen years later / loop
def s8a(c, t, lt):
    """Split: El Viejo's 'TEO' (charcoal sleeve) | Teo's '1' (lime sleeve). Same rain, same lights."""
    sky(c, '#03050a', '#0c1522')
    for half, (sleeve, text, seed, ang) in enumerate((('#262a31', 'TEO', 381, 24), ('#7cab19', '1', 382, -24))):
        c.save()
        x0 = half * W / 2
        c.clipRect(skia.Rect(x0, 0, x0 + W / 2, H))
        bokeh(c, t, seed, y0=100, y1=1500, a=0.4, drift=(lt * 40) * (1 if half else -1))
        floodlight(c, x0 + 270, 300, t, 0.7, beams=False)
        sl = ease_out(seg(lt, 0.0, 0.5)) * (1 if half == 0 else -1)
        wrist(c, x0 + 270 + 200 * (1 - abs(sl)) * (-1 if half == 0 else 1), 1000, 90 + (ang if half == 0 else -ang),
              sleeve, text, scale=0.62, font_size=150 if text == 'TEO' else 220,
              skin='#2a1d16')
        rain(c, t, n=110, seed=seed, a=0.26)
        c.restore()
    c.drawLine(W / 2, 0, W / 2, H, paint('#000000', 1, stroke=10))
    return 0.25 * math.exp(-lt * 10)


def s8(c, t, f):
    lt = t - 28.4
    if lt < 2.2:
        return s8a(c, t, lt)
    k = lt - 2.2  # loop: back to the boy in his crouch, waiting for the kick that opens the video
    kid_save(c, t, -1.0, zm=1.0 + 0.1 * ease(k / 2.4))
    return 0.2 * math.exp(-k * 10)


SCENES = [(0.0, 2.8, s1), (2.8, 5.2, s2), (5.2, 9.4, s3), (9.4, 14.2, s4), (14.2, 17.6, s5),
          (17.6, 23.6, s6), (23.6, 28.4, s7), (28.4, 33.0, s8)]
