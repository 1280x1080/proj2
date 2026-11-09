"""VIDEO_003 - ANIMATIC shots (placeholders until the real 2D shots are drawn).

Every shot name used in edit_video003.SCENES draws a lit placeholder card: lighting state of the
scene (FLUO / DIM / RED / LOBBY), the shot name and the scene's visual description, kept clear
of the HUD (top), rule cards (13-21 %), captions (64 % / 80 %).  Replace one shot at a time with
real drawings: add shot_<name>(canvas, t) and put it in SHOTS - the edit picks it up unchanged.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "PIPELINE" / "twod"))
sys.path.insert(0, str(HERE))
import skia  # noqa: E402

import flat  # noqa: E402
import kit  # noqa: E402
from kit import H, W  # noqa: E402
import edit_video003 as E  # noqa: E402

B = E.B
SEG = sorted(E.SEGMENTS, key=lambda s: s["t0"])
SC = {s["id"]: s for s in E.SCENES}
LIGHT = {  # background gradient top, bottom, accent
    "FLUO": ("#1f2c33", "#0d1418", "#cfe3e8"),
    "DIM": ("#141a1e", "#070a0c", "#7d8f94"),
    "RED": ("#4a0d0b", "#140302", "#ff6b5a"),
    "LOBBY": ("#4a2a12", "#1a0f06", "#ffcf8a"),
}


def scene_at(t):
    cur = SEG[0]
    for s in SEG:
        if s["t0"] <= t:
            cur = s
    return SC[cur["scene"]]


def light_state(t, sc):
    if sc["id"] in ("S26", "S28") or (B["bell"] <= t < B["stay"] and sc["shot"] == "lobby_pov"):
        return "LOBBY"
    if t >= B["drop"]:
        return "RED"
    if t >= B["lights_die"]:
        return "DIM"
    return "FLUO"


def placeholder(c, t):
    sc = scene_at(t)
    st = light_state(t, sc)
    top, bot, acc = LIGHT[st]
    flat.linear_grad(c, (0, 0, W, H), [top, bot])
    if st == "DIM":  # dying fluorescent flicker
        c.drawRect(skia.Rect.MakeWH(W, H), flat.paint("#000000", 0.35 * (1 - kit.flicker(t, 1.0, 0.8, 3))))
    # simple elevator frame lines so the space reads (doors + ceiling panels)
    line = flat.paint(acc, 0.18, stroke=6)
    c.drawRect(skia.Rect.MakeLTRB(170, 520, 910, 1500), line)
    c.drawLine(540, 520, 540, 1500, line)
    for i in range(3):
        c.drawRect(skia.Rect.MakeLTRB(250 + i * 200, 470, 410 + i * 200, 500), flat.paint(acc, 0.35 if st != "RED" else 0.1))
    flat.glow(c, 540, 480, 520, acc, 0.12)
    # shot label + description (between the rule cards and the captions); kept off the title card
    # and the choice screen, which carry their own text
    if sc["shot"] == "choice_bg" or t < B["title_out"] + 0.05:
        flat.vignette(c, W, H, 0.5)
        return
    kit.draw_text(c, sc["shot"].upper().replace("_", " "), W / 2, 600, 70, color=acc, weight="Black", stroke=10,
                  stroke_color="#000000")
    kit.draw_text(c, f'{sc["id"]} · {st}', W / 2, 660, 34, color="#ffffff", weight="Bold", alpha=0.7)
    lines = kit.wrap(sc["visual"], 38, W - 2 * kit.SAFE - 120, "SemiBold")[:7]
    for i, ln in enumerate(lines):
        kit.draw_text(c, ln, W / 2, 740 + i * 50, 38, color="#e8e8ea", weight="SemiBold", alpha=0.85)
    kit.draw_text(c, "ANIMATIC · placeholder shot", W / 2, 1860, 28, color="#ffffff", weight="Bold", alpha=0.35)
    flat.vignette(c, W, H, 0.5)


SHOTS = {name: placeholder for name in {s["shot"] for s in E.SCENES}}
