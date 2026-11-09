"""edl_engine.py - compositor: EDL module -> finished 1080x1920 H.264/AAC mp4.

An EDL is a Python module (VIDEOS/VIDEO_NNN/edit_videoNNN.py) defining:

    DURATION  = 10.0
    SOURCES   = {"room": dict(kind="2d", shot="room"),                       # anim2d.SHOTS["room"](canvas, t)
                 "wide": dict(kind="frames", dir="renders/wide", fps=30)}    # Blender PNGs f_0001.png ...
    SEGMENTS  = [dict(t0=0, t1=4, src="room", offset=0.0, speed=1.0, fx=[...]), ...]
    OVERLAYS  = [dict(kind="title", t0=0.2, t1=2.5, text="...", y=0.18), ...]
    CAPTIONS  = dict(timing="audio/timing.json", y=0.72, emphasis=["word"], speakers=False,
                     overrides=[(t0, t1, y)], offset=0.0)
    AUDIO     = "audio/mix_master.wav"

Segment fields
    src       source name, or [a, b] with split="h"|"v" for split screens
    offset    source time at t0 (default 0)   speed (default 1)   src_t: callable(t_out) -> t_src (overrides)
    freeze    source time to hold (freeze frame)
    fx        list of effects (times are absolute output times):
        {"fx":"zoom", "keys":[(t, scale, (cx, cy)), ...], "ease":"inout"}  punch-in / slow push
        {"fx":"shake", "t0":..,"t1":..,"amp":18, "freq":14}
        {"fx":"flash", "t":.., "dur":0.25, "color":"#ffffff"}
        {"fx":"whip",  "t":.., "dur":0.22, "dir":(1,0)}               whip pan w/ motion blur centred on t
        {"fx":"tint",  "color":"#2a62ff", "amount":0.35, "t0":.., "t1":..}  (freeze-frame tint)
        {"fx":"vhs",   "t0":.., "t1":..}                               rewind look (pair with src_t going backwards)
        {"fx":"pixelate", "t0":.., "t1":.., "block":28}
        {"fx":"vignette", "strength":0.4}
        {"fx":"black", "t0":.., "t1":..}                               hard cut to black
        {"fx":"fade", "t0":.., "t1":.., "from":0, "to":1, "color":"#000000"}

Everything is 2D, so fixes never need a source re-render.  All overlays/captions go through
paste(), which keeps them inside the safe area (>= SAFE px margins, shrink to fit).

CLI:
    python edl_engine.py VIDEOS/VIDEO_001/edit_video001.py [--out EXPORTS/x.mp4] [--frames 0:60]
                         [--still 3.5 ...] [--workers 4] [--plan]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import multiprocessing as mp
import os
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
import skia

PIPE = Path(__file__).resolve().parents[1]
STUDIO = PIPE.parent
sys.path.insert(0, str(PIPE / "twod"))
import flat  # noqa: E402
import kit  # noqa: E402
from kit import FPS, H, SAFE, W  # noqa: E402

# ============================================================================ loading

def load_module(path, name=None):
    path = Path(path).resolve()
    if str(path.parent) not in sys.path:
        sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name or path.stem, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Edit:
    def __init__(self, edl_path):
        self.path = Path(edl_path).resolve()
        self.dir = self.path.parent
        self.m = load_module(self.path)
        self.duration = float(self.m.DURATION)
        self.sources = getattr(self.m, "SOURCES", {})
        self.segments = sorted(getattr(self.m, "SEGMENTS", []), key=lambda s: s["t0"])
        self.overlays = getattr(self.m, "OVERLAYS", [])
        self.captions_cfg = getattr(self.m, "CAPTIONS", None)
        self.audio = getattr(self.m, "AUDIO", None)
        self._anim = None
        self.captions = build_captions(self) if self.captions_cfg else []

    @property
    def nframes(self):
        return int(round(self.duration * FPS))

    @property
    def anim(self):
        if self._anim is None:
            self._anim = load_module(self.dir / "anim2d.py", "anim2d_" + self.dir.name)
        return self._anim

    def segment_at(self, t):
        cur = None
        for s in self.segments:
            if s["t0"] <= t < s["t1"] + 1e-9:
                cur = s
        return cur

    @staticmethod
    def src_time(seg, t):
        if "freeze" in seg:
            return seg["freeze"]
        if "src_t" in seg:
            return seg["src_t"](t)
        return seg.get("offset", 0.0) + (t - seg["t0"]) * seg.get("speed", 1.0)

    def plan(self):
        """[(frame, [(source, src_time), ...])] for every output frame - what the edit actually shows."""
        out = []
        for i in range(self.nframes):
            t = i / FPS
            seg = self.segment_at(t)
            uses = []
            if seg is not None:
                srcs = seg["src"] if isinstance(seg["src"], (list, tuple)) else [seg["src"]]
                st = self.src_time(seg, t)
                for s in srcs:
                    uses.append((s, st))
                for fx in seg.get("fx", []):  # whip blur samples neighbours
                    if fx["fx"] == "whip" and abs(t - fx["t"]) <= fx.get("dur", 0.22) / 2:
                        uses.append((srcs[0], st))
            out.append((i, uses))
        return out


# ============================================================================ sources

@lru_cache(maxsize=64)
def _load_png(path):
    data = skia.Data.MakeFromFileName(str(path))
    return skia.Image.MakeFromEncoded(data) if data else None


def draw_source(edit: Edit, canvas, name, t, matrix: skia.Matrix | None = None):
    """Draw source `name` at source time t into canvas (full frame), with an optional 2D matrix."""
    spec = edit.sources.get(name, dict(kind="2d", shot=name))
    canvas.save()
    if matrix is not None:
        canvas.concat(matrix)
    kind = spec.get("kind", "2d")
    if kind == "2d":
        edit.anim.SHOTS[spec.get("shot", name)](canvas, t)
    elif kind == "frames":
        fps = spec.get("fps", FPS)
        fr = int(round(t * fps)) + spec.get("first", 1)
        d = edit.dir / spec["dir"]
        fr = max(spec.get("first", 1), fr)
        img = None
        while img is None and fr >= spec.get("first", 1):
            p = d / f"f_{fr:04d}.png"
            img = _load_png(p) if p.exists() else None
            fr -= 1
        if img is None:
            canvas.drawRect(skia.Rect.MakeWH(W, H), flat.paint("#ff00ff"))  # missing-frame marker
        else:
            canvas.drawImageRect(img, skia.Rect.MakeWH(W, H), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    elif kind == "color":
        canvas.drawRect(skia.Rect.MakeWH(W, H), flat.paint(spec["color"]))
    canvas.restore()


# ============================================================================ segment effects

def _active(fx, t):
    return fx.get("t0", -1e9) <= t <= fx.get("t1", 1e9)


def scale_about(s, cx, cy):
    return skia.Matrix.Concat(skia.Matrix.Translate(cx, cy),
                              skia.Matrix.Concat(skia.Matrix.Scale(s, s), skia.Matrix.Translate(-cx, -cy)))


def zoom_matrix(seg, t):
    m = skia.Matrix()
    for fx in seg.get("fx", []):
        if fx["fx"] == "zoom" and _active(fx, t):
            keys = kit.Keys([(k[0], (k[1], k[2][0], k[2][1]), fx.get("ease", "inout")) for k in fx["keys"]])
            s, cx, cy = keys(t)
            cx *= W if cx <= 1.0 else 1
            cy *= H if cy <= 1.0 else 1
            # scale about (cx, cy) but keep the frame covered
            z = scale_about(s, cx, cy)
            m = skia.Matrix.Concat(m, z)
        elif fx["fx"] == "shake" and _active(fx, t):
            amp = fx.get("amp", 18) * (1 - kit.span(t, fx.get("t0", t), fx.get("t1", t + 1), "linear")) \
                if fx.get("decay", True) else fx.get("amp", 18)
            f = fx.get("freq", 14)
            dx = kit.wiggle(t, f, amp, 3)
            dy = kit.wiggle(t, f, amp, 9)
            sc = 1 + 2.2 * fx.get("amp", 18) / W  # overscan so edges never show
            sh = skia.Matrix.Translate(dx, dy)
            sh = skia.Matrix.Concat(sh, scale_about(sc, W / 2, H / 2))
            m = skia.Matrix.Concat(sh, m)
    return m


def render_segment_picture(edit: Edit, seg, t):
    """Base picture for one output time (source + zoom/shake/whip/split) -> skia.Image."""
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    c.clear(skia.ColorBLACK)
    if seg is None:
        return surf.makeImageSnapshot()
    st = edit.src_time(seg, t)
    m = zoom_matrix(seg, t)
    srcs = seg["src"] if isinstance(seg["src"], (list, tuple)) else [seg["src"]]
    if len(srcs) == 2:
        horiz = seg.get("split", "h") == "h"  # h = top/bottom halves (stacked)
        for i, s in enumerate(srcs):
            c.save()
            if horiz:
                c.clipRect(skia.Rect.MakeXYWH(0, i * H / 2, W, H / 2))
                c.translate(0, -H / 4 + i * H / 2)
            else:
                c.clipRect(skia.Rect.MakeXYWH(i * W / 2, 0, W / 2, H))
                c.translate(-W / 4 + i * W / 2, 0)
            draw_source(edit, c, s, st, m)
            c.restore()
        line = flat.paint("#ffffff", stroke=8)
        if horiz:
            c.drawLine(0, H / 2, W, H / 2, line)
        else:
            c.drawLine(W / 2, 0, W / 2, H, line)
    else:
        whip = next((fx for fx in seg.get("fx", []) if fx["fx"] == "whip"
                     and abs(t - fx["t"]) <= fx.get("dur", 0.22) / 2), None)
        if whip is None:
            draw_source(edit, c, srcs[0], st, m)
        else:
            # motion-blurred whip: several offset copies, offset peaks at the whip centre
            u = (t - whip["t"]) / (whip.get("dur", 0.22) / 2)  # -1..1
            dx, dy = whip.get("dir", (1, 0))
            strength = (1 - abs(u)) ** 0.7
            travel = (u if whip.get("travel", True) else 0) * W * 0.6
            layer = skia.Surface(W, H)
            draw_source(edit, layer.getCanvas(), srcs[0], st, m)
            img = layer.makeImageSnapshot()
            n = 9
            p = skia.Paint(AntiAlias=True)
            for k in range(n):
                off = (k / (n - 1) - 0.5) * strength * W * 0.35 + travel
                p.setAlphaf(1.0 if k == 0 else 1.0 / (k + 1))
                c.drawImage(img, -off * dx, -off * dy, skia.SamplingOptions(), p)
    return surf.makeImageSnapshot()


def apply_post(edit, seg, t, canvas):
    """Effects drawn on top of the base picture (flash, tint, black, fade, vignette)."""
    if seg is None:
        return
    for fx in seg.get("fx", []):
        k = fx["fx"]
        if k == "flash":
            dur = fx.get("dur", 0.25)
            u = (t - fx["t"]) / dur
            if 0 <= u <= 1:
                canvas.drawRect(skia.Rect.MakeWH(W, H), flat.paint(fx.get("color", "#ffffff"), (1 - u) ** 2))
        elif k == "tint" and _active(fx, t):
            p = flat.paint(fx.get("color", "#3060ff"), fx.get("amount", 0.35), blend=skia.BlendMode.kColor)
            canvas.drawRect(skia.Rect.MakeWH(W, H), p)
            canvas.drawRect(skia.Rect.MakeWH(W, H), flat.paint("#000000", 0.15))
        elif k == "vignette" and _active(fx, t):
            flat.vignette(canvas, W, H, fx.get("strength", 0.4))
        elif k == "black" and _active(fx, t):
            canvas.drawRect(skia.Rect.MakeWH(W, H), flat.paint("#000000"))
        elif k == "fade" and _active(fx, t):
            a = kit.lerp(fx.get("from", 0.0), fx.get("to", 1.0), kit.span(t, fx["t0"], fx["t1"], "linear"))
            canvas.drawRect(skia.Rect.MakeWH(W, H), flat.paint(fx.get("color", "#000000"), a))


def apply_pixel_fx(seg, t, arr):
    """Effects that need pixel access (pixelate, vhs).  arr: HxWx3 uint8."""
    if seg is None:
        return arr
    for fx in seg.get("fx", []):
        if fx["fx"] == "pixelate" and _active(fx, t):
            b = int(fx.get("block", 28))
            small = arr[::b, ::b]
            arr = np.repeat(np.repeat(small, b, 0), b, 1)[:H, :W]
        elif fx["fx"] == "vhs" and _active(fx, t):
            arr = vhs(arr, t)
    return np.ascontiguousarray(arr)


def vhs(arr, t):
    r = np.random.default_rng(int(t * 1000))
    out = arr.astype(np.int16)
    out[:, :, 0] = np.roll(out[:, :, 0], 6, axis=1)
    out[:, :, 2] = np.roll(out[:, :, 2], -5, axis=1)
    out[::3] = (out[::3] * 0.82).astype(np.int16)  # scanlines
    for _ in range(3):  # tracking bands
        y = int((t * 900 + r.integers(0, H)) % H)
        h = int(r.integers(8, 40))
        out[y:y + h] = np.roll(out[y:y + h], int(r.integers(-40, 40)), axis=1) + 25
    out += r.integers(-14, 14, out.shape[:2], dtype=np.int16)[:, :, None]
    return np.clip(out, 0, 255).astype(np.uint8)


# ============================================================================ paste (safe-area enforcement)

def paste(canvas, img: skia.Image, cx, cy, scale=1.0, alpha=1.0, rot=0.0, margin=SAFE):
    """Draw an overlay image centred at (cx, cy); shrink + move so it stays fully inside the safe area."""
    w, h = img.width() * scale, img.height() * scale
    # bounding box of the rotated image
    a = math.radians(rot)
    bw = abs(w * math.cos(a)) + abs(h * math.sin(a))
    bh = abs(w * math.sin(a)) + abs(h * math.cos(a))
    maxw, maxh = W - 2 * margin, H - 2 * margin
    k = min(1.0, maxw / max(bw, 1), maxh / max(bh, 1))
    scale *= k
    bw, bh = bw * k, bh * k
    cx = min(max(cx, margin + bw / 2), W - margin - bw / 2)
    cy = min(max(cy, margin + bh / 2), H - margin - bh / 2)
    canvas.save()
    canvas.translate(cx, cy)
    canvas.rotate(rot)
    canvas.scale(scale, scale)
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(max(0.0, min(1.0, alpha)))
    canvas.drawImage(img, -img.width() / 2, -img.height() / 2, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    canvas.restore()
    return skia.Rect.MakeXYWH(cx - bw / 2, cy - bh / 2, bw, bh)


def _layer(w, h):
    s = skia.Surface(int(math.ceil(w)), int(math.ceil(h)))
    s.getCanvas().clear(skia.ColorTRANSPARENT)
    return s


def text_block(lines, size, color="#ffffff", weight="Black", stroke=0, stroke_color="#000000", pad=24,
               bg=None, bg_alpha=1.0, radius=28, line_gap=1.12, max_w=W - 2 * SAFE, colors=None):
    """Render centred multi-line text (optionally on a rounded box) into an image."""
    # shrink so the widest line fits
    s = size
    while s > 16 and max(kit.measure(l, s, weight) for l in lines) + 2 * pad + stroke > max_w:
        s *= 0.95
    f = kit.font(s, weight)
    widths = [f.measureText(l) for l in lines]
    lw = max(widths) + 2 * pad + stroke
    lh = len(lines) * s * line_gap + 2 * pad * 0.8
    surf = _layer(lw, lh)
    c = surf.getCanvas()
    if bg is not None:
        c.drawRoundRect(skia.Rect.MakeWH(lw, lh), radius, radius, flat.paint(bg, bg_alpha))
    for i, (l, w) in enumerate(zip(lines, widths)):
        x = (lw - w) / 2
        y = pad * 0.8 + s * 0.88 + i * s * line_gap
        blob = skia.TextBlob(l, f)
        if stroke:
            c.drawTextBlob(blob, x, y, skia.Paint(AntiAlias=True, Color=flat.hexc(stroke_color),
                                                  Style=skia.Paint.kStroke_Style, StrokeWidth=stroke,
                                                  StrokeJoin=skia.Paint.kRound_Join))
        col = colors[i] if colors else color
        c.drawTextBlob(blob, x, y, skia.Paint(AntiAlias=True, Color=flat.hexc(col)))
    return surf.makeImageSnapshot()


# ============================================================================ overlays

def _anim_in_out(ov, t, din=0.25, dout=0.2):
    u_in = kit.span(t, ov["t0"], ov["t0"] + ov.get("in", din), "linear")
    u_out = 1 - kit.span(t, ov["t1"] - ov.get("out", dout), ov["t1"], "linear")
    return u_in, u_out


def _pos(ov, dx=0.5, dy=0.2):
    x, y = ov.get("x", dx), ov.get("y", dy)
    return (x * W if x <= 1.0 else x), (y * H if y <= 1.0 else y)


def ov_title(ov, t, canvas):
    ui, uo = _anim_in_out(ov, t, 0.35, 0.25)
    lines = ov["text"].split("\n") if "\n" in ov["text"] else kit.wrap(ov["text"], ov.get("size", 110), W - 2 * SAFE - 60)
    img = text_block(lines, ov.get("size", 110), ov.get("color", "#ffffff"), stroke=ov.get("stroke", 14),
                     stroke_color=ov.get("stroke_color", "#1b1b1f"), bg=ov.get("bg"), bg_alpha=ov.get("bg_alpha", 0.9))
    cx, cy = _pos(ov, 0.5, 0.2)
    paste(canvas, img, cx, cy, scale=0.6 + 0.4 * kit.back_out(ui), alpha=min(ui * 2, 1) * uo)
    if ov.get("sub"):
        sub = text_block([ov["sub"]], ov.get("sub_size", 52), ov.get("sub_color", "#f4e9d0"), weight="Bold",
                         stroke=8, stroke_color="#1b1b1f")
        u2 = kit.span(t, ov["t0"] + 0.25, ov["t0"] + 0.55)
        paste(canvas, sub, cx, cy + img.height() / 2 + 40 + (1 - u2) * 20, alpha=u2 * uo)


def ov_stamp(ov, t, canvas):
    ui, uo = _anim_in_out(ov, t, 0.18, 0.2)
    col = ov.get("color", "#d8433a")
    lines = [ov["text"]]
    img0 = text_block(lines, ov.get("size", 96), col, pad=30)
    w, h = img0.width() + 16, img0.height() + 16
    surf = _layer(w, h)
    c = surf.getCanvas()
    c.drawRoundRect(skia.Rect.MakeXYWH(8, 8, w - 16, h - 16), 18, 18, flat.paint(ov.get("bg", "#fff6ea"), 0.94))
    c.drawRoundRect(skia.Rect.MakeXYWH(8, 8, w - 16, h - 16), 18, 18, flat.paint(col, stroke=10))
    c.drawImage(img0, 8, 8)
    cx, cy = _pos(ov, 0.5, 0.3)
    sc = 1.8 - 0.8 * kit.ease_out(ui, 4)
    paste(canvas, surf.makeImageSnapshot(), cx, cy, scale=sc, alpha=min(1, ui * 3) * uo, rot=ov.get("rot", -8))


def ov_chip(ov, t, canvas):
    ui, uo = _anim_in_out(ov, t, 0.22, 0.18)
    img = text_block([ov["text"]], ov.get("size", 46), ov.get("color", "#1b1b1f"), weight="ExtraBold",
                     bg=ov.get("bg", "#fff4dc"), radius=999, pad=22)
    cx, cy = _pos(ov, 0.5, 0.12)
    paste(canvas, img, cx, cy - (1 - kit.back_out(ui)) * 30, alpha=ui * uo)


def ov_counter(ov, t, canvas):
    ui, uo = _anim_in_out(ov, t)
    u = kit.span(t, ov.get("count_t0", ov["t0"]), ov.get("count_t1", ov["t1"] - 0.3), ov.get("ease", "out"))
    v = kit.lerp(ov["from"], ov["to"], u)
    fmt = ov.get("fmt", "{:,.0f}")
    lines = [fmt.format(v)] + ([ov["label"]] if ov.get("label") else [])
    img = text_block(lines, ov.get("size", 120), ov.get("color", "#ffffff"), stroke=12, stroke_color="#1b1b1f",
                     colors=[ov.get("color", "#ffffff"), ov.get("label_color", "#f2d48a")] if ov.get("label") else None)
    cx, cy = _pos(ov, 0.5, 0.25)
    paste(canvas, img, cx, cy, scale=0.8 + 0.2 * kit.back_out(ui), alpha=ui * uo)


def ov_timer(ov, t, canvas):
    ui, uo = _anim_in_out(ov, t)
    el = t - ov["t0"]
    v = ov.get("start", 0) + (-el if ov.get("down", False) else el) * ov.get("rate", 1.0)
    v = max(0, v)
    txt = f"{int(v // 60):02d}:{int(v % 60):02d}" + (f".{int((v * 10) % 10)}" if ov.get("tenths") else "")
    img = text_block([txt], ov.get("size", 84), ov.get("color", "#ffffff"), weight="Bold", bg="#121216",
                     bg_alpha=0.75, radius=20)
    cx, cy = _pos(ov, 0.5, 0.1)
    paste(canvas, img, cx, cy, alpha=ui * uo)


def ov_lower_third(ov, t, canvas):
    ui, uo = _anim_in_out(ov, t, 0.35, 0.25)
    name = text_block([ov["name"]], ov.get("size", 58), "#ffffff", weight="Black", bg=ov.get("bg", "#1d2b3a"),
                      radius=14, pad=20)
    role = text_block([ov.get("role", "")], ov.get("size", 58) * 0.6, "#1d2b3a", weight="Bold",
                      bg=ov.get("bg2", "#f2d48a"), radius=12, pad=16) if ov.get("role") else None
    x0 = SAFE + 30
    cy = _pos(ov, 0.5, 0.8)[1]
    slide = (1 - kit.ease_out(ui)) * -600
    paste(canvas, name, x0 + name.width() / 2 + slide, cy, alpha=uo)
    if role is not None:
        paste(canvas, role, x0 + 20 + role.width() / 2 + slide * 1.3, cy + name.height() / 2 + role.height() / 2 + 6,
              alpha=uo)


def ov_hud(ov, t, canvas):
    """items: [(label, keys)] where keys = [(t, value), ...]; a value change flashes for 0.4 s."""
    ui, uo = _anim_in_out(ov, t)
    parts = []
    for label, keys in ov["items"]:
        val, changed = keys[0][1], -9
        for kt, kv in keys:
            if t >= kt:
                val, changed = kv, kt
        fl = 1 - kit.span(t, changed, changed + 0.4, "linear")
        parts.append((label, str(val), fl))
    size = ov.get("size", 40)
    imgs = []
    for label, val, fl in parts:
        bg = flat.lerp_col(flat.hexc("#15161b"), flat.hexc(ov.get("flash", "#f2b134")), fl)
        imgs.append(text_block([f"{label} {val}"], size * (1 + 0.15 * fl), "#ffffff", weight="ExtraBold", bg=bg,
                               bg_alpha=0.82, radius=16, pad=16))
    gap = 18
    tw = sum(i.width() for i in imgs) + gap * (len(imgs) - 1)
    th = max(i.height() for i in imgs)
    surf = _layer(tw, th)
    c = surf.getCanvas()
    x = 0
    for i in imgs:
        c.drawImage(i, x, (th - i.height()) / 2)
        x += i.width() + gap
    cx, cy = _pos(ov, 0.5, 0.07)
    paste(canvas, surf.makeImageSnapshot(), cx, cy, alpha=ui * uo)


def ov_choices(ov, t, canvas):
    """Choice cards ('comment 1, 2 or 3'): options=[...], prompt='...'."""
    ui, uo = _anim_in_out(ov, t, 0.3, 0.25)
    cx, cy = _pos(ov, 0.5, 0.42)
    if ov.get("prompt"):
        pimg = text_block([ov["prompt"]], 64, "#ffffff", stroke=10, stroke_color="#1b1b1f")
        paste(canvas, pimg, cx, cy - 240, alpha=ui * uo)
    colors = ov.get("colors", ["#e2574c", "#3f8fd6", "#55a868", "#d9a43b"])
    for i, txt in enumerate(ov["options"]):
        d = kit.span(t, ov["t0"] + 0.12 * i, ov["t0"] + 0.12 * i + 0.35, "back")
        img = text_block([f"{i + 1}  {txt}"], ov.get("size", 56), "#ffffff", weight="ExtraBold",
                         bg=colors[i % len(colors)], radius=26, pad=26, max_w=W - 2 * SAFE - 40)
        paste(canvas, img, cx + (1 - d) * 700 * (1 if i % 2 else -1), cy - 90 + i * (img.height() + 26),
              alpha=min(1, d * 1.5) * uo)


def ov_text(ov, t, canvas):
    ui, uo = _anim_in_out(ov, t, 0.15, 0.15)
    lines = kit.wrap(ov["text"], ov.get("size", 64), W - 2 * SAFE - 50, ov.get("weight", "Black"))
    img = text_block(lines, ov.get("size", 64), ov.get("color", "#ffffff"), weight=ov.get("weight", "Black"),
                     stroke=ov.get("stroke", 10), stroke_color=ov.get("stroke_color", "#1b1b1f"), bg=ov.get("bg"),
                     bg_alpha=ov.get("bg_alpha", 0.85))
    cx, cy = _pos(ov, 0.5, 0.5)
    paste(canvas, img, cx, cy, alpha=ui * uo, rot=ov.get("rot", 0.0))


OVERLAY_KINDS = dict(title=ov_title, stamp=ov_stamp, chip=ov_chip, counter=ov_counter, timer=ov_timer,
                     lower_third=ov_lower_third, hud=ov_hud, choices=ov_choices, text=ov_text)

# ============================================================================ captions

def build_captions(edit: Edit):
    cfg = edit.captions_cfg
    timing = kit.Timing(edit.dir / cfg["timing"])
    off = cfg.get("offset", 0.0)
    maxw = cfg.get("max_words", 4)
    phrases = []
    for ln in timing.data["lines"]:
        cur = []
        for w in ln["words"]:
            cur.append(w)
            ends = w["w"].rstrip()[-1:] in ".,!?;:—–"
            if ends or len(cur) >= maxw:
                phrases.append((ln, cur))
                cur = []
        if cur:
            # avoid a dangling single word: merge into the previous phrase of the same line
            if len(cur) == 1 and phrases and phrases[-1][0] is ln and len(phrases[-1][1]) < maxw + 1:
                phrases[-1] = (ln, phrases[-1][1] + cur)
            else:
                phrases.append((ln, cur))
    caps = []
    for i, (ln, ws) in enumerate(phrases):
        t0 = ws[0]["start"] + off - 0.04
        t1 = ws[-1]["end"] + off + 0.25
        if i + 1 < len(phrases):
            t1 = min(t1, phrases[i + 1][1][0]["start"] + off - 0.04)
        caps.append(dict(t0=t0, t1=max(t1, t0 + 0.3), who=ln.get("who", "narrator"), line=ln.get("id"),
                         words=[dict(w, start=w["start"] + off, end=w["end"] + off) for w in ws]))
    return caps


def _cap_y(cfg, t):
    y = cfg.get("y", 0.72)
    for t0, t1, yy in cfg.get("overrides", []):
        if t0 <= t <= t1:
            y = yy
    return y * H if y <= 1 else y


def draw_captions(edit: Edit, canvas, t):
    cfg = edit.captions_cfg
    if not cfg:
        return
    cap = next((c for c in edit.captions if c["t0"] <= t < c["t1"]), None)
    if cap is None:
        return
    # per-line key-word colours (line_colors={line_id: {word: colour}}) replace the global emphasis list
    lc = cfg.get("line_colors")
    if lc is not None:
        colors = {kit._norm(k): v for k, v in lc.get(cap.get("line"), {}).items()}
    else:
        colors = {kit._norm(e): cfg.get("emphasis_color", "#ff8a3d") for e in cfg.get("emphasis", [])}
    emph = set(colors)
    size = cfg.get("size", 84)
    base_col = cfg.get("color", "#ffffff")
    hi_col = cfg.get("highlight", "#ffd23f")
    words = [w["w"].strip() for w in cap["words"]]
    if cfg.get("upper"):
        words = [w.upper() for w in words]
    # layout: one or two lines that fit inside the safe width
    maxw = W - 2 * SAFE - 40
    s = size
    lines = kit.wrap(" ".join(words), s, maxw)
    while len(lines) > 2 and s > 40:
        s *= 0.92
        lines = kit.wrap(" ".join(words), s, maxw)
    f = kit.font(s, "Black")
    space = f.measureText(" ")
    stroke = max(6, s * 0.16)
    gap = s * 1.12
    lw = max(f.measureText(l) for l in lines) * 1.15 + stroke * 2 + 20
    lh = gap * len(lines) + s * 0.4 + stroke
    if cfg.get("speakers") and cap["who"] != "narrator":
        lh += s * 0.75
    surf = _layer(lw + 40, lh + 40)
    c = surf.getCanvas()
    y = 20 + s * 0.9 + stroke / 2
    if cfg.get("speakers") and cap["who"] != "narrator":
        lab = cap["who"].upper()
        lf = kit.font(s * 0.5, "Black")
        lwid = lf.measureText(lab)
        lx = (lw + 40 - lwid) / 2
        c.drawRoundRect(skia.Rect.MakeXYWH(lx - 16, 14, lwid + 32, s * 0.62), 12, 12, flat.paint("#141418", 0.85))
        c.drawString(lab, lx, 14 + s * 0.5, lf,
                     skia.Paint(AntiAlias=True, Color=flat.hexc(cfg.get("speaker_colors", {}).get(cap["who"], "#9fd3ff"))))
        y += s * 0.75
    wi = 0
    for l in lines:
        lws = l.split(" ")
        n_em = sum(1 for w in lws if kit._norm(w) in emph)
        x = (lw + 40 - f.measureText(l) - n_em * s * 0.24) / 2
        for w in lws:
            em_pad = s * 0.12 if kit._norm(w) in emph else 0.0
            x += em_pad
            wd = cap["words"][wi]
            active = wd["start"] - 0.02 <= t <= wd["end"] + 0.06 or (t > wd["end"] and wi + 1 < len(cap["words"])
                                                                      and t < cap["words"][wi + 1]["start"])
            col = colors[kit._norm(w)] if kit._norm(w) in emph else (hi_col if active else base_col)
            blob = skia.TextBlob(w, f)
            pop = 1.0
            if kit._norm(w) in emph:
                pop = 1.0 + 0.12 * (1 - kit.span(t, wd["start"], wd["start"] + 0.2, "out"))
            c.save()
            ww = f.measureText(w)
            c.translate(x + ww / 2, y - s * 0.35)
            c.scale(pop, pop)
            c.translate(-(x + ww / 2), -(y - s * 0.35))
            c.drawTextBlob(blob, x, y, skia.Paint(AntiAlias=True, Color=flat.hexc("#141418"),
                                                  Style=skia.Paint.kStroke_Style, StrokeWidth=stroke,
                                                  StrokeJoin=skia.Paint.kRound_Join))
            c.drawTextBlob(blob, x, y, skia.Paint(AntiAlias=True, Color=flat.hexc(col)))
            c.restore()
            x += ww + space + em_pad
            wi += 1
        y += gap
    u = kit.span(t, cap["t0"], cap["t0"] + 0.1, "out")
    paste(canvas, surf.makeImageSnapshot(), W / 2, _cap_y(cfg, t), scale=0.92 + 0.08 * u, alpha=min(1.0, u * 1.5))


# ============================================================================ frame render

_EDIT: Edit | None = None


def _init_worker(edl_path):
    global _EDIT
    _EDIT = Edit(edl_path)


def render_frame(edit: Edit, i):
    t = i / FPS
    seg = edit.segment_at(t)
    base = render_segment_picture(edit, seg, t)
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    c.drawImage(base, 0, 0)
    apply_post(edit, seg, t, c)
    arr = kit.surface_to_array(surf)
    arr = apply_pixel_fx(seg, t, arr)
    if any(fx["fx"] in ("pixelate", "vhs") for fx in (seg or {}).get("fx", [])):
        surf = skia.Surface(W, H)
        c = surf.getCanvas()
        rgba = np.dstack([arr, np.full(arr.shape[:2], 255, np.uint8)])
        c.drawImage(skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType), 0, 0)
    for ov in edit.overlays:
        if ov["t0"] <= t < ov["t1"]:
            OVERLAY_KINDS[ov["kind"]](ov, t, c)
    draw_captions(edit, c, t)
    return kit.surface_to_array(surf)


def _worker_frame(i):
    return i, render_frame(_EDIT, i).tobytes()


def export(edl_path, out=None, frames=None, workers=None, crf=18, preset="slow"):
    edit = Edit(edl_path)
    num = edit.dir.name.split("_")[-1]
    out = Path(out) if out else STUDIO / "EXPORTS" / f"video{num}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    rng = range(*frames) if frames else range(edit.nframes)
    audio = edit.dir / edit.audio if edit.audio else None
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"]
    if audio and audio.exists():
        cmd += ["-ss", f"{rng.start / FPS:.4f}", "-t", f"{len(rng) / FPS:.4f}", "-i", str(audio)]
    cmd += ["-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
            "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709"]
    if audio and audio.exists():
        cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest"]
    else:
        print("WARNING: no audio file, exporting silent video")
    cmd += ["-movflags", "+faststart", str(out)]
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    workers = workers or max(1, (os.cpu_count() or 2))
    with mp.get_context("fork").Pool(workers, initializer=_init_worker, initargs=(str(edit.path),)) as pool:
        for n, (i, buf) in enumerate(pool.imap(_worker_frame, rng, chunksize=2)):
            proc.stdin.write(buf)
            if n % 30 == 0:
                el = time.time() - t0
                print(f"  frame {i}/{rng.stop}  {el:.1f}s  ({el / (n + 1):.3f} s/frame)", flush=True)
    proc.stdin.close()
    proc.wait()
    dt = time.time() - t0
    stats = dict(out=str(out), frames=len(rng), seconds=round(dt, 1), sec_per_frame=round(dt / max(1, len(rng)), 3),
                 workers=workers)
    print(json.dumps(stats))
    return stats


def stills(edl_path, times, out_dir):
    edit = Edit(edl_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for t in times:
        arr = render_frame(edit, int(round(t * FPS)))
        from PIL import Image
        p = out_dir / f"still_{t:06.2f}.png"
        Image.fromarray(arr).save(p)
        paths.append(p)
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edl")
    ap.add_argument("--out")
    ap.add_argument("--frames", help="a:b output frame range")
    ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--still-dir")
    ap.add_argument("--workers", type=int)
    ap.add_argument("--plan", action="store_true", help="print which source frames the edit uses")
    ap.add_argument("--preset", default="slow")
    a = ap.parse_args()
    if a.plan:
        for i, uses in Edit(a.edl).plan():
            print(i, uses)
        return
    if a.still:
        d = a.still_dir or (Path(a.edl).resolve().parent / "qc" / "stills")
        for p in stills(a.edl, a.still, d):
            print(p)
        return
    fr = tuple(int(x) for x in a.frames.split(":")) if a.frames else None
    export(a.edl, a.out, fr, a.workers, preset=a.preset)


if __name__ == "__main__":
    main()
