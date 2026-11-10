"""VIDEO_008 - THE FREQUENCY THAT KNOWS TOMORROW, Part 1: radio studio at 1:06 AM.

You (the mascot) never speak - the voices are recordings / the phone, so the SPEAKERS, VU METERS and the PHONE
react to the voice instead of a mouth.  Your face + body follow the scene table's emotion per line (flat.emote).
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
from beats import B, CLOCK0, TIMING, end, start  # noqa: E402
from flat import CAST, Light, Puppet, capsule, cel, emote, glow, hexc, paint, poly_path, rrect_path  # noqa: E402
from kit import H, W, blink, lerp, span, wiggle  # noqa: E402

YOU = Puppet(CAST["mascot"], "you")
RED_C, WARM, MONI = "#ff3b2f", "#ffcf8a", "#9fc8ff"
FEET_Y = 1840  # you sit high enough that the desk crosses your chest, not your chin
VOICES = ("radio", "phone", "unknown")


def amp(t, who=VOICES):
    if not TIMING:
        return 0.0
    return max(TIMING.mouth(t, w) for w in who)


def red_amt(t):
    return 0.0 if t < start("F15") - 0.1 else min(1.0, (t - start("F15")) / 25.0) * 0.8 + 0.2


def grade(c, t, k=1.0):
    full = skia.Rect.MakeWH(W, H)
    c.drawRect(full, paint("#c8b8a8", 0.10 * k, blend=skia.BlendMode.kMultiply))
    r = red_amt(t)
    if r > 0:
        c.drawRect(full, paint("#d0453a", 0.30 * r * k, blend=skia.BlendMode.kMultiply))
    flat.vignette(c, W, H, 0.45)


def you_emotion(t):
    import edit_video008 as E
    cur, prev, t_cur = "calm", "calm", 0.0
    for sid, line, emo in E.SCENE_EMO:
        t0 = E._t0(sid, line)
        if t >= t0:
            prev, cur, t_cur = cur, emo, t0
    return prev, cur, span(t, t_cur, t_cur + 0.3)


def you_pose(t):
    prev, cur, u = you_emotion(t)
    P = dict(eye_open=blink(t, seed=81), pupil=(0.0, 0.0), turn=0.05)
    P = emote(P, prev, t)
    P = emote(P, cur, t, amount=u)
    # where you look
    if start("F05") <= t < start("F08") or start("F13") <= t < start("F16") or start("F20") <= t < start("F23"):
        P["pupil"] = (0.7, -0.4)        # up at the speakers
    if start("F10") <= t < start("F13") or start("F16") <= t < start("F20") or t >= start("F27"):
        P["pupil"] = (0.8, 0.4)         # at the phone (desk, right)
    if start("F08") <= t < start("F10") or start("F24") <= t < start("F27"):
        P["pupil"] = (-0.8, 0.3)        # at the computer (desk, left)
    return P


# ============================================================================ the studio (frontal)

def foam(c, l, tp, r, b, col="#2a2d33"):
    c.drawRect(skia.Rect.MakeLTRB(l, tp, r, b), paint(col))
    for y in range(int(tp), int(b), 60):
        for x in range(int(l), int(r), 60):
            c.drawPath(poly_path([(x, y), (x + 60, y), (x + 30, y + 30)]), paint("#000000", 0.12))


def on_air(c, x, y, s=1.0, t=0.0):
    on = 1.0 if t > 0.05 else 0.0
    if t < 0.6:
        on = 1.0 if int(t * 14) % 2 else 0.3  # flickers on at frame 0
    c.drawRoundRect(skia.Rect.MakeLTRB(x - 170 * s, y - 50 * s, x + 170 * s, y + 50 * s), 14 * s, 14 * s,
                    paint("#ff3b2f" if on > 0.5 else "#4a1512"))
    kit.draw_text(c, "ON AIR", x, y + 22 * s, 66 * s, color="#ffffff" if on > 0.5 else "#7a3a35", weight="Black", max_w=320 * s)
    if on > 0.5:
        glow(c, x, y, 380 * s, RED_C, 0.35)


def studio(c, t, you_x=540, you_scale=1.2, step=0.0, faders=True):
    flat.linear_grad(c, (0, 0, W, H), ["#2f3238", "#1d1f24"])
    foam(c, 0, 160, W, 1150)
    # window to the dark control room
    c.drawRect(skia.Rect.MakeLTRB(300, 430, 780, 860), paint("#0b0e14"))
    c.drawRect(skia.Rect.MakeLTRB(300, 430, 780, 860), paint("#4a4f58", stroke=14))
    on_air(c, 540, 270, 0.8, t)
    # wall speakers
    for x in (110, 970):
        c.drawRoundRect(skia.Rect.MakeLTRB(x - 80, 380, x + 80, 640), 12, 12, paint("#15171b"))
        a = amp(t) if t >= B["speakers_on"] else 0.0
        c.drawCircle(x, 540, 56 + 6 * a, paint("#2a2d33"))
        c.drawCircle(x, 540, 20, paint("#3a3e46"))
        c.drawCircle(x, 440, 22, paint("#2a2d33"))
        c.drawCircle(x + 56, 400, 6, paint("#3fd06b" if t >= B["speakers_on"] else "#173a22"))
    # wall clock (left of the window)
    c.drawCircle(200, 760, 70, paint("#e9e6df"))
    sec = CLOCK0 + int(t)
    for ang, ln, wdt, col in (((1 + (sec // 60) / 60) / 12 * 360, 36, 8, "#1a1a1a"),
                              ((sec // 60) % 60 / 60 * 360, 54, 6, "#1a1a1a"), ((sec % 60) / 60 * 360, 60, 3, "#c0392b")):
        a = math.radians(ang - 90)
        c.drawLine(200, 760, 200 + math.cos(a) * ln, 760 + math.sin(a) * ln, paint(col, stroke=wdt))
    # transmitter rack (right edge)
    c.drawRect(skia.Rect.MakeLTRB(900, 700, 1080, 1350), paint("#121418"))
    for k in range(12):
        on = (int(t * 3 + k * 1.7) % 3) != 0
        c.drawCircle(940 + (k % 3) * 40, 760 + (k // 3) * 60, 8, paint("#3fd06b" if on else "#123a1e"))
    # you, behind the desk
    P = you_pose(t)
    L = Light(dir=(-0.3, -0.8), shadow_px=16, rim=RED_C if red_amt(t) > 0.3 else WARM, rim_alpha=0.6, rim_px=5)
    YOU.draw(c, you_x, FEET_Y, you_scale, P, light=L, shadow=False)
    # desk + console + computer (left) + phone (right) + mic boom (right, clear of the face)
    c.drawRect(skia.Rect.MakeLTRB(0, 1350, W, H), paint("#3a2a22"))
    c.drawRect(skia.Rect.MakeLTRB(0, 1330, W, 1370), paint("#5a4030"))
    c.drawRoundRect(skia.Rect.MakeLTRB(300, 1250, 780, 1360), 14, 14, paint("#202328"))
    for k in range(8 if faders else 0):  # (left out of close-ups: they'd sit right under the caption line)
        y = 1290 + 20 * math.sin(k * 1.3)
        c.drawRect(skia.Rect.MakeLTRB(330 + k * 56, 1270, 340 + k * 56, 1345), paint("#0e0f12"))
        c.drawRoundRect(skia.Rect.MakeLTRB(320 + k * 56, y, 350 + k * 56, y + 18), 4, 4, paint("#c8ccd2"))
    c.drawRoundRect(skia.Rect.MakeLTRB(40, 1080, 290, 1300), 12, 12, paint("#15171b"))
    c.drawRoundRect(skia.Rect.MakeLTRB(56, 1096, 274, 1260), 8, 8, paint("#2b4a7a"))
    glow(c, 165, 1180, 260, MONI, 0.12)
    c.drawRoundRect(skia.Rect.MakeLTRB(820, 1250, 1040, 1350), 16, 16, paint("#1b1d22"))
    ringing = (B["ring"] <= t < B["ring_stop"]) or (B["ring2"] <= t < start("F28"))
    blink3 = ringing and int(t * 4) % 2 == 0
    c.drawCircle(1000, 1290, 10, paint(RED_C if blink3 or (start("F17") <= t < start("F19")) else "#3a1512"))
    c.drawLine(1040, 140, 760, 1080, paint("#2a2d33", stroke=14))  # boom arm from the ceiling, right
    c.drawRoundRect(skia.Rect.MakeLTRB(730, 1050, 800, 1200), 30, 30, paint("#15171b"))


def shot_studio_wide(c, t):
    step = span(t, start("F19"), start("F19") + 1.2)  # you slowly step away from the phone (to the left, back)
    studio(c, t, you_x=540 - 110 * step, you_scale=1.2 - 0.08 * step)
    grade(c, t)


def shot_you_cu(c, t):
    c.save()
    c.translate(540, 900)
    c.scale(1.9, 1.9)
    c.translate(-540, -1000)
    studio(c, t, faders=False)
    c.restore()
    glow(c, 120, 1500, 700, MONI, 0.10)
    grade(c, t)


def shot_onair_cu(c, t):
    foam(c, 0, 0, W, H, "#25282e")
    on_air(c, 540, 820, 2.4, t)
    grade(c, t, 0.6)


def shot_clock_cu(c, t):
    foam(c, 0, 0, W, H, "#25282e")
    cx, cy, r = 540, 900, 380
    c.drawCircle(cx, cy, r + 30, paint("#15171b"))
    c.drawCircle(cx, cy, r, paint("#ece9e2"))
    for k in range(60):
        a = math.radians(k * 6 - 90)
        r0 = r - (40 if k % 5 == 0 else 18)
        c.drawLine(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * (r - 8), cy + math.sin(a) * (r - 8),
                   paint("#1a1a1a", stroke=10 if k % 5 == 0 else 4))
    sec = CLOCK0 + t
    hrs = (1 + (sec / 60) / 60) % 12
    for ang, ln, wdt, col in ((hrs / 12 * 360, 200, 20, "#1a1a1a"), ((sec / 60) % 60 / 60 * 360, 300, 14, "#1a1a1a"),
                              ((int(sec) % 60) / 60 * 360, 330, 6, "#c0392b")):
        a = math.radians(ang - 90)
        c.drawLine(cx, cy, cx + math.cos(a) * ln, cy + math.sin(a) * ln, paint(col, stroke=wdt))
    c.drawCircle(cx, cy, 18, paint("#c0392b"))
    grade(c, t, 0.6)


def shot_speaker_cu(c, t):
    foam(c, 0, 0, W, H, "#25282e")
    c.drawRoundRect(skia.Rect.MakeLTRB(190, 300, 890, 1600), 40, 40, paint("#121418"))
    on = t >= B["speakers_on"]
    a = amp(t) if on else 0.0
    if on and (abs(t - B["crackle"]) < 0.8 or abs(t - B["speakers_on"]) < 0.5):
        a = max(a, 0.6 + 0.4 * math.sin(t * 60))
    for k, r in enumerate((280, 230, 170)):
        c.drawCircle(540, 1120, r + 14 * a * (1 - k * 0.3), paint(["#2a2d33", "#22252a", "#1b1d22"][k]))
    c.drawCircle(540, 1120, 80 + 10 * a, paint("#3a3e46"))
    c.drawCircle(540, 560, 120, paint("#22252a"))
    c.drawCircle(540, 560, 50, paint("#3a3e46"))
    c.drawCircle(800, 380, 18, paint("#3fd06b" if on else "#173a22"))
    if on:
        glow(c, 800, 380, 80, "#3fd06b", 0.4)
    grade(c, t, 0.7)


def shot_console_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#1d1f24", "#121316"])
    c.drawRoundRect(skia.Rect.MakeLTRB(60, 300, 1020, 1700), 30, 30, paint("#202328"))
    # LCD: what's playing
    c.drawRoundRect(skia.Rect.MakeLTRB(120, 360, 960, 640), 16, 16, paint("#0c1a12"))
    kit.draw_text(c, "PLAYING:  UNTITLED", 160, 440, 46, color="#8cf5a8", weight="Bold", align="left")
    kit.draw_text(c, "REC TIME  01:07:30 AM", 160, 520, 46, color="#ff8a7a", weight="Black", align="left")
    kit.draw_text(c, "VOICE  MATCH: YOU", 160, 600, 34, color="#8cf5a8", weight="Bold", align="left")
    a = amp(t)
    for k, x in enumerate((300, 780)):  # analog VU meters
        c.drawRoundRect(skia.Rect.MakeLTRB(x - 210, 720, x + 210, 1040), 16, 16, paint("#efe2b8"))
        c.drawArc(skia.Rect.MakeLTRB(x - 170, 780, x + 170, 1120), 210, 120, False, paint("#1a1a1a", stroke=4))
        c.drawArc(skia.Rect.MakeLTRB(x - 170, 780, x + 170, 1120), 300, 30, False, paint("#c0392b", stroke=10))
        lvl = min(1.0, a * (0.9 + 0.15 * k) + 0.04 * wiggle(t, 20, 1, k))
        ang = math.radians(-60 + 120 * lvl - 90)
        c.drawLine(x, 1040, x + math.cos(ang) * 230, 1040 + math.sin(ang) * 230, paint("#1a1a1a", stroke=6))
        kit.draw_text(c, "VU", x, 1010, 34, color="#5a4a2a", weight="Black")
    for k in range(8):  # faders (below the caption line)
        y = 1640 + 40 * math.sin(k * 1.7)
        c.drawRect(skia.Rect.MakeLTRB(150 + k * 105, 1580, 162 + k * 105, 1760), paint("#0b0c0e"))
        c.drawRoundRect(skia.Rect.MakeLTRB(130 + k * 105, y, 182 + k * 105, y + 40), 6, 6, paint("#d8dce2"))
    if a > 0.05:
        glow(c, 540, 880, 600, "#ff8a7a", 0.12 * a)
    grade(c, t, 0.7)


def shot_computer_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#1d1f24", "#121316"])
    c.drawRoundRect(skia.Rect.MakeLTRB(60, 420, 1020, 1380), 30, 30, paint("#15171b"))
    scr = skia.Rect.MakeLTRB(100, 460, 980, 1340)
    flat.linear_grad(c, (scr.left(), scr.top(), scr.right(), scr.bottom()), ["#1f3a66", "#132544"])
    c.drawRect(skia.Rect.MakeLTRB(100, 460, 980, 520), paint("#0d1830"))
    kit.draw_text(c, "WKTM PLAYOUT 3.2", 130, 502, 32, color="#9fc8ff", weight="Bold", align="left")
    if t < start("F24") - 0.1:  # searching for the recording
        c.drawRoundRect(skia.Rect.MakeLTRB(150, 580, 930, 660), 10, 10, paint("#0d1830"))
        kit.draw_text(c, "search: 01:07:30  voice=you", 175, 635, 34, color="#ffffff", weight="SemiBold", align="left")
        u = span(t, start("F08"), start("F08") + 1.0)
        if u < 1:
            kit.draw_text(c, "Searching recordings" + "." * (1 + int(t * 4) % 3), 540, 860, 48, color="#9fc8ff", weight="Bold")
        else:
            kit.draw_text(c, "No file found.", 540, 860, 74, color="#ff8a7a", weight="Black")
            kit.draw_text(c, "Scheduled broadcasts: none", 540, 960, 40, color="#9fc8ff", weight="Bold")
    else:
        u = span(t, start("F24"), start("F24") + 0.3, "back")
        box = skia.Rect.MakeLTRB(140, 600 + (1 - u) * 40, 940, 1260)
        c.drawRoundRect(box, 20, 20, paint("#0b1222", 0.97 * min(1, u)))
        c.drawRect(skia.Rect.MakeLTRB(box.left(), box.top(), box.right(), box.top() + 90), paint("#c0392b"))
        kit.draw_text(c, "TRANSMISSION RECEIVED", 540, box.top() + 64, 48, color="#ffffff", weight="Black", max_w=760)
        if t >= start("F25") - 0.1:
            kit.draw_text(c, "FROM: WKTM 98.7 FM  (THIS STATION)", 540, box.top() + 170, 36, color="#ffcf8a", weight="Bold",
                          max_w=760)
        if t >= start("F26") - 0.1:
            for i, ln in enumerate(["STOP LISTENING", "TO THE VERSION OF YOU", "THAT WANTS TO SURVIVE."]):
                kit.draw_text(c, ln, 540, box.top() + 300 + i * 90, 60, color="#ffffff", weight="Black", max_w=760)
    glow(c, 540, 900, 700, MONI, 0.14)
    grade(c, t, 0.6)


def desk_phone(c, t, cx=540, cy=1000, s=1.0, shake=0.0):
    c.save()
    c.translate(cx + shake, cy)
    c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-380, -260, 380, 300), 50, 50, paint("#1b1d22"))
    c.drawRoundRect(skia.Rect.MakeLTRB(-400, -330, 400, -170), 70, 70, paint("#24272d"))  # handset
    c.drawRoundRect(skia.Rect.MakeLTRB(-120, -130, 300, -40), 10, 10, paint("#0c1a12"))  # display
    ringing = (B["ring"] <= t < B["ring_stop"]) or (B["ring2"] <= t < start("F28"))
    connected = start("F17") - 0.1 <= t < start("F19") or start("F28") - 0.1 <= t < B["freeze"]
    txt = "LINE 3  RINGING" if ringing else ("LINE 3  CONNECTED" if connected else "")
    if txt:
        kit.draw_text(c, txt, 90, -70, 30, color="#8cf5a8", weight="Bold", max_w=400)
    for k in range(4):  # line buttons 1-4
        y = -110 + k * 80
        lit = k == 2 and ((ringing and int(t * 4) % 2 == 0) or connected)
        c.drawRoundRect(skia.Rect.MakeLTRB(-330, y, -170, y + 56), 10, 10, paint("#33363c"))
        c.drawCircle(-140, y + 28, 14, paint(RED_C if lit else "#3a1512"))
        f = kit.font(30, "Black")
        c.drawString(f"LINE {k + 1}", -315, y + 40, f, paint("#c8ccd2"))
    for k in range(12):
        c.drawRoundRect(skia.Rect.MakeLTRB(-60 + (k % 3) * 120, 0 + (k // 3) * 66, 40 + (k % 3) * 120, 52 + (k // 3) * 66),
                        8, 8, paint("#33363c"))
    a = amp(t, ("phone", "unknown"))
    for k in range(10):  # handset earpiece holes glow with the voice
        c.drawCircle(-320 + k * 18, -250, 6, paint("#ffcf8a", 0.15 + 0.85 * a))
    c.restore()
    if a > 0.05:
        glow(c, cx - 230 * s, cy - 250 * s, 260, "#ffcf8a", 0.25 * a)


def shot_phone_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#3a2a22", "#241912"])
    ringing = (B["ring"] <= t < B["ring_stop"]) or (B["ring2"] <= t < start("F28"))
    desk_phone(c, t, s=1.22, shake=wiggle(t, 50, 8, 2) if ringing else 0.0)
    glow(c, 540, 900, 700, WARM, 0.10)
    grade(c, t, 0.7)


def shot_receiver_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#3a2a22", "#241912"])
    desk_phone(c, t, cx=540, cy=1050, s=1.36)
    grade(c, t, 0.7)


def shot_cable_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#2a2420", "#1a1512"])
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 900), paint("#2f3238"))  # wall
    c.drawRect(skia.Rect.MakeLTRB(0, 880, W, 920), paint("#4a4038"))  # skirting
    c.drawRoundRect(skia.Rect.MakeLTRB(700, 600, 840, 780), 12, 12, paint("#e6e2d8"))  # empty wall jack
    c.drawRoundRect(skia.Rect.MakeLTRB(745, 660, 795, 710), 6, 6, paint("#1a1a1a"))
    cord = skia.Path()
    cord.moveTo(-20, 1000)
    cord.cubicTo(250, 1180, 300, 960, 520, 1100)
    cord.cubicTo(640, 1180, 600, 1250, 520, 1230)
    c.drawPath(cord, paint("#d8d4c8", stroke=18))
    c.save()
    c.rotate(-30, 520, 1230)
    c.drawRoundRect(skia.Rect.MakeLTRB(430, 1190, 530, 1265), 10, 10, paint("#cfd6dd", 0.95))  # the plug, lying loose
    c.drawRect(skia.Rect.MakeLTRB(445, 1202, 485, 1215), paint("#c9a14a"))
    c.restore()
    glow(c, 600, 1300, 600, "#ffcf8a", 0.08)
    grade(c, t, 0.8)


SWITCH = (380, 900, 700, 1100)  # MAIN POWER switch box (kept clear of captions)


def shot_transmitter_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#1d1f24", "#121316"])
    c.drawRoundRect(skia.Rect.MakeLTRB(160, 200, 920, 1800), 20, 20, paint("#0f1114"))
    kit.draw_text(c, "TX-1  TRANSMITTER", 540, 300, 54, color="#d8dce2", weight="Black")
    for r in range(3):
        c.drawRect(skia.Rect.MakeLTRB(200, 360 + r * 140, 880, 480 + r * 140), paint("#1b1e23"))
        for k in range(8):
            on = (int(t * 4 + k * 1.3 + r) % 4) != 0
            col = ["#3fd06b", "#f2b134", RED_C][(k + r) % 3]
            c.drawCircle(250 + k * 80, 420 + r * 140, 12, paint(col if on else "#1f2a22"))
    l, tp, r_, b = SWITCH
    kit.draw_text(c, "MAIN POWER", 540, tp - 20, 40, color="#ffffff", weight="Black")
    c.drawRoundRect(skia.Rect.MakeLTRB(l, tp, r_, b), 20, 20, paint("#2a2d33"))
    c.drawRoundRect(skia.Rect.MakeLTRB(l + 90, tp + 30, r_ - 90, b - 30), 14, 14, paint(RED_C))
    c.drawPath(capsule((540, 1800), (540, H + 50), 60), paint("#1a1a1a"))
    glow(c, 540, (tp + b) / 2, 300, RED_C, 0.25)
    grade(c, t, 0.7)


def shot_choice_bg(c, t):
    c.clear(hexc("#060608"))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 0, 538, H))
    c.translate(270 - 540 * 0.55, 620)
    c.scale(0.55, 0.55)
    shot_transmitter_cu(c, t)
    c.restore()
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(542, 0, W, H))
    flat.linear_grad(c, (542, 0, W, H), ["#3a2a22", "#241912"])
    desk_phone(c, t, cx=810, cy=1150, s=0.68)
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(536, 0, 544, H), paint("#000000"))
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", 0.35))
    flat.vignette(c, W, H, 0.6)


def _face_zone(x, s):
    hx, hy = YOU.head_pos(x, FEET_Y, s)
    r = YOU.HEAD_RX * YOU.s.head_scale * s
    return (hx - r * 1.15, hy - r * 1.5, hx + r * 1.15, hy + r * 1.35)


def _cu_zone(t):
    l, tp, r, b = _face_zone(540, 1.2)  # map through the CU transform
    f = lambda x, y: (540 + (x - 540) * 1.9, 900 + (y - 1000) * 1.9)  # noqa: E731
    (l2, t2), (r2, b2) = f(l, tp), f(r, b)
    return [("your face", l2, t2, r2, b2)]


ZONES = {"transmitter_cu": lambda t: [("MAIN POWER switch", *SWITCH)],
         "cable_cu": lambda t: [("the unplugged plug", 400, 1150, 560, 1290)],
         "studio_wide": lambda t: [("your face", *_face_zone(540 - 110 * span(t, start("F19"), start("F19") + 1.2),
                                                             1.2 - 0.08 * span(t, start("F19"), start("F19") + 1.2)))],
         "you_cu": _cu_zone}

SHOTS = dict(onair_cu=shot_onair_cu, console_cu=shot_console_cu, studio_wide=shot_studio_wide, clock_cu=shot_clock_cu,
             speaker_cu=shot_speaker_cu, you_cu=shot_you_cu, computer_cu=shot_computer_cu, phone_cu=shot_phone_cu,
             cable_cu=shot_cable_cu, receiver_cu=shot_receiver_cu, transmitter_cu=shot_transmitter_cu, choice_bg=shot_choice_bg)
