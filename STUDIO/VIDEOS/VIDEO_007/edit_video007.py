"""EDL for VIDEO_007 - 5 s standards test: lights out, Kai panics, Mia answers from behind him."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, DURATION, ESTIMATED, end, start  # noqa: E402,F401
from anim2d import KAI_FACE, MID_TWO  # noqa: E402

BEATS = B
RED, YEL = "#e8423a", "#ffd23f"
SEGMENTS = [  # absolute shot time (engine default)
    dict(t0=0.0, t1=start("T2") - 0.08, src="hall", fx=[dict(fx="zoom", keys=[(0.0, 1.0, MID_TWO), (start("T2"), 1.08, MID_TWO)])]),
    dict(t0=start("T2") - 0.08, t1=start("T3") - 0.08, src="hall",
         fx=[dict(fx="zoom", keys=[(start("T2") - 0.08, 1.55, KAI_FACE), (start("T3"), 1.62, KAI_FACE)])]),
    dict(t0=start("T3") - 0.08, t1=DURATION, src="hall",
         fx=[dict(fx="zoom", keys=[(start("T3") - 0.08, 1.3, MID_TWO), (DURATION, 1.38, MID_TWO)])]),
]
SOURCES = {"hall": dict(kind="2d", shot="hall")}
OVERLAYS = [dict(kind="chip", t0=0.1, t1=DURATION, text="STANDARDS TEST", size=26, y=0.05, bg="#15161b", color="#d7d7dc")]
CAPTIONS = dict(timing="audio/timing.json", y=0.75, size=84, max_words=5, highlight="#ffffff", upper=True, speakers=True,
                speaker_colors={"mia": "#ff9ec4", "kai": "#9fd3ff"},
                line_colors={"T1": {"out.": RED}, "T2": {"where": YEL}, "T3": {"behind": RED}})
AUDIO = "audio/mix_master.wav"
