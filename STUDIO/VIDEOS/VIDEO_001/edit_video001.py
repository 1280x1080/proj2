"""EDL for VIDEO_001 - 'the fourth flicker' (10 s pipeline test, 2D mode).

All times come from beats.py (word timing), so a re-recorded line re-times the edit.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, DURATION, FLICKS_ALL  # noqa: E402,F401

BEATS = B

# screen positions (from the room camera in anim2d.py)
FACE = (658, 884)
DOOR = (850, 917)

SOURCES = {
    "room": dict(kind="2d", shot="room"),
    "lamp": dict(kind="2d", shot="lamp"),
}

cut_lamp_in = B["three"] - 0.2
cut_lamp_out = B["flicks"][2] + 0.45
whip_t = B["knocks"][0] - 0.12

SEGMENTS = [
    # wide room, slow push toward Mia while the narrator sets the rule
    dict(t0=0.0, t1=cut_lamp_in, src="room", offset=0.0,
         fx=[dict(fx="zoom", keys=[(0.0, 1.0, FACE), (cut_lamp_in, 1.12, FACE)], ease="linear")]),
    # insert: the lamp flickers three times
    dict(t0=cut_lamp_in, t1=cut_lamp_out, src="lamp", offset=cut_lamp_in,
         fx=[dict(fx="zoom", keys=[(cut_lamp_in, 1.0, (540, 1000)), (cut_lamp_out, 1.06, (540, 1000))])]),
    # back on Mia: calm... then the 4th flicker -> punch-in + shake
    dict(t0=cut_lamp_out, t1=DURATION, src="room", offset=cut_lamp_out,
         fx=[dict(fx="zoom", keys=[(cut_lamp_out, 1.12, FACE), (B["reveal"], 1.16, FACE),
                                   (B["reveal"] + 0.16, 1.55, FACE), (whip_t - 0.11, 1.6, FACE),
                                   (whip_t + 0.11, 1.85, DOOR), (DURATION, 1.95, DOOR)], ease="inout"),
             dict(fx="shake", t0=B["reveal"], t1=B["reveal"] + 0.45, amp=14, freq=18),
             dict(fx="whip", t=whip_t, dur=0.22, dir=(1, 0), travel=False),
             dict(fx="shake", t0=B["knocks"][0], t1=B["knocks"][2] + 0.25, amp=10, freq=22),
             dict(fx="vignette", strength=0.25, t0=B["reveal"])]),
]

OVERLAYS = [
    dict(kind="chip", t0=0.15, t1=B["reveal"] - 0.05, text="11:00 PM", y=0.085, bg="#fff1d6"),
    dict(kind="hud", t0=cut_lamp_in - 0.1, t1=B["line2_start"] + 0.2, y=0.15,
         items=[("FLICKERS", [(0, 0)] + [(ft, i + 1) for i, ft in enumerate(FLICKS_ALL)])]),
    dict(kind="stamp", t0=B["reveal"] + 0.12, t1=B["line2_start"] - 0.05, text="FOUR?!", y=0.27, rot=-7,
         color="#e2574c"),
    dict(kind="text", t0=B["knocks"][0] + 0.05, t1=DURATION, text="knock knock knock", y=0.2, size=60,
         weight="ExtraBold", color="#ffe7b0", rot=-3),
]

CAPTIONS = dict(timing="audio/timing.json", y=0.70, size=82, emphasis=["three", "four."],
                speakers=True, speaker_colors={"mia": "#ffb38a"})

AUDIO = "audio/mix_master.wav"
