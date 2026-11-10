"""EDL for VIDEO_009 - THE LAST BELL, Part 1: "The Lockdown".
SCENES: (id, line, shot, HER emotion, YOUR emotion, caption override, key words).  Both characters act every line."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, DURATION, ESTIMATED, end, start, word  # noqa: E402,F401

BEATS = B
RED, YEL = "#e8423a", "#ffd23f"

SCENES = [
    # ---- hook (flash-forward): fixed cuts 0-1-2-3 s
    ("HA", "H1", "two_cu", "happy", "happy", None, {"crush": YEL}),
    ("HB", None, "class_wide", "shocked", "shocked", None, {}),
    ("HC", None, "door_cu", "scared", "scared", None, {}),
    ("H2", "H2", "two_cu", "scared", "scared", None, {"her": RED, "voice": RED}),
    # ---- the romantic intro (warm afternoon)
    ("P01", "P01", "class_wide", "happy", "nervous", None, {"crush": YEL}),
    ("P02", "P02", "paper_cu", "happy", "happy", None, {"project.": YEL}),
    ("P03", "P03", "two_cu", "happy", "happy", None, {"laughing": YEL}),
    ("P04", "P04", "you_cu", "happy", "happy", None, {"awkward.": YEL}),
    # ---- lockdown
    ("P05", "P05", "class_wide", "shocked", "shocked", None, {"alarm": RED}),
    ("P06", "P06", "alarm_cu", "shocked", "shocked", None, {"red.": RED}),
    ("P07", "P07", "alarm_cu", "scared", "scared", None, {"lockdown.": RED}),
    ("P08", "P08", "her_cu", "scared", "scared", None, {"name.": RED}),
    ("P09", "P09", "two_cu", "scared", "nervous", None, {"smiling.": RED}),
    ("P10", "P10", "class_wide", "scared", "scared", None, {"silent.": YEL}),
    ("P11", "P11", "door_cu", "scared", "scared", None, {"knocks.": RED}),
    ("P12", "P12", "door_cu", "scared", "scared", None, {"in?": RED}),
    ("P13", "P13", "her_cu", "scared", "scared", None, {"beside": YEL}),
    ("P14", "P14", "her_cu", "determined", "scared", None, {"open": RED}),
    ("P15", "P15", "door_cu", "scared", "scared", None, {"exactly": RED}),
    ("P16", "P16", "door_cu", "scared", "terrified", None, {"closer.": RED}),
    ("P17", "P17", "arm_cu", "terrified", "scared", None, {"shaking.": RED}),
    ("P18", "P18", "her_cu", "terrified", "scared", None, {"not": RED}),
    ("P19", "P19", "you_cu", "scared", "terrified", None, {"cold.": RED}),
    ("P20", "P20", "door_cu", "scared", "terrified", None, {"like": RED}),
    ("P21", "P21", "two_cu", "suspicious", "shocked", None, {"confused.": YEL}),
    ("P22", "P22", "phone_cu", "nervous", "nervous", None, {"unknown": RED}),
    ("P23", "P23", "phone_cu", "scared", "scared", None, {"behind": RED}),
    ("P24", "P24", "behind_pov", "scared", "terrified", None, {"nobody": RED}),
    ("P25", "P25", "phone_cu", "sad", "shocked", None, {"last": RED}),
    ("P26", "P26", "her_cu", "sad", "scared", None, {"crying.": YEL}),
    ("P27", "P27", "her_cu", "sad", "scared", None, {"remember": RED}),
    ("P28", "P28", "door_cu", "terrified", "terrified", None, {"handle": RED}),
    ("P29", "P29", "hands_cu", "terrified", "terrified", None, {"hand": YEL}),
    ("P30", "P30", "her_cu", "determined", "terrified", None, {"shadow.": RED}),
    ("FRZ", None, "two_cu", "terrified", "terrified", None, {}),
    ("CH", "P31", "choice_bg", "terrified", "terrified", None, {"comment": YEL}),
]
SCENE_EMO = [(sid, line, her, you) for sid, line, shot, her, you, *_ in SCENES]


def _t0(sid, line):
    return {"HA": 0.0, "HB": B["hook_red"], "HC": B["hook_door"], "H2": B["hook_text"], "P01": B["story"],
            "FRZ": B["freeze"], "CH": B["choice"]}.get(sid, start(line) - 0.08 if line else 0.0)


FOCUS = dict(two_cu=(540, 980), class_wide=(540, 1000), door_cu=(540, 900), her_cu=(540, 860), you_cu=(540, 860),
             paper_cu=(540, 1000), alarm_cu=(540, 800), arm_cu=(540, 1000), phone_cu=(540, 960), behind_pov=(540, 1000),
             hands_cu=(540, 1000), choice_bg=(540, 1000))
SEGMENTS = []
for i, (sid, line, shot, her, you, cap, keys) in enumerate(SCENES):
    t0 = _t0(sid, line)
    t1 = _t0(SCENES[i + 1][0], SCENES[i + 1][1]) if i + 1 < len(SCENES) else DURATION
    if sid == "P30":
        t1 = B["freeze"]
    f = FOCUS[shot]
    fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.07, f)], ease="linear")]
    if sid in ("HB", "P05"):
        fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t0 + 0.12, 1.15, f), (t1, 1.2, f)], ease="out"),
              dict(fx="shake", t0=t0, t1=t0 + 0.4, amp=12, freq=20)]
    if shot == "door_cu" and sid in ("HC", "P11", "P15"):
        fx.append(dict(fx="shake", t0=t0 + (0.0 if sid != "P11" else end("P11") - t0), t1=t1, amp=6, freq=16))
    seg = dict(t0=t0, t1=t1, src=shot, fx=fx, scene=sid)
    if sid == "FRZ":
        seg.update(freeze=B["freeze"] - 0.4, offset=B["freeze"] - 0.4)
        seg["fx"] = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.1, f)]), dict(fx="tint", color=RED, amount=0.3, t0=t0, t1=t1),
                     dict(fx="flash", t=t0, dur=0.15)]
    if sid == "CH":
        seg["fx"] = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.12, f)], ease="linear")]
    SEGMENTS.append(seg)
SOURCES = {name: dict(kind="2d", shot=name) for name in {s["src"] for s in SEGMENTS}}

OVERLAYS = [
    dict(kind="text", t0=B["hook_text"] + 0.1, t1=B["story"], text="THE PROBLEM? SHE'S ALREADY SITTING NEXT TO YOU.", size=56,
         y=0.17, weight="Black", color="#ffffff", stroke=12, stroke_color="#141418"),
    dict(kind="title", t0=B["story"] + 0.1, t1=B["story"] + 2.4, text="THE LAST BELL", sub="PART 1 · THE LOCKDOWN", size=110,
         y=0.17, sub_color=YEL, stroke=14),
    dict(kind="chip", t0=B["alarm"], t1=B["choice"], text="LOCKDOWN · ROOM 2B", size=26, y=0.045, bg="#c0392b", color="#ffffff"),
    # choice screen: pinned to the storage-room door (A, left) and the window (B, right)
    dict(kind="title", t0=B["choice"], t1=DURATION, text="WHAT DO YOU DO?", size=96, y=0.12, stroke=12),
    dict(kind="text", t0=B["choice"] + 0.3, t1=DURATION, text="A  HIDE IN THE STORAGE ROOM", size=50, x=0.5, y=0.215,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#e2574c", bg_alpha=0.96),
    dict(kind="text", t0=B["choice"] + 0.3, t1=DURATION, text="Risk: only one way out", size=34, x=0.5, y=0.258,
         weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.7),
    dict(kind="text", t0=B["choice"] + 0.8, t1=DURATION, text="B  ESCAPE THROUGH THE WINDOW", size=50, x=0.5, y=0.315,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#3f8fd6", bg_alpha=0.96),
    dict(kind="text", t0=B["choice"] + 0.8, t1=DURATION, text="Risk: 2nd floor - and something's in the courtyard", size=34, x=0.5,
         y=0.358, weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.7),
    dict(kind="text", t0=start("P31") - 0.1, t1=DURATION, text="COMMENT A OR B · YOUR DECISION DETERMINES PART 2", size=33,
         y=0.885, weight="Black", color="#ffd23f", stroke=8, stroke_color="#141418"),
]
CAPTIONS = dict(
    timing="audio/timing.json", y=0.71, size=80, max_words=5, highlight="#ffffff", upper=True, speakers=True,
    speaker_names={"her": "HER", "outside": "OUTSIDE · HER VOICE?", "intercom": "INTERCOM"},
    speaker_colors={"her": "#ff9ec4", "outside": "#ff6a5a", "intercom": "#9fd3ff"},
    line_colors={line: keys for sid, line, shot, her, you, cap, keys in SCENES if line and keys},
)
AUDIO = "audio/mix_master.wav"
