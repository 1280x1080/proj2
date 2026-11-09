"""EDL for VIDEO_003 - GOING DOWN, Part 1 (series pilot).

SCENES is the scene plan (one script line = one cut). SEGMENTS, OVERLAYS and CAPTIONS for
edl_engine.py are built from it, so re-recording a line re-times every cut, card and HUD change.
Times come from beats.py (word timing once narrate.py has run, estimates before that).

Shots named in SCENES are drawn by anim2d.py (SHOTS dict); that file is the next production
step, not part of this script pass.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from beats import B, CHOICE_HOLD, DURATION, ESTIMATED, end, start, word  # noqa: E402,F401

BEATS = B
RED, YEL = "#e8423a", "#ffd23f"

# ---------------------------------------------------------------------------------------------
# Lighting states used by the visual descriptions (anim2d reads the same beat times):
#   FLUO  - cold fluorescent, slight green-white, every ceiling panel on
#   DIM   - panels dying one by one from the back (from S21 "dying")
#   RED   - emergency light only, deep red (from S25 "drops")
#   LOBBY - warm lobby light spilling through the open doors over the RED car (S26-S28)
# HUD: clock (top-left, under the "NIGHT 1 - TOWER B" tag) + RIDERS counter (top-right).
# ---------------------------------------------------------------------------------------------
SCENES = [
    # ---- 1. HOOK (0-3 s) -----------------------------------------------------------------
    dict(id="S01", line="S01", shot="panel_cu", key=("itself.", RED),
         visual="ECU of the button panel. Frame 0: button 13 clicks in on its own and lights up amber. No hands in shot. FLUO.",
         cam="punch-in on the 13 button at the click, then slow push", sfx=[("click_ui", -4, 0.0), ("lamp_buzz", None, 0)],
         hud=("3:07 AM", 1), note="Title card GOING DOWN / PART 1 over this shot."),
    # ---- 2. WRONG NORMAL (3-15 s) --------------------------------------------------------
    dict(id="S02", line="S02", shot="car_wide", key=("twenty-two.", YEL),
         visual="Wide, elevator interior from the front corner. You (teen mascot, red cap backwards, hoodie) hold a trash bag, sleepy, half-lidded. Floor display reads 22. FLUO.",
         cam="slow push-in", sfx=[("room_tone", None, 0)], hud=("3:07 AM", 1)),
    dict(id="S03", line="S03", shot="you_cu", key=("thirteenth", RED),
         visual="MCU you. Eyes drift to the panel, brows knit. FLUO, cold top light.",
         cam="hold, tiny drift", sfx=[], hud=("3:07 AM", 1),
         note="Panel in the background shows 12 then 14 - there is no 13 row printed in the building directory sticker."),
    dict(id="S04", line="S04", shot="panel_cu", key=("glowing.", RED),
         visual="ECU button 13 glowing amber. Every other button is dark. FLUO.",
         cam="punch-in on 'glowing'", sfx=[("riser", -26, 0.0)], hud=("3:07 AM", 1)),
    dict(id="S05", line="S05", shot="mirror_pov", key=("alone.", YEL),
         visual="Mirror on the back wall: your reflection, the trash bag, the corner behind you EMPTY. FLUO.",
         cam="slow push toward the empty corner", sfx=[], hud=("3:07 AM", 1),
         note="CLUE for 1-STEP OUT: Gus is sitting in that corner (we learn in S09) but the mirror never shows him."),
    # ---- 3. THE PRESENCE (15-25 s) -------------------------------------------------------
    dict(id="S06", line="S06", shot="doors_13", key=("thirteen.", RED),
         visual="Doors slide open from your POV onto floor 13: a long dark hallway, every apartment door open. Indicator above reads 13. FLUO in car, black outside.",
         cam="hold, then slow push into the hallway", sfx=[("ding", -10, -0.25), ("whoosh_soft", -12, 0.0)], hud=("3:09 AM", 1)),
    dict(id="S07", line="S07", shot="doors_13", key=("raincoat", RED),
         visual="Same POV, pushing in down the hallway: a very tall woman in a red raincoat, hood brushing the ceiling, faces the wall. Too still. Water drips from the hem onto the carpet.",
         cam="slow zoom on her", sfx=[("heartbeat", -14, 0.4)], hud=("3:09 AM", 1)),
    dict(id="S08", line="S08", shot="doors_13", key=("turn.", RED),
         visual="Her hood starts to turn - the doors slam shut across her before we see a face.",
         cam="shake on the door close", sfx=[("door_close", -6, 0.6)], hud=("3:09 AM", 1)),
    # ---- 4. THE GUIDE (25-40 s) ----------------------------------------------------------
    dict(id="S09", line="S09", shot="gus_reveal", key=("someone", RED),
         visual="Over your shoulder: an old man in grey coveralls sits on an upturned bucket in the back corner. You flinch, eyes wide. FLUO.",
         cam="whip pan to the corner", sfx=[("whoosh", -9, -0.15), ("impact_soft", -8, 0.05)], hud=("3:09 AM", 2),
         note="RIDERS 1 -> 2 (he was 'not there' - bump)."),
    dict(id="S10", line="S10", shot="gus_cu", key=("Gus.", YEL),
         visual="CU Gus: tired kind eyes, grey stubble, name tag GUS stitched on the chest, a mop beside him. FLUO.",
         cam="slow push", sfx=[], hud=("3:09 AM", 2)),
    dict(id="S11", line="S11", shot="gus_cu", key=("hand.", YEL),
         visual="Gus leans in, uncaps a black marker with his teeth. Calm, certain.",
         cam="hold", sfx=[], hud=("3:12 AM", 2)),
    dict(id="S12", line="S12", shot="palm_cu", key=("rules", YEL),
         visual="Top-down ECU of your palm. The marker writes 1. 2. 3. FLUO.",
         cam="slow push", sfx=[("tick", -16, 0.2), ("tick", -16, 0.6)], hud=("3:12 AM", 2)),
    dict(id="S13", line="S13", shot="gus_cu", key=("mirror", YEL), card=1,
         visual="CU Gus, one finger up, looking straight at you.",
         cam="push", sfx=[("click_ui", -14, 0.0)], hud=("3:12 AM", 2)),
    dict(id="S14", line="S14", shot="palm_cu", key=("press", YEL), card=2,
         visual="Your palm, rule 2 underlined. Your hand trembles.",
         cam="hold", sfx=[("click_ui", -14, 0.0)], hud=("3:12 AM", 2)),
    dict(id="S15", line="S15", shot="gus_cu", key=("twice.", YEL), card=3,
         visual="CU Gus, three fingers up, eyes flick to the floor display.",
         cam="slow push", sfx=[("click_ui", -14, 0.0)], hud=("3:12 AM", 2),
         note="Rule 3 is the one the cliffhanger tests."),
    dict(id="S15b", line=None, at=("S15", "bell"), shot="indicator_cu", key=None,
         visual="Insert: the brass bell / floor indicator above the doors, numbers ticking down 12, 11, 10.",
         cam="hold", sfx=[], hud=("3:12 AM", 2)),
    # ---- 5. TESTS (40-70 s) --------------------------------------------------------------
    dict(id="S16", line="S16", shot="doors_9", key=("Nobody", RED),
         visual="Doors open on 9: empty, ordinary hallway, a flickering exit sign. FLUO.",
         cam="hold", sfx=[("ding", -10, -0.25), ("whoosh_soft", -12, 0.0)], hud=("3:14 AM", 2),
         note="TEST rule 1 starts: doors are open."),
    dict(id="S17", line="S17", shot="mirror_pov", key=("behind", RED),
         visual="Edge of frame: the mirror shows a red hood right behind your head - and Gus's corner empty again. You are NOT looking at it - we see it, you don't.",
         cam="slow push on the hood", sfx=[("heartbeat", -10, 0.0), ("heartbeat", -12, 0.8)], hud=("3:14 AM", 2),
         note="CLUE for 1-STEP OUT (second look): Gus is not in the reflection."),
    dict(id="S18", line="S18", shot="you_cu", key=("shoes", YEL),
         visual="CU you, eyes locked on your shoes, sweating, jaw tight. Doors close in the background.",
         cam="hold, slight shake", sfx=[("whoosh_soft", -14, 1.0)], hud=("3:14 AM", 2),
         note="Rule 1 PASSED."),
    dict(id="S19", line="S19", shot="rider_corner", key=("inside.", RED),
         visual="Wide: the red-raincoat woman now stands in the front corner, facing it, hood brushing the ceiling. Gus has not moved. FLUO.",
         cam="punch-in on 'inside'", sfx=[("impact_hard", -10, 0.35)], hud=("3:14 AM", 3),
         note="RIDERS 2 -> 3. TEST rule 2 starts."),
    dict(id="S20", line="S20", shot="rider_corner", key=("thirteen,", RED),
         visual="Her back. A long grey hand points at the panel without her turning.",
         cam="slow push", sfx=[], hud=("3:14 AM", 3)),
    dict(id="S21", line="S21", shot="car_wide", key=("die.", RED),
         visual="Wide: ceiling panels die one by one from the back toward you. DIM.",
         cam="hold, flicker", sfx=[("flicker_zap", -6, 0.6), ("flicker_zap", -8, 1.1)], hud=("3:14 AM", 3)),
    dict(id="S22", line="S22", shot="you_cu", key=("Mom.", RED),
         visual="CU you. The voice is your mom's, soft and tired. Your eyes well up. DIM, one panel left.",
         cam="slow push", sfx=[], hud=("3:15 AM", 3),
         note="EMOTIONAL MANIPULATION test of rule 2."),
    dict(id="S23", line="S23", shot="thumb_cu", key=("button.", YEL),
         visual="ECU your thumb resting on button 13; the marker '2.' on your palm is visible. DIM.",
         cam="slow push", sfx=[("heartbeat", -8, 0.0)], hud=("3:15 AM", 3)),
    dict(id="S24", line="S24", shot="hand_slap", key=("slaps", YEL),
         visual="Gus's hand slaps yours off the panel. His coverall sleeve is dripping wet.",
         cam="shake + white flash", sfx=[("thud_wood", -4, 0.15), ("impact_soft", -8, 0.15)], hud=("3:15 AM", 3),
         note="CLUE for 1-STEP OUT: Gus's sleeve is wet - so is the hand in S30. Rule 2 PASSED."),
    dict(id="S25", line="S25", shot="car_red", key=("red.", RED),
         visual="The car drops: everything jolts, emergency light snaps on, the whole car goes RED. Floor display spins down.",
         cam="hard shake", sfx=[("whoosh", -6, 0.0), ("impact_cinematic", -4, 0.4)], hud=("3:16 AM", 3)),
    # ---- 6. CLIFFHANGER (70-85 s) --------------------------------------------------------
    dict(id="S26", line="S26", shot="lobby_pov", key=("twice.", YEL),
         visual="Doors open onto your lobby, warm light flooding the RED car. Mr. Reyes, the night doorman you know, smiles and waves you out. Lobby wall clock reads 3:07. Through the glass street doors: daylight.",
         cam="slow push", sfx=[("ding", -8, -0.2), ("ding", -8, 0.25), ("ding", -34, 0.75), ("whoosh_soft", -12, 0.4)],
         hud=("3:07 AM", 3),
         note="CLUES for 2-STAY IN: HUD clock jumps BACK to 3:07; daylight at 3 AM; a barely audible THIRD ding (-34 dB) after the two loud ones."),
    dict(id="S28", line="S28", shot="palm_cu", key=("go.", YEL),
         visual="Your palm under red light, rule 3 '...when the bell rings twice.' - the doorman waving, out of focus, behind it. LOBBY + RED.",
         cam="push", sfx=[("riser", -14, 0.0)], hud=("3:07 AM", 3)),
    dict(id="S29", line="S29", shot="gus_cu", key=("Stay", RED),
         visual="CU Gus, RED-lit, eyes locked on the doorman, not on you. Grave.",
         cam="slow push", sfx=[], hud=("3:07 AM", 3),
         note="Contradicts his own rule 3."),
    dict(id="S30a", line="S30", shot="wet_hand_cu", key=("wet", RED), until_word="settles",
         visual="ECU: a pale wet hand lands on your shoulder from behind. Water drips on your hoodie. RED.",
         cam="punch-in", sfx=[("impact_soft", -6, 0.1), ("heartbeat", -6, 0.3)], hud=("3:07 AM", 4),
         note="RIDERS 3 -> 4 - nobody new is visible."),
    dict(id="S30b", line=None, shot="you_cu", key=None, freeze=True,
         visual="CU you, eyes huge, mouth open - FREEZE FRAME with a red tint.",
         cam="freeze + punch 1.0->1.12", sfx=[("impact_cinematic", -6, 0.0)], hud=("3:07 AM", 4)),
    # ---- 7. CHOICE SCREEN (last ~5 s) ------------------------------------------------------
    dict(id="S31", line="S31", shot="choice_bg", key=("out?", RED),
         visual="Dimmed lobby POV through the open doors. PART 2 / DO YOU STEP OUT? / COMMENT 1 OR 2 - TOP COMMENT DECIDES PART 2 / pills 1 STEP OUT (red) and 2 STAY IN (blue).",
         cam="hold", sfx=[("pop", -12, 0.2), ("pop", -12, 0.35)], hud=None),
]

# ---------------------------------------------------------------------------------------------
# build SEGMENTS
# ---------------------------------------------------------------------------------------------
FOCUS = dict(indicator_cu=(540, 700), panel_cu=(560, 900), car_wide=(540, 960), you_cu=(540, 860), mirror_pov=(540, 900), doors_13=(540, 980),
             doors_9=(540, 980), gus_reveal=(560, 900), gus_cu=(540, 860), palm_cu=(540, 960), rider_corner=(540, 900),
             thumb_cu=(540, 960), hand_slap=(540, 960), car_red=(540, 960), lobby_pov=(540, 980), wet_hand_cu=(540, 900),
             choice_bg=(540, 960))


def _t0(sc):
    if sc.get("at"):
        return word(*sc["at"]) - 0.04
    if sc["id"] == "S01":
        return 0.0
    if sc["id"] == "S30b":
        return B["freeze"]
    if sc["id"] == "S31":
        return B["choice"]
    return start(sc["line"]) - 0.06


def _cam(sc, t0, t1):
    c, f = sc["cam"], FOCUS.get(sc["shot"], (540, 960))
    fx = []
    if "punch" in c:
        at = t0 if sc["id"] != "S04" else B["thirteen_glow"]
        fx.append(dict(fx="zoom", keys=[(t0, 1.0, f), (at, 1.0, f), (at + 0.14, 1.22, f), (t1, 1.28, f)], ease="out"))
    elif "push" in c or "zoom" in c:
        fx.append(dict(fx="zoom", keys=[(t0, 1.0, f), (t1, 1.09, f)], ease="linear"))
    elif "drift" in c:
        fx.append(dict(fx="zoom", keys=[(t0, 1.03, f), (t1, 1.06, f)], ease="linear"))
    if "shake" in c:
        fx.append(dict(fx="shake", t0=t0, t1=min(t1, t0 + (0.9 if "hard" in c else 0.5)), amp=22 if "hard" in c else 10, freq=18))
    if "whip" in c:
        fx.append(dict(fx="whip", t=t0 + 0.06, dur=0.2, dir=(1, 0), travel=False))
    if "flash" in c:
        fx.append(dict(fx="flash", t=t0 + 0.15, dur=0.18))
    return fx


SEGMENTS = []
for i, sc in enumerate(SCENES):
    t0 = _t0(sc)
    t1 = _t0(SCENES[i + 1]) if i + 1 < len(SCENES) else DURATION
    if sc["id"] == "S30a":
        t1 = B["freeze"]
    seg = dict(t0=t0, t1=t1, src=sc["shot"], offset=t0, fx=_cam(sc, t0, t1), scene=sc["id"])
    if sc.get("freeze"):
        seg.update(freeze=B["freeze"], offset=B["freeze"])
        seg["fx"] = [dict(fx="zoom", keys=[(t0, 1.0, FOCUS["you_cu"]), (t1, 1.12, FOCUS["you_cu"])]),
                     dict(fx="tint", color=RED, amount=0.35, t0=t0, t1=t1), dict(fx="flash", t=t0, dur=0.15)]
    # colour shift toward red during the tests, full red after the drop
    if B["lights_die"] <= t0 < B["drop"]:
        seg["fx"].append(dict(fx="tint", color=RED, amount=0.1 + 0.15 * (t0 - B["lights_die"]) / max(0.1, B["drop"] - B["lights_die"]),
                              t0=t0, t1=t1))
    if t0 >= B["lights_die"]:
        seg["fx"].append(dict(fx="vignette", strength=0.45, t0=t0, t1=t1))
    SEGMENTS.append(seg)

# ---------------------------------------------------------------------------------------------
# OVERLAYS: title card, HUD, survival-rule cards, choice screen
# ---------------------------------------------------------------------------------------------
HUD_END = B["choice"]
clock_keys = [(_t0(sc), sc["hud"][0]) for sc in SCENES if sc["hud"]]
riders_keys = [(_t0(sc), sc["hud"][1]) for sc in SCENES if sc["hud"]]


def _dedupe(keys):
    out = []
    for t, v in keys:
        if not out or out[-1][1] != v:
            out.append((t, v))
    return out


RULES = {1: "Never look in the mirror with the doors open",
         2: "Never press a floor she asks for",
         3: "Only get out when the bell rings twice"}
_card_t = {sc["card"]: _t0(sc) for sc in SCENES if sc.get("card")}
_card_end = {1: _card_t[2], 2: _card_t[3], 3: start("S16") - 0.06}

OVERLAYS = [
    # title card over the hook
    dict(kind="title", t0=0.05, t1=B["title_out"], text="GOING DOWN", sub="PART 1", size=120, y=0.2,
         sub_color=YEL, stroke=14),
    # HUD
    dict(kind="chip", t0=0.0, t1=HUD_END, text="NIGHT 1 · TOWER B", size=24, x=0.17, y=0.03, bg="#15161b",
         color="#d7d7dc"),
    dict(kind="hud", t0=0.0, t1=HUD_END, x=0.15, y=0.068, size=40, items=[("", _dedupe(clock_keys))], flash=RED),
    dict(kind="hud", t0=0.0, t1=HUD_END, x=0.85, y=0.05, size=36, items=[("RIDERS", _dedupe(riders_keys))],
         flash=RED),
]
for n in (1, 2, 3):
    OVERLAYS += [
        dict(kind="stamp", t0=_card_t[n], t1=_card_end[n], text=f"SURVIVAL RULE #{n}", size=46, y=0.135, rot=-3,
             color=RED, bg="#f1e9d6"),
        dict(kind="text", t0=_card_t[n] + 0.08, t1=_card_end[n], text=RULES[n].upper(), size=52, y=0.205,
             weight="ExtraBold", color="#2a2420", stroke=0, bg="#f1e9d6", bg_alpha=0.97),
    ]
OVERLAYS += [
    dict(kind="title", t0=B["choice"], t1=DURATION, text="PART 2", sub="DO YOU STEP OUT?", size=130, y=0.12,
         sub_color=YEL, sub_size=60, stroke=12),
    dict(kind="text", t0=B["choice"] + 0.3, t1=DURATION, text="COMMENT 1 OR 2 · TOP COMMENT DECIDES PART 2",
         size=36, y=0.255, weight="ExtraBold", color="#ffffff", stroke=6),
    dict(kind="choices", t0=B["choice"] + 0.25, t1=DURATION, options=["STEP OUT", "STAY IN"],
         colors=["#e2574c", "#3f8fd6"], size=62, y=0.52),
]

# ---------------------------------------------------------------------------------------------
# CAPTIONS (word timing, max 5 words, no karaoke sweep, danger words red)
#   - upper / line_colors are the series caption spec: ALL CAPS and one key word per line,
#     RED = danger, YELLOW = rules/objects.  The current edl_engine reads neither key (it ignores
#     unknown keys), so today captions render in script case with only the RED `emphasis` words
#     coloured.  See README "Caption gap".
# ---------------------------------------------------------------------------------------------
_line_colors = {}
for sc in SCENES:
    if sc.get("key") and sc.get("line"):
        _line_colors.setdefault(sc["line"], {})[sc["key"][0]] = sc["key"][1]

CAPTIONS = dict(
    timing="audio/timing.json", y=0.64, size=86, max_words=5, highlight="#ffffff",
    emphasis=sorted({w for d in _line_colors.values() for w, c in d.items() if c == RED}), emphasis_color=RED,
    speakers=False,
    # keep captions off faces (close-ups) and below the choice pills
    overrides=[(sg["t0"], sg["t1"], 0.80) for sg in SEGMENTS if sg["src"] in ("you_cu", "gus_cu", "choice_bg")],
    upper=True, line_colors=_line_colors,
)

AUDIO = "audio/mix_master.wav"
