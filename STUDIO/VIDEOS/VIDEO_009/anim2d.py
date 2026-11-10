"""VIDEO_009 - THE LAST BELL, Part 1: classroom 2B after school.

Every pose: flat.emote(emotion for this line) for BOTH characters + TIMING.lip for HER spoken lines.
The voice outside the door is never seen: a silhouette behind frosted glass, knocks, the handle.
Afternoon is warm; from the alarm (and in the hook's flash-forward) the room goes red but faces stay lit.
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
from beats import B, TIMING, end, red, start, word  # noqa: E402
from flat import CAST, Light, Puppet, Style, blob, capsule, cel, ellipse_path, emote, glow, hexc, paint, poly_path, rrect_path  # noqa: E402
from kit import H, W, blink, lerp, span, wiggle  # noqa: E402

YOU = Puppet(CAST["mascot"], "you")
HER = Puppet(Style(skin="#d9a07a", hair="#3a2416", hair_style="long", shirt="#2f4a7a", shirt_detail="#f2efe6",
                   pants="#3b3f4a", shoes="#2a2420", eyes="#4a2e1c", skirt=True, height=0.97), "her")
SUN, RED_C = "#ffc98a", "#ff3b2f"
FEET = 1860
YOU_X, HER_X, SC = 360, 720, 1.1


def emo_at(t):
    import edit_video009 as E
    cur = prev = ("happy", "happy")
    t_cur = 0.0
    for sid, line, her, you in E.SCENE_EMO:
        t0 = E._t0(sid, line)
        if t >= t0:
            prev, cur, t_cur = cur, (her, you), t0
    return prev, cur, span(t, t_cur, t_cur + 0.3)


def poses(t):
    (ph, py), (ch, cy), u = emo_at(t)
    her = emote(emote(dict(eye_open=blink(t, seed=91), turn=-0.3, pupil=(-0.5, 0.0)), ph, t, seed=1), ch, t, amount=u, seed=1)
    you = emote(emote(dict(eye_open=blink(t, seed=92), turn=0.3, pupil=(0.5, 0.0)), py, t, seed=2), cy, t, amount=u, seed=2)
    # looking at each other in the intro; at the door once it knocks
    if t >= start("P11") - 0.2 or B["hook_door"] <= t < B["story"]:
        her.update(pupil=(0.8, 0.0), turn=0.2)
        you.update(pupil=(0.9, 0.0), turn=0.3)
    if start("P02") - 0.1 <= t < start("P05"):  # laughing at your handwriting / you, smitten
        her.update(mouth="grin", head_tilt=6 + 3 * math.sin(t * 9), blush=0.5)
        you.update(blush=0.8, mouth="smile", pupil=(0.6, 0.2))
    if t < B["hook_red"]:  # hook 0-1 s: laughing together
        her.update(mouth="grin", head_tilt=6 + 3 * math.sin(t * 9))
        you.update(mouth="grin")
    if start("P13") <= t < start("P14"):  # she slowly shakes her head
        her.update(turn=0.15 + 0.35 * math.sin((t - start("P13")) * 2 * math.pi * 0.9), pupil=(0.7, 0.0))
    if start("P21") <= t < start("P22"):  # you turn to her; she looks confused
        you.update(turn=0.45, pupil=(0.9, 0.0))
        her.update(pupil=(-0.6, -0.2), head_tilt=-7, brow=(0.5, -0.3), mouth="neutral")
    if start("P26") <= t < B["choice"]:  # crying, looking right at you
        her.update(pupil=(-0.8, 0.1), turn=-0.35)
    if TIMING:
        her = TIMING.lip(her, t, "her")
    return her, you


def light_for(t):
    r = red(t)
    if r > 0.5:
        return Light(dir=(0.6, -0.6), shadow_px=18, rim=RED_C, rim_alpha=0.75, rim_px=6)
    return Light(dir=(-0.8, -0.4), shadow_px=16, rim=SUN, rim_alpha=0.8, rim_px=6)


def tears(c, p, x, scale, t, t0):
    """Tears running down from her eyes (drawn on top of the face)."""
    hx, hy = p.head_pos(x, FEET, scale)
    s = scale
    for side in (-1, 1):
        ex, ey = hx + (-0.35 * 38 + side * 40) * s, hy + 26 * s  # from the lower lid down
        u = ((t - t0) * 0.5 + (0.3 if side > 0 else 0)) % 1
        c.drawPath(capsule((ex, ey), (ex + side * 3, ey + 70 * s * min(1, (t - t0) * 2)), 7 * s), paint("#cfe8ff", 0.75))
        c.drawCircle(ex + side * 3, ey + 70 * s * u + 20, 6 * s, paint("#e8f6ff", 0.8))


# ============================================================================ the classroom (frontal)

def classroom(c, t, people=True, door_open=0.0, hide=False):
    r = red(t)
    flat.linear_grad(c, (0, 0, W, H), [flat.lerp_col(hexc("#d9cdb8"), hexc("#3a1a1a"), r), flat.lerp_col(hexc("#b9ab94"), hexc("#200d0d"), r)])
    # storage-room door (left)
    c.drawRect(skia.Rect.MakeLTRB(20, 520, 230, 1250), paint(flat.lerp_col(hexc("#7a5a3e"), hexc("#3a1e18"), r)))
    c.drawRoundRect(skia.Rect.MakeLTRB(55, 600, 195, 650), 6, 6, paint("#efe6d4" if r < 0.5 else "#5a3a34"))
    kit.draw_text(c, "STORAGE", 125, 636, 26, color="#3a2a1a", weight="Black", max_w=130)
    c.drawCircle(200, 900, 10, paint("#c9a14a"))
    # windows (middle): afternoon sky -> dusk red
    for k in range(2):
        wx = 280 + k * 250
        sky = skia.Rect.MakeLTRB(wx, 380, wx + 220, 900)
        flat.linear_grad(c, (sky.left(), sky.top(), sky.right(), sky.bottom()),
                         [flat.lerp_col(hexc("#f7c27a"), hexc("#2a0f12"), r), flat.lerp_col(hexc("#f39a6a"), hexc("#140608"), r)])
        c.drawRect(sky, paint("#e9e2d2" if r < 0.5 else "#4a2a2a", stroke=14))
        c.drawLine(wx + 110, 380, wx + 110, 900, paint("#e9e2d2" if r < 0.5 else "#4a2a2a", stroke=8))
    if r < 0.5:
        flat.light_cone(c, (520, 640), (300, 1500), (900, 1500), SUN, 0.18 * (1 - r))
    # hallway door (right) with a frosted panel
    dr = skia.Rect.MakeLTRB(810, 480, 1060, 1260)
    c.drawRect(dr, paint(flat.lerp_col(hexc("#7a5a3e"), hexc("#3a1e18"), r)))
    fg = skia.Rect.MakeLTRB(860, 540, 1010, 760)
    c.drawRect(fg, paint(flat.lerp_col(hexc("#cfd8dc"), hexc("#6a5a5a"), r)))
    c.drawCircle(830, 900, 11, paint("#c9a14a"))
    # intercom speaker + emergency beacon (top right)
    c.drawRoundRect(skia.Rect.MakeLTRB(860, 200, 1010, 300), 12, 12, paint("#2a2d33"))
    for k in range(5):
        c.drawLine(880, 220 + k * 16, 990, 220 + k * 16, paint("#4a4f58", stroke=5))
    if r > 0:
        on = 0.6 + 0.4 * math.sin(t * 7)
        c.drawCircle(780, 250, 30, paint(RED_C))
        glow(c, 780, 250, 500 * on, RED_C, 0.35 * r)
    # wall clock
    c.drawCircle(560, 250, 60, paint("#efe9df" if r < 0.5 else "#5a4a4a"))
    c.drawLine(560, 250, 560, 205, paint("#1a1a1a", stroke=6))
    c.drawLine(560, 250, 590, 262, paint("#1a1a1a", stroke=8))
    # you + her behind the pushed-together desks
    if people:
        her, you = poses(t)
        L = light_for(t)
        shift = 60 * span(t, start("P10"), start("P10") + 1.5)  # away from the windows
        if people != "her":
            YOU.draw(c, YOU_X + shift, FEET, SC, you, light=L, shadow=False)
        if people != "you":
            HER.draw(c, HER_X + shift * 0.6, FEET, SC, her, light=L, shadow=False)
        if t >= start("P26") and people != "you":
            tears(c, HER, HER_X + shift * 0.6, SC, t, start("P26"))
    c.drawRect(skia.Rect.MakeLTRB(80, 1350, 1000, 1400), paint(flat.lerp_col(hexc("#c49a6c"), hexc("#4a2a1e"), r)))  # desk top
    c.drawRect(skia.Rect.MakeLTRB(100, 1400, 980, H), paint(flat.lerp_col(hexc("#a87c52"), hexc("#3a1e16"), r)))
    c.drawLine(540, 1400, 540, H, paint("#000000", 0.15, stroke=6))
    # project sheets on the desk
    c.save()
    c.rotate(-4, 420, 1370)
    c.drawRect(skia.Rect.MakeLTRB(300, 1355, 560, 1395), paint("#f4efe2" if r < 0.5 else "#8a7a72"))
    c.restore()
    if r > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint("#ff3b2f", 0.08 * r * (0.6 + 0.4 * math.sin(t * 7)), blend=skia.BlendMode.kPlus))
    flat.vignette(c, W, H, 0.4 + 0.2 * r)


def shot_class_wide(c, t):
    classroom(c, t)


def _cu(c, t, cx, cy, s, people=True):
    c.save()
    c.translate(540, 900)
    c.scale(s, s)
    c.translate(-cx, -cy)
    classroom(c, t, people=people)
    c.restore()
    flat.vignette(c, W, H, 0.35)


def face_xy(p, x):
    return p.head_pos(x, FEET, SC)


def shot_two_cu(c, t):
    hy = face_xy(YOU, YOU_X)[1]
    _cu(c, t, 540, hy + 60, 1.65)


def shot_her_cu(c, t):
    shift = 60 * span(t, start("P10"), start("P10") + 1.5) * 0.6
    x, y = face_xy(HER, HER_X + shift)
    _cu(c, t, x, y + 70, 2.4, people="her")


def shot_you_cu(c, t):
    shift = 60 * span(t, start("P10"), start("P10") + 1.5)
    x, y = face_xy(YOU, YOU_X + shift)
    _cu(c, t, x, y + 70, 2.4, people="you")


def knock_jolt(t):
    j = 0.0
    for kt in list(B["knocks"]) + [B["hook_door"] + 0.1, B["hook_door"] + 0.45, B["knock2"] - 0.25, B["knock2"] + 0.2]:
        u = t - kt
        if 0 <= u < 0.22:
            j = max(j, (1 - u / 0.22) * 10)
    return j


def shot_door_cu(c, t):
    r = red(t)
    flat.linear_grad(c, (0, 0, W, H), [flat.lerp_col(hexc("#d9cdb8"), hexc("#3a1a1a"), r), flat.lerp_col(hexc("#b9ab94"), hexc("#200d0d"), r)])
    j = knock_jolt(t)
    c.save()
    c.translate(0, -j * 0.5)
    dr = skia.Rect.MakeLTRB(200, 200, 880, 1900)
    c.drawRect(skia.Rect.MakeLTRB(170, 170, 910, 1900), paint("#5a4030" if r < 0.5 else "#2a1410"))
    c.drawRect(dr, paint(flat.lerp_col(hexc("#7a5a3e"), hexc("#3a1e18"), r)))
    fg = skia.Rect.MakeLTRB(330, 330, 750, 900)
    c.drawRect(fg, paint(flat.lerp_col(hexc("#cfd8dc"), hexc("#7a6a6a"), r)))
    # the silhouette behind the frosted glass (never more than a blurry shape)
    present = (B["hook_door"] <= t < B["story"]) or t >= end("P11")
    if present:
        lean = 30 * span(t, start("P16"), start("P16") + 1.0) if t < start("P19") else 30
        tilt = 14 * span(t, start("P20"), start("P20") + 0.8) if t >= start("P20") else 0
        c.save()
        c.clipRect(fg)
        c.rotate(tilt, 540, 700)
        c.drawPath(ellipse_path(540, 560 - lean * 0.2, 95 + lean * 0.4, 120 + lean * 0.4), paint("#1a1414", 0.75, blur=26))
        c.drawPath(blob([(400, 900), (420, 720), (540, 660), (660, 720), (680, 900)], 0.4), paint("#1a1414", 0.7, blur=30))
        if start("P16") <= t < start("P19"):  # a hand pressed flat on the glass
            c.drawPath(ellipse_path(640, 620, 50, 70), paint("#2a1e1e", 0.8, blur=10))
        c.restore()
    c.drawRect(fg, paint("#3a2a1e", stroke=16))
    # handle (turns at the end)
    ang = -35 * span(t, B["handle"] + 0.1, B["handle"] + 1.6) if t >= B["handle"] else 0.0
    c.save()
    c.rotate(ang, 790, 1150)
    c.drawRoundRect(skia.Rect.MakeLTRB(640, 1130, 800, 1170), 18, 18, paint("#c9a14a"))
    c.restore()
    c.drawCircle(790, 1150, 26, paint("#a8842f"))
    c.restore()
    # light under the door: a shadow passes
    c.drawRect(skia.Rect.MakeLTRB(200, 1880, 880, 1900), paint("#ffd9a0" if r < 0.5 else "#ff6a5a", 0.8))
    if present:
        c.drawRect(skia.Rect.MakeLTRB(420, 1880, 640, 1900), paint("#000000", 0.95))
    flat.vignette(c, W, H, 0.45)


def shot_alarm_cu(c, t):
    r = max(red(t), 0.6)
    flat.linear_grad(c, (0, 0, W, H), ["#3a1a1a", "#1a0a0a"])
    c.drawRoundRect(skia.Rect.MakeLTRB(240, 660, 840, 1060), 30, 30, paint("#2a2d33"))  # intercom
    a = max(TIMING.mouth(t, "intercom") if TIMING else 0.0, 0.0)
    for k in range(9):
        c.drawLine(290, 700 + k * 40, 790, 700 + k * 40, paint("#4a4f58", stroke=12 + 4 * a))
    on = 0.5 + 0.5 * math.sin(t * 7)
    c.drawCircle(540, 300, 110, paint("#5a0f0a"))
    c.drawCircle(540, 300, 92, paint(RED_C, 0.6 + 0.4 * on))
    glow(c, 540, 300, 900 * (0.6 + 0.4 * on), RED_C, 0.4 * r)
    kit.draw_text(c, "LOCKDOWN", 540, 1180, 84, color="#ffffff", weight="Black", alpha=0.5 + 0.5 * on)
    flat.vignette(c, W, H, 0.5)


def shot_paper_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#c49a6c", "#a87c52"])
    c.save()
    c.rotate(-5, 540, 960)
    c.drawRect(skia.Rect.MakeLTRB(160, 380, 920, 1500), paint("#f4efe2"))
    for k in range(14):
        c.drawLine(200, 480 + k * 70, 880, 480 + k * 70, paint("#9fc4e8", 0.6, stroke=3))
    kit.draw_text(c, "SCIENCE FAIR PROJECT", 540, 450, 50, color="#2a3a6a", weight="Black", max_w=700)
    f = kit.font(60, "Bold")
    f.setSkewX(-0.35)
    for i, ln in enumerate(["the water cycel", "evapration -> clouds", "rain (???)"]):  # your terrible handwriting
        c.save()
        c.rotate(wiggle(i, 1, 3, i), 220, 640 + i * 140)
        c.drawString(ln, 220 + i * 12, 640 + i * 140, f, paint("#2a2a35"))
        c.restore()
    f2 = kit.font(56, "Bold")
    c.drawString("ha! :)", 600, 1180, f2, paint("#d0457a"))  # her note in the margin
    c.restore()
    L = Light(dir=(-0.8, -0.4), shadow_px=14)
    tap = abs(math.sin(t * 6)) * 20
    cel(c, capsule((1150, 1500), (720, 1000 - tap), 90), HER.s.shirt, L, k=3)
    cel(c, capsule((730, 1010 - tap), (640, 860 - tap), 46), HER.s.skin, L, k=2)  # her finger pointing at your writing
    flat.vignette(c, W, H, 0.35)


def shot_arm_cu(c, t):
    r = red(t)
    flat.linear_grad(c, (0, 0, W, H), ["#3a1a1a", "#200d0d"])
    L = light_for(t)
    cel(c, capsule((-100, 1300), (1200, 1000), 260), YOU.s.shirt, L, k=4)  # your forearm across the frame
    shake = wiggle(t, 30, 7, 3)
    hx, hy = 560 + shake, 1060
    cel(c, capsule((540 + shake, 1900), (hx, 1250), 200), HER.s.shirt, L, k=4)  # her sleeve
    hand = blob([(hx - 170, hy + 160), (hx - 190, hy - 60), (hx - 40, hy - 150), (hx + 150, hy - 120), (hx + 190, hy + 120)], 0.45)
    cel(c, hand, HER.s.skin, L, k=3)
    for k in range(4):  # fingers wrapped over your arm
        fx = hx - 120 + k * 75
        a, b = (fx, hy + 20), (fx - 15, hy + 190 + (k % 2) * 20)  # curled down over your forearm
        c.drawPath(capsule(a, b, 52), paint(HER.s.skin))
        c.drawPath(capsule(a, b, 52), paint(flat.shade(hexc(HER.s.skin), 0.8), stroke=3))
    flat.vignette(c, W, H, 0.5)


def shot_hands_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#3a1a1a", "#200d0d"])
    L = light_for(t)
    u = span(t, start("P29"), start("P29") + 0.5, "out")
    cel(c, capsule((-80, 1500), (430, 1060), 190), YOU.s.shirt, L, k=4)
    cel(c, blob([(380, 960), (560, 930), (600, 1110), (420, 1160)], 0.4), YOU.s.skin, L, k=3)  # your hand
    hx = lerp(1250, 600, u)
    cel(c, capsule((1300, 1500), (hx + 80, 1060), 180), HER.s.shirt, L, k=4)
    cel(c, blob([(hx - 120, 900), (hx + 80, 880), (hx + 120, 1100), (hx - 80, 1140)], 0.4), HER.s.skin, L, k=3)  # her hand over yours
    flat.vignette(c, W, H, 0.5)


def shot_phone_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#3a1a1a", "#1a0a0a"])
    c.drawRoundRect(skia.Rect.MakeLTRB(200, 260, 880, 1680), 60, 60, paint("#101216"))
    c.drawRoundRect(skia.Rect.MakeLTRB(230, 290, 850, 1650), 46, 46, paint("#0d1018"))
    kit.draw_text(c, "Unknown number", 540, 380, 40, color="#ffffff", weight="Bold")
    # the photo: the two of you at the desks, seen from BEHIND
    ph = skia.Rect.MakeLTRB(270, 450, 810, 1010)
    u = span(t, start("P22") + 0.2, start("P22") + 0.6, "back")
    if u > 0:
        c.save()
        c.clipRect(ph)
        flat.linear_grad(c, (ph.left(), ph.top(), ph.right(), ph.bottom()), ["#f7c27a", "#d9cdb8"])
        c.drawRect(skia.Rect.MakeLTRB(270, 450, 810, 600), paint("#e9e2d2"))
        for cx, col in ((430, YOU.s.cap), (650, HER.s.hair)):
            c.drawCircle(cx, 800, 95, paint(col))  # backs of two heads
            c.drawRect(skia.Rect.MakeLTRB(cx - 120, 880, cx + 120, 1010), paint("#9aa3ad" if cx < 540 else HER.s.shirt))
        c.drawRect(skia.Rect.MakeLTRB(270, 960, 810, 1010), paint("#a87c52"))
        c.restore()
        c.drawRect(ph, paint("#ffffff", stroke=6))
        kit.draw_text(c, "Room 2B · 3:41 PM", 540, 1060, 30, color="#9fa8b8", weight="SemiBold")
    if t >= start("P25") - 0.1:
        v = span(t, start("P25"), start("P25") + 0.3, "back")
        c.drawRoundRect(skia.Rect.MakeLTRB(270, 1120, 810, 1330), 30, 30, paint("#2b3242", 0.96 * min(1, v)))
        kit.draw_text(c, "She hasn't told you", 300, 1200, 40, color="#ffffff", weight="SemiBold", align="left", max_w=500)
        kit.draw_text(c, "what happened last time.", 300, 1260, 40, color="#ffffff", weight="SemiBold", align="left", max_w=500)
    glow(c, 540, 900, 700, "#cfe6ff", 0.12)
    flat.vignette(c, W, H, 0.45)


def shot_behind_pov(c, t):
    r = red(t)
    flat.linear_grad(c, (0, 0, W, H), ["#3a1a1a", "#200d0d"])
    for row in range(3):  # empty desks at the back of the room
        for k in range(3):
            x, y, s = 200 + k * 340, 1100 + row * 260, 1 + row * 0.25
            c.drawRect(skia.Rect.MakeLTRB(x - 110 * s, y, x + 110 * s, y + 30 * s), paint("#4a2a1e"))
            c.drawLine(x - 90 * s, y + 30 * s, x - 90 * s, y + 160 * s, paint("#2a1410", stroke=8))
            c.drawLine(x + 90 * s, y + 30 * s, x + 90 * s, y + 160 * s, paint("#2a1410", stroke=8))
    c.drawRect(skia.Rect.MakeLTRB(80, 300, 520, 700), paint("#1a0a0a"))  # back board
    c.drawRect(skia.Rect.MakeLTRB(760, 420, 960, 1000), paint("#3a1e18"))  # storage door
    kit.draw_text(c, "STORAGE", 860, 520, 28, color="#8a6a5a", weight="Black", max_w=180)
    on = 0.5 + 0.5 * math.sin(t * 7)
    glow(c, 540, 200, 900, RED_C, 0.25 * on)
    flat.vignette(c, W, H, 0.6)


def shot_choice_bg(c, t):
    classroom(c, t)
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", 0.35))
    # the door is opening: a dark shadow reaches across the floor toward your shadows
    u = span(t, B["choice"], B["choice"] + 6.0, "linear")
    c.drawPath(poly_path([(1060, 1260), (1060 - 480 * u, 1330), (1060 - 520 * u, 1400), (1060, 1400)]), paint("#000000", 0.6, blur=8))
    # the courtyard below the window: something waiting
    c.drawPath(ellipse_path(480, 870, 14, 30), paint("#000000", 0.85))
    c.drawCircle(480, 832, 12, paint("#000000", 0.85))
    for (x, y), col, letter in (((125, 980), "#e2574c", "A"), ((400, 830), "#3f8fd6", "B")):  # storage door + window
        p = 1 + 0.08 * math.sin(t * 6 + x)
        c.drawCircle(x, y, 40 * p, paint(col))
        c.drawCircle(x, y, 40 * p, paint("#ffffff", stroke=5))
        kit.draw_text(c, letter, x, y + 17, 48, color="#ffffff", weight="Black")
    flat.vignette(c, W, H, 0.6)


def _face_zone(p, x, s=SC):
    hx, hy = p.head_pos(x, FEET, s)
    r = p.HEAD_RX * p.s.head_scale * s
    return (hx - r * 1.15, hy - r * 1.5, hx + r * 1.15, hy + r * 1.35)


def _zones_wide(t):
    shift = 60 * span(t, start("P10"), start("P10") + 1.5)
    return [("your face", *_face_zone(YOU, YOU_X + shift)), ("her face", *_face_zone(HER, HER_X + shift * 0.6))]


def _cu_zones(cx, cy, s, t):
    out = []
    for name, l, tp, r, b in _zones_wide(t):
        f = lambda x, y: (540 + (x - cx) * s, 900 + (y - cy) * s)  # noqa: E731
        (l2, t2), (r2, b2) = f(l, tp), f(r, b)
        out.append((name, l2, t2, r2, b2))
    return out


ZONES = {
    "class_wide": _zones_wide,
    "two_cu": lambda t: _cu_zones(540, face_xy(YOU, YOU_X)[1] + 60, 1.65, t),
    "her_cu": lambda t: _cu_zones(face_xy(HER, HER_X + 36 * span(t, start("P10"), start("P10") + 1.5))[0],
                                  face_xy(HER, HER_X)[1] + 70, 2.4, t)[1:],
    "you_cu": lambda t: _cu_zones(face_xy(YOU, YOU_X + 60 * span(t, start("P10"), start("P10") + 1.5))[0],
                                  face_xy(YOU, YOU_X)[1] + 70, 2.4, t)[:1],
}
ZONES.update({
    "alarm_cu": lambda t: [("beacon", 430, 190, 650, 410), ("intercom", 240, 660, 840, 1060), ("LOCKDOWN", 300, 1110, 780, 1200)],
    "door_cu": lambda t: [("glass", 330, 330, 750, 900), ("handle", 600, 1100, 830, 1200)],
    "phone_cu": lambda t: [("photo", 270, 450, 810, 1010)] + ([("message", 270, 1120, 810, 1330)] if t >= start("P25") - 0.1 else []),
})
SHOTS = dict(class_wide=shot_class_wide, two_cu=shot_two_cu, her_cu=shot_her_cu, you_cu=shot_you_cu, door_cu=shot_door_cu,
             alarm_cu=shot_alarm_cu, paper_cu=shot_paper_cu, arm_cu=shot_arm_cu, hands_cu=shot_hands_cu,
             phone_cu=shot_phone_cu, behind_pov=shot_behind_pov, choice_bg=shot_choice_bg)
