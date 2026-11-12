"""EDL for VIDEO_013 - AFTER HOURS, Part 1.
SCENES: (id, line, shot, group emotion, key words).  Two jumpscares (SC1 after L08, SC2 after L11)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, DURATION, ESTIMATED, end, start, word  # noqa: E402,F401

BEATS = B
RED, YEL = "#e8423a", "#ffd23f"

SCENES = [
    ("HA", "H1", "hall_group", "nervous", {"midnight": YEL, "exam": YEL}),
    ("HB", None, "papers_cu", "scared", {"already": RED, "grading": RED}),
    ("L01", "L01", "game_night", "happy", {"rewind.": YEL, "four": YEL}),
    ("L02", "L02", "game_night", "happy", {"easy": YEL}),
    ("L03", "L03", "exam_cu", "sad", {"not": RED, "fail.": RED}),
    ("L04", "L04", "plan_cu", "determined", {"plan.": YEL, "12.": YEL, "fix": YEL}),
    ("L05", "L05", "hall_group", "nervous", {"midnight.": YEL, "black.": RED}),
    ("L06", "L06", "room12", "suspicious", {"graded.": RED, "same": RED}),
    ("L07", "L07", "papers_cu", "scared", {"tonight.": RED}),
    ("L08", "L08", "intercom_cu", "scared", {"five": RED, "seats.": RED}),
    ("L08b", None, "group_cu", "scared", {}),
    ("SC1", None, "scare_door", "terrified", {}),
    ("L09", "L09", "group_cu", "terrified", {"slams": RED, "four.": RED}),
    ("L10", "L10", "group_cu", "terrified", {"kai?": RED}),
    ("L11", "L11", "room12", "terrified", {"detention.": RED, "four": RED}),
    ("SC2", None, "scare_teacher", "terrified", {}),
    ("CH", "L12", "choice_bg", "terrified", {"top": YEL, "comment": YEL}),
]
SCENE_EMO = [(sid, line, emo) for sid, line, shot, emo, _ in SCENES]


def _t0(sid, line):
    return {"HA": 0.0, "HB": B["hook_cut"], "L01": B["story"], "L08b": end("L08") + 0.05, "SC1": B["scare1"],
            "L09": B["scare1_end"], "SC2": B["scare2"], "CH": B["scare2_end"]}.get(sid, start(line) - 0.08 if line else 0.0)


FOCUS = dict(hall_group=(540, 950), papers_cu=(540, 800), game_night=(540, 800), exam_cu=(540, 800), plan_cu=(540, 800),
             room12=(540, 800), intercom_cu=(540, 700), group_cu=(540, 900), scare_door=(540, 800), scare_teacher=(540, 800),
             choice_bg=(540, 900))
SEGMENTS = []
for i, (sid, line, shot, emo, keys) in enumerate(SCENES):
    t0 = _t0(sid, line)
    t1 = _t0(SCENES[i + 1][0], SCENES[i + 1][1]) if i + 1 < len(SCENES) else DURATION
    f = FOCUS[shot]
    fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.06, f)], ease="linear")]
    if sid in ("SC1", "SC2"):
        fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t0 + 0.08, 1.3, f), (t1, 1.45, f)], ease="out"),
              dict(fx="shake", t0=t0, t1=t1, amp=26, freq=24), dict(fx="flash", t=t0, dur=0.1)]
    if sid == "L09":
        fx.append(dict(fx="shake", t0=t0, t1=t0 + 0.5, amp=12, freq=18))
    if sid == "L01":
        fx.append(dict(fx="flash", t=t0, dur=0.2))  # rewind
    if sid == "CH":
        fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.05, f)], ease="linear"), dict(fx="flash", t=t0, dur=0.12)]
    SEGMENTS.append(dict(t0=t0, t1=t1, src=shot, fx=fx, scene=sid))
SOURCES = {name: dict(kind="2d", shot=name) for name in {s["src"] for s in SEGMENTS}}

OVERLAYS = [
    dict(kind="title", t0=B["story"] + 0.1, t1=B["story"] + 2.4, text="AFTER HOURS", sub="PART 1", size=120,
         y=0.11, sub_color=YEL, stroke=14),
    dict(kind="chip", t0=B["story"] + 2.5, t1=start("L03") - 0.08, text="THE NIGHT BEFORE THE EXAM · 4:02 AM", size=26, y=0.045,
         bg="#15161b", color="#d7d7dc"),
    dict(kind="chip", t0=start("L03") - 0.08, t1=B["midnight"], text="EXAM DAY", size=28, y=0.045, bg="#15161b", color="#d7d7dc"),
    dict(kind="chip", t0=B["midnight"], t1=B["choice"], text="12:00 AM · INSIDE THE SCHOOL", size=26, y=0.045, bg="#3a0c0a",
         color="#ffb0a8"),
    dict(kind="title", t0=B["choice"], t1=DURATION, text="WHAT DO YOU DO?", size=96, y=0.09, stroke=12),
    dict(kind="text", t0=B["choice"] + 0.3, t1=DURATION, text="A  SIT DOWN AND OBEY", size=56, x=0.5, y=0.175,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#e2574c", bg_alpha=0.96),
    dict(kind="text", t0=B["choice"] + 0.3, t1=DURATION, text="Risk: this class never ends", size=34, x=0.5, y=0.215,
         weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.7),
    dict(kind="text", t0=B["choice"] + 0.8, t1=DURATION, text="B  RUN FOR THE GYM WINDOW", size=56, x=0.5, y=0.265,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#3f8fd6", bg_alpha=0.96),
    dict(kind="text", t0=B["choice"] + 0.8, t1=DURATION, text="Risk: she takes whoever is last", size=34, x=0.5,
         y=0.305, weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.7),
    dict(kind="text", t0=B["choice"] + 1.2, t1=DURATION, text="TOP COMMENT DECIDES PART 2", size=50, x=0.5, y=0.385,
         weight="Black", color="#141418", stroke=0, bg="#ffd23f", bg_alpha=1.0),
    dict(kind="text", t0=B["choice"] + 1.2, t1=DURATION, text="comment A or B - the most-liked comment wins", size=34, x=0.5,
         y=0.432, weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.75),
]
CAPTIONS = dict(
    timing="audio/timing.json", y=0.775, size=80, max_words=5, highlight="#ffffff", upper=True, speakers=True,
    speaker_names={"mia": "MIA", "teacher": "INTERCOM"},
    speaker_colors={"mia": "#ff9ec4", "teacher": "#9fd3ff"},
    line_colors={line: keys for sid, line, shot, emo, keys in SCENES if line and keys},
)
AUDIO = "audio/mix_master.wav"
