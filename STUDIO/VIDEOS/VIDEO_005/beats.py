"""Story beats for VIDEO_005 (OPEN 24/7 - Part 1).

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
        d = n / 3.3 + 0.15
        if ln.get("at") is not None:
            t = max(t, float(ln["at"]))
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
B["title_out"] = 2.0
B["chime_ghost"] = word("S04", "chime")
B["s17"] = max(38.5, end("S16") + 0.3)            # quiet beat: no VO, "YOUR COMMENT COULD DECIDE PART 2"
B["customer"] = start("S18")
B["mop"] = start("S21a") + 0.5
B["leaves"] = start("S22")
B["ring333"] = start("S23")
B["ring_stop"] = start("S26") + 0.3
B["ring334"] = start("S27")
B["lights_die"] = start("S28")
B["glitch"] = start("S29") + 0.4                   # CUSTOMERS glitches 2 -> 4
B["touch"] = start("S32")
B["freeze"] = end("S32") + 0.25
B["choice"] = max(78.5, B["freeze"] + 0.9)
DURATION = round(max(84.0, B["choice"] + 5.5), 2)
