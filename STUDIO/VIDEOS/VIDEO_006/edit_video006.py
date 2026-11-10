"""EDL for VIDEO_006 - 5 s Qwen3-TTS demo: narrator + a two-person exchange (speaker labels on)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, DURATION, ESTIMATED, end, start  # noqa: E402,F401

BEATS = B
RED, YEL = "#e8423a", "#ffd23f"
MIA_FACE, KAI_FACE, MID = (320, 1080), (760, 1060), (540, 1000)  # zoom about the real face centres

SEGMENTS = [
    dict(t0=0.0, t1=start("D2") - 0.08, src="porch", fx=[dict(fx="zoom", keys=[(0.0, 1.0, MID), (start("D2"), 1.07, MID)])]),
    dict(t0=start("D2") - 0.08, t1=start("D3") - 0.08, src="porch",
         fx=[dict(fx="zoom", keys=[(start("D2") - 0.08, 1.75, MIA_FACE), (start("D3"), 1.82, MIA_FACE)])]),
    dict(t0=start("D3") - 0.08, t1=DURATION, src="porch",
         fx=[dict(fx="zoom", keys=[(start("D3") - 0.08, 1.75, KAI_FACE), (DURATION, 1.85, KAI_FACE)]),
             dict(fx="shake", t0=start("D3"), t1=start("D3") + 0.3, amp=6, freq=18)]),
]
SOURCES = {"porch": dict(kind="2d", shot="porch")}
OVERLAYS = [
    dict(kind="chip", t0=0.1, t1=DURATION, text="DEMO · QWEN3-TTS VOICES", size=26, y=0.05, bg="#15161b", color="#d7d7dc"),
]
CAPTIONS = dict(timing="audio/timing.json", y=0.75, size=84, max_words=5, highlight="#ffffff", upper=True,
                speakers=True, speaker_colors={"mia": "#ff9ec4", "kai": "#9fd3ff"},
                line_colors={"D1": {"dare.": RED}, "D2": {'first."': YEL}, "D3": {"way.": RED}})
AUDIO = "audio/mix_master.wav"
