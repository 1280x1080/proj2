"""EDL for VIDEO_004 - THE ROOM THAT WASN'T THERE, Part 1: "Don't Open the Door".

SCENES (one script line = one cut, plus inserts on key words) -> SEGMENTS / OVERLAYS / CAPTIONS.
Times come from beats.py (narration word timing).  Shots are drawn in anim2d.py.

Lighting: MOON (blue night, phone glow on your face) -> hallway light under the door goes out on "Silence"
-> a red cast creeps in from the third text message on -> choice screen in deep red/dark.
HUD: "NIGHT 1 · APT 317" tag + clock that never moves off 3:17 AM (a planted mystery) + DOORS counter (1 -> 2).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, CHOICE_HOLD, DURATION, ESTIMATED, end, start, word  # noqa: E402,F401

BEATS = B
RED, YEL = "#e8423a", "#ffd23f"

SCENES = [
    # ---- HOOK -----------------------------------------------------------------------------------
    dict(id="R01", line="R01", shot="clock_cu", key=("three-seventeen", RED),
         visual="ECU bedside digital clock, red digits flip 3:16 -> 3:17 on frame ~9. The phone beside it starts glowing.",
         cam="punch-in on the flip, then slow push", sfx=[("phone_vibrate", -8, 0.1), ("tick", -18, 0.3)],
         hud=("3:17 AM", 1), note="Title card THE ROOM THAT WASN'T THERE / PART 1."),
    dict(id="R02", line="R02", shot="phone_cu", key=("ringing.", YEL),
         visual="Phone on the nightstand, ringing and buzzing across the wood: UNKNOWN NUMBER.",
         cam="slow push", sfx=[("phone_ring", -12, -0.2), ("phone_ring", -13, 1.35), ("phone_vibrate", -14, 0.0)],
         hud=("3:17 AM", 1)),
    dict(id="R03", line="R03", shot="you_cu", key=("unknown", RED),
         visual="CU you, half asleep, blue phone glow from below; you lift the phone to your ear on 'answer'.",
         cam="hold, tiny drift", sfx=[("phone_ring", -14, 0.0), ("click_ui", -16, 1.4)], hud=("3:17 AM", 1)),
    dict(id="R04", line="R04", shot="phone_cu", key=("whispers.", RED),
         visual="Phone screen: call connected, UNKNOWN 00:01, the voice waveform barely moving.",
         cam="slow push", sfx=[("breath_close", -22, 0.0)], hud=("3:17 AM", 1)),
    dict(id="R05", line="R05", shot="door_wide", key=("door.", RED),
         visual="From the bed: your bedroom door, closed, a thin line of warm hallway light under it. Moonlight.",
         cam="slow push", sfx=[], hud=("3:17 AM", 1)),
    # ---- WRONG NORMAL / PRESENCE ----------------------------------------------------------------
    dict(id="R06", line="R06", shot="you_cu", key=("freeze.", RED),
         visual="CU you: eyes snap wide, phone still at your ear.", cam="punch-in", sfx=[], hud=("3:17 AM", 1)),
    dict(id="R06b", line=None, at=("R06", "knocking"), shot="door_wide", key=None,
         visual="The door jolts slightly in its frame; the light under it flickers - a shadow passes.",
         cam="shake", sfx=[("knock_slow", -10, 0.05), ("knock_slow", -12, 0.55)], hud=("3:17 AM", 1)),
    dict(id="R07", line="R07", shot="door_cu", key=("knocks.", RED),
         visual="ECU upper door panel. Three slow knocks land in the pause after the line: the wood jumps each time, dust drifts down.",
         cam="hold, shake on each knock", sfx=[], hud=("3:17 AM", 1)),
    dict(id="R08", line="R08", shot="phone_cu", key=("text", YEL),
         visual="Phone buzzes in your hand: lock-screen notification 'Unknown: I'm outside...'.",
         cam="slow push", sfx=[("phone_vibrate", -8, -0.15), ("text_ping", -10, 0.25)], hud=("3:17 AM", 1)),
    dict(id="R09", line="R09", shot="phone_cu", key=("outside.", RED),
         visual="Chat open. Header: Unknown, +1 (555) 013-0317. Typing dots, then the bubble 'I'm outside. Let me in.'",
         cam="hold", sfx=[], hud=("3:17 AM", 1),
         note="CLUE (B): the sender's number ends in 0317 - the same as the frozen clock and the apartment number."),
    dict(id="R10", line="R10", shot="you_cu", key=("message.", YEL),
         visual="CU you staring at the screen, glow on your face, a bead of sweat.", cam="slow push",
         sfx=[], hud=("3:17 AM", 1)),
    dict(id="R11", line="R11", shot="phone_cu", key=("pretending", RED),
         visual="Second bubble arrives under the first: 'Don't listen to the thing pretending to be me.'",
         cam="slow push", sfx=[], hud=("3:17 AM", 1)),
    dict(id="R12", line="R12", shot="you_cu", key=("drops.", RED),
         visual="CU you: the colour drains, mouth falls open.", cam="slow pull out", sfx=[("heartbeat", -10, 0.2)],
         hud=("3:17 AM", 1)),
    dict(id="R13", line="R13", shot="bed_wide", key=("yours.", RED),
         visual="Wide bedroom: you small in the bed, phone glow, door left, tall wardrobe right. Moonlight through the blinds.",
         cam="slow push", sfx=[("heartbeat", -12, 0.3), ("heartbeat", -13, 1.1)], hud=("3:17 AM", 1)),
    dict(id="R14", line="R14", shot="door_wide", key=("Silence.", YEL),
         visual="The door. The knocking stops - then the hallway light under it goes OUT on 'Silence'.",
         cam="slow push", sfx=[("tinnitus", None, 0)], hud=("3:17 AM", 1)),
    dict(id="R14b", line=None, at=("R14", "silence."), shot="bed_wide", key=None,
         visual="Wide: the room holds its breath. You, tiny in the bed, phone glow. Nothing moves.",
         cam="slow push", sfx=[], hud=("3:17 AM", 1)),
    dict(id="R15", line="R15", shot="door_under_cu", key=("own", RED),
         visual="ECU of the gap under the door, almost black: two shadows of feet... then a second pair beside them.",
         cam="slow push", sfx=[("floor_creak", -10, 0.3), ("floor_creak", -12, 1.4)], hud=("3:17 AM", 1),
         note="CLUE (A): four feet outside - whatever is out there is not alone / not one thing."),
    dict(id="R16", line="R16", shot="door_wide", key=("inside.", RED),
         visual="The door, dark gap. Your own voice, gentle, right against the wood.", cam="slow push",
         sfx=[("breath_close", -18, 0.0)], hud=("3:17 AM", 1)),
    dict(id="R17", line="R17", shot="you_cu", key=("door.", YEL),
         visual="CU you, eyes locked on the door.", cam="hold", sfx=[], hud=("3:17 AM", 1)),
    dict(id="R17b", line=None, at=("R17", "handle"), shot="handle_cu", key=None,
         visual="ECU brass lever handle slowly dipping down.", cam="slow push", sfx=[("handle_creak", -6, 0.1)],
         hud=("3:17 AM", 1)),
    dict(id="R18", line="R18", shot="you_cu", key=("strange.", YEL),
         visual="CU you, brows knit - something doesn't add up.", cam="drift", sfx=[], hud=("3:17 AM", 1)),
    dict(id="R19", line="R19", shot="handle_cu", key=("lock.", YEL),
         visual="Pull back on the handle plate: no keyhole, no lock. There never was one.", cam="slow pull out",
         sfx=[], hud=("3:17 AM", 1)),
    dict(id="R20", line="R20", shot="door_wide", key=("creak", RED),
         visual="The whole door bows inward a few millimetres and creaks - low, wrong - then settles.", cam="push",
         sfx=[("door_creak_long", -8, 0.2)], hud=("3:17 AM", 1),
         note="CLUE (A): it's not the sound your door makes - whatever is outside isn't using it the normal way."),
    dict(id="R21", line="R21", shot="phone_cu", key=("lights", YEL),
         visual="The phone flares bright in the dark. Battery icon red.", cam="punch-in",
         sfx=[("phone_vibrate", -8, -0.1), ("text_ping", -9, 0.2)], hud=("3:17 AM", 1)),
    dict(id="R22", line="R22", shot="phone_cu", key=("wardrobe.", YEL),
         visual="Third bubble, all urgent: 'There's a second door behind your wardrobe. Get inside. NOW.'",
         cam="shake", sfx=[], hud=("3:17 AM", 1)),
    dict(id="R23", line="R23", shot="bed_wide", key=("wardrobe.", YEL),
         visual="Wide: you twist toward the tall wardrobe on the right wall. Red creeps into the shadows.",
         cam="whip", sfx=[("whoosh_soft", -10, -0.1)], hud=("3:17 AM", 1)),
    # ---- THE SECOND DOOR -----------------------------------------------------------------------------
    dict(id="R24", line="R24", shot="wardrobe_cu", key=("small", RED),
         visual="The wardrobe sits an inch off the wall; in the gap behind it, a small, old wooden door you've never seen.",
         cam="slow push", sfx=[("riser", -16, 0.0)], hud=("3:17 AM", 2),
         note="DOORS 1 -> 2. CLUE (B): the dust on the floor in front of the small door is scraped in an arc - it has been opened from inside."),
    dict(id="R25", line="R25", shot="small_door_cu", key=("scratches", RED),
         visual="ECU small door: fresh scratch lines appear in the wood from the other side; flakes of paint fall.",
         cam="hold", sfx=[("scratch_wood", -4, 0.1), ("scratch_wood", -6, 1.4)], hud=("3:17 AM", 2)),
    dict(id="R26", line="R26", shot="you_cu", key=("whispers.", RED),
         visual="CU you, frozen, breath held. Red light now on one side of your face.", cam="slow push",
         sfx=[("breath_close", -16, 0.0)], hud=("3:17 AM", 2)),
    dict(id="R27", line="R27", shot="small_door_cu", key=("found", RED),
         visual="ECU of the small door's keyhole: pitch black. Something on the other side breathes against it.",
         cam="slow push", sfx=[("breath_close", -12, -0.2)], hud=("3:17 AM", 2)),
    dict(id="R27b", line=None, shot="you_cu", key=None, freeze=True,
         visual="CU you - FREEZE FRAME, red tint.", cam="freeze", sfx=[("impact_cinematic", -8, 0.0)], hud=("3:17 AM", 2)),
    # ---- CHOICE ---------------------------------------------------------------------------------------
    dict(id="R28", line="R28", shot="choice_bg", key=("comment", YEL),
         visual="Split frame: left, your bedroom door (B); right, the small wooden door (A). Both breathe faint light at the edges.",
         cam="slow push", sfx=[("pop", -14, 0.4), ("pop", -14, 0.6)], hud=None),
    dict(id="R29", line="R29", shot="choice_bg", key=("you.", YEL), focus=(810, 1000),
         visual="Same frame, pushing in on the small door (A).", cam="slow push", sfx=[], hud=None),
    dict(id="R30", line="R30", shot="choice_bg", key=("face.", RED), focus=(270, 1000),
         visual="Same frame, pushing in on the bedroom door (B).", cam="slow push", sfx=[], hud=None),
    dict(id="R31", line="R31", shot="choice_bg", key=("top", YEL), visual="Back to both doors; hold for the vote.",
         cam="slow push", sfx=[], hud=None),
]

FOCUS = dict(clock_cu=(540, 860), phone_cu=(540, 900), you_cu=(540, 860), door_wide=(540, 900), door_cu=(540, 760),
             door_under_cu=(540, 1100), handle_cu=(560, 900), bed_wide=(540, 1000), wardrobe_cu=(560, 1000),
             small_door_cu=(540, 960), choice_bg=(540, 960))


def _t0(sc):
    if sc.get("at"):
        return word(*sc["at"]) - 0.04
    if sc["id"] == "R01":
        return 0.0
    if sc["id"] == "R27b":
        return B["freeze"]
    if sc["id"] == "R28":
        return B["choice"]
    if sc["id"] in ("R29", "R30", "R31"):
        return start(sc["line"]) - 0.1
    return start(sc["line"]) - 0.06


def _cam(sc, t0, t1):
    c, f = sc["cam"], sc.get("focus") or FOCUS.get(sc["shot"], (540, 960))
    fx = []
    if "punch" in c:
        at = B["clock_flip"] if sc["id"] == "R01" else t0
        fx.append(dict(fx="zoom", keys=[(t0, 1.0, f), (at, 1.0, f), (at + 0.14, 1.2, f), (t1, 1.26, f)], ease="out"))
    elif "pull" in c:
        fx.append(dict(fx="zoom", keys=[(t0, 1.12, f), (t1, 1.0, f)], ease="linear"))
    elif "push" in c:
        fx.append(dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.09, f)], ease="linear"))
    elif "drift" in c:
        fx.append(dict(fx="zoom", keys=[(t0, 1.03, f), (t1, 1.06, f)], ease="linear"))
    if "shake on each knock" in c:
        for kt in B["knocks"]:
            fx.append(dict(fx="shake", t0=kt, t1=kt + 0.3, amp=12, freq=22))
    elif "shake" in c:
        fx.append(dict(fx="shake", t0=t0, t1=min(t1, t0 + 0.5), amp=10, freq=18))
    if "whip" in c:
        fx.append(dict(fx="whip", t=t0 + 0.06, dur=0.2, dir=(1, 0), travel=False))
    return fx


CUTS = [sc for sc in SCENES if sc.get("cut", True)]
SEGMENTS = []
for i, sc in enumerate(CUTS):
    t0 = _t0(sc)
    t1 = _t0(CUTS[i + 1]) if i + 1 < len(CUTS) else DURATION
    seg = dict(t0=t0, t1=t1, src=sc["shot"], offset=t0, fx=_cam(sc, t0, t1), scene=sc["id"])
    if sc.get("freeze"):
        seg.update(freeze=B["freeze"], offset=B["freeze"])
        seg["fx"] = [dict(fx="zoom", keys=[(t0, 1.0, FOCUS["you_cu"]), (t1, 1.12, FOCUS["you_cu"])]),
                     dict(fx="tint", color=RED, amount=0.35, t0=t0, t1=t1), dict(fx="flash", t=t0, dur=0.15)]
    if t0 >= B["text3"] - 0.5 and not sc.get("freeze"):  # red creeps in from the third message
        seg["fx"].append(dict(fx="tint", color=RED, amount=0.1 + 0.2 * min(1.0, (t0 - B["text3"]) / 12.0), t0=t0, t1=t1))
    seg["fx"].append(dict(fx="vignette", strength=0.35, t0=t0, t1=t1))
    SEGMENTS.append(seg)

# ---- OVERLAYS -------------------------------------------------------------------------------------------
HUD_END = B["choice"]
doors_keys = []
for sc in SCENES:
    if sc.get("hud") and (not doors_keys or doors_keys[-1][1] != sc["hud"][1]):
        doors_keys.append((_t0(sc), sc["hud"][1]))

OVERLAYS = [
    dict(kind="title", t0=0.05, t1=B["title_out"], text="THE ROOM THAT\nWASN'T THERE", sub="PART 1", size=100, y=0.2,
         sub_color=YEL, stroke=14),
    dict(kind="chip", t0=0.0, t1=HUD_END, text="NIGHT 1 · APT 317", size=24, x=0.17, y=0.03, bg="#15161b", color="#d7d7dc"),
    dict(kind="hud", t0=0.0, t1=HUD_END, x=0.15, y=0.068, size=40, items=[("", [(0.0, "3:17 AM")])], flash=RED),
    dict(kind="hud", t0=0.0, t1=HUD_END, x=0.86, y=0.05, size=36, items=[("DOORS", doors_keys)], flash=RED),
    # choice screen
    dict(kind="title", t0=B["choice"], t1=DURATION, text="PART 2", sub="WHICH DOOR DO YOU TRUST?", size=120, y=0.1,
         sub_color=YEL, sub_size=54, stroke=12),
    dict(kind="text", t0=B["choice"] + 0.35, t1=DURATION, text="COMMENT A OR B · TOP COMMENT DECIDES PART 2", size=34,
         y=0.215, weight="ExtraBold", color="#ffffff", stroke=6),
    dict(kind="text", t0=B["choice"] + 0.45, t1=DURATION, text="B  CONFRONT WHAT'S OUTSIDE", size=54, x=0.27, y=0.31,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#3f8fd6", bg_alpha=0.95),
    dict(kind="text", t0=B["choice"] + 0.6, t1=DURATION, text="A  HIDE IN THE SMALL DOOR", size=54, x=0.73, y=0.39,
         weight="ExtraBold", color="#ffffff", stroke=0, bg="#e2574c", bg_alpha=0.95),
]

# ---- CAPTIONS (ALL CAPS, one key word per line: RED danger / YELLOW rules & objects) ---------------------
_line_colors = {}
for sc in SCENES:
    if sc.get("key") and sc.get("line"):
        _line_colors.setdefault(sc["line"], {})[sc["key"][0]] = sc["key"][1]

CAPTIONS = dict(
    timing="audio/timing.json", y=0.66, size=86, max_words=5, highlight="#ffffff", speakers=False,
    upper=True, line_colors=_line_colors,
    overrides=[(sg["t0"], sg["t1"], 0.80) for sg in SEGMENTS if sg["src"] in ("you_cu", "phone_cu", "choice_bg", "clock_cu")],
)

AUDIO = "audio/mix_master.wav"
