"""VIDEO_012 - ORDER #000, Part 1: 2 AM, mukbangs, a food order - and a delivery guy who arrives far too fast.

YOU act every line (flat.emote).  The mukbang girl lip-syncs her warning; the delivery guy's grin barely moves when he
talks.  Two jumpscares: his face slams into the door camera (scare_cam) and something looks out of the bag (scare_bag).
The apps on screen are generic originals (no real app's UI).
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

YOU = Puppet(CAST["mascot"], "you")
GIRL = Puppet(Style(skin="#f0c2a0", hair="#5a2d3a", hair_style="long", shirt="#f2a2c0", shirt_detail="#ffffff",
                    pants="#3b3f4a", eyes="#4a2e1c", height=0.97), "streamer")
FEET, SC, YOU_X = 1960, 1.15, 540
PHONE = "#9fc8ff"


def emo_at(t):
    import edit_video012 as E
    cur = prev = "calm"
    t_cur = 0.0
    for sid, line, you in E.SCENE_EMO:
        t0 = E._t0(sid, line)
        if t >= t0:
            prev, cur, t_cur = cur, you, t0
    return prev, cur, span(t, t_cur, t_cur + 0.3)


def pose(t):
    p, cu, u = emo_at(t)
    you = emote(emote(dict(eye_open=blink(t, seed=51)), p, t, seed=2), cu, t, amount=u, seed=2)
    you["pupil"] = (0.0, 0.75)  # eyes on the phone in your hands
    if B["knocks"][0] <= t < start("L04"):  # head snaps toward the front door
        you.update(pupil=(0.95, -0.1), turn=0.45)
    if start("L08") - 0.1 <= t < start("L09") or t >= start("L11") - 0.1:  # staring at the bag at the foot of the bed
        you["pupil"] = (0.0, 0.95)
    return you


def creep_face(c, x, y, s, t, talk=0.0, alpha=1.0, cap=True):
    """The delivery guy: skin a shade too grey, eyes that never blink, a smile that is too wide."""
    c.drawPath(ellipse_path(x, y, 120 * s, 140 * s), paint("#c9b8a8", alpha))
    for side in (-1, 1):
        ex = x + side * 48 * s
        c.drawPath(ellipse_path(ex, y - 26 * s, 30 * s, 34 * s), paint("#f4f1ea", alpha))
        c.drawCircle(ex, y - 26 * s, 9 * s, paint("#0a0a0c", alpha))
        c.drawPath(ellipse_path(ex, y - 26 * s, 30 * s, 34 * s), paint("#3a2a24", alpha, stroke=3 * s))
    m = skia.Path()
    op = (10 + 22 * talk) * s
    m.moveTo(x - 86 * s, y + 44 * s)
    m.quadTo(x, y + 80 * s, x + 86 * s, y + 44 * s)
    m.quadTo(x, y + 96 * s + op, x - 86 * s, y + 44 * s)
    m.close()
    c.drawPath(m, paint("#1a0a0c", alpha))
    c.save()
    c.clipPath(m, doAntiAlias=True)
    for k in range(-5, 6):
        c.drawRoundRect(skia.Rect.MakeLTRB(x + k * 17 * s - 7.5 * s, y + 40 * s, x + k * 17 * s + 7.5 * s, y + 78 * s), 3, 3,
                        paint("#f0eee4", alpha))
    c.restore()
    if cap:
        c.drawPath(blob([(x - 128 * s, y - 70 * s), (x - 100 * s, y - 170 * s), (x + 100 * s, y - 170 * s), (x + 128 * s, y - 70 * s)], 0.4),
                   paint("#2f8f4e", alpha))
        c.drawPath(rrect_path(x - 150 * s, y - 86 * s, x + 150 * s, y - 60 * s, 12 * s), paint("#236e3c", alpha))
        kit.draw_text(c, "QB", x, y - 104 * s, 44 * s, color="#ffffff", weight="Black", max_w=200 * s, alpha=alpha)


# ============================================================================ your bedroom (you, sitting up in bed)

def bedroom(c, t, bag=False, people=True):
    flat.linear_grad(c, (0, 0, W, H), ["#12142a", "#1a1c36"])
    c.drawRect(skia.Rect.MakeLTRB(120, 380, 400, 780), paint("#0d1830"))  # window, blinds half down
    for k in range(5):
        c.drawLine(120, 400 + k * 44, 400, 400 + k * 44, paint("#2a3050", stroke=14))
    c.drawRect(skia.Rect.MakeLTRB(120, 380, 400, 780), paint("#2a3050", stroke=12))
    c.drawRect(skia.Rect.MakeLTRB(700, 300, 960, 1100), paint("#2c2420"))  # bedroom door
    c.drawCircle(730, 720, 10, paint("#b9953f"))
    c.drawPath(rrect_path(140, 880, 940, 1500, 60), paint("#3a2f5c"))  # headboard
    c.drawPath(rrect_path(210, 1010, 870, 1440, 110), paint("#cfcbe4"))  # pillow
    if people:
        L = Light(dir=(0.0, 0.9), shadow_px=14, rim=PHONE, rim_alpha=0.9, rim_px=6)
        p = pose(t)
        YOU.draw(c, YOU_X, FEET, SC, p, light=L, shadow=False)
    # blanket + the phone held up in front of you (we see its back, glowing edges)
    c.drawPath(blob([(0, 1560), (300, 1470), (780, 1470), (W, 1560), (W, H), (0, H)], 0.3), paint("#4a3f7a"))
    c.drawPath(blob([(0, 1700), (500, 1640), (W, 1720), (W, H), (0, H)], 0.3), paint("#3f356a"))
    if people:  # the phone in your hands (its back to us), lighting your face
        ph = 4 * math.sin(t * 1.3)
        glow(c, 540, 1400 + ph, 520, PHONE, 0.35)
        c.drawRoundRect(skia.Rect.MakeLTRB(470, 1330 + ph, 610, 1470 + ph), 18, 18, paint("#101216"))
        c.drawCircle(500, 1356 + ph, 9, paint("#2a2e3a"))
        for side in (-1, 1):
            c.drawPath(ellipse_path(540 + side * 78, 1440 + ph, 34, 44), paint(YOU.s.skin))
    if bag:
        paper_bag(c, 540, 1760, 1.0, t)
    flat.vignette(c, W, H, 0.55)


def paper_bag(c, x, y, s, t, opening=0.0):
    """The order: a paper bag with the app's logo.  Receipt: ORDER #000."""
    wob = 0.0
    if t >= B["move"]:
        wob = 5 * math.sin((t - B["move"]) * 26) * min(1.0, (t - B["move"]) * 2)
    c.save()
    c.rotate(wob, x, y)
    c.drawPath(poly_path([(x - 150 * s, y), (x - 170 * s, y - 330 * s), (x + 170 * s, y - 330 * s), (x + 150 * s, y)]), paint("#c9a36a"))
    c.drawPath(poly_path([(x + 150 * s, y), (x + 170 * s, y - 330 * s), (x + 120 * s, y - 330 * s), (x + 100 * s, y)]), paint("#b08a54"))
    c.drawPath(poly_path([(x - 170 * s, y - 330 * s), (x + 170 * s, y - 330 * s), (x + 160 * s, y - 380 * s), (x - 160 * s, y - 380 * s)]),
               paint("#b9935c"))  # folded top
    c.drawCircle(x - 20 * s, y - 180 * s, 62 * s, paint("#2f8f4e"))
    kit.draw_text(c, "QB", x - 20 * s, y - 158 * s, 60 * s, color="#ffffff", weight="Black", max_w=120 * s)
    c.drawRect(skia.Rect.MakeLTRB(x + 30 * s, y - 370 * s, x + 150 * s, y - 250 * s), paint("#f4f1ea"))  # receipt
    kit.draw_text(c, "ORDER", x + 90 * s, y - 330 * s, 24 * s, color="#1a1c22", weight="Black", max_w=110 * s)
    kit.draw_text(c, "#000", x + 90 * s, y - 286 * s, 38 * s, color="#c0392b", weight="Black", max_w=110 * s)
    c.restore()


def shot_bed_you(c, t):
    bedroom(c, t)


def shot_bed_bag(c, t):
    """The foot of your bed: the bag is already here."""
    flat.linear_grad(c, (0, 0, W, H), ["#12142a", "#1a1c36"])
    c.drawRect(skia.Rect.MakeLTRB(640, 200, 940, 1000), paint("#2c2420"))  # your door - locked
    c.drawCircle(680, 640, 12, paint("#b9953f"))
    c.drawRoundRect(skia.Rect.MakeLTRB(662, 540, 698, 600), 8, 8, paint("#8a8f98"))
    c.drawPath(blob([(0, 1100), (300, 1000), (800, 1000), (W, 1100), (W, H), (0, H)], 0.3), paint("#4a3f7a"))
    c.drawPath(blob([(0, 1500), (500, 1420), (W, 1520), (W, H), (0, H)], 0.3), paint("#3f356a"))
    glow(c, 540, 900, 600, PHONE, 0.2)
    c.drawPath(ellipse_path(540, 1190, 230, 40), paint("#000000", 0.35))
    paper_bag(c, 540, 1180, 1.25, t)
    flat.vignette(c, W, H, 0.55)


def shot_scare_bag(c, t):
    """JUMPSCARE 2: the top of the bag tears open - fingers on the rim, and his face looking out of the dark."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#0a0810"))
    u = t - B["scare2"]
    c.drawPath(poly_path([(40, H), (0, 700), (W, 700), (W - 40, H)]), paint("#c9a36a"))
    hole = blob([(120, 760), (300, 420 - 60 * u), (780, 420 - 60 * u), (960, 760), (860, 1250), (220, 1250)], 0.4)
    c.drawPath(hole, paint("#050308"))
    c.save()
    c.clipPath(hole, doAntiAlias=True)
    creep_face(c, 540 + 3 * math.sin(t * 60), 900 - 80 * u, 2.3 + 0.5 * u, t, cap=False)
    c.restore()
    for side in (-1, 1):  # fingers gripping the torn paper
        for k in range(4):
            fx = 540 + side * (300 + k * 46)
            c.drawPath(capsule((fx, 1330), (fx - side * 10, 1200 - (k % 2) * 16), 40), paint("#c9b8a8"))
    kit.draw_text(c, "ORDER #000", 540, 1560, 80, color="#c0392b", weight="Black")
    flat.vignette(c, W, H, 0.6)


# ============================================================================ phone screens

def phone_frame(c, colr="#0d1018"):
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#08090e"))
    c.drawRoundRect(skia.Rect.MakeLTRB(50, 150, 1030, 1420), 60, 60, paint("#15171e"))
    scr = rrect_path(76, 176, 1004, 1394, 40)
    c.drawPath(scr, paint(colr))
    return scr


def shot_phone_feed(c, t):
    """A generic vertical-video app: a mukbang.  Later she stops eating, looks at YOU, and talks."""
    scr = phone_frame(c)
    stare = t >= B["stare"] and t >= B["story"] + 5
    c.save()
    c.clipPath(scr, doAntiAlias=True)
    flat.linear_grad(c, (76, 176, 1004, 1394), ["#ffd9e6", "#ffeedd"] if not stare else ["#3a2a34", "#241a22"])
    for k in range(3):  # fairy lights behind her
        c.drawCircle(220 + k * 300, 300, 16, paint("#ffd23f" if not stare else "#5a4a20"))
    p = dict(eye_open=blink(t, seed=61) if not stare else 1.0)
    if stare:
        p = emote(p, "scared", t, seed=6)
        p.update(pupil=(0.0, 0.0), sweat=0.0, mouth="flat")
        if TIMING:
            p = TIMING.lip(p, t, "streamer")
    else:
        chew = abs(math.sin(t * 9))
        p = emote(p, "happy", t, seed=6)
        p.update(mouth="o", talk=0.25 + 0.5 * chew, pupil=(0.0, 0.6), head_tilt=3 * math.sin(t * 4.5))
    L = Light(dir=(0.0, -0.9), shadow_px=12, rim="#ffffff", rim_alpha=0.5, rim_px=4)
    GIRL.draw(c, 540, 1470, 1.25, p, light=L, shadow=False)
    # table + a mountain of noodles
    c.drawRect(skia.Rect.MakeLTRB(76, 1130, 1004, 1394), paint("#8a5a3a" if not stare else "#3a2a22"))
    c.drawPath(ellipse_path(540, 1180, 250, 70), paint("#f4f1ea"))
    c.drawPath(blob([(330, 1170), (400, 1020), (540, 980), (690, 1030), (750, 1170)], 0.5), paint("#e8a23f" if not stare else "#7a5a2a"))
    for k in range(7):
        c.drawPath(ellipse_path(400 + k * 46, 1110 - 30 * math.sin(k * 1.3), 40, 16), paint("#f6c46a" if not stare else "#8a6a3a", stroke=7))
    c.drawPath(ellipse_path(540, 1200, 250, 60), paint("#d0312d" if not stare else "#5a1a1a", stroke=18))
    if not stare:  # chopsticks carrying noodles to her mouth
        yy = 940 + 60 * abs(math.sin(t * 4.5))
        c.drawLine(760, 1150, 600, yy, paint("#3a2a1a", stroke=9))
        c.drawLine(790, 1140, 620, yy - 10, paint("#3a2a1a", stroke=9))
        c.drawPath(capsule((606, yy), (590, yy + 90), 20), paint("#f6c46a"))
    # app chrome (original design)
    for k in range(3):
        c.drawCircle(930, 760 + k * 130, 40, paint("#000000", 0.35))
    c.drawPath(blob([(930, 782), (906, 752), (918, 738), (930, 750), (942, 738), (954, 752)], 0.3), paint("#ff4a6a" if not stare else "#6a2a3a"))
    c.drawRoundRect(skia.Rect.MakeLTRB(916, 874, 944, 902), 6, 6, paint("#ffffff", 0.9))
    c.drawPath(poly_path([(916, 1020), (946, 1004), (946, 1036)]), paint("#ffffff", 0.9))
    kit.draw_text(c, "@noodle.queen", 110, 1290, 40, color="#ffffff", weight="Bold", align="left", max_w=500, stroke=6)
    live = "LIVE · 1 watching" if stare else "MUKBANG · 48 spicy noodles"
    kit.draw_text(c, live, 110, 1344, 34, color="#ff8a8a" if stare else "#ffffff", weight="SemiBold", align="left", max_w=640, stroke=6)
    c.restore()
    flat.vignette(c, W, H, 0.4)


def shot_app_order(c, t):
    """A generic food-delivery app ('QuickBite').  The driver is never where he should be."""
    scr = phone_frame(c, "#f4f1ea")
    hook = t < B["story"]
    late = t >= start("L06") - 0.1 and not hook
    c.save()
    c.clipPath(scr, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(76, 176, 1004, 330), paint("#2f8f4e"))
    kit.draw_text(c, "QuickBite", 540, 280, 64, color="#ffffff", weight="Black", max_w=600)
    # map
    c.drawRect(skia.Rect.MakeLTRB(76, 330, 1004, 880), paint("#dfe8d8"))
    for k in range(5):
        c.drawLine(76, 400 + k * 110, 1004, 380 + k * 110, paint("#ffffff", stroke=22))
        c.drawLine(180 + k * 190, 330, 160 + k * 190, 880, paint("#ffffff", stroke=22))
    hx, hy, rx, ry = 800, 760, 190, 440  # your home / the restaurant
    c.drawCircle(hx, hy, 30, paint("#3f8fd6"))
    kit.draw_text(c, "YOU", hx, hy + 76, 30, color="#1a1c22", weight="Black", max_w=120)
    c.drawCircle(rx, ry, 30, paint("#e08a2f"))
    kit.draw_text(c, "RESTAURANT", rx + 24, ry - 44, 28, color="#1a1c22", weight="Black", max_w=260)
    for k in range(9):
        u = k / 9
        c.drawCircle(lerp(rx, hx, u), lerp(ry, hy, u), 6, paint("#8a8f98"))
    if hook or (not late and t >= B["order"] + 0.5):  # the driver pin is ALREADY at your house
        pulse = 1 + 0.3 * abs(math.sin(t * 6))
        c.drawCircle(hx - 40, hy - 30, 24 * pulse, paint("#d0312d", 0.4))
        c.drawCircle(hx - 40, hy - 30, 18, paint("#d0312d"))
    if late:  # the real Sam: still at the restaurant
        c.drawCircle(rx + 30, ry + 26, 18, paint("#2f8f4e"))
        c.drawCircle(hx - 40, hy - 30, 18, paint("#d0312d"))
        kit.draw_text(c, "?", hx - 40, hy - 18, 34, color="#ffffff", weight="Black", max_w=40)
    # status card
    c.drawRoundRect(skia.Rect.MakeLTRB(110, 920, 970, 1340), 36, 36, paint("#ffffff"))
    if hook:
        rows = [("Your driver is", "#5a5f6c", 40), ("1 MIN AWAY", "#d0312d", 84), ("Restaurant: 40 min from you", "#1a1c22", 40)]
    elif late:
        rows = [("Sam is still at the restaurant", "#1a1c22", 44), ("PICKING UP YOUR ORDER", "#2f8f4e", 54), ("Arrives in 41 min", "#5a5f6c", 40)]
    elif t >= B["order"]:
        v = span(t, B["order"], B["order"] + 0.25, "back")
        rows = [("ORDER PLACED", "#2f8f4e", 76 * min(1.0, v)), ("Order #000 · spicy noodles", "#1a1c22", 40),
                ("Your driver is arriving now", "#d0312d", 44)]
    else:
        rows = [("Spicy noodles ×1", "#1a1c22", 52), ("Delivery: 40-50 min", "#5a5f6c", 40), ("TAP TO ORDER", "#2f8f4e", 64)]
    for k, (txt, colr, size) in enumerate(rows):
        if size > 4:
            kit.draw_text(c, txt, 540, 1030 + k * 110, size, color=colr, weight="Black" if size > 50 else "Bold", max_w=800)
    c.restore()
    if not hook and not late and t < B["order"]:
        tap = span(t, B["order"] - 0.5, B["order"])
        c.drawCircle(700, 1300 + 60 * (1 - tap), 46, paint("#000000", 0.25))
    flat.vignette(c, W, H, 0.4)


# ============================================================================ the door camera

def knock_jolt(t):
    j = 0.0
    for kt in B["knocks"]:
        u = t - kt
        if 0 <= u < 0.2:
            j = max(j, (1 - u / 0.2) * 10)
    return j


def shot_doorcam(c, t):
    """Your door camera (wide lens, night vision): the hallway and whoever is standing in it."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#05070a"))
    lens = rrect_path(40, 170, 1040, 1400, 90)
    c.save()
    c.clipPath(lens, doAntiAlias=True)
    flat.linear_grad(c, (40, 170, 1040, 1400), ["#2a3a34", "#16201c"])
    c.drawPath(poly_path([(40, 1400), (330, 980), (750, 980), (1040, 1400)]), paint("#22302a"))  # hallway floor
    c.drawRect(skia.Rect.MakeLTRB(330, 420, 750, 980), paint("#1a2620"))  # far wall
    c.drawRect(skia.Rect.MakeLTRB(470, 560, 610, 980), paint("#101a16"))  # neighbour's door
    hook = t < B["story"]
    here = hook or (start("L04") - 0.2 <= t < B["gone"])
    if here:
        lean = 0.0 if hook else span(t, start("L05"), end("L05"), "linear") * 0.25  # he leans in while he talks
        s = 1.0 + lean
        x, y = 540, 760 + 40 * lean
        talk = max(TIMING.mouth(t, "sam") if TIMING else 0.0, 0.0)
        c.drawPath(blob([(x - 210 * s, 1420), (x - 190 * s, y + 170 * s), (x - 90 * s, y + 110 * s), (x + 90 * s, y + 110 * s),
                         (x + 190 * s, y + 170 * s), (x + 210 * s, 1420)], 0.35), paint("#2f8f4e"))  # jacket
        c.drawPath(poly_path([(x - 40 * s, y + 120 * s), (x + 40 * s, y + 120 * s), (x, y + 260 * s)]), paint("#e9e6dc"))
        creep_face(c, x, y, s, t, talk=talk)
        bx, by = x + 10, y + 520 * s  # the bag held up to the lens
        c.drawPath(poly_path([(bx - 110, by + 200), (bx - 124, by), (bx + 124, by), (bx + 110, by + 200)]), paint("#c9a36a"))
        c.drawCircle(bx, by + 96, 44, paint("#2f8f4e"))
        kit.draw_text(c, "QB", bx, by + 112, 42, color="#ffffff", weight="Black", max_w=90)
    elif t >= B["gone"]:  # nobody.  (the bag is not on the mat either)
        g = math.sin(t * 50) > 0.7
        if g:
            for k in range(5):
                c.drawRect(skia.Rect.MakeLTRB(40, 300 + k * 210, 1040, 330 + k * 210), paint("#cfe8dc", 0.12))
    c.drawRect(skia.Rect.MakeLTRB(40, 170, 1040, 1400), paint("#7dffb0", 0.06))  # night-vision tint
    for k in range(0, 1230, 6):
        c.drawLine(40, 170 + k, 1040, 170 + k, paint("#000000", 0.10, stroke=2))
    c.restore()
    c.drawPath(lens, paint("#000000", 0.5, stroke=40, blur=30))
    if math.sin(t * 5) > 0:
        c.drawCircle(120, 250, 14, paint("#ff4a3a"))
    kit.draw_text(c, "REC", 150, 264, 36, color="#ffffff", weight="Bold", align="left", max_w=120)
    kit.draw_text(c, "FRONT DOOR · 02:07 AM", 990, 264, 34, color="#ffffff", weight="Bold", align="right", max_w=520)
    j = knock_jolt(t)
    if j:
        c.drawRect(skia.Rect.MakeWH(W, H), paint("#ffffff", 0.03 * j))
    flat.vignette(c, W, H, 0.5)


def shot_scare_cam(c, t):
    """JUMPSCARE 1: he was looking at the camera the whole time.  His face fills the lens."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#0a1410"))
    u = t - B["scare1"]
    creep_face(c, 540 + 4 * math.sin(t * 70), 800, 3.0 + 0.9 * u, t, talk=1.0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#7dffb0", 0.08))
    rng = __import__("numpy").random.default_rng(int(t * 30))
    for _ in range(8):
        y = int(rng.integers(0, H))
        c.drawRect(skia.Rect.MakeLTRB(0, y, W, y + int(rng.integers(8, 60))), paint("#e8fff2" if rng.random() > 0.5 else "#000000", 0.35))
    flat.vignette(c, W, H, 0.6)


def shot_choice_bg(c, t):
    c.save()
    c.translate(0, 250)  # the bag sits below the choice pills
    shot_bed_bag(c, t)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", 0.35))
    flat.vignette(c, W, H, 0.5)


def _face_zone():
    hx, hy = YOU.head_pos(YOU_X, FEET, SC)
    r = YOU.HEAD_RX * YOU.s.head_scale * SC
    return ("your face", hx - r * 1.15, hy - r * 1.5, hx + r * 1.15, hy + r * 1.35)


ZONES = {
    "bed_you": lambda t: [_face_zone()],
    "bed_bag": lambda t: [("bag", 330, 700, 760, 1190)],
    "choice_bg": lambda t: [("bag", 330, 960, 760, 1430)],
    "phone_feed": lambda t: [("her face", 380, 430, 700, 800), ("noodles", 290, 980, 790, 1260)],
    "app_order": lambda t: [("map", 76, 330, 1004, 880), ("status", 110, 920, 970, 1340)],
    "doorcam": lambda t: [("door camera", 330, 560, 750, 1000)],
    "scare_cam": lambda t: [("face", 180, 380, 900, 1220)],
    "scare_bag": lambda t: [("face", 220, 420, 860, 1250)],
}
SHOTS = dict(bed_you=shot_bed_you, bed_bag=shot_bed_bag, scare_bag=shot_scare_bag, phone_feed=shot_phone_feed,
             app_order=shot_app_order, doorcam=shot_doorcam, scare_cam=shot_scare_cam, choice_bg=shot_choice_bg)
