"""Story beats for VIDEO_001, computed from the narration's word timing.

Every time in the edit, the animation, the SFX cues and the music comes from here, so
re-recording a line re-times the whole video automatically.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "PIPELINE" / "twod"))
from kit import Timing  # noqa: E402

TIMING = Timing(HERE / "audio" / "timing.json")
L1, L2 = TIMING.line("L1"), TIMING.line("L2")

B = {}
B["line1_start"] = L1["start"]
B["eleven"] = TIMING.word("L1", "eleven")["start"]
B["three"] = TIMING.word("L1", "three")["start"]
B["line1_end"] = L1["end"]
# the three normal flickers land on "exactly three times."; the fourth one is the twist
_t = TIMING.word("L1", "times.")
B["flicks"] = [B["three"] + 0.05, _t["start"] + 0.02, _t["end"] + 0.12]
B["reveal"] = B["line1_end"] + 0.75           # 4th flicker (nobody says it, we see it)
B["line2_start"] = L2["start"]
B["wait_end"] = TIMING.word("L2", "wait...")["end"]
B["four"] = TIMING.word("L2", "four.")["start"]
B["line2_end"] = L2["end"]
B["gate_start"] = B["reveal"] - 0.05
B["knock"] = B["line2_end"] + 0.9            # someone knocks: final beat
B["knocks"] = [B["knock"], B["knock"] + 0.24, B["knock"] + 0.48]
DURATION = max(10.0, round(B["knock"] + 1.6, 2))

FLICKS_ALL = B["flicks"] + [B["reveal"]]


def lamp_level(t):
    """1 = lamp on, ~0.1 = off.  Each flicker is a quick double dip."""
    lvl = 1.0
    for ft in FLICKS_ALL:
        u = t - ft
        if 0 <= u < 0.22:
            lvl = min(lvl, 0.12 if (u < 0.07 or 0.12 <= u < 0.17) else 0.75)
    return lvl


def flick_count(t):
    return sum(1 for ft in FLICKS_ALL if t >= ft)
