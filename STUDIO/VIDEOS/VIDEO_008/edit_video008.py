"""EDL for VIDEO_008 - THE FREQUENCY THAT KNOWS TOMORROW, Part 1: "The Voice on the Radio".
Scene table -> SEGMENTS / OVERLAYS / CAPTIONS.  `emo` = YOUR on-screen emotion during that line (flat.emote)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, CLOCK0, DEATH, DURATION, ESTIMATED, clock, end, start, word  # noqa: E402,F401

BEATS = B
RED, YEL = "#e8423a", "#ffd23f"

#  id     line   shot             emo          caption (None = spoken words)                    key words             tx
SCENES = [
    ("F01", "F01", "onair_cu", "calm", None, {"dying.": RED}, 0),
    ("F02", "F02", "console_cu", "calm", None, {"ninety": RED}, 0),
    ("F03", "F03", "studio_wide", "calm", None, {"alone": YEL}, 0),
    ("F04", "F04", "clock_cu", "calm", "IT'S 1:06 AM.", {"1:06": YEL}, 0),
    ("F05", "F05", "speaker_cu", "shocked", None, {"themselves.": RED}, 1),
    ("F06", "F06", "you_cu", "shocked", None, {"own": RED}, 1),
    ("F07", "F07", "console_cu", "scared", None, {"three.": RED}, 1),
    ("F08", "F08", "computer_cu", "suspicious", None, {"file.": YEL}, 1),
    ("F09", "F09", "you_cu", "suspicious", None, {"nothing.": YEL}, 1),
    ("F10", "F10", "phone_cu", "nervous", None, {"ringing.": RED}, 1),
    ("F11", "F11", "you_cu", "nervous", None, {"three.": YEL}, 1),
    ("F12", "F12", "cable_cu", "scared", None, {"disconnected": RED}, 1),
    ("F13", "F13", "speaker_cu", "scared", None, {"again.": YEL}, 2),
    ("F14", "F14", "you_cu", "scared", None, {"terrified.": RED}, 2),
    ("F15", "F15", "console_cu", "terrified", None, {"alone!": RED}, 2),
    ("F16", "F16", "phone_cu", "scared", None, {"silence.": YEL}, 2),
    ("F17", "F17", "receiver_cu", "scared", None, {"receiver.": YEL}, 2),
    ("F18", "F18", "receiver_cu", "terrified", None, {"alone": RED}, 2),
    ("F19", "F19", "studio_wide", "terrified", None, {"away": YEL}, 2),
    ("F20", "F20", "speaker_cu", "shocked", None, {"crackle.": RED}, 3),
    ("F21", "F21", "console_cu", "terrified", None, {"remember.": RED}, 3),
    ("F22", "F22", "you_cu", "terrified", None, {"freeze.": RED}, 3),
    ("F23", "F23", "transmitter_cu", "determined", None, {"transmitter.": YEL}, 3),
    ("F24", "F24", "computer_cu", "shocked", None, {"message.": YEL}, 4),
    ("F25", "F25", "computer_cu", "shocked", None, {"own": RED}, 4),
    ("F25b", None, "onair_cu", "shocked", None, {}, 4),
    ("F26", "F26", "you_cu", "suspicious", "THE MESSAGE: STOP LISTENING TO THE VERSION OF YOU THAT WANTS TO SURVIVE.",
     {"survive.": RED}, 4),
    ("F26b", None, "computer_cu", "suspicious", None, {}, 4),
    ("F27", "F27", "phone_cu", "scared", None, {"yours.": RED}, 5),
    ("F27b", None, "you_cu", "terrified", None, {}, 5),
    ("F28", "F28", "receiver_cu", "terrified", None, {"please.": YEL}, 5),
    ("F28b", None, "you_cu", "terrified", None, {}, 5),     # freeze on your face
    ("F29", "F29", "choice_bg", "determined", None, {"conflicting": RED}, 5),
    ("F30", "F30", "choice_bg", "determined", None, {"destroy": YEL}, 5),
    ("F31", "F31", "choice_bg", "determined", None, {"disappear": RED}, 5),
    ("F32", "F32", "choice_bg", "determined", None, {"comment": YEL}, 5),
]
AT = {"F25b": ("F25", "own"), "F26b": ("F26", "stop"), "F27b": ("F27", "this")}  # insert cuts on these words
SCENE_EMO = [(sid, line, emo) for sid, line, shot, emo, *_ in SCENES]
FOCUS = dict(onair_cu=(540, 860), console_cu=(540, 1000), studio_wide=(540, 1000), clock_cu=(540, 900), speaker_cu=(540, 900),
             you_cu=(540, 880), computer_cu=(540, 960), phone_cu=(540, 960), cable_cu=(540, 1100), receiver_cu=(540, 960),
             transmitter_cu=(540, 900), choice_bg=(540, 960))


def _t0(sid, line):
    if sid in AT:
        return word(*AT[sid]) - 0.05
    if sid == "F01":
        return 0.0
    if sid == "F28b":
        return B["freeze"]
    if sid == "F29":
        return B["choice"]
    return start(line) - 0.08


CUTS = [s for s in SCENES if s[0] not in ("F30", "F31", "F32")]   # the choice screen is one continuous shot
SEGMENTS = []
for i, (sid, line, shot, emo, cap, keys, tx) in enumerate(CUTS):
    t0 = _t0(sid, line)
    t1 = _t0(CUTS[i + 1][0], CUTS[i + 1][1]) if i + 1 < len(CUTS) else DURATION
    if sid == "F28":
        t1 = B["freeze"]
    f = FOCUS[shot]
    fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.08, f)], ease="linear")]
    if shot in ("speaker_cu",) and sid in ("F05", "F20"):
        fx = [dict(fx="zoom", keys=[(t0, 1.0, f), (t0 + 0.14, 1.25, f), (t1, 1.3, f)], ease="out"),
              dict(fx="shake", t0=t0, t1=t0 + 0.45, amp=14, freq=20)]
    if shot == "phone_cu" and sid in ("F10", "F27"):
        fx.append(dict(fx="shake", t0=t0, t1=t0 + 0.5, amp=8, freq=24))
    seg = dict(t0=t0, t1=t1, src=shot, fx=fx, scene=sid)
    if sid == "F29":  # one calm choice shot: a gentle push only, so nothing slides under the pills / caption
        seg["fx"] = [dict(fx="zoom", keys=[(t0, 1.0, (540, 1000)), (t1, 1.14, (540, 1000))], ease="linear"),
                     dict(fx="vignette", strength=0.4, t0=t0, t1=t1)]
    if sid == "F28b":
        seg.update(freeze=B["freeze"] - 0.5, offset=B["freeze"] - 0.5)
        seg["fx"] = [dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.12, f)]), dict(fx="tint", color=RED, amount=0.35, t0=t0, t1=t1),
                     dict(fx="flash", t=t0, dur=0.15)]
    if t0 >= start("F15") - 0.1 and sid != "F28b":  # the red creeps in once your recorded voice is terrified
        seg["fx"].append(dict(fx="vignette", strength=0.4, t0=t0, t1=t1))
    SEGMENTS.append(seg)

SOURCES = {name: dict(kind="2d", shot=name) for name in {s["src"] for s in SEGMENTS}}

# ---- HUD: clock ticking every second (turns red at the recording's 1:07:30), TRANSMISSIONS counter ----
HUD_END = DURATION
death_t = DEATH - CLOCK0
clock_keys = [(float(k), clock(k)) for k in range(0, int(DURATION) + 1)]
tx_keys = []
for sid, line, shot, emo, cap, keys, tx in SCENES:
    if not tx_keys or tx_keys[-1][1] != tx:
        tx_keys.append((_t0(sid, line), tx))
OVERLAYS = [
    dict(kind="title", t0=0.05, t1=B["title_out"], text="THE FREQUENCY\nTHAT KNOWS TOMORROW", sub="PART 1", size=84, y=0.2,
         sub_color=YEL, stroke=14),
    dict(kind="chip", t0=0.0, t1=HUD_END, text="NIGHT 1 · WKTM 98.7", size=24, x=0.17, y=0.03, bg="#15161b", color="#d7d7dc"),
    dict(kind="hud", t0=0.0, t1=min(death_t, HUD_END), x=0.17, y=0.068, size=36, items=[("", [k for k in clock_keys if k[0] < death_t])],
         flash="#15161b"),
    dict(kind="hud", t0=0.0, t1=HUD_END, x=0.80, y=0.05, size=32, items=[("TRANSMISSIONS", tx_keys)], flash=RED),
]
if death_t < HUD_END:
    OVERLAYS.append(dict(kind="hud", t0=death_t, t1=HUD_END, x=0.17, y=0.068, size=36,
                         items=[("", [k for k in clock_keys if k[0] >= death_t])], flash=RED))
    OVERLAYS.append(dict(kind="text", t0=death_t, t1=HUD_END, text="1:07:30 — THE RECORDING", size=30, x=0.25, y=0.105,
                         weight="ExtraBold", color="#ffffff", stroke=0, bg=RED, bg_alpha=0.95))
# choice screen (pills pinned to the transmitter on the left and the phone on the right)
OVERLAYS += [
    dict(kind="title", t0=B["choice"], t1=DURATION, text="WHAT DO YOU DO?", size=96, y=0.19, stroke=12),
    dict(kind="text", t0=start("F30") - 0.1, t1=DURATION, text="A  DESTROY THE TRANSMITTER", size=42, x=0.29, y=0.28,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#e2574c", bg_alpha=0.96),
    dict(kind="text", t0=start("F30") - 0.1, t1=DURATION, text="What if the warnings were the only thing keeping you alive?",
         size=23, x=0.27, y=0.325, weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.7),
    dict(kind="text", t0=start("F30") + 0.6, t1=DURATION, text="B  ANSWER THE PHONE", size=42, x=0.72, y=0.40,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#3f8fd6", bg_alpha=0.96),
    dict(kind="text", t0=start("F30") + 0.6, t1=DURATION, text="What if the voice on the phone is the only one telling the truth?",
         size=23, x=0.75, y=0.45, weight="Bold", color="#ffffff", stroke=0, bg="#000000", bg_alpha=0.7),
    dict(kind="text", t0=start("F32") - 0.1, t1=DURATION, text="COMMENT A OR B · YOUR CHOICE DECIDES PART 2", size=34, y=0.885,
         weight="Black", color="#ffd23f", stroke=8, stroke_color="#141418"),
]

CAPTIONS = dict(
    timing="audio/timing.json", y=0.70, size=80, max_words=5, highlight="#ffffff", upper=True, speakers=True,
    speaker_names={"radio": "YOU · RADIO", "phone": "YOU · PHONE", "unknown": "UNKNOWN"},
    speaker_colors={"radio": "#ffb38a", "phone": "#ffb38a", "unknown": "#c9a7ff"},
    line_text={line: cap for sid, line, shot, emo, cap, keys, tx in SCENES if line and cap},
    line_colors={line: keys for sid, line, shot, emo, cap, keys, tx in SCENES if line and keys},
)
AUDIO = "audio/mix_master.wav"
