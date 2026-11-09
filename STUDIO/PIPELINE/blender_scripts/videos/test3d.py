"""3D smoke test: living room, one rigged character who waves, blinks and talks; two cameras.

Template for videos/videoNNN.py: a module with build(timing=None) and a JOBS table.
JOBS: job -> dict(camera=<object name>, start=<scene frame of source time 0>, end=<last frame>)
"""
import json
from pathlib import Path

from studio_lib import cameras, characters, lights, scene, sets, toon

JOBS = {
    "wide": dict(camera="CamWide", start=1, end=90),
    "close": dict(camera="CamClose", start=1, end=90),
}

TOON = True


def build(timing_path=None):
    sc = scene.reset()
    scene.fast_eevee(sc)
    sc.frame_end = 90
    sets.living_room()
    mia = characters.make_character("Mia", dict(skin="#e9b896", hair="#2f2019", shirt="#d4704f", pants="#34495e",
                                                hair_style="bob"), location=(0.3, 2.6, 0))
    lights.three_point(target=(0.3, 2.6, 1.4), key_energy=500)
    lights.practical("LampBulb", (-1.8, 4.3, 1.55), 80)
    # performance: idle -> wave -> talk
    mia.pose(1, arm_r=(5, 6), arm_l=(5, 6))
    mia.pose(20, arm_r=(5, 6), arm_l=(5, 6))
    mia.pose(32, arm_r=(10, 150), elbow_r=-30, arm_l=(5, 6), head=(0, 0, -8))
    for f, e in ((40, -60), (48, -10), (56, -60), (64, -10)):
        mia.pose(f, arm_r=(10, 150), elbow_r=e, arm_l=(5, 6), head=(0, 0, -8))
    mia.pose(78, arm_r=(5, 6), arm_l=(5, 6))
    mia.expression(1, "neutral")
    mia.expression(30, "happy")
    mia.expression(70, "surprised")
    for f in (12, 50, 84):
        mia.blink(f)
    words = [dict(w="hi", start=1.2, end=1.45), dict(w="there", start=1.5, end=1.9)]
    if timing_path and Path(timing_path).exists():
        words = json.loads(Path(timing_path).read_text())["lines"][0]["words"]
    mia.lipsync(words)
    mia.look(1, 0, 0)
    mia.look(70, -1, 0.3)
    cam, tgt = cameras.camera("CamWide", (0.0, -2.2, 1.5), (0.2, 2.6, 1.15), lens=28)
    cameras.move(cam, tgt, [(1, (0.0, -2.2, 1.5), (0.2, 2.6, 1.15), 28), (90, (0.15, -1.6, 1.45), (0.25, 2.6, 1.2), 30)])
    cameras.camera("CamClose", (0.25, 1.35, 1.62), (0.3, 2.6, 1.6), lens=50)
    if TOON:
        toon.apply_toon()
    return sc
