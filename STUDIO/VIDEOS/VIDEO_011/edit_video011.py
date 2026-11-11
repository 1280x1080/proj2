"""EDL for VIDEO_011 - LAST ONE IN THE CALL, Part 1.
SCENES: (id, line, shot, YOUR emotion, key words).  Two jumpscares (SC1 after L07, SC2 after L10)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, DURATION, ESTIMATED, end, start, word  # noqa: E402,F401

BEATS = B
RED, YEL = "#e8423a", "#ffd23f"

SCENES = [
    ("HA", "H1", "call_ui", "nervous", {"left": RED, "breathing": RED}),
    ("HB", None, "you_cu", "scared", {}),
    ("L01", "L01", "room_wide", "happy", {"normal": YEL, "fortnite.": YEL}),
    ("L02", "L02", "game_screen", "happy", {"cracked": YEL}),
    ("L03", "L03", "call_ui", "calm", {"marcus.": RED, "dee.": RED}),
    ("L04", "L04", "you_cu", "calm", {"only": YEL}),
    ("L05", "L05", "call_ui", "suspicious", {"knocking": RED}),
    ("L06", "L06", "you_cu", "nervous", {"third": RED}),
    ("L07", "L07", "call_ui", "scared", {"marcus.": RED, "smiling.": RED}),
    ("SC1", None, "scare_tile", "shocked", {}),
    ("L08", "L08", "you_cu", "shocked", {"scream.": RED, "never": RED}),
    ("L09", "L09", "phone_cu", "scared", {"not": RED}),
    ("L10", "L10", "call_ui", "terrified", {"behind": RED}),
    ("SC2", None, "scare_face", "terrified", {}),
    ("L11", "L11", "reflect_cu", "terrified", {"open.": RED, "standing": RED}),
    ("L12", "L12", "window_cu", "terrified", {"knocks...": RED}),
    ("FRZ", None, "you_cu", "terrified", {}),
    ("CH", "L13", "choice_bg", "terrified", {"comment": YEL}),
]
SCENE_EMO = [(sid, line, you) for sid, line, shot, you, _ in SCENES]


def _t0(sid, line):
    return {"HA": 0.0, "HB": word("H1", "So") - 0.1, "L01": B["story"], "SC1": B["scare1"], "L08": B["scare1_end"],
            "SC2": B["scare2"], "L11": B["scare2_end"], "FRZ": B["freeze"],
            "CH": B["choice"]}.get(sid, start(line) - 0.08 if line else 0.0)


FOCUS = dict(call_ui=(540, 800), you_cu=(540, 860), room_wide=(540, 1000), game_screen=(540, 800), scare_tile=(540, 800),
             phone_cu=(540, 900), scare_face=(540, 860), reflect_cu=(540, 800), window_cu=(540, 800), choice_bg=(540, 1000))
SEGMENTS = []
for i, (sid, line, shot, you, keys) in enumerate(SCENES):
    t0 = _t0(sid, line)
    t1 = _t0(SCENES[i + 1][0], SCENES[i + 1][1]) if i + 1 < len(SCENES) else DURATION
    f = FOCUS[shot]
    fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.06, f)], ease="linear")]
    if sid in ("SC1", "SC2"):  # jumpscare: slam zoom + hard shake + white flash
        fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t0 + 0.08, 1.35, f), (t1, 1.5, f)], ease="out"),
              dict(fx="shake", t0=t0, t1=t1, amp=26, freq=24), dict(fx="flash", t=t0, dur=0.1)]
    if sid == "L12":
        fx.append(dict(fx="shake", t0=B["knocks"][0], t1=t1, amp=7, freq=16))
    seg = dict(t0=t0, t1=t1, src=shot, fx=fx, scene=sid)
    if sid == "FRZ":
        seg.update(freeze=B["freeze"] - 0.05, offset=B["freeze"] - 0.05)
        seg["fx"] = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.1, f)]), dict(fx="tint", color=RED, amount=0.25, t0=t0, t1=t1),
                     dict(fx="flash", t=t0, dur=0.15)]
    SEGMENTS.append(seg)
SOURCES = {name: dict(kind="2d", shot=name) for name in {s["src"] for s in SEGMENTS}}

OVERLAYS = [
    dict(kind="title", t0=B["story"] + 0.1, t1=B["story"] + 2.6, text="LAST ONE IN THE CALL", sub="PART 1", size=74,
         y=0.11, sub_color=YEL, stroke=14),
    dict(kind="chip", t0=B["story"] + 2.7, t1=B["leave1"], text="12:04 AM · SQUAD 4/4", size=28, y=0.045, bg="#15161b", color="#d7d7dc"),
    dict(kind="chip", t0=B["leave1"], t1=B["leave2"], text="12:51 AM · SQUAD 3/4", size=28, y=0.045, bg="#15161b", color="#d7d7dc"),
    dict(kind="chip", t0=B["leave2"], t1=B["choice"], text="1:00 AM · 2 IN CALL", size=28, y=0.045, bg="#3a0c0a", color="#ffb0a8"),
    dict(kind="title", t0=B["choice"], t1=DURATION, text="WHAT DO YOU DO?", size=96, y=0.12, stroke=12),
    dict(kind="text", t0=B["choice"] + 0.3, t1=DURATION, text="A  TURN AROUND", size=52, x=0.5, y=0.215,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#e2574c", bg_alpha=0.96),
    dict(kind="text", t0=B["choice"] + 0.3, t1=DURATION, text="Risk: you see what's in the doorway", size=34, x=0.5, y=0.258,
         weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.7),
    dict(kind="text", t0=B["choice"] + 0.8, t1=DURATION, text="B  KEEP YOUR EYES ON THE SCREEN", size=52, x=0.5, y=0.315,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#3f8fd6", bg_alpha=0.96),
    dict(kind="text", t0=B["choice"] + 0.8, t1=DURATION, text="Risk: it's already walking toward you", size=34, x=0.5,
         y=0.358, weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.7),
    dict(kind="text", t0=end("L13") + 0.1, t1=DURATION, text="COMMENT A OR B · YOUR CHOICE DECIDES PART 2", size=36,
         y=0.885, weight="Black", color="#ffd23f", stroke=8, stroke_color="#141418"),
]
CAPTIONS = dict(
    timing="audio/timing.json", y=0.775, size=80, max_words=5, highlight="#ffffff", upper=True, speakers=True,
    speaker_names={"jay": "JAY · VOICE CHAT"},
    speaker_colors={"jay": "#8fe3a0"},
    line_colors={line: keys for sid, line, shot, you, keys in SCENES if line and keys},
)
AUDIO = "audio/mix_master.wav"
