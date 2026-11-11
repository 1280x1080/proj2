"""VIDEO_010 - FLIGHT 417, Part 1: a night flight on the route where Flight 417 vanished.

YOU (seat 14A, window) and the OLD MAN (14B) act every line with flat.emote (+ sweat / pinpoint pupils / tears from
the emotion presets); the old man lip-syncs his lines.  The captain is only a PA speaker.  The ghost plane is seen
through the window.  After the flicker the cabin is on cold emergency lighting - the room darkens, faces stay lit.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "PIPELINE" / "twod"))
sys.path.insert(0, str(HERE))
import skia  # noqa: E402

import flat  # noqa: E402
import kit  # noqa: E402
from beats import B, TIMING, dark, end, start, word  # noqa: E402,F401
from flat import CAST, Light, Puppet, Style, blob, capsule, cel, ellipse_path, emote, glow, hexc, paint, poly_path, rrect_path  # noqa: E402
from kit import H, W, blink, lerp, span  # noqa: E402

YOU = Puppet(CAST["mascot"], "you")
MAN = Puppet(Style(skin="#dfae90", hair="#d4d4d8", hair_style="short", shirt="#6b5340", shirt_detail="#ece6d6",
                   pants="#3b3f4a", eyes="#5a6470", glasses=True, old=True, height=0.98), "man")
FEET, SC = 1880, 1.1
YOU_X, MAN_X = 330, 750
WARM, COLD, EXIT_RED = "#ffd9a0", "#8fb8ff", "#ff4a3a"


def col(a, b, k):
    return flat.lerp_col(hexc(a), hexc(b), k)


def emo_at(t):
    import edit_video010 as E
    cur = prev = ("calm", "calm")
    t_cur = 0.0
    for sid, line, man, you in E.SCENE_EMO:
        t0 = E._t0(sid, line)
        if t >= t0:
            prev, cur, t_cur = cur, (man, you), t0
    return prev, cur, span(t, t_cur, t_cur + 0.35)


def poses(t):
    (pm, py), (cm, cy), u = emo_at(t)
    man = emote(emote(dict(eye_open=blink(t, seed=31), turn=-0.2), pm, t, seed=1), cm, t, amount=u, seed=1)
    you = emote(emote(dict(eye_open=blink(t, seed=32), turn=0.15), py, t, seed=2), cy, t, amount=u, seed=2)
    L = lambda a, b: a <= t < b  # noqa: E731
    if L(start("L03") - 0.1, start("L06")):  # small talk: he looks at his watch, then at you; you listen
        man.update(pupil=(-0.3, 0.7) if t < start("L05") else (-0.7, 0.0), turn=-0.3)
        you.update(pupil=(0.8, 0.0), turn=0.35)
    if L(B["flicker"], start("L08")):  # both look up at the lights / the speaker
        man.update(pupil=(0.0, -0.9), head_tilt=0)
        you.update(pupil=(0.0, -0.9), head_tilt=0)
    if L(start("L08") - 0.1, start("L13")) or t < B["story"]:  # the window (screen-left)
        you.update(pupil=(-0.9, 0.0), turn=-0.45)
        man.update(pupil=(-0.9, -0.1), turn=-0.45)
    if L(start("L11") - 0.1, start("L13")):  # he cries when he sees her
        man["tears"] = span(t, start("L11"), start("L11") + 1.2)
    if L(start("L13") - 0.1, start("L15")):  # you look back over your shoulder, then up at the speaker
        you.update(pupil=(0.9, -0.2) if t < start("L14") else (0.0, -0.9), turn=0.4 if t < start("L14") else 0.0)
        man.update(pupil=(-0.9, -0.1), turn=-0.45, tears=1.0)
    if t >= start("L15") - 0.1:  # he turns to you, smiling through tears; you stare at him
        man.update(pupil=(-0.8, 0.0), turn=-0.35, tears=0.8, mouth="smile", lid=0.25, brow=(0.3, 0.5), head_tilt=5)
        you.update(pupil=(0.9, 0.0), turn=0.4)
    if t >= B["door"]:  # your eyes snap to the door on your left
        you.update(pupil=(-0.9, 0.0), turn=-0.4)
    if TIMING:
        man = TIMING.lip(man, t, "man")
    return man, you


def light_for(t):
    if dark(t) > 0.5:
        return Light(dir=(-0.7, -0.5), shadow_px=18, rim=COLD, rim_alpha=0.8, rim_px=6)
    return Light(dir=(0.2, -0.9), shadow_px=14, rim=WARM, rim_alpha=0.6, rim_px=5)


# ============================================================================ sky + planes

def sky(c, t, rect=None):
    l, tp, r, b = rect or (0, 0, W, H)
    flat.linear_grad(c, (l, tp, r, b), ["#060a18", "#10203f", "#1c3158"])
    rng = __import__("numpy").random.default_rng(5)
    for _ in range(60):
        x, y = l + rng.random() * (r - l), tp + rng.random() * (b - tp) * 0.7
        c.drawCircle(x, y, 1.5 + rng.random() * 1.5, paint("#ffffff", 0.3 + 0.5 * rng.random()))


def clouds(c, t, y0, speed, alpha, seed, l=0, r=W, scale=1.0):
    rng = __import__("numpy").random.default_rng(seed)
    span_w = (r - l) + 600
    for k in range(6):
        x = l - 300 + ((rng.random() * span_w - t * speed) % span_w)
        y = y0 + rng.random() * 120 * scale
        w = (220 + rng.random() * 200) * scale
        c.drawPath(ellipse_path(x, y, w, w * 0.22), paint("#31456e", alpha, blur=14))
        c.drawPath(ellipse_path(x + w * 0.3, y - w * 0.1, w * 0.6, w * 0.2), paint("#3d5484", alpha, blur=12))


def plane(c, cx, cy, s, ghost=False, t=0.0, lights=True):
    """Side view airliner flying screen-right.  ghost = old faded paint, rust streaks, no lights, '417' on the tail."""
    body, belly, stripe = ("#8d949c", "#6a7078", "#5a3a34") if ghost else ("#e9edf2", "#b9c2cc", "#2f5fa8")
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    # tail fin
    fin = poly_path([(-330, -30), (-400, -190), (-320, -190), (-230, -40)])
    c.drawPath(fin, paint(stripe if not ghost else "#767c84"))
    c.drawPath(poly_path([(-360, 0), (-440, -40), (-390, -40), (-300, 0)]), paint(belly))  # stabiliser
    # fuselage
    c.drawPath(blob([(-380, 0), (-300, -42), (250, -42), (360, -20), (400, 6), (330, 36), (-280, 36)], 0.35), paint(body))
    c.drawPath(blob([(-360, 14), (330, 14), (330, 36), (-280, 36)], 0.2), paint(belly))
    c.drawLine(-300, -6, 330, -6, paint(stripe, stroke=7))
    c.drawPath(blob([(330, -22), (372, -14), (360, -2), (322, -6)], 0.3), paint("#16202e"))  # cockpit glass
    for k in range(14):  # windows
        wx = -250 + k * 40
        lit = (not ghost) and lights
        c.drawRoundRect(skia.Rect.MakeLTRB(wx, -28, wx + 16, -12), 5, 5, paint("#ffe7a8" if lit else "#11161f"))
    # wing + engine
    c.drawPath(poly_path([(-20, 10), (-170, 96), (-110, 96), (90, 14)]), paint(belly))
    c.drawPath(rrect_path(-30, 40, 60, 74, 16), paint("#59606a" if ghost else "#8a94a0"))
    if ghost:
        for x, hgt in ((-180, 30), (-60, 22), (90, 34), (210, 18)):  # rust / grime streaks
            c.drawLine(x, -30, x - 6, -30 + hgt, paint("#5a3a2a", 0.55, stroke=5))
        kit.draw_text(c, "417", -322, -92, 56, color="#2a1a18", weight="Black", max_w=200)
    else:
        if lights and math.sin(t * 8) > 0.6:
            glow(c, -395, -188, 60, "#ff4a3a", 0.9)
            c.drawCircle(-395, -188, 6, paint("#ff6a5a"))
        if lights:
            c.drawCircle(398, 6, 5, paint("#ffffff"))
    c.restore()


def shot_plane_ext(c, t):
    sky(c, t)
    c.drawCircle(820, 360, 90, paint("#e9eefc"))
    glow(c, 820, 360, 420, "#cfdcff", 0.35)
    clouds(c, t, 1150, 40, 0.8, 3)
    u = t - B["story"]
    plane(c, 380 + u * 40, 800 - u * 14 + 8 * math.sin(t * 1.3), 1.25, t=t)
    clouds(c, t, 1420, 90, 0.95, 4, scale=1.5)
    flat.vignette(c, W, H, 0.5)


def shot_radar_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#04100c", "#020806"])
    cx, cy, R = 540, 760, 430
    c.drawCircle(cx, cy, R + 26, paint("#0c1f18"))
    c.drawCircle(cx, cy, R, paint("#031a12"))
    for k in (1, 2, 3):
        c.drawCircle(cx, cy, R * k / 3, paint("#1f8f5c", 0.5, stroke=3))
    c.drawLine(cx - R, cy, cx + R, cy, paint("#1f8f5c", 0.35, stroke=2))
    c.drawLine(cx, cy - R, cx, cy + R, paint("#1f8f5c", 0.35, stroke=2))
    ang = t * 2.2
    c.save()
    c.clipPath(ellipse_path(cx, cy, R, R), doAntiAlias=True)
    for k in range(24):  # sweep with a fading trail
        a = ang - k * 0.03
        c.drawLine(cx, cy, cx + R * math.cos(a), cy + R * math.sin(a), paint("#3dffa0", 0.5 * (1 - k / 24), stroke=7))
    # the route (dashed) and the blip
    for k in range(12):
        x = cx - 330 + k * 56
        c.drawLine(x, cy + 120 - k * 20, x + 26, cy + 120 - k * 20 - 9, paint("#3dffa0", 0.35, stroke=4))
    hook = t < B["story"]
    t_van = 1.6 if hook else B["vanish"]
    t_in = 0.0 if hook else start("L02") - 0.1
    u = span(t, t_in, t_van, "linear")
    bx, by = cx - 300 + u * 330, cy + 112 - u * 118
    gone = t >= t_van
    if not gone:
        pulse = 0.5 + 0.5 * math.sin(t * 9)
        glow(c, bx, by, 60, "#7dffc0", 0.5 + 0.4 * pulse)
        c.drawCircle(bx, by, 11, paint("#c9ffe4"))
        kit.draw_text(c, "FL417", bx + 86, by - 22, 34, color="#9dffd0", weight="Bold", max_w=200)
    else:
        v = span(t, t_van, t_van + 0.5)
        c.drawCircle(bx, by, 11 + 70 * v, paint("#ff4a3a", 0.8 * (1 - v), stroke=5))
        c.drawLine(bx - 16, by - 16, bx + 16, by + 16, paint("#ff4a3a", 0.9, stroke=6))
        c.drawLine(bx - 16, by + 16, bx + 16, by - 16, paint("#ff4a3a", 0.9, stroke=6))
    c.restore()
    if gone and math.sin(t * 7) > -0.3:
        c.drawRoundRect(skia.Rect.MakeLTRB(270, 196, 810, 286), 14, 14, paint("#3a0c0a", 0.95))
        kit.draw_text(c, "SIGNAL LOST", 540, 262, 62, color="#ff5a4a", weight="Black", max_w=500)
    flat.vignette(c, W, H, 0.55)


def ghost_alpha(t):
    if t < B["story"]:
        return span(t, B["hook_ghost"], B["hook_ghost"] + 0.4)
    return span(t, B["plane"], B["plane"] + 1.2)


def shot_window_pov(c, t):
    """Your window: cabin wall + oval window; the ghost plane slides in beside you."""
    k = dark(t) if t >= B["story"] else 1.0
    c.drawRect(skia.Rect.MakeWH(W, H), paint(col("#b9bcc4", "#3a4256", k)))
    for x in (60, 1020):
        c.drawLine(x, 0, x, H, paint("#000000", 0.12, stroke=6))
    win = rrect_path(170, 300, 910, 1240, 300)
    c.drawPath(rrect_path(120, 250, 960, 1290, 340), paint(col("#d9dce2", "#566078", k)))
    c.save()
    c.clipPath(win, doAntiAlias=True)
    sky(c, t, (170, 300, 910, 1240))
    clouds(c, t, 1020, 70, 0.9, 7, 170, 910)
    a = ghost_alpha(t)
    if a > 0:
        c.saveLayerAlpha(None, int(255 * a))
        plane(c, 560 - (1 - a) * 260, 760 + 6 * math.sin(t * 1.1), 0.92, ghost=True, t=t)
        c.restore()
    clouds(c, t, 1150, 140, 0.9, 8, 170, 910, 1.3)
    c.drawPath(win, paint("#ffffff", 0.05))
    c.restore()
    c.drawPath(win, paint(col("#8d929c", "#232a3a", k), stroke=18))
    c.drawPath(rrect_path(170, 300, 910, 430, 60), paint(col("#c9ccd4", "#4a5266", k), 0.0))  # (shade stays up)
    flat.vignette(c, W, H, 0.5)


def shot_tail_cu(c, t):
    sky(c, t)
    clouds(c, t, 1300, 160, 0.9, 11, scale=1.6)
    sh = 6 * math.sin(t * 1.2)
    fin = poly_path([(40, 1250 + sh), (300, 330 + sh), (760, 330 + sh), (1040, 1250 + sh)])
    c.drawPath(fin, paint("#767c84"))
    c.save()
    c.clipPath(fin, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(0, 980 + sh, W, 1060 + sh), paint("#5a3a34"))
    for x, y0, hgt in ((330, 420, 200), (480, 380, 300), (640, 560, 260), (800, 700, 220), (240, 800, 240)):  # rust runs
        c.drawLine(x, y0 + sh, x - 10, y0 + hgt + sh, paint("#4a2e22", 0.6, stroke=12))
    for x, y in ((420, 880), (700, 440), (880, 1100)):  # flaked paint
        c.drawPath(blob([(x - 40, y), (x, y - 26), (x + 46, y + 4), (x + 10, y + 34)], 0.4), paint("#5c626a"))
    kit.draw_text(c, "417", 545, 800 + sh, 300, color="#231512", weight="Black", max_w=640)
    kit.draw_text(c, "417", 540, 794 + sh, 300, color="#e6e2da", weight="Black", max_w=640, alpha=0.82)
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(0, 1250 + sh, W, H), paint("#6a7078"))  # fuselage top
    c.drawLine(0, 1250 + sh, W, 1250 + sh, paint("#4a4f58", stroke=8))
    flat.vignette(c, W, H, 0.6)


def pale_face(c, x, y, s, look=(0, 0), hair=None, t=0.0):
    """A passenger of Flight 417 behind the glass: grey skin, hollow eyes locked on you."""
    if hair:
        c.drawPath(ellipse_path(x, y - 20 * s, 76 * s, 84 * s), paint(hair))
    c.drawPath(ellipse_path(x, y, 66 * s, 78 * s), paint("#aab4c0"))
    c.drawPath(blob([(x - 110 * s, y + 190 * s), (x - 80 * s, y + 80 * s), (x + 80 * s, y + 80 * s), (x + 110 * s, y + 190 * s)], 0.4),
               paint("#4a5262"))
    for side in (-1, 1):
        ex = x + side * 26 * s
        c.drawPath(ellipse_path(ex, y - 8 * s, 17 * s, 21 * s), paint("#0a0d14"))
        c.drawCircle(ex + look[0] * 5 * s, y - 8 * s + look[1] * 5 * s, 4.5 * s, paint("#e8f0ff"))
    c.drawLine(x - 14 * s, y + 38 * s, x + 14 * s, y + 38 * s, paint("#3a4252", stroke=4 * s))


def shot_ghost_windows(c, t):
    """Close on the side of Flight 417: three windows, everyone staring; the woman in the middle points behind you."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#7d848c"))
    c.drawRect(skia.Rect.MakeLTRB(0, 1180, W, H), paint("#5d636b"))
    c.drawRect(skia.Rect.MakeLTRB(0, 1130, W, 1180), paint("#5a3a34"))
    for x, y0, hgt in ((120, 0, 260), (420, 60, 180), (760, 0, 300), (980, 200, 240)):
        c.drawLine(x, y0, x - 8, y0 + hgt, paint("#4a2e22", 0.5, stroke=12))
    bob = 5 * math.sin(t * 1.1)
    pointing = t >= start("L12") - 0.1 and t >= B["story"]
    raise_u = span(t, start("L12") + 0.5, B["point"] + 0.3, "out") if pointing else 0.0
    for k, cx in enumerate((150, 540, 930)):
        win = rrect_path(cx - 150, 380 + bob, cx + 150, 900 + bob, 130)
        c.drawPath(rrect_path(cx - 172, 358 + bob, cx + 172, 922 + bob, 150), paint("#555b63"))
        c.save()
        c.clipPath(win, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeLTRB(cx - 150, 380 + bob, cx + 150, 900 + bob), paint("#0b111c"))
        if k == 1:  # his wife: grey bun, cardigan - exactly as she was ten years ago
            c.drawCircle(cx, 560 + bob, 44, paint("#c9c9cf"))
            pale_face(c, cx, 690 + bob, 1.25, hair="#c9c9cf", t=t)
            if raise_u > 0:  # arm comes up and the finger points past you
                hx, hy = cx + 78, lerp(960, 760, raise_u) + bob
                c.drawPath(capsule((cx + 110, 930 + bob), (hx, hy), 46), paint("#4a5262"))
                c.drawCircle(hx, hy, 30, paint("#aab4c0"))
                c.drawPath(capsule((hx, hy), (hx + 44, hy - 48), 15), paint("#aab4c0"))  # index finger: past you
        else:
            pale_face(c, cx + (20 if k == 0 else -20), 700 + bob, 1.15, look=(1 if k == 0 else -1, 0),
                      hair="#2a2e38" if k == 0 else "#4a3a30", t=t)
        c.drawPath(win, paint("#9fc0ff", 0.07))
        c.restore()
        c.drawPath(win, paint("#3a3f47", stroke=12))
    flat.vignette(c, W, H, 0.6)


# ============================================================================ the cabin (frontal, row 14)

def cabin(c, t, people=True):
    k = dark(t)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(col("#c3c6ce", "#2c3448", k)))
    # overhead bins + light strip
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 330), paint(col("#dfe1e6", "#3a4258", k)))
    c.drawLine(0, 330, W, 330, paint("#000000", 0.2, stroke=6))
    for x in (270, 810):
        c.drawLine(x, 40, x, 330, paint("#000000", 0.1, stroke=4))
        c.drawRoundRect(skia.Rect.MakeLTRB(x - 60, 270, x + 60, 290), 8, 8, paint(col("#9a9ea8", "#1e2434", k)))
    strip_on = 1 - k
    c.drawRoundRect(skia.Rect.MakeLTRB(60, 346, W - 60, 372), 12, 12, paint(col("#55524a", "#fff3d6", strip_on)))
    if strip_on > 0:
        glow(c, 540, 372, 800, WARM, 0.22 * strip_on)
    # seat-belt sign + EXIT sign (always lit)
    c.drawRoundRect(skia.Rect.MakeLTRB(470, 400, 610, 452), 10, 10, paint("#1a1c22"))
    kit.draw_text(c, "FASTEN", 540, 437, 26, color="#ffb23f", weight="Black", max_w=120)
    c.drawRoundRect(skia.Rect.MakeLTRB(40, 400, 190, 458), 10, 10, paint("#0f2a16" if k < 0.5 else "#3a0c0a"))
    kit.draw_text(c, "EXIT", 115, 443, 34, color="#5dff8f" if k < 0.5 else EXIT_RED, weight="Black", max_w=130)
    if k > 0.5:
        glow(c, 115, 430, 420, EXIT_RED, 0.3 + 0.1 * math.sin(t * 5))
    # your window (left wall, beside 14A): night outside, the other plane once it arrives
    win = rrect_path(40, 640, 190, 880, 70)
    c.drawPath(rrect_path(22, 620, 208, 900, 86), paint(col("#e3e5ea", "#4a5268", k)))
    c.save()
    c.clipPath(win, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(40, 640, 190, 880), paint("#0a1226"))
    a = ghost_alpha(t)
    if a > 0:
        c.drawRect(skia.Rect.MakeLTRB(40, 730, 190, 800), paint("#8d949c", a))
        for j in range(3):
            c.drawRoundRect(skia.Rect.MakeLTRB(58 + j * 44, 746, 80 + j * 44, 772), 6, 6, paint("#11161f", a))
    c.restore()
    c.drawPath(win, paint(col("#8d929c", "#232a3a", k), stroke=8))
    # seats 14A / 14B
    seat, seat_d = col("#3a4f86", "#1e2a4c", k), col("#2c3d6c", "#16203c", k)
    for x in (YOU_X, MAN_X):
        c.drawPath(rrect_path(x - 190, 1000, x + 190, 1700, 60), paint(seat))
        c.drawPath(rrect_path(x - 150, 880, x + 150, 1190, 70), paint(seat_d))  # headrest
        c.drawPath(rrect_path(x - 150, 880, x + 150, 960, 40), paint("#e9e6dc" if k < 0.5 else "#8a8fa0"))  # antimacassar
    if people:
        man, you = poses(t)
        L = light_for(t)
        if people != "man":
            YOU.draw(c, YOU_X, FEET, SC, you, light=L, shadow=False)
        if people != "you":
            MAN.draw(c, MAN_X, FEET, SC, man, light=L, shadow=False)
            # his seat belt: buckled until he opens it
            if t < B["unbuckle"] + 0.4:
                c.drawLine(MAN_X - 150, 1484, MAN_X + 150, 1484, paint("#8a8f98", stroke=26))
                c.drawRoundRect(skia.Rect.MakeLTRB(MAN_X - 34, 1462, MAN_X + 34, 1506), 8, 8, paint("#c9ccd2"))
            else:
                c.drawLine(MAN_X - 150, 1484, MAN_X - 90, 1560, paint("#8a8f98", stroke=26))
                c.drawLine(MAN_X + 150, 1484, MAN_X + 100, 1570, paint("#8a8f98", stroke=26))
        if people != "man":
            c.drawLine(YOU_X - 150, 1484, YOU_X + 150, 1484, paint("#8a8f98", stroke=26))
            c.drawRoundRect(skia.Rect.MakeLTRB(YOU_X - 34, 1462, YOU_X + 34, 1506), 8, 8, paint("#c9ccd2"))
    # armrest between the seats + the seat backs of row 13 in the foreground (screens)
    c.drawRoundRect(skia.Rect.MakeLTRB(505, 1440, 575, 1640), 20, 20, paint(col("#6a7080", "#2a3044", k)))
    for x in (YOU_X - 40, MAN_X + 40):
        c.drawPath(rrect_path(x - 230, 1540, x + 230, H + 80, 50), paint(col("#33457a", "#141c36", k)))
        scr = skia.Rect.MakeLTRB(x - 130, 1610, x + 130, 1770)
        on = t < B["black"]
        c.drawRoundRect(scr, 12, 12, paint("#101a2e" if on else "#05070c"))
        if on:
            c.drawLine(x - 100, 1730, x + 100, 1650, paint("#6fb7ff", 0.8, stroke=4))  # the route map
            c.drawCircle(x + 20 + 8 * math.sin(t), 1684, 7, paint("#ffffff"))
            glow(c, x, 1690, 260, "#6fb7ff", 0.18)
    if k > 0.5:
        c.drawRect(skia.Rect.MakeWH(W, H), paint("#16306a", 0.10, blend=skia.BlendMode.kPlus))
    flat.vignette(c, W, H, 0.4 + 0.2 * k)


def shot_cabin_two(c, t):
    cabin(c, t)


def _cu(c, t, cx, cy, s, people=True):
    c.save()
    c.translate(540, 900)
    c.scale(s, s)
    c.translate(-cx, -cy)
    cabin(c, t, people=people)
    c.restore()
    flat.vignette(c, W, H, 0.35)


def shot_man_cu(c, t):
    x, y = MAN.head_pos(MAN_X, FEET, SC)
    _cu(c, t, x, y + 60, 2.3, people="man")


def shot_you_cu(c, t):
    x, y = YOU.head_pos(YOU_X, FEET, SC)
    _cu(c, t, x + 40, y + 60, 2.3, people="you")


def shot_watch_cu(c, t):
    """His wrist: an old watch.  It is stopped at 2:17 - the minute the lights will flicker."""
    flat.linear_grad(c, (0, 0, W, H), ["#33457a", "#1e2a4c"])
    L = Light(dir=(0.2, -0.9), shadow_px=16, rim=WARM, rim_alpha=0.6, rim_px=5)
    tr = 5 * math.sin(t * 23)  # his hand trembles
    cel(c, capsule((640 + tr, 985), (400 + tr, 760), 170), MAN.s.skin, L, k=4)  # wrist
    fist = blob([(300 + tr, 560), (450 + tr, 600), (480 + tr, 760), (360 + tr, 850), (210 + tr, 790), (190 + tr, 640)], 0.5)
    cel(c, fist, MAN.s.skin, L, k=4)                                            # loosely closed hand
    for j in range(3):
        c.drawLine(250 + j * 55 + tr, 600 + j * 12, 225 + j * 55 + tr, 700 + j * 14, paint(flat.shade(hexc(MAN.s.skin), 0.78), stroke=6))
    cel(c, capsule((1200, 1500), (640 + tr, 985), 300), MAN.s.shirt, L, k=4)   # cardigan sleeve
    c.drawPath(capsule((700 + tr, 925), (585 + tr, 1045), 60), paint(MAN.s.shirt_detail))  # shirt cuff
    wx, wy = 520 + tr, 872
    c.save()
    c.rotate(42, wx, wy)
    c.drawRoundRect(skia.Rect.MakeLTRB(wx - 60, wy - 190, wx + 60, wy + 190), 20, 20, paint("#4a3020"))  # strap
    c.restore()
    c.drawCircle(wx, wy, 132, paint("#b9953f"))
    c.drawCircle(wx, wy, 112, paint("#f4efe2"))
    for k in range(12):
        a = k * math.pi / 6
        c.drawLine(wx + 92 * math.sin(a), wy - 92 * math.cos(a), wx + 104 * math.sin(a), wy - 104 * math.cos(a),
                   paint("#2a2420", stroke=5))
    ha, ma = math.radians(68.5), math.radians(102)  # 2:17
    c.drawLine(wx, wy, wx + 58 * math.sin(ha), wy - 58 * math.cos(ha), paint("#1a1614", stroke=10))
    c.drawLine(wx, wy, wx + 88 * math.sin(ma), wy - 88 * math.cos(ma), paint("#1a1614", stroke=7))
    sa = math.radians(222 + (1.5 if math.sin(t * 6.283) > 0 else 0))  # the second hand twitches but never moves on
    c.drawLine(wx, wy, wx + 94 * math.sin(sa), wy - 94 * math.cos(sa), paint("#c0392b", stroke=3))
    c.drawCircle(wx, wy, 8, paint("#1a1614"))
    c.drawPath(ellipse_path(wx - 36, wy - 44, 46, 26), paint("#ffffff", 0.18))
    flat.vignette(c, W, H, 0.45)


def shot_panel_cu(c, t):
    """The overhead panel: PA speaker, reading lights, the seat-belt sign.  The grille pulses with the captain's voice."""
    k = dark(t)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(col("#dfe1e6", "#343c52", k)))
    c.drawRoundRect(skia.Rect.MakeLTRB(120, 300, 960, 1160), 50, 50, paint(col("#c3c6ce", "#232a3c", k)))
    a = max(TIMING.mouth(t, "captain") if TIMING else 0.0, 0.0)
    wrong = t >= start("L14") - 0.1
    c.drawCircle(540, 600, 190, paint("#1a1c22"))
    for j in range(7):
        y = 480 + j * 40
        hw = math.sqrt(max(0.0, 170 ** 2 - (y - 600) ** 2))
        c.drawLine(540 - hw, y, 540 + hw, y, paint("#ff6a5a" if wrong else "#6a7286", 0.6 + 0.4 * a, stroke=10 + 8 * a))
    if a > 0.05:
        glow(c, 540, 600, 420, EXIT_RED if wrong else COLD, 0.25 * a)
    for x in (230, 850):  # reading lights (dead after the flicker)
        c.drawCircle(x, 420, 46, paint("#8a8f98"))
        c.drawCircle(x, 420, 32, paint(col("#fff3d6", "#2a2e3a", k)))
    sign = skia.Rect.MakeLTRB(300, 880, 780, 1060)
    c.drawRoundRect(sign, 20, 20, paint("#101216"))
    if wrong and math.sin(t * 11) > -0.2:
        kit.draw_text(c, "417", 540, 1012, 130, color=EXIT_RED, weight="Black", max_w=420)
        glow(c, 540, 970, 420, EXIT_RED, 0.3)
    elif not wrong:
        on = 0.6 + 0.4 * math.sin(t * 6)
        kit.draw_text(c, "FASTEN SEAT BELT", 540, 990, 44, color="#ffb23f", weight="Black", max_w=430, alpha=on)
    flat.vignette(c, W, H, 0.5)


def shot_seats_pov(c, t):
    """Looking back down the cabin: empty seats, belts still buckled; the few passengers left are dark, still shapes."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#2c3448"))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 300), paint("#3a4258"))
    c.drawPath(poly_path([(440, 300), (640, 300), (760, H), (320, H)]), paint("#1c2234"))  # aisle
    glow(c, 540, 330, 600, EXIT_RED, 0.25 + 0.08 * math.sin(t * 5))
    c.drawRoundRect(skia.Rect.MakeLTRB(470, 300, 610, 352), 8, 8, paint("#3a0c0a"))
    kit.draw_text(c, "EXIT", 540, 340, 30, color=EXIT_RED, weight="Black", max_w=120)
    occupied = {(0, 1), (1, 2), (2, 0)}
    for row, (y, s) in enumerate(((560, 0.6), (820, 0.8), (1160, 1.08))):
        for j, side in enumerate((-1, -1, 1, 1)):
            off = (330 + (j % 2) * 190) * s if side < 0 else (330 + (j % 2) * 190) * s
            x = 540 + side * off
            w, hgt = 84 * s, 300 * s
            c.drawPath(rrect_path(x - w, y - hgt * 0.5, x + w, y + hgt * 0.5, 30 * s), paint("#1e2a4c"))
            c.drawPath(rrect_path(x - w * 0.8, y - hgt * 0.62, x + w * 0.8, y - hgt * 0.2, 26 * s), paint("#16203c"))
            if (row, j) in occupied:  # someone still there, head down, not moving
                c.drawPath(ellipse_path(x, y - hgt * 0.3, 48 * s, 56 * s), paint("#0a0e18"))
                c.drawPath(blob([(x - 80 * s, y + hgt * 0.5), (x - 60 * s, y - hgt * 0.1), (x + 60 * s, y - hgt * 0.1),
                                 (x + 80 * s, y + hgt * 0.5)], 0.4), paint("#0a0e18"))
            else:  # empty - but the belt is fastened across the seat
                by = y + hgt * 0.28
                c.drawLine(x - w, by, x + w, by, paint("#9aa0aa", stroke=16 * s))
                c.drawRoundRect(skia.Rect.MakeLTRB(x - 22 * s, by - 15 * s, x + 22 * s, by + 15 * s), 5, 5, paint("#dfe2e8"))
                glow(c, x, by, 60 * s, "#cfdcff", 0.25)
    flat.vignette(c, W, H, 0.6)


def shot_door_cu(c, t):
    """The emergency exit beside you.  The red handle turns on its own; the latch light goes from green to red."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#2c3448"))
    c.drawPath(rrect_path(150, 200, 930, 1900, 120), paint("#566078"))
    c.drawPath(rrect_path(190, 240, 890, 1900, 100), paint("#454e64"))
    win = rrect_path(400, 330, 680, 700, 120)
    c.save()
    c.clipPath(win, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(400, 330, 680, 700), paint("#0a1226"))
    c.drawRect(skia.Rect.MakeLTRB(400, 470, 680, 580), paint("#8d949c"))  # Flight 417, right outside
    for j in range(3):
        c.drawRoundRect(skia.Rect.MakeLTRB(430 + j * 80, 496, 472 + j * 80, 548), 10, 10, paint("#11161f"))
    c.restore()
    c.drawPath(win, paint("#232a3a", stroke=14))
    u = span(t, B["door"] + 0.5, B["freeze"], "inout")
    jit = 3 * math.sin(t * 40) * (1 if 0 < u < 1 else 0)
    c.drawCircle(540, 1010, 150, paint("#2a3040"))
    c.save()
    c.rotate(-100 * u + jit, 540, 1010)
    c.drawRoundRect(skia.Rect.MakeLTRB(500, 800, 580, 1060), 36, 36, paint("#d0312d"))
    c.drawRoundRect(skia.Rect.MakeLTRB(514, 816, 566, 900), 20, 20, paint("#f06a5a"))
    c.restore()
    c.drawCircle(540, 1010, 44, paint("#8a8f98"))
    locked = u < 0.85
    lamp = "#3dff8f" if locked else EXIT_RED
    c.drawCircle(760, 1010, 24, paint(lamp))
    glow(c, 760, 1010, 160, lamp, 0.5)
    c.drawRoundRect(skia.Rect.MakeLTRB(380, 1110, 700, 1180), 12, 12, paint("#d0312d"))
    kit.draw_text(c, "EMERGENCY EXIT", 540, 1160, 36, color="#ffffff", weight="Black", max_w=300)
    if u > 0:
        glow(c, 540, 1010, 600, EXIT_RED, 0.2 * u)
    flat.vignette(c, W, H, 0.55)


def shot_choice_bg(c, t):
    cabin(c, t)
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", 0.3))
    hx, hy = MAN.head_pos(MAN_X, FEET, SC)
    for (x, y), colr, letter in (((hx + 190, hy - 60), "#e2574c", "A"), ((540, 820), "#3f8fd6", "B")):
        p = 1 + 0.08 * math.sin(t * 6 + x)
        c.drawCircle(x, y, 40 * p, paint(colr))
        c.drawCircle(x, y, 40 * p, paint("#ffffff", stroke=5))
        kit.draw_text(c, letter, x, y + 17, 48, color="#ffffff", weight="Black")
    kit.draw_text(c, "COCKPIT", 540, 905, 30, color="#cfe0ff", weight="Black", max_w=200)
    flat.vignette(c, W, H, 0.6)


def _face_zone(p, x, s=SC):
    hx, hy = p.head_pos(x, FEET, s)
    r = p.HEAD_RX * p.s.head_scale * s
    return (hx - r * 1.15, hy - r * 1.5, hx + r * 1.15, hy + r * 1.35)


def _zones_wide(t):
    return [("your face", *_face_zone(YOU, YOU_X)), ("old man's face", *_face_zone(MAN, MAN_X))]


def _cu_zones(cx, cy, s, t):
    out = []
    for name, l, tp, r, b in _zones_wide(t):
        out.append((name, 540 + (l - cx) * s, 900 + (tp - cy) * s, 540 + (r - cx) * s, 900 + (b - cy) * s))
    return out


def _man_c():
    x, y = MAN.head_pos(MAN_X, FEET, SC)
    return x, y + 60


def _you_c():
    x, y = YOU.head_pos(YOU_X, FEET, SC)
    return x + 40, y + 60


ZONES = {
    "cabin_two": _zones_wide,
    "choice_bg": _zones_wide,
    "man_cu": lambda t: _cu_zones(*_man_c(), 2.3, t)[1:],
    "you_cu": lambda t: _cu_zones(*_you_c(), 2.3, t)[:1],
    "radar_cu": lambda t: [("radar", 110, 330, 970, 1190), ("SIGNAL LOST", 270, 196, 810, 286)],
    "window_pov": lambda t: [("window", 170, 300, 910, 1240)],
    "tail_cu": lambda t: [("417", 240, 560, 840, 820)],
    "ghost_windows": lambda t: [("windows", 0, 380, W, 900)],
    "watch_cu": lambda t: [("watch", 380, 730, 660, 1010)],
    "panel_cu": lambda t: [("speaker", 350, 410, 730, 790), ("sign", 300, 880, 780, 1060)],
    "door_cu": lambda t: [("door window", 400, 330, 680, 700), ("handle", 390, 790, 700, 1180)],
    "seats_pov": lambda t: [("seats", 100, 400, 980, 1330)],
}
SHOTS = dict(cabin_two=shot_cabin_two, man_cu=shot_man_cu, you_cu=shot_you_cu, watch_cu=shot_watch_cu, panel_cu=shot_panel_cu,
             seats_pov=shot_seats_pov, door_cu=shot_door_cu, choice_bg=shot_choice_bg, plane_ext=shot_plane_ext,
             radar_cu=shot_radar_cu, window_pov=shot_window_pov, tail_cu=shot_tail_cu, ghost_windows=shot_ghost_windows)
