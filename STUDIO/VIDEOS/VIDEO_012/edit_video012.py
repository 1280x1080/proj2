"""EDL for VIDEO_012 - ORDER #000, Part 1.
SCENES: (id, line, shot, YOUR emotion, key words).  Two jumpscares (SC1 after L06, SC2 after L11)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, DURATION, ESTIMATED, end, start, word  # noqa: E402,F401

BEATS = B
RED, YEL = "#e8423a", "#ffd23f"

SCENES = [
    ("HA", "H1", "app_order", "calm", {"one": YEL, "forty": RED}),
    ("HB", None, "doorcam", "scared", {}),
    ("L01", "L01", "bed_you", "happy", {"tiktok,": YEL, "mukbangs.": YEL}),
    ("L01b", None, "phone_feed", "happy", {}),
    ("L02", "L02", "app_order", "happy", {"starving.": YEL, "placed.": YEL}),
    ("L03", "L03", "bed_you", "shocked", {"knocks.": RED}),
    ("L04", "L04", "doorcam", "suspicious", {"blinking.": RED, "wide.": RED}),
    ("L05", "L05", "doorcam", "scared", {"open": RED, "cold.": RED}),
    ("L06", "L06", "app_order", "scared", {"real": RED, "still": RED}),
    ("L06b", None, "doorcam", "scared", {}),
    ("SC1", None, "scare_cam", "terrified", {}),
    ("L07", "L07", "doorcam", "terrified", {"gone.": RED, "lock": YEL}),
    ("L08", "L08", "bed_bag", "shocked", {"already": RED, "bed.": RED}),
    ("L09", "L09", "phone_feed", "nervous", {"stopped": RED, "staring": RED}),
    ("L10", "L10", "phone_feed", "scared", {"bag.": RED, "gets": RED}),
    ("L11", "L11", "bed_bag", "terrified", {"move.": RED}),
    ("SC2", None, "scare_bag", "terrified", {}),
    ("CH", "L12", "choice_bg", "terrified", {"top": YEL, "comment": YEL}),
]
SCENE_EMO = [(sid, line, you) for sid, line, shot, you, _ in SCENES]


def _t0(sid, line):
    return {"HA": 0.0, "HB": word("H1", "but") - 0.15, "L01": B["story"], "L01b": word("L01", "scrolling") - 0.05, "L06b": end("L06") + 0.05,
            "SC1": B["scare1"], "L07": B["scare1_end"], "SC2": B["scare2"],
            "CH": B["scare2_end"]}.get(sid, start(line) - 0.08 if line else 0.0)


FOCUS = dict(app_order=(540, 800), bed_you=(540, 900), phone_feed=(540, 800), doorcam=(540, 800), scare_cam=(540, 800),
             bed_bag=(540, 900), scare_bag=(540, 850), choice_bg=(540, 900))
SEGMENTS = []
for i, (sid, line, shot, you, keys) in enumerate(SCENES):
    t0 = _t0(sid, line)
    t1 = _t0(SCENES[i + 1][0], SCENES[i + 1][1]) if i + 1 < len(SCENES) else DURATION
    f = FOCUS[shot]
    fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.06, f)], ease="linear")]
    if sid in ("SC1", "SC2"):  # jumpscare: slam zoom + hard shake + white flash
        fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t0 + 0.08, 1.3, f), (t1, 1.45, f)], ease="out"),
              dict(fx="shake", t0=t0, t1=t1, amp=26, freq=24), dict(fx="flash", t=t0, dur=0.1)]
    if sid == "L03":
        fx.append(dict(fx="shake", t0=B["knocks"][0], t1=t1, amp=7, freq=16))
    if sid == "CH":
        fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.05, f)], ease="linear"), dict(fx="flash", t=t0, dur=0.12)]
    SEGMENTS.append(dict(t0=t0, t1=t1, src=shot, fx=fx, scene=sid))
SOURCES = {name: dict(kind="2d", shot=name) for name in {s["src"] for s in SEGMENTS}}

OVERLAYS = [
    dict(kind="title", t0=B["story"] + 0.1, t1=B["story"] + 2.4, text="ORDER #000", sub="PART 1", size=120,
         y=0.11, sub_color=YEL, stroke=14),
    dict(kind="chip", t0=B["story"] + 2.5, t1=B["choice"], text="2:07 AM · HOME ALONE", size=28, y=0.045, bg="#15161b", color="#d7d7dc"),
    # choice screen - the rule is the loudest thing on it
    dict(kind="title", t0=B["choice"], t1=DURATION, text="WHAT DO YOU DO?", size=96, y=0.09, stroke=12),
    dict(kind="text", t0=B["choice"] + 0.3, t1=DURATION, text="A  OPEN THE BAG", size=56, x=0.5, y=0.175,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#e2574c", bg_alpha=0.96),
    dict(kind="text", t0=B["choice"] + 0.3, t1=DURATION, text="Risk: that's how he gets in", size=34, x=0.5, y=0.215,
         weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.7),
    dict(kind="text", t0=B["choice"] + 0.8, t1=DURATION, text="B  THROW IT OUT THE WINDOW", size=56, x=0.5, y=0.265,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#3f8fd6", bg_alpha=0.96),
    dict(kind="text", t0=B["choice"] + 0.8, t1=DURATION, text="Risk: he's waiting right below it", size=34, x=0.5,
         y=0.305, weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.7),
    dict(kind="text", t0=B["choice"] + 1.2, t1=DURATION, text="TOP COMMENT DECIDES PART 2", size=62, x=0.5, y=0.385,
         weight="Black", color="#141418", stroke=0, bg="#ffd23f", bg_alpha=1.0),
    dict(kind="text", t0=B["choice"] + 1.2, t1=DURATION, text="comment A or B - the most-liked comment wins", size=34, x=0.5,
         y=0.43, weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.75),
]
CAPTIONS = dict(
    timing="audio/timing.json", y=0.775, size=80, max_words=5, highlight="#ffffff", upper=True, speakers=True,
    speaker_names={"sam": "DELIVERY GUY · AT THE DOOR", "streamer": "MUKBANG GIRL · ON YOUR PHONE"},
    speaker_colors={"sam": "#ff8a7a", "streamer": "#ff9ec4"},
    line_colors={line: keys for sid, line, shot, you, keys in SCENES if line and keys},
)
AUDIO = "audio/mix_master.wav"
