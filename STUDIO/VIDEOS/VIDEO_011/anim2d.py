"""VIDEO_011 - LAST ONE IN THE CALL, Part 1: a normal night of gaming, then the squad leaves the voice chat one by one.

YOU are the only character on screen (headset on, lit by the monitor); Jay is a voice-chat tile whose ring follows his
voice.  Two jumpscares: Jay's tile turns into a grinning face (scare_tile) and the face behind you (scare_face).
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
from beats import B, TIMING, end, left, start, word  # noqa: E402,F401
from flat import CAST, Light, Puppet, blob, capsule, cel, ellipse_path, emote, glow, hexc, paint, poly_path, rrect_path  # noqa: E402
from kit import H, W, blink, lerp, span  # noqa: E402

YOU = Puppet(CAST["mascot"], "you")
FEET, SC, YOU_X = 1880, 1.1, 540
SCREEN, LED = "#7fb8ff", "#b06cff"


def emo_at(t):
    import edit_video011 as E
    cur = prev = "calm"
    t_cur = 0.0
    for sid, line, you in E.SCENE_EMO:
        t0 = E._t0(sid, line)
        if t >= t0:
            prev, cur, t_cur = cur, you, t0
    return prev, cur, span(t, t_cur, t_cur + 0.3)


def pose(t):
    p, cu, u = emo_at(t)
    you = emote(emote(dict(eye_open=blink(t, seed=41), pupil=(0.0, 0.25)), p, t, seed=2), cu, t, amount=u, seed=2)
    L = lambda a, b: a <= t < b  # noqa: E731
    you["pupil"] = (0.0, 0.3)  # eyes on the monitor (just under the camera)
    if L(B["story"], start("L03")):  # hyped, bouncing a little
        you.update(head_tilt=4 * math.sin(t * 7), mouth="grin")
    if L(start("L05"), start("L07")):  # listening hard: eyes flick to the side
        you["pupil"] = (0.7 * math.sin(t * 1.3), 0.1)
    if L(start("L09") - 0.1, start("L10")):  # reading the phone in your hand
        you.update(pupil=(0.2, 0.95), head_tilt=-4)
    if L(start("L11"), B["freeze"]):  # frozen: only the eyes move, to the reflection, then to the window
        you["pupil"] = (0.0, 0.3) if t < start("L12") else (-0.95, 0.0)
    if t >= B["freeze"]:
        you["pupil"] = (-0.95, 0.0)
    return you


def door_open(t):
    return span(t, B["scare2"], B["scare2"] + 0.2) if t >= B["story"] else 0.0


def pale_grin(c, x, y, s, t, alpha=1.0):
    """The thing wearing a friend's face: grey skin, hollow eyes with pin pupils, a grin that is too wide."""
    j = 3 * math.sin(t * 61)
    c.drawPath(ellipse_path(x + j, y - 30 * s, 150 * s, 170 * s), paint("#0c0e14", alpha))  # hair / hood
    c.drawPath(ellipse_path(x + j, y, 128 * s, 150 * s), paint("#b4bcc8", alpha))
    for side in (-1, 1):
        ex = x + j + side * 52 * s
        c.drawPath(ellipse_path(ex, y - 26 * s, 34 * s, 42 * s), paint("#05070b", alpha))
        c.drawCircle(ex, y - 26 * s, 6 * s, paint("#ffffff", alpha))
        c.drawLine(ex - 30 * s, y - 78 * s, ex + 30 * s, y - (90 if side < 0 else 90) * s + side * -10 * s, paint("#3a4252", alpha, stroke=7 * s))
    m = skia.Path()  # grin from ear to ear
    m.moveTo(x + j - 92 * s, y + 46 * s)
    m.quadTo(x + j, y + 86 * s, x + j + 92 * s, y + 46 * s)
    m.quadTo(x + j, y + 150 * s, x + j - 92 * s, y + 46 * s)
    m.close()
    c.drawPath(m, paint("#14080a", alpha))
    c.save()
    c.clipPath(m, doAntiAlias=True)
    for k in range(-5, 6):
        c.drawRoundRect(skia.Rect.MakeLTRB(x + j + k * 18 * s - 8 * s, y + 40 * s, x + j + k * 18 * s + 8 * s, y + 84 * s), 3, 3,
                        paint("#eef0e8", alpha))
    c.restore()


# ============================================================================ your room (camera sits on top of the monitor)

def room(c, t, people=True, cu=False):
    op = door_open(t)
    flat.linear_grad(c, (0, 0, W, H), ["#14162a", "#1b1e38"])
    c.drawLine(0, 300, W, 300, paint(LED, 0.9, stroke=10))  # LED strip
    glow(c, 540, 300, 900, LED, 0.18 + 0.03 * math.sin(t * 2))
    # window (left) - curtains, moonlight
    c.drawRect(skia.Rect.MakeLTRB(90, 430, 390, 900), paint("#0d1830"))
    c.drawCircle(300, 520, 34, paint("#dfe8ff", 0.9))
    c.drawLine(240, 430, 240, 900, paint("#2a3050", stroke=8))
    c.drawRect(skia.Rect.MakeLTRB(90, 430, 390, 900), paint("#2a3050", stroke=12))
    for x0, x1 in ((70, 150), (330, 410)):
        c.drawPath(blob([(x0, 410), (x1, 410), (x1 - 10, 930), (x0 + 10, 930)], 0.2), paint("#3a2f5c"))
    if t >= B["knocks"][0] - 2.0 and t >= B["story"]:  # someone is at YOUR window now
        a = span(t, B["knocks"][0] - 2.0, B["knocks"][0] - 1.0)
        c.drawPath(ellipse_path(215, 700, 42, 54), paint("#05070b", 0.9 * a))
        c.drawPath(blob([(150, 900), (165, 770), (265, 770), (280, 900)], 0.4), paint("#05070b", 0.9 * a))
    # poster
    c.drawRect(skia.Rect.MakeLTRB(470, 470, 640, 700), paint("#263a6a"))
    kit.draw_text(c, "GG", 555, 610, 70, color="#ffd23f", weight="Black", max_w=150)
    # bedroom door (right): closed all night ... until it isn't
    c.drawRect(skia.Rect.MakeLTRB(740, 420, 990, 1160), paint("#0c0d18"))  # frame / dark hallway
    if op > 0:
        c.drawRect(skia.Rect.MakeLTRB(760, 440, 970, 1160), paint("#1a2440"))
        glow(c, 865, 800, 300, "#3a5488", 0.25)
        c.drawPath(ellipse_path(865, 640, 44, 56), paint("#04050a"))  # someone standing in it
        c.drawPath(blob([(790, 1160), (800, 730), (930, 730), (940, 1160)], 0.35), paint("#04050a"))
        for side in (-1, 1):
            c.drawCircle(865 + side * 16, 636, 4, paint("#ffffff", 0.9))
        c.drawPath(poly_path([(760, 440), (760 - 120 * op, 470), (760 - 120 * op, 1190), (760, 1160)]), paint("#3a2c22"))
    else:
        c.drawRect(skia.Rect.MakeLTRB(760, 440, 970, 1160), paint("#3a2c22"))
        c.drawCircle(790, 820, 10, paint("#b9953f"))
    # gaming chair + you
    c.drawPath(rrect_path(YOU_X - 200, 900, YOU_X + 200, 1700, 90), paint("#16171f"))
    c.drawPath(rrect_path(YOU_X - 170, 930, YOU_X - 120, 1660, 20), paint("#c0392b"))
    c.drawPath(rrect_path(YOU_X + 120, 930, YOU_X + 170, 1660, 20), paint("#c0392b"))
    if people:
        L = Light(dir=(0.0, 0.8), shadow_px=14, rim=SCREEN, rim_alpha=0.85, rim_px=6)
        p = pose(t)
        YOU.draw(c, YOU_X, FEET, SC, p, light=L, shadow=False)
        headset(c, t, p)
    # desk + the top edge of the monitor (its light on everything)
    c.drawRect(skia.Rect.MakeLTRB(0, 1465, W, H), paint("#23201e"))
    c.drawRect(skia.Rect.MakeLTRB(0, 1465, W, 1480), paint("#3a3430"))
    c.drawRoundRect(skia.Rect.MakeLTRB(120, 1790, 960, H + 40), 20, 20, paint("#08090c"))
    flick = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 5.1)
    glow(c, 540, 1800, 900, SCREEN, 0.3 * flick)
    c.drawRoundRect(skia.Rect.MakeLTRB(60, 1560, 150, 1760), 16, 16, paint("#2fbf6b"))  # energy drink
    c.drawRect(skia.Rect.MakeLTRB(60, 1620, 150, 1680), paint("#101216"))
    flat.vignette(c, W, H, 0.55)


def headset(c, t, p):
    hx, hy = YOU.head_pos(YOU_X, FEET, SC, p)
    r = YOU.HEAD_RX * YOU.s.head_scale * SC
    c.save()
    c.rotate(p.get("head_tilt", 0), hx, hy + 60)
    band = skia.Path()
    band.moveTo(hx - r * 1.05, hy + 6)
    band.cubicTo(hx - r * 1.15, hy - r * 1.75, hx + r * 1.15, hy - r * 1.75, hx + r * 1.05, hy + 6)
    c.drawPath(band, paint("#16171c", stroke=22))
    for side in (-1, 1):
        c.drawPath(rrect_path(hx + side * r * 1.05 - 26, hy - 44, hx + side * r * 1.05 + 26, hy + 64, 22), paint("#1d1f26"))
        c.drawPath(rrect_path(hx + side * r * 1.05 - 12, hy - 22, hx + side * r * 1.05 + 12, hy + 42, 10), paint("#3ddc84"))
    mic = skia.Path()
    mic.moveTo(hx - r * 1.05, hy + 50)
    mic.quadTo(hx - r * 0.95, hy + 118, hx - r * 0.42, hy + 104)
    c.drawPath(mic, paint("#16171c", stroke=8))
    c.drawCircle(hx - r * 0.42, hy + 104, 12, paint("#16171c"))
    c.restore()


def shot_room_wide(c, t):
    room(c, t)


def shot_you_cu(c, t):
    x, y = YOU.head_pos(YOU_X, FEET, SC)
    c.save()
    c.translate(540, 900)
    c.scale(2.2, 2.2)
    c.translate(-x, -(y + 60))
    room(c, t)
    c.restore()
    flat.vignette(c, W, H, 0.4)


# ============================================================================ the voice chat

TILES = [("you", "YOU", "#d0312d", 80, 330), ("jay", "JAY", "#2fbf6b", 560, 330),
         ("marcus", "MARCUS", "#e08a2f", 80, 780), ("dee", "DEE", "#8f5fe0", 560, 780)]


def jay_level(t):
    return max(TIMING.mouth(t, "jay") if TIMING else 0.0, 0.0)


def shot_call_ui(c, t):
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#101218"))
    c.drawRect(skia.Rect.MakeLTRB(0, 150, W, 280), paint("#181b24"))
    c.drawCircle(110, 215, 16, paint("#3ddc84"))
    kit.draw_text(c, "VOICE · the boys", 150, 232, 46, color="#e8eaf0", weight="Bold", align="left", max_w=600)
    n_in = 4 - sum(1 for k in ("marcus", "dee") if left(k, t))
    kit.draw_text(c, f"{n_in} in call", 990, 230, 36, color="#8a90a0", weight="SemiBold", align="right", max_w=260)
    hook = t < B["story"]
    wrong = hook or t >= B["scare1_end"]  # after the scream, whatever is on Jay's mic isn't Jay
    for key, name, colr, x, y in TILES:
        gone = left(key, t)
        rect = skia.Rect.MakeLTRB(x, y, x + 440, y + 410)
        c.drawRoundRect(rect, 36, 36, paint("#1d212c" if not gone else "#14161c"))
        cx, cy = x + 220, y + 170
        if key == "jay":
            lvl = jay_level(t)
            if wrong and lvl < 0.05:  # no words - just slow breathing on an open mic
                lvl = 0.25 + 0.2 * math.sin(t * 2.4)
            if lvl > 0.04:
                ring = "#ff4a3a" if wrong else "#3ddc84"
                c.drawRoundRect(rect, 36, 36, paint(ring, 0.5 + 0.5 * lvl, stroke=10))
                glow(c, cx, cy, 300, ring, 0.25 * lvl)
        if key == "you" and not gone and math.sin(t * 3) > 0.97:
            c.drawRoundRect(rect, 36, 36, paint("#3ddc84", 0.5, stroke=8))
        a = 0.3 if gone else 1.0
        c.drawCircle(cx, cy, 104, paint(colr if not gone else "#3a3d48", a))
        kit.draw_text(c, name[0], cx, cy + 36, 110, color="#ffffff", weight="Black", alpha=a, max_w=160)
        if key == "jay" and wrong:
            c.drawCircle(cx, cy, 104, paint("#000000", 0.45))
        kit.draw_text(c, name, cx, y + 350, 44, color="#e8eaf0" if not gone else "#5a5f6c", weight="Bold", max_w=380)
        if gone:
            kit.draw_text(c, "left the call", cx, y + 392, 30, color="#c0564a", weight="SemiBold", max_w=380)
            t_left = {"marcus": B["leave1"], "dee": B["leave2"]}[key]
            if not hook and 0 <= t - t_left < 0.5:
                c.drawRoundRect(rect, 36, 36, paint("#ff4a3a", 1 - (t - t_left) / 0.5, stroke=10))
    # bottom bar
    c.drawRoundRect(skia.Rect.MakeLTRB(300, 1250, 780, 1370), 60, 60, paint("#181b24"))
    for k, colr in enumerate(("#3a3f4e", "#3a3f4e", "#d0312d")):
        c.drawCircle(400 + k * 140, 1310, 42, paint(colr))
    flat.vignette(c, W, H, 0.45)


def shot_scare_tile(c, t):
    """JUMPSCARE 1: Jay screams and his tile fills the screen with a grinning face, tearing like a bad stream."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#0a1a10"))
    u = t - B["scare1"]
    pale_grin(c, 540, 820, 2.3 + 0.6 * u, t)
    rng = __import__("numpy").random.default_rng(int(t * 30))
    for _ in range(9):  # tearing bars
        y = rng.integers(0, H)
        hgt = rng.integers(10, 70)
        c.drawRect(skia.Rect.MakeLTRB(0, y, W, y + hgt), paint("#ff2a3a" if rng.random() > 0.5 else "#0a0c10", 0.5))
    kit.draw_text(c, "JAY", 540, 1420, 70, color="#ff4a3a", weight="Black")
    flat.vignette(c, W, H, 0.6)


def shot_scare_face(c, t):
    """JUMPSCARE 2: 'Look behind you.'  It is already over your shoulder."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#07080e"))
    u = t - B["scare2"]
    pale_grin(c, 560, 760, 2.6 + 0.8 * u, t)
    # your shoulder + headset silhouette in the foreground
    c.drawPath(blob([(-60, H), (40, 1500), (330, 1380), (520, 1560), (560, H)], 0.4), paint("#020306"))
    c.drawCircle(250, 1330, 190, paint("#020306"))
    glow(c, 540, 1900, 700, SCREEN, 0.2)
    flat.vignette(c, W, H, 0.6)


def shot_game_screen(c, t):
    """An original, generic battle-royale HUD (not any real game's art): hills, a storm wall, a squad list."""
    flat.linear_grad(c, (0, 0, W, H), ["#6fb7ff", "#bfe3ff", "#8fd08a"])
    c.drawPath(blob([(0, 1200), (200, 1000), (460, 1120), (760, 960), (W, 1100), (W, H), (0, H)], 0.4), paint("#5fb86a"))
    c.drawPath(blob([(0, 1400), (300, 1260), (700, 1380), (W, 1280), (W, H), (0, H)], 0.4), paint("#4aa25a"))
    for x, y, s in ((180, 1010, 1.0), (820, 980, 1.2), (620, 1110, 0.8)):
        c.drawRect(skia.Rect.MakeLTRB(x - 10 * s, y, x + 10 * s, y + 90 * s), paint("#6a4a2a"))
        c.drawPath(poly_path([(x, y - 130 * s), (x + 70 * s, y + 20 * s), (x - 70 * s, y + 20 * s)]), paint("#2f7a45"))
    sw = 60 + 30 * math.sin(t * 0.8)  # the storm closing in from the right
    for k in range(14):  # soft wall: denser toward the edge
        c.drawRect(skia.Rect.MakeLTRB(W - 300 - sw + k * 26, 0, W, H), paint("#8a4fe0", 0.07))
    cx, cy = 540 + 14 * math.sin(t * 2.2), 860 + 8 * math.sin(t * 3.1)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        c.drawLine(cx + dx * 16, cy + dy * 16, cx + dx * 46, cy + dy * 46, paint("#ffffff", stroke=6))
    c.drawCircle(cx, cy, 5, paint("#ffffff"))
    for k, (name, colr) in enumerate((("YOU", "#d0312d"), ("JAY", "#2fbf6b"), ("MARCUS", "#e08a2f"), ("DEE", "#8f5fe0"))):
        y = 330 + k * 74
        c.drawRoundRect(skia.Rect.MakeLTRB(50, y, 430, y + 60), 12, 12, paint("#000000", 0.45))
        c.drawCircle(84, y + 30, 18, paint(colr))
        kit.draw_text(c, name, 116, y + 42, 32, color="#ffffff", weight="Bold", align="left", max_w=160)
        c.drawRoundRect(skia.Rect.MakeLTRB(280, y + 22, 410, y + 38), 6, 6, paint("#1a1c22"))
        c.drawRoundRect(skia.Rect.MakeLTRB(280, y + 22, 280 + 130 * (0.9 - 0.15 * k), y + 38), 6, 6, paint("#5dff8f"))
    c.drawRoundRect(skia.Rect.MakeLTRB(760, 330, 1030, 400), 14, 14, paint("#000000", 0.45))
    kit.draw_text(c, "12 LEFT", 895, 380, 38, color="#ffffff", weight="Black", max_w=240)
    pop = span(t, start("L02"), start("L02") + 0.25, "back")
    if pop > 0:
        c.drawRoundRect(skia.Rect.MakeLTRB(240, 1180, 840, 1300), 20, 20, paint("#ffd23f", min(1.0, pop)))
        kit.draw_text(c, "SQUAD WIPE +4", 540, 1265, 64, color="#1a1c22", weight="Black", max_w=560)
    flat.vignette(c, W, H, 0.3)


def shot_phone_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#14162a", "#0c0d18"])
    sh = 4 * math.sin(t * 31)  # your hand is shaking
    c.save()
    c.translate(sh, 0)
    c.drawRoundRect(skia.Rect.MakeLTRB(200, 260, 880, 1400), 60, 60, paint("#101216"))
    c.drawRoundRect(skia.Rect.MakeLTRB(230, 290, 850, 1370), 46, 46, paint("#0d1018"))
    c.drawCircle(330, 400, 44, paint("#e08a2f"))
    kit.draw_text(c, "M", 330, 418, 50, color="#ffffff", weight="Black", max_w=70)
    kit.draw_text(c, "Marcus", 400, 418, 46, color="#ffffff", weight="Bold", align="left", max_w=400)
    kit.draw_text(c, "left the call 9 min ago", 270, 520, 30, color="#8a90a0", weight="SemiBold", align="left", max_w=560)
    for k, (txt, t0) in enumerate((("don't answer jay", B["text"]), ("that's not him anymore", word("L09", "That's")))):
        v = span(t, t0, t0 + 0.25, "back")
        if v > 0:
            y = 600 + k * 190
            c.drawRoundRect(skia.Rect.MakeLTRB(270, y, 810, y + 150), 34, 34, paint("#2b3242", min(1.0, v)))
            kit.draw_text(c, txt, 300, y + 92, 44, color="#ffffff", weight="SemiBold", align="left", max_w=480)
    c.restore()
    glow(c, 540, 800, 700, "#cfe6ff", 0.12)
    flat.vignette(c, W, H, 0.5)


def shot_reflect_cu(c, t):
    """Your monitor went dark - now it is a mirror: you, and behind you the bedroom door."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#0b0c12"))
    scr = rrect_path(70, 260, 1010, 1330, 30)
    c.drawPath(rrect_path(40, 230, 1040, 1360, 44), paint("#1a1c24"))
    c.save()
    c.clipPath(scr, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(70, 260, 1010, 1330), paint("#0a0d16"))
    c.drawLine(70, 420, 1010, 420, paint("#5a3a9a", 0.5, stroke=8))  # the LED strip, reflected
    op = span(t, B["door"] - 0.6, B["door"] + 0.2)
    # the door behind you (mirrored: it is on the left in the reflection)
    c.drawRect(skia.Rect.MakeLTRB(150, 380, 400, 1040), paint("#1a1e30"))
    c.drawRect(skia.Rect.MakeLTRB(170, 400, 380, 1040), paint(flat.lerp_col(hexc("#241c18"), hexc("#2c4478"), op)))
    if op > 0.3:
        a = span(t, B["door"], B["door"] + 0.8)
        glow(c, 275, 720, 380, "#5a7ac0", 0.45 * op)
        c.drawPath(ellipse_path(275, 590, 46, 58), paint("#020308", a))
        c.drawPath(blob([(196, 1040), (206, 680), (344, 680), (354, 1040)], 0.35), paint("#020308", a))
        e = span(t, word("L11", "standing"), word("L11", "standing") + 0.3)
        for side in (-1, 1):
            c.drawCircle(275 + side * 17, 586, 4.5, paint("#ffffff", e))
    # your reflection: headset, cap, shoulders - a dark shape with a rim of screen light
    c.drawPath(blob([(330, 1330), (380, 1050), (700, 1050), (760, 1330)], 0.4), paint("#18203a"))
    c.drawCircle(545, 900, 150, paint("#18203a"))
    c.drawPath(ellipse_path(545, 900, 150, 150), paint("#4a64a8", 0.8, stroke=5))
    band = skia.Path()
    band.moveTo(390, 910)
    band.cubicTo(380, 680, 710, 680, 700, 910)
    c.drawPath(band, paint("#2a3050", stroke=22))
    for x in (392, 698):
        c.drawPath(rrect_path(x - 24, 860, x + 24, 960, 20), paint("#2a3050"))
    c.drawLine(120, 300, 420, 1300, paint("#ffffff", 0.04, stroke=120))  # glass sheen
    c.restore()
    c.drawRoundRect(skia.Rect.MakeLTRB(480, 1360, 600, 1440), 8, 8, paint("#1a1c24"))
    flat.vignette(c, W, H, 0.5)


def knock_jolt(t):
    j = 0.0
    for kt in B["knocks"]:
        u = t - kt
        if 0 <= u < 0.2:
            j = max(j, (1 - u / 0.2) * 12)
    return j


def shot_window_cu(c, t):
    """Your window.  Something stands outside it and knocks."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#14162a"))
    j = knock_jolt(t)
    win = skia.Rect.MakeLTRB(190, 300, 890, 1300)
    c.drawRect(win, paint("#0d1830"))
    c.drawCircle(700, 480, 60, paint("#dfe8ff", 0.9))
    glow(c, 700, 480, 300, "#cfdcff", 0.25)
    a = span(t, start("L12") + 0.2, start("L12") + 1.2)
    c.save()
    c.clipRect(win)
    c.drawPath(ellipse_path(520, 760 - j, 120, 150), paint("#04050a", a))
    c.drawPath(blob([(330, 1300), (360, 960), (680, 960), (710, 1300)], 0.4), paint("#04050a", a))
    if t >= B["knocks"][0] - 0.1:  # the hand on the glass, and the smile
        c.drawPath(ellipse_path(720, 900 - j * 2, 46, 60), paint("#04050a"))
        for k in range(4):
            c.drawPath(capsule((690 + k * 20, 870 - j * 2), (686 + k * 22, 800 - j * 2), 16), paint("#04050a"))
        g = span(t, B["knocks"][0], B["knocks"][0] + 0.3)
        for side in (-1, 1):
            c.drawCircle(520 + side * 44, 730 - j, 7, paint("#ffffff", g))
        m = skia.Path()
        m.moveTo(450, 810 - j)
        m.quadTo(520, 870 - j, 590, 810 - j)
        c.drawPath(m, paint("#e8ecf4", g, stroke=7))
    c.restore()
    c.drawLine(540, 300, 540, 1300, paint("#2a3050", stroke=14))
    c.drawRect(win, paint("#2a3050", stroke=22))
    for x0, x1 in ((90, 300), (780, 990)):  # curtains
        c.drawPath(blob([(x0, 240), (x1, 240), (x1 - 30, 1360), (x0 + 30, 1360)], 0.2), paint("#3a2f5c"))
        for k in range(3):
            xx = x0 + 40 + k * 55
            c.drawLine(xx, 260, xx - 8, 1340, paint("#2c2348", stroke=8))
    flat.vignette(c, W, H, 0.55)


def shot_choice_bg(c, t):
    room(c, t)
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", 0.25))
    for (x, y), colr, letter in (((865, 520), "#e2574c", "A"), ((540, 1740), "#3f8fd6", "B")):
        p = 1 + 0.08 * math.sin(t * 6 + x)
        c.drawCircle(x, y, 40 * p, paint(colr))
        c.drawCircle(x, y, 40 * p, paint("#ffffff", stroke=5))
        kit.draw_text(c, letter, x, y + 17, 48, color="#ffffff", weight="Black")
    flat.vignette(c, W, H, 0.6)


def _face_zone():
    hx, hy = YOU.head_pos(YOU_X, FEET, SC)
    r = YOU.HEAD_RX * YOU.s.head_scale * SC
    return ("your face", hx - r * 1.15, hy - r * 1.5, hx + r * 1.15, hy + r * 1.35)


def _cu_zone(t):
    name, l, tp, r, b = _face_zone()
    x, y = YOU.head_pos(YOU_X, FEET, SC)
    f = lambda px, py: (540 + (px - x) * 2.2, 900 + (py - (y + 60)) * 2.2)  # noqa: E731
    (l2, t2), (r2, b2) = f(l, tp), f(r, b)
    return [(name, l2, t2, r2, b2)]


ZONES = {
    "room_wide": lambda t: [_face_zone()],
    "choice_bg": lambda t: [_face_zone()],
    "you_cu": _cu_zone,
    "call_ui": lambda t: [("tiles", 80, 330, 1000, 1190), ("call bar", 300, 1250, 780, 1370)],
    "phone_cu": lambda t: [("messages", 270, 600, 810, 940)],
    "reflect_cu": lambda t: [("monitor", 70, 260, 1010, 1330)],
    "window_cu": lambda t: [("window", 190, 300, 890, 1300)],
    "game_screen": lambda t: [("squad list", 50, 330, 430, 620), ("banner", 240, 1180, 840, 1300)],
    "scare_tile": lambda t: [("face", 240, 470, 840, 1170)],
    "scare_face": lambda t: [("face", 220, 370, 900, 1150)],
}
SHOTS = dict(room_wide=shot_room_wide, you_cu=shot_you_cu, call_ui=shot_call_ui, scare_tile=shot_scare_tile,
             scare_face=shot_scare_face, game_screen=shot_game_screen, phone_cu=shot_phone_cu, reflect_cu=shot_reflect_cu,
             window_cu=shot_window_cu, choice_bg=shot_choice_bg)
