"""EDL for VIDEO_002 - mascot test (5 s, 2D)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, DURATION  # noqa: E402,F401

BEATS = B
FACE = (540, 860)

SOURCES = {"studio": dict(kind="2d", shot="studio")}

SEGMENTS = [
    dict(t0=0.0, t1=DURATION, src="studio",
         fx=[dict(fx="zoom", keys=[(0.0, 1.0, FACE), (B["studio"] - 0.2, 1.08, FACE), (B["studio"] + 0.05, 1.32, FACE),
                                   (B["cap"] + 0.1, 1.36, FACE), (B["wink"], 1.55, FACE), (DURATION, 1.6, FACE)]),
             dict(fx="shake", t0=B["land"], t1=B["land"] + 0.35, amp=16, freq=20),
             dict(fx="flash", t=B["wink"] + 0.05, dur=0.18, color="#fff4dc")]),
]

OVERLAYS = [
    dict(kind="chip", t0=B["land"] + 0.05, t1=B["studio"] - 0.1, text="NEW MASCOT", y=0.085, bg="#d0312d",
         color="#ffffff"),
    dict(kind="stamp", t0=B["cap"] + 0.05, t1=DURATION, text="FRESH CAP", y=0.16, rot=-6, color="#d0312d"),
]

CAPTIONS = dict(timing="audio/timing.json", y=0.71, size=84, emphasis=["mascot.", "cap."], speakers=False)

AUDIO = "audio/mix_master.wav"
