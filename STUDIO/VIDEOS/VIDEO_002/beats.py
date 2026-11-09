"""Story beats for VIDEO_002 (5 s mascot test), from word timing."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "PIPELINE" / "twod"))
from kit import Timing  # noqa: E402

TIMING = Timing(HERE / "audio" / "timing.json")
L1 = TIMING.line("L1")

B = {}
B["land"] = 0.22                                   # drops into frame on frame 0, lands here
B["yo"] = TIMING.word("L1", "yo!")["start"]
B["mascot"] = TIMING.word("L1", "mascot.")["start"]
B["studio"] = TIMING.word("L1", "studio,")["start"]
B["cap"] = TIMING.word("L1", "cap.")["start"]      # taps the cap
B["line_end"] = L1["end"]
B["wink"] = B["line_end"] + 0.15
DURATION = 5.0
