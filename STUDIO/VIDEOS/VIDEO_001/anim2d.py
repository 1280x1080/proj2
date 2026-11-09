"""VIDEO_001 - 2D shots.  One draw function per shot: shot_NAME(canvas, t), native 1080x1920.

Shots
  room : one-point-perspective living room at night, Mia standing with a mug, floor lamp left.
  lamp : close-up of the lamp shade / bulb (insert shot for the flickers).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "PIPELINE" / "twod"))
sys.path.insert(0, str(HERE))
import skia  # noqa: E402

import flat  # noqa: E402
import kit  # noqa: E402
from beats import B, TIMING, flick_count, lamp_level  # noqa: E402
from flat import CAST, Light, Puppet, blob, cel, glow, hexc, paint, poly_path  # noqa: E402
from kit import H, W, Keys, blink, span  # noqa: E402

CAM = kit.Cam1P(vx=W / 2, vy=860, cam_h=150, f=887)
MIA = Puppet(CAST["mia"], "mia")
MIA_POS = (20, 150)  # world x, z
LAMP_POS = (-165, 430)
UNIT = 0.2125  # puppet units -> world cm (puppet ~800 u = 170 cm)

WARM = "#ffc87a"
NIGHT = "#0c1633"


# ============================================================================ room

def _quad(c, pts3, color, alpha=None):
    c.drawPath(poly_path(CAM.quad(pts3)), paint(color, alpha))


def draw_room(c, lamp):
    X0, X1, Hh, ZB, ZN = -300, 300, 280, 700, 105
    # ceiling, walls, floor
    _quad(c, [(X0, Hh, ZN), (X1, Hh, ZN), (X1, Hh, ZB), (X0, Hh, ZB)], "#a89479")
    _quad(c, [(X0, 0, ZN), (X0, Hh, ZN), (X0, Hh, ZB), (X0, 0, ZB)], "#b9a385")
    _quad(c, [(X1, 0, ZN), (X1, Hh, ZN), (X1, Hh, ZB), (X1, 0, ZB)], "#b29c7f")
    _quad(c, [(X0, 0, ZB), (X1, 0, ZB), (X1, Hh, ZB), (X0, Hh, ZB)], "#cdb89a")
    # wallpaper stripes on the back wall
    for i in range(1, 20):
        x = X0 + i * 30
        a, b = CAM.project(x, 0, ZB)[:2], CAM.project(x, Hh, ZB)[:2]
        c.drawLine(*a, *b, paint("#c4ae8f", stroke=6))
    # floor + planks converging to the vanishing point
    _quad(c, [(X0, 0, ZN), (X1, 0, ZN), (X1, 0, ZB), (X0, 0, ZB)], "#8d6a4b")
    for i in range(-14, 15):
        x = i * 22
        a, b = CAM.project(x, 0, ZN)[:2], CAM.project(x, 0, ZB)[:2]
        c.drawLine(*a, *b, paint("#7a5a3e", stroke=3))
    for z in (160, 230, 330, 470, 640):
        a, b = CAM.project(X0, 0, z)[:2], CAM.project(X1, 0, z)[:2]
        c.drawLine(*a, *b, paint("#7f5f43", 0.6, stroke=2))
    # skirting
    _quad(c, [(X0, 0, ZB), (X1, 0, ZB), (X1, 10, ZB), (X0, 10, ZB)], "#e9dfcf")
    # window (back wall, left) with night sky + moon
    wx0, wx1, wy0, wy1 = -255, -70, 95, 235
    sky = CAM.quad([(wx0, wy1, ZB), (wx1, wy1, ZB), (wx1, wy0, ZB), (wx0, wy0, ZB)])
    l, t = sky[0]
    r, b = sky[2]
    flat.linear_grad(c, (l, t, r, b), ["#0b1638", "#1d3263", "#2c4677"])
    c.drawCircle(l + (r - l) * 0.7, t + (b - t) * 0.3, 22, paint("#f1ecd6"))
    flat.glow(c, l + (r - l) * 0.7, t + (b - t) * 0.3, 70, "#9fb6ff", 0.25)
    for sx, sy in ((0.2, 0.2), (0.35, 0.55), (0.12, 0.7), (0.5, 0.15)):
        c.drawCircle(l + (r - l) * sx, t + (b - t) * sy, 2.2, paint("#dfe6ff"))
    c.drawRect(skia.Rect.MakeLTRB(l, t, r, b), paint("#efe6d6", stroke=12))
    c.drawLine((l + r) / 2, t, (l + r) / 2, b, paint("#efe6d6", stroke=8))
    c.drawLine(l, (t + b) / 2, r, (t + b) / 2, paint("#efe6d6", stroke=8))
    # curtains
    for side, x in ((-1, l), (1, r)):
        cx = x + side * 6
        cur = blob([(cx - 34, t - 22), (cx + 34, t - 22), (cx + 30 + side * 6, b + 40), (cx - 30 + side * 6, b + 46)], 0.3)
        cel(c, cur, "#8e3f3a", Light(dir=(-0.8, -0.4), shadow_px=10))
    # picture frame
    fq = CAM.quad([(-25, 205, ZB), (95, 205, ZB), (95, 130, ZB), (-25, 130, ZB)])
    c.drawRect(skia.Rect.MakeLTRB(*fq[0], *fq[2]), paint("#e8d9b8"))
    pl, pt, pr, pb = fq[0][0] + 10, fq[0][1] + 10, fq[2][0] - 10, fq[2][1] - 10
    flat.linear_grad(c, (pl, pt, pr, pb), ["#86b2c9", "#d7c08c"])
    c.drawPath(poly_path([(pl, pb), (pl + (pr - pl) * 0.4, pt + (pb - pt) * 0.4), (pr, pb)]), paint("#5f7f5a"))
    c.drawRect(skia.Rect.MakeLTRB(*fq[0], *fq[2]), paint("#5b3d28", stroke=8))
    # door (back wall, right)
    dq = CAM.quad([(185, 210, ZB), (290, 210, ZB), (290, 0, ZB), (185, 0, ZB)])
    dl, dt, dr, db_ = dq[0][0], dq[0][1], dq[2][0], dq[2][1]
    c.drawRect(skia.Rect.MakeLTRB(dl - 8, dt - 8, dr + 8, db_), paint("#e9dfcf"))
    c.drawRect(skia.Rect.MakeLTRB(dl, dt, dr, db_), paint("#6e4b34"))
    for k in range(2):
        yy0 = dt + 14 + k * (db_ - dt) / 2
        c.drawRoundRect(skia.Rect.MakeLTRB(dl + 14, yy0, dr - 14, yy0 + (db_ - dt) / 2 - 26), 4, 4,
                        paint("#5e3f2b", stroke=5))
    c.drawCircle(dl + 16, (dt + db_) / 2 + 10, 6, paint("#d9b45a"))
    # light gap under the door (hallway light) - grows on the knock
    knock_u = span(c_t[0], B["knocks"][0] - 0.05, B["knocks"][0] + 0.25)
    if knock_u > 0:
        c.drawRect(skia.Rect.MakeLTRB(dl + 4, db_ - 4, dr - 4, db_), paint("#ffe8b0", 0.9 * knock_u))
    # rug
    rug = [CAM.project(x, 0, z)[:2] for x, z in ((-170, 300), (170, 300), (210, 470), (-210, 470))]
    c.drawPath(blob(rug, 0.6), paint("#5a6f7d"))
    c.drawPath(blob(rug, 0.6), paint("#d9c9a8", stroke=6))
    # side table + plant (right)
    sx, sz = 215, 330
    top = CAM.quad([(sx - 45, 70, sz - 30), (sx + 45, 70, sz - 30), (sx + 45, 70, sz + 30), (sx - 45, 70, sz + 30)])
    for lx in (-38, 38):
        a, b = CAM.project(sx + lx, 70, sz - 25)[:2], CAM.project(sx + lx, 0, sz - 25)[:2]
        c.drawLine(*a, *b, paint("#4a3221", stroke=10))
    c.drawPath(poly_path(top), paint("#6b4a32"))
    px, py, ps = CAM.project(sx, 70, sz)
    c.drawPath(poly_path([(px - 16 * ps, py), (px + 16 * ps, py), (px + 12 * ps, py - 26 * ps), (px - 12 * ps, py - 26 * ps)]),
               paint("#c2683f"))
    for k, ang in enumerate((-50, -20, 10, 35, 60)):
        a = math.radians(ang - 90)
        tip = (px + math.cos(a) * 46 * ps, py - 26 * ps + math.sin(a) * 46 * ps)
        leaf = blob([(px, py - 24 * ps), ((px + tip[0]) / 2 + 8, (py - 24 * ps + tip[1]) / 2), tip,
                     ((px + tip[0]) / 2 - 8, (py - 24 * ps + tip[1]) / 2)], 0.5)
        c.drawPath(leaf, paint("#4f8a55" if k % 2 else "#3f7347"))


c_t = [0.0]  # current time for helpers that need it


def draw_lamp(c, lamp, lit_glow=True):
    x, z = LAMP_POS
    base = CAM.project(x, 0, z)
    top = CAM.project(x, 150, z)
    s = base[2]
    c.drawOval(skia.Rect.MakeLTRB(base[0] - 26 * s, base[1] - 5 * s, base[0] + 26 * s, base[1] + 5 * s), paint("#2d2622"))
    c.drawLine(base[0], base[1], top[0], top[1], paint("#3a302a", stroke=4 * s))
    sh_top = CAM.project(x, 190, z)
    w0, w1 = 20 * s, 32 * s
    shade_p = poly_path([(sh_top[0] - w0, sh_top[1]), (sh_top[0] + w0, sh_top[1]), (top[0] + w1, top[1]), (top[0] - w1, top[1])])
    on = kit.lerp(hexc("#9a8a6d"), 0, 0)
    col = flat.lerp_col(hexc("#a8946f"), hexc("#ffe2a6"), max(0, (lamp - 0.1) / 0.9))
    c.drawPath(shade_p, paint(col))
    c.drawPath(shade_p, paint("#7a6648", 0.6, stroke=3))
    return (top[0], top[1] - 4 * s, s)


def mia_pose(t):
    eo = blink(t, seed=3)
    pose = dict(breathe=t, eye_open=eo, arm_r=(26, 128), hold_r="mug", arm_l=(10, 14), mouth="smile",
                pupil=(0.1, 0.05), lid=0.15, brow=(0.0, 0.0), turn=0.08, head_tilt=-2)
    # bored glance at each normal flicker
    look = 0.0
    for ft in B["flicks"]:
        look = max(look, span(t, ft - 0.05, ft + 0.15) * (1 - span(t, ft + 0.6, ft + 0.95)))
    pose["pupil"] = (kit.lerp(0.1, -0.85, look), 0.05)
    pose["turn"] = kit.lerp(0.08, -0.22, look)
    pose["lid"] = kit.lerp(0.15, 0.35, look)
    pose["mouth"] = "neutral" if look > 0.3 else "smile"
    # the fourth flicker: startle
    r = span(t, B["reveal"], B["reveal"] + 0.18, "out")
    if r > 0:
        pose.update(eye_open=kit.lerp(eo, max(eo, 1.0) * 1.0, r), lid=0.0, brow=(0.9 * r, 0.75 * r), mouth="o",
                    pupil=(kit.lerp(0.1, -0.9, r), -0.1), turn=kit.lerp(0.08, -0.45, r),
                    arm_r=(kit.lerp(26, 38, r), kit.lerp(128, 112, r)), head_tilt=kit.lerp(-2, 4, r))
        pose["crouch"] = 0.06 * math.sin(math.pi * span(t, B["reveal"], B["reveal"] + 0.35, "linear"))
    # Mia speaks
    talk = TIMING.mouth(t, "mia")
    if t >= B["line2_start"] - 0.1:
        pose["talk"] = talk
        pose["mouth"] = "neutral" if t < B["four"] else "frown"
        back = span(t, B["four"] - 0.25, B["four"] + 0.1)
        pose["pupil"] = (kit.lerp(-0.9, 0.0, back), 0.0)
        pose["turn"] = kit.lerp(-0.45, -0.05, back)
    # knock: head snaps to the door (screen right)
    k = span(t, B["knocks"][0] + 0.05, B["knocks"][0] + 0.3, "out")
    if k > 0:
        pose.update(turn=kit.lerp(pose["turn"], 0.62, k), pupil=(kit.lerp(pose["pupil"][0], 1.0, k), -0.15),
                    brow=(0.9, 0.6), mouth="o", talk=0.0, eye_open=max(pose["eye_open"], 0.95 if k > 0.5 else 0))
    return pose


def shot_room(c, t):
    c_t[0] = t
    lamp = lamp_level(t)
    c.clear(hexc("#000000"))
    draw_room(c, lamp)
    bulb = draw_lamp(c, lamp)
    # warm pool of light on the floor + wall
    if lamp > 0.2:
        glow(c, bulb[0], bulb[1] + 40, 520 * lamp, WARM, 0.22 * lamp)
    # Mia
    x, z = MIA_POS
    sx, sy, s = CAM.project(x, 0, z)
    light = Light(dir=(-0.75, -0.55), shadow_px=16, rim=WARM if lamp > 0.5 else "#9fb6ff",
                  rim_alpha=0.75 if lamp > 0.5 else 0.5, rim_px=5)
    MIA.draw(c, sx, sy, s * UNIT, mia_pose(t), light=light)
    # night darkness when the lamp drops, then the lamp's own glow on top
    dark = (1 - lamp) * 0.62 + 0.08
    c.drawRect(skia.Rect.MakeWH(W, H), paint(NIGHT, dark, blend=skia.BlendMode.kMultiply))
    c.drawRect(skia.Rect.MakeWH(W, H), paint(NIGHT, dark * 0.35))
    if lamp > 0.2:
        glow(c, bulb[0], bulb[1], 300 * lamp, WARM, 0.45 * lamp)
    else:  # moonlight from the window when the lamp is out
        glow(c, 330, 760, 420, "#7d9cff", 0.12)
    flat.vignette(c, W, H, 0.42)


def shot_lamp(c, t):
    """Insert: close-up of the lamp shade + bulb."""
    lamp = lamp_level(t)
    flat.linear_grad(c, (0, 0, W, H), ["#3b3128", "#241d18"])
    for i in range(12):
        x = 60 + i * 90
        c.drawLine(x, 0, x, H, paint("#2f2720", stroke=24))
    cx, top, bot = W / 2 + 40, 520, 1020
    wt, wb = 250, 410
    shade_p = poly_path([(cx - wt, top), (cx + wt, top), (cx + wb, bot), (cx - wb, bot)])
    col = flat.lerp_col(hexc("#6d5f49"), hexc("#ffe0a0"), max(0, (lamp - 0.1) / 0.9))
    c.drawPath(shade_p, paint(col))
    for k in range(1, 9):
        u = k / 9
        c.drawLine(cx - wt + (cx - wb - (cx - wt)) * 0 + u * 2 * wt, top, cx - wb + u * 2 * wb, bot,
                   paint("#000000", 0.05, stroke=3))
    c.drawPath(shade_p, paint("#5a4a35", stroke=6))
    # bulb under the shade
    by = bot + 40
    c.drawCircle(cx, by, 70, paint(flat.lerp_col(hexc("#8d8577"), hexc("#fff4d6"), lamp)))
    c.drawRect(skia.Rect.MakeLTRB(cx - 38, bot - 30, cx + 38, by - 50), paint("#b9a67a"))
    c.drawLine(cx, by + 70, cx, H, paint("#2b231e", stroke=26))
    if lamp > 0.2:
        glow(c, cx, by, 700 * lamp, WARM, 0.55 * lamp)
        glow(c, cx, by, 180, "#ffffff", 0.35 * lamp)
    # dust motes in the beam
    for i in range(26):
        ph = i * 2.399
        px = cx + math.sin(ph * 3.1 + t * 0.4) * 380
        py = by + 120 + ((i * 97 + t * 30 * (1 + i % 3)) % 700)
        c.drawCircle(px, py, 2 + i % 3, paint("#fff2cf", 0.35 * lamp))
    flat.vignette(c, W, H, 0.55)


SHOTS = dict(room=shot_room, lamp=shot_lamp)
