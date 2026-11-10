"""flat.py - 2D vector cut-out puppets + painting helpers (Skia).

Puppet(style).draw(canvas, x, y, scale, pose)   # (x, y) = point between the feet, on the floor

Look: flat fill + one cel-shadow tone (shape minus itself shifted toward the light) + optional
rim light on the lit edge.  Pose is a plain dict (see POSE_DEFAULT); every key optional.

Local puppet units: origin at the feet, y down (Skia convention), so the body lives at y < 0.
An adult is ~800 units tall; `scale` maps units -> pixels.
"""
from __future__ import annotations

import colorsys
import math
from dataclasses import dataclass, field

import numpy as np
import skia

# ============================================================================ colour helpers

def hexc(h, a=1.0):
    """'#rrggbb' | (r,g,b) 0-255 | (r,g,b) 0-1 floats -> skia Color4f-compatible int ARGB."""
    if isinstance(h, int):
        return h
    if isinstance(h, str):
        h = h.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    else:
        r, g, b = h[:3]
        if max(r, g, b) <= 1.0 and isinstance(r, float):
            r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return skia.ColorSetARGB(int(max(0, min(1, a)) * 255), int(r), int(g), int(b))


def rgb(c):
    return skia.ColorGetR(c), skia.ColorGetG(c), skia.ColorGetB(c)


def with_alpha(c, a):
    r, g, b = rgb(c)
    return skia.ColorSetARGB(int(max(0, min(1, a)) * 255), r, g, b)


def shade(c, k=0.72, hue_shift=0.03, sat=1.08):
    """Cel-shadow tone: darker, slightly cooler, a bit more saturated (natural, not muddy)."""
    r, g, b = [v / 255 for v in rgb(c)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + hue_shift) % 1.0 if h > 0.08 else (h - hue_shift * 0.5) % 1.0
    r, g, b = colorsys.hls_to_rgb(h, l * k, min(1, s * sat))
    return skia.ColorSetARGB(skia.ColorGetA(c), int(r * 255), int(g * 255), int(b * 255))


def tint(c, k=1.15):
    r, g, b = [v / 255 for v in rgb(c)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, min(1, l * k), s)
    return skia.ColorSetARGB(skia.ColorGetA(c), int(r * 255), int(g * 255), int(b * 255))


def lerp_col(a, b, t):
    ra, rb = rgb(a), rgb(b)
    return skia.ColorSetARGB(255, *[int(x + (y - x) * t) for x, y in zip(ra, rb)])


def paint(color, alpha=None, aa=True, blend=None, stroke=None, cap=skia.Paint.kRound_Cap, blur=0.0):
    c = hexc(color) if not isinstance(color, int) else color
    if alpha is not None:
        c = with_alpha(c, alpha)
    p = skia.Paint(AntiAlias=aa, Color=c)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blend is not None:
        p.setBlendMode(blend)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


# ============================================================================ path helpers

def ellipse_path(cx, cy, rx, ry):
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def rrect_path(l, t, r, b, rad):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(l, t, r, b), rad, rad))
    return p


def poly_path(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def blob(pts, tension=0.5, close=True):
    """Smooth path through points (Catmull-Rom -> cubic Beziers)."""
    pts = [tuple(map(float, q)) for q in pts]
    n = len(pts)
    p = skia.Path()
    p.moveTo(*pts[0])
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else p2
        k = tension / 3 * 2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 2, p1[1] + (p2[1] - p0[1]) * k / 2)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 2, p2[1] - (p3[1] - p1[1]) * k / 2)
        p.cubicTo(*c1, *c2, *p2)
    if close:
        p.close()
    return p


def stroke_to_path(path, width, cap=skia.Paint.kRound_Cap):
    pt = skia.Paint(Style=skia.Paint.kStroke_Style, StrokeWidth=width, StrokeCap=cap,
                    StrokeJoin=skia.Paint.kRound_Join, AntiAlias=True)
    out = skia.Path()
    pt.getFillPath(path, out)
    return out


def capsule(a, b, w):
    p = skia.Path()
    p.moveTo(*a)
    p.lineTo(*b)
    return stroke_to_path(p, w)


def limb_path(pts, w0, w1=None):
    """Tapered limb through 2-3 joints as a filled path (round joints)."""
    w1 = w0 if w1 is None else w1
    out = skia.Path()
    for i in range(len(pts) - 1):
        wa = w0 + (w1 - w0) * i / max(1, len(pts) - 1)
        seg = capsule(pts[i], pts[i + 1], wa)
        out = skia.Op(out, seg, skia.PathOp.kUnion_PathOp) if not out.isEmpty() else seg
    return out


def shifted(path, dx, dy):
    q = skia.Path(path)
    q.offset(dx, dy)
    return q


def op(a, b, kind="diff"):
    k = {"diff": skia.PathOp.kDifference_PathOp, "union": skia.PathOp.kUnion_PathOp,
         "inter": skia.PathOp.kIntersect_PathOp, "xor": skia.PathOp.kXOR_PathOp}[kind]
    r = skia.Op(a, b, k)
    return r if r is not None else skia.Path()


# ============================================================================ lighting

@dataclass
class Light:
    """dir = unit-ish vector pointing from the character TOWARD the light, in screen space."""
    dir: tuple = (-0.7, -0.7)
    shadow_px: float = 16.0  # shadow crescent width in puppet units
    rim: object = None  # colour of rim light (None = off)
    rim_px: float = 5.0
    rim_alpha: float = 0.85
    shadow_strength: float = 1.0  # 0 = flat, 1 = full cel tone


DEFAULT_LIGHT = Light()


def cel(canvas, path, color, light: Light = DEFAULT_LIGHT, shadow=None, k=1.0, rim=True):
    """Flat fill + cel shadow crescent + optional rim light."""
    c = hexc(color)
    canvas.drawPath(path, paint(c))
    if light.shadow_strength > 0:
        lx, ly = light.dir
        d = light.shadow_px * k
        sh = op(path, shifted(path, lx * d, ly * d))
        sc = shadow if shadow is not None else shade(c)
        if light.shadow_strength < 1:
            sc = lerp_col(c, sc, light.shadow_strength)
        canvas.drawPath(sh, paint(sc))
    if rim and light.rim is not None:
        lx, ly = light.dir
        d = light.rim_px * k
        rr = op(path, shifted(path, -lx * d, -ly * d))
        canvas.drawPath(rr, paint(light.rim, light.rim_alpha))


# ============================================================================ painting helpers

def fill_rect(canvas, l, t, r, b, color, alpha=None):
    canvas.drawRect(skia.Rect.MakeLTRB(l, t, r, b), paint(color, alpha))


def linear_grad(canvas, rect, colors, stops=None, vertical=True, alpha=1.0, path=None):
    l, t, r, b = rect
    pts = [skia.Point(l, t), skia.Point(l, b)] if vertical else [skia.Point(l, t), skia.Point(r, t)]
    cols = [hexc(c) for c in colors]
    sh = skia.GradientShader.MakeLinear(pts, cols, stops)
    p = skia.Paint(AntiAlias=True, Shader=sh)
    p.setAlphaf(alpha)
    if path is not None:
        canvas.drawPath(path, p)
    else:
        canvas.drawRect(skia.Rect.MakeLTRB(l, t, r, b), p)


def radial_grad(canvas, cx, cy, r, colors, stops=None, rect=None, alpha=1.0, blend=None):
    sh = skia.GradientShader.MakeRadial(skia.Point(cx, cy), r, [hexc(c) for c in colors], stops)
    p = skia.Paint(AntiAlias=True, Shader=sh)
    p.setAlphaf(alpha)
    if blend is not None:
        p.setBlendMode(blend)
    if rect is None:
        canvas.drawCircle(cx, cy, r, p)
    else:
        canvas.drawRect(skia.Rect.MakeLTRB(*rect), p)


def glow(canvas, cx, cy, r, color, intensity=0.6):
    """Painted additive light glow (lamp, window, screen)."""
    c = hexc(color)
    radial_grad(canvas, cx, cy, r, [with_alpha(c, intensity), with_alpha(c, intensity * 0.35), with_alpha(c, 0)],
                [0, 0.35, 1], blend=skia.BlendMode.kPlus)


def light_cone(canvas, apex, left, right, color, intensity=0.25):
    """Soft additive beam (window light, lamp cone)."""
    c = hexc(color)
    path = poly_path([apex, left, right])
    mid = ((left[0] + right[0]) / 2, (left[1] + right[1]) / 2)
    sh = skia.GradientShader.MakeLinear([skia.Point(*apex), skia.Point(*mid)],
                                        [with_alpha(c, intensity), with_alpha(c, 0)])
    p = skia.Paint(AntiAlias=True, Shader=sh, BlendMode=skia.BlendMode.kPlus)
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
    canvas.drawPath(path, p)


def vignette(canvas, w, h, strength=0.45, color="#000000"):
    c = hexc(color)
    r = math.hypot(w, h) * 0.55
    radial_grad(canvas, w / 2, h / 2, r, [with_alpha(c, 0), with_alpha(c, 0), with_alpha(c, strength)],
                [0, 0.55, 1], rect=(0, 0, w, h))


def floor_shadow(canvas, x, y, rx, ry, alpha=0.28):
    canvas.drawOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry),
                    paint("#000000", alpha, blur=ry * 0.5))


def grain(canvas, w, h, t, amount=0.035, seed=0):
    """Subtle animated film grain via a tiny noise image scaled up (cheap)."""
    r = np.random.default_rng(seed + int(t * 30))
    n = (r.random((h // 4, w // 4)) * 255).astype(np.uint8)
    rgba = np.dstack([n, n, n, np.full_like(n, int(255 * amount))])
    img = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    p = skia.Paint(BlendMode=skia.BlendMode.kOverlay)
    canvas.drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(), p)


# ============================================================================ puppet

POSE_DEFAULT = dict(
    eye_open=1.0,         # 0 closed .. 1 open (blink drives this)
    pupil=(0.0, 0.0),     # look direction, -1..1 each axis
    lid=0.0,              # upper-lid droop 0..1 (tired / suspicious)
    brow=(0.0, 0.0),      # (raise -1..1, angle -1 angry .. +1 worried)
    mouth="smile",        # smile | neutral | frown | o | grin | flat | smirk
    talk=0.0,             # 0..1 mouth opening (from word timing)
    speaking=False,       # True while this character's line plays: mouth fully closes between syllables
    head_tilt=0.0,        # degrees
    turn=0.0,             # fake 3/4 head/body turn -1 (to screen-left) .. 1 (to screen-right)
    lean=0.0,             # whole-body lean, degrees
    arm_l=(8.0, 10.0),    # (shoulder, elbow) degrees; shoulder 0 = down, + = outward; elbow + = bend inward/up
    arm_r=(8.0, 10.0),
    walk=None,            # front/back stepping phase (cycles per unit), None = standing
    view="front",         # front | side
    cycle=0.0,            # side view walk/run phase
    run=False,
    crouch=0.0,           # 0..1
    hold_r=None,          # 'mug' | 'phone' | 'letter' | callable(canvas, x, y, ang)
    hold_l=None,
    blush=0.0,
    breathe=0.0,          # time (s) for idle breathing
)


@dataclass
class Style:
    skin: str = "#e8b894"
    hair: str = "#3b2a22"
    hair_style: str = "short"      # short | bob | long | bun | spiky | bald
    shirt: str = "#3f6fb5"
    shirt_detail: str = "#f2efe8"  # collar / stripe
    pants: str = "#3a3f4b"
    shoes: str = "#2a2420"
    eyes: str = "#3b2a1e"
    lips: str = "#b5574b"
    height: float = 1.0            # body length multiplier (kids < 1)
    width: float = 1.0
    head_scale: float = 1.0
    sleeves: str = "long"          # long | short
    skirt: bool = False
    glasses: bool = False
    beard: bool = False
    cap: str | None = None         # cap colour (None = no cap)
    cap_backwards: bool = True


class Puppet:
    # base skeleton in units (front view)
    HIP_Y, SHOULDER_Y, HEAD_Y = -330.0, -545.0, -685.0
    HEAD_RX, HEAD_RY = 112.0, 120.0

    def __init__(self, style: Style | None = None, name="hero"):
        self.s = style or Style()
        self.name = name
        self.skin_sh = shade(hexc(self.s.skin), 0.84, hue_shift=-0.006, sat=0.92)

    # ------------------------------------------------------------------ public
    def draw(self, canvas, x, y, scale, pose=None, facing=1, light: Light = DEFAULT_LIGHT, shadow=True):
        P = dict(POSE_DEFAULT)
        if pose:
            P.update(pose)
        if shadow:
            floor_shadow(canvas, x, y, 120 * scale * self.s.width, 18 * scale)
        canvas.save()
        canvas.translate(x, y)
        canvas.scale(scale * facing, scale)
        lt = Light(dir=(light.dir[0] * facing, light.dir[1]), shadow_px=light.shadow_px, rim=light.rim,
                   rim_px=light.rim_px, rim_alpha=light.rim_alpha, shadow_strength=light.shadow_strength)
        if P["view"] == "side":
            self._draw_side(canvas, P, lt)
        else:
            self._draw_front(canvas, P, lt)
        canvas.restore()

    def head_pos(self, x, y, scale, pose=None, facing=1):
        """Screen position of the head centre (for caption avoidance, glows, etc)."""
        P = dict(POSE_DEFAULT)
        P.update(pose or {})
        h = self.s.height
        cy = (self.HEAD_Y - 10 * self.s.head_scale) * self._body_k(h) * (1 - 0.0) + self._crouch_dy(P)
        return x, y + cy * scale

    # ------------------------------------------------------------------ geometry helpers
    def _body_k(self, h):
        return h

    def _crouch_dy(self, P):
        return P["crouch"] * 130

    @staticmethod
    def _arm_pts(root, side, sh, el, l1, l2):
        a1 = math.radians(sh)
        a2 = math.radians(sh - el)
        e = (root[0] + side * math.sin(a1) * l1, root[1] + math.cos(a1) * l1)
        h = (e[0] + side * math.sin(a2) * l2, e[1] + math.cos(a2) * l2)
        return [root, e, h], math.degrees(math.atan2(h[1] - e[1], h[0] - e[0]))

    # ------------------------------------------------------------------ front view
    def _draw_front(self, c, P, L):
        S = self.s
        W, H = S.width, S.height
        t_b = P["breathe"]
        breathe = math.sin(t_b * 2 * math.pi / 3.6) * 3
        crouch = P["crouch"]
        bob = 0.0
        lift_l = lift_r = 0.0
        swing = 0.0
        if P["walk"] is not None:
            ph = P["walk"] * 2 * math.pi
            lift_l = max(0.0, math.sin(ph)) * 34
            lift_r = max(0.0, -math.sin(ph)) * 34
            bob = -abs(math.sin(ph)) * 10
            swing = math.sin(ph) * 14
        hip_y = self.HIP_Y * H + crouch * 130 + bob
        sh_y = self.SHOULDER_Y * H + crouch * 130 + bob + breathe * 0.4
        head_y = self.HEAD_Y * H + crouch * 130 + bob + breathe * 0.6
        turn = P["turn"]
        tx = turn * 14  # torso shift for fake 3/4

        c.save()
        c.rotate(P["lean"], 0, hip_y)

        # ---- legs (knees bend outward when crouching)
        for side, lift in ((-1, lift_l), (1, lift_r)):
            hx = side * 40 * W + tx * 0.5
            ankle = (side * (44 + crouch * 30) * W, -32 - lift)
            knee = (side * (44 + crouch * 70) * W + tx * 0.3, (hip_y + ankle[1]) / 2 - crouch * 10 + lift * 0.2)
            leg = limb_path([(hx, hip_y), knee, ankle], 52 * W, 44 * W)
            cel(c, leg, S.pants, L)
            shoe = blob([(ankle[0] - 30 * W, ankle[1] + 14), (ankle[0] - 24, ankle[1] - 12),
                         (ankle[0] + 26 + side * 8, ankle[1] - 8), (ankle[0] + 36 * W + side * 10, ankle[1] + 18),
                         (ankle[0], ankle[1] + 26)])
            cel(c, shoe, S.shoes, L, k=0.6)

        # ---- skirt / hips
        hips = blob([(-84 * W + tx, hip_y - 40), (84 * W + tx, hip_y - 40), (86 * W + tx, hip_y + 24),
                     (0 + tx, hip_y + 34), (-86 * W + tx, hip_y + 24)], 0.4)
        if S.skirt:
            sk = poly_path([(-82 * W + tx, hip_y - 40), (82 * W + tx, hip_y - 40), (122 * W + tx, hip_y + 110),
                            (-122 * W + tx, hip_y + 110)])
            cel(c, sk, S.pants, L)
        else:
            cel(c, hips, S.pants, L)

        # ---- torso
        torso = blob([(-92 * W + tx, sh_y + 6), (-50 * W + tx, sh_y - 14), (50 * W + tx, sh_y - 14),
                      (92 * W + tx, sh_y + 6), (84 * W + tx, (sh_y + hip_y) / 2), (80 * W + tx, hip_y - 20),
                      (-80 * W + tx, hip_y - 20), (-84 * W + tx, (sh_y + hip_y) / 2)], 0.45)
        cel(c, torso, S.shirt, L)
        # collar detail
        collar = poly_path([(-30 + tx * 1.4, sh_y - 12), (30 + tx * 1.4, sh_y - 12), (0 + tx * 1.4, sh_y + 30)])
        c.drawPath(collar, paint(S.shirt_detail))

        # ---- neck
        neck = rrect_path(-24 + tx * 1.5, sh_y - 48, 24 + tx * 1.5, sh_y + 4, 12)
        cel(c, neck, S.skin, L, shadow=shade(self.skin_sh, 0.85))

        # ---- arms
        for side, key, hold in ((-1, "arm_l", P["hold_l"]), (1, "arm_r", P["hold_r"])):
            shv, elv = P[key]
            shv = shv - side * swing * 0.0 + (swing * side if P["walk"] is not None else 0) * 0.6
            root = (side * 84 * W + tx, sh_y + 14)
            pts, ang = self._arm_pts(root, side, shv, elv, 118 * H, 112 * H)
            arm_col = S.shirt if S.sleeves == "long" else S.skin
            if S.sleeves == "short":
                sleeve = limb_path([pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * 0.45,
                                             pts[0][1] + (pts[1][1] - pts[0][1]) * 0.45)], 46)
                cel(c, limb_path(pts, 36, 32), S.skin, L, shadow=self.skin_sh)
                cel(c, sleeve, S.shirt, L)
            else:
                cel(c, limb_path(pts, 40, 36), arm_col, L)
            hx, hy = pts[2]
            cel(c, ellipse_path(hx, hy, 22, 24), S.skin, L, shadow=self.skin_sh, k=0.6)
            if hold:
                self._draw_item(c, hold, hx, hy, ang, L)

        # ---- head
        c.save()
        c.rotate(P["head_tilt"], 0 + tx, sh_y - 30)
        self._draw_head_front(c, P, L, head_y, turn)
        c.restore()
        c.restore()

    def _draw_head_front(self, c, P, L, hy, turn):
        S = self.s
        hs = S.head_scale
        rx, ry = self.HEAD_RX * hs, self.HEAD_RY * hs
        hx = turn * 10
        fx = hx + turn * 38 * hs  # face-feature centre shift for fake 3/4
        hair = hexc(S.hair)

        # back hair
        if S.hair_style in ("bob", "long"):
            bottom = hy + (ry * 0.85 if S.hair_style == "bob" else ry * 1.9)
            back = blob([(hx - rx * 1.12, hy - ry * 0.2), (hx - rx * 0.9, hy - ry * 1.05), (hx + rx * 0.9, hy - ry * 1.05),
                         (hx + rx * 1.12, hy - ry * 0.2), (hx + rx * 1.1, bottom), (hx - rx * 1.1, bottom)], 0.45)
            cel(c, back, shade(hair, 0.85), L)
        if S.hair_style == "bun":
            cel(c, ellipse_path(hx - turn * 20, hy - ry * 1.08, rx * 0.42, ry * 0.36), hair, L)
        if S.cap and S.cap_backwards:
            # backwards brim sticks out behind the head: peeks out on the side away from the face
            bx = hx - turn * rx * 1.05
            bw = rx * (0.42 + 0.62 * abs(turn))
            brim = blob([(bx - bw, hy - ry * 0.58), (bx, hy - ry * 0.72), (bx + bw, hy - ry * 0.58),
                         (bx + bw * 0.7, hy - ry * 0.47), (bx - bw * 0.7, hy - ry * 0.47)], 0.45)
            cel(c, brim, shade(hexc(S.cap), 0.82), L, k=0.5)

        # ears
        for side in (-1, 1):
            vis = 1 - max(0, side * turn) * 0.9
            if vis > 0.15:
                ex = hx + side * rx * (0.97 - 0.12 * side * turn)
                cel(c, ellipse_path(ex, hy + 8, 18 * vis, 26), S.skin, L, shadow=self.skin_sh, k=0.5)

        # head shape: slightly squarer jaw
        head = blob([(hx - rx, hy - ry * 0.15), (hx - rx * 0.78, hy - ry * 0.86), (hx, hy - ry),
                     (hx + rx * 0.78, hy - ry * 0.86), (hx + rx, hy - ry * 0.15), (hx + rx * 0.82, hy + ry * 0.62),
                     (hx + turn * 16, hy + ry), (hx - rx * 0.82, hy + ry * 0.62)], 0.5)
        cel(c, head, S.skin, L, shadow=self.skin_sh, k=1.0)

        # cheeks
        if P["blush"] > 0:
            for side in (-1, 1):
                c.drawOval(skia.Rect.MakeXYWH(fx + side * 52 * hs - 20, hy + 26, 40, 20),
                           paint("#e0675a", 0.35 * P["blush"], blur=6))

        # eyes
        brows = []
        eo = max(0.0, min(1.0, P["eye_open"]))
        px, py = P["pupil"]
        for side in (-1, 1):
            far = (side * turn) < 0
            sq = 1 - (abs(turn) * 0.32 if far else 0)
            ex = fx + side * 42 * hs * (1 - abs(turn) * 0.12)
            ey = hy - 4
            erx, ery = 19 * hs * sq, 25 * hs
            if eo < 0.18:
                arc = skia.Path()
                arc.moveTo(ex - erx, ey + 2)
                arc.quadTo(ex, ey + 12, ex + erx, ey + 2)
                c.drawPath(arc, paint("#2a1d18", stroke=5))
            else:
                eye = ellipse_path(ex, ey, erx, ery * eo)
                c.drawPath(eye, paint("#fbfaf7"))
                c.save()
                c.clipPath(eye, doAntiAlias=True)
                pxx = ex + (px + turn * 0.35) * erx * 0.45
                pyy = ey + py * ery * 0.4
                c.drawCircle(pxx, pyy, 12.5 * hs, paint(S.eyes))
                c.drawCircle(pxx, pyy, 6.5 * hs, paint("#120c0a"))
                c.drawCircle(pxx - 4, pyy - 5, 3.6 * hs, paint("#ffffff"))
                lid = P["lid"]
                if lid > 0:
                    c.drawRect(skia.Rect.MakeLTRB(ex - erx - 2, ey - ery - 2, ex + erx + 2, ey - ery + 2 * ery * lid * 0.6),
                               paint(shade(hexc(S.skin), 0.9)))
                c.restore()
                c.drawPath(ellipse_path(ex, ey, erx, ery * eo), paint("#2a1d18", 0.55, stroke=2.2))
            # brows
            raise_, angle = P["brow"]
            by = ey - (33 if S.cap else 38) * hs - raise_ * 12
            inner = (ex - side * 16 * sq, by - angle * 9 * 1)
            outer = (ex + side * 18 * sq, by + angle * 6 * 1 - 3)
            bp = skia.Path()
            bp.moveTo(*inner)
            bp.quadTo((inner[0] + outer[0]) / 2, by - 7, *outer)
            brows.append(bp)
            if not S.cap:
                c.drawPath(bp, paint(shade(hair, 0.9), stroke=9 * hs))

        if S.glasses:
            for side in (-1, 1):
                ex = fx + side * 42 * hs
                c.drawRoundRect(skia.Rect.MakeLTRB(ex - 30, hy - 30, ex + 30, hy + 22), 14, 14,
                                paint("#2b2b2e", stroke=5))
            c.drawLine(fx - 12, hy - 8, fx + 12, hy - 8, paint("#2b2b2e", stroke=5))

        # nose
        nx = fx + turn * 14
        npth = skia.Path()
        npth.moveTo(nx - 2 + turn * 4, hy + 8)
        npth.quadTo(nx + 10 * (1 if turn >= 0 else -1) + turn * 6, hy + 34, nx - 4, hy + 38)
        c.drawPath(npth, paint(shade(self.skin_sh, 0.85), stroke=5))

        # mouth
        self._draw_mouth(c, P, fx + turn * 6, hy + 66 * hs, hs)

        if S.beard:
            bd = blob([(hx - rx * 0.86, hy + ry * 0.2), (hx - rx * 0.6, hy + ry * 1.05), (hx, hy + ry * 1.18),
                       (hx + rx * 0.6, hy + ry * 1.05), (hx + rx * 0.86, hy + ry * 0.2), (hx, hy + ry * 0.62)], 0.5)
            c.drawPath(op(bd, ellipse_path(fx + turn * 6, hy + 66 * hs, 30, 16 + P["talk"] * 14)), paint(hair))

        # front hair cap (stops above brows)
        self._draw_hair_cap(c, hx, hy, rx, ry, turn, hair, L)
        if S.cap:
            self._draw_cap_front(c, hx, hy, rx, ry, turn, hair, L)
            for bp in brows:  # brows read on top of the bangs (cartoon convention)
                c.drawPath(bp, paint(shade(hair, 0.75), stroke=9 * hs))

    def _draw_cap_front(self, c, hx, hy, rx, ry, turn, hair, L):
        """Baseball cap worn backwards: dome + band, snapback opening at the front with hair showing
        through it, bangs hanging below the band."""
        cap = hexc(self.s.cap)
        dark = shade(cap, 0.78)
        sw = turn * 30
        band_c = hy - ry * 0.64         # band height at the front centre
        band_s = hy - ry * 0.4          # band height at the sides (over the ears)
        dome = blob([(hx - rx * 1.05, band_s), (hx - rx * 1.03, hy - ry * 0.78), (hx - rx * 0.45 + sw * 0.4, hy - ry * 1.16),
                     (hx + rx * 0.45 + sw * 0.4, hy - ry * 1.16), (hx + rx * 1.03, hy - ry * 0.78), (hx + rx * 1.05, band_s),
                     (hx + rx * 0.55 + sw, hy - ry * 0.57), (hx + sw, band_c), (hx - rx * 0.55 + sw, hy - ry * 0.57)], 0.45)
        cel(c, dome, cap, L, k=1.1)
        # panel seams + top button
        top = (hx + sw * 0.5, hy - ry * 1.13)
        for dx in (-0.62, 0.62):
            seam = skia.Path()
            seam.moveTo(*top)
            seam.quadTo(hx + rx * dx * 0.8 + sw * 0.7, hy - ry * 0.98, hx + rx * dx + sw * 0.8, hy - ry * 0.6)
            c.drawPath(seam, paint(dark, 0.7, stroke=4))
        c.drawCircle(*top, 9, paint(dark))
        # band along the lower edge
        band = skia.Path()
        band.moveTo(hx - rx * 1.03, band_s - 4)
        band.quadTo(hx - rx * 0.5 + sw, hy - ry * 0.64, hx + sw, band_c - 4)
        band.quadTo(hx + rx * 0.5 + sw, hy - ry * 0.64, hx + rx * 1.03, band_s - 4)
        c.drawPath(band, paint(dark, stroke=11))
        # snapback opening (hair shows through) + strap
        ow, oh = rx * 0.28, ry * 0.26
        ox, oy = hx + sw, band_c - 2
        opening = skia.Path()
        opening.moveTo(ox - ow, oy)
        opening.cubicTo(ox - ow, oy - oh * 1.3, ox + ow, oy - oh * 1.3, ox + ow, oy)
        opening.close()
        c.drawPath(opening, paint(shade(hair, 0.9)))
        for k in range(3):  # a few hair strands visible inside the opening
            hxk = ox - ow * 0.55 + k * ow * 0.55
            c.drawLine(hxk, oy - oh * 0.7, hxk + 6 + turn * 6, oy - 4, paint(tint(hair, 1.5), 0.5, stroke=3))
        strap = rrect_path(ox - ow - 4, oy - 14, ox + ow + 4, oy + 1, 5)
        c.drawPath(strap, paint(dark))
        c.drawRoundRect(skia.Rect.MakeLTRB(ox - 9, oy - 16, ox + 9, oy + 3), 3, 3, paint("#d8d4cc"))
        # bangs hanging below the band (some of the fringe still showing)
        tip_y = hy - ry * 0.4
        locks = [(-0.52, 0.82), (-0.22, 1.0), (0.1, 0.92), (0.4, 0.75)]
        for off, ln in locks:
            x0 = hx + rx * off + sw
            y0 = hy - ry * 0.6 + abs(off) * ry * 0.1
            tip = (x0 - 10 + turn * 8, y0 + (tip_y - y0) * ln + 4)
            lock = blob([(x0 - 26, y0 - 6), (x0 + 24, y0 - 6), (x0 + 12, (y0 + tip[1]) / 2), tip,
                         (x0 - 20, (y0 + tip[1]) / 2)], 0.35)
            cel(c, lock, hair, L, k=0.5)
        c.drawPath(band, paint(dark, stroke=11))
        # short hair at the sides, under the cap, above the ears
        for side in (-1, 1):
            vis = 1 - max(0, side * turn) * 0.8
            sx = hx + side * rx * (0.98 - 0.1 * side * turn)
            tuft = blob([(sx - side * 4, band_s - 8), (sx + side * 14 * vis, band_s - 4),
                         (sx + side * 8 * vis, band_s + 34), (sx - side * 12, band_s + 22)], 0.4)
            c.drawPath(tuft, paint(hair))

    def _draw_hair_cap(self, c, hx, hy, rx, ry, turn, hair, L):
        st = self.s.hair_style
        if st == "bald":
            return
        sweep = turn * 20
        if st == "spiky":
            pts = []
            n = 13
            for i in range(n):
                a = math.pi * (1.02 + 0.96 * i / (n - 1))
                r = 1.2 if i % 2 else 0.96
                pts.append((hx + math.cos(a) * rx * r + sweep * (i % 2), hy + math.sin(a) * ry * r - 6))
            spikes = poly_path([(hx - rx * 0.9, hy - ry * 0.2)] + pts + [(hx + rx * 0.9, hy - ry * 0.2)])
            fr = hy - ry * 0.5
            base = blob([(hx - rx * 1.05, hy - ry * 0.05), (hx - rx, hy - ry * 0.8), (hx, hy - ry * 1.08),
                         (hx + rx, hy - ry * 0.8), (hx + rx * 1.05, hy - ry * 0.05), (hx + rx * 0.85, hy - ry * 0.35),
                         (hx + rx * 0.4 + sweep, fr), (hx - rx * 0.05 + sweep, fr + 14), (hx - rx * 0.5 + sweep, fr),
                         (hx - rx * 0.88, hy - ry * 0.32)], 0.42)
            cap = op(spikes, base, "union")
        else:
            fringe = hy - ry * (0.5 if st in ("short", "spiky") else 0.42)
            pts = [(hx - rx * 1.06, hy - ry * 0.05 + (ry * 0.5 if st in ("bob", "long") else 0)),
                   (hx - rx * 1.02, hy - ry * 0.75), (hx - rx * 0.4, hy - ry * 1.12), (hx + rx * 0.5, hy - ry * 1.1),
                   (hx + rx * 1.04, hy - ry * 0.7),
                   (hx + rx * 1.06, hy - ry * 0.05 + (ry * 0.5 if st in ("bob", "long") else 0)),
                   (hx + rx * 0.88, hy - ry * 0.35), (hx + rx * 0.5 + sweep, fringe),
                   (hx - rx * 0.1 + sweep, fringe + 16), (hx - rx * 0.62 + sweep, fringe - 4),
                   (hx - rx * 0.9, hy - ry * 0.3)]
            cap = blob(pts, 0.42)
        cel(c, cap, hair, L, k=0.9)
        # one hair highlight stroke
        hl = skia.Path()
        hl.moveTo(hx - rx * 0.55 + sweep * 0.5, hy - ry * 0.86)
        hl.quadTo(hx - rx * 0.1 + sweep * 0.5, hy - ry * 1.02, hx + rx * 0.3 + sweep * 0.5, hy - ry * 0.92)
        c.drawPath(hl, paint(tint(hair, 1.6), 0.55, stroke=7))

    def _draw_mouth(self, c, P, mx, my, hs):
        talk = max(0.0, min(1.0, P["talk"]))
        shape = P["mouth"]
        dark = hexc("#5a2320")
        line = paint("#4a2420", stroke=5.5 * hs)
        speaking = P.get("speaking", False)
        if speaking and talk <= 0.08:  # talking characters close their mouth between syllables / words
            shape = {"o": "neutral", "grin": "smile"}.get(shape, shape)
        if talk > 0.08 or (shape in ("o", "grin") and not speaking):
            if shape == "o":
                w, h = (12 + talk * 10, 6 + talk * 30) if speaking else (15 + talk * 4, 14 + talk * 14)
            elif shape == "grin":
                w, h = 38, (6 + talk * 28) if speaking else (14 + talk * 16)
            else:
                w, h = 26 + talk * 8, 5 + talk * 32
            w *= hs
            h *= hs
            m = skia.Path()
            if shape == "o":
                m.addOval(skia.Rect.MakeLTRB(mx - w, my - h * 0.5, mx + w, my + h * 0.6))
            else:
                curve = {"smile": 8, "grin": 12, "frown": -6}.get(shape, 2)
                m.moveTo(mx - w, my - curve * 0.3)
                m.quadTo(mx, my + curve * 0.4 - h * 0.15, mx + w, my - curve * 0.3)
                m.quadTo(mx + w * 0.4, my + h, mx, my + h)
                m.quadTo(mx - w * 0.4, my + h, mx - w, my - curve * 0.3)
                m.close()
            c.drawPath(m, paint(dark))
            c.save()
            c.clipPath(m, doAntiAlias=True)
            c.drawOval(skia.Rect.MakeLTRB(mx - w * 0.6, my + h * 0.45, mx + w * 0.6, my + h * 1.3), paint("#d0605a"))
            if shape != "o":
                c.drawRect(skia.Rect.MakeLTRB(mx - w, my - 20, mx + w, my + max(3.0, h * 0.18)), paint("#f6f3ee"))
            c.restore()
            return
        mp = skia.Path()
        if shape in ("smile", "smirk"):
            mp.moveTo(mx - 26 * hs, my - 4)
            mp.quadTo(mx, my + 14 * hs, mx + 26 * hs, my - (10 if shape == "smirk" else 4))
        elif shape == "frown":
            mp.moveTo(mx - 22 * hs, my + 6)
            mp.quadTo(mx, my - 8 * hs, mx + 22 * hs, my + 6)
        else:  # neutral / flat
            mp.moveTo(mx - 20 * hs, my)
            mp.quadTo(mx, my + (3 if shape == "neutral" else 0), mx + 20 * hs, my)
        c.drawPath(mp, line)

    # ------------------------------------------------------------------ side view
    def _draw_side(self, c, P, L):
        """Profile facing +x.  Walk/run cycle from P['cycle'] (one step pair per unit)."""
        S = self.s
        W, H = S.width, S.height
        run = P["run"]
        ph = P["cycle"] * 2 * math.pi
        amp_h = 38 if run else 24
        amp_k = 70 if run else 38
        lean = (12 if run else 3) + P["lean"]
        bob = -abs(math.cos(ph)) * (16 if run else 7) + (12 if run else 4)
        hip = (0.0, self.HIP_Y * H + bob + P["crouch"] * 130)
        c.save()
        c.rotate(lean, hip[0], hip[1])
        l1, l2 = 150 * H, 150 * H

        def leg(phase, col):
            th = math.radians(amp_h * math.sin(phase))
            knee_b = math.radians(amp_k * max(0, math.sin(phase + 1.3)) + 6)
            k = (hip[0] + math.sin(th) * l1, hip[1] + math.cos(th) * l1)
            a = (k[0] + math.sin(th - knee_b) * l2, k[1] + math.cos(th - knee_b) * l2)
            cel(c, limb_path([hip, k, a], 50 * W, 42 * W), col, L)
            foot = blob([(a[0] - 18, a[1] - 14), (a[0] + 40, a[1] - 6), (a[0] + 46, a[1] + 14), (a[0] - 22, a[1] + 16)])
            cel(c, foot, S.shoes, L, k=0.6)

        def arm(phase, col):
            sw = (40 if run else 26) * math.sin(phase)
            el = 80 if run else 18
            root = (8, self.SHOULDER_Y * H + bob + 16)
            a1 = math.radians(-sw)
            e = (root[0] - math.sin(a1) * 115 * H, root[1] + math.cos(a1) * 115 * H)
            a2 = a1 - math.radians(el)
            h = (e[0] - math.sin(a2) * 108 * H, e[1] + math.cos(a2) * 108 * H)
            cel(c, limb_path([root, e, h], 40, 36), col if S.sleeves == "long" else S.skin, L)
            cel(c, ellipse_path(h[0], h[1], 21, 23), S.skin, L, k=0.6)

        far = shade(hexc(S.pants), 0.8)
        arm(ph, shade(hexc(S.shirt), 0.8))
        leg(ph + math.pi, far)
        # torso
        sy = self.SHOULDER_Y * H + bob
        torso = blob([(-46 * W, sy + 6), (30 * W, sy - 8), (52 * W, sy + 40), (46 * W, hip[1] - 10),
                      (-40 * W, hip[1] - 10), (-52 * W, sy + 60)], 0.45)
        leg(ph, S.pants)
        cel(c, torso, S.shirt, L)
        cel(c, blob([(-46 * W, hip[1] - 36), (46 * W, hip[1] - 36), (48 * W, hip[1] + 20), (-48 * W, hip[1] + 20)], 0.4),
            S.pants, L)
        # neck + head profile
        hy = self.HEAD_Y * H + bob
        cel(c, rrect_path(-18, sy - 50, 22, sy + 6, 10), S.skin, L)
        hs = S.head_scale
        rx, ry = self.HEAD_RX * hs * 0.95, self.HEAD_RY * hs
        hair = hexc(S.hair)
        if S.hair_style in ("bob", "long"):
            bottom = hy + (ry * 0.85 if S.hair_style == "bob" else ry * 1.8)
            cel(c, blob([(-rx * 1.1, hy - ry * 0.3), (-rx * 0.6, hy - ry * 1.05), (rx * 0.3, hy - ry * 1.05),
                         (rx * 0.2, bottom), (-rx * 1.1, bottom)], 0.45), shade(hair, 0.85), L)
        head = blob([(-rx, hy), (-rx * 0.7, hy - ry * 0.9), (rx * 0.4, hy - ry), (rx * 0.98, hy - ry * 0.35),
                     (rx * 1.12, hy + ry * 0.05), (rx * 0.98, hy + ry * 0.2), (rx * 0.9, hy + ry * 0.62),
                     (rx * 0.3, hy + ry), (-rx * 0.5, hy + ry * 0.8)], 0.5)
        cel(c, head, S.skin, L, shadow=self.skin_sh)
        cel(c, ellipse_path(-rx * 0.12, hy + 8, 18, 26), S.skin, L, k=0.5)  # ear
        # eye
        ex, ey = rx * 0.58, hy - 6
        eo = max(0.0, min(1.0, P["eye_open"]))
        if eo < 0.18:
            c.drawLine(ex - 12, ey + 4, ex + 10, ey + 4, paint("#2a1d18", stroke=5))
        else:
            e = ellipse_path(ex, ey, 12, 22 * eo)
            c.drawPath(e, paint("#fbfaf7"))
            c.save()
            c.clipPath(e, doAntiAlias=True)
            c.drawCircle(ex + 4, ey, 9, paint(S.eyes))
            c.drawCircle(ex + 4, ey, 5, paint("#120c0a"))
            c.restore()
        raise_, angle = P["brow"]
        c.drawLine(ex - 14, ey - 36 - raise_ * 10, ex + 14, ey - 38 - raise_ * 10 + angle * 6,
                   paint(shade(hair, 0.9), stroke=9))
        # mouth (profile)
        talk = P["talk"]
        mx, my = rx * 0.82, hy + 62
        if talk > 0.06:
            m = blob([(mx - 20, my - 4), (mx + 6, my - 6), (mx + 6, my + 4 + talk * 16), (mx - 14, my + 2 + talk * 10)])
            c.drawPath(m, paint("#5a2320"))
        else:
            c.drawLine(mx - 18, my, mx + 4, my - (3 if P["mouth"] == "smile" else 0), paint("#4a2420", stroke=5))
        # hair cap
        if S.hair_style != "bald":
            cap = blob([(-rx * 1.06, hy + ry * 0.25), (-rx * 0.95, hy - ry * 0.8), (rx * 0.2, hy - ry * 1.12),
                        (rx * 1.02, hy - ry * 0.55), (rx * 0.7, hy - ry * 0.48), (rx * 0.1, hy - ry * 0.52),
                        (-rx * 0.4, hy - ry * 0.2), (-rx * 0.62, hy + ry * 0.05)], 0.42)
            cel(c, cap, hair, L, k=0.9)
        if S.cap:
            capc = hexc(S.cap)
            dome = blob([(-rx * 1.06, hy - ry * 0.3), (-rx * 0.9, hy - ry * 0.95), (rx * 0.25, hy - ry * 1.16),
                         (rx * 1.0, hy - ry * 0.6), (rx * 0.85, hy - ry * 0.42), (-rx * 0.2, hy - ry * 0.36)], 0.45)
            brim = blob([(-rx * 0.95, hy - ry * 0.44), (-rx * 1.75, hy - ry * 0.42), (-rx * 1.8, hy - ry * 0.32),
                         (-rx * 0.95, hy - ry * 0.28)], 0.3) if S.cap_backwards else \
                blob([(rx * 0.9, hy - ry * 0.5), (rx * 1.7, hy - ry * 0.4), (rx * 1.7, hy - ry * 0.32), (rx * 0.9, hy - ry * 0.36)], 0.3)
            cel(c, brim, shade(capc, 0.82), L, k=0.5)
            cel(c, dome, capc, L, k=1.0)
            lock = blob([(rx * 0.55, hy - ry * 0.42), (rx * 0.92, hy - ry * 0.44), (rx * 0.86, hy - ry * 0.2)], 0.4)
            cel(c, lock, hair, L, k=0.4)
        arm(ph + math.pi, S.shirt)
        c.restore()

    # ------------------------------------------------------------------ props
    def _draw_item(self, c, item, x, y, ang, L):
        if callable(item):
            item(c, x, y, ang)
            return
        if item == "mug":
            body = rrect_path(x - 26, y - 46, x + 26, y + 18, 10)
            handle = stroke_to_path(ellipse_path(x + 30, y - 14, 16, 18), 9)
            cel(c, handle, "#e9e4da", L, k=0.4)
            cel(c, body, "#e9e4da", L, k=0.8)
            c.drawOval(skia.Rect.MakeLTRB(x - 24, y - 52, x + 24, y - 40), paint("#5b3a24"))
            cel(c, ellipse_path(x - 4, y + 2, 18, 22), "#e8b894", L, k=0.4, rim=False)  # fingers over the mug
        elif item == "phone":
            c.save()
            c.rotate(ang - 90, x, y)
            cel(c, rrect_path(x - 22, y - 52, x + 22, y + 30, 8), "#22252b", L, k=0.5)
            c.drawRoundRect(skia.Rect.MakeLTRB(x - 17, y - 46, x + 17, y + 24), 5, 5, paint("#8fd0ff", 0.9))
            c.restore()
        elif item == "letter":
            c.save()
            c.rotate(ang - 90, x, y)
            cel(c, poly_path([(x - 40, y - 60), (x + 40, y - 60), (x + 40, y + 20), (x - 40, y + 20)]), "#f4efe2", L, k=0.4)
            for i in range(4):
                c.drawLine(x - 28, y - 44 + i * 14, x + 24 - (i == 3) * 20, y - 44 + i * 14, paint("#9a948a", stroke=3))
            c.restore()


# ============================================================================ preset cast

CAST = {
    "mia": Style(skin="#e9b896", hair="#2f2019", hair_style="bob", shirt="#d4704f", shirt_detail="#f3ece2",
                 pants="#34495e", shoes="#3a2c25", eyes="#4a3020", sleeves="long"),
    "leo": Style(skin="#b97c55", hair="#1d1612", hair_style="short", shirt="#4f7a5a", shirt_detail="#e9e2d2",
                 pants="#2e3440", shoes="#2a2420", eyes="#2a1d14"),
    "nana": Style(skin="#efc6a4", hair="#c9c4bd", hair_style="bun", shirt="#7b5ea7", shirt_detail="#efe6f6",
                  pants="#5a4a6b", skirt=True, glasses=True, height=0.93),
    # mascot: average-height teen (5'9" ~ 175 cm vs the 170 cm base puppet), red cap on backwards, bangs showing
    "teen": Style(skin="#e6b08a", hair="#3b2718", hair_style="short", shirt="#9aa3ad", shirt_detail="#e9ecef",
                  pants="#3b5b86", shoes="#ecebe6", eyes="#3a2416", height=1.03, width=0.9, head_scale=1.04,
                  sleeves="long", cap="#d0312d", cap_backwards=True),
    "kid": Style(skin="#f0c2a0", hair="#8a5a2b", hair_style="spiky", shirt="#e3b23c", shirt_detail="#ffffff",
                 pants="#3e6c9c", height=0.72, width=0.85, head_scale=1.12, sleeves="short"),
}

CAST["mascot"] = CAST["teen"]
