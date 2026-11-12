"""VIDEO_013 - AFTER HOURS, Part 1: five friends sneak into school at midnight to fix their exam answers.

The five (YOU, KAI, BEN, MIA, ZOE) act every line with flat.emote; Mia lip-syncs her lines.  The teacher is a voice on
the intercom, red ink, chalk writing by itself - and two jumpscares (her face at the door window, then at the board).
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
from beats import B, TIMING, end, start, word  # noqa: E402,F401
from flat import CAST, Light, Puppet, Style, blob, capsule, cel, ellipse_path, emote, glow, hexc, paint, poly_path, rrect_path  # noqa: E402
from kit import H, W, blink, lerp, span  # noqa: E402

KIDS = {
    "you": Puppet(CAST["mascot"], "you"),
    "kai": Puppet(Style(skin="#c98f62", hair="#15131a", hair_style="spiky", shirt="#e3b23c", shirt_detail="#2a2a35",
                        pants="#2f3440", eyes="#2a1a12", height=1.04), "kai"),
    "ben": Puppet(Style(skin="#f0c8a8", hair="#8a5a2b", hair_style="short", shirt="#3f8f5a", shirt_detail="#e9ecef",
                        pants="#4a4038", eyes="#3a2a1e", glasses=True, width=1.12, height=0.98), "ben"),
    "mia": Puppet(Style(skin="#e8b894", hair="#5a2d3a", hair_style="long", shirt="#f2a2c0", shirt_detail="#ffffff",
                        pants="#3b3f4a", eyes="#4a2e1c", skirt=True, height=0.95), "mia"),
    "zoe": Puppet(Style(skin="#9a6a4a", hair="#1a1418", hair_style="bun", shirt="#8f5fe0", shirt_detail="#e9e2f8",
                        pants="#2a2e3a", eyes="#1a1210", height=0.96), "zoe"),
}
ORDER = ["ben", "mia", "you", "kai", "zoe"]
TORCH = "#fff1c4"
VARIANT = {  # the same group mood, played differently by each of them
    "kai": {"nervous": "determined", "sad": "angry", "suspicious": "determined"},
    "ben": {"nervous": "scared", "determined": "nervous", "suspicious": "nervous"},
    "zoe": {"happy": "teasing", "scared": "suspicious"},
}


def emo_at(t):
    import edit_video013 as E
    cur = prev = "calm"
    t_cur = 0.0
    for sid, line, emo in E.SCENE_EMO:
        t0 = E._t0(sid, line)
        if t >= t0:
            prev, cur, t_cur = cur, emo, t0
    return prev, cur, span(t, t_cur, t_cur + 0.3)


def pose(name, t, look=(0.0, 0.0)):
    p, cu, u = emo_at(t)
    v = VARIANT.get(name, {})
    seed = ORDER.index(name) + 3
    P = emote(emote(dict(eye_open=blink(t, seed=70 + seed)), v.get(p, p), t, seed=seed), v.get(cu, cu), t, amount=u, seed=seed)
    P["pupil"] = look
    if name == "mia" and TIMING:
        P = TIMING.lip(P, t, "mia")
    return P


def teacher_face(c, x, y, s, t, alpha=1.0):
    """Ms. ___ : grey skin, a tight bun, round glasses that reflect white so you never see her eyes, a thin wide smile."""
    j = 3 * math.sin(t * 57)
    c.drawCircle(x + j, y - 150 * s, 62 * s, paint("#2a2a30", alpha))  # bun
    c.drawPath(ellipse_path(x + j, y - 20 * s, 132 * s, 158 * s), paint("#2a2a30", alpha))
    c.drawPath(ellipse_path(x + j, y, 116 * s, 146 * s), paint("#b9bcc0", alpha))
    for side in (-1, 1):
        ex = x + j + side * 50 * s
        c.drawCircle(ex, y - 24 * s, 40 * s, paint("#f4f6f8", alpha))
        c.drawCircle(ex, y - 24 * s, 40 * s, paint("#1a1a1e", alpha, stroke=7 * s))
        c.drawPath(ellipse_path(ex - 10 * s, y - 34 * s, 14 * s, 8 * s), paint("#ffffff", alpha))
    c.drawLine(x + j - 10 * s, y - 24 * s, x + j + 10 * s, y - 24 * s, paint("#1a1a1e", alpha, stroke=7 * s))
    m = skia.Path()
    m.moveTo(x + j - 84 * s, y + 58 * s)
    m.quadTo(x + j, y + 84 * s, x + j + 84 * s, y + 58 * s)
    m.quadTo(x + j, y + 112 * s, x + j - 84 * s, y + 58 * s)
    m.close()
    c.drawPath(m, paint("#3a0c10", alpha))
    c.save()
    c.clipPath(m, doAntiAlias=True)
    for k in range(-5, 6):
        c.drawRoundRect(skia.Rect.MakeLTRB(x + j + k * 16 * s - 7 * s, y + 54 * s, x + j + k * 16 * s + 7 * s, y + 84 * s), 3, 3,
                        paint("#eeeae0", alpha))
    c.restore()


# ============================================================================ the hallway, the five of you

def hallway(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#0c0e18", "#141826"])
    c.drawPath(poly_path([(0, H), (360, 1000), (720, 1000), (W, H)]), paint("#1a1e2c"))          # floor
    c.drawPath(poly_path([(0, 0), (360, 420), (360, 1000), (0, H)]), paint("#161a28"))           # left lockers
    c.drawPath(poly_path([(W, 0), (720, 420), (720, 1000), (W, H)]), paint("#161a28"))
    for k in range(5):
        u = k / 5
        for side in (-1, 1):
            x = 540 + side * lerp(540, 180, u)
            c.drawLine(x, lerp(0, 420, u), x, lerp(H, 1000, u), paint("#0a0c14", stroke=6))
    c.drawRect(skia.Rect.MakeLTRB(360, 420, 720, 1000), paint("#07080e"))                       # the far end
    c.drawRoundRect(skia.Rect.MakeLTRB(490, 440, 590, 484), 6, 6, paint("#0f2a16"))
    kit.draw_text(c, "EXIT", 540, 474, 28, color="#5dff8f", weight="Black", max_w=90)
    glow(c, 540, 462, 220, "#5dff8f", 0.18)


def group(c, t, feet, sc, xs, kai=True, look=(0.0, 0.0)):
    L = Light(dir=(0.0, 0.9), shadow_px=12, rim=TORCH, rim_alpha=0.8, rim_px=5)
    for name, x in zip(ORDER, xs):
        if name == "kai" and not kai:
            continue
        KIDS[name].draw(c, x, feet, sc, pose(name, t, look), light=L, shadow=True)


def shot_hall_group(c, t):
    hallway(c, t)
    sway = 30 * math.sin(t * 1.1)
    flat.light_cone(c, (540, 1500), (160 + sway, 600), (920 + sway, 600), TORCH, 0.16)
    group(c, t, 1470, 0.66, (150, 345, 540, 735, 930), look=(0.3 * math.sin(t * 0.9), -0.1))
    flat.vignette(c, W, H, 0.6)


def shot_group_cu(c, t):
    """Room 12, the five of you facing the door ... then four."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#10121c"))
    c.drawRect(skia.Rect.MakeLTRB(0, 300, W, 760), paint("#18301f"))  # the blackboard behind you
    c.drawRect(skia.Rect.MakeLTRB(0, 300, W, 760), paint("#3a2c22", stroke=18))
    c.drawRect(skia.Rect.MakeLTRB(0, 1470, W, H), paint("#1a1e2c"))
    kai = t < B["slam"]
    group(c, t, 1470, 0.72, (130, 335, 540, 745, 950), kai=kai, look=(0.9, 0.0) if t < B["slam"] + 1.5 else (0.0, 0.0))
    if not kai:  # where Kai stood: his flashlight, still on, rolling to a stop
        u = span(t, B["slam"], B["slam"] + 1.2, "out")
        fx = 745 + 60 * u
        glow(c, fx + 120, 1490, 260, TORCH, 0.3)
        c.save()
        c.rotate(-200 * (1 - u), fx, 1490)
        c.drawRoundRect(skia.Rect.MakeLTRB(fx - 60, 1472, fx + 50, 1508), 12, 12, paint("#e3b23c"))
        c.drawRoundRect(skia.Rect.MakeLTRB(fx + 40, 1462, fx + 80, 1518), 8, 8, paint("#c9ccd2"))
        c.restore()
    flat.vignette(c, W, H, 0.55)


# ============================================================================ the night before

def shot_game_night(c, t):
    """Five webcam tiles in a group call: everybody gaming at 4 AM."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#101218"))
    tiles = [(80, 330), (560, 330), (80, 700), (560, 700), (320, 1070)]
    cols = {"you": "#2a3a6a", "kai": "#5a4a1a", "ben": "#1f4a30", "mia": "#5a2a44", "zoe": "#3a2a6a"}
    L = Light(dir=(0.0, 0.9), shadow_px=10, rim="#9fd3ff", rim_alpha=0.8, rim_px=4)
    for (x, y), name in zip(tiles, ["you", "kai", "mia", "ben", "zoe"]):
        r = rrect_path(x, y, x + 440, y + 340, 30)
        c.drawPath(r, paint(cols[name]))
        c.save()
        c.clipPath(r, doAntiAlias=True)
        glow(c, x + 220, y + 340, 300, "#9fd3ff", 0.3 + 0.1 * math.sin(t * 9 + x))
        P = pose(name, t, (0.0, 0.4))
        P["head_tilt"] = P.get("head_tilt", 0) + 5 * math.sin(t * 6 + x * 0.01)
        if name != "mia" or not P.get("speaking"):
            P["mouth"] = "grin"
        KIDS[name].draw(c, x + 220, y + 690, 0.72, P, light=L, shadow=False)
        c.restore()
        speaking = name == "mia" and TIMING and TIMING.talking(t, "mia")
        c.drawPath(r, paint("#3ddc84" if speaking else "#2a2e3a", stroke=10 if speaking else 6))
        c.drawRoundRect(skia.Rect.MakeLTRB(x + 14, y + 284, x + 150, y + 326), 10, 10, paint("#000000", 0.6))
        kit.draw_text(c, name.upper(), x + 82, y + 316, 30, color="#ffffff", weight="Bold", max_w=120)
    wave = span(t, start("L01") + 1.2, start("L01") + 1.5, "back")
    if wave > 0:
        c.drawRoundRect(skia.Rect.MakeLTRB(300, 210, 780, 300), 18, 18, paint("#ffd23f", min(1.0, wave)))
        kit.draw_text(c, "VICTORY #1", 540, 276, 56, color="#1a1c22", weight="Black", max_w=440)
    flat.vignette(c, W, H, 0.4)


def shot_exam_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#c49a6c", "#a87c52"])
    c.save()
    c.rotate(-4, 540, 800)
    c.drawRect(skia.Rect.MakeLTRB(150, 260, 930, 1340), paint("#f4efe2"))
    kit.draw_text(c, "FINAL EXAM", 540, 360, 64, color="#1a1c22", weight="Black", max_w=700)
    kit.draw_text(c, "Name:  you", 200, 440, 36, color="#3a3f4e", weight="SemiBold", align="left", max_w=500)
    for row in range(8):
        y = 520 + row * 90
        kit.draw_text(c, f"{row + 1}.", 220, y + 14, 34, color="#1a1c22", weight="Bold", max_w=60)
        for k in range(4):
            c.drawCircle(330 + k * 110, y, 24, paint("#1a1c22", stroke=4))
        pick = (row * 3 + 1) % 4
        c.drawCircle(330 + pick * 110, y, 18, paint("#3a3f4e"))
        c.drawLine(790, y - 22, 840, y + 22, paint("#d0312d", stroke=8))  # wrong
        c.drawLine(840, y - 22, 790, y + 22, paint("#d0312d", stroke=8))
    c.restore()
    v = span(t, B["fail"] - 0.15, B["fail"] + 0.1, "back")
    if v > 0:
        s = 2.2 - 1.2 * min(1.0, v)
        c.save()
        c.translate(700, 420)
        c.rotate(-14)
        c.scale(s, s)
        c.drawCircle(0, 0, 150, paint("#d0312d", stroke=16))
        kit.draw_text(c, "F", 0, 60, 190, color="#d0312d", weight="Black", max_w=200)
        c.restore()
        kit.draw_text(c, "12 / 100", 700, 660, 70, color="#d0312d", weight="Black", max_w=400)
    flat.vignette(c, W, H, 0.4)


def shot_plan_cu(c, t):
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#08090e"))
    c.drawRoundRect(skia.Rect.MakeLTRB(50, 150, 1030, 1420), 60, 60, paint("#15171e"))
    c.drawRoundRect(skia.Rect.MakeLTRB(76, 176, 1004, 1394), 40, 40, paint("#0d1018"))
    kit.draw_text(c, "the squad (5)", 540, 270, 50, color="#ffffff", weight="Bold", max_w=600)
    msgs = [("KAI", "#e3b23c", "answer sheets are in Room 12", start("L04") + 0.2),
            ("KAI", "#e3b23c", "we go in TONIGHT. midnight.", word("L04", "The")),
            ("MIA", "#f2a2c0", "you are actually insane", word("L04", "locked")),
            ("ZOE", "#8f5fe0", "gym window never locks...", word("L04", "Tonight,")),
            ("BEN", "#3f8f5a", "...i'm in", word("L04", "fix"))]
    for k, (who, colr, txt, t0) in enumerate(msgs):
        v = span(t, t0, t0 + 0.22, "back")
        if v <= 0:
            continue
        y = 350 + k * 200
        c.drawCircle(150, y + 70, 40, paint(colr, min(1.0, v)))
        kit.draw_text(c, who[0], 150, y + 88, 46, color="#ffffff", weight="Black", max_w=60)
        kit.draw_text(c, who, 210, y + 30, 28, color=colr, weight="Bold", align="left", max_w=200)
        c.drawRoundRect(skia.Rect.MakeLTRB(206, y + 44, 950, y + 150), 30, 30, paint("#2b3242", min(1.0, v)))
        kit.draw_text(c, txt, 236, y + 112, 42, color="#ffffff", weight="SemiBold", align="left", max_w=690)
    flat.vignette(c, W, H, 0.45)


# ============================================================================ room 12

def chalk_text(c, txt, x, y, size, u):
    n = max(0, min(len(txt), int(len(txt) * u + 0.999))) if u > 0 else 0
    if n:
        f = kit.font(size, "Black")
        c.drawString(txt[:n], x, y, f, paint("#f2f2ea", 0.92))


def room12(c, t, teacher=0.0):
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#10121c"))
    c.drawRect(skia.Rect.MakeLTRB(90, 330, 800, 830), paint("#18301f"))  # blackboard
    c.drawRect(skia.Rect.MakeLTRB(90, 330, 800, 830), paint("#3a2c22", stroke=18))
    kit.draw_text(c, "ROOM 12", 445, 410, 44, color="#cfd8c8", weight="Black", max_w=400, alpha=0.5)
    if t >= B["chalk"] and t >= B["story"]:
        u1 = span(t, B["chalk"], B["chalk"] + 1.6, "linear")
        u2 = span(t, word("L11", "Four"), B["chalk_end"], "linear")
        chalk_text(c, "KAI - DETENTION", 140, 570, 64, u1)
        chalk_text(c, "4 LEFT", 140, 700, 110, u2)
        if 0 < u1 < 1 or 0 < u2 < 1:  # the chalk itself, moving with no hand
            cx = 140 + (560 * u1 if u2 <= 0 else 380 * u2)
            cy = 560 if u2 <= 0 else 680
            c.drawRoundRect(skia.Rect.MakeLTRB(cx, cy - 40, cx + 16, cy + 10), 5, 5, paint("#ffffff"))
    # intercom + clock
    c.drawRoundRect(skia.Rect.MakeLTRB(860, 330, 1000, 430), 12, 12, paint("#2a2d33"))
    for k in range(4):
        c.drawLine(880, 352 + k * 18, 980, 352 + k * 18, paint("#4a4f58", stroke=5))
    c.drawCircle(930, 560, 52, paint("#d9d6cc"))
    c.drawLine(930, 560, 930, 522, paint("#1a1a1a", stroke=6))
    c.drawLine(930, 560, 930, 530, paint("#1a1a1a", stroke=9))
    # door (right) with a window
    c.drawRect(skia.Rect.MakeLTRB(850, 660, 1040, 1300), paint("#3a2c22"))
    c.drawRect(skia.Rect.MakeLTRB(900, 720, 990, 880), paint("#0a0c14"))
    if teacher > 0:  # she is IN the room now, by the board
        tx = 770
        c.drawPath(blob([(tx - 110, 1300), (tx - 90, 760), (tx + 90, 760), (tx + 110, 1300)], 0.3), paint("#06070c", teacher))
        c.drawPath(ellipse_path(tx, 660, 62, 78), paint("#06070c", teacher))
        c.drawCircle(tx, 580, 34, paint("#06070c", teacher))
        for side in (-1, 1):
            c.drawCircle(tx + side * 26, 652, 15, paint("#f4f6f8", teacher))
    # teacher's desk: the stack of answer sheets, the red pen
    c.drawRect(skia.Rect.MakeLTRB(120, 1180, 820, 1300), paint("#5a4030"))
    c.drawRect(skia.Rect.MakeLTRB(100, 1150, 840, 1190), paint("#6a4c38"))
    for k in range(5):
        c.save()
        c.rotate(-6 + k * 3, 470, 1120)
        c.drawRect(skia.Rect.MakeLTRB(350, 1070 - k * 6, 590, 1150 - k * 6), paint("#f4efe2"))
        c.restore()
    c.drawLine(380, 1094, 520, 1094, paint("#d0312d", stroke=6))
    c.drawLine(640, 1140, 760, 1110, paint("#d0312d", stroke=12))
    sway = 40 * math.sin(t * 0.9)
    glow(c, 470 + sway, 1000, 620, TORCH, 0.22)
    flat.vignette(c, W, H, 0.6)


def shot_room12(c, t):
    room12(c, t)


def shot_choice_bg(c, t):
    room12(c, t, teacher=1.0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", 0.3))
    flat.vignette(c, W, H, 0.5)


def shot_papers_cu(c, t):
    """The answer sheets.  A red pen is marking them - nobody is holding it (hook) / already marked (L07)."""
    flat.linear_grad(c, (0, 0, W, H), ["#5a4030", "#3a2a20"])
    names = ["YOU", "KAI", "BEN", "MIA", "ZOE"]
    hook = t < B["story"]
    wu = span(t, B["hook_cut"] + 0.3, B["story"] - 0.3, "linear") if hook else 1.0
    for k, nm in enumerate(names):
        c.save()
        c.rotate(-8 + k * 4, 540, 2200)
        x0 = 50 + k * 162
        c.drawRect(skia.Rect.MakeLTRB(x0, 330, x0 + 330, 1260), paint("#f4efe2"))
        c.drawRect(skia.Rect.MakeLTRB(x0, 330, x0 + 330, 1260), paint("#000000", 0.25, stroke=3))
        kit.draw_text(c, nm, x0 + 24, 400, 40, color="#1a1c22", weight="Black", align="left", max_w=200)
        for row in range(6):
            c.drawLine(x0 + 24, 470 + row * 60, x0 + 200, 470 + row * 60, paint("#8a8f98", stroke=5))
        if k == 4 or not hook:  # top sheet shows the note being written
            u = wu if k == 4 else 1.0
            f = kit.font(54, "Black")
            for j, ln in enumerate(("SEE ME.", "TONIGHT.")):
                n = int(len(ln) * max(0.0, min(1.0, u * 2 - j)) + 0.999) if u * 2 - j > 0 else 0
                c.drawString(ln[:n], x0 + 24, 930 + j * 80, f, paint("#d0312d"))
            if u > 0.05:
                c.drawCircle(x0 + 250, 420, 46, paint("#d0312d", stroke=9))
                kit.draw_text(c, "F", x0 + 250, 444, 62, color="#d0312d", weight="Black", max_w=70)
        c.restore()
    if hook:  # the pen, writing on its own
        px, py = 730 + 160 * ((wu * 2) % 1), 930 + (80 if wu > 0.5 else 0) + 6 * math.sin(t * 40)
        c.save()
        c.rotate(28, px, py)
        c.drawRoundRect(skia.Rect.MakeLTRB(px - 14, py - 300, px + 14, py - 30), 10, 10, paint("#d0312d"))
        c.drawPath(poly_path([(px - 14, py - 30), (px + 14, py - 30), (px, py)]), paint("#2a2a30"))
        c.restore()
    flat.vignette(c, W, H, 0.5)


def shot_intercom_cu(c, t):
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#10121c"))
    c.drawRoundRect(skia.Rect.MakeLTRB(240, 460, 840, 900), 30, 30, paint("#2a2d33"))
    a = max(TIMING.mouth(t, "teacher") if TIMING else 0.0, 0.0)
    for k in range(9):
        c.drawLine(290, 510 + k * 44, 790, 510 + k * 44, paint("#8a8f98" if a < 0.05 else "#ff6a5a", 0.6 + 0.4 * a, stroke=12 + 6 * a))
    c.drawCircle(780, 950, 14, paint("#ff4a3a" if math.sin(t * 8) > 0 else "#5a1a14"))
    kit.draw_text(c, "ROOM 12", 540, 1040, 60, color="#cfd3dc", weight="Black", max_w=400, alpha=0.7)
    glow(c, 540, 680, 600, "#ff4a3a", 0.2 * a)
    flat.vignette(c, W, H, 0.55)


def shot_scare_door(c, t):
    """JUMPSCARE 1: the little window in the classroom door - her face is pressed against it."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#3a2c22"))
    u = t - B["scare1"]
    win = rrect_path(170, 300, 910, 1300, 30)
    c.drawPath(win, paint("#05060a"))
    c.save()
    c.clipPath(win, doAntiAlias=True)
    teacher_face(c, 540, 820, 2.5 + 0.7 * u, t)
    c.drawLine(170, 300, 600, 1300, paint("#ffffff", 0.05, stroke=160))
    c.restore()
    c.drawPath(win, paint("#1a1410", stroke=26))
    flat.vignette(c, W, H, 0.6)


def shot_scare_teacher(c, t):
    """JUMPSCARE 2: the chalk stops.  She is standing right in front of you."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#18301f"))
    kit.draw_text(c, "4 LEFT", 540, 300, 150, color="#f2f2ea", weight="Black", alpha=0.5)
    u = t - B["scare2"]
    c.drawPath(blob([(60, H), (160, 1350), (920, 1350), (1020, H)], 0.3), paint("#0c0d12"))
    teacher_face(c, 540, 880, 2.7 + 0.8 * u, t)
    flat.vignette(c, W, H, 0.6)


ZONES = {
    "hall_group": lambda t: [("faces", 60, 900, 1020, 1130)],
    "group_cu": lambda t: [("faces", 40, 860, 1040, 1120)],
    "game_night": lambda t: [("tiles", 80, 330, 1000, 1410)],
    "exam_cu": lambda t: [("exam", 150, 260, 930, 1340)],
    "plan_cu": lambda t: [("chat", 100, 350, 960, 1340)],
    "room12": lambda t: [("board", 90, 330, 800, 830), ("desk", 100, 1040, 840, 1300)],
    "choice_bg": lambda t: [("desk", 100, 1040, 840, 1300)],
    "papers_cu": lambda t: [("papers", 130, 330, 950, 1260)],
    "intercom_cu": lambda t: [("speaker", 240, 460, 840, 900)],
    "scare_door": lambda t: [("face", 170, 300, 910, 1300)],
    "scare_teacher": lambda t: [("face", 200, 440, 880, 1300)],
}
SHOTS = dict(hall_group=shot_hall_group, group_cu=shot_group_cu, game_night=shot_game_night, exam_cu=shot_exam_cu,
             plan_cu=shot_plan_cu, room12=shot_room12, choice_bg=shot_choice_bg, papers_cu=shot_papers_cu,
             intercom_cu=shot_intercom_cu, scare_door=shot_scare_door, scare_teacher=shot_scare_teacher)
