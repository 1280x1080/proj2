"""EDL for VIDEO_010 - FLIGHT 417, Part 1: "The Same Route".
SCENES: (id, line, shot, MAN emotion, YOUR emotion, key words).  Both characters act every line."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, DURATION, ESTIMATED, end, start, word  # noqa: E402,F401

BEATS = B
RED, YEL = "#e8423a", "#ffd23f"

SCENES = [
    ("HA", "H1", "radar_cu", "calm", "calm", {"same": YEL, "vanished": RED}),
    ("HB", None, "window_pov", "shocked", "shocked", {}),
    ("L01", "L01", "plane_ext", "calm", "calm", {"417": YEL}),
    ("L02", "L02", "radar_cu", "calm", "calm", {"vanished.": RED, "nothing.": RED}),
    ("L03", "L03", "cabin_two", "nervous", "calm", {"same": YEL, "14a.": YEL}),
    ("L04", "L04", "watch_cu", "nervous", "calm", {"watch.": YEL}),
    ("L05", "L05", "man_cu", "sad", "nervous", {"wife": YEL, "that": RED}),
    ("L06", "L06", "cabin_two", "nervous", "shocked", {"flicker.": RED, "black.": RED}),
    ("L07", "L07", "panel_cu", "nervous", "scared", {"lost": RED}),
    ("L08", "L08", "window_pov", "nervous", "shocked", {"another": RED}),
    ("L09", "L09", "tail_cu", "shocked", "scared", {"417.": RED}),
    ("L10", "L10", "ghost_windows", "shocked", "scared", {"staring": RED}),
    ("L11", "L11", "man_cu", "shocked", "scared", {"wife.": YEL, "aged": RED}),
    ("L12", "L12", "ghost_windows", "sad", "scared", {"behind": RED}),
    ("L13", "L13", "seats_pov", "sad", "terrified", {"empty.": RED, "buckled.": RED}),
    ("L14", "L14", "panel_cu", "happy", "terrified", {"417.": RED, "everyone.": RED}),
    ("L15", "L15", "cabin_two", "happy", "terrified", {"smiling.": RED}),
    ("L16", "L16", "man_cu", "happy", "terrified", {"waiting": YEL, "us.": RED}),
    ("L17", "L17", "door_cu", "happy", "terrified", {"unlock": RED}),
    ("FRZ", None, "you_cu", "happy", "terrified", {}),
    ("CH", "L18", "choice_bg", "happy", "terrified", {"comment": YEL}),
]
SCENE_EMO = [(sid, line, man, you) for sid, line, shot, man, you, _ in SCENES]


def _t0(sid, line):
    return {"HA": 0.0, "HB": B["hook_ghost"], "L01": B["story"], "FRZ": B["freeze"],
            "CH": B["choice"]}.get(sid, start(line) - 0.08 if line else 0.0)


FOCUS = dict(radar_cu=(540, 760), window_pov=(540, 800), plane_ext=(540, 800), cabin_two=(540, 1000), watch_cu=(540, 900),
             man_cu=(540, 860), you_cu=(540, 860), panel_cu=(540, 700), tail_cu=(540, 800), ghost_windows=(540, 800),
             seats_pov=(540, 900), door_cu=(540, 900), choice_bg=(540, 1000))
SEGMENTS = []
for i, (sid, line, shot, man, you, keys) in enumerate(SCENES):
    t0 = _t0(sid, line)
    t1 = _t0(SCENES[i + 1][0], SCENES[i + 1][1]) if i + 1 < len(SCENES) else DURATION
    f = FOCUS[shot]
    fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.06, f)], ease="linear")]
    if sid in ("HB", "L09"):
        fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t0 + 0.15, 1.1, f), (t1, 1.16, f)], ease="out"),
              dict(fx="shake", t0=t0, t1=t0 + 0.35, amp=10, freq=20)]
    if sid == "L06":
        fx.append(dict(fx="shake", t0=B["flicker"], t1=B["flicker"] + 0.7, amp=8, freq=18))
    seg = dict(t0=t0, t1=t1, src=shot, fx=fx, scene=sid)
    if sid == "FRZ":
        seg.update(freeze=B["freeze"] - 0.05, offset=B["freeze"] - 0.05)
        seg["fx"] = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.1, f)]), dict(fx="tint", color=RED, amount=0.25, t0=t0, t1=t1),
                     dict(fx="flash", t=t0, dur=0.15)]
    SEGMENTS.append(seg)
SOURCES = {name: dict(kind="2d", shot=name) for name in {s["src"] for s in SEGMENTS}}

OVERLAYS = [
    dict(kind="title", t0=B["story"] + 0.1, t1=B["story"] + 2.6, text="FLIGHT 417", sub="PART 1 · THE SAME ROUTE", size=120,
         y=0.14, sub_color=YEL, stroke=14),
    dict(kind="chip", t0=B["story"] + 2.7, t1=B["tonight"], text="10 YEARS AGO", size=28, y=0.045, bg="#15161b", color="#d7d7dc"),
    dict(kind="chip", t0=B["tonight"], t1=B["choice"], text="TONIGHT · SAME ROUTE · SEAT 14A", size=26, y=0.045, bg="#15161b",
         color="#d7d7dc"),
    dict(kind="title", t0=B["choice"], t1=DURATION, text="WHAT DO YOU DO?", size=96, y=0.12, stroke=12),
    dict(kind="text", t0=B["choice"] + 0.3, t1=DURATION, text="A  HOLD HIM BACK", size=52, x=0.5, y=0.215,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#e2574c", bg_alpha=0.96),
    dict(kind="text", t0=B["choice"] + 0.3, t1=DURATION, text="Risk: the door is opening for you too", size=34, x=0.5, y=0.258,
         weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.7),
    dict(kind="text", t0=B["choice"] + 0.8, t1=DURATION, text="B  RUN TO THE COCKPIT", size=52, x=0.5, y=0.315,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#3f8fd6", bg_alpha=0.96),
    dict(kind="text", t0=B["choice"] + 0.8, t1=DURATION, text="Risk: who is flying this plane?", size=34, x=0.5,
         y=0.358, weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.7),
    dict(kind="text", t0=start("L18") - 0.1, t1=DURATION, text="COMMENT A OR B · YOUR CHOICE DECIDES PART 2", size=36,
         y=0.885, weight="Black", color="#ffd23f", stroke=8, stroke_color="#141418"),
]
CAPTIONS = dict(
    timing="audio/timing.json", y=0.71, size=80, max_words=5, highlight="#ffffff", upper=True, speakers=True,
    speaker_names={"man": "OLD MAN", "captain": "CAPTAIN"},
    speaker_colors={"man": "#ffd9a0", "captain": "#9fd3ff"},
    line_colors={line: keys for sid, line, shot, man, you, keys in SCENES if line and keys},
)
AUDIO = "audio/mix_master.wav"
