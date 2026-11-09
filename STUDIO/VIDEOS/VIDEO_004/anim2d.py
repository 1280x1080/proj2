"""VIDEO_004 - THE ROOM THAT WASN'T THERE, Part 1: 2D shots (Skia), native 1080x1920.

shot_NAME(canvas, t) with t = absolute video time (EDL offset = cut time), keyed to beats.py.
Night palette: moonlight blue, phone glow on your face, warm hallway light under the door until
"Silence", red creeping in from the third text.  The monster is never shown.
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
from beats import B, TIMING, end, start, word  # noqa: E402
from flat import (CAST, Light, Puppet, blob, capsule, cel, ellipse_path, glow, hexc, lerp_col, paint, poly_path,  # noqa: E402
                  rrect_path, shade, tint, with_alpha)
from kit import H, W, blink, lerp, span, wiggle  # noqa: E402

YOU = Puppet(CAST["mascot"], "you")
SKIN = CAST["mascot"].skin
MOON, PHONE_GLOW, WARM, RED_C = "#7d9cff", "#cfe6ff", "#ffc77a", "#ff3b2f"
WALL, WALL_D, WOOD, WOOD_D = "#2b3550", "#1c2438", "#6b4a32", "#4a3222"
SENDER = "+1 (555) 013-0317"
TEXTS = [("text1", "I'm outside. Let me in."), ("text2", "Don't listen to the thing pretending to be me."),
         ("text3", "There's a second door behind your wardrobe. Get inside. NOW.")]


def red_amt(t):
    return 0.0 if t < B["text3"] else min(1.0, (t - B["text3"]) / 10.0)


def hall_light(t):
    """Warm light under the bedroom door: on until 'Silence', then out (a faint cold glow later)."""
    if t < B["silence"]:
        return 1.0 - 0.6 * (wiggle(t, 3, 1, 4) > 0.75 and B["knocking"] <= t < B["knock_stop"])
    return 0.0


def light_you(t):
    if red_amt(t) > 0.2:
        return Light(dir=(0.8, -0.3), shadow_px=18, rim=RED_C, rim_alpha=0.6 + 0.3 * red_amt(t), rim_px=6)
    return Light(dir=(0.1, 0.9), shadow_px=16, rim=PHONE_GLOW, rim_alpha=0.6, rim_px=5)  # lit from the phone below


def night_grade(c, t, amount=1.0):
    full = skia.Rect.MakeWH(W, H)
    c.drawRect(full, paint("#5a6fb0", 0.35 * amount, blend=skia.BlendMode.kMultiply))
    r = red_amt(t)
    if r > 0:
        c.drawRect(full, paint("#c43a2c", 0.35 * r, blend=skia.BlendMode.kMultiply))
    flat.vignette(c, W, H, 0.55)


def moon_stripes(c, x0, y0, w, h, ang=-18, alpha=0.10, n=6):
    c.save()
    c.rotate(ang, x0 + w / 2, y0 + h / 2)
    for i in range(n):
        y = y0 + i * h / n
        c.drawRect(skia.Rect.MakeLTRB(x0, y, x0 + w, y + h / n * 0.45), paint(MOON, alpha))
    c.restore()


def dust(c, x, y, t, t0, n=10, spread=300):
    u = t - t0
    if not 0 <= u < 1.4:
        return
    for i in range(n):
        dx = (i - n / 2) * spread / n + math.sin(i * 3.1) * 20
        yy = y + u * (120 + 60 * (i % 3)) + 0.5 * 300 * u * u
        c.drawCircle(x + dx, yy, 2.5 + i % 3, paint("#d8d2c4", 0.6 * (1 - u / 1.4)))


# ============================================================================ YOU (in bed)

def you_pose(t):
    eo = blink(t, seed=31)
    P = dict(breathe=t, eye_open=eo, lid=0.5, mouth="flat", pupil=(0.0, 0.2), brow=(-0.1, 0.0), turn=0.05,
             arm_l=(8, 12), arm_r=(8, 12), head_tilt=-3)
    if t >= B["answer"] - 0.2:  # phone to your ear
        P.update(arm_r=(8, 12), lid=0.3, pupil=(-0.2, 0.0), _ear=True)
    if t >= start("R06"):  # freeze
        P.update(lid=0.0, eye_open=max(eo, 0.95), brow=(0.9, 0.5), mouth="o", pupil=(-0.6, 0.0), turn=-0.2)
    if t >= start("R08"):  # looking at the phone in front of you
        P.update(arm_r=(18, 118), hold_r="phone", pupil=(0.2, 0.75), lid=0.15, brow=(0.5, 0.6), mouth="flat", turn=0.05)
    if t >= start("R12"):  # stomach drops
        P.update(mouth="o", brow=(0.8, 1.0), pupil=(0.0, 0.3), lid=0.0)
    if t >= start("R17"):  # eyes on the door (screen left)
        P.update(pupil=(-0.9, 0.0), turn=-0.35, brow=(0.7, 0.8), mouth="flat")
    if t >= start("R18"):
        P.update(brow=(0.1, -0.4), lid=0.25, pupil=(-0.7, 0.0))
    if t >= start("R23"):  # turn toward the wardrobe (screen right)
        P.update(turn=0.55, pupil=(0.9, 0.0), brow=(0.8, 0.8), lid=0.0, mouth="o")
    if t >= start("R26"):
        P.update(eye_open=1.0, brow=(1.0, 0.9), mouth="o", talk=0.25, pupil=(0.8, 0.1))
    return P


def bedroom_bg(c, t, cx=540):
    flat.linear_grad(c, (0, 0, W, H), [WALL, WALL_D])
    moon_stripes(c, 80, 120, 900, 900, alpha=0.08)
    # headboard + pillow
    c.drawRoundRect(skia.Rect.MakeLTRB(cx - 520, 980, cx + 520, 1500), 40, 40, paint("#3a2a24"))
    c.drawRoundRect(skia.Rect.MakeLTRB(cx - 460, 1260, cx + 460, 1500), 60, 60, paint("#c9cfdc"))


def shot_you_cu(c, t):
    bedroom_bg(c, t)
    P = you_pose(t)
    ear = P.pop("_ear", False) and t < start("R08")
    P.pop("_ear", None)
    sc = 2.3
    YOU.draw(c, 540, 2430, sc, P, light=light_you(t), shadow=False)
    if ear:  # phone pressed to your ear (screen-left side of the head), hand under it
        L = light_you(t)
        hx, hy = 540 - 250, 980
        cel(c, capsule((hx - 40, hy + 520), (hx - 10, hy + 130), 120), CAST["mascot"].shirt, L, k=3)
        c.save()
        c.rotate(-12, hx, hy)
        c.drawRoundRect(skia.Rect.MakeLTRB(hx - 55, hy - 170, hx + 55, hy + 150), 22, 22, paint("#101216"))
        c.drawRoundRect(skia.Rect.MakeLTRB(hx - 45, hy - 160, hx + 45, hy + 140), 16, 16, paint(PHONE_GLOW, 0.5))
        c.restore()
        cel(c, ellipse_path(hx - 5, hy + 120, 70, 85), SKIN, L, k=2)
        glow(c, hx + 40, hy, 420, PHONE_GLOW, 0.25)
    # blanket over your lap
    c.drawPath(blob([(-60, 1720), (360, 1620), (760, 1660), (1140, 1600), (1140, H + 40), (-60, H + 40)], 0.4), paint("#3f5a8a"))
    c.drawPath(blob([(-60, 1720), (360, 1620), (760, 1660), (1140, 1600)], close=False), paint("#5d7bb0", stroke=10))
    # phone glow from below / beside
    gx, gy = (720, 1480) if t >= start("R08") else ((760, 820) if t >= B["answer"] - 0.2 else (900, 1800))
    glow(c, gx, gy, 700, PHONE_GLOW, 0.22 if t >= B["answer"] - 0.2 else 0.12)
    if start("R10") <= t < start("R12"):  # a bead of sweat
        ph = (t - start("R10")) / 2.0 % 1
        c.drawOval(skia.Rect.MakeLTRB(330, 640 + ph * 120, 344, 664 + ph * 120), paint("#e8f6ff", 0.8 * (1 - ph)))
    night_grade(c, t, 0.7)


# ============================================================================ clock / phone

def shot_clock_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), [WALL_D, "#0d1220"])
    c.drawRect(skia.Rect.MakeLTRB(0, 1180, W, H), paint(WOOD_D))  # nightstand top
    c.drawRect(skia.Rect.MakeLTRB(0, 1180, W, 1210), paint(WOOD))
    # clock body
    c.drawRoundRect(skia.Rect.MakeLTRB(170, 620, 910, 1190), 60, 60, paint("#121318"))
    c.drawRoundRect(skia.Rect.MakeLTRB(220, 700, 860, 1080), 30, 30, paint("#07080a"))
    txt = "3:16" if t < B["clock_flip"] else "3:17"
    kit.draw_text(c, txt, 540, 1000, 300, color="#ff2a1a", weight="Black")
    glow(c, 540, 890, 520, "#ff2a1a", 0.35)
    kit.draw_text(c, "AM", 790, 1060, 46, color="#ff2a1a", weight="Black", alpha=0.8)
    # phone beside, buzzing + screen glow
    buzz = wiggle(t, 40, 6, 1) if t < start("R03") else 0
    px = 980 + buzz
    c.drawRoundRect(skia.Rect.MakeLTRB(px - 40, 1060, px + 300, 1210), 24, 24, paint("#15171c"))
    c.drawRoundRect(skia.Rect.MakeLTRB(px - 28, 1070, px + 290, 1200), 18, 18, paint(PHONE_GLOW, 0.85))
    glow(c, px + 120, 1130, 420, PHONE_GLOW, 0.25 + 0.1 * math.sin(t * 10))
    night_grade(c, t, 0.5)


def phone_frame(c, t, hand=True, x=540, y=1000, tilt=0.0, buzz=0.0):
    c.save()
    c.translate(x + buzz, y)
    c.rotate(tilt)
    L = light_you(t)
    if hand:
        cel(c, blob([(-420, 420), (-300, 120), (-160, 260), (-120, 760), (-460, 900)], 0.4), SKIN, L, k=3)
    c.drawRoundRect(skia.Rect.MakeLTRB(-330, -700, 330, 700), 70, 70, paint("#101216"))
    c.drawRoundRect(skia.Rect.MakeLTRB(-300, -670, 300, 670), 52, 52, paint("#0b0d12"))
    c.drawRoundRect(skia.Rect.MakeLTRB(-60, -655, 60, -625), 15, 15, paint("#000000"))
    return L


def phone_end(c, t, hand=True):
    if hand:
        L = light_you(t)
        for k in range(3):  # fingers over the right edge
            cel(c, capsule((330, -120 + k * 130), (250, -100 + k * 130), 70), SKIN, L, k=2)
        cel(c, capsule((-330, 300), (-250, 160), 80), SKIN, L, k=2)
    c.restore()


def status_bar(c, t, red_batt=False):
    kit.draw_text(c, "3:17", 540 - 200, 1000 - 590, 34, color="#ffffff", weight="Bold")
    c.drawRoundRect(skia.Rect.MakeLTRB(540 + 190, 1000 - 615, 540 + 240, 1000 - 595), 4, 4, paint("#ffffff", stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(540 + 193, 1000 - 612, 540 + (205 if red_batt else 232), 1000 - 598),
               paint("#ff3b2f" if red_batt else "#ffffff"))


def screen_incoming(c, t):
    flat.linear_grad(c, (240, 330, 840, 1670), ["#25304a", "#0f1422"])
    kit.draw_text(c, "incoming call", 540, 520, 34, color="#c8d0e0", weight="SemiBold")
    c.drawCircle(540, 700, 110, paint("#55607a"))
    kit.draw_text(c, "?", 540, 740, 120, color="#ffffff", weight="Black")
    kit.draw_text(c, "Unknown Number", 540, 920, 60, color="#ffffff", weight="Bold")
    for k, col in enumerate(("#e2574c", "#3fb36b")):
        cx = 390 + k * 300
        pulse = 1 + 0.08 * math.sin(t * 8 + k)
        c.drawCircle(cx, 1420, 70 * pulse, paint(col))
    glow(c, 540, 1000, 700, PHONE_GLOW, 0.12)


def screen_call(c, t):
    flat.linear_grad(c, (240, 330, 840, 1670), ["#1d2638", "#0c1019"])
    kit.draw_text(c, "Unknown", 540, 620, 64, color="#ffffff", weight="Bold")
    el = max(0.0, t - B["answer"])
    kit.draw_text(c, f"{int(el // 60):02d}:{int(el % 60):02d}", 540, 690, 40, color="#9aa6bf", weight="SemiBold")
    amp = TIMING.mouth(t, "caller") if TIMING else 0.0
    for k in range(17):  # voice waveform
        h = 10 + amp * 140 * abs(math.sin(k * 1.7 + t * 18)) * (1 - abs(k - 8) / 10)
        c.drawRoundRect(skia.Rect.MakeLTRB(330 + k * 25, 980 - h, 344 + k * 25, 980 + h), 7, 7, paint("#9fd3ff", 0.9))
    c.drawCircle(540, 1420, 70, paint("#e2574c"))


def bubble_layout(texts, w=470, size=44):
    out = []
    for txt in texts:
        lines = kit.wrap(txt, size, w, "SemiBold")
        out.append((lines, size))
    return out


def screen_chat(c, t, notif_only=False):
    flat.linear_grad(c, (240, 330, 840, 1670), ["#0f131c", "#0a0d14"])
    if notif_only:  # lock screen with a notification card
        kit.draw_text(c, "3:17", 540, 640, 170, color="#ffffff", weight="Bold")
        u = span(t, B["text1"], B["text1"] + 0.3, "back")
        if u > 0:
            r = skia.Rect.MakeLTRB(270, 760 + (1 - u) * -60, 810, 930 + (1 - u) * -60)
            c.drawRoundRect(r, 26, 26, paint("#2a3040", 0.95 * min(1, u)))
            kit.draw_text(c, "Unknown", 300, r.top() + 52, 32, color="#ffffff", weight="Bold", align="left")
            kit.draw_text(c, "I'm outside. Let me in.", 300, r.top() + 112, 34, color="#d8deea", weight="SemiBold", align="left")
        return
    c.drawRect(skia.Rect.MakeLTRB(240, 330, 840, 520), paint("#151a24"))
    c.drawCircle(540, 400, 36, paint("#55607a"))
    kit.draw_text(c, "Unknown", 540, 475, 34, color="#ffffff", weight="Bold")
    kit.draw_text(c, SENDER, 540, 508, 22, color="#8a94a8", weight="SemiBold")
    y = 580
    for (key, txt) in TEXTS:
        tt = B[key]
        if t < tt - 0.7:
            break
        if t < tt:  # typing dots
            c.drawRoundRect(skia.Rect.MakeLTRB(270, y, 400, y + 70), 34, 34, paint("#2b3242"))
            for k in range(3):
                a = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 9 - k))
                c.drawCircle(300 + k * 35, y + 35, 9, paint("#c8d0e0", a))
            break
        lines = kit.wrap(txt, 42, 470, "SemiBold")
        bh = 34 + len(lines) * 54
        u = span(t, tt, tt + 0.25, "back")
        urgent = key == "text3"
        r = skia.Rect.MakeLTRB(270, y, 270 + 40 + max(kit.measure(l, 42, "SemiBold") for l in lines), y + bh)
        c.save()
        c.translate(270, y)
        c.scale(0.8 + 0.2 * u, 0.8 + 0.2 * u)
        c.translate(-270, -y)
        c.drawRoundRect(r, 30, 30, paint("#7a1f1a" if urgent else "#2b3242"))
        for i, ln in enumerate(lines):
            kit.draw_text(c, ln, 290, y + 60 + i * 54, 42, color="#ffffff", weight="SemiBold", align="left")
        c.restore()
        y += bh + 26


def shot_phone_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), [WALL_D, "#0a0e18"])
    on_stand = t < B["answer"] - 0.2
    if on_stand:  # on the nightstand, ringing and buzzing
        c.drawRect(skia.Rect.MakeLTRB(0, 1500, W, H), paint(WOOD_D))
        c.drawRect(skia.Rect.MakeLTRB(0, 1500, W, 1530), paint(WOOD))
        buzz = wiggle(t, 45, 10, 2)
        phone_frame(c, t, hand=False, y=950, tilt=-6, buzz=buzz)
        c.restore()
        c.save()
        c.translate(buzz, 0)
        c.translate(540, 950)
        c.rotate(-6)
        c.translate(-540, -950)
        screen_incoming(c, t)
        c.restore()
        for k in range(3):  # buzz marks
            a = 0.5 * (0.5 + 0.5 * math.sin(t * 20 + k))
            c.drawLine(140 - k * 30, 760, 140 - k * 30, 1140, paint("#ffffff", a * 0.4, stroke=6))
            c.drawLine(940 + k * 30, 760, 940 + k * 30, 1140, paint("#ffffff", a * 0.4, stroke=6))
        night_grade(c, t, 0.4)
        return
    flare = 1.0 + 0.6 * (1 - span(t, start("R21") - 0.1, start("R21") + 0.6, "out")) * (t >= start("R21") - 0.1)
    buzz = wiggle(t, 45, 8, 3) if (abs(t - B["text1"]) < 0.5 or abs(t - B["text2"]) < 0.5 or abs(t - B["text3"]) < 0.5) else 0
    phone_frame(c, t, hand=True, buzz=buzz)
    c.restore()
    c.save()
    c.translate(buzz, 0)
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(240, 330, 840, 1670), 52, 52))
    if t < start("R08") - 0.1:
        screen_call(c, t)
    elif t < start("R09") - 0.1:
        screen_chat(c, t, notif_only=True)
    else:
        screen_chat(c, t)
    status_bar(c, t, red_batt=t >= start("R21") - 0.1)
    c.restore()
    # thumb over the left edge
    c.save()
    c.translate(540 + buzz, 1000)
    cel(c, capsule((-350, 470), (-255, 250), 82), SKIN, light_you(t), k=2)
    c.restore()
    glow(c, 540, 1000, 820, PHONE_GLOW, 0.16 * flare)
    night_grade(c, t, 0.35)


# ============================================================================ the bedroom door

DOOR = skia.Rect.MakeLTRB(250, 330, 830, 1700)


def door_jolt(t):
    j = 0.0
    for kt in list(B["knocks"]) + [B["knocking"] + 0.05, B["knocking"] + 0.55]:
        u = t - kt
        if 0 <= u < 0.25:
            j = max(j, (1 - u / 0.25) * 9)
    return j


def handle_angle(t):
    return -38 * span(t, B["handle"] + 0.1, B["handle"] + 1.8, "inout") * (1 - span(t, start("R21"), start("R21") + 0.6))


def draw_door(c, t, r=DOOR, scale=1.0):
    j = door_jolt(t)
    bow = 6 * math.sin(math.pi * span(t, B["creak"], B["creak"] + 1.6, "linear"))
    c.save()
    c.translate(0, -j * 0.4)
    c.drawRect(skia.Rect.MakeLTRB(r.left() - 50, r.top() - 50, r.right() + 50, r.bottom()), paint("#6f7488"))  # frame
    c.drawRect(skia.Rect.MakeLTRB(r.left(), r.top(), r.right(), r.bottom()), paint("#7d8296"))
    flat.linear_grad(c, (r.left(), r.top(), r.right(), r.bottom()), ["#8d93a8", "#5f6478"], vertical=False, alpha=0.6)
    w, h = r.width(), r.height()
    for k in range(2):  # recessed panels
        for col in range(2):
            pr = skia.Rect.MakeLTRB(r.left() + 50 + col * (w / 2 - 25), r.top() + 60 + k * (h / 2 - 20),
                                    r.left() + w / 2 - 25 + col * (w / 2 - 25), r.top() + h / 2 - 40 + k * (h / 2 - 20))
            c.drawRoundRect(pr, 10, 10, paint("#4f5466", stroke=8))
    if bow > 0.1:
        c.drawRect(r, paint("#000000", 0.05 * bow))
    # lever handle
    hx, hy = r.right() - 80, r.top() + h * 0.52
    c.drawRoundRect(skia.Rect.MakeLTRB(hx - 26, hy - 70, hx + 26, hy + 70), 12, 12, paint("#b08a3e"))
    c.save()
    c.rotate(handle_angle(t), hx, hy)
    c.drawRoundRect(skia.Rect.MakeLTRB(hx - 130, hy - 14, hx + 14, hy + 14), 12, 12, paint("#d4ad5a"))
    c.restore()
    c.restore()
    # light under the door
    hl = hall_light(t)
    gap = skia.Rect.MakeLTRB(r.left() + 6, r.bottom() - 8, r.right() - 6, r.bottom())
    c.drawRect(gap, paint("#050505"))
    if hl > 0:
        c.drawRect(gap, paint(WARM, 0.9 * hl))
        glow(c, (r.left() + r.right()) / 2, r.bottom() + 10, 420, WARM, 0.28 * hl)
        if B["knocking"] <= t < B["knock_stop"]:  # a shadow passes
            sx = r.left() + (t * 180) % w
            c.drawRect(skia.Rect.MakeLTRB(sx, gap.top(), sx + 90, gap.bottom()), paint("#000000", 0.9))


def shot_door_wide(c, t):
    flat.linear_grad(c, (0, 0, W, H), [WALL, WALL_D])
    moon_stripes(c, -100, 200, 1300, 1300, alpha=0.07)
    c.drawRect(skia.Rect.MakeLTRB(0, 1700, W, H), paint("#2a2420"))
    draw_door(c, t)
    night_grade(c, t)


def shot_door_cu(c, t):
    c.save()
    c.translate(540, 900)
    c.scale(2.3, 2.3)
    c.translate(-540, -760)
    flat.linear_grad(c, (0, 0, W, H), [WALL, WALL_D])
    draw_door(c, t)
    c.restore()
    for kt in B["knocks"]:
        dust(c, 540, 300, t, kt, n=14, spread=700)
    night_grade(c, t)


def shot_door_under_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#202a40", "#141a28"])
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 1080), paint("#6f7488"))  # bottom of the door
    flat.linear_grad(c, (0, 0, W, 1080), ["#7d8296", "#555a6c"], alpha=0.7)
    c.drawRect(skia.Rect.MakeLTRB(0, 1080, W, 1150), paint("#7f95d6"))  # the gap: cold hallway light
    glow(c, 540, 1115, 600, "#8fa6ff", 0.25)
    for k, (x, t_in) in enumerate(((330, start("R15") - 0.2), (520, start("R15") - 0.2), (700, start("R15") + 1.2), (860, start("R15") + 1.4))):
        a = span(t, t_in, t_in + 0.6)
        if a > 0:
            c.drawRect(skia.Rect.MakeLTRB(x - 60 + wiggle(t, 1.2, 4, k), 1080, x + 60, 1150), paint("#000000", 0.95 * a))
    c.drawRect(skia.Rect.MakeLTRB(0, 1150, W, H), paint("#2a2420"))  # floorboards
    for k in range(6):
        c.drawLine(0, 1250 + k * 120, W, 1240 + k * 120, paint("#000000", 0.25, stroke=3))
    night_grade(c, t, 0.8)


def shot_handle_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#7d8296", "#545a6c"])
    pull = span(t, start("R19") - 0.06, end("R19"), "out") if t >= start("R19") - 0.06 else 0.0
    s = lerp(2.0, 1.4, pull)
    hx, hy = 560, 900
    c.save()
    c.translate(hx, hy)
    c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-60, -180, 60, 180), 24, 24, paint("#b08a3e"))  # back plate - no keyhole
    c.drawRoundRect(skia.Rect.MakeLTRB(-60, -180, 60, 180), 24, 24, paint("#7e6128", stroke=5))
    c.save()
    c.rotate(handle_angle(t))
    c.drawRoundRect(skia.Rect.MakeLTRB(-330, -32, 30, 32), 28, 28, paint("#d4ad5a"))
    c.drawRoundRect(skia.Rect.MakeLTRB(-330, -32, 30, -10), 20, 20, paint("#f2d48a", 0.6))
    c.restore()
    c.drawCircle(0, 0, 46, paint("#c69d4a"))
    c.restore()
    night_grade(c, t, 0.7)


# ============================================================================ room / wardrobe / small door

def shot_bed_wide(c, t):
    flat.linear_grad(c, (0, 0, W, H), [WALL, WALL_D])
    c.drawRect(skia.Rect.MakeLTRB(0, 1380, W, H), paint("#2a2420"))
    # window with blinds (back wall, top)
    c.drawRect(skia.Rect.MakeLTRB(360, 300, 720, 640), paint("#0b1430"))
    for k in range(9):
        c.drawRect(skia.Rect.MakeLTRB(360, 300 + k * 38, 720, 316 + k * 38), paint("#9fb6e8", 0.55))
    glow(c, 540, 470, 380, MOON, 0.18)
    # bedroom door (left)
    door = skia.Rect.MakeLTRB(30, 640, 300, 1390)
    c.drawRect(skia.Rect.MakeLTRB(10, 620, 320, 1390), paint("#6f7488"))
    c.drawRect(door, paint("#7d8296"))
    c.drawRoundRect(skia.Rect.MakeLTRB(240, 990, 280, 1010), 6, 6, paint("#d4ad5a"))
    c.drawRect(skia.Rect.MakeLTRB(36, 1382, 294, 1390), paint(WARM if hall_light(t) > 0 else "#050505"))
    # wardrobe (right), slightly off the wall
    wr = skia.Rect.MakeLTRB(800, 520, 1070, 1400)
    c.drawRect(skia.Rect.MakeLTRB(wr.left() + 18, wr.top() + 10, wr.right() + 18, wr.bottom()), paint("#0b0d14"))
    cel(c, rrect_path(wr.left(), wr.top(), wr.right(), wr.bottom(), 6), WOOD, Light(dir=(-0.6, -0.5), shadow_px=20))
    c.drawLine((wr.left() + wr.right()) / 2, wr.top() + 20, (wr.left() + wr.right()) / 2, wr.bottom() - 20, paint(WOOD_D, stroke=6))
    # bed + you
    c.drawRoundRect(skia.Rect.MakeLTRB(300, 980, 780, 1200), 30, 30, paint("#3a2a24"))
    P = you_pose(t)
    P.pop("_ear", None)
    YOU.draw(c, 540, 1720, 0.95, P, light=light_you(t), shadow=False)
    c.drawPath(blob([(240, 1420), (540, 1360), (840, 1420), (860, 1700), (220, 1700)], 0.4), paint("#3f5a8a"))
    if t >= B["answer"]:
        glow(c, 600, 1250, 360, PHONE_GLOW, 0.2)
    night_grade(c, t)


def shot_wardrobe_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), [WALL, WALL_D])
    c.drawRect(skia.Rect.MakeLTRB(0, 1600, W, H), paint("#2a2420"))
    # the small door, low on the wall behind the wardrobe (right side gap)
    reveal = span(t, B["small_door"] - 0.2, B["small_door"] + 1.0)
    sd = skia.Rect.MakeLTRB(700, 1150, 980, 1600)
    c.drawRect(skia.Rect.MakeLTRB(sd.left() - 16, sd.top() - 16, sd.right() + 16, sd.bottom()), paint("#3b2a1c"))
    c.drawRect(sd, paint("#5a3d26"))
    for k in range(4):
        x = sd.left() + 20 + k * 65
        c.drawLine(x, sd.top() + 10, x, sd.bottom() - 10, paint("#3b2a1c", stroke=5))
    c.drawCircle(sd.right() - 50, (sd.top() + sd.bottom()) / 2, 18, paint("#2a2a2a", stroke=6))
    # dust on the floor, scraped in an arc (the door has been opened from the inside)
    c.drawOval(skia.Rect.MakeLTRB(600, 1600, 1060, 1700), paint("#9a9488", 0.25))
    arc = skia.Path()
    arc.addArc(skia.Rect.MakeLTRB(700, 1450, 1000, 1750), 0, 180)
    c.drawPath(arc, paint("#2a2420", stroke=24))
    # wardrobe in front, an inch off the wall (shifts left on the reveal)
    off = lerp(0, -130, reveal)
    wr = skia.Rect.MakeLTRB(80 + off, 200, 760 + off, 1640)
    c.drawRect(skia.Rect.MakeLTRB(wr.right(), wr.top() + 30, wr.right() + 30, wr.bottom()), paint("#07080c", 0.8))
    cel(c, rrect_path(wr.left(), wr.top(), wr.right(), wr.bottom(), 8), WOOD, Light(dir=(-0.6, -0.5), shadow_px=24))
    mid = (wr.left() + wr.right()) / 2
    c.drawLine(mid, wr.top() + 30, mid, wr.bottom() - 30, paint(WOOD_D, stroke=8))
    for s in (-1, 1):
        c.drawRoundRect(skia.Rect.MakeLTRB(mid + s * 40 - 10, 880, mid + s * 40 + 10, 980), 5, 5, paint("#c69d4a"))
    glow(c, 860, 1380, 420, MOON, 0.10)
    night_grade(c, t)


def shot_small_door_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#3b2a1c", "#25190f"])
    pr = skia.Rect.MakeLTRB(90, 250, 990, 1750)
    c.drawRect(pr, paint("#5a3d26"))
    for k in range(6):  # planks
        x = pr.left() + 30 + k * 150
        c.drawLine(x, pr.top(), x, pr.bottom(), paint("#3b2a1c", stroke=8))
        c.drawLine(x + 60, pr.top() + 80 + k * 37, x + 70, pr.top() + 220 + k * 37, paint("#3b2a1c", 0.5, stroke=3))
    for y in (500, 1450):  # iron straps
        c.drawRect(skia.Rect.MakeLTRB(pr.left(), y - 26, pr.right(), y + 26), paint("#2c2a28"))
        for x in range(150, 1000, 160):
            c.drawCircle(x, y, 9, paint("#55504a"))
    # keyhole + ring
    kx, ky = 760, 980
    c.drawCircle(kx, ky - 30, 34, paint("#020202"))
    c.drawPath(poly_path([(kx - 20, ky - 10), (kx + 20, ky - 10), (kx + 32, ky + 80), (kx - 32, ky + 80)]), paint("#020202"))
    c.drawCircle(kx - 220, ky, 70, paint("#2c2a28", stroke=14))
    # fresh scratches appearing from the other side
    sc = span(t, B["scratch"], B["scratch"] + 2.4, "linear")
    for i in range(7):
        u = max(0.0, min(1.0, sc * 7 - i))
        if u <= 0:
            continue
        x0, y0 = 260 + i * 70, 700 + (i % 3) * 140
        c.drawLine(x0, y0, x0 + 40 * u, y0 + 360 * u, paint("#d9c3a0", 0.85, stroke=6))
        c.drawLine(x0 + 18, y0 + 10, x0 + 18 + 40 * u, y0 + 10 + 330 * u, paint("#d9c3a0", 0.6, stroke=4))
    dust(c, 540, 1100, t, B["scratch"] + 0.2, n=12, spread=500)
    # breath on the keyhole ("Finally. You found me.")
    if t >= B["found_me"] - 0.3:
        br = 0.5 + 0.5 * math.sin((t - B["found_me"]) * 2 * math.pi / 1.5)
        c.drawCircle(kx, ky + 10, 120 + 30 * br, paint("#dfe8f0", 0.10 + 0.08 * br, blur=30))
    night_grade(c, t, 0.6)


def shot_choice_bg(c, t):
    c.clear(hexc("#05060a"))
    breathe = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 2.4)
    # left: your bedroom door (B), handle down, cold light under it
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 0, 538, H))
    c.translate(-250, 260)
    c.scale(1.0, 1.0)
    flat.linear_grad(c, (0, -260, W, H), [WALL, WALL_D])
    draw_door(c, max(t, B["handle"] + 2.0))
    c.restore()
    glow(c, 270, 1880, 380, "#5f7bd0", 0.12 + 0.12 * breathe)
    # right: the small door (A), breath at the keyhole
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(542, 0, W, H))
    c.drawRect(skia.Rect.MakeLTRB(542, 0, W, H), paint("#25190f"))
    c.translate(164, 330)
    c.scale(0.85, 0.85)
    shot_small_door_cu(c, t)
    c.restore()
    glow(c, 810, 1000, 380, "#ff5a4a", 0.10 + 0.10 * breathe)
    c.drawRect(skia.Rect.MakeLTRB(536, 0, 544, H), paint("#000000"))
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", 0.35))
    night_grade(c, t, 0.5)


SHOTS = dict(clock_cu=shot_clock_cu, phone_cu=shot_phone_cu, you_cu=shot_you_cu, door_wide=shot_door_wide,
             door_cu=shot_door_cu, door_under_cu=shot_door_under_cu, handle_cu=shot_handle_cu, bed_wide=shot_bed_wide,
             wardrobe_cu=shot_wardrobe_cu, small_door_cu=shot_small_door_cu, choice_bg=shot_choice_bg)
