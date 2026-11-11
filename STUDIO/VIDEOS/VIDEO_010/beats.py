"""Story beats for VIDEO_010 (FLIGHT 417 - Part 1).

One script line = one scene, so every cut sits on a line start.  Once narrate.py has run, times come
from audio/timing.json (word level).  Before that, times are ESTIMATED from word counts
(2.6 words/s + pause_after) so the scene plan / animatic can be timed; ESTIMATED = True then.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "PIPELINE" / "twod"))

SCRIPT = json.loads((HERE / "script.json").read_text())
_timing_path = HERE / "audio" / "timing.json"
ESTIMATED = not _timing_path.exists()

if not ESTIMATED:
    from kit import Timing  # noqa: E402
    TIMING = Timing(_timing_path)
    LINES = {ln["id"]: ln for ln in TIMING.data["lines"]}
else:
    TIMING = None
    LINES, t = {}, float(SCRIPT.get("lead_in", 0.3))
    for ln in SCRIPT["lines"]:
        n = len(ln["text"].split())
        d = n / 3.0 + 0.15
        LINES[ln["id"]] = dict(id=ln["id"], who=ln["who"], text=ln["text"], start=round(t, 2), end=round(t + d, 2))
        t += d + ln.get("pause_after", 0.3)


def start(lid):
    return LINES[lid]["start"]


def end(lid):
    return LINES[lid]["end"]


def word(lid, w):
    """Start time of a word (exact with timing.json; estimated by word position otherwise)."""
    if TIMING:
        return TIMING.word(lid, w)["start"]
    toks = [t.lower().strip('"') for t in LINES[lid]["text"].split()]
    i = toks.index(w.lower().strip('"'))
    return start(lid) + (end(lid) - start(lid)) * i / len(toks)


B = {}
B["hook_ghost"] = word("H1", "vanished") - 0.9   # hook: radar blip dies -> flash-forward of the ghost plane
B["story"] = start("L01") - 0.08
B["vanish"] = word("L02", "vanished.")
B["tonight"] = start("L03") - 0.08
B["flicker"] = word("L06", "flicker.")
B["black"] = word("L06", "Every")
B["plane"] = word("L08", "Another")
B["point"] = word("L12", "points")
B["unbuckle"] = word("L15", "unbuckles")
B["door"] = start("L17")
B["freeze"] = end("L17") + 0.15
B["choice"] = B["freeze"] + 0.7
DURATION = round(max(end("L18") + 3.4, B["choice"] + 4.5), 2)


def dark(t):
    """0 = normal night cabin, 1 = emergency lighting (after the flicker).  Flickers for 0.7 s first."""
    import math
    f = B["flicker"]
    if t < f:
        return 0.0
    if t < f + 0.7:
        return 1.0 if math.sin((t - f) * 43) > 0.1 else 0.0
    return 1.0
