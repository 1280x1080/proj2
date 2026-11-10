"""VIDEO_007 - hallway at night.  Every pose goes through flat.emote (face + body) and TIMING.lip (talking)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "PIPELINE" / "twod"))
sys.path.insert(0, str(HERE))
import skia  # noqa: E402

import flat  # noqa: E402
import kit  # noqa: E402
from beats import B, TIMING, end, start  # noqa: E402
from flat import CAST, Light, Puppet, emote, glow, paint, poly_path  # noqa: E402
from kit import H, W, blink, span  # noqa: E402

KAI, MIA = Puppet(CAST["mascot"], "kai"), Puppet(CAST["mia"], "mia")
KAI_AT, MIA_AT, SCALE_K, SCALE_M = (650, 1900), (330, 1830), 1.2, 1.05
WARM, MOON = "#ffd9a0", "#8fa8ff"


def _face(p, at, sc):
    x, y = p.head_pos(at[0], at[1], sc)
    r = p.HEAD_RX * p.s.head_scale * sc
    return (x - r * 1.15, y - r * 1.5, x + r * 1.15, y + r * 1.35)


KAI_FACE = tuple(int(v) for v in KAI.head_pos(*KAI_AT, SCALE_K))
MID_TWO = (int((KAI_FACE[0] + MIA.head_pos(*MIA_AT, SCALE_M)[0]) / 2), KAI_FACE[1])
ZONES = {"hall": lambda t: [("Kai's face", *_face(KAI, KAI_AT, SCALE_K))] +
         ([("Mia's face", *_face(MIA, MIA_AT, SCALE_M))] if t >= start("T3") - 0.3 else [])}


def lights(t):
    """1 = ceiling light on, 0 = out (a short flicker on the way down)."""
    if t < B["out"]:
        return 1.0
    u = t - B["out"]
    return 0.0 if u > 0.35 else (0.6 if int(u * 20) % 2 else 0.1)


def kai_pose(t):
    P = dict(eye_open=blink(t, seed=71), turn=0.05, pupil=(0.0, 0.0))
    P = emote(P, "neutral", t)
    P = emote(P, "nervous", t, amount=span(t, B["out"], B["out"] + 0.4))          # lights die -> nervous
    if t >= start("T2") - 0.15:
        P = emote(P, "scared", t, amount=span(t, start("T2") - 0.15, start("T2") + 0.2))
        P["pupil"] = (-0.5 + 0.9 * ((t * 1.3) % 1 > 0.5), 0.0)                    # eyes dart, searching
    if t >= start("T3"):  # listening to her: terrified, turning toward the voice behind him
        P = emote(P, "terrified", t, amount=span(t, start("T3"), start("T3") + 0.3))
        P.update(turn=-0.35 * span(t, start("T3") + 0.2, start("T3") + 0.8), pupil=(-0.8, 0.0))
    return TIMING.lip(P, t, "kai") if TIMING else P


def mia_pose(t):
    P = dict(eye_open=blink(t, seed=72), turn=0.4, pupil=(0.7, 0.05))
    P = emote(P, "teasing", t)
    return TIMING.lip(P, t, "mia") if TIMING else P


def shot_hall(c, t):
    lt = lights(t)
    flat.linear_grad(c, (0, 0, W, H), ["#3a3530", "#221e1b"])
    vx, vy = 540, 900
    c.drawPath(poly_path([(0, H), (W, H), (vx + 120, vy + 160), (vx - 120, vy + 160)]), paint("#2c2723"))  # floor
    c.drawPath(poly_path([(0, 0), (W, 0), (vx + 120, vy - 240), (vx - 120, vy - 240)]), paint("#2a2622"))  # ceiling
    c.drawRect(skia.Rect.MakeLTRB(vx - 120, vy - 240, vx + 120, vy + 160), paint("#1b2236"))                # far window
    c.drawRect(skia.Rect.MakeLTRB(vx - 120, vy - 240, vx + 120, vy + 160), paint("#4a4038", stroke=10))
    glow(c, vx, vy - 40, 360, MOON, 0.18)
    for s in (-1, 1):  # side doors
        for k, u in enumerate((0.2, 0.55)):
            xa, xb = (0 if s < 0 else W) + s * -1 * u * 420, (0 if s < 0 else W) + s * -1 * (u + 0.14) * 420
            c.drawPath(poly_path([(xa, 520 + u * 330), (xb, 520 + (u + 0.14) * 330), (xb, 1500 - (u + 0.14) * 300), (xa, 1500 - u * 300)]),
                       paint("#4a3a2c"))
    # ceiling light
    c.drawRoundRect(skia.Rect.MakeLTRB(420, 230, 660, 262), 10, 10, paint(WARM if lt > 0.5 else "#3a3632"))
    if lt > 0:
        glow(c, 540, 300, 900, WARM, 0.35 * lt)
    dark = 1 - lt
    # the room goes dark; the characters stay readable in moonlight (emotion must read with the sound off)
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#1a2448", 0.6 * dark, blend=skia.BlendMode.kMultiply))
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", 0.25 * dark))
    L = Light(dir=(0.0, -1.0), shadow_px=16, rim=WARM if lt > 0.5 else MOON, rim_alpha=0.6 if lt > 0.5 else 0.9, rim_px=6)
    # Mia, behind his shoulder, fades in out of the dark for her line
    a = span(t, start("T3") - 0.35, start("T3") + 0.1)
    if a > 0:
        c.saveLayerAlpha(None, int(255 * a))
        MIA.draw(c, *MIA_AT, SCALE_M, mia_pose(t), light=Light(dir=(0.6, -0.6), shadow_px=18, rim=MOON, rim_alpha=0.9, rim_px=6))
        c.restore()
    KAI.draw(c, *KAI_AT, SCALE_K, kai_pose(t), light=L)
    if dark > 0:  # cool moonlight cast on the characters (lighter than the room)
        c.drawRect(skia.Rect.MakeLTRB(150, 700, 950, H), paint("#6a7fc0", 0.22 * dark, blend=skia.BlendMode.kMultiply))
        glow(c, 540, 900, 700, MOON, 0.10 * dark)
    flat.vignette(c, W, H, 0.45 + 0.15 * dark)


SHOTS = dict(hall=shot_hall)
