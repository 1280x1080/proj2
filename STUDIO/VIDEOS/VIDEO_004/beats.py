"""Story beats for VIDEO_004 (THE ROOM THAT WASN'T THERE - Part 1).

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
        d = n / 2.6 + 0.15
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
B["title_out"] = min(2.7, end("R01") + 0.15)
B["clock_flip"] = 0.3                             # 3:16 -> 3:17 on screen
B["ring"] = start("R02") - 0.25
B["answer"] = word("R03", "answer.")
B["knocking"] = word("R06", "knocking")
B["knocks"] = [end("R07") + 0.12, end("R07") + 0.62, end("R07") + 1.12]   # the three slow knocks, in the pause
B["text1"] = start("R09") - 0.3
B["text2"] = start("R11") - 0.3
B["knock_stop"] = start("R14")
B["silence"] = word("R14", "silence.")
B["own_voice"] = start("R16")
B["handle"] = word("R17", "handle")
B["creak"] = word("R20", "creak")
B["text3"] = start("R22") - 0.3
B["small_door"] = word("R24", "small")         # DOORS 1 -> 2
B["scratch"] = start("R25")
B["found_me"] = start("R27")
B["freeze"] = end("R27") + 0.3
B["choice"] = start("R28") - 0.1
CHOICE_HOLD = 2.2
DURATION = round(end("R31") + CHOICE_HOLD, 2)
