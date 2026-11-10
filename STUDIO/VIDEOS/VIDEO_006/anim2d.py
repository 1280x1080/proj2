"""VIDEO_006 - the porch of an old house at midnight; Mia (left) and Kai (the mascot, right) with a flashlight."""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "PIPELINE" / "twod"))
sys.path.insert(0, str(HERE))
import skia  # noqa: E402

import flat  # noqa: E402
import kit  # noqa: E402
from beats import TIMING, start  # noqa: E402
from flat import CAST, Light, Puppet, blob, glow, paint, poly_path  # noqa: E402
from kit import H, W, blink, span  # noqa: E402

MIA = Puppet(CAST["mia"], "mia")
KAI = Puppet(CAST["mascot"], "kai")
MOON = "#9fb6ff"


def flashlight(c, x, y, ang):
    c.save()
    c.rotate(ang - 90 + 70, x, y)
    c.drawRoundRect(skia.Rect.MakeLTRB(x - 14, y - 70, x + 14, y + 10), 6, 6, paint("#2b2f36"))
    c.restore()


def shot_porch(c, t):
    flat.linear_grad(c, (0, 0, W, H), ["#070b18", "#141c33"])
    c.drawCircle(860, 260, 70, paint("#eef2ff"))
    glow(c, 860, 260, 300, MOON, 0.25)
    # the old house: dark facade, porch door, one dim window
    c.drawPath(poly_path([(60, 520), (540, 220), (1020, 520)]), paint("#0e1220"))
    c.drawRect(skia.Rect.MakeLTRB(90, 520, 990, 1500), paint("#121828"))
    for k in range(9):
        c.drawLine(90, 560 + k * 100, 990, 560 + k * 100, paint("#000000", 0.25, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(430, 760, 650, 1420), paint("#05070c"))
    c.drawRect(skia.Rect.MakeLTRB(430, 760, 650, 1420), paint("#2a3248", stroke=12))
    flick = 0.5 + 0.5 * kit.flicker(t, 1.0, 0.8, 2, rate=4)
    c.drawRect(skia.Rect.MakeLTRB(180, 620, 320, 760), paint("#d8b46a", 0.35 * flick))
    glow(c, 250, 690, 200, "#ffcf8a", 0.12 * flick)
    c.drawRect(skia.Rect.MakeLTRB(0, 1420, W, H), paint("#1a2030"))  # porch boards
    for k in range(6):
        c.drawLine(0, 1460 + k * 80, W, 1460 + k * 80, paint("#000000", 0.3, stroke=3))
    # flashlight beam from Kai toward the door
    flat.light_cone(c, (700, 1130), (420, 760), (640, 1420), "#fff2c8", 0.22)
    L = Light(dir=(0.5, -0.7), shadow_px=16, rim=MOON, rim_alpha=0.7, rim_px=5)
    mia_talk = TIMING.mouth(t, "mia") if TIMING else 0.0
    kai_talk = TIMING.mouth(t, "kai") if TIMING else 0.0
    mia_on = t >= start("D2") - 0.1
    kai_on = t >= start("D3") - 0.1
    MIA.draw(c, 320, 1880, 1.15, dict(breathe=t, eye_open=blink(t, seed=61), turn=0.45, pupil=(0.7, 0.0),
                                      mouth="smirk" if mia_on else "smile", talk=mia_talk, brow=(0.3, 0.0),
                                      arm_r=(25, 120) if mia_on else (10, 14)), light=L)
    KAI.draw(c, 760, 1880, 1.15, dict(breathe=t, eye_open=blink(t, seed=62), turn=-0.45, pupil=(-0.7, 0.0),
                                      mouth="o" if kai_on else "flat", talk=kai_talk,
                                      brow=(0.9, 0.9) if kai_on else (0.5, 0.6), arm_r=(35, 95), hold_r=flashlight,
                                      crouch=0.05 * math.sin(math.pi * span(t, start("D3"), start("D3") + 0.4, "linear"))),
             light=L, facing=1)
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#3a4a80", 0.25, blend=skia.BlendMode.kMultiply))
    flat.vignette(c, W, H, 0.5)


SHOTS = dict(porch=shot_porch)
