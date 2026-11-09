"""VIDEO_002 - 2D shots: 'studio' = bright room, the teen mascot centre frame."""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "PIPELINE" / "twod"))
sys.path.insert(0, str(HERE))
import skia  # noqa: E402

import flat  # noqa: E402
import kit  # noqa: E402
from beats import B, TIMING  # noqa: E402
from flat import CAST, Light, Puppet, blob, cel, glow, hexc, paint, poly_path  # noqa: E402
from kit import H, W, blink, span  # noqa: E402

CAM = kit.Cam1P(vx=W / 2, vy=860, cam_h=150, f=887)
TEEN = Puppet(CAST["mascot"], "teen")
POS = (0, 150)
UNIT = 0.2125
SUN = "#ffe3b3"


def _quad(c, pts3, color, alpha=None):
    c.drawPath(poly_path(CAM.quad(pts3)), paint(color, alpha))


def draw_room(c, t):
    X0, X1, Hh, ZB, ZN = -300, 300, 280, 700, 105
    _quad(c, [(X0, Hh, ZN), (X1, Hh, ZN), (X1, Hh, ZB), (X0, Hh, ZB)], "#d9dfe3")
    _quad(c, [(X0, 0, ZN), (X0, Hh, ZN), (X0, Hh, ZB), (X0, 0, ZB)], "#a9c4cf")
    _quad(c, [(X1, 0, ZN), (X1, Hh, ZN), (X1, Hh, ZB), (X1, 0, ZB)], "#a3bdc8")
    _quad(c, [(X0, 0, ZB), (X1, 0, ZB), (X1, Hh, ZB), (X0, Hh, ZB)], "#b8d0d9")
    _quad(c, [(X0, 0, ZN), (X1, 0, ZN), (X1, 0, ZB), (X0, 0, ZB)], "#c9a27a")
    for i in range(-14, 15):
        a, b = CAM.project(i * 22, 0, ZN)[:2], CAM.project(i * 22, 0, ZB)[:2]
        c.drawLine(*a, *b, paint("#b48d66", stroke=3))
    _quad(c, [(X0, 0, ZB), (X1, 0, ZB), (X1, 10, ZB), (X0, 10, ZB)], "#f1efe9")
    # big window (daylight) on the back wall, left
    q = CAM.quad([(-250, 245, ZB), (-40, 245, ZB), (-40, 80, ZB), (-250, 80, ZB)])
    l, tp = q[0]
    r, b = q[2]
    flat.linear_grad(c, (l, tp, r, b), ["#8fc7ef", "#cfe9f7"])
    for cx, cy, rr in ((0.3, 0.45, 26), (0.45, 0.4, 34), (0.62, 0.47, 24)):  # drifting cloud
        c.drawCircle(l + (r - l) * (cx + 0.02 * math.sin(t * 0.6)), tp + (b - tp) * cy, rr, paint("#ffffff", 0.9))
    c.drawRect(skia.Rect.MakeLTRB(l, tp, r, b), paint("#f6f3ee", stroke=12))
    c.drawLine((l + r) / 2, tp, (l + r) / 2, b, paint("#f6f3ee", stroke=8))
    # poster + shelf, back wall right
    pq = CAM.quad([(40, 230, ZB), (150, 230, ZB), (150, 110, ZB), (40, 110, ZB)])
    c.drawRect(skia.Rect.MakeLTRB(*pq[0], *pq[2]), paint("#f2b134"))
    pl, pt, pr, pb = pq[0][0], pq[0][1], pq[2][0], pq[2][1]
    c.drawCircle((pl + pr) / 2, (pt + pb) / 2 - 10, (pr - pl) * 0.28, paint("#d0312d"))
    c.drawRect(skia.Rect.MakeLTRB(pl + 12, pb - 30, pr - 12, pb - 18), paint("#1d2b3a"))
    sq = CAM.quad([(180, 150, ZB), (285, 150, ZB), (285, 140, ZB), (180, 140, ZB)])
    c.drawRect(skia.Rect.MakeLTRB(*sq[0], *sq[2]), paint("#6b4a32"))
    for k, col in enumerate(("#3f6fb5", "#e2574c", "#55a868", "#d9a43b")):
        bx = sq[0][0] + 8 + k * 22
        c.drawRect(skia.Rect.MakeLTRB(bx, sq[0][1] - 40 + (k % 2) * 6, bx + 16, sq[0][1]), paint(col))
    # rug
    rug = [CAM.project(x, 0, z)[:2] for x, z in ((-180, 260), (180, 260), (230, 470), (-230, 470))]
    c.drawPath(blob(rug, 0.6), paint("#e9e2d2"))
    c.drawPath(blob(rug, 0.6), paint("#d0312d", 0.5, stroke=8))
    # daylight beam from the window
    flat.light_cone(c, ((l + r) / 2, (tp + b) / 2), (260, 1700), (760, 1700), SUN, 0.16)


def teen_pose(t):
    pose = dict(breathe=t, eye_open=blink(t, seed=5), mouth="grin", pupil=(0.0, 0.05), turn=0.12,
                arm_l=(9, 12), arm_r=(9, 12), brow=(0.2, 0.0), head_tilt=-2)
    pose["talk"] = TIMING.mouth(t, "teen")
    # "Yo!" wave (right arm up, waggle)
    w = span(t, B["yo"] - 0.25, B["yo"] - 0.05, "back") * (1 - span(t, B["mascot"] - 0.1, B["mascot"] + 0.2))
    if w > 0:
        waggle = 25 * math.sin(t * 2 * math.pi * 3.2)
        pose["arm_r"] = (kit.lerp(9, 150, w), kit.lerp(12, 20 + waggle, w))
        pose["brow"] = (0.6, 0.0)
    # thumb to chest on "mascot"
    m = span(t, B["mascot"] - 0.1, B["mascot"] + 0.15) * (1 - span(t, B["studio"] + 0.1, B["studio"] + 0.35))
    if m > 0:
        pose["arm_l"] = (kit.lerp(9, 22, m), kit.lerp(12, 135, m))
    # turn on "same studio" (shows the backwards brim), tap the cap on "cap"
    trn = span(t, B["studio"] - 0.2, B["studio"] + 0.1) * (1 - span(t, B["cap"] + 0.4, B["cap"] + 0.7))
    pose["turn"] = kit.lerp(0.12, 0.55, trn)
    pose["pupil"] = (kit.lerp(0.0, -0.5, trn), 0.05)
    cp = span(t, B["cap"] - 0.3, B["cap"] - 0.05, "out") * (1 - span(t, B["cap"] + 0.45, B["cap"] + 0.7))
    if cp > 0:
        pose["arm_r"] = (kit.lerp(9, 160, cp), kit.lerp(12, 311, cp))
        pose["head_tilt"] = kit.lerp(-2, 5, cp)
    # wink at the end
    if t >= B["wink"]:
        u = span(t, B["wink"], B["wink"] + 0.25) * (1 - span(t, B["wink"] + 0.45, B["wink"] + 0.6))
        pose["eye_open"] = 1.0
        pose["lid"] = 0.0
        pose["mouth"] = "smirk"
        pose["_wink"] = u
    # landing squash
    land = span(t, B["land"] - 0.02, B["land"] + 0.06, "out") * (1 - span(t, B["land"] + 0.1, B["land"] + 0.4))
    pose["crouch"] = 0.32 * land
    if t < B["land"]:
        pose.update(arm_l=(30, 40), arm_r=(30, 40), mouth="o", brow=(0.8, 0))
    return pose


def shot_studio(c, t):
    c.clear(hexc("#000000"))
    draw_room(c, t)
    x, z = POS
    sx, sy, s = CAM.project(x, 0, z)
    drop = 0.0 if t >= B["land"] else -480 * (1 - kit.ease_in(t / B["land"], 2))
    pose = teen_pose(t)
    wink = pose.pop("_wink", 0.0)
    light = Light(dir=(-0.7, -0.55), shadow_px=15, rim=SUN, rim_alpha=0.8, rim_px=5)
    TEEN.draw(c, sx, sy + drop, s * UNIT, pose, light=light, shadow=False)
    sc = s * UNIT
    flat.floor_shadow(c, sx, sy, 120 * sc * (1 + drop / 1400), 18 * sc, 0.28 * (1 + drop / 1400))
    if wink > 0.05:  # close his right eye (screen-left) with a skin lid + lash line
        hx, hy = TEEN.head_pos(sx, sy, sc)
        ex = sx + (pose["turn"] * 10 + pose["turn"] * 38 * 1.04 - 42 * 1.04 * (1 - abs(pose["turn"]) * 0.12)) * sc
        ey = sy + (TEEN.HEAD_Y * 1.03 - 4 + 0) * sc + (hy - hy)
        r = 30 * sc
        c.drawOval(skia.Rect.MakeLTRB(ex - r * 0.75, ey - r * 0.95, ex + r * 0.75, ey + r * 0.95 * (2 * wink - 1)),
                   paint(TEEN.s.skin))
        arc = skia.Path()
        arc.moveTo(ex - r * 0.7, ey + r * 0.95 * (2 * wink - 1))
        arc.quadTo(ex, ey + r * 0.95 * (2 * wink - 1) + 8 * sc, ex + r * 0.7, ey + r * 0.95 * (2 * wink - 1))
        c.drawPath(arc, paint("#2a1d18", stroke=5 * sc))
    flat.vignette(c, W, H, 0.3)


SHOTS = dict(studio=shot_studio)
