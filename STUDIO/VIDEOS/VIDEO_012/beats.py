"""Story beats for VIDEO_012 (ORDER #000 - Part 1).

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
B["story"] = start("L01") - 0.08
B["order"] = word("L02", "Order")
B["knocks"] = [end("L03") + 0.15, end("L03") + 0.55, end("L03") + 0.95]
B["scare1"] = end("L06") + 0.4                # JUMPSCARE 1: his face slams into the door camera
B["scare1_end"] = B["scare1"] + 0.7
B["gone"] = start("L07") - 0.08
B["stare"] = word("L09", "stopped")           # the streamer stops eating and looks at you
B["move"] = word("L11", "move.")
B["scare2"] = end("L11") + 0.5                # JUMPSCARE 2: something looks out of the bag
B["scare2_end"] = B["scare2"] + 0.75
B["freeze"] = B["scare2_end"]
B["choice"] = B["freeze"] + 0.5
DURATION = round(max(end("L12") + 3.6, B["choice"] + 4.5), 2)
