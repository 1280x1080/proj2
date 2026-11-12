"""Story beats for VIDEO_013 (AFTER HOURS - Part 1).

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
B["hook_cut"] = word("H1", "But") - 0.15       # hook: the five of you in the hallway -> the red pen grading by itself
B["story"] = start("L01") - 0.08
B["fail"] = word("L03", "fail.")
B["midnight"] = start("L05") - 0.08
B["graded"] = word("L06", "graded.")
B["scare1"] = end("L08") + 0.4                 # JUMPSCARE 1: the teacher's face at the door window
B["scare1_end"] = B["scare1"] + 0.7
B["slam"] = start("L09")
B["chalk"] = word("L11", "Kai.")
B["chalk_end"] = end("L11")
B["scare2"] = end("L11") + 0.5                 # JUMPSCARE 2: she is standing at the board
B["scare2_end"] = B["scare2"] + 0.75
B["choice"] = B["scare2_end"]
DURATION = round(max(end("L12") + 3.6, B["choice"] + 4.5), 2)
