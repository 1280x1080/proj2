"""VIDEO_005 - OPEN 24/7, Part 1: 2D shots (Skia), native 1080x1920, t = absolute video time.

Store at 3 AM: cold fluorescent inside, black rain outside.  After the lights die: only the monitor's
blue glow and the warm line under the back-room door.  The barefoot woman is wet hair + a too-wide smile;
whatever is behind you is never shown.
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
from flat import CAST, Light, Puppet, Style, blob, capsule, cel, ellipse_path, glow, hexc, paint, poly_path, rrect_path, shade  # noqa: E402
from kit import H, W, blink, lerp, span, wiggle  # noqa: E402

M = CAST["mascot"]
CLERK = Puppet(Style(skin=M.skin, hair=M.hair, hair_style="short", shirt="#2a7a5e", shirt_detail="#f2efe6", pants="#3b5b86",
                     shoes=M.shoes, eyes=M.eyes, height=M.height, width=M.width, head_scale=M.head_scale, cap=M.cap,
                     cap_backwards=True), "clerk")
JAN = Puppet(Style(skin="#c9a184", hair="#b8b4ad", hair_style="short", shirt="#34405a", shirt_detail="#2a3348", pants="#34405a",
                   shoes="#2a2420", eyes="#3a2c22", height=0.95, width=1.05), "janitor")
SKIN = M.skin
FLUO, MONI, WARM, RED_C = "#e8f6ee", "#8fc4ff", "#ffc477", "#ff3b2f"
PALE = "#c9d3d0"

CHOICE_TARGETS = {  # pill anchor (px) -> target (px); pills are OVERLAYS in the EDL at the same anchors
    1: ((0.66 * W, 0.72 * H - 40), (850, 1150)),
    2: ((0.40 * W, 0.255 * H + 40), (470, 640)),
    3: ((0.30 * W, 0.46 * H + 40), (195, 900)),
    4: ((0.70 * W, 0.34 * H + 40), (915, 730)),
}


def dark(t):
    return t >= B["lights_die"]


def grade(c, t, amount=1.0):
    full = skia.Rect.MakeWH(W, H)
    if dark(t):
        c.drawRect(full, paint("#0a1424", 0.55 * amount, blend=skia.BlendMode.kMultiply))
    else:
        c.drawRect(full, paint("#cfe8dc", 0.12 * amount, blend=skia.BlendMode.kMultiply))
    flat.vignette(c, W, H, 0.45 if not dark(t) else 0.6)


def rain(c, t, x0=0, y0=0, x1=W, y1=H, n=70, alpha=0.35, seed=0):
    for i in range(n):
        x = x0 + ((i * 137 + seed * 31) % 1000) / 1000 * (x1 - x0)
        y = y0 + ((t * (900 + (i % 5) * 120) + i * 211) % (y1 - y0 + 200)) - 100
        c.drawLine(x, y, x - 8, y + 46, paint("#b8c8e0", alpha, stroke=2.5))


def light_clerk(t):
    if dark(t):
        return Light(dir=(0.8, 0.5), shadow_px=24, rim=MONI, rim_alpha=0.9, rim_px=7)
    return Light(dir=(-0.2, -1.0), shadow_px=14, rim=FLUO, rim_alpha=0.5, rim_px=4)


# ============================================================================ poses

def clerk_pose(t):
    P = dict(breathe=t, eye_open=blink(t, seed=41), lid=0.35, mouth="flat", pupil=(0.0, 0.3), brow=(0.0, 0.3), turn=0.05,
             arm_l=(10, 30), arm_r=(10, 30))
    if t < start("S03"):  # reading the sticky note
        P.update(pupil=(-0.3, 0.8), brow=(0.2, 0.5), lid=0.3)
    if t >= start("S04"):
        P.update(lid=0.0, brow=(0.5, 0.4), pupil=(0.7, 0.0))
    if t >= start("S05"):  # slowly turn to the door (screen right)
        u = span(t, start("S05"), start("S05") + 1.2)
        P.update(turn=lerp(0.05, 0.6, u), pupil=(lerp(0.3, 0.9, u), 0.0))
    if t >= start("S10"):
        P.update(turn=-0.4, pupil=(-0.9, 0.0), brow=(0.8, 0.6), mouth="o")
    if t >= start("S12"):
        P.update(turn=-0.2, pupil=(-0.5, -0.1), mouth="flat", brow=(0.4, 0.6))
    if t >= B["customer"]:
        P.update(turn=0.0, pupil=(0.0, 0.0), brow=(0.7, 0.8), mouth="flat", lid=0.0)
    if t >= B["ring333"]:
        P.update(turn=0.4, pupil=(0.8, -0.2), brow=(0.9, 0.9), mouth="o")
    if t >= B["lights_die"]:
        P.update(turn=0.1, pupil=(0.3, 0.2), brow=(1.0, 0.9), mouth="o", lid=0.0, eye_open=1.0)
    if t >= B["touch"]:
        P.update(pupil=(-0.4, 0.0), brow=(1.0, 1.0), mouth="o", talk=0.35)
    return P


def jan_pose(t):
    talk = TIMING.mouth(t, "janitor") if TIMING else 0.0
    P = dict(breathe=t, eye_open=blink(t, seed=51), lid=0.5, mouth="flat", talk=talk, pupil=(0.0, 0.1), brow=(-0.1, 0.4),
             turn=0.1, arm_l=(12, 20), arm_r=(12, 20))
    if start("S15") <= t < start("S16"):  # glance at the monitor, then away fast
        u = span(t, start("S15") + 0.3, start("S15") + 0.6) * (1 - span(t, start("S15") + 1.4, start("S15") + 1.55))
        P.update(pupil=(lerp(0.0, 0.95, u), 0.2), turn=lerp(0.1, 0.4, u), brow=(0.2, 0.7))
    return P


# ============================================================================ the counter set (customer side)

def door_open_amount(t):
    if t < start("S10"):
        return 0.0
    if t < B["lights_die"]:
        return span(t, start("S10") + 0.2, start("S10") + 1.6)
    return 0.0


def name_tag(c, x, y, s, scratched=False, text="ALEX"):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 34 * s, y - 13 * s, 68 * s, 26 * s), 4 * s, 4 * s, paint("#f2efe6"))
    if scratched:
        for k in range(5):
            c.drawLine(x - 30 * s + k * 12 * s, y - 10 * s, x - 20 * s + k * 12 * s, y + 10 * s, paint("#5b5b5b", stroke=3 * s))
    else:
        f = kit.font(16 * s, "Black")
        c.drawString(text, x - f.measureText(text) / 2, y + 6 * s, f, paint("#1d4f3e"))


def store_back(c, t, show_clerk=True, clerk_scale=0.95, phone_shake=0.0, behind=False):
    d = dark(t)
    flat.linear_grad(c, (0, 0, W, H), ["#d9ddd2", "#b9bfb3"] if not d else ["#0b0f17", "#06080c"])
    if not d:  # ceiling lights
        for k in range(3):
            c.drawRoundRect(skia.Rect.MakeLTRB(80 + k * 340, 120, 340 + k * 340, 150), 10, 10, paint(FLUO))
            glow(c, 210 + k * 340, 140, 300, FLUO, 0.15)
    # back-room door (left) with EMPLOYEES ONLY
    dr = skia.Rect.MakeLTRB(60, 420, 330, 1250)
    o = door_open_amount(t)
    c.drawRect(skia.Rect.MakeLTRB(dr.left() - 16, dr.top() - 16, dr.right() + 16, dr.bottom()), paint("#7a7f78" if not d else "#151820"))
    if o > 0:
        c.drawRect(dr, paint(WARM))
        glow(c, (dr.left() + dr.right()) / 2, 900, 420, WARM, 0.35 * o)
    c.drawRect(skia.Rect.MakeLTRB(dr.left(), dr.top(), dr.right() - (dr.width() - 30) * o, dr.bottom()),
               paint("#5a636b" if not d else "#10141b"))
    if o < 0.5:
        c.drawRoundRect(skia.Rect.MakeLTRB(110, 560, 280, 610), 6, 6, paint("#c8463c" if not d else "#2a0f0d"))
        kit.draw_text(c, "EMPLOYEES ONLY", 195, 593, 20, color="#ffffff", weight="Black", max_w=160, alpha=0.9 if not d else 0.2)
    if d:  # the only light left: a warm line under the back-room door
        c.drawRect(skia.Rect.MakeLTRB(dr.left() + 4, dr.bottom() - 8, dr.right() - 4, dr.bottom()), paint(WARM))
        glow(c, 195, 1255, 260, WARM, 0.35)
    # cigarette / snack rack
    rk = skia.Rect.MakeLTRB(380, 380, 770, 1000)
    c.drawRect(rk, paint("#3a3f46" if not d else "#0d1016"))
    cols = ["#e2574c", "#3f8fd6", "#f2b134", "#55a868", "#ffffff", "#8e5ea2"]
    for r in range(5):
        for k in range(7):
            col = cols[(r * 3 + k) % len(cols)]
            c.drawRect(skia.Rect.MakeXYWH(395 + k * 53, 400 + r * 118, 44, 96), paint(col if not d else "#141820"))
    # wall phone (right)
    sh = wiggle(t, 60, 6, 3) * phone_shake
    c.save()
    c.translate(sh, 0)
    c.drawRoundRect(skia.Rect.MakeLTRB(850, 600, 980, 860), 18, 18, paint("#d8cfb6" if not d else "#1b1a17"))
    c.drawRoundRect(skia.Rect.MakeLTRB(862, 610, 968, 700), 30, 30, paint("#c7bc9e" if not d else "#141310"))
    for k in range(9):
        c.drawCircle(885 + (k % 3) * 30, 735 + (k // 3) * 32, 9, paint("#8f8670" if not d else "#0e0d0b"))
    c.restore()
    c.drawPath(blob([(915, 860), (900, 930), (930, 990), (905, 1050)], close=False), paint("#4a4436", stroke=6))
    # clerk behind the counter
    if show_clerk:
        P = clerk_pose(t)
        CLERK.draw(c, 540, 1960, clerk_scale * 1.6, P, light=light_clerk(t), shadow=False)
        hx, hy = CLERK.head_pos(540, 1960, clerk_scale * 1.6, P)
        name_tag(c, 470, hy + 330 * clerk_scale, 1.6 * clerk_scale)
    if behind and d:  # something darker than the dark, right behind your head
        c.drawPath(ellipse_path(430, 640, 150, 210), paint("#000000", 0.55, blur=40))
    # counter (front)
    c.drawRect(skia.Rect.MakeLTRB(0, 1250, W, H), paint("#6b7b74" if not d else "#0c0f13"))
    c.drawRect(skia.Rect.MakeLTRB(0, 1240, W, 1290), paint("#9aa8a1" if not d else "#141a20"))
    for k in range(5):
        c.drawLine(k * 230, 1300, k * 230, H, paint("#000000", 0.12, stroke=4))
    # register (left) + monitor (right, back to us)
    c.drawRoundRect(skia.Rect.MakeLTRB(130, 1080, 420, 1250), 14, 14, paint("#2b2f35" if not d else "#07080a"))
    c.drawRoundRect(skia.Rect.MakeLTRB(170, 1000, 380, 1090), 8, 8, paint("#1b1f24" if not d else "#060708"))
    c.drawRoundRect(skia.Rect.MakeLTRB(710, 1020, 990, 1250), 30, 30, paint("#3a3c40" if not d else "#0b0c0e"))
    if d:
        glow(c, 760, 1060, 520, MONI, 0.45 + 0.05 * math.sin(t * 13))


def shot_counter_wide(c, t):
    store_back(c, t)
    grade(c, t)


def shot_clerk_cu(c, t):
    c.save()
    c.translate(540, 760)
    c.scale(1.7, 1.7)
    c.translate(-540, -760)
    store_back(c, t)
    c.restore()
    # sticky note in the foreground
    c.save()
    c.rotate(-6, 300, 1500)
    c.drawRect(skia.Rect.MakeLTRB(120, 1340, 520, 1700), paint("#f7e36b"))
    c.drawRect(skia.Rect.MakeLTRB(120, 1340, 520, 1380), paint("#e8cf4e"))
    f = kit.font(64, "Bold")
    f.setSkewX(-0.2)
    c.drawString("Night pay", 160, 1480, f, paint("#2a2a35"))
    c.drawString("x3", 160, 1580, f, paint("#c0392b"))
    c.restore()
    grade(c, t)


# ============================================================================ outside / glass / door

def shot_store_ext(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#05070d", "#0d1220"])
    c.drawRect(skia.Rect.MakeLTRB(0, 1240, W, H), paint("#0a0d14"))  # road
    for k in range(6):
        c.drawRect(skia.Rect.MakeLTRB(80 + k * 190, 1560, 180 + k * 190, 1580), paint("#d8c27a", 0.4))
    # store box
    c.drawRect(skia.Rect.MakeLTRB(170, 760, 910, 1250), paint("#262a33"))
    c.drawRect(skia.Rect.MakeLTRB(150, 720, 930, 780), paint("#1a1d24"))
    win = skia.Rect.MakeLTRB(220, 860, 860, 1220)
    c.drawRect(win, paint(FLUO))
    for k in range(4):
        c.drawRect(skia.Rect.MakeLTRB(250 + k * 150, 940, 340 + k * 150, 1210), paint("#9fb3a8"))
    c.drawLine(540, 860, 540, 1220, paint("#262a33", stroke=10))
    glow(c, 540, 1040, 700, FLUO, 0.25)
    # neon sign OPEN 24/7 (buzzing)
    on = 0.7 + 0.3 * kit.flicker(t, 1.0, 0.5, 3, rate=12)
    kit.draw_text(c, "OPEN 24/7", 540, 760, 76, color="#ff4a3a", weight="Black", alpha=on)
    glow(c, 540, 730, 260, "#ff4a3a", 0.35 * on)
    # reflections on the wet road
    c.drawRect(skia.Rect.MakeLTRB(220, 1260, 860, 1500), paint(FLUO, 0.10))
    c.drawRect(skia.Rect.MakeLTRB(380, 1260, 700, 1330), paint("#ff4a3a", 0.12 * on))
    # streetlight
    c.drawLine(990, 1240, 990, 520, paint("#1c1f26", stroke=14))
    lit = kit.flicker(t, 1.0, 0.9, 9, rate=6) > 0.55
    if lit:
        flat.light_cone(c, (950, 540), (760, 1250), (1180, 1250), "#ffd79a", 0.25)
    rain(c, t, n=110, alpha=0.4)
    grade(c, t, 0.5)


def shot_glass_pov(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#060910", "#0e1320"])
    c.drawRect(skia.Rect.MakeLTRB(0, 1180, W, H), paint("#0a0d14"))
    c.drawLine(0, 1180, W, 1150, paint("#d8c27a", 0.3, stroke=6))
    lit = kit.flicker(t, 1.0, 0.6, 4, rate=7) > 0.5
    c.drawLine(700, 1180, 700, 420, paint("#3a3f48", stroke=14))
    c.drawLine(700, 430, 640, 430, paint("#3a3f48", stroke=12))
    if lit:
        flat.light_cone(c, (640, 440), (430, 1180), (900, 1180), "#ffd79a", 0.45)
        glow(c, 640, 440, 160, "#ffd79a", 0.8)
        c.drawOval(skia.Rect.MakeLTRB(430, 1160, 900, 1210), paint("#ffd79a", 0.25))
    # glass + drops
    for i in range(40):
        x = (i * 97) % W
        y = (i * 211 + t * 60 * (1 + i % 3)) % H
        c.drawOval(skia.Rect.MakeLTRB(x - 5, y - 8, x + 5, y + 8), paint("#cfe0f0", 0.3))
    rain(c, t, n=50, alpha=0.18, seed=3)
    for x in (0, 1040):
        c.drawRect(skia.Rect.MakeLTRB(x, 0, x + 40, H), paint("#2a2f36"))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 60), paint("#2a2f36"))
    c.drawRect(skia.Rect.MakeWH(W, H), paint(FLUO, 0.06))  # store reflection in the glass
    grade(c, t, 0.4)


def chime_angle(t):
    a = 0.0
    if start("S04") - 0.5 <= t < start("S05"):
        a = 28 * math.sin((t - start("S04")) * 2 * math.pi * 1.6) * math.exp(-max(0.0, t - start("S04")) * 0.4)
    return a


def shot_chime_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#b9bfb3", "#9ea59a"])
    # door glass (dark rain) + frame
    c.drawRect(skia.Rect.MakeLTRB(160, 500, 920, H), paint("#0b0f18"))
    rain(c, t, 160, 500, 920, H, n=40, alpha=0.3)
    c.drawRect(skia.Rect.MakeLTRB(160, 500, 920, H), paint("#3a3f46", stroke=30))
    c.drawRect(skia.Rect.MakeLTRB(120, 300, 960, 470), paint("#8a9188"))
    closing = span(t, start("S22"), start("S22") + 0.8) if t >= start("S22") else 1.0
    if t >= start("S22"):  # door swinging shut behind her
        c.drawRect(skia.Rect.MakeLTRB(160 + 760 * closing, 500, 920, H), paint("#1a1f2a", 0.8))
    # bracket + bell
    c.drawRect(skia.Rect.MakeLTRB(500, 470, 580, 520), paint("#6e5a2c"))
    c.save()
    c.rotate(chime_angle(t), 540, 520)
    c.drawLine(540, 520, 540, 640, paint("#7a6a3a", stroke=8))
    bell = blob([(470, 760), (480, 680), (540, 630), (600, 680), (610, 760)], 0.4)
    cel(c, bell, "#c9a14a", Light(dir=(-0.6, -0.7), shadow_px=20, rim="#fff0c0", rim_alpha=0.8))
    c.drawOval(skia.Rect.MakeLTRB(455, 745, 625, 785), paint("#a8842f"))
    c.drawCircle(540, 790, 16, paint("#6e5a2c"))
    c.restore()
    grade(c, t)


def shot_doorway_quiet(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#b9bfb3", "#9ea59a"])
    c.drawRect(skia.Rect.MakeLTRB(200, 300, 880, 1800), paint("#070a12"))
    rain(c, t, 200, 300, 880, 1800, n=60, alpha=0.35)
    c.drawRect(skia.Rect.MakeLTRB(200, 300, 880, 1800), paint("#3a3f46", stroke=34))
    c.drawRect(skia.Rect.MakeLTRB(0, 1800, W, H), paint("#7d847a"))
    c.drawOval(skia.Rect.MakeLTRB(300, 1790, 780, 1840), paint("#9fb3c9", 0.35))  # puddle at the mat
    grade(c, t)


# ============================================================================ phone / monitor

def shot_phone_counter(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#7d8a84", "#5f6b66"])
    c.save()
    c.rotate(-3 + wiggle(t, 40, 1.5, 2) * (t < start("S06") + 0.5), 540, 980)
    c.drawRoundRect(skia.Rect.MakeLTRB(210, 320, 870, 1640), 60, 60, paint("#101216"))
    c.drawRoundRect(skia.Rect.MakeLTRB(240, 350, 840, 1610), 44, 44, paint("#0d1018"))
    kit.draw_text(c, "3:00", 540, 520, 120, color="#ffffff", weight="Bold")
    u = span(t, start("S06") + 0.1, start("S06") + 0.45, "back")
    dy = (1 - u) * -40
    c.drawRoundRect(skia.Rect.MakeLTRB(270, 650 + dy, 810, 1270 + dy), 34, 34, paint("#2a3040", 0.96 * min(1, u)))
    if u > 0:
        kit.draw_text(c, "MANAGER", 300, 720 + dy, 38, color="#9fd3ff", weight="Black", align="left", max_w=480)
        for i, ln in enumerate(["Whatever happens,", "DON'T open the", "back room."]):
            kit.draw_text(c, ln, 300, 820 + dy + i * 82, 54, color="#ff6a5a" if "DON'T" in ln else "#ffffff",
                          weight="ExtraBold", align="left", max_w=490)
    c.restore()
    glow(c, 540, 980, 700, "#cfe6ff", 0.12)
    grade(c, t, 0.6)


FEEDS = ["CAM 1 DOOR", "CAM 2 AISLE 2", "CAM 3 BACK", "CAM 4 AISLE 4"]


def feed_scene(c, k, t, r):
    l, tp, rr, b = r.left(), r.top(), r.right(), r.bottom()
    w, h = rr - l, b - tp
    c.drawRect(r, paint("#2e3a33"))
    vx, vy = l + w / 2, tp + h * 0.45
    c.drawPath(poly_path([(l, b), (rr, b), (vx + w * 0.08, vy), (vx - w * 0.08, vy)]), paint("#4c5a51"))
    if k in (1, 3):  # aisles
        for s in (-1, 1):
            c.drawPath(poly_path([(vx + s * w * 0.5, tp), (vx + s * w * 0.1, vy - h * 0.15), (vx + s * w * 0.1, vy + h * 0.05),
                                  (vx + s * w * 0.5, b)]), paint("#6a776e"))
    if k == 0:
        c.drawRect(skia.Rect.MakeLTRB(l + w * 0.3, tp + h * 0.15, rr - w * 0.3, b - h * 0.1), paint("#141a20"))
    if k == 2:
        c.drawRect(skia.Rect.MakeLTRB(l + w * 0.35, tp + h * 0.2, rr - w * 0.35, b - h * 0.15), paint("#3c4440"))
    if k == 3 and t >= start("S08") - 0.2:  # the tall figure, facing the shelf, too still
        fx, fy = l + w * 0.62, b - h * 0.18
        c.drawPath(blob([(fx - w * 0.04, fy), (fx - w * 0.05, fy - h * 0.55), (fx, fy - h * 0.72), (fx + w * 0.05, fy - h * 0.55),
                         (fx + w * 0.04, fy)], 0.3), paint("#0b0e0c"))
    # grain + scanlines + label
    r_ = (int(t * 30) * 7 + k) % 97
    for i in range(0, int(h), 6):
        c.drawLine(l, tp + i, rr, tp + i, paint("#000000", 0.12, stroke=2))
    for i in range(30):
        x = l + ((i * 53 + r_ * 17) % 1000) / 1000 * w
        y = tp + ((i * 91 + r_ * 31) % 1000) / 1000 * h
        c.drawCircle(x, y, 2, paint("#ffffff", 0.25))
    kit.draw_text(c, FEEDS[k], l + 14, tp + 34, 24, color="#e8ffe8", weight="Bold", align="left", max_w=w)
    kit.draw_text(c, "03:00:" + f"{int(t * 7) % 60:02d}", rr - 14, b - 14, 20, color="#e8ffe8", weight="Bold", align="right")


def shot_monitor_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#2b2f35", "#1a1d22"])
    c.drawRoundRect(skia.Rect.MakeLTRB(40, 420, 1040, 1600), 70, 70, paint("#3a3c40"))
    scr = skia.Rect.MakeLTRB(110, 500, 970, 1500)
    c.drawRoundRect(scr, 40, 40, paint("#05070a"))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(scr, 40, 40))
    hw, hh = scr.width() / 2, scr.height() / 2
    for k in range(4):
        r = skia.Rect.MakeXYWH(scr.left() + (k % 2) * hw + 6, scr.top() + (k // 2) * hh + 6, hw - 12, hh - 12)
        feed_scene(c, k, t, r)
    c.restore()
    glow(c, 540, 1000, 700, "#bfe8c8", 0.15)
    c.drawRect(skia.Rect.MakeLTRB(0, 1600, W, H), paint("#6b7b74"))
    grade(c, t, 0.4)


def shot_monitor_face(c, t):
    c.clear(hexc("#03050a"))
    P = clerk_pose(t)
    CLERK.draw(c, 540, 2440, 2.3, P, light=light_clerk(t), shadow=False)
    glow(c, 820, 1500, 900, MONI, 0.32 + 0.04 * math.sin(t * 15))
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#0a1424", 0.45, blend=skia.BlendMode.kMultiply))
    flat.vignette(c, W, H, 0.7)


def shot_face_cu(c, t):
    shot_monitor_face(c, t)


# ============================================================================ aisle / back room / janitor

def shot_aisle_pov(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#d9ddd2", "#b9bfb3"])
    vx, vy = 540, 820
    c.drawPath(poly_path([(0, H), (W, H), (vx + 80, vy + 60), (vx - 80, vy + 60)]), paint("#c8cdc2"))
    for i in range(10):  # floor tile lines
        y = vy + 60 + (H - vy - 60) * (i / 10) ** 1.8
        c.drawLine(0, y, W, y, paint("#a8aea2", 0.5, stroke=2))
    cols = ["#e2574c", "#3f8fd6", "#f2b134", "#55a868", "#8e5ea2"]
    for s in (-1, 1):
        c.drawPath(poly_path([(vx + s * 540, 0), (vx + s * 90, vy - 260), (vx + s * 90, vy + 60), (vx + s * 540, H)]), paint("#e9ece4"))
        for r in range(6):
            for k in range(6):
                u0, u1 = k / 6, (k + 0.8) / 6
                x0, x1 = lerp(vx + s * 520, vx + s * 100, u0), lerp(vx + s * 520, vx + s * 100, u1)
                ty = lerp(120, vy - 240, u0) + r * lerp(230, 50, u0)
                c.drawRect(skia.Rect.MakeLTRB(min(x0, x1), ty, max(x0, x1), ty + lerp(170, 35, u0)), paint(cols[(r + k) % 5]))
    for i in range(3):
        glow(c, vx, 160 + i * 220, 260, FLUO, 0.12)
    # wet bare footprints coming toward the camera, then stopping
    for k in range(7):
        u = k / 7
        y = lerp(vy + 90, 1700, u ** 1.3)
        x = vx + (24 if k % 2 else -24) * lerp(0.3, 2.4, u)
        s = lerp(0.25, 1.6, u)
        foot = blob([(x - 18 * s, y), (x - 14 * s, y - 50 * s), (x, y - 62 * s), (x + 14 * s, y - 50 * s), (x + 18 * s, y)], 0.45)
        c.drawPath(foot, paint("#8fa2a8", 0.55))
        for tz in range(4):
            c.drawCircle(x - 12 * s + tz * 8 * s, y - 72 * s, 4 * s, paint("#8fa2a8", 0.55))
    grade(c, t)


def shot_backroom_door(c, t):
    d = dark(t)
    flat.linear_grad(c, (0, 0, W, H), ["#b9bfb3", "#9ea59a"] if not d else ["#05070b", "#020305"])
    dr = skia.Rect.MakeLTRB(240, 330, 840, 1750)
    o = door_open_amount(t)
    c.drawRect(skia.Rect.MakeLTRB(dr.left() - 40, dr.top() - 40, dr.right() + 40, dr.bottom()), paint("#6f746d" if not d else "#0c0f14"))
    c.drawRect(dr, paint(WARM if o > 0 else "#000000"))
    if o > 0:
        glow(c, 540, 1000, 900, WARM, 0.4 * o)
        c.drawPath(poly_path([(dr.left(), dr.bottom()), (dr.right(), dr.bottom()), (dr.right() + 300 * o, H), (dr.left() - 300 * o, H)]),
                   paint(WARM, 0.18 * o))
    door_w = dr.width() * (1 - 0.9 * o)
    c.drawRect(skia.Rect.MakeLTRB(dr.left(), dr.top(), dr.left() + door_w, dr.bottom()), paint("#5a636b" if not d else "#0b0e13"))
    c.drawRoundRect(skia.Rect.MakeLTRB(dr.left() + door_w - 60, 1020, dr.left() + door_w - 30, 1060), 6, 6,
                    paint("#c9a14a" if not d else "#3a2e14"))
    if door_w > 300:
        c.drawRoundRect(skia.Rect.MakeLTRB(dr.left() + 60, 560, dr.left() + 340, 640), 8, 8, paint("#c8463c" if not d else "#2a0f0d"))
        kit.draw_text(c, "EMPLOYEES ONLY", dr.left() + 200, 614, 32, color="#ffffff", weight="Black", max_w=260,
                      alpha=1.0 if not d else 0.25)
    if d:  # light under the door
        c.drawRect(skia.Rect.MakeLTRB(dr.left() + 6, dr.bottom() - 12, dr.right() - 6, dr.bottom()), paint(WARM))
        glow(c, 540, dr.bottom(), 500, WARM, 0.4)
        c.drawRect(skia.Rect.MakeLTRB(0, dr.bottom(), W, H), paint("#050608"))
    grade(c, t, 0.5 if d else 1.0)


def mop_bucket(c, x, y, s):
    c.drawPath(poly_path([(x - 90 * s, y - 150 * s), (x + 90 * s, y - 150 * s), (x + 75 * s, y), (x - 75 * s, y)]), paint("#d6b13a"))
    c.drawOval(skia.Rect.MakeLTRB(x - 90 * s, y - 165 * s, x + 90 * s, y - 135 * s), paint("#6f8a8c"))
    c.drawLine(x + 30 * s, y - 150 * s, x + 80 * s, y - 640 * s, paint("#8a6a45", stroke=12 * s))


def shot_janitor_wide(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#b9bfb3", "#9ea59a"])
    dr = skia.Rect.MakeLTRB(240, 330, 840, 1750)
    c.drawRect(skia.Rect.MakeLTRB(dr.left() - 40, dr.top() - 40, dr.right() + 40, dr.bottom()), paint("#6f746d"))
    c.drawRect(dr, paint(WARM))
    glow(c, 540, 900, 900, WARM, 0.4)
    c.drawRect(skia.Rect.MakeLTRB(0, 1750, W, H), paint("#7d847a"))
    P = jan_pose(t)
    walk = span(t, start("S11") - 0.1, start("S11") + 1.4)
    JAN.draw(c, 520, lerp(1700, 1820, walk), lerp(1.4, 1.55, walk), P,
             light=Light(dir=(0.0, -1.0), shadow_px=16, rim=WARM, rim_alpha=0.9, rim_px=7))
    hx, hy = JAN.head_pos(520, 1820, 1.55, P)
    name_tag(c, 580, hy + 300, 2.0, scratched=True)
    mop_bucket(c, 820, 1840, 1.2)
    grade(c, t)


def shot_janitor_low(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#9ea59a", "#cfd4c8"])
    for k in range(3):
        c.drawRoundRect(skia.Rect.MakeLTRB(80 + k * 340, 60, 340 + k * 340, 95), 10, 10, paint(FLUO))
    P = jan_pose(t)
    c.save()
    c.rotate(-4, 540, 1400)
    JAN.draw(c, 540, 2700, 2.6, P, light=Light(dir=(0.0, -1.0), shadow_px=24, rim=FLUO, rim_alpha=0.6, rim_px=6), shadow=False)
    c.restore()
    name_tag(c, 680, 1460, 3.0, scratched=True)
    grade(c, t)


def shot_janitor_cu(c, t):
    store_back(c, t, show_clerk=False)
    P = jan_pose(t)
    JAN.draw(c, 540, 2420, 2.25, P, light=light_clerk(t), shadow=False)
    name_tag(c, 650, 1330, 2.6, scratched=True)
    grade(c, t)


def shot_card_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#9aa8a1", "#7d8a84"])
    u = span(t, start("S13") + 0.25, start("S13") + 0.55, "out")
    s = lerp(1.6, 1.0, u)
    c.save()
    c.translate(540, 980)
    c.rotate(lerp(-25, -3, u))
    c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeLTRB(-420, -560, 420, 560), 26, 26, paint("#000000", 0.25 * u, blur=20))
    c.drawRoundRect(skia.Rect.MakeLTRB(-400, -540, 400, 540), 26, 26, paint("#f1e9d6"))
    c.drawRoundRect(skia.Rect.MakeLTRB(-400, -540, 400, 540), 26, 26, paint("#ffffff", 0.25, stroke=14))
    ft = kit.font(52, "Black")
    c.drawString("NIGHT SHIFT RULES", -ft.measureText("NIGHT SHIFT RULES") / 2, -410, ft, paint("#c0392b"))
    f = kit.font(50, "Bold")
    f.setSkewX(-0.18)
    rules = [["1. Never let anyone", "behind the counter."], ["2. If the lights go out,", "don't look at the monitor."],
             ["3. Never answer the", "phone at 3:33."]]
    for i, ls in enumerate(rules):
        for j, ln in enumerate(ls):
            c.drawString(ln, -340, -270 + i * 250 + j * 66, f, paint("#1c1c24"))
    c.restore()
    if t >= start("S14"):  # his finger taps rule 1
        tap = abs(math.sin((t - start("S14")) * 2 * math.pi * 1.4)) * 30
        fx, fy = 300, 720 - tap
        L = Light(dir=(0, -1), shadow_px=14)
        cel(c, capsule((fx + 260, fy + 520), (fx, fy), 120), "#34405a", L, k=3)
        cel(c, capsule((fx + 20, fy + 40), (fx - 40, fy - 60), 52), JAN.s.skin, L, k=2)
        cel(c, ellipse_path(fx + 50, fy + 80, 95, 80), JAN.s.skin, L, k=2)
    grade(c, t, 0.7)


def shot_wall_phone(c, t):
    ring = 0.0
    for t0, t1 in ((B["ring333"] - 0.15, B["ring_stop"]), (B["ring334"], B["lights_die"])):
        if t0 <= t < t1:
            ring = 1.0 if ((t - t0) % 1.6) < 1.1 else 0.0
    flat.linear_grad(c, (0, 0, W, H), ["#b9bfb3", "#9ea59a"])
    sh = wiggle(t, 70, 14, 5) * ring
    c.save()
    c.translate(sh, 0)
    c.drawRoundRect(skia.Rect.MakeLTRB(240, 380, 840, 1480), 70, 70, paint("#d8cfb6"))
    c.drawRoundRect(skia.Rect.MakeLTRB(290, 420, 790, 760), 150, 150, paint("#c7bc9e"))
    c.drawRoundRect(skia.Rect.MakeLTRB(290, 420, 790, 760), 150, 150, paint("#8f8670", stroke=8))
    for k in range(12):
        x, y = 390 + (k % 3) * 150, 870 + (k // 3) * 140
        c.drawCircle(x, y, 48, paint("#efe6cc"))
        kit.draw_text(c, "123456789*0#"[k], x, y + 20, 52, color="#5a5240", weight="Black")
    c.restore()
    c.drawPath(blob([(540, 1480), (500, 1600), (600, 1700), (520, 1820), (560, 1940)], close=False), paint("#4a4436", stroke=14))
    if ring:
        for k in range(3):
            c.drawLine(150 - k * 40, 600, 150 - k * 40, 1200, paint("#ffffff", 0.5, stroke=8))
            c.drawLine(930 + k * 40, 600, 930 + k * 40, 1200, paint("#ffffff", 0.5, stroke=8))
    if B["ring333"] - 0.15 <= t < B["ring334"]:
        c.drawRect(skia.Rect.MakeWH(W, H), paint("#e0453a", 0.25, blend=skia.BlendMode.kMultiply))
    grade(c, t)


def shot_callerid_cu(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#c7bc9e", "#a89e80"])
    c.drawRoundRect(skia.Rect.MakeLTRB(140, 600, 940, 1300), 40, 40, paint("#1d2a20"))
    c.drawRoundRect(skia.Rect.MakeLTRB(180, 640, 900, 1260), 24, 24, paint("#8fd6a0", 0.9))
    kit.draw_text(c, "INCOMING", 540, 760, 50, color="#123018", weight="Black")
    kit.draw_text(c, "HOME", 540, 930, 150, color="#123018", weight="Black")
    amp = TIMING.mouth(t, "sister") if TIMING else 0.0
    for k in range(21):
        h = 8 + (amp * 120 + 20 * (t < start("S25"))) * abs(math.sin(k * 1.3 + t * 16)) * (1 - abs(k - 10) / 12)
        c.drawRoundRect(skia.Rect.MakeLTRB(250 + k * 28, 1110 - h, 266 + k * 28, 1110 + h), 6, 6, paint("#123018"))
    glow(c, 540, 950, 700, "#8fd6a0", 0.25)
    grade(c, t, 0.6)


def shot_hand_receiver(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#b9bfb3", "#9ea59a"])
    c.drawRoundRect(skia.Rect.MakeLTRB(160, 1100, 920, 1900), 60, 60, paint("#d8cfb6"))
    c.drawRoundRect(skia.Rect.MakeLTRB(200, 1060, 880, 1300), 110, 110, paint("#c7bc9e"))
    c.drawRoundRect(skia.Rect.MakeLTRB(200, 1060, 880, 1300), 110, 110, paint("#8f8670", stroke=8))
    L = Light(dir=(-0.3, -1), shadow_px=18)
    shake = wiggle(t, 24, 10, 2)
    gripped = t >= start("S26")
    hx, hy = 560 + (0 if gripped else shake), 820 + (0 if gripped else wiggle(t, 21, 8, 4))
    cel(c, capsule((hx - 520, hy - 520), (hx - 60, hy - 40), 170), CLERK.s.shirt, L, k=3)
    hand = blob([(hx - 120, hy - 60), (hx + 60, hy - 120), (hx + 200, hy - 20), (hx + 160, hy + 120), (hx - 80, hy + 90)], 0.45)
    cel(c, hand, SKIN, L, k=3)
    for k in range(4):
        cel(c, capsule((hx + 40 + k * 40, hy + 60), (hx + 60 + k * 45, hy + 190), 46), SKIN, L, k=2)
    if gripped:  # the janitor's hand clamps your wrist
        u = span(t, start("S26"), start("S26") + 0.15, "out")
        jx = lerp(1300, hx - 130, u)
        cel(c, capsule((jx + 700, hy - 300), (jx + 80, hy - 100), 180), "#34405a", L, k=3)
        cel(c, blob([(jx - 70, hy - 170), (jx + 120, hy - 190), (jx + 150, hy - 10), (jx - 60, hy + 20)], 0.45), JAN.s.skin, L, k=3)
    grade(c, t)


# ============================================================================ the woman

def woman(c, x, feet_y, h, t, smile=1.0, lean=0.0, hands_on_counter=False, crop_low=False):
    """Barefoot, soaking wet; dark hair hangs over the face; only a too-wide smile shows."""
    skin, hair, dress = "#cfd8d6", "#0b0b0e", "#8f9a99"
    L = Light(dir=(0.0, -1.0), shadow_px=0.03 * h, rim=FLUO, rim_alpha=0.4, rim_px=0.006 * h)
    hx, hy = x + lean * 0.12 * h, feet_y - 0.88 * h
    if not crop_low:
        for s in (-1, 1):  # bare legs + feet
            c.drawPath(capsule((x + s * 0.05 * h, feet_y - 0.4 * h), (x + s * 0.055 * h, feet_y - 0.03 * h), 0.05 * h), paint(skin))
            c.drawOval(skia.Rect.MakeLTRB(x + s * 0.055 * h - 0.04 * h, feet_y - 0.03 * h, x + s * 0.055 * h + 0.05 * h, feet_y + 0.01 * h),
                       paint(skin))
    body = blob([(x - 0.13 * h, feet_y - 0.72 * h), (x + 0.13 * h, feet_y - 0.72 * h), (x + 0.17 * h, feet_y - 0.36 * h),
                 (x - 0.17 * h, feet_y - 0.36 * h)], 0.35)
    c.save()
    c.rotate(lean * 14, x, feet_y - 0.4 * h)
    cel(c, body, dress, L, k=2)
    for s in (-1, 1):  # arms
        if hands_on_counter:
            c.drawPath(capsule((x + s * 0.12 * h, feet_y - 0.7 * h), (x + s * 0.2 * h, feet_y - 0.46 * h), 0.04 * h), paint(skin))
        else:
            c.drawPath(capsule((x + s * 0.13 * h, feet_y - 0.7 * h), (x + s * 0.15 * h, feet_y - 0.4 * h), 0.04 * h), paint(skin))
    c.drawPath(ellipse_path(hx, hy, 0.095 * h, 0.115 * h), paint(skin))
    # the smile (too wide) shows through a parting in the hair
    if smile > 0:
        sm = skia.Path()
        sm.moveTo(hx - 0.075 * h, hy + 0.03 * h)
        sm.quadTo(hx, hy + 0.085 * h * smile, hx + 0.075 * h, hy + 0.03 * h)
        sm.quadTo(hx, hy + 0.06 * h * smile, hx - 0.075 * h, hy + 0.03 * h)
        c.drawPath(sm, paint("#1a0b0b"))
        for k in range(9):
            tx = hx - 0.06 * h + k * 0.015 * h
            c.drawRect(skia.Rect.MakeLTRB(tx, hy + 0.035 * h, tx + 0.011 * h, hy + 0.05 * h), paint("#f1ece0"))
    hairp = blob([(hx - 0.11 * h, hy - 0.1 * h), (hx, hy - 0.14 * h), (hx + 0.11 * h, hy - 0.1 * h), (hx + 0.13 * h, hy + 0.35 * h),
                  (hx + 0.06 * h, hy + 0.36 * h), (hx + 0.08 * h, hy + 0.02 * h), (hx - 0.08 * h, hy + 0.02 * h),
                  (hx - 0.06 * h, hy + 0.36 * h), (hx - 0.13 * h, hy + 0.35 * h)], 0.4)
    c.drawPath(hairp, paint(hair))
    c.drawRect(skia.Rect.MakeLTRB(hx - 0.09 * h, hy - 0.09 * h, hx + 0.09 * h, hy + 0.025 * h), paint(hair))  # hair over the eyes
    for k in range(5):
        c.drawLine(hx - 0.07 * h + k * 0.035 * h, hy - 0.08 * h, hx - 0.075 * h + k * 0.035 * h, hy + 0.3 * h,
                   paint("#2a2a30", 0.6, stroke=0.006 * h))
    c.restore()
    for i in range(6):  # dripping
        ph = (t * 1.4 + i * 0.29) % 1
        dx = (i - 3) * 0.05 * h
        c.drawOval(skia.Rect.MakeLTRB(x + dx - 4, feet_y - 0.36 * h + ph * 0.34 * h, x + dx + 4, feet_y - 0.36 * h + ph * 0.34 * h + 12),
                   paint("#cfe6ff", 0.7 * (1 - ph)))


def shot_woman_door(c, t):
    shot_doorway_quiet(c, t)
    u = span(t, start("S18"), start("S18") + 0.6)
    woman(c, 540, 1810, 1350, t, smile=u)
    grade(c, t, 0.4)


def shot_woman_counter(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#d9ddd2", "#b9bfb3"])
    for k in range(4):
        c.drawRect(skia.Rect.MakeLTRB(40 + k * 260, 300, 240 + k * 260, 1100), paint(["#e2574c", "#3f8fd6", "#f2b134", "#55a868"][k], 0.6))
    woman(c, 540, 1900, 1500, t, hands_on_counter=True, crop_low=True)
    c.drawRect(skia.Rect.MakeLTRB(0, 1300, W, H), paint("#6b7b74"))  # counter (your side)
    c.drawRect(skia.Rect.MakeLTRB(0, 1290, W, 1340), paint("#9aa8a1"))
    for s in (-1, 1):  # her hands flat on the counter
        c.drawOval(skia.Rect.MakeLTRB(540 + s * 300 - 90, 1280, 540 + s * 300 + 90, 1340), paint("#cfd8d6"))
    c.drawRect(skia.Rect.MakeLTRB(200, 1330, 880, 1350), paint("#cfe6ff", 0.4))  # water on the counter
    grade(c, t)


def shot_woman_smile(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#d9ddd2", "#b9bfb3"])
    lean = span(t, start("S20"), end("S20") + 0.4, "in_")
    h = 3400 * (1 + 0.15 * lean)
    woman(c, 540, 760 + 0.88 * h, h, t, lean=lean * 0.6, crop_low=True)
    grade(c, t)


def shot_mop_block(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#d9ddd2", "#b9bfb3"])
    c.drawRect(skia.Rect.MakeLTRB(0, 1100, W, H), paint("#6b7b74"))
    c.drawRect(skia.Rect.MakeLTRB(380, 1100, 700, H), paint("#3a423f"))  # the counter gap
    pull = span(t, B["mop"] + 0.05, B["mop"] + 0.5)
    for s in (-1, 1):  # her pale hands reaching in, then pulling back
        hx = 540 + s * 80 - s * 40 * pull
        c.drawPath(capsule((hx, 700 - 300 * pull), (hx, 1150 - 260 * pull), 70), paint("#cfd8d6"))
    u = span(t, B["mop"], B["mop"] + 0.12, "out")
    mx = lerp(1500, 540, u)
    c.save()
    c.rotate(-4, mx, 1080)
    c.drawRoundRect(skia.Rect.MakeLTRB(mx - 900, 1050, mx + 700, 1110), 30, 30, paint("#8a6a45"))
    c.drawRoundRect(skia.Rect.MakeLTRB(mx - 900, 1050, mx + 700, 1070), 20, 20, paint("#b08a5e"))
    c.restore()
    grade(c, t)


# ============================================================================ dark: ear / shoulder / choice

def shot_ear_ecu(c, t):
    c.clear(hexc("#020306"))
    L = Light(dir=(0.9, 0.3), shadow_px=40, rim=MONI, rim_alpha=0.8, rim_px=10)
    cel(c, ellipse_path(700, 1000, 520, 640), SKIN, L, k=5)  # side of the head
    cel(c, blob([(520, 820), (420, 880), (400, 1080), (470, 1200), (560, 1150), (540, 950)], 0.45), SKIN, L, k=4)  # ear
    c.drawPath(blob([(470, 920), (440, 1000), (470, 1100)], close=False), paint(shade(hexc(SKIN), 0.6), stroke=14))
    c.drawPath(blob([(620, 380), (1100, 300), (1180, 700), (900, 600)], 0.4), paint(CLERK.s.hair))
    glow(c, 1000, 1300, 800, MONI, 0.25)
    br = 0.5 + 0.5 * math.sin((t - start("S30a")) * 2 * math.pi / 1.4)
    c.drawPath(ellipse_path(220, 980, 160, 120), paint("#cfd8e8", 0.05 + 0.05 * br, blur=40))  # breath in the dark
    flat.vignette(c, W, H, 0.7)


def shot_shoulder_hand(c, t):
    c.clear(hexc("#020306"))
    L = Light(dir=(0.9, 0.3), shadow_px=40, rim=MONI, rim_alpha=0.8, rim_px=10)
    sh = blob([(-100, H), (-60, 1100), (400, 900), (900, 1000), (1180, 1300), (1180, H)], 0.4)
    cel(c, sh, CLERK.s.shirt, L, k=4)
    cel(c, ellipse_path(820, 560, 300, 360), SKIN, L, k=4)
    u = span(t, B["touch"] + 0.1, B["touch"] + 0.7, "out")
    hx, hy = lerp(-200, 380, u), lerp(700, 960, u)
    cel(c, blob([(hx - 120, hy - 60), (hx + 120, hy - 100), (hx + 170, hy + 60), (hx - 60, hy + 100)], 0.4), "#cfd8d6", L, k=3)
    for k in range(4):
        fx = hx - 40 + k * 55
        c.drawPath(capsule((fx, hy + 40), (fx + 30, hy + 260 + (k % 2) * 30), 40), paint("#c3ceca"))
    if u > 0.5:
        for i in range(5):
            ph = (t * 1.3 + i * 0.27) % 1
            c.drawOval(skia.Rect.MakeLTRB(hx + i * 40 - 4, hy + 280 + ph * 400, hx + i * 40 + 4, hy + 292 + ph * 400), paint("#cfe6ff", 0.7 * (1 - ph)))
    glow(c, 900, 1500, 800, MONI, 0.25)
    flat.vignette(c, W, H, 0.7)


def shot_choice_bg(c, t):
    ring = ((t - B["choice"]) % 1.6) < 1.1
    store_back(c, t, phone_shake=1.0 if ring else 0.0, behind=True)
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", 0.25))
    for n, (a, b) in CHOICE_TARGETS.items():  # leader lines from each pill to its spot in the scene
        u = span(t, B["choice"] + 0.3 + 0.15 * (n - 1), B["choice"] + 0.8 + 0.15 * (n - 1))
        if u <= 0:
            continue
        ex, ey = lerp(a[0], b[0], u), lerp(a[1], b[1], u)
        c.drawLine(a[0], a[1], ex, ey, paint("#ffffff", 0.85, stroke=4))
        pulse = 1 + 0.25 * math.sin(t * 6 + n)
        c.drawCircle(b[0], b[1], 14 * pulse * u, paint(["#e2574c", "#3f8fd6", "#55a868", "#d9a43b"][n - 1]))
        c.drawCircle(b[0], b[1], 14 * pulse * u, paint("#ffffff", stroke=4))
    flat.vignette(c, W, H, 0.6)


SHOTS = dict(store_ext=shot_store_ext, clerk_cu=shot_clerk_cu, glass_pov=shot_glass_pov, chime_cu=shot_chime_cu,
             counter_wide=shot_counter_wide, phone_counter=shot_phone_counter, monitor_cu=shot_monitor_cu,
             aisle_pov=shot_aisle_pov, backroom_door=shot_backroom_door, janitor_wide=shot_janitor_wide,
             janitor_low=shot_janitor_low, card_cu=shot_card_cu, janitor_cu=shot_janitor_cu, wall_phone=shot_wall_phone,
             doorway_quiet=shot_doorway_quiet, woman_door=shot_woman_door, woman_counter=shot_woman_counter,
             woman_smile=shot_woman_smile, mop_block=shot_mop_block, callerid_cu=shot_callerid_cu,
             hand_receiver=shot_hand_receiver, monitor_face=shot_monitor_face, ear_ecu=shot_ear_ecu,
             shoulder_hand=shot_shoulder_hand, face_cu=shot_face_cu, choice_bg=shot_choice_bg)
