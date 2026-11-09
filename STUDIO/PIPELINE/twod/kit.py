"""kit.py - timing, text, lip-sync and camera helpers for 2D shots.

W, H = 1080, 1920 (native 9:16).  SAFE = 36 px minimum margin for any text.
"""
from __future__ import annotations

import json
import math
from bisect import bisect_right
from functools import lru_cache
from pathlib import Path

import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
SAFE = 36
STUDIO = Path(__file__).resolve().parents[2]
FONTS = STUDIO / "ASSETS" / "fonts"

# ============================================================================ easing / keys

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_in_out(t):
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_out(t, p=3):
    t = clamp(t)
    return 1 - (1 - t) ** p


def ease_in(t, p=3):
    return clamp(t) ** p


def back_out(t, s=1.7):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def elastic_out(t):
    t = clamp(t)
    if t in (0, 1):
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1


EASES = dict(linear=clamp, smooth=smooth, inout=ease_in_out, out=ease_out, in_=ease_in, back=back_out,
             elastic=elastic_out, hold=lambda t: 0.0)


def span(t, t0, t1, ease="inout"):
    """0..1 progress of t through [t0, t1] with easing."""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return EASES[ease]((t - t0) / (t1 - t0))


class Keys:
    """Eased keyframes.  Keys([(t, value, ease_into_this_key), ...]); values may be floats or tuples."""

    def __init__(self, keys):
        ks = []
        for k in keys:
            ks.append((float(k[0]), k[1], k[2] if len(k) > 2 else "inout"))
        self.k = sorted(ks, key=lambda q: q[0])
        self.ts = [q[0] for q in self.k]

    def __call__(self, t):
        i = bisect_right(self.ts, t)
        if i == 0:
            return self.k[0][1]
        if i >= len(self.k):
            return self.k[-1][1]
        t0, v0, _ = self.k[i - 1]
        t1, v1, e = self.k[i]
        u = EASES[e]((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
        if isinstance(v0, (tuple, list)):
            return tuple(lerp(a, b, u) for a, b in zip(v0, v1))
        return lerp(v0, v1, u)


def wiggle(t, freq=1.0, amp=1.0, seed=0):
    """Smooth pseudo-random wobble (sum of sines)."""
    s = seed * 1.618
    return amp * (0.6 * math.sin(t * freq * 2.1 + s) + 0.3 * math.sin(t * freq * 3.7 + s * 2.3)
                  + 0.1 * math.sin(t * freq * 7.3 + s * 4.1))


def flicker(t, base=1.0, amount=0.15, seed=0, rate=9.0):
    """Light flicker: mostly steady with occasional dips."""
    n = wiggle(t, rate, 1.0, seed)
    dip = max(0.0, math.sin(t * 1.3 + seed) ** 40) * 0.6
    return base * (1 - amount * (0.5 + 0.5 * n) - amount * dip)


def blink(t, seed=0, period=3.4, dur=0.14):
    """Eye-open 0..1 with natural irregular blinks (deterministic in t)."""
    r = np.random.default_rng(seed)
    offs = r.uniform(0, period, 1)[0]
    k = math.floor((t + offs) / period)
    rr = np.random.default_rng(seed * 1000 + k + 7)
    start = k * period - offs + rr.uniform(0.2, period - dur - 0.2)
    u = (t - start) / dur
    if 0 <= u <= 1:
        return abs(1 - 2 * u) ** 0.7
    # occasional double blink
    if rr.random() < 0.2:
        u2 = (t - start - dur - 0.08) / dur
        if 0 <= u2 <= 1:
            return abs(1 - 2 * u2) ** 0.7
    return 1.0


# ============================================================================ word timing / lip-sync

class Timing:
    """Loads timing.json from narrate.py:  {"lines": [{"id","who","start","end","text","words":[{"w","start","end"}]}]}"""

    def __init__(self, path):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text())
        self.lines = {ln["id"]: ln for ln in self.data["lines"]}
        self.words = []
        for ln in self.data["lines"]:
            for w in ln["words"]:
                self.words.append(dict(w, line=ln["id"], who=ln.get("who", "narrator")))

    def line(self, lid):
        return self.lines[lid]

    def word(self, lid, text_or_index):
        """Find a word in a line by index or (case-insensitive, punctuation-stripped) text."""
        ws = self.lines[lid]["words"]
        if isinstance(text_or_index, int):
            return ws[text_or_index]
        key = _norm(text_or_index)
        for w in ws:
            if _norm(w["w"]) == key:
                return w
        raise KeyError(f"word {text_or_index!r} not in line {lid}: {[w['w'] for w in ws]}")

    def mouth(self, t, who=None):
        """0..1 mouth opening at time t for speaker `who` (None = any)."""
        best = 0.0
        for w in self.words:
            if who is not None and w["who"] != who:
                continue
            if w["start"] - 0.05 <= t <= w["end"] + 0.05:
                d = max(0.08, w["end"] - w["start"])
                n_syl = max(1, _syllables(w["w"]))
                u = (t - w["start"]) / d
                env = math.sin(math.pi * clamp(u)) ** 0.5
                osc = 0.55 + 0.45 * abs(math.sin(math.pi * n_syl * clamp(u)))
                best = max(best, env * osc)
        return best

    def speaking(self, t, who=None, pad=0.1):
        for ln in self.data["lines"]:
            if who is None or ln.get("who") == who:
                if ln["start"] - pad <= t <= ln["end"] + pad:
                    return ln
        return None


def _norm(s):
    return "".join(ch for ch in s.lower() if ch.isalnum() or ch == "'")


def _syllables(word):
    w = _norm(word)
    v = "aeiouy"
    n, prev = 0, False
    for ch in w:
        isv = ch in v
        if isv and not prev:
            n += 1
        prev = isv
    if w.endswith("e") and n > 1:
        n -= 1
    return max(1, n)


# ============================================================================ text

@lru_cache(maxsize=32)
def typeface(weight="Black"):
    return skia.Typeface.MakeFromFile(str(FONTS / f"Inter-{weight}.otf"))


def font(size, weight="Black"):
    f = skia.Font(typeface(weight), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def measure(text, size, weight="Black"):
    return font(size, weight).measureText(text)


def fit_size(text, size, max_w, weight="Black", min_size=18):
    """Largest size <= size so that `text` fits in max_w."""
    s = size
    while s > min_size and measure(text, s, weight) > max_w:
        s *= 0.95
    return s


def wrap(text, size, max_w, weight="Black"):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if measure(trial, size, weight) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_text(canvas, text, x, y, size, color="#ffffff", weight="Black", align="center", stroke=0,
              stroke_color="#000000", shadow=0.0, alpha=1.0, max_w=None, tracking=0.0):
    """Draw one line.  (x, y) = anchor at baseline.  Shrinks to max_w (default: safe width)."""
    from flat import hexc, with_alpha
    max_w = max_w or (W - 2 * SAFE)
    size = fit_size(text, size, max_w, weight)
    f = font(size, weight)
    w = f.measureText(text)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    x0 = clamp(x0, SAFE, W - SAFE - w)  # never overflow the safe area
    blob = skia.TextBlob(text, f)
    if shadow > 0:
        sp = skia.Paint(AntiAlias=True, Color=with_alpha(hexc("#000000"), 0.45 * alpha))
        sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, shadow))
        canvas.drawTextBlob(blob, x0 + shadow * 0.3, y + shadow * 0.6, sp)
    if stroke > 0:
        sp = skia.Paint(AntiAlias=True, Color=with_alpha(hexc(stroke_color), alpha), Style=skia.Paint.kStroke_Style,
                        StrokeWidth=stroke, StrokeJoin=skia.Paint.kRound_Join)
        canvas.drawTextBlob(blob, x0, y, sp)
    canvas.drawTextBlob(blob, x0, y, skia.Paint(AntiAlias=True, Color=with_alpha(hexc(color), alpha)))
    return skia.Rect.MakeXYWH(x0, y - size * 0.75, w, size)


# ============================================================================ one-point perspective camera

class Cam1P:
    """Simple one-point perspective for rooms/corridors.

    World: x right (units ~ cm), h up from the floor, z depth away from the camera.
    Screen: vanishing point (vx, vy) = horizon; camera height cam_h; focal f (px at z = 1 unit scale).
    project(x, h, z) -> (sx, sy, s) with s the pixel-per-unit scale at that depth (use it to scale puppets).
    """

    def __init__(self, vx=W / 2, vy=H * 0.42, cam_h=160.0, f=900.0, cam_x=0.0, cam_z=0.0):
        self.vx, self.vy, self.cam_h, self.f, self.cam_x, self.cam_z = vx, vy, cam_h, f, cam_x, cam_z

    def scale(self, z):
        return self.f / max(1e-3, z - self.cam_z)

    def project(self, x, h, z):
        s = self.scale(z)
        return self.vx + (x - self.cam_x) * s, self.vy + (self.cam_h - h) * s, s

    def quad(self, pts3):
        return [self.project(*p)[:2] for p in pts3]

    def floor_y(self, z):
        return self.project(0, 0, z)[1]

    def z_for_floor_y(self, sy):
        """Inverse: depth of the floor point that appears at screen y."""
        return self.cam_z + self.f * self.cam_h / max(1e-3, sy - self.vy)


# ============================================================================ canvas helpers

def new_surface(w=W, h=H):
    return skia.Surface(w, h)


def surface_to_array(surface):
    """-> HxWx3 uint8 RGB."""
    img = surface.makeImageSnapshot()
    arr = img.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
    return arr[:, :, :3].copy()


def save_png(surface, path):
    surface.makeImageSnapshot().save(str(path), skia.kPNG)
