"""Story beats for VIDEO_009 (THE LAST BELL - Part 1).

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
B["hook_red"] = 1.0                      # flash-forward: 0-1 laughing, 1-2 red, 2-3 door knock
B["hook_door"] = 2.0
B["hook_text"] = 3.0
B["story"] = start("P01") - 0.1          # back to the calm afternoon
B["alarm"] = word("P05", "emergency")
B["knocks"] = [end("P11") + 0.1, end("P11") + 0.55, end("P11") + 1.0]
B["knock2"] = start("P15")
B["photo"] = start("P22")
B["handle"] = start("P28")
B["freeze"] = end("P30") + 0.25
B["choice"] = B["freeze"] + 0.8
DURATION = round(max(end("P31") + 3.6, B["choice"] + 4.5), 2)


def red(t):
    """0 = warm afternoon, 1 = lockdown red (also during the hook's flash-forward)."""
    if B["hook_red"] <= t < B["story"]:
        return 1.0
    if t >= B["alarm"]:
        return min(1.0, (t - B["alarm"]) / 0.4)
    return 0.0
