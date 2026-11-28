"""ns01 — Night Shift Rules, Episode 1: The Knock.
You work the night shift at the Wren Motel. Rule 1: never open the office door after 3 a.m.
At 3:00 something knocks with the manager's voice. The peephole shows him at the far end of the hall, back turned...
then its face is at the lens. Ends on the viewer vote: A open it / B don't.
Plant: the rules note's P.S. "I ALWAYS HAVE MY KEY." (so the knocker who 'forgot his key' is not Hale).
Scene functions take GLOBAL time t. Return value = white flash amount (0..1)."""
import math
import skia
from lib import *
from shots import zoom
from horror import (darkness, dust, flicker, corridor, visitor, scare_face, office_door, cctv, glitch,
                    peephole_mask, neon_text, note, RED, FULL)

RULES = [("NIGHT SHIFT RULES", 70, '#141414'),
         ("1. NEVER OPEN THE OFFICE", 46, '#1b1b1b'), ("    DOOR AFTER 3 A.M.", 46, '#1b1b1b'),
         ("2. ROOM 9 IS EMPTY. IF ITS", 46, '#1b1b1b'), ("    LIGHT IS ON, DON'T LOOK.", 46, '#1b1b1b'),
         ("3. IF SOMEONE SAYS YOUR", 46, '#1b1b1b'), ("    NAME, DON'T ANSWER.", 46, '#1b1b1b'),
         ("", 20, '#000000'),
         ("- HALE", 52, '#1b1b1b'),
         ("", 30, '#000000'),
         ("P.S. I ALWAYS HAVE MY KEY.", 44, '#9a1a1a')]


def cctv_hall(c, t, lt, knock_t=0.35):
    """CCTV, high corner: the Visitor at the office door (right wall, near), arm swinging into a knock."""
    cam = Cam(horizon=640, F=820, h=2.45, xoff=0.45)
    f = flicker(t, 3, dead=0.2)
    corridor(c, t, cam, lamps=[(2.5, 0.8 * f), (7, 0.9), (11.5, 0.6), (16, 0.7 * flicker(t, 4, dead=0.5)), (20, 0.4)],
             length=24, end_glow=0.7)
    x, y = cam.p(1.0, 3.4)
    s = cam.s(3.4, 1.9) / 190
    swing = math.exp(-max(0, lt - knock_t) * 6) * math.cos(max(0, lt - knock_t) * 12)
    lift = ease_out(seg(lt, 0.0, knock_t))
    pz = dict(torso=180, head=6, uaL=-3, faL=-1, uaR=lerp(10, 105, lift) - 20 * swing, faR=lerp(6, 150, lift),
              thL=-2, shL=-1, thR=2, shR=1)
    visitor(c, x, y, s, t, back=True, pose=pz, rim_a=0.35, shade=0.55)
    sx, sy = shake(lt, 10 * math.exp(-(lt - knock_t) * 7) if lt > knock_t else 0)
    return sx, sy


# =============================================================== S1 0-1.5 CCTV: the knock   |  S1b 1.5-2.8 inside
def s1(c, t, f):
    lt = t
    c.save()
    sx, sy = shake(lt, 9 * math.exp(-(lt - 0.35) * 7) if lt > 0.35 else 0)
    c.translate(sx, sy)
    zoom(c, 1.0 + 0.05 * lt, 540, 900)
    cctv_hall(c, t, lt)
    c.restore()
    cctv(c, t, 'CAM 04  HALLWAY', '03:01:%02d' % (12 + int(lt)))
    glitch(c, t, 0.9 * math.exp(-(lt - 0.35) * 5) if lt > 0.35 else 0.25 * (lt < 0.1), seed=1)
    return 0.25 * math.exp(-(lt - 0.35) * 10) if lt > 0.35 else 0.0


def s1b(c, t, f):
    lt = t - 1.5
    hits = [0.0, 0.33, 0.66]
    sh = sum(math.exp(-(lt - h) * 9) for h in hits if lt > h)
    rattle = 0.5 + 0.5 * math.sin(lt * 38) if lt < 1.0 else 0.2
    office_door(c, t, shake_amt=sh, handle=rattle, gap_light=0.8, feet=1.0, light=0.32)
    lx, ly = 600 + 60 * math.sin(t * 1.7), 1000 + 40 * math.sin(t * 2.3)
    darkness(c, lx, ly, 560, dark=0.9)
    glitch(c, t, 0.35 * min(1, sh), seed=2)
    return 0.2 * math.exp(-lt * 12)


# =============================================================== S2 2.8-5.1 the Wren Motel
def s2(c, t, f):
    lt = t - 2.8
    c.save()
    zoom(c, 1.0 + 0.35 * (1 - ease_out(lt / 0.4)) + 0.06 * lt / 2.3, 540, 900)
    sky(c, '#020308', '#0b1020', 0, 1150)
    # motel block
    c.drawRect(skia.Rect(-100, 860, W + 100, 1240), paint('#16130f'))
    c.drawRect(skia.Rect(-100, 830, W + 100, 870), paint('#0c0a08'))
    for k in range(7):
        x = 40 + k * 150
        lit = (k == 4)
        c.drawRect(skia.Rect(x, 960, x + 70, 1180), paint('#2a1d14' if not lit else '#ffd27a', 1 if not lit else 0.9))
        c.drawString(str(k + 1), x + 26, 945, skia.Font(FONT, 34), paint('#8a7a5a', 0.7))
        if lit:
            glow(c, x + 35, 1080, 220, '#ffd27a', 0.3)
    # office window with a silhouette (you)
    c.drawRect(skia.Rect(780, 980, 1010, 1130), paint('#ffe6a8', 0.85))
    figure(c, POSES['stand'], 900, 1120, 1.4, kit='guard', front=True, rim_a=0.0)
    glow(c, 895, 1060, 300, '#ffe6a8', 0.25)
    # parking lot
    g = skia.Paint()
    g.setShader(lin_shader(0, 1240, 0, H, ['#0a0b0f', '#121418']))
    c.drawRect(skia.Rect(-100, 1240, W + 100, H + 100), g)
    for k in range(6):
        c.drawLine(80 + k * 180, 1300, 20 + k * 200, 1520, paint('#d8d2b0', 0.18, stroke=8))
    # neon sign on a pole
    c.drawLine(300, 820, 300, 1240, paint('#0c0c0e', 1, stroke=18))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(70, 330, 530, 720), 24, 24), paint('#0d0b0b'))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(70, 330, 530, 720), 24, 24), paint('#2a2222', 1, stroke=6))
    on = flicker(t, 11, rate=0.7, dead=0.25)
    neon_text(c, 'WREN', 300, 470, 140, RED, on)
    neon_text(c, 'MOTEL', 300, 600, 120, RED, 1.0)
    vac = flicker(t, 12, rate=1.3, dead=0.55)
    neon_text(c, 'VACANCY', 300, 690, 64, '#45ff8a', vac)
    glow(c, 300, 520, 420, RED, 0.18 + 0.12 * on)
    # reflection in the wet lot
    c.save()
    c.translate(0, 2 * 1250); c.scale(1, -1)
    c.saveLayerAlpha(skia.Rect(-100, 0, W + 100, H * 2), 60)
    neon_text(c, 'MOTEL', 300, 600, 120, RED, 1.0)
    c.restore()
    c.restore()
    rain(c, t, n=260, seed=201, a=0.28)
    c.restore()
    rain(c, t, n=40, seed=202, a=0.35, width=6, length=150, blur=6, speed=3600)
    return 0.3 * math.exp(-lt * 10)


# =============================================================== S3 5.1-7.5 the rules (flashlight sweep -> P.S.)
def s3(c, t, f):
    lt = t - 5.1
    c.save()
    zoom(c, 1.12 + 0.04 * lt, 540, 860)
    c.drawRect(FULL, paint('#17110d'))
    r = rng_for(301)
    for i in range(40):
        y = i * 52 + r.random() * 20
        c.drawLine(-100, y, W + 100, y + r.random() * 30 - 15, paint('#22180f', 0.9, stroke=4))
    note(c, 540, 900, -2.5, 1.12, RULES)
    # a key-shaped hook on the desk edge, empty (it's the manager's hook)
    c.restore()
    u = ease(seg(lt, 0.1, 2.0))
    lx = lerp(430, 520, u) + 30 * math.sin(t * 2)
    ly = lerp(560, 1260, u)
    darkness(c, lx, ly, 470, dark=0.92)
    dust(c, t, lx, ly, 400, seed=303, a=0.45)
    return 0.2 * math.exp(-lt * 12)


# =============================================================== S4 7.5-10.3 the hallway lights die
def s4(c, t, f):
    lt = t - 7.5
    cam = Cam(horizon=880, F=950, h=1.65)
    lamps = []
    for i, z in enumerate((2, 6, 10, 14, 18, 22)):
        die = 2.3 - i * 0.38         # far lamps die first, then toward you
        b = 1.0 if lt < die - 0.5 else (flicker(t, 20 + i, rate=1.4, dead=0.6) if lt < die else 0.0)
        lamps.append((z, b))
    c.save()
    zoom(c, 1.0, 540, 900)
    corridor(c, t, cam, dolly=0.25 * lt, lamps=lamps, length=26, end_glow=1.0)
    c.restore()
    total = sum(b for _, b in lamps)
    darkness(c, 540, 1000, 700, dark=0.55 * (1 - total / 6))
    return 0.0


# =============================================================== S5 10.3-12.4 3:00 / the three knocks
def led_clock(c, t, txt):
    c.drawRect(FULL, paint('#050404'))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(120, 620, 960, 1100), 40, 40), paint('#0e0b0a'))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(120, 620, 960, 1100), 40, 40), paint('#2a2220', 1, stroke=6))
    f = skia.Font(FONT, 380)
    w = f.measureText(txt)
    glow(c, 540, 860, 420, RED, 0.35)
    c.drawString(txt, 540 - w / 2, 1000, f, paint(RED, 0.25, blur=24))
    c.drawString(txt, 540 - w / 2, 1000, f, paint('#ff4a3a'))


def s5(c, t, f):
    lt = t - 10.3
    if lt < 0.7:
        led_clock(c, t, '2:59' if lt < 0.2 else '3:00')
        glitch(c, t, 0.5 * math.exp(-(lt - 0.2) * 9) if lt > 0.2 else 0, seed=5)
        return 0.15 * math.exp(-(lt - 0.2) * 10) if lt > 0.2 else 0.0
    k = lt - 0.7
    hits = [0.0, 0.42, 0.84]
    sh = sum(math.exp(-(k - h) * 9) for h in hits if k > h)
    c.save()
    zoom(c, 1.15 + 0.06 * k, 540, 700)
    office_door(c, t, shake_amt=sh, handle=0.0, gap_light=0.8, feet=1.0, light=0.3)
    c.restore()
    darkness(c, 540, 760, 520, dark=0.9)
    return 0.12 * sum(math.exp(-(k - h) * 14) for h in hits if k > h)


# =============================================================== S6 12.4-16.9 the voice: the gap, then the handle
def s6(c, t, f):
    lt = t - 12.4
    if lt < 2.8:
        # floor level: light strip under the door, two feet blocking it, shifting
        c.save()
        c.translate(0, -620)
        zoom(c, 2.6, 540, 1700)
        shift = 12 * math.sin(lt * 1.3)
        office_door(c, t, gap_light=1.0, feet=0.0, light=0.25)
        for k_ in range(5):  # light spilling across the floor toward you
            glow(c, 540, 1716 + k_ * 30, 380 - k_ * 40, '#ffd9a0', 0.10)
        for fx in (430 + shift, 640 + shift):
            c.drawRect(skia.Rect(fx - 70, 1694, fx + 70, 1714), paint('#000000', 0.97))
            sh_ = skia.Path()
            sh_.moveTo(fx - 70, 1714); sh_.lineTo(fx + 70, 1714); sh_.lineTo(fx + 120, 1900); sh_.lineTo(fx - 120, 1900)
            sh_.close()
            c.drawPath(sh_, paint('#000000', 0.6, blur=6))
        c.restore()
        darkness(c, 540, 1080, 640, dark=0.8, tint=0.0)
        glitch(c, t, 0.15 * (math.sin(lt * 7) > 0.92), seed=6)
        return 0.0
    k = lt - 2.8
    c.save()
    zoom(c, 2.0 + 0.1 * k, 820, 1000)
    office_door(c, t, handle=ease_in(seg(k, 0.2, 1.6)) * 0.75, gap_light=0.8, light=0.3)
    c.restore()
    darkness(c, 760, 960, 520, dark=0.88)
    return 0.15 * math.exp(-k * 12)


# =============================================================== S7 16.9-22.2 through the peephole
def peep_hall(c, t, lt, fig=True):
    cam = Cam(horizon=820, F=1900, h=1.6)
    lamps = [(2, 0.0), (6, 0.0), (10, flicker(t, 41, rate=0.9, dead=0.3)), (14, 0.0), (18, 0.0), (22, 0.0)]
    c.save()
    zoom(c, 1.0 + 0.10 * ease(seg(lt, 0, 5.3)), 540, 820)
    corridor(c, t, cam, lamps=lamps, length=26, end_glow=1.0)
    if fig:
        Z = 10.2
        x, y = cam.p(0.0, Z)
        s = cam.s(Z, 1.9) / 190
        visitor(c, x, y, s, t, back=True, rim_a=0.7 * lamps[2][1] + 0.15)
    c.restore()


def s7(c, t, f):
    lt = t - 16.9
    peep_hall(c, t, lt)
    peephole_mask(c)
    glitch(c, t, 0.12 + 0.3 * (lt > 3.4) * math.exp(-(lt - 3.4) * 5), seed=7)
    return 0.15 * math.exp(-lt * 12)


# =============================================================== S8 22.2-24.3 JUMP SCARE
def s8(c, t, f):
    lt = t - 22.2
    c.drawRect(FULL, paint('#000000'))
    pop = ease_out(seg(lt, 0.05, 0.15))
    if lt < 0.05:
        peep_hall(c, t, 5.3, fig=False)
    else:
        peep_hall(c, t, 5.3, fig=False)
        scare_face(c, 540, 770, lerp(0.7, 0.98, pop) + 0.03 * lt, t, open_=ease(seg(lt, 0.3, 1.4)))
    peephole_mask(c)
    glitch(c, t, 1.0 * math.exp(-(lt - 0.05) * 2.2) if lt > 0.05 else 0, seed=8)
    return 0.7 * math.exp(-(lt - 0.05) * 9) if lt > 0.05 else 0.0


# =============================================================== S9 24.3-33.2 the vote
def option(c, y, letter, label, fill, a, pulse=1.0):
    c.save()
    c.translate(540, y + 70); c.scale(pulse, pulse); c.translate(-540, -(y + 70))
    rr = skia.RRect.MakeRectXY(skia.Rect(110, y, 970, y + 140), 26, 26)
    c.drawRRect(rr, paint('#000000', 0.55 * a, blur=16))
    c.drawRRect(rr, paint(fill, 0.92 * a))
    c.drawRRect(rr, paint('#ffffff', 0.9 * a, stroke=5))
    f1 = skia.Font(FONT, 120)
    c.drawString(letter, 150, y + 117, f1, paint('#ffffff', a))
    c.drawLine(250, y + 22, 250, y + 118, paint('#ffffff', 0.7 * a, stroke=4))
    f2 = skia.Font(FONT, 96)
    c.drawString(label, 285, y + 106, f2, paint('#ffffff', a))
    c.restore()


def s9(c, t, f):
    lt = t - 24.3
    k2 = [3.3, 7.6]
    sh = sum(math.exp(-(lt - h) * 9) for h in k2 if lt > h)
    office_door(c, t, shake_amt=sh, handle=0.15 + 0.15 * math.sin(t * 9) * (lt > 6.1), gap_light=0.8, feet=1.0,
                light=0.3)
    darkness(c, 540, 900, 560, dark=0.93)
    c.drawRect(FULL, paint('#000000', 0.35))
    a1 = ease_out(seg(lt, 0.15, 0.45))
    a2 = ease_out(seg(lt, 0.45, 0.75))
    f = skia.Font(FONT, 92)
    q = 'DO YOU OPEN THE DOOR?'
    al = ease(seg(lt, 0.0, 0.3))
    c.drawString(q, 540 - f.measureText(q) / 2 + 4, 470 + 6, f, paint('#000000', 0.6 * al, blur=6))
    c.drawString(q, 540 - f.measureText(q) / 2, 470, f, paint('#ffffff', al))
    pa = 1 + 0.04 * math.sin(t * 6) * (lt > 1.8)
    option(c, 560, 'A', 'OPEN IT', '#7a1010', a1, pa)
    option(c, 760, 'B', "DON'T OPEN", '#1c1c22', a2, 2 - pa)
    f3 = skia.Font(FONT, 64)
    s_ = 'COMMENT  A  OR  B  ·  YOU DECIDE EP 2'
    a3 = ease(seg(lt, 1.7, 2.1))
    c.drawString(s_, 540 - f3.measureText(s_) / 2, 1020, f3, paint(RED, a3))
    glitch(c, t, 0.25 * sh, seed=9)
    return 0.12 * math.exp(-lt * 10)


# =============================================================== S10 33.2-33.8 loop back to the CCTV
def s10(c, t, f):
    lt = t - 33.2
    c.save()
    zoom(c, 1.0, 540, 900)
    cctv_hall(c, t, -1.0)
    c.restore()
    cctv(c, t, 'CAM 04  HALLWAY', '03:01:11')
    glitch(c, t, 0.5 * math.exp(-lt * 8), seed=10)
    return 0.0


SCENES = [(0.0, 1.5, s1), (1.5, 2.8, s1b), (2.8, 5.1, s2), (5.1, 7.5, s3), (7.5, 10.3, s4), (10.3, 12.4, s5),
          (12.4, 16.9, s6), (16.9, 22.2, s7), (22.2, 24.3, s8), (24.3, 33.2, s9), (33.2, 33.8, s10)]
