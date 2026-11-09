"""VIDEO_003 - GOING DOWN, Part 1: 2D shots (Skia), drawn natively at 1080x1920.

Every shot is shot_NAME(canvas, t) with t = absolute video time (the EDL uses offset = cut time),
so poses, doors and lights key off the same beats as the edit (beats.py / word timing).

Lighting states (see edit_video003): FLUO -> DIM (panels die at S21) -> RED (from the drop, S25);
the lobby shots add warm LOBBY light.
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
from flat import (CAST, Light, Puppet, Style, blob, capsule, cel, ellipse_path, glow, hexc, lerp_col, limb_path,  # noqa: E402
                  paint, poly_path, rrect_path, shade, tint, with_alpha)
from kit import H, W, blink, clamp, lerp, span, wiggle  # noqa: E402

# ============================================================================ cast
YOU = Puppet(CAST["mascot"], "you")
GUS = Puppet(Style(skin="#dcae8e", hair="#c9c6c0", hair_style="short", shirt="#7f8a86", shirt_detail="#5d6764",
                   pants="#7f8a86", shoes="#3a332d", eyes="#4a3a2c", glasses=True, beard=True, height=0.97, width=1.05),
             "gus")
REYES = Puppet(Style(skin="#c68a62", hair="#1d1612", hair_style="short", shirt="#23324f", shirt_detail="#d9b45a",
                     pants="#23324f", shoes="#151515", eyes="#2a1d14"), "reyes")
UNIT = 0.2125  # puppet units -> cm
RAIN = "#a8231d"
STEEL, STEEL_D, STEEL_L = "#7d8790", "#5d666e", "#a3adb5"
FLUO_C, RED_C, WARM = "#dff3f6", "#ff3b2f", "#ffcf8a"
SKIN = CAST["mascot"].skin

# ============================================================================ light state


def panels_on(t):
    """How many of the 6 ceiling panels are lit."""
    t_start = start("S21") + 0.35
    if t < t_start:
        return 6
    if t >= B["drop"]:
        return 0
    u = span(t, t_start, B["lights_die"] + 0.25, "linear")
    return max(1, 6 - int(u * 5.99))


def state(t):
    if t >= B["drop"]:
        return "RED"
    if panels_on(t) < 6:
        return "DIM"
    return "FLUO"


def light_for(st, warm=False):
    if st == "RED":
        return Light(dir=(-0.4, -0.85), shadow_px=20, rim=RED_C, rim_alpha=0.9, rim_px=6)
    if warm:
        return Light(dir=(0.6, -0.6), shadow_px=16, rim=WARM, rim_alpha=0.85, rim_px=6)
    if st == "DIM":
        return Light(dir=(0.0, -1.0), shadow_px=20, rim="#9fb3b8", rim_alpha=0.4, rim_px=4)
    return Light(dir=(-0.2, -1.0), shadow_px=14, rim=FLUO_C, rim_alpha=0.55, rim_px=4)


def grade(c, t, st=None, warm=0.0):
    """Global lighting pass for a shot."""
    st = st or state(t)
    full = skia.Rect.MakeWH(W, H)
    if st == "FLUO":
        c.drawRect(full, paint("#cfe8ee", 0.10, blend=skia.BlendMode.kMultiply))
    elif st == "DIM":
        n = panels_on(t)
        dark = 0.15 + (6 - n) * 0.05
        fl = 1 - kit.flicker(t, 1.0, 0.9, 7, rate=14)
        c.drawRect(full, paint("#1b2428", min(0.6, dark + fl * 0.3), blend=skia.BlendMode.kMultiply))
        c.drawRect(full, paint("#000000", dark * 0.25))
    elif st == "RED":
        c.drawRect(full, paint("#e0453a", 0.85, blend=skia.BlendMode.kMultiply))
        c.drawRect(full, paint("#2a0503", 0.35))
    if warm > 0:
        c.drawRect(full, paint("#ffb766", 0.18 * warm, blend=skia.BlendMode.kOverlay))
    flat.vignette(c, W, H, 0.5 if st != "FLUO" else 0.38)


# ============================================================================ poses for YOU


def you_pose(t):
    eo = blink(t, seed=11)
    P = dict(breathe=t, eye_open=eo, lid=0.42, mouth="flat", pupil=(0.05, 0.35), brow=(-0.1, 0.0), turn=0.08,
             arm_l=(10, 14), arm_r=(9, 12), head_tilt=-2, hold_l=trash_bag)
    if t >= start("S03") - 0.1:  # eyes drift to the panel, brows knit
        u = span(t, start("S03"), start("S03") + 0.5)
        P.update(pupil=(lerp(0.05, 0.85, u), 0.0), lid=lerp(0.42, 0.18, u), brow=(-0.1, 0.5 * u), turn=lerp(0.08, 0.25, u))
    if t >= B["doors13"]:  # alert
        P.update(lid=0.0, brow=(0.5, 0.35), pupil=(0.0, -0.05), mouth="neutral", turn=0.0)
    if t >= B["gus"]:  # flinch
        u = span(t, B["gus"], B["gus"] + 0.2, "out")
        P.update(brow=(0.9, 0.6), mouth="o", pupil=(lerp(0, 0.7, u), 0.0), turn=lerp(0, 0.35, u),
                 crouch=0.08 * math.sin(math.pi * span(t, B["gus"], B["gus"] + 0.5, "linear")))
    if t >= start("S10"):  # listening, worried
        P.update(brow=(0.35, 0.6), mouth="flat", pupil=(0.45, 0.0), turn=0.25)
    if t >= start("S16"):  # stare at your shoes
        P.update(pupil=(0.0, 1.0), lid=0.45, brow=(0.2, 0.8), mouth="flat", turn=0.0, head_tilt=4)
    if t >= B["inside"]:  # she's inside
        P.update(pupil=(-0.6, 0.0), lid=0.0, brow=(0.8, 0.8), mouth="o", head_tilt=0)
    if t >= B["mom"]:  # mom's voice - eyes well up
        P.update(pupil=(-0.3, 0.1), lid=0.1, brow=(0.6, 1.0), mouth="frown", eye_open=max(eo, 0.85))
    if t >= B["drop"]:
        P.update(brow=(1.0, 0.8), mouth="o", lid=0.0, pupil=(0.0, -0.3))
    if t >= start("S28"):  # looking at your palm
        P.update(pupil=(0.0, 0.8), mouth="flat", brow=(0.4, 0.9))
    if t >= B["wet_hand"]:  # terrified
        P.update(brow=(1.0, 0.9), mouth="o", talk=0.35, lid=0.0, eye_open=1.0, pupil=(0.55, 0.15), turn=0.3)
    return P


def trash_bag(c, x, y, ang):
    bag = blob([(x - 46, y + 10), (x - 8, y - 6), (x + 30, y + 10), (x + 70, y + 120), (x + 30, y + 190),
                (x - 50, y + 185), (x - 82, y + 110)], 0.45)
    cel(c, bag, "#1c1f24", Light(dir=(-0.3, -1), shadow_px=22, rim="#8fa3ad", rim_alpha=0.5, rim_px=5))
    c.drawPath(blob([(x - 18, y - 4), (x + 4, y - 18), (x + 18, y + 2), (x, y + 16)], 0.4), paint("#2b2f36"))
    c.drawLine(x - 30, y + 70, x - 10, y + 150, paint("#ffffff", 0.08, stroke=6))


# ============================================================================ props / creatures


def drips(c, x, y, t, n=5, spread=40, seed=0, length=160, alpha=0.75):
    for i in range(n):
        ph = ((t * (1.6 + 0.3 * (i % 3)) + i * 0.37 + seed * 0.13) % 1.0)
        dx = (i - n / 2) * spread / n + math.sin(i * 7.1 + seed) * 6
        yy = y + ph * length
        c.drawOval(skia.Rect.MakeLTRB(x + dx - 3, yy - 6, x + dx + 3, yy + 5), paint("#cfe6ff", alpha * (1 - ph)))


def rider_back(c, x, feet_y, h, t, st, turn=0.0, point=0.0, hood_touch=None):
    """Very tall woman in a red raincoat seen from behind (hood up). h = height in px."""
    L = light_for(st)
    w_sh, w_hem = 0.30 * h, 0.44 * h
    top = feet_y - h
    hood_cy = top + 0.085 * h
    # legs + boots
    for s in (-1, 1):
        c.drawPath(capsule((x + s * 0.06 * h, feet_y - 0.2 * h), (x + s * 0.065 * h, feet_y - 0.02 * h), 0.06 * h),
                   paint("#22262b"))
    coat = blob([(x - w_sh / 2, top + 0.2 * h), (x - w_sh * 0.35, top + 0.14 * h), (x + w_sh * 0.35, top + 0.14 * h),
                 (x + w_sh / 2, top + 0.2 * h), (x + w_hem / 2, feet_y - 0.17 * h), (x, feet_y - 0.15 * h),
                 (x - w_hem / 2, feet_y - 0.17 * h)], 0.3)
    cel(c, coat, RAIN, L, k=2.0)
    c.drawLine(x, top + 0.2 * h, x, feet_y - 0.16 * h, paint(shade(hexc(RAIN), 0.7), stroke=0.012 * h))
    c.drawLine(x - w_sh * 0.55, top + 0.5 * h, x + w_sh * 0.55, top + 0.5 * h, paint(shade(hexc(RAIN), 0.65), stroke=0.02 * h))
    # sleeves (long arms)
    for s in (-1, 1):
        if s == 1 and point > 0:
            continue
        sl = capsule((x + s * w_sh * 0.48, top + 0.22 * h), (x + s * w_sh * 0.58, top + 0.62 * h), 0.085 * h)
        cel(c, sl, shade(hexc(RAIN), 0.92), L)
        c.drawPath(capsule((x + s * w_sh * 0.58, top + 0.64 * h), (x + s * w_sh * 0.6, top + 0.74 * h), 0.035 * h),
                   paint("#9aa39e"))
    if point > 0:  # long grey hand reaching to the panel (screen right) without turning
        sx, sy = x + w_sh * 0.48, top + 0.24 * h
        ex = sx + lerp(0.1, 0.55, point) * h
        ey = sy + lerp(0.38, 0.12, point) * h
        cel(c, capsule((sx, sy), (ex, ey), 0.08 * h), shade(hexc(RAIN), 0.92), L)
        fx, fy = ex + 0.16 * h * point, ey - 0.02 * h
        c.drawPath(capsule((ex, ey), (fx, fy), 0.03 * h), paint("#9aa39e"))
        for k in range(3):  # long fingers
            c.drawPath(capsule((fx, fy), (fx + 0.07 * h, fy - 0.02 * h + k * 0.018 * h), 0.009 * h), paint("#8d9691"))
    # hood
    hood = blob([(x - 0.13 * h, hood_cy + 0.06 * h), (x - 0.12 * h, hood_cy - 0.05 * h), (x - turn * 0.03 * h, hood_cy - 0.1 * h),
                 (x + 0.12 * h, hood_cy - 0.05 * h), (x + 0.13 * h, hood_cy + 0.06 * h), (x, hood_cy + 0.11 * h)], 0.45)
    cel(c, hood, RAIN, L, k=1.6)
    if turn > 0:  # hood edge rotating into view - a sliver of darkness where a face should be
        c.drawPath(blob([(x + 0.13 * h * turn, hood_cy - 0.05 * h), (x + 0.15 * h * turn + 4, hood_cy + 0.03 * h),
                         (x + 0.12 * h * turn, hood_cy + 0.09 * h), (x + 0.08 * h * turn, hood_cy + 0.02 * h)], 0.4),
                   paint("#050505"))
    c.drawPath(blob([(x - 0.04 * h, hood_cy - 0.07 * h), (x + 0.05 * h, hood_cy - 0.08 * h)], close=False),
               paint(tint(hexc(RAIN), 1.4), 0.4, stroke=0.012 * h))
    drips(c, x - w_hem * 0.3, feet_y - 0.17 * h, t, n=4, spread=w_hem * 0.6, seed=3, length=0.15 * h)
    flat.floor_shadow(c, x, feet_y, w_hem * 0.6, 0.03 * h, 0.35)


def name_tag(c, x, y, s):
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 30 * s, y - 13 * s, 60 * s, 26 * s), 4 * s, 4 * s, paint("#f2efe6"))
    f = kit.font(17 * s, "Black")
    c.drawString("GUS", x - f.measureText("GUS") / 2, y + 6 * s, f, paint("#2c3a6b"))


def bucket(c, x, y, s, L):
    b = poly_path([(x - 58 * s, y - 95 * s), (x + 58 * s, y - 95 * s), (x + 46 * s, y), (x - 46 * s, y)])
    cel(c, b, "#d6b13a", L, k=0.8 * s)
    c.drawOval(skia.Rect.MakeLTRB(x - 58 * s, y - 104 * s, x + 58 * s, y - 86 * s), paint("#a8892c"))


def mop(c, x, y, s, L):
    c.drawLine(x, y - 330 * s, x + 18 * s, y - 40 * s, paint("#8a6a45", stroke=9 * s))
    head = blob([(x - 10 * s, y - 50 * s), (x + 46 * s, y - 46 * s), (x + 58 * s, y), (x - 24 * s, y)], 0.4)
    c.drawPath(head, paint("#cfc8b8"))


def gus_sitting(c, x, feet_y, s, t, st, pose=None):
    L = light_for(st)
    bucket(c, x + 6 * s / UNIT * UNIT, feet_y, s / 0.6, L)
    P = dict(breathe=t, eye_open=blink(t, seed=21), crouch=0.62, mouth="flat", lid=0.35, pupil=(-0.4, 0.1),
             arm_l=(18, 70), arm_r=(18, 70), turn=-0.25, brow=(0.0, 0.2))
    if pose:
        P.update(pose)
    GUS.draw(c, x, feet_y, s, P, light=L, shadow=False)
    hx, hy = GUS.head_pos(x, feet_y, s, P)
    name_tag(c, x - 34 * s / 0.6 * 0.6 * 1.7, hy + 260 * s, s * 1.6)


# ============================================================================ elevator interior (looking at the back wall)
CAM = kit.Cam1P(vx=W / 2, vy=820, cam_h=150, f=760)
X0, X1, HH, ZN, ZB = -110, 110, 240, 62, 260


def _q(c, pts, col, a=None):
    c.drawPath(poly_path(CAM.quad(pts)), paint(col, a))


def car_interior(c, t, st, show_mirror_refl=True):
    n = panels_on(t)
    # walls / floor / ceiling
    _q(c, [(X0, HH, ZN), (X1, HH, ZN), (X1, HH, ZB), (X0, HH, ZB)], "#3d454c")
    _q(c, [(X0, 0, ZN), (X0, HH, ZN), (X0, HH, ZB), (X0, 0, ZB)], STEEL_D)
    _q(c, [(X1, 0, ZN), (X1, HH, ZN), (X1, HH, ZB), (X1, 0, ZB)], "#646d75")
    _q(c, [(X0, 0, ZB), (X1, 0, ZB), (X1, HH, ZB), (X0, HH, ZB)], STEEL)
    _q(c, [(X0, 0, ZN), (X1, 0, ZN), (X1, 0, ZB), (X0, 0, ZB)], "#2e2b29")
    # brushed panel seams on the side walls
    for z in (110, 160, 210):
        for xw in (X0, X1):
            a, b = CAM.project(xw, 0, z)[:2], CAM.project(xw, HH, z)[:2]
            c.drawLine(*a, *b, paint("#000000", 0.18, stroke=3))
    # floor tiles
    for z in (100, 140, 180, 220):
        a, b = CAM.project(X0, 0, z)[:2], CAM.project(X1, 0, z)[:2]
        c.drawLine(*a, *b, paint("#000000", 0.25, stroke=2))
    # mirror on the back wall
    mq = CAM.quad([(-92, 225, ZB), (92, 225, ZB), (92, 92, ZB), (-92, 92, ZB)])
    mr = skia.Rect.MakeLTRB(*mq[0], *mq[2])
    flat.linear_grad(c, (mr.left(), mr.top(), mr.right(), mr.bottom()), ["#9fb3bd", "#6f828c"])
    c.drawLine(mr.left() + 30, mr.top() + 20, mr.left() + 90, mr.bottom() - 30, paint("#ffffff", 0.12, stroke=14))
    c.drawRect(mr, paint("#c9d1d6", stroke=6))
    # handrail
    a, b = CAM.project(X0 + 8, 92, ZB - 6)[:2], CAM.project(X1 - 8, 92, ZB - 6)[:2]
    c.drawLine(*a, *b, paint("#c9d1d6", stroke=7))
    # ceiling light panels (die from the back first)
    order = [(z, x) for z in (215, 160, 105) for x in (-1, 1)]
    for i, (z, sx) in enumerate(order):
        on = i >= 6 - n
        q = CAM.quad([(sx * 12, HH - 0.5, z - 22), (sx * 70, HH - 0.5, z - 22), (sx * 70, HH - 0.5, z + 22), (sx * 12, HH - 0.5, z + 22)])
        c.drawPath(poly_path(q), paint(FLUO_C if on else "#22292e"))
        if on:
            cx = sum(p[0] for p in q) / 4
            cy = sum(p[1] for p in q) / 4
            glow(c, cx, cy + 40, 260, FLUO_C, 0.10)
    if st == "RED":  # emergency lamp on the back wall
        ex, ey, _ = CAM.project(0, 232, ZB)
        c.drawRoundRect(skia.Rect.MakeLTRB(ex - 40, ey - 12, ex + 40, ey + 12), 6, 6, paint("#ff5a4a"))
        glow(c, ex, ey, 520, RED_C, 0.5)
    # button panel on the right wall near the doors + small floor display
    pq = CAM.quad([(X1 - 0.5, 165, 74), (X1 - 0.5, 165, 100), (X1 - 0.5, 95, 100), (X1 - 0.5, 95, 74)])
    c.drawPath(poly_path(pq), paint("#b9c2c8"))
    for k in range(6):
        bx, by, s = CAM.project(X1 - 1, 155 - k * 11, 87)
        lit = k == 2 and t < B["drop"]
        c.drawCircle(bx, by, 2.3 * s, paint("#ffb23e" if lit else "#7b858c"))
        if lit:
            glow(c, bx, by, 40, "#ffb23e", 0.5)


def you_in_car(c, t, st, x=-25, z=150):
    sx, sy, s = CAM.project(x, 0, z)
    YOU.draw(c, sx, sy, s * UNIT, you_pose(t), light=light_for(st))
    return sx, sy, s


# ============================================================================ doors wall (looking at the doors from inside)
DL, DR, DT, DB = 250, 830, 560, 1600


def door_open_amount(t):
    """0 closed .. 1 open, from the scene being shown."""
    def opening(t0, t_close=None, dur=0.55):
        o = span(t, t0, t0 + dur, "inout")
        if t_close is not None:
            o *= 1 - span(t, t_close, t_close + 0.35, "in_")
        return o
    if t < start("S16") - 0.2:
        return opening(B["doors13"] - 0.05, word("S08", "cut") - 0.1)
    if t < B["bell"] - 0.5:
        return opening(start("S16") - 0.05, end("S18"))
    return opening(B["bell"] + 0.25, None, 0.7)


def doors_wall(c, t, st, inside_fn, floor_txt):
    o = door_open_amount(t)
    flat.linear_grad(c, (0, 0, W, H), ["#6b747c", "#4d555c"])
    for x in (120, 960):  # wall seams
        c.drawLine(x, 0, x, H, paint("#000000", 0.2, stroke=4))
    # opening
    op = skia.Rect.MakeLTRB(DL, DT, DR, DB)
    c.save()
    c.clipRect(op)
    inside_fn(c, t)
    c.restore()
    # door panels (slide outward)
    half = (DR - DL) / 2
    for s in (-1, 1):
        w = half * (1 - o)
        if w <= 1:
            continue
        r = skia.Rect.MakeLTRB(DL, DT, DL + w, DB) if s < 0 else skia.Rect.MakeLTRB(DR - w, DT, DR, DB)
        c.drawRect(r, paint(STEEL_L))
        c.drawRect(r, paint("#000000", 0.15, stroke=4))
        flat.linear_grad(c, (r.left(), r.top(), r.right(), r.bottom()), [with_alpha(hexc("#ffffff"), 0.18),
                                                                          with_alpha(hexc("#ffffff"), 0.0)], vertical=False)
    c.drawRect(op, paint("#3a4249", stroke=18))
    # floor indicator + bell above the doors
    c.drawRoundRect(skia.Rect.MakeLTRB(430, 410, 650, 500), 12, 12, paint("#121417"))
    kit.draw_text(c, floor_txt(t), 540, 478, 64, color="#ff9a3c", weight="Black")
    c.drawCircle(720, 455, 26, paint("#c8a14a"))
    c.drawCircle(712, 446, 8, paint("#f1d48a", 0.8))
    # car floor in front
    flat.linear_grad(c, (0, DB, W, H), ["#2e2b29", "#151413"])
    c.drawRect(skia.Rect.MakeLTRB(DL - 20, DB - 6, DR + 20, DB + 12), paint("#9aa3aa"))


def hallway(c, t, wall="#2a2622", carpet="#4a2420", lights=0.15, doors_open=True, exit_sign=False):
    vx, vy = 540, 960
    c.drawRect(skia.Rect.MakeLTRB(DL, DT, DR, DB), paint(shade(hexc(wall), 0.7)))
    end = skia.Rect.MakeLTRB(vx - 60, vy - 110, vx + 60, vy + 70)
    c.drawPath(poly_path([(DL, DB), (DR, DB), (end.right(), end.bottom()), (end.left(), end.bottom())]), paint(carpet))
    c.drawPath(poly_path([(DL, DT), (DR, DT), (end.right(), end.top()), (end.left(), end.top())]), paint(shade(hexc(wall), 0.6)))
    c.drawPath(poly_path([(DL, DT), (end.left(), end.top()), (end.left(), end.bottom()), (DL, DB)]), paint(wall))
    c.drawPath(poly_path([(DR, DT), (end.right(), end.top()), (end.right(), end.bottom()), (DR, DB)]), paint(shade(hexc(wall), 0.85)))
    c.drawRect(end, paint(shade(hexc(wall), 1.1)))
    for k, u in enumerate((0.15, 0.42, 0.62, 0.76)):  # doors along both walls
        for s in (-1, 1):
            xa = lerp(DL if s < 0 else DR, end.left() if s < 0 else end.right(), u)
            xb = lerp(DL if s < 0 else DR, end.left() if s < 0 else end.right(), u + 0.1)
            ya_t, ya_b = lerp(DT + 120, end.top() + 30, u), lerp(DB, end.bottom(), u)
            yb_t, yb_b = lerp(DT + 120, end.top() + 30, u + 0.1), lerp(DB, end.bottom(), u + 0.1)
            col = "#050505" if doors_open else "#5b4030"
            c.drawPath(poly_path([(xa, ya_t), (xb, yb_t), (xb, yb_b), (xa, ya_b)]), paint(col))
    for u in (0.3, 0.7):
        cy = lerp(DT, end.top(), u)
        glow(c, vx, cy + 20, 160 * (1 - u * 0.6), "#d8c79a", lights * (0.6 + 0.4 * kit.flicker(t, 1.0, 0.6, int(u * 10))))
    if exit_sign:
        on = kit.flicker(t, 1.0, 0.8, 5, rate=11) > 0.55
        c.drawRect(skia.Rect.MakeLTRB(vx - 34, end.top() - 30, vx + 34, end.top() - 8), paint("#1f9a4a" if on else "#0d3b1d"))
        if on:
            glow(c, vx, end.top() - 20, 90, "#3dff7a", 0.25)
    return end


def inside_13(c, t):
    end = hallway(c, t)
    if t >= start("S07") - 0.15:
        ex = (end.left() + end.right()) / 2
        turn = span(t, start("S08"), word("S08", "cut"), "linear") * 0.8
        rider_back(c, ex, end.bottom() + 40, 330, t, "FLUO", turn=turn)


def floor_txt_13(t):
    if t < B["doors13"]:
        return "14"
    return "13"


def inside_9(c, t):
    hallway(c, t, wall="#8a8170", carpet="#5b5348", lights=0.35, doors_open=False, exit_sign=True)


def floor_txt_9(t):
    return "9"


def lobby(c, t, dim=0.0):
    # warm lobby: marble floor, back wall with clock, glass street doors with daylight
    c.drawRect(skia.Rect.MakeLTRB(DL, DT, DR, DB), paint("#c9a77c"))
    flat.linear_grad(c, (DL, 1180, DR, DB), ["#e9dcc6", "#b9a58a"])
    for k in range(6):
        y = 1180 + k * 70
        c.drawLine(DL, y, DR, y, paint("#8a7559", 0.25, stroke=2))
    gd = skia.Rect.MakeLTRB(420, 760, 660, 1180)
    flat.linear_grad(c, (gd.left(), gd.top(), gd.right(), gd.bottom()), ["#eaf6ff", "#b9dcf2"])
    glow(c, 540, 970, 300, "#ffffff", 0.35)
    c.drawRect(gd, paint("#3b2f22", stroke=10))
    c.drawLine(540, 760, 540, 1180, paint("#3b2f22", stroke=8))
    # wall clock 3:07
    cx, cy = 340, 700
    c.drawCircle(cx, cy, 52, paint("#f7f1e6"))
    c.drawCircle(cx, cy, 52, paint("#3b2f22", stroke=7))
    for k, (ang, ln) in enumerate(((3 / 12 * 360 + 7 / 60 * 30, 26), (7 / 60 * 360, 40))):
        a = math.radians(ang - 90)
        c.drawLine(cx, cy, cx + math.cos(a) * ln, cy + math.sin(a) * ln, paint("#1a1a1a", stroke=6 - k * 2))
    # desk
    c.drawRect(skia.Rect.MakeLTRB(640, 1100, 830, 1240), paint("#5b3d28"))
    c.drawRect(skia.Rect.MakeLTRB(630, 1090, 830, 1110), paint("#7a553a"))
    # Mr. Reyes waving
    wave = math.sin(t * 2 * math.pi * 1.6)
    P = dict(breathe=t, eye_open=1.0, mouth="smile", arm_r=(150, 30 + 20 * wave), turn=0.15, pupil=(0.0, 0.0),
             brow=(0.1, 0.0))
    REYES.draw(c, 470, 1420, 0.62, P, light=Light(dir=(0.5, -0.8), rim=WARM, rim_alpha=0.6))
    glow(c, 540, 900, 600, WARM, 0.18)
    if dim > 0:
        c.drawRect(skia.Rect.MakeLTRB(DL, DT, DR, DB), paint("#000000", dim))


def floor_txt_lobby(t):
    return "L"


# ============================================================================ SHOTS


def shot_panel_cu(c, t, thumb=False):
    st = state(t)
    flat.linear_grad(c, (0, 0, W, H), ["#b7c0c6", "#8d979e"])
    for i in range(40):  # brushed steel
        y = i * 48 + (i * 17) % 23
        c.drawLine(0, y, W, y + 6, paint("#ffffff", 0.06, stroke=3))
    c.drawRoundRect(skia.Rect.MakeLTRB(170, 260, 910, 1700), 40, 40, paint("#a7b0b6"))
    c.drawRoundRect(skia.Rect.MakeLTRB(170, 260, 910, 1700), 40, 40, paint("#6c757b", stroke=8))
    floors = [(15, 14), (13, 12), (11, 10), (9, 8)]
    press = span(t, 0.0, 0.08, "linear") * (1 - span(t, 0.12, 0.3))
    lit13 = t >= 0.0 and t < B["drop"]
    for r, row in enumerate(floors):
        for k, n in enumerate(row):
            cx, cy = 380 + k * 320, 520 + r * 330
            pressed = n == 13
            rr = 105
            c.drawCircle(cx, cy + 10, rr + 8, paint("#59626a"))
            col = "#ffb23e" if (pressed and lit13) else "#c9d1d6"
            c.drawCircle(cx, cy + (press * 10 if pressed else 0), rr, paint(col))
            c.drawCircle(cx, cy + (press * 10 if pressed else 0), rr, paint("#6c757b", stroke=6))
            kit.draw_text(c, str(n), cx, cy + 38 + (press * 10 if pressed else 0), 110,
                          color="#5a3a10" if (pressed and lit13) else "#4a5157", weight="Black", max_w=200)
            if pressed and lit13:
                pulse = 0.55 + 0.15 * math.sin(t * 6)
                glow(c, cx, cy, 380, "#ffb23e", pulse * (1.2 if t >= B["thirteen_glow"] - 0.1 and t < start("S05") else 0.8))
    if thumb:
        draw_thumb(c, t)
    grade(c, t, st)


def draw_thumb(c, t):
    tr = wiggle(t, 9, 5, 2)
    tipx, tipy = 380 + tr, 850
    L = light_for("FLUO")
    hand = blob([(tipx + 150, tipy + 260), (tipx + 420, tipy + 180), (tipx + 760, tipy + 420), (tipx + 820, tipy + 1200),
                 (tipx + 300, tipy + 1200), (tipx + 120, tipy + 620)], 0.4)
    cel(c, hand, SKIN, L, k=3)
    th = capsule((tipx + 260, tipy + 420), (tipx + 10, tipy + 20), 130)
    cel(c, th, SKIN, L, k=3)
    c.drawOval(skia.Rect.MakeLTRB(tipx - 40, tipy - 40, tipx + 50, tipy + 40), paint("#f2d0bb", 0.9))
    for k in range(3):  # knuckles of the curled fingers
        c.drawPath(capsule((tipx + 420 + k * 110, tipy + 210 + k * 30), (tipx + 470 + k * 110, tipy + 330 + k * 30), 95),
                   paint(shade(hexc(SKIN), 0.92)))
    f = kit.font(100, "Black")  # marker "2." on the palm
    c.save()
    c.rotate(-14, tipx + 450, tipy + 700)
    c.drawString("2.", tipx + 420, tipy + 760, f, paint("#1a1a22", 0.85))
    c.restore()


def shot_thumb_cu(c, t):
    shot_panel_cu(c, t, thumb=True)


def shot_car_wide(c, t, force_state=None):
    st = force_state or state(t)
    c.clear(hexc("#000000"))
    car_interior(c, t, st)
    if t >= B["gus"]:
        sx, sy, s = CAM.project(72, 0, 228)
        gus_sitting(c, sx, sy, s * UNIT, t, st)
        mop(c, sx + 70, sy, s * UNIT * 1.6, light_for(st))
    if t >= B["inside"]:
        sx, sy, s = CAM.project(-82, 0, 232)
        rider_back(c, sx, sy, (HH - 4) * s * 0.98, t, st)
    you_in_car(c, t, st)
    grade(c, t, st)


def shot_car_red(c, t):
    shot_car_wide(c, t, "RED")
    u = span(t, B["drop"], B["drop"] + 0.6, "linear")
    if u < 1:  # drop streaks
        for i in range(14):
            x = (i * 83) % W
            y = (t * 4200 + i * 230) % H
            c.drawLine(x, y, x, y - 260, paint("#ffb0a8", 0.18 * (1 - u), stroke=5))


def shot_you_cu(c, t):
    st = state(t)
    flat.linear_grad(c, (0, 0, W, H), ["#8f99a1", "#5b646b"])
    mq = skia.Rect.MakeLTRB(-40, 180, 640, 1250)  # mirror edge behind
    flat.linear_grad(c, (mq.left(), mq.top(), mq.right(), mq.bottom()), ["#a9bcc6", "#7f939d"])
    c.drawRect(mq, paint("#c9d1d6", stroke=10))
    for i, z in enumerate((0, 1)):
        c.drawRect(skia.Rect.MakeLTRB(160 + i * 460, 0, 420 + i * 460, 40), paint(FLUO_C if panels_on(t) > 2 + i else "#22292e"))
    P = you_pose(t)
    P["hold_l"] = None
    sc = 2.35
    YOU.draw(c, 540, 2460, sc, P, light=light_for(st), shadow=False)
    hx, hy = YOU.head_pos(540, 2460, sc, P)
    if start("S16") <= t < B["inside"]:  # sweat
        for k in range(2):
            ph = (t * 0.5 + k * 0.5) % 1
            c.drawOval(skia.Rect.MakeLTRB(320 + k * 420, 700 + ph * 140, 334 + k * 420, 726 + ph * 140), paint("#e8f6ff", 0.8 * (1 - ph)))
    if B["mom"] <= t < B["drop"]:  # tears welling
        for s in (-1, 1):
            c.drawOval(skia.Rect.MakeLTRB(540 + s * 98 - 40, 800, 540 + s * 98 + 40, 822), paint("#d9f1ff", 0.55))
    grade(c, t, st)


def mirror_reflection(c, t, st, rect):
    """Inside the mirror: you (front), the trash bag, the EMPTY corner behind-right (Gus never appears)."""
    c.save()
    c.clipRect(rect)
    flat.linear_grad(c, (rect.left(), rect.top(), rect.right(), rect.bottom()), ["#7e8f98", "#56656d"])
    # reflected car back corner (right) - empty
    c.drawLine(rect.right() - 210, rect.top(), rect.right() - 210, rect.bottom(), paint("#3c464d", stroke=8))
    c.drawPath(poly_path([(rect.right() - 210, rect.bottom() - 260), (rect.right(), rect.bottom() - 140),
                          (rect.right(), rect.bottom()), (rect.right() - 210, rect.bottom())]), paint("#33302d"))
    for k, x in enumerate((rect.left() + 140, rect.left() + 480)):
        c.drawRect(skia.Rect.MakeLTRB(x, rect.top(), x + 220, rect.top() + 26), paint(FLUO_C if panels_on(t) > 2 else "#22292e"))
    P = you_pose(t)
    YOU.draw(c, rect.left() + 400, rect.bottom() + 600, 1.25, P, light=light_for(st), shadow=False)
    if t >= B["mirror_test"]:  # a red hood right behind your head
        u = span(t, B["mirror_test"], B["mirror_test"] + 0.8, "out")
        yhx, yhy = YOU.head_pos(rect.left() + 400, rect.bottom() + 600, 1.25, P)
        hx = yhx + lerp(230, 120, u)
        hy = yhy - 150
        hood = blob([(hx - 110, hy + 120), (hx - 95, hy - 40), (hx, hy - 95), (hx + 95, hy - 40), (hx + 110, hy + 120),
                     (hx, hy + 170)], 0.45)
        c.drawPath(hood, paint(RAIN))
        c.drawPath(blob([(hx - 55, hy + 10), (hx + 55, hy + 10), (hx + 45, hy + 140), (hx - 45, hy + 140)], 0.4), paint("#050505"))
        # re-draw your head over the hood so the hood is BEHIND you
        YOU.draw(c, rect.left() + 400, rect.bottom() + 600, 1.25, P, light=light_for(st), shadow=False)
    c.drawLine(rect.left() + 60, rect.top() + 40, rect.left() + 220, rect.bottom() - 60, paint("#ffffff", 0.10, stroke=26))
    c.restore()


def shot_mirror_pov(c, t):
    st = state(t)
    flat.linear_grad(c, (0, 0, W, H), [STEEL, STEEL_D])
    r = skia.Rect.MakeLTRB(90, 260, 990, 1660)
    mirror_reflection(c, t, st, r)
    c.drawRect(r, paint("#c9d1d6", stroke=16))
    c.drawLine(40, 1760, W - 40, 1760, paint("#c9d1d6", stroke=14))  # handrail
    grade(c, t, st)


def shot_doors_13(c, t):
    doors_wall(c, t, state(t), inside_13, floor_txt_13)
    grade(c, t, state(t))


def shot_doors_9(c, t):
    doors_wall(c, t, state(t), inside_9, floor_txt_9)
    grade(c, t, state(t))


def shot_lobby_pov(c, t, dim=0.0):
    st = state(t)
    doors_wall(c, t, st, lambda cc, tt: lobby(cc, tt, dim), floor_txt_lobby)
    # the lobby stays warm; the car around it is red
    grade(c, t, st, warm=1.0)
    glow(c, 540, 1080, 520, WARM, 0.22 * (1 - dim))


def shot_choice_bg(c, t):
    shot_lobby_pov(c, t, dim=0.55)
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", 0.45))


def shot_gus_reveal(c, t):
    st = state(t)
    c.clear(hexc("#000000"))
    car_interior(c, t, st)
    sx, sy, s = CAM.project(55, 0, 215)
    gus_sitting(c, sx, sy, s * UNIT * 1.15, t, st, dict(pupil=(-0.6, 0.0), lid=0.25, mouth="flat", brow=(0.2, 0.1)))
    mop(c, sx + 95, sy, s * UNIT * 1.9, light_for(st))
    # back of YOUR head + shoulder, foreground left (cap backwards: the brim points at us)
    L = light_for(st)
    flin = 18 * math.sin(math.pi * span(t, B["gus"], B["gus"] + 0.4, "linear"))
    hx, hy = 250 - flin, 1260
    sh = blob([(hx - 330, 1920), (hx - 300, hy + 260), (hx - 60, hy + 170), (hx + 230, hy + 240), (hx + 330, 1920)], 0.4)
    cel(c, sh, CAST["mascot"].shirt, L, k=3)
    cel(c, ellipse_path(hx, hy, 175, 195), CAST["mascot"].skin, L, k=3)
    cel(c, blob([(hx - 178, hy - 10), (hx - 150, hy - 150), (hx, hy - 205), (hx + 150, hy - 150), (hx + 178, hy - 10),
                 (hx + 120, hy + 110), (hx - 120, hy + 110)], 0.45), CAST["mascot"].hair, L, k=3)
    cap = blob([(hx - 182, hy - 40), (hx - 160, hy - 160), (hx, hy - 215), (hx + 160, hy - 160), (hx + 182, hy - 40),
                (hx, hy - 60)], 0.45)
    cel(c, cap, CAST["mascot"].cap, L, k=3)
    brim = blob([(hx - 150, hy - 70), (hx + 150, hy - 70), (hx + 120, hy + 10), (hx - 120, hy + 10)], 0.4)
    cel(c, brim, shade(hexc(CAST["mascot"].cap), 0.8), L, k=2)
    c.drawRoundRect(skia.Rect.MakeLTRB(hx - 60, hy - 120, hx + 60, hy - 95), 6, 6, paint(shade(hexc(CAST["mascot"].cap), 0.7)))
    grade(c, t, st)


def shot_gus_cu(c, t):
    st = state(t)
    flat.linear_grad(c, (0, 0, W, H), ["#6f7a82", "#4b545b"])
    c.drawLine(760, 0, 760, H, paint("#3f474d", stroke=10))  # wall corner
    mq = skia.Rect.MakeLTRB(-60, 120, 520, 1100)
    flat.linear_grad(c, (mq.left(), mq.top(), mq.right(), mq.bottom()), ["#a9bcc6", "#7f939d"])  # mirror edge: no Gus in it
    c.drawRect(mq, paint("#c9d1d6", stroke=10))
    talk = TIMING.mouth(t, "gus")
    P = dict(breathe=t, eye_open=blink(t, seed=21), talk=talk, mouth="flat", lid=0.3, pupil=(0.25, 0.05), turn=0.15,
             brow=(0.15, 0.3), arm_l=(10, 14), arm_r=(10, 14))
    if start("S11") <= t < start("S12"):
        P.update(arm_r=(25, 150), hold_r=marker, brow=(0.3, 0.1))
    for n, sid in ((1, "S13"), (2, "S14"), (3, "S15")):
        if start(sid) <= t < end(sid) + 0.6:
            P.update(arm_r=(22, 158), hold_r=fingers(n), pupil=(0.0, 0.0), brow=(0.4, 0.2))
    if t >= B["stay"]:
        P.update(pupil=(-0.8, 0.0), brow=(-0.3, 0.6), lid=0.1, turn=-0.1)
    sc = 2.2
    GUS.draw(c, 520, 2420, sc, P, light=light_for(st), shadow=False)
    name_tag(c, 520 + 95, 1240, 2.6)
    if st == "RED":
        drips(c, 760, 1500, t, n=6, spread=100, seed=4, length=300, alpha=0.4)
    grade(c, t, st)


def marker(c, x, y, ang):
    c.save()
    c.rotate(ang - 90 + 20, x, y)
    c.drawRoundRect(skia.Rect.MakeLTRB(x - 14, y - 110, x + 14, y + 20), 8, 8, paint("#1a1a1f"))
    c.drawRoundRect(skia.Rect.MakeLTRB(x - 10, y - 130, x + 10, y - 104), 5, 5, paint("#f2efe6"))
    c.restore()
    cel(c, ellipse_path(x, y - 6, 26, 28), GUS.s.skin, Light(), k=0.5, rim=False)


def fingers(n):
    def draw(c, x, y, ang):
        for k in range(n):
            dx = (k - (n - 1) / 2) * 16
            c.drawPath(capsule((x + dx, y - 6), (x + dx * 1.3, y - 62), 15), paint(GUS.s.skin))
            c.drawPath(capsule((x + dx, y - 6), (x + dx * 1.3, y - 62), 15), paint(shade(hexc(GUS.s.skin), 0.8), stroke=2))
        c.drawPath(ellipse_path(x, y + 6, 30, 26), paint(GUS.s.skin))
    return draw


RULE_TXT = ["1. NO MIRROR - DOORS OPEN", "2. DON'T PRESS HER FLOOR", "3. OUT ON 2 BELLS ONLY"]


def shot_palm_cu(c, t):
    st = state(t)
    lobbyish = t >= B["bell"]
    if lobbyish:  # out-of-focus lobby + waving doorman behind the palm
        flat.linear_grad(c, (0, 0, W, H), ["#6b4a2c", "#2a1a10"])
        glow(c, 540, 700, 700, WARM, 0.45)
        c.drawPath(ellipse_path(820, 650, 90, 110), paint("#23324f", 0.6, blur=18))
        c.drawPath(ellipse_path(820, 500, 55, 60), paint("#c68a62", 0.6, blur=18))
    else:
        flat.linear_grad(c, (0, 0, W, H), ["#3b4248", "#22272b"])
        c.drawRect(skia.Rect.MakeLTRB(0, 1500, W, H), paint("#2e2b29"))
    L = light_for(st, warm=lobbyish)
    tr = wiggle(t, 10, 5 if t >= start("S14") else 1.5, 9)
    cx, cy = 560 + tr, 1060
    palm = blob([(cx - 330, cy - 210), (cx + 300, cy - 260), (cx + 360, cy + 260), (cx + 120, cy + 560),
                 (cx - 260, cy + 520), (cx - 400, cy + 160)], 0.45)
    for k, (fx, fl) in enumerate(((-250, 300), (-90, 360), (70, 350), (220, 290))):
        cel(c, capsule((cx + fx, cy - 200), (cx + fx * 1.1, cy - 200 - fl), 128), SKIN, L, k=3)
    cel(c, capsule((cx - 330, cy + 160), (cx - 560, cy - 80), 135), SKIN, L, k=3)
    cel(c, palm, SKIN, L, k=3)
    c.drawPath(blob([(cx - 250, cy + 60), (cx - 20, cy - 10), (cx + 220, cy + 40)], close=False), paint("#c48a6a", 0.4, stroke=6))
    c.drawPath(blob([(cx - 200, cy + 250), (cx + 20, cy + 150), (cx + 240, cy + 190)], close=False), paint("#c48a6a", 0.4, stroke=6))
    # handwritten rules (written progressively during S12)
    f = kit.font(56, "Black")
    f.setSkewX(-0.18)
    prog = span(t, start("S12") + 0.15, end("S12") + 0.2, "linear") if t < start("S13") else 1.0
    tot = sum(len(s) for s in RULE_TXT)
    shown = int(prog * tot)
    c.save()
    c.rotate(-7, cx, cy)
    tip = None
    for i, line in enumerate(RULE_TXT):
        n = max(0, min(len(line), shown))
        shown -= len(line)
        if n <= 0:
            continue
        txt = line[:n]
        x0, y0 = cx - 300, cy - 60 + i * 110
        hl = lobbyish and i == 2
        c.drawString(txt, x0, y0, f, paint("#d9201a" if hl else "#16161c", 0.9))
        if i == 1 and t >= start("S14") and not lobbyish:
            u = span(t, start("S14") + 0.2, start("S14") + 0.8, "linear")
            c.drawLine(x0, y0 + 16, x0 + f.measureText(line) * u, y0 + 20, paint("#16161c", 0.9, stroke=8))
        tip = (x0 + f.measureText(txt), y0 - 10)
    c.restore()
    if tip and prog < 1:  # marker in Gus's hand
        mx, my = tip
        c.save()
        c.rotate(-30, mx, my)
        c.drawRoundRect(skia.Rect.MakeLTRB(mx - 18, my - 300, mx + 18, my), 10, 10, paint("#1a1a1f"))
        c.restore()
        cel(c, ellipse_path(mx + 150, my - 260, 70, 85), GUS.s.skin, L, k=2)
    grade(c, t, st, warm=1.0 if lobbyish else 0.0)


def shot_indicator_cu(c, t):
    st = state(t)
    flat.linear_grad(c, (0, 0, W, H), ["#6b747c", "#4d555c"])
    c.drawRoundRect(skia.Rect.MakeLTRB(190, 520, 890, 900), 30, 30, paint("#121417"))
    n = max(10, 12 - int(max(0.0, t - word("S15", "bell")) / 0.6))
    kit.draw_text(c, str(n), 540, 820, 300, color="#ff9a3c", weight="Black")
    glow(c, 540, 710, 380, "#ff9a3c", 0.25)
    c.drawCircle(540, 1220, 160, paint("#c8a14a"))  # brass bell
    c.drawCircle(500, 1170, 50, paint("#f1d48a", 0.8))
    c.drawRect(skia.Rect.MakeLTRB(520, 1360, 560, 1440), paint("#8a6a2e"))
    grade(c, t, st)


def shot_rider_corner(c, t):
    st = state(t)
    flat.linear_grad(c, (0, 0, 540, H), [STEEL, STEEL_D])
    flat.linear_grad(c, (540, 0, W, H), ["#646d75", "#495157"])
    c.drawLine(540, 0, 540, H, paint("#2f363b", stroke=10))
    c.drawRect(skia.Rect.MakeLTRB(0, 1620, W, H), paint("#2e2b29"))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 170), paint("#3d454c"))
    on = panels_on(t)
    for k in range(2):
        c.drawRect(skia.Rect.MakeLTRB(150 + k * 520, 120, 410 + k * 520, 160), paint(FLUO_C if on > 3 + k else "#22292e"))
    c.drawRoundRect(skia.Rect.MakeLTRB(900, 820, 1080, 1260), 14, 14, paint("#b9c2c8"))  # panel at the right edge
    for k in range(4):
        c.drawCircle(990, 900 + k * 100, 30, paint("#ffb23e" if k == 1 else "#7b858c"))
    point = span(t, start("S20") + 0.2, start("S20") + 0.9) if t >= start("S20") else 0.0
    rider_back(c, 470, 1700, 1420, t, st, point=point)
    grade(c, t, st)


def shot_hand_slap(c, t):
    st = state(t)
    flat.linear_grad(c, (0, 0, W, H), ["#b7c0c6", "#8d979e"])
    c.drawRoundRect(skia.Rect.MakeLTRB(120, 300, 960, 1500), 40, 40, paint("#a7b0b6"))
    for k, n in enumerate((14, 13, 12)):
        c.drawCircle(540, 520 + k * 330, 105, paint("#ffb23e" if n == 13 else "#c9d1d6"))
        kit.draw_text(c, str(n), 540, 560 + k * 330, 110, color="#4a5157", weight="Black", max_w=200)
    t0 = B["slap"] + 0.15
    u = span(t, t0, t0 + 0.12, "out")
    L = light_for(st)
    # your hand being knocked away (moves left/down)
    yx, yy = lerp(700, 220, u), lerp(900, 1500, u)
    cel(c, blob([(yx - 160, yy), (yx + 40, yy - 120), (yx + 260, yy + 60), (yx + 120, yy + 420), (yx - 120, yy + 380)], 0.45),
        SKIN, L, k=3)
    # Gus's hand comes in from the right, wet sleeve
    gx = lerp(1500, 760, span(t, t0 - 0.2, t0, "in_"))
    sl = blob([(gx + 100, 700), (gx + 900, 650), (gx + 900, 1150), (gx + 100, 1100)], 0.3)
    cel(c, sl, GUS.s.shirt, L, k=3)
    c.drawPath(sl, paint("#bfe0ff", 0.12))
    cel(c, blob([(gx - 160, 800), (gx + 150, 720), (gx + 160, 1080), (gx - 120, 1050)], 0.45), GUS.s.skin, L, k=3)
    drips(c, gx + 300, 1120, t, n=7, spread=500, seed=1, length=500)
    grade(c, t, st)


def shot_wet_hand_cu(c, t):
    st = state(t)
    flat.linear_grad(c, (0, 0, W, H), ["#3a1513", "#120504"])
    L = light_for(st)
    # your shoulder / hoodie and the side of your face (cap backwards)
    sh = blob([(-100, H), (-60, 1150), (300, 980), (760, 1060), (1180, 1250), (1180, H)], 0.4)
    cel(c, sh, CAST["mascot"].shirt, L, k=3)
    cel(c, ellipse_path(300, 640, 260, 300), SKIN, L, k=3)
    cel(c, blob([(40, 560), (80, 380), (300, 300), (520, 380), (560, 560), (300, 470)], 0.45), CAST["mascot"].cap, L, k=3)
    c.drawCircle(470, 640, 30, paint("#fbfaf7"))
    c.drawCircle(480, 640, 15, paint("#120c0a"))
    # the wet hand lands from behind
    t0 = B["wet_hand"] + 0.12
    u = span(t, t0, t0 + 0.35, "out")
    hx, hy = lerp(1300, 760, u), lerp(700, 1050, u)
    arm = capsule((hx + 160, hy - 260), (1300, hy - 700), 150)
    cel(c, arm, "#2a2d33", L, k=3)
    hand = blob([(hx - 40, hy - 80), (hx + 170, hy - 140), (hx + 220, hy + 40), (hx + 60, hy + 120), (hx - 80, hy + 60)], 0.4)
    cel(c, hand, "#b9c4bf", L, k=3)
    for k in range(4):  # long fingers over the shoulder
        fx = hx - 60 + k * 50
        c.drawPath(capsule((fx, hy + 40), (fx - 40, hy + 240 + (k % 2) * 30), 34), paint("#aeb9b4"))
    c.drawPath(hand, paint("#e9f6ff", 0.18))
    if u > 0.5:
        drips(c, hx + 40, hy + 200, t, n=6, spread=200, seed=6, length=500)
    grade(c, t, st)


SHOTS = dict(panel_cu=shot_panel_cu, car_wide=shot_car_wide, you_cu=shot_you_cu, mirror_pov=shot_mirror_pov,
             doors_13=shot_doors_13, gus_reveal=shot_gus_reveal, gus_cu=shot_gus_cu, palm_cu=shot_palm_cu,
             indicator_cu=shot_indicator_cu, doors_9=shot_doors_9, rider_corner=shot_rider_corner, thumb_cu=shot_thumb_cu,
             hand_slap=shot_hand_slap, car_red=shot_car_red, lobby_pov=shot_lobby_pov, wet_hand_cu=shot_wet_hand_cu,
             choice_bg=shot_choice_bg)
